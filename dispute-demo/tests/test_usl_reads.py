"""USL sidecar tests use explicit source doubles; HTTP fixtures are opt-in."""
from copy import deepcopy
import csv
from datetime import datetime, timezone
import http.client
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from integration import usl_reads as usl

ROOT = Path(__file__).resolve().parents[1]


class UslReadTests(unittest.TestCase):
    def setUp(self):
        self.case = ['DP-0020','TX-0020','CUST-013',11400,'SGD','2026-10-15T09:00:00Z',
                     'TX-0020','CUST-013',11400,'SGD','2026-10-15T09:00:00Z']
        self.merchant = ['ME-0001','DP-0020','CUST-013','refund_promise','received_unverified',
                         '2026-10-16T09:00:00Z','merchant-v1']
        self.history = ['CH-0001','DP-0020','CUST-013','DP-0004','unknown','2026-10-16T09:00:00Z',
                        'customer-v1','CUST-013','2026-10-15T09:00:00Z']
        self.responses = [[self.case], [self.merchant], [self.history], [['DP-0020', 1, 1]]]
        self.queries = []
        self.closed = 0

    def channel(self):
        owner = self
        class Channel:
            def run(self, query, limit):
                owner.queries.append(query)
                owner.assertTrue(query.startswith('SELECT '))
                owner.assertIn("'DP-0020'", query)
                owner.assertTrue(query.endswith('LIMIT 101'))
                owner.assertEqual(limit, 101)
                value = owner.responses.pop(0)
                if isinstance(value, Exception):
                    raise value
                return SimpleNamespace(rows=value)
            def close(self):
                owner.closed += 1
        return Channel()

    def read(self):
        result = usl._read_preview('DP-0020', channel_factory=self.channel)
        self.assertEqual(self.closed, 1)
        return result.to_dict()

    def unavailable(self):
        result = self.read()
        self.assertEqual(result['status'], 'unavailable')
        self.assertIsNone(result['case'])
        self.assertEqual(result['merchant_evidence'], ())
        self.assertFalse(result['financial_action_authority'])
        return result

    def test_typed_scoped_reads_and_explicit_unverified_freshness(self):
        value = self.read()
        self.assertEqual(value['case']['customer_id'], 'CUST-013')
        self.assertEqual(value['counts'], {'merchant_evidence':1,'prior_cases':1})
        self.assertEqual(value['status'], 'unverified')
        self.assertEqual(value['freshness'], 'unverified')
        self.assertIsNone(value['activation_timestamp'])
        self.assertFalse(value['atomic_snapshot'])
        self.assertEqual(value['native_dq'], 'not_executed_by_preview')
        self.assertIn('FileStore', value['provenance']['merchant_evidence'])
        self.assertEqual(len(self.queries), 4)
        self.assertEqual(value['joined_counts'], (1, 1))

    def test_join_mismatch_is_not_a_success(self):
        self.responses[3] = [['DP-0020', 9, 9]]
        self.unavailable()

    def test_invalid_ids_are_rejected_before_any_connection(self):
        factory = Mock(side_effect=AssertionError('must not connect'))
        for value in (None, '', 'DP-001', 'DP-0020; DROP TABLE x', 'DP-0020\n', '../../secret'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                usl._read_preview(value, channel_factory=factory)
        factory.assert_not_called()

    def test_disabled_default_does_not_start_worker(self):
        with patch.object(usl, '_bounded_worker') as worker:
            self.assertEqual(usl.preview_case('DP-0020')['status'], 'disabled')
            worker.assert_not_called()

    def test_missing_case_is_not_empty_success(self):
        self.responses[0] = []
        self.unavailable()

    def test_duplicate_case_is_rejected(self):
        self.responses[0] *= 2
        self.unavailable()

    def test_malformed_schema_is_rejected(self):
        self.responses[1] = [self.merchant[:-1]]
        self.unavailable()

    def test_changed_raw_case_is_rejected(self):
        self.case[8] = 11399
        self.unavailable()

    def test_cross_case_merchant_is_rejected(self):
        self.merchant[1] = 'DP-0014'
        self.unavailable()

    def test_cross_customer_merchant_is_rejected(self):
        self.merchant[2] = 'CUST-008'
        self.unavailable()

    def test_prior_ownership_is_independently_checked(self):
        self.history[7] = 'CUST-008'
        self.unavailable()

    def test_missing_prior_anchor_is_rejected(self):
        self.history[7] = None
        self.unavailable()

    def test_self_history_is_rejected(self):
        self.history[3] = 'DP-0020'
        self.unavailable()

    def test_duplicate_merchant_key_is_rejected(self):
        self.responses[1] *= 2
        self.unavailable()

    def test_duplicate_history_with_different_key_is_rejected(self):
        other = list(self.history)
        other[0] = 'CH-0002'
        self.responses[2].append(other)
        self.unavailable()

    def test_source_overflow_is_not_truncated_success(self):
        self.responses[1] *= 101
        self.unavailable()

    def test_overlarge_cell_and_byte_budget_fail(self):
        self.merchant[3] = 'x' * 1000000
        self.unavailable()
        self.setUp()
        with patch.object(usl, 'MAX_BYTES', 10):
            self.unavailable()

    def test_disconnected_filestore_or_rest_returns_no_partial_data(self):
        original = deepcopy(self.responses)
        for index in (1, 2):
            self.responses, self.closed = deepcopy(original), 0
            self.responses[index] = OSError('private endpoint credentials')
            value = self.unavailable()
            self.assertNotIn('credentials', json.dumps(value))

    def test_static_empty_sources_remain_unverified(self):
        self.responses[1:] = [[], [], [['DP-0020', 0, 0]]]
        value = self.read()
        self.assertEqual(value['status'], 'unverified')
        self.assertIn('merchant_source_empty_for_case', value['issues'])
        self.assertIn('history_source_empty_for_case', value['issues'])

    def test_unknown_versions_and_future_times_fail(self):
        original = deepcopy(self.responses)
        for index, field, value in ((1,6,'merchant-v2'),(2,5,'2999-01-01T00:00:00Z'),(2,4,'provisional_credit')):
            self.responses, self.closed = deepcopy(original), 0
            self.responses[index][0][field] = value
            self.unavailable()

    def test_prior_observation_cannot_precede_case(self):
        self.history[5] = '2026-10-01T09:00:00Z'
        self.unavailable()

    def test_null_money_and_malformed_timestamp_fail(self):
        for field, rawfield, value in ((3,8,None),(3,8,True),(3,8,1.5),(5,10,'not a timestamp')):
            self.setUp()
            self.case[field] = self.case[rawfield] = value
            self.unavailable()

    def test_connection_and_close_failure_are_sanitized(self):
        value = usl._read_preview('DP-0020', channel_factory=Mock(side_effect=OSError('secret')))
        self.assertEqual(value.status, 'unavailable')
        channel = self.channel()
        channel.close = Mock(side_effect=OSError('secret'))
        value = usl._read_preview('DP-0020', channel_factory=lambda:channel)
        self.assertEqual(value.issues, ('source_close_failed',))

    def test_parent_refuses_bad_worker_output(self):
        for value in (b'not json', b'{}', b'x' * (usl.MAX_BYTES+1)):
            with patch.object(usl, '_bounded_worker', return_value=value):
                self.assertEqual(usl.preview_case('DP-0020', enabled=True)['status'], 'unavailable')
        with patch.object(usl, '_bounded_worker', side_effect=TimeoutError):
            self.assertEqual(usl.preview_case('DP-0020', enabled=True)['issues'], ('preview_timeout',))

    def test_worker_time_and_pipe_size_are_actually_bounded(self):
        popen = subprocess.Popen
        for script, timeout in [('import time; time.sleep(30)', .15), ('print("x" * 400000)', 5)]:
            def start(*args, **kwargs):
                return popen([sys.executable, '-c', script], **kwargs)
            with patch.object(usl.subprocess, 'Popen', side_effect=start), self.assertRaises((TimeoutError, ValueError)):
                usl._bounded_worker('DP-0020', timeout)

    def test_import_has_no_writer_or_workflow_dependency(self):
        code = "import sys; before=list(sys.path); import integration.usl_reads; assert sys.path==before; assert not any(x in sys.modules for x in ('app.action_service','app.orchestrator','app.policy_engine','app.critic','app.reviewer','psycopg','jaydebeapi'))"
        result = subprocess.run([sys.executable,'-c',code], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_fixtures_have_unique_ids_and_match_source_ownership(self):
        with (ROOT/'data/synthetic/transactions.csv').open() as f:
            transactions = {r['transaction_id']:r for r in csv.DictReader(f)}
        with (ROOT/'data/synthetic/disputes.csv').open() as f:
            cases = {r['dispute_id']:transactions[r['transaction_id']]['customer_id'] for r in csv.DictReader(f)}
        with (ROOT/'integration/usl/fixtures/merchant_evidence.csv').open() as f:
            merchants = list(csv.DictReader(f))
        history = json.loads((ROOT/'integration/usl/fixtures/customer_history.json').read_text())['history']
        self.assertEqual(len({r['evidence_id'] for r in merchants}), 4)
        self.assertEqual(len({r['history_id'] for r in history}), 3)
        for r in merchants:
            self.assertEqual(cases[r['dispute_id']], r['customer_id'])
        for r in history:
            self.assertEqual(cases[r['current_dispute_id']], cases[r['prior_dispute_id']])
            self.assertEqual(r['prior_outcome'], 'unknown')


@unittest.skipUnless(os.environ.get('DISPUTE_UI_HTTP_TESTS') == '1', 'NOT RUN: loopback fixtures require DISPUTE_UI_HTTP_TESTS=1')
class UslHttpTests(unittest.TestCase):
    def serve(self, handler):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        def cleanup():
            server.shutdown()
            server.server_close()
            thread.join()
        self.addCleanup(cleanup)
        return server

    def request(self, server, method, path):
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_default_disabled_and_invalid_input_never_dispatch(self):
        from app.ui import handler_for
        jobs, preview = Mock(), Mock()
        server = self.serve(handler_for(jobs, usl_preview=preview))
        self.assertFalse(json.loads(self.request(server,'GET','/api/config')[1])['usl_enabled'])
        self.assertEqual(json.loads(self.request(server,'GET','/api/usl?id=DP-0020')[1])['status'], 'disabled')
        self.assertEqual(self.request(server,'GET','/api/usl?id=DP-0020&id=DP-0014')[0], 400)
        self.assertEqual(self.request(server,'GET','/api/usl?id=anything')[0], 400)
        preview.assert_not_called()
        jobs.submit.assert_not_called()

    def test_optional_preview_success_or_failure_cannot_submit_job(self):
        from app.ui import handler_for
        jobs = Mock()
        preview = Mock(return_value={'status':'unverified','financial_action_authority':False})
        server = self.serve(handler_for(jobs, usl_enabled=True, usl_preview=preview,
            inventory=Mock(side_effect=RuntimeError('inventory unavailable'))))
        self.assertEqual(self.request(server,'GET','/api/inventory')[0], 503)
        self.assertEqual(self.request(server,'GET','/api/usl?id=DP-0020')[0], 200)
        preview.assert_called_once_with('DP-0020', enabled=True, timeout_seconds=180)
        preview.side_effect = RuntimeError('private source password')
        status, body = self.request(server,'GET','/api/usl?id=DP-0020')
        self.assertEqual(status, 503)
        self.assertNotIn(b'password', body)
        jobs.submit.assert_not_called()
        jobs.recoveries.assert_not_called()

    def test_fixture_service_only_serves_fixed_get_route(self):
        from integration.usl_sources.server import Handler
        server = self.serve(Handler)
        status, data = self.request(server,'GET','/v1/history')
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(data)['history']), 3)
        for method, path in (('POST','/v1/history'), ('GET','/v1/history?url=x'), ('GET','/../../.env.local')):
            self.assertIn(self.request(server,method,path)[0], (404, 501))
