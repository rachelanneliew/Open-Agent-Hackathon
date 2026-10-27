"""Bounded Nightshift JSON transport, verified against installed 0.92.7.

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
STRUCTURED_ERRORS = frozenset(('structured_output_unsupported', 'structured_output_schema_rejected',
    'schema_validation_failed', 'invalid_json_output', 'response_truncated', 'response_refused'))
PROVIDER_ERRORS = frozenset(('provider_route_failed', 'provider_error', 'provider_rejected_request',
    'provider_auth_failed', 'rate_limited', 'first_token_timeout', 'engine_timeout',
    'model_unavailable_for_account', 'endpoint_retired'))


class ModelError(Exception):
    def __init__(self, code, *, path='$'):
        self.code = code
        self.path = safe_error_path(path)
        super().__init__(code)


def safe_error_path(value):
    """Provider errors may echo arbitrary property names; retain known names only."""
    fields = {'kind', 'proposal', 'request', 'uncertainties', 'recommendation', 'outcome',
        'currency', 'amount_minor', 'evidence_ids', 'policy_rule_ids', 'missing_evidence',
        'category', 'reason', 'policy_rule_id', 'name', 'dispute_id'}
    if (type(value) is not str or len(value) > 240 or
            re.fullmatch(r'\$(?:\.[a-z_]+|\[[0-9]{1,6}\])*', value) is None or
            not set(re.findall(r'\.([a-z_]+)', value)) <= fields):
        return '$'
    return value


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
        headers.update({'Content-Type': 'application/json', 'meterless-scope': 'user',
                        'meterless-tier-split': 'off'})
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
        path = '$'
        if code != 'unauthorized':
            # Preserve only known machine codes, never provider text/content.
            try:
                body = strict_json(exc.read(MAX_BYTES + 1).decode('utf-8'))
                reported = body.get('error', {}).get('code')
                if type(reported) is str and reported in (STRUCTURED_ERRORS | PROVIDER_ERRORS):
                    code = reported
                    errors = body.get('meterless', {}).get('validation', {}).get('errors', [])
                    if type(errors) is list and errors and type(errors[0]) is dict:
                        path = safe_error_path(errors[0].get('path'))
            except (ValueError, TypeError, AttributeError, OSError, UnicodeError, RecursionError):
                pass
        raise ModelError(code, path=path) from None
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
            if type(result) is not dict or set(result) not in ({'response'}, {'error'}, {'error', 'path'}):
                raise ModelError('malformed_response')
            if 'error' in result:
                code = result['error']
                raise ModelError(code if type(code) is str and code in (
                    {'unauthorized', 'provider_unavailable', 'malformed_response'} | STRUCTURED_ERRORS | PROVIDER_ERRORS)
                    else 'provider_unavailable', path=result.get('path', '$'))
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

    def complete(self, messages, *, timeout_seconds=180, response_schema=None):
        # Installed proxy.js forwards json_object and disables semantic caching
        # for structured requests. tool_choice:none also selects the structured
        # path, skipping Nightshift answer-memory/scaffold injection; no native
        # tools are supplied or authorized. Still validate every result locally.
        response_format = ({'type': 'json_schema', 'json_schema': {
            'name': 'dispute_investigator', 'strict': True, 'schema': response_schema}}
            if response_schema is not None else {'type': 'json_object'})
        return self._request('/chat/completions', {'model': self.config.route,
            'messages': messages, 'max_tokens': 4096, 'stream': False, 'temperature': 0,
            'tool_choice': 'none', 'response_format': response_format}, timeout_seconds)


def _main():
    try:
        request = strict_json(sys.stdin.read(MAX_BYTES + 1))
        result = {'response': _http_request(request)}
    except ModelError as exc:
        result = {'error': exc.code, 'path': exc.path}
    except Exception:
        result = {'error': 'provider_unavailable'}
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    _main()
