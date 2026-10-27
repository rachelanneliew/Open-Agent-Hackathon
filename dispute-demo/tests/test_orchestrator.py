"""Explicitly offline model/storage stubs; never live integration evidence."""
from dataclasses import replace
from datetime import timedelta
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from app.fresh_tools import FreshSnapshot
from app.investigator import Investigator
from app.reviewer import Reviewer
from app.journal import FileJournal, load_request
from app.orchestrator import Budgets, Controller
from app.runtime_io import BoundaryError
from app.schemas import CommitResult, ExecutionStatus, Outcome
from app.tools import CustomerHistory, DecisionHistory
import test_tools


class ScriptedClient:
    """Fault-injection test client, never imported by runtime code."""
    config = SimpleNamespace(route='test/stub')

    def __init__(self, scripts=()):
        self.scripts, self.calls = list(scripts), []

    def complete(self, messages, **kwargs):
        value = json.loads(messages[1]['content'])
        self.calls.append(value)
        policy = value['policy']
        proposal = dict(recommendation=dict(outcome=policy['allowed_outcomes'][0],
            currency=policy['currency'], amount_minor=policy['credit_limit_minor']),
            evidence_ids=sorted({e for c in policy['rule_checks'] for e in c['evidence_ids']}),
            policy_rule_ids=[c['policy_rule_id'] for c in policy['rule_checks'] if c['status'] != 'not_evaluated'],
            missing_evidence=policy['missing_evidence'])
        obj = dict(kind='proposal', proposal=proposal, request=None, uncertainties=[])
        if self.scripts:
            step = self.scripts.pop(0)
            if isinstance(step, Exception):
                raise step
            obj = step(obj, value)
        return {'model': 'test/stub', 'choices': [{'finish_reason': 'stop',
            'message': {'role': 'assistant', 'content': json.dumps(obj)}}]}


class ScriptedReviewerClient:
    """Separate scripted Agent 2 completion, explicitly test-only."""
    config = SimpleNamespace(route='test/scripted-reviewer')

    def __init__(self, scripts=()):
        self.scripts, self.calls = list(scripts), []

    def complete(self, messages, **kwargs):
        value = json.loads(messages[1]['content'])
        self.calls.append(value)
        obj = dict(verdict='accept', issue_codes=[], evidence_ids=[], policy_rule_ids=[],
                   feedback='SCRIPTED reviewer acceptance for isolated testing.', uncertainties=[])
        if self.scripts:
            step = self.scripts.pop(0)
            if isinstance(step, Exception):
                raise step
            obj = step(obj, value)
        return {'model': 'test/scripted-reviewer', 'choices': [{'finish_reason': 'stop',
            'message': {'role': 'assistant', 'content': json.dumps(obj)}}]}


def reviewer_objection(obj, _):
    return dict(obj, verdict='revise', issue_codes=['material_omission'],
                feedback='SCRIPTED challenge: recheck supporting evidence and policy precedence.')


def faulty(obj, _):
    obj['proposal']['recommendation']['amount_minor'] += 1
    return obj


