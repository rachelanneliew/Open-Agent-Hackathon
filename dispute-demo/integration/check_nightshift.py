#!/usr/bin/env python3
"""Check Nightshift authentication and optionally make one small model request.

Run --set-token to save the Nightshift runtime token using a hidden prompt.
Provider keys belong in Nightshift's Setup > Providers, not in this script.
"""
import argparse
import getpass
import json
import os
import re
import shlex
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[1] / '.env.local'
APP_ID = 'dispute-investigation'


class CheckError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the runtime token to a redirected destination.
        return None


def load_settings():
    settings = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            key, sep, value = line.partition('=')
            key = key.strip()
            if sep and key.startswith('METERLESS_'):
                words = shlex.split(value, comments=True)
                settings[key] = ' '.join(words)
    settings.update({k: v for k, v in os.environ.items() if k.startswith('METERLESS_')})
    return settings


def save_token():
    token = getpass.getpass('Paste the Nightshift runtime token (hidden): ').strip()
    if not token or token == 'rt-local' or any(c.isspace() for c in token):
        raise CheckError('Enter the real runtime token from Setup > Providers.')
    original = ENV_FILE.read_text() if ENV_FILE.exists() else ''
    line = 'METERLESS_RUNTIME_TOKEN=' + shlex.quote(token)
    pattern = r'^METERLESS_RUNTIME_TOKEN=.*$'
    if re.search(pattern, original, flags=re.MULTILINE):
        updated = re.sub(pattern, lambda _: line, original, flags=re.MULTILINE)
    else:
        updated = original.rstrip('\n') + '\n' + line + '\n'
    with tempfile.NamedTemporaryFile(mode='w', dir=ENV_FILE.parent, delete=False) as f:
        temp_path = Path(f.name)
        try:
            os.chmod(temp_path, 0o600)
            f.write(updated)
            f.flush()
            os.replace(temp_path, ENV_FILE)
        finally:
            temp_path.unlink(missing_ok=True)
    print('Saved the runtime token in private dispute-demo/.env.local.')


def normalize_base(value):
    value = value.strip()
    if '://' not in value:
        value = 'http://' + value
    url = urllib.parse.urlsplit(value)
    if (url.scheme not in ('http', 'https') or not url.hostname or url.username
            or url.password or url.query or url.fragment):
        raise CheckError('Use the runtime base URL without credentials, query or fragment.')
    if url.scheme == 'http' and url.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise CheckError('This local setup check permits HTTP only on loopback addresses.')
    if url.path.rstrip('/') not in ('', '/v1', '/v1/models', '/v1/chat/completions', '/healthz'):
        raise CheckError('Use the Nightshift base URL, for example http://127.0.0.1:8088/v1.')
    return urllib.parse.urlunsplit((url.scheme, url.netloc, '/v1', '', ''))


def request_json(base, path, token, payload=None):
    headers = {'Authorization': 'Bearer ' + token, 'meterless-app': APP_ID,
               'Accept': 'application/json'}
    data = None
    if payload is not None:
        headers.update({'Content-Type': 'application/json', 'meterless-scope': 'user'})
        data = json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=180 if payload is not None else 15) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise CheckError('Unauthorized: refresh the Nightshift runtime token with --set-token.') from None
        raise CheckError(f'Nightshift returned HTTP {exc.code}. Check its Console for provider or lane errors.') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise CheckError('Nightshift is unreachable or timed out. Keep the app open and check its endpoint.') from None
    except (ValueError, UnicodeError):
        raise CheckError('Nightshift returned an invalid JSON response.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--set-token', action='store_true', help='Save runtime token via a hidden prompt')
    parser.add_argument('--chat', action='store_true', help='Send one small test prompt; provider usage may apply')
    args = parser.parse_args()
    try:
        if args.set_token:
            save_token()
        settings = load_settings()
        base = normalize_base(settings.get('METERLESS_BASE_URL', 'http://127.0.0.1:8088/v1'))
        token = settings.get('METERLESS_RUNTIME_TOKEN', '')
        if not token or token == 'rt-local':
            raise CheckError('Runtime token missing. Run this script with --set-token first.')
        result = request_json(base, '/models', token)
        if not isinstance(result, dict) or not isinstance(result.get('data'), list):
            raise CheckError('Nightshift returned an unexpected model list.')
        ids = sorted({row['id'] for row in result['data']
                      if isinstance(row, dict) and isinstance(row.get('id'), str)})
        if not any(model.startswith('meterless/') for model in ids):
            raise CheckError('The endpoint did not advertise Meterless routing modes.')
        print(f'PASS: authenticated model discovery ({len(ids)} model IDs).')
        print('Available IDs: ' + ', '.join(ids))
        if not args.chat:
            print('Model inference was not tested by this command. If your provider key is saved in Nightshift, run --chat next.')
            return 0
        model = settings.get('METERLESS_MODEL') or 'meterless/auto'
        if model not in ids:
            raise CheckError('METERLESS_MODEL is not advertised by this runtime. Choose an ID listed above.')
        response = request_json(base, '/chat/completions', token, {
            'model': model, 'messages': [{'role': 'user', 'content': 'Reply with one word: READY'}],
            'max_tokens': 512, 'stream': False,
        })
        try:
            content = response['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError):
            raise CheckError('Nightshift returned no chat completion.') from None
        if not isinstance(content, str) or not content.strip():
            raise CheckError('Nightshift returned no non-empty text reply.')
        print('PASS: received a real text reply via Nightshift.')
        print('Requested model: ' + model)
        print('Reply: ' + content.strip())
        return 0
    except (CheckError, ValueError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
