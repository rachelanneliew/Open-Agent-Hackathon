"""Transport stubs plus opt-in local HTTP fixture (never a live model)."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import subprocess
import threading
import time
import unittest
from unittest.mock import patch

from app.nightshift import ModelError, NightshiftClient, NightshiftConfig, strict_json


class NightshiftTests(unittest.TestCase):
    def client(self):
        return NightshiftClient(NightshiftConfig('127.0.0.1:8088/v1/models', 'PRIVATE_TEST_TOKEN'))

    def test_private_configuration_and_normalization(self):
        c = self.client().config
        self.assertEqual(c.base_url, 'http://127.0.0.1:8088/v1')
        self.assertNotIn('PRIVATE_TEST_TOKEN', repr(c))
        for url in ('http://outside.example/v1', 'https://user:password@host/v1',
                    'https://host/v1?token=secret', 'https://host/unexpected'):
            with self.assertRaisesRegex(ModelError, 'configuration_unavailable'):
                NightshiftConfig(url, 'token')
        for token in ('', 'rt-local', 'a\nb', 'a b', '\u0100'):
            with self.assertRaises(ModelError):
                NightshiftConfig('localhost', token)

    def test_config_load_failure_never_leaks_exception(self):
        with patch('app.nightshift.load_settings', side_effect=ValueError('PRIVATE_VALUE')):
            with self.assertRaisesRegex(ModelError, '^configuration_unavailable$'):
                NightshiftConfig.from_environment()

    def test_subprocess_deadline_token_not_in_argv_and_fixed_request(self):
        completed = subprocess.CompletedProcess([], 0, '{"response":{"choices":[]}}', '')
        with patch('app.nightshift.subprocess.run', return_value=completed) as run:
            self.client().complete([{'role': 'user', 'content': 'case'}], timeout_seconds=3)
        self.assertNotIn('PRIVATE_TEST_TOKEN', str(run.call_args.args))
        request = json.loads(run.call_args.kwargs['input'])
        self.assertEqual(run.call_args.kwargs['timeout'], 3)
        self.assertEqual(request['url'], 'http://127.0.0.1:8088/v1/chat/completions')
        self.assertEqual(set(request['payload']), {'model', 'messages', 'max_tokens', 'stream',
            'temperature', 'tool_choice', 'response_format'})
        self.assertFalse(request['payload']['stream'])
        self.assertNotIn('tools', request['payload'])
        self.assertEqual(request['payload']['response_format'], {'type': 'json_object'})
        self.assertEqual(request['payload']['tool_choice'], 'none')
        self.assertEqual(request['payload']['temperature'], 0)

    def test_timeout_untrusted_stderr_and_malformed_worker_output(self):
        for result, code in ((subprocess.TimeoutExpired('secret', 1, output='PRIVATE'), 'timeout'),
                            (OSError('PRIVATE'), 'provider_unavailable'),
                            (subprocess.CompletedProcess([], 1, '', 'PRIVATE'), 'provider_unavailable'),
                            (subprocess.CompletedProcess([], 0, '{"error":"PRIVATE"}', ''), 'provider_unavailable'),
                            (subprocess.CompletedProcess([], 0, '{"error":"unauthorized"}', ''), 'unauthorized')):
            kwargs = {'side_effect': result} if isinstance(result, Exception) else {'return_value': result}
            with patch('app.nightshift.subprocess.run', **kwargs):
                with self.assertRaisesRegex(ModelError, '^' + code + '$'):
                    self.client().complete([])

    def test_discovery_requires_advertised_route_and_runtime(self):
        client = self.client()
        for response in ({}, {'data': []}, {'data': [{'id': 'other/model'}]}, {'data': [{'id': 'meterless/fast'}]}):
            with patch.object(client, '_request', return_value=response):
                with self.assertRaises(ModelError):
                    client.discover()
        with patch.object(client, '_request', return_value={'data': [{'id': 'meterless/auto'}, {'id': 'meterless/new'}]}):
            self.assertEqual(client.discover(), ('meterless/auto', 'meterless/new'))

    def test_budgets_rejected_before_process_start(self):
        with patch('app.nightshift.subprocess.run') as run:
            for timeout in (0, -1, 181, True, '3', float('nan')):
                with self.assertRaises(ModelError):
                    self.client().complete([], timeout_seconds=timeout)
            with self.assertRaisesRegex(ModelError, 'input_too_large'):
                self.client().complete([{'role': 'user', 'content': 'x' * 262144}])
            run.assert_not_called()

    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        for text in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(text)


@unittest.skipUnless(os.environ.get('DISPUTE_NIGHTSHIFT_HTTP_TESTS') == '1',
                     'Opt in to local HTTP transport fixtures; these are not live Nightshift')
class LocalHTTPTests(unittest.TestCase):
    @contextmanager
    def server(self, *, status=200, body=b'{"data":[{"id":"meterless/auto"}]}', delay=0, redirect=False):
        seen = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.respond()
            def do_POST(self):
                self.respond()
            def respond(self):
                content = self.rfile.read(int(self.headers.get('Content-Length', 0)))
                seen.append((self.path, {key.lower(): value for key, value in self.headers.items()}, content))
                time.sleep(delay)
                self.send_response(status)
                if redirect:
                    self.send_header('Location', '/redirect-target')
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            def log_message(self, *_):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield NightshiftClient(NightshiftConfig(f'http://127.0.0.1:{server.server_port}', 'TEST_TOKEN')), seen
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_real_worker_auth_headers_and_text_payload(self):
        with self.server() as (client, seen):
            self.assertEqual(client.discover(), ('meterless/auto',))
            client.complete([{'role': 'user', 'content': 'synthetic'}])
        self.assertEqual(seen[0][0], '/v1/models')
        self.assertEqual(seen[0][1]['authorization'], 'Bearer TEST_TOKEN')
        self.assertEqual(seen[1][1]['meterless-scope'], 'user')
        self.assertEqual(seen[1][1]['meterless-tier-split'], 'off')
        self.assertEqual(seen[1][1]['meterless-app'], 'dispute-investigation')
        self.assertEqual(json.loads(seen[1][2])['messages'][0]['content'], 'synthetic')

    def test_real_http_auth_error_is_sanitized(self):
        with self.server(status=401, body=b'PRIVATE provider details') as (client, _):
            with self.assertRaisesRegex(ModelError, '^unauthorized$'):
                client.discover()

    def test_redirect_cannot_forward_token(self):
        with self.server(status=302, redirect=True) as (client, seen):
            with self.assertRaisesRegex(ModelError, '^provider_unavailable$'):
                client.discover()
        self.assertEqual(len(seen), 1)

    def test_oversized_and_duplicate_json_body_refused(self):
        for body in (b'x' * 262145, b'{"data":[],"data":[]}'):
            with self.server(body=body) as (client, _):
                with self.assertRaisesRegex(ModelError, '^malformed_response$'):
                    client.discover()

    def test_total_deadline_kills_worker_even_before_headers(self):
        with self.server(delay=2) as (client, _):
            start = time.monotonic()
            with self.assertRaisesRegex(ModelError, '^timeout$'):
                client.complete([], timeout_seconds=0.3)
            self.assertLess(time.monotonic() - start, 1.5)


if __name__ == '__main__':
    unittest.main()