def read_request(name='get_customer_history'):
    return lambda obj, v: dict(kind='read', request=dict(name=name,
        dispute_id=v['policy']['reference']['dispute_id']), proposal=None, uncertainties=[])


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.source = test_tools.RetrievalTests()
        self.source.setUp()
        self.addCleanup(self.source.tearDown)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.journal = FileJournal(temporary.name)
        self.client = ScriptedClient()
        self.reviewer_client = ScriptedReviewerClient()
        self.reads = Mock(side_effect=lambda did, **_: self.snapshot(did))
        self.writer = Mock(side_effect=self.committed)
        self.controller = Controller(investigator=Investigator(self.client), reviewer=Reviewer(self.reviewer_client), read_snapshot=self.reads,
            commit=self.writer, journal=self.journal, mode='offline_test')

    def snapshot(self, did='DP-0014'):
        c = self.source.tools.get_dispute_context(did).data
        c = replace(c, reference=replace(c.reference, source_revision=10))
        anchor = next(t for t in c.transactions if t.transaction_id == c.dispute.transaction_id)
        return FreshSnapshot(context=c, history=CustomerHistory(dispute_id=did, customer_id=anchor.customer_id,
            snapshot_id=c.reference.snapshot_id, evaluation_at=c.reference.evaluation_at,
            captured_at=c.captured_at, source_revision=10, source_channel='offline_test', cases=()),
            decisions=DecisionHistory(reference=c.reference, captured_at=c.captured_at,
                source_channel='offline_test', decisions=()))

    @staticmethod
    def committed(request, **_):
        return CommitResult(run_id=request.run_id, proposal_id=request.proposal.proposal_id,
            idempotency_key=request.idempotency_key, reference=request.context.reference,
            status=ExecutionStatus.COMMITTED, message='Explicit test-only commit stub',
            decision_id=str(uuid4()), recommendation=request.proposal.recommendation,
            committed_at=request.context.captured_at + timedelta(seconds=1),
            simulated_credit_id=str(uuid4()) if request.proposal.recommendation.outcome is Outcome.PROVISIONAL_CREDIT else None)

    def test_four_outcomes_use_same_critic_writer_no_memory_or_sqlite(self):
        with patch('sqlite3.connect', side_effect=AssertionError('No SQLite writes')):
            # Source fixture was assembled before patch; snapshot reads need its
            # existing connection only, never a new one.
            for did in ('DP-0014', 'DP-0019', 'DP-0024', 'DP-0029'):
                r = self.controller.run(did)
                self.assertTrue(r.persisted, r.to_dict())
                self.assertEqual(r.memory_mode, 'no_memory')
                request = load_request(r.recovery_request)
                self.assertEqual(request, self.writer.call_args.args[0])
                self.assertEqual(Path(r.recovery_request).stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.writer.call_count, 4)

    def test_fault_corrected_exactly_once_before_one_write(self):
        self.client.scripts = [faulty]
        r = self.controller.run('DP-0014')
        self.assertTrue(r.persisted)
        self.assertEqual((r.state.model_calls, r.state.proposal_revision), (3, 1))
        self.assertEqual(self.writer.call_count, 1)
        self.assertIsNotNone(self.client.calls[1]['correction'])
        proposals = [e['result']['proposal'] for e in r.events if e['kind'] == 'investigator']
        self.assertNotEqual(proposals[0]['proposal_id'], proposals[1]['proposal_id'])

    def test_second_fault_terminal_no_credit_or_fabricated_review(self):
        self.client.scripts = [faulty, faulty]
        r = self.controller.run('DP-0014')
        self.assertFalse(r.persisted)
        self.assertEqual(r.state.error, 'critic_unresolved_no_action')
        self.assertEqual(r.state.model_calls, 2)
        self.writer.assert_not_called()

    def test_new_reads_invalidate_context_and_recompute_policy(self):
        first = self.snapshot()
        self.source.db.execute("UPDATE dispute.settlements SET amount_minor=5000 WHERE movement_type='refund' AND transaction_id='TX-0014'")
        second = self.snapshot()
        self.reads.side_effect = [first, second]
        self.client.scripts = [read_request('get_dispute_context')]
        r = self.controller.run('DP-0014')
        self.assertTrue(r.persisted)
        self.assertNotEqual(self.client.calls[0]['policy']['reference'], self.client.calls[1]['policy']['reference'])
        self.assertEqual(r.state.commit_result.recommendation.amount_minor, 5000)

    def test_every_read_projection_uses_current_binding(self):
        for name in ('get_customer_history', 'get_dispute_state', 'get_existing_decisions'):
            self.client.scripts = [read_request(name)]
            r = self.controller.run('DP-0014')
            self.assertTrue(r.persisted, r.to_dict())
            self.assertEqual(r.state.tool_calls, 2)

    def test_read_during_correction_does_not_reset_budget(self):
        self.client.scripts = [faulty, read_request()]
        r = self.controller.run('DP-0014')
        self.assertEqual(r.state.error, 'new_read_during_correction_requires_new_run')
        self.assertEqual(self.reads.call_count, 1)
        self.writer.assert_not_called()

    def test_tool_and_model_budgets_count_attempts(self):
        self.client.scripts = [read_request()] * 8
        r = self.controller.run('DP-0014')
        self.assertEqual(r.state.error, 'tool_budget_exhausted')
        self.assertEqual((r.state.tool_calls, r.state.model_calls), (3, 3))
        self.controller.budgets = Budgets(model_calls=1)
        self.client.scripts = [faulty]
        r = self.controller.run('DP-0014')
        self.assertEqual(r.state.error, 'model_budget_exhausted')
        self.writer.assert_not_called()

    def test_duration_exhaustion_after_read_never_calls_model(self):
        self.controller.clock = Mock(side_effect=[0, 0, 301])
        r = self.controller.run('DP-0014')
        self.assertEqual(r.state.error, 'total_duration_exhausted')
        self.assertEqual(r.state.tool_calls, 1)
        self.assertEqual(self.client.calls, [])

    def test_required_read_failure_or_cross_case_never_writes(self):
        for value in (BoundaryError('read_timeout'), self.snapshot('DP-0001')):
            self.reads.side_effect = [value]
            r = self.controller.run('DP-0014')
            self.assertFalse(r.persisted)
        self.writer.assert_not_called()

    def test_unavailable_malformed_uncertain_model_never_writes(self):
        scripts = [OSError('SECRET'), lambda o, v: {'extra': 'bad'},
                   lambda o, v: dict(o, uncertainties=['Missing fact'])]
        for step in scripts:
            self.client.scripts = [step]
            r = self.controller.run('DP-0014')
            self.assertFalse(r.persisted)
            self.assertNotIn('SECRET', json.dumps(r.to_dict()))
        self.writer.assert_not_called()

    def test_journal_failure_prevents_commit(self):
        self.journal.prepare = Mock(side_effect=OSError('SECRET'))
        r = self.controller.run('DP-0014')
        self.assertFalse(r.persisted)
        self.writer.assert_not_called()

    def test_commit_timeout_retains_identical_recovery_request(self):
        self.writer.side_effect = BoundaryError('commit_timeout')
        r = self.controller.run('DP-0014')
        self.assertFalse(r.persisted)
        self.assertEqual(r.state.commit_result.status, ExecutionStatus.FAILED)
        request = load_request(r.recovery_request)
        self.assertEqual(request, self.writer.call_args.args[0])
        original = self.committed(request)
        self.writer.side_effect = lambda req, **_: replace(original, status=ExecutionStatus.REUSED)
        calls = len(self.client.calls)
        recovered = self.controller.retry(request, r.recovery_request)
        self.assertTrue(recovered.persisted)
        self.assertEqual(recovered.state.commit_result.decision_id, original.decision_id)
        self.assertEqual(len(self.client.calls), calls)
        self.assertEqual(self.writer.call_args.args[0], request)

    def test_optional_work_and_trace_failure_preserve_confirmed_commit(self):
        self.controller.post_commit = Mock(side_effect=OSError('SECRET'))
        self.journal.finish = Mock(side_effect=OSError('SECRET'))
        r = self.controller.run('DP-0014')
        self.assertTrue(r.persisted)
        self.assertEqual(self.writer.call_count, 1)
        self.assertNotIn('SECRET', json.dumps(r.to_dict()))

    def test_invalid_commit_binding_never_claims_persistence(self):
        self.writer.side_effect = lambda request, **_: replace(self.committed(request), run_id=str(uuid4()))
        r = self.controller.run('DP-0014')
        self.assertFalse(r.persisted)
        self.assertIn('unconfirmed', r.state.commit_result.message)

    def test_historical_null_revision_cannot_enter_controller(self):
        self.reads.side_effect = [self.source.tools.get_dispute_context('DP-0014').data]
        r = self.controller.run('DP-0014')
        self.assertFalse(r.persisted)
        self.writer.assert_not_called()

    def test_invalid_budgets(self):
        for kwargs in ({'model_calls': True}, {'tool_calls': 0}, {'total_seconds': float('nan')},
                       {'model_seconds': 181}, {'total_seconds': float('inf')}):
            with self.assertRaises(ValueError):
                Budgets(**kwargs)

    def test_runtime_worker_hard_deadline_and_sanitized_errors(self):
        import subprocess
        from app import runtime_io
        with patch.object(runtime_io.subprocess, 'run', side_effect=subprocess.TimeoutExpired('safe', .01)):
            with self.assertRaisesRegex(BoundaryError, '^read_timeout$'):
                runtime_io.read_snapshot('DP-0014', timeout_seconds=.01)
        with patch.object(runtime_io.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='SECRET')):
            with self.assertRaisesRegex(BoundaryError, '^read_unavailable$'):
                runtime_io.read_snapshot('DP-0014', timeout_seconds=.01)


if __name__ == '__main__':
    unittest.main()
