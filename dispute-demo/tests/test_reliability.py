"""T12: composed safety failures and intentionally isolated reset/replay.

PostgreSQL and H-MEM are real where flagged. Model responses are scripted and
source reads use the isolated database, never the live Zetaris transport.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from app.action_service import commit_simulated_decision
from app.journal import load_request
from app.runtime_io import BoundaryError
from app.ui_jobs import Jobs
import test_action_service as actions
import test_end_to_end as workflow
from test_orchestrator import faulty, reviewer_objection

ROOT = Path(__file__).resolve().parents[1]


class RuntimeImportTests(unittest.TestCase):
    def test_normal_packages_import_without_test_path_injection_or_connections(self):
        code = '''
import importlib, socket, subprocess, sys
from unittest.mock import patch
before = list(sys.path)
modules = ('app.main', 'app.ui', 'app.orchestrator', 'app.action_service',
 'app.investigator', 'app.reviewer', 'app.reviewer_contract', 'app.nightshift', 'app.history', 'app.memory_workflow',
 'app.fresh_tools', 'app.runtime_io', 'integration.fresh_reads',
 'integration.analyst_reads', 'agent.hmem_client', 'agent.memory_service',
 'agent.critic', 'agent.policy_engine', 'agent.resolver', 'demo.replay', 'demo.verify')
with patch('socket.socket', side_effect=AssertionError('Import network')), \\
     patch('subprocess.Popen', side_effect=AssertionError('Import process')):
 for name in modules: importlib.import_module(name)
assert sys.path == before
assert not any(name in sys.modules for name in ('psycopg', 'jaydebeapi', 'jpype', 'sqlite3'))
assert not any(name.startswith('test_') or 'expected_results' in name for name in sys.modules)
print(len(modules))
'''
        result = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '21')

    def test_replay_default_is_read_only_preview_and_rejects_arbitrary_targets(self):
        from demo import replay
        with patch.object(replay.subprocess, 'run', side_effect=AssertionError('No execution in preview')):
            with patch('builtins.print') as output:
                self.assertEqual(replay.main([]), 0)
            self.assertEqual(json.loads(output.call_args.args[0])['status'], 'preview_only')
        for args in (['--dsn', 'shared'], ['--memory-dir', '/tmp/shared'], ['--container', 'shared']):
            with patch('sys.stderr'), self.assertRaises(SystemExit) as error:
                replay.main(args)
            self.assertEqual(error.exception.code, 2)

    def test_cleanup_refuses_unowned_container_or_bound_host_directory(self):
        from types import SimpleNamespace
        good = dict(Id='owned-id', Name='/dispute-t05-test-owned', Config=dict(
            Image='postgres:16-alpine', Labels={'dispute-purpose':'t05-isolated-test'}),
            Mounts=[{'Type':'volume'}])
        for changed in (dict(good, Id='someone-else'), dict(good, Name='/shared'),
                        dict(good, Mounts=[{'Type':'bind'}]),
                        dict(good, Config=dict(Image='postgres:16-alpine', Labels={}))):
            fake = SimpleNamespace(container='owned-id', docker=Mock(return_value=SimpleNamespace(
                returncode=0, stdout=json.dumps([changed]))))
            with self.assertRaisesRegex(AssertionError, 'ownership mismatch'):
                ReliabilityDatabaseTests.cleanup.__func__(fake)
            self.assertEqual(fake.docker.call_args_list[0].args, ('inspect', 'owned-id'))
            self.assertEqual(fake.docker.call_count, 1)


@unittest.skipUnless(os.environ.get('DISPUTE_ACTION_TESTS') == '1',
                     'NOT RUN: real disposable PostgreSQL requires DISPUTE_ACTION_TESTS=1')
class ReliabilityDatabaseTests(unittest.TestCase):
    docker = classmethod(actions.ActionServiceTests.docker.__func__)
    sql = classmethod(actions.ActionServiceTests.sql.__func__)
    setUpClass = classmethod(workflow.FreshDatabaseTests.setUpClass.__func__)
    connect = actions.ActionServiceTests.connect
    value = actions.ActionServiceTests.value
    source_write = actions.ActionServiceTests.source_write
    tearDown = actions.ActionServiceTests.tearDown
    snapshot = workflow.FreshDatabaseTests.snapshot

    @classmethod
    def cleanup(cls):
        # Only a container created by this fixture may be removed. No compose,
        # name prefix sweep, shared volume or user-supplied resource is accepted.
        inspected = cls.docker('inspect', cls.container)
        if inspected.returncode:
            raise AssertionError('Owned replay container cannot be verified; cleanup refused')
        row = json.loads(inspected.stdout)[0]
        if (row['Id'] != cls.container or
            not row['Name'].startswith('/dispute-t05-test-') or
            row['Config']['Labels'].get('dispute-purpose') != 't05-isolated-test' or
            row['Config']['Image'] != 'postgres:16-alpine' or
            any(m['Type'] != 'volume' for m in row['Mounts'])):
            raise AssertionError('Replay ownership mismatch; cleanup refused')
        actions.ActionServiceTests.cleanup.__func__(cls)

    def setUp(self):
        workflow.FreshDatabaseTests.setUp(self)
        self._new_memory()

    def _new_memory(self):
        temporary = tempfile.TemporaryDirectory(prefix='dispute-t12-')
        self.addCleanup(temporary.cleanup)
        self.memory_root = Path(temporary.name) / 'memory'

    def empty(self):
        for table in ('investigations', 'decisions', 'simulated_credits', 'credit_reservations', 'audit_events', 'review_queue'):
            self.assertEqual(self.value(f'SELECT count(*) FROM dispute_actions.{table}'), 0, table)

    def source_hashes(self):
        return {name: self.value(f'SELECT md5(jsonb_agg(t ORDER BY 1)::text) FROM '
            f'(SELECT * FROM public.{name} ORDER BY 1) t') for name in
            ('transactions', 'settlements', 'disputes', 'evidence', 'evidence_documents', 'policy_rules')}

    def via_ui(self, did='DP-0014'):
        def factory(journal):
            self.controller.journal = journal
            return self.controller
        with tempfile.TemporaryDirectory(prefix='dispute-t12-ui-') as temporary:
            jobs = Jobs(Path(temporary) / 'ui', self.controller.journal.directory,
                controller_factory=factory, memory_retry=lambda _: self.fail('Unexpected retry'))
            try:
                op = jobs.submit(dict(operation_id=str(uuid4()), dispute_id=did, kind='investigate', run_id=None))
                for thread in jobs.threads:
                    thread.join(30)
                    self.assertFalse(thread.is_alive())
                result = jobs.get(op['operation_id'])
                self.assertEqual(result['status'], 'finished', result)
                return result['result']
            finally:
                jobs.close()

    def test_provider_and_required_data_timeouts_create_no_decision_or_queue(self):
        for mode in ('provider', 'data'):
            with self.subTest(mode=mode):
                if mode == 'provider':
                    self.client.scripts = [TimeoutError('private provider failure')]
                else:
                    self.controller.read_snapshot = Mock(side_effect=BoundaryError('read_timeout'))
                result = self.via_ui('DP-0008')
                self.assertFalse(result['persisted'])
                self.assertIsNone(result['state']['commit_result'])
                self.assertNotIn('private provider failure', json.dumps(result))
                self.assertEqual(result['state']['error'], 'investigator_unavailable' if mode == 'provider' else 'read_timeout')
                self.empty()

    def test_real_audit_failure_rolls_back_through_ui_and_memory_is_not_saved(self):
        memory = Mock()
        memory.recall.return_value = ()
        self.controller.memory_factory = lambda _: memory
        before = self.value('SELECT revision FROM dispute_control.source_revision')
        self.sql("CREATE FUNCTION public.t12_fail_audit() RETURNS trigger LANGUAGE plpgsql AS $$ "
                 "BEGIN RAISE EXCEPTION 'intentional test failure'; END $$; "
                 "CREATE TRIGGER t12_failure BEFORE INSERT ON dispute_actions.audit_events "
                 "FOR EACH ROW EXECUTE FUNCTION public.t12_fail_audit();", self.database)
        result = self.via_ui('DP-0008')
        self.assertFalse(result['persisted'])
        self.assertEqual(result['state']['commit_result']['status'], 'rejected')
        self.assertIsNone(result['state']['commit_result']['decision_id'])
        memory.save.assert_not_called()
        self.empty()
        self.assertEqual(self.value('SELECT revision FROM dispute_control.source_revision'), before)

    def test_lost_review_ack_is_unconfirmed_then_recovers_actual_queue(self):
        self.controller.commit = lambda req, **_: commit_simulated_decision(req,
            connect=lambda: actions.ConnectionProxy(self.connect(), lost_ack=True))
        result = self.via_ui('DP-0008')
        self.assertFalse(result['persisted'])
        self.assertEqual(result['state']['commit_result']['status'], 'failed')
        self.assertIsNone(result['state']['commit_result']['decision_id'])
        self.assertEqual(self.value('SELECT count(*) FROM public.dispute_pending_reviews'), 1)
        path = self.controller.journal.directory / (result['state']['run_id'] + '.request.json')
        calls = len(self.client.calls)
        self.controller.commit = lambda req, **_: commit_simulated_decision(req, connect=self.connect)
        recovered = self.controller.retry(load_request(path), str(path))
        self.assertTrue(recovered.persisted)
        self.assertEqual(recovered.state.commit_result.status.value, 'reused')
        self.assertEqual(len(self.client.calls), calls)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 0)

    @unittest.skipUnless(os.environ.get('DISPUTE_HMEM_TESTS') == '1', 'NOT RUN: real H-MEM requires DISPUTE_HMEM_TESTS=1')
    def test_reset_replay_twice(self):
        from agent.hmem_client import HmemClient
        from agent.memory_service import DisputeMemory
        reports = []
        pristine = self.source_hashes()
        def source_files():
            return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for folder in ('data/synthetic', 'policies', 'tests/fixtures')
                    for p in (ROOT / folder).rglob('*') if p.is_file()}
        original_files = source_files()
        for cycle in range(2):
            if cycle:
                # Explicit reset of the previously created disposable DB only.
                # Memory/journal get new private namespaces; old temp trees are
                # removed by their owning TemporaryDirectory cleanup callbacks.
                self.tearDown()
                self.setUp()
            self.empty()
            self.assertEqual(self.value('SELECT revision FROM dispute_control.source_revision'), 0)
            self.assertFalse(self.memory_root.exists())
            self.controller.memory_factory = lambda seconds: DisputeMemory(HmemClient(self.memory_root, timeout=seconds))
            records = []
            first = None
            for did, outcome in [('DP-0014', 'provisional_credit'), ('DP-0020', 'request_evidence'),
                                 ('DP-0029', 'decline'), ('DP-0008', 'human_review'),
                                 ('DP-0017', 'provisional_credit'), ('DP-0033', 'decline'),
                                 ('DP-0034', 'provisional_credit'), ('DP-0003', 'provisional_credit')]:
                if did == 'DP-0020':
                    self.reviewer_client.scripts = [reviewer_objection]
                if did == 'DP-0003':
                    self.client.scripts = [faulty]  # Explicit +1 fault, corrected once.
                result = self.controller.run(did)
                self.assertTrue(result.persisted, result.to_dict())
                receipt = result.state.commit_result
                self.assertEqual(receipt.recommendation.outcome.value, outcome)
                self.assertEqual(result.events[-1]['status'], 'stored')
                if did == 'DP-0014':
                    first = result
                    self.assertEqual(receipt.recommendation.amount_minor, 6000)
                if did == 'DP-0017':
                    verified = [e for e in result.events if e['kind'] == 'memory_verified']
                    self.assertTrue(verified, result.events)
                    self.assertIn(first.state.commit_result.decision_id, json.dumps(verified))
                if did in ('DP-0033', 'DP-0034'):
                    self.assertEqual(receipt.reference.policy_version, 'v1' if did == 'DP-0033' else 'v2')
                if did == 'DP-0003':
                    self.assertEqual((result.state.model_calls, result.state.proposal_revision), (3, 1))
                if did == 'DP-0020':
                    self.assertEqual((result.state.model_calls, result.state.proposal_revision), (4, 1))
                    self.assertEqual([e['result']['feedback']['verdict'] for e in result.events if e['kind'] == 'reviewer'], ['revise', 'accept'])
                records.append(dict(dispute_id=did, receipt=receipt.to_dict(),
                    collaboration=[e for e in result.events if e['kind'] in ('investigator', 'critic', 'reviewer', 'correction', 'final_gate')],
                    critic=[e['result']['verdict'] for e in result.events if e['kind'] == 'critic'][-1],
                    model_calls=result.state.model_calls, correction=result.state.proposal_revision,
                    memory=[e for e in result.events if e['kind'] in ('memory_verified', 'memory_save')]))
            recovered = self.controller.retry(load_request(first.recovery_request), first.recovery_request)
            self.assertEqual(recovered.state.commit_result.status.value, 'reused')
            self.assertEqual(recovered.state.commit_result.decision_id, first.state.commit_result.decision_id)
            repeated = self.controller.run('DP-0014')
            self.assertFalse(repeated.persisted)
            self.assertEqual(repeated.state.commit_result.message, 'effective_credit_already_exists')
            self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 8)
            self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 4)
            self.assertEqual(self.value('SELECT count(*) FROM public.dispute_pending_reviews'), 1)
            self.assertEqual(self.source_hashes(), pristine)
            reports.append(dict(cycle=cycle + 1, database=self.database, initial_decisions=0,
                initial_revision=0, initial_memory_empty=True, decisions=8, credits=4,
                pending_reviews=1, source_hashes=pristine, records=records,
                exact_retry='reused', ordinary_rerun='effective_credit_already_exists'))
        self.assertNotEqual(reports[0]['database'], reports[1]['database'])
        self.assertTrue({r['receipt']['decision_id'] for r in reports[0]['records']}.isdisjoint(
            r['receipt']['decision_id'] for r in reports[1]['records']))
        self.assertEqual(source_files(), original_files)
        if os.environ.get('DISPUTE_REPLAY_TESTS') == '1':
            print('REPLAY_JSON=' + json.dumps(dict(cycles=reports, source_files_unchanged=True)))


if __name__ == '__main__':
    unittest.main()
