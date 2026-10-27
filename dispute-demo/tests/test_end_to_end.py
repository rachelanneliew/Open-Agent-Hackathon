"""Real isolated PostgreSQL + canonical controller + labelled scripted model.

No live Zetaris/Nightshift claim. Uses only the disposable T05 fixture lifecycle.
"""
from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import unittest

from app.action_service import commit_simulated_decision
from app.fresh_tools import snapshot_from_bundle
from app.investigator import Investigator
from app.reviewer import Reviewer
from app.journal import FileJournal, load_request
from app.orchestrator import Controller
from app.schemas import ExecutionStatus, Outcome
import test_action_service as fixture
from test_orchestrator import ScriptedClient, ScriptedReviewerClient, faulty


@unittest.skipUnless(os.environ.get('DISPUTE_ACTION_TESTS') == '1',
                     'NOT RUN: real isolated PostgreSQL requires DISPUTE_ACTION_TESTS=1')
class FreshDatabaseTests(unittest.TestCase):
    # Reuse fixture methods without inheriting/rerunning unrelated T05 tests.
    docker = classmethod(fixture.ActionServiceTests.docker.__func__)
    sql = classmethod(fixture.ActionServiceTests.sql.__func__)
    cleanup = classmethod(fixture.ActionServiceTests.cleanup.__func__)
    connect = fixture.ActionServiceTests.connect
    value = fixture.ActionServiceTests.value
    source_write = fixture.ActionServiceTests.source_write
    tearDown = fixture.ActionServiceTests.tearDown

    @classmethod
    def setUpClass(cls):
        fixture.ActionServiceTests.setUpClass.__func__(cls)
        cls.sql((fixture.ROOT / 'db/migrations/002_fresh_read_bundle.sql').read_text())

    def setUp(self):
        fixture.ActionServiceTests.setUp(self)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.client = ScriptedClient()
        self.reviewer_client = ScriptedReviewerClient()
        self.controller = Controller(investigator=Investigator(self.client), reviewer=Reviewer(self.reviewer_client),
            read_snapshot=self.snapshot, commit=lambda request, **_: commit_simulated_decision(request, connect=self.connect),
            journal=FileJournal(temporary.name), mode='fault_injection')

    def snapshot(self, did='DP-0014', **_):
        with self.connect() as conn:
            raw = conn.execute('SELECT payload FROM public.dispute_read_bundle WHERE dispute_id=%s', (did,)).fetchone()[0]
            captured = conn.execute('SELECT clock_timestamp()').fetchone()[0]
        return snapshot_from_bundle(json.loads(raw), captured, source_channel='offline_test')

    def test_view_all_cases_fresh_revision_and_four_outcomes(self):
        for did, outcome in (('DP-0014', Outcome.PROVISIONAL_CREDIT), ('DP-0020', Outcome.REQUEST_EVIDENCE),
                             ('DP-0029', Outcome.DECLINE), ('DP-0008', Outcome.HUMAN_REVIEW)):
            result = self.controller.run(did)
            self.assertTrue(result.persisted, result.to_dict())
            self.assertEqual(result.state.commit_result.recommendation.outcome, outcome)
            snapshot = self.snapshot(did)
            self.assertEqual(snapshot.decisions.decisions[-1].decision_id, result.state.commit_result.decision_id)
            self.assertGreater(snapshot.context.reference.source_revision, result.state.reference.source_revision)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.review_queue'), 1)

    def test_exact_retry_reuses_original_ordinary_rerun_never_adds_credit(self):
        result = self.controller.run('DP-0014')
        self.assertTrue(result.persisted, result.to_dict())
        retry = self.controller.retry(load_request(result.recovery_request), result.recovery_request)
        self.assertEqual(retry.state.commit_result.status, ExecutionStatus.REUSED)
        self.assertEqual(retry.state.commit_result.decision_id, result.state.commit_result.decision_id)
        rerun = self.controller.run('DP-0014')
        self.assertFalse(rerun.persisted)
        self.assertEqual(rerun.state.commit_result.message, 'effective_credit_already_exists')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)

    def test_fault_corrected_once_before_real_commit(self):
        self.client.scripts = [faulty]
        result = self.controller.run('DP-0014')
        self.assertTrue(result.persisted, result.to_dict())
        self.assertEqual(result.state.proposal_revision, 1)
        self.assertEqual(len(self.client.calls), 2)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)

    def test_second_fault_leaves_all_action_tables_empty(self):
        self.client.scripts = [faulty, faulty]
        result = self.controller.run('DP-0014')
        self.assertFalse(result.persisted)
        self.assertEqual(result.state.error, 'critic_unresolved_no_action')
        for table in ('investigations', 'decisions', 'simulated_credits', 'audit_events', 'review_queue'):
            self.assertEqual(self.value(f'SELECT count(*) FROM dispute_actions.{table}'), 0)

    def test_changed_source_refuses_stale_model_proposal(self):
        def change(obj, _):
            self.source_write("UPDATE public.disputes SET dispute_status=dispute_status WHERE dispute_id='DP-0014'")
            return obj
        self.client.scripts = [change]
        result = self.controller.run('DP-0014')
        self.assertFalse(result.persisted)
        self.assertEqual(result.state.commit_result.message, 'source_revision_stale')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 0)

    def test_lost_commit_ack_then_exact_recovery_no_duplicate(self):
        self.controller.commit = lambda request, **_: commit_simulated_decision(request,
            connect=lambda: fixture.ConnectionProxy(self.connect(), lost_ack=True))
        result = self.controller.run('DP-0014')
        self.assertFalse(result.persisted)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)
        self.controller.commit = lambda request, **_: commit_simulated_decision(request, connect=self.connect)
        retry = self.controller.retry(load_request(result.recovery_request), result.recovery_request)
        self.assertEqual(retry.state.commit_result.status, ExecutionStatus.REUSED)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_reviewer_objection_revision_and_recheck_before_real_commit(self):
        from test_orchestrator import reviewer_objection
        self.reviewer_client.scripts = [reviewer_objection]
        result = self.controller.run('DP-0014')
        self.assertTrue(result.persisted, result.to_dict())
        self.assertEqual(result.state.model_calls, 4)
        self.assertEqual(len(self.client.calls), 2)
        self.assertEqual(len(self.reviewer_client.calls), 2)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_source_change_during_reviewer_invalidates_commit(self):
        def change(obj, _):
            self.source_write("UPDATE public.disputes SET dispute_status=dispute_status WHERE dispute_id='DP-0014'")
            return obj
        self.reviewer_client.scripts = [change]
        result = self.controller.run('DP-0014')
        self.assertFalse(result.persisted)
        self.assertEqual(result.state.commit_result.message, 'source_revision_stale')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 0)

    def test_additive_view_preserves_sources_and_exposes_only_scoped_decisions(self):
        self.assertEqual(self.value('SELECT count(*) FROM public.transactions'), 42)
        self.assertEqual(self.value('SELECT count(*) FROM public.settlements'), 54)
        self.assertEqual(self.value('SELECT count(*) FROM public.dispute_read_bundle'), 40)
        self.assertEqual(self.value('SELECT max(version) FROM dispute_control.schema_migrations'), 2)
        with self.connect('action_admin') as conn:
            conn.execute('SET ROLE dispute_reader')
            self.assertEqual(conn.execute('SELECT count(*) FROM public.dispute_read_bundle').fetchone()[0], 40)
        result = self.controller.run('DP-0014')
        self.assertTrue(result.persisted)
        self.assertEqual(self.snapshot('DP-0001').decisions.decisions, ())
