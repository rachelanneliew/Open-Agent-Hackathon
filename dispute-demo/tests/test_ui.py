"""UI coordination and real loopback HTTP tests; workflow doubles are explicit."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from http.server import ThreadingHTTPServer

from app.journal import load_request
from app.ui import browser_value, handler_for
from app.ui_jobs import Jobs, JobError, _save
from integration.analyst_reads import read_inventory
from integration import get_dispute_context as source
import test_orchestrator as fixture


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.cases = [('DP-0014', 'refund_missing', 10000, 'SGD', 'open')]
        self.queue, self.revisions, self.closed = [], [10, 10], 0
        self.plan = 'Scan InsertableJDBCTableRelation(...) DISPUTE.disputes'
        self.queries = []

    def channel(self):
        owner = self
        class Channel:
            def run(self, query, limit):
                owner.queries.append(query)
                rows = [(owner.plan,)] if query.startswith('EXPLAIN ') else (
                    [(owner.revisions.pop(0),)] if 'SELECT revision' in query else (
                    ([(r[2],r[1]) for r in owner.queue] if query.startswith('SELECT dispute_id, status ') else owner.queue)
                    if 'dispute_pending_reviews' in query else owner.cases))
                if not query.startswith('EXPLAIN ') and ' JOIN ' in query and hasattr(owner, 'joined'):
                    rows = owner.joined
                return SimpleNamespace(rows=rows)
            def close(self):
                owner.closed += 1
        return Channel()

    def test_only_source_queue_and_direct_reads_are_displayed(self):
        self.queue = [(str(uuid4()), 'queued', 'DP-0014')]
        value = read_inventory(channel_factory=self.channel)
        self.assertEqual(value['queue'][0]['decision_id'], self.queue[0][0])
        self.assertEqual(value['source_revision'], 10)
        self.assertEqual(len(self.queries), 10)
        self.assertEqual(self.closed, 1)

    def test_outage_or_invalid_queue_is_not_an_empty_success(self):
        for queue in ([(str(uuid4()), 'recommended', 'DP-0014')], [(str(uuid4()), 'queued', 'DP-9999')], [('fake', 'queued', 'DP-0014')]):
            self.queue, self.revisions = queue, [10, 10]
            with self.assertRaises(source.ReadUnavailable):
                read_inventory(channel_factory=self.channel)
        with self.assertRaises(source.ReadUnavailable):
            read_inventory(channel_factory=Mock(side_effect=OSError('private details')))

    def test_cached_or_overflow_inventory_fails_closed(self):
        self.plan = 'InMemoryTableScan'
        with self.assertRaises(source.SourceError):
            read_inventory(channel_factory=self.channel)
        self.plan = 'Scan InsertableJDBCTableRelation(...) DISPUTE.disputes'
        self.cases *= 1001
        with self.assertRaises(source.ReadIncomplete):
            read_inventory(channel_factory=self.channel)

    def test_revision_race_retries_only_twice(self):
        self.revisions = [9, 10, 10, 10]
        self.assertEqual(read_inventory(channel_factory=self.channel)['source_revision'], 10)
        self.assertEqual(self.closed, 2)
        self.revisions = [10, 11, 11, 12]
        with self.assertRaises(source.ReadIncomplete):
            read_inventory(channel_factory=self.channel)

    def test_missing_or_ambiguous_queue_receipt_join_fails_closed(self):
        self.queue = [(str(uuid4()), 'queued', 'DP-0014')]
        for joined in ([], self.queue * 2):
            self.joined, self.revisions = joined, [10, 10]
            with self.assertRaises(source.ReadUnavailable):
                read_inventory(channel_factory=self.channel)


class JobsTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.retry_memory = Mock(return_value=dict(mode='memory_retry', action_called=False))
        self.factory = Mock(side_effect=self.controller)
        self.jobs = self.open()
        self.addCleanup(lambda: self.jobs.close())

    def controller(self, journal):
        self.fixture.controller.journal = journal
        # Use immutable fixture snapshots assembled in the test thread; SQLite
        # is test-source construction only and never accessed by the job worker.
        self.fixture.controller.read_snapshot = lambda did, **_: self.snapshots[did]
        return self.fixture.controller

    def open(self):
        self.snapshots = {did:self.fixture.snapshot(did) for did in ('DP-0014', 'DP-0024')}
        return Jobs(self.directory, self.fixture.journal.directory,
                    controller_factory=self.factory, memory_retry=self.retry_memory)

    def payload(self, kind='investigate', run_id=None, did='DP-0014'):
        return dict(operation_id=str(uuid4()), dispute_id=did, kind=kind, run_id=run_id)

    def finish(self, payload):
        value = self.jobs.submit(payload)
        for thread in self.jobs.threads:
            thread.join(5)
            self.assertFalse(thread.is_alive())
        return self.jobs.get(value['operation_id'])

    def test_double_click_and_restart_reuse_one_operation(self):
        payload = self.payload()
        with ThreadPoolExecutor(4) as pool:
            values = list(pool.map(lambda _:self.jobs.submit(payload), range(4)))
        final = self.finish(payload)
        self.assertEqual({x['operation_id'] for x in values}, {payload['operation_id']})
        self.assertTrue(final['result']['persisted'])
        self.fixture.writer.assert_called_once()
        self.assertNotIn('recovery_request', final['result'])
        self.assertEqual(final['result']['display']['context']['reference']['dispute_id'], 'DP-0014')
        self.jobs.close()
        self.jobs = self.open()
        self.assertEqual(self.jobs.submit(payload), final)
        self.fixture.writer.assert_called_once()

    def test_different_key_same_inflight_case_coalesces_other_case_busy(self):
        entered, release = threading.Event(), threading.Event()
        original = self.fixture.writer.side_effect
        def blocked(*args, **kwargs):
            entered.set()
            self.assertTrue(release.wait(5))
            return original(*args, **kwargs)
        self.fixture.writer.side_effect = blocked
        first = self.jobs.submit(self.payload())
        self.assertTrue(entered.wait(5))
        try:
            self.assertEqual(self.jobs.submit(self.payload())['operation_id'], first['operation_id'])
            with self.assertRaises(JobError):
                self.jobs.submit(self.payload(did='DP-0024'))
        finally:
            release.set()
        self.finish(first['input'])
        self.fixture.writer.assert_called_once()

    def test_request_id_conflict_and_cross_case_recovery_rejected(self):
        payload = self.payload()
        result = self.finish(payload)
        with self.assertRaises(JobError):
            self.jobs.submit(dict(payload, dispute_id='DP-0024'))
        with self.assertRaises(ValueError):
            self.jobs.submit(self.payload('recover', result['run_id'], 'DP-0024'))
        with self.assertRaises(ValueError):
            self.jobs.get('../../private')
        self.fixture.writer.assert_called_once()

    def test_retry_uses_exact_request_and_memory_retry_never_calls_writer(self):
        first = self.finish(self.payload())
        request = load_request(self.fixture.journal.directory / (first['run_id'] + '.request.json'))
        recovered = self.finish(self.payload('recover', first['run_id']))
        self.assertEqual(self.fixture.writer.call_args.args[0], request)
        self.assertEqual(recovered['result']['display']['proposal'], request.proposal.to_dict())
        calls = self.fixture.writer.call_count
        memory = self.finish(self.payload('memory', first['run_id']))
        self.assertFalse(memory['result']['action_called'])
        self.assertEqual(self.fixture.writer.call_count, calls)
        self.retry_memory.assert_called_once_with(self.fixture.journal.directory / (first['run_id'] + '.trace.json'))

    def test_restart_interruptions_do_not_dispatch_automatically(self):
        payload = self.payload()
        value = dict(operation_id=payload['operation_id'], input=payload, status='running', run_id=None, result=None, error=None)
        _save(self.directory / (payload['operation_id'] + '.json'), value)
        result = self.jobs.submit(payload)
        self.assertEqual(result['status'], 'interrupted')
        self.factory.assert_not_called()
        self.fixture.writer.assert_not_called()

    def test_journal_association_failure_prevents_action_dispatch(self):
        from app import ui_jobs
        original = ui_jobs._save
        def save(path, value):
            if value['run_id'] is not None and value['status'] == 'running':
                raise OSError('disk full')
            original(path, value)
        with patch.object(ui_jobs, '_save', side_effect=save):
            result = self.finish(self.payload())
        self.assertFalse(result['result']['persisted'])
        self.fixture.writer.assert_not_called()
        self.assertEqual(len(self.jobs.recoveries('DP-0014')), 1)

    def test_second_server_refused_and_files_private(self):
        with self.assertRaises(JobError):
            self.open()
        result = self.finish(self.payload())
        path = self.directory / (result['operation_id'] + '.json')
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_bigint_display_does_not_round_money(self):
        self.assertEqual(browser_value({'amount_minor': 2**63-1}), {'amount_minor': str(2**63-1)})
        self.assertEqual(browser_value({'persisted':True,'amount_minor':6000}), {'persisted':True,'amount_minor':6000})


@unittest.skipUnless(os.environ.get('DISPUTE_UI_HTTP_TESTS') == '1',
                     'NOT RUN: loopback UI HTTP fixtures require DISPUTE_UI_HTTP_TESTS=1')
class HttpTests(unittest.TestCase):
    def setUp(self):
        self.jobs = Mock()
        self.jobs.submit.return_value = {'status':'running'}
        self.inventory = Mock(return_value={'queue':[]})
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(self.jobs, inventory=self.inventory, memory_enabled=False))
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            conn.request(method, path, body, headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_page_assets_and_security_headers(self):
        code, headers, body = self.request('GET', '/')
        self.assertEqual(code, 200)
        self.assertIn(b'Dispute workbench', body)
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'], 'no-store')
        for path in ('/app.js', '/style.css'):
            self.assertEqual(self.request('GET', path)[0], 200)
        self.assertNotEqual(self.request('GET', '/../../.env.local')[0], 200)

    def test_cross_origin_and_dns_rebinding_cannot_act(self):
        token = json.loads(self.request('GET', '/api/config')[2])['token']
        for extra in ({}, {'X-Analyst-Token':token,'Origin':'https://example.invalid'},
                      {'X-Analyst-Token':token,'Host':'evil.invalid'},
                      {'X-Analyst-Token':token,'Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.request('POST','/api/job','{}',dict(extra, **{'Content-Type':'application/json'}))[0],403)
        self.jobs.submit.assert_not_called()

    def test_valid_post_dispatches_once_and_no_memory_is_explicit(self):
        config = json.loads(self.request('GET', '/api/config')[2])
        self.assertEqual(config['memory_mode'], 'no_memory')
        headers = {'Content-Type':'application/json','X-Analyst-Token':config['token']}
        self.assertEqual(self.request('POST','/api/job','{"kind":"investigate"}',headers)[0],202)
        self.jobs.submit.assert_called_once()
        self.assertEqual(self.request('POST','/api/job','{"kind":"memory"}',headers)[0],400)
        self.jobs.submit.assert_called_once()

    def test_read_failure_is_not_empty_queue_and_secret_is_sanitized(self):
        self.inventory.side_effect = RuntimeError('private credential')
        code, _, body = self.request('GET','/api/inventory')
        self.assertEqual(code,503)
        self.assertNotIn(b'private credential',body)
        self.assertNotIn(b'"queue": []',body)

    def test_duplicate_json_and_oversized_requests_refused(self):
        config = json.loads(self.request('GET','/api/config')[2])
        headers = {'Content-Type':'application/json','X-Analyst-Token':config['token']}
        for body in ('{"kind":"investigate","kind":"memory"}', ' ' * 4097):
            self.assertEqual(self.request('POST','/api/job',body,headers)[0],400)
        self.jobs.submit.assert_not_called()
