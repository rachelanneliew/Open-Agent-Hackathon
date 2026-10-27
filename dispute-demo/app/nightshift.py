"""Bounded text-only Nightshift transport; no provider feature assumptions.

Reuse the existing private configuration/authentication conventions. Each HTTP
request runs in a short-lived child so the parent enforces a wall-clock deadline
even during DNS, headers or a trickling body. Secrets travel over stdin, never
argv, prompts or diagnostic text. No automatic model/request retries.
"""
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

from integration.check_nightshift import APP_ID, CheckError, NoRedirect, load_settings, normalize_base

MAX_BYTES = 262144


class ModelError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def strict_json(text):
    def pairs(items):
        if len(items) != len(dict(items)):
            raise ValueError('Duplicate fields')
        return dict(items)
    def constant(_):
        raise ValueError('Non-finite number')
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('Response too large')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def label(value):
    """Metadata only, never extract identity from free-form assistant prose."""
    return value if type(value) is str and re.fullmatch(r'[A-Za-z0-9_.:/-]{1,160}', value) else None


@dataclass(frozen=True)
class NightshiftConfig:
    base_url: str
    token: str = field(repr=False)
    route: str = 'meterless/auto'
    timeout_seconds: float = 180

    def __post_init__(self):
        try:
            base = normalize_base(self.base_url)
            if (not self.token or self.token == 'rt-local' or not self.token.isascii()
                    or any(c.isspace() or ord(c) < 33 for c in self.token)
                    or label(self.route) is None or type(self.timeout_seconds) not in (int, float)
                    or not 0 < self.timeout_seconds <= 180):
                raise ValueError()
            object.__setattr__(self, 'base_url', base)
        except (CheckError, ValueError, TypeError, AttributeError):
            raise ModelError('configuration_unavailable') from None

    @classmethod
    def from_environment(cls):
        try:
            values = load_settings()
            return cls(values.get('METERLESS_BASE_URL', 'http://127.0.0.1:8088/v1'),
                       values.get('METERLESS_RUNTIME_TOKEN', ''),
                       values.get('METERLESS_MODEL') or 'meterless/auto')
        except Exception:
            raise ModelError('configuration_unavailable') from None


def _http_request(request):
    """Child-only HTTP path. Deliberately bounded and without proxy/redirects."""
    headers = {'Authorization': 'Bearer ' + request['token'], 'meterless-app': APP_ID,
               'Accept': 'application/json'}
    payload = request['payload']
    data = None
    if payload is not None:
        data = json.dumps(payload, allow_nan=False).encode()
        headers.update({'Content-Type': 'application/json', 'meterless-scope': 'user'})
    req = urllib.request.Request(request['url'], data=data, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=request['timeout']) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ModelError('malformed_response')
            return strict_json(raw.decode('utf-8'))
    except urllib.error.HTTPError as exc:
        code = 'unauthorized' if exc.code in (401, 403) else 'provider_unavailable'
        raise ModelError(code) from None
    except (TimeoutError, urllib.error.URLError, OSError):
        raise ModelError('provider_unavailable') from None
    except (ValueError, UnicodeError, RecursionError):
        raise ModelError('malformed_response') from None


class NightshiftClient:
    def __init__(self, config):
        if type(config) is not NightshiftConfig:
            raise ModelError('configuration_unavailable')
        self.config = config

    def _request(self, path, payload, timeout_seconds):
        if type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= 180:
            raise ModelError('invalid_budget')
        timeout = min(self.config.timeout_seconds, timeout_seconds)
        request = {'url': self.config.base_url + path, 'token': self.config.token,
                   'payload': payload, 'timeout': timeout}
        try:
            encoded = json.dumps(request, allow_nan=False)
            if len(encoded.encode()) > MAX_BYTES:
                raise ModelError('input_too_large')
            completed = subprocess.run([sys.executable, '-m', 'app.nightshift'],
                input=encoded, capture_output=True, text=True, timeout=timeout,
                cwd=Path(__file__).resolve().parents[1], check=False)
            if completed.returncode:
                raise ModelError('provider_unavailable')
            result = strict_json(completed.stdout)
            if type(result) is not dict or set(result) not in ({'response'}, {'error'}):
                raise ModelError('malformed_response')
            if 'error' in result:
                code = result['error']
                raise ModelError(code if code in ('unauthorized', 'provider_unavailable',
                    'malformed_response') else 'provider_unavailable')
            return result['response']
        except subprocess.TimeoutExpired:
            # subprocess.run kills and waits for this child before raising.
            raise ModelError('timeout') from None
        except (OSError, ValueError, UnicodeError, RecursionError):
            raise ModelError('provider_unavailable') from None

    def discover(self, *, timeout_seconds=15):
        response = self._request('/models', None, timeout_seconds)
        if type(response) is not dict or type(response.get('data')) is not list:
            raise ModelError('malformed_response')
        ids = tuple(row['id'] for row in response['data']
                    if type(row) is dict and label(row.get('id')) is not None)
        if not any(x.startswith('meterless/') for x in ids) or self.config.route not in ids:
            raise ModelError('route_unavailable')
        return ids

    def complete(self, messages, *, timeout_seconds=180):
        # Prompt JSON is validated locally. No native tools or response_format
        # fields: the published provider contract guarantees text completions.
        return self._request('/chat/completions', {'model': self.config.route,
            'messages': messages, 'max_tokens': 4096, 'stream': False}, timeout_seconds)


def _main():
    try:
        request = strict_json(sys.stdin.read(MAX_BYTES + 1))
        result = {'response': _http_request(request)}
    except ModelError as exc:
        result = {'error': exc.code}
    except Exception:
        result = {'error': 'provider_unavailable'}
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    _main()
