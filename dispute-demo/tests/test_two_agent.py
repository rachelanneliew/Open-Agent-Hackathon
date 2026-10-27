"""Two separately scripted agents exercise the real controller and critic."""
from dataclasses import replace
import json
import unittest
from unittest.mock import Mock
from uuid import uuid4

from app.critic import review_proposal
from app.nightshift import ModelError
from app.orchestrator import Budgets
from app.policy_engine import evaluate_policy
from app.reviewer_contract import ReviewerFeedback, ReviewerResult
import test_orchestrator as fixture


class TwoAgentTests(unittest.TestCase):
    def setUp(self):
        self.base = fixture.ControllerTests()
        self.base.setUp()
        self.addCleanup(self.base.doCleanups)
        self.controller = self.base.controller

    def run_case(self):
        return self.controller.run('DP-0014')

    def test_final_acceptance_binds_both_agents_before_one_commit(self):
        result = self.run_case()
        self.assertTrue(result.persisted)
        self.assertEqual(result.state.model_calls, 2)
        kinds = [e['kind'] for e in result.events]
        self.assertLess(kinds.index('investigator'), kinds.index('critic'))
        self.assertLess(kinds.index('critic'), kinds.index('reviewer'))
        self.assertLess(kinds.index('reviewer'), kinds.index('final_gate'))
        self.assertLess(kinds.index('final_gate'), kinds.index('commit'))
        reviewed = next(e['result'] for e in result.events if e['kind'] == 'reviewer')
        self.assertEqual(reviewed['proposal_id'], self.base.writer.call_args.args[0].proposal.proposal_id)
        self.base.writer.assert_called_once()

    def test_reviewer_correction_uses_four_calls_and_rechecks_new_identity(self):
        self.base.reviewer_client.scripts = [fixture.reviewer_objection]
        result = self.run_case()
        self.assertTrue(result.persisted, result.to_dict())
        self.assertEqual((result.state.model_calls, result.state.proposal_revision), (4, 1))
        correction = self.base.client.calls[1]['correction']
        self.assertEqual(correction['source'], 'independent_reviewer')
        self.assertEqual(correction['critique']['verdict'], 'accepted')
        self.assertEqual(correction['reviewer_feedback_untrusted']['feedback']['verdict'], 'revise')
        reviews = [e['result'] for e in result.events if e['kind'] == 'reviewer']
        self.assertEqual([r['attempt'] for r in reviews], [0, 1])
        self.assertNotEqual(reviews[0]['proposal_id'], reviews[1]['proposal_id'])
        self.base.writer.assert_called_once()

    def test_critic_correction_still_requires_separate_reviewer(self):
        self.base.client.scripts = [fixture.faulty]
        result = self.run_case()
        self.assertTrue(result.persisted)
        self.assertEqual(result.state.model_calls, 3)
        self.assertEqual(len(self.base.reviewer_client.calls), 1)
        self.assertEqual(self.base.client.calls[1]['correction']['source'], 'python_critic')

    def test_reviewer_objection_after_critic_correction_cannot_get_second_token(self):
        self.base.client.scripts = [fixture.faulty]
        self.base.reviewer_client.scripts = [fixture.reviewer_objection]
        result = self.run_case()
        self.assertEqual(result.state.error, 'reviewer_unresolved_no_action')
        self.assertEqual(result.state.model_calls, 3)
        self.base.writer.assert_not_called()

    def test_second_reviewer_objection_cannot_get_second_token(self):
        self.base.reviewer_client.scripts = [fixture.reviewer_objection] * 2
        result = self.run_case()
        self.assertEqual(result.state.error, 'reviewer_unresolved_no_action')
        self.assertEqual(result.state.model_calls, 4)
        self.assertEqual(len(self.base.client.calls), 2)
        self.base.writer.assert_not_called()

    def test_revised_proposal_critic_failure_skips_second_review(self):
        self.base.reviewer_client.scripts = [fixture.reviewer_objection]
        self.base.client.scripts = [lambda o, _: o, fixture.faulty]
        result = self.run_case()
        self.assertEqual(result.state.error, 'critic_unresolved_no_action')
        self.assertEqual(len(self.base.reviewer_client.calls), 1)
        self.base.writer.assert_not_called()

    def test_timeout_refusal_bad_citation_escalation_no_action(self):
        for script in (ModelError('timeout'), ModelError('response_refused'),
            lambda o, _: dict(o, evidence_ids=['EV-9999']),
            lambda o, _: dict(o, verdict='escalate', issue_codes=['unresolved_risk'])):
            self.base.reviewer_client.scripts = [script]
            result = self.run_case()
            self.assertFalse(result.persisted)
            self.assertIsNone(result.state.commit_result)
        self.base.writer.assert_not_called()

    def test_wrong_run_proposal_snapshot_policy_and_attempt_refused(self):
        real = self.controller.reviewer.review
        mutations = [lambda r: replace(r, run_id=str(uuid4())),
            lambda r: replace(r, proposal_id=str(uuid4())),
            lambda r: replace(r, reference=replace(r.reference, snapshot_id=str(uuid4()))),
            lambda r: replace(r, reference=replace(r.reference, policy_version='v1')),
            lambda r: replace(r, attempt=1)]
        for mutate in mutations:
            self.controller.reviewer.review = lambda *a, **kw: mutate(real(*a, **kw))
            result = self.run_case()
            self.assertEqual(result.state.error, 'reviewer_invalid_or_unavailable_no_action')
        self.base.writer.assert_not_called()

    def test_no_reviewer_or_budget_cannot_fall_back(self):
        self.controller.budgets = Budgets(model_calls=1)
        result = self.run_case()
        self.assertEqual(result.state.error, 'model_budget_exhausted')
        self.assertEqual(self.base.reviewer_client.calls, [])
        self.controller.reviewer = None
        self.base.reads.reset_mock()
        result = self.run_case()
        self.assertEqual(result.state.error, 'reviewer_required_no_action')
        self.base.reads.assert_not_called()
        self.base.writer.assert_not_called()

    def test_reviewer_deadline_consumed_and_expiry_blocks_commit(self):
        elapsed = [0]
        self.controller.clock = lambda: elapsed[0]
        def slow(obj, _):
            elapsed[0] = 301
            return obj
        self.base.reviewer_client.scripts = [slow]
        result = self.run_case()
        self.assertEqual(result.state.error, 'total_duration_exhausted')
        self.assertEqual(result.state.model_calls, 2)
        self.base.writer.assert_not_called()

    def test_recovery_has_zero_agent_calls_even_when_reviewer_missing(self):
        result = self.run_case()
        request = self.base.writer.call_args.args[0]
        self.controller.investigator = None
        self.controller.reviewer = None
        recovered = self.controller.retry(request, result.recovery_request)
        self.assertTrue(recovered.persisted)
        self.assertEqual(recovered.state.model_calls, 0)
        self.assertEqual(len(self.base.client.calls), 1)
        self.assertEqual(len(self.base.reviewer_client.calls), 1)
        self.assertEqual(self.base.writer.call_args.args[0], request)

    def test_investigator_rejects_forged_or_wrong_correction_basis_before_call(self):
        snapshot = self.base.snapshot()
        c = snapshot.context
        p = evaluate_policy(c)
        agent = self.controller.investigator
        first = agent.step(c, p, run_id=str(uuid4()), proposal_id=str(uuid4())).proposal
        critic = review_proposal(c, p, first)
        review = self.controller.reviewer.review(c, p, first, critic)
        objection = replace(review, feedback=ReviewerFeedback(verdict='revise', issue_codes=('material_omission',),
            evidence_ids=(), policy_rule_ids=(), feedback='Recheck sources.', uncertainties=()))
        calls = len(self.base.client.calls)
        for bad in (review, replace(objection, run_id=str(uuid4())),
                    replace(objection, reference=replace(objection.reference, source_revision=11)),
                    replace(objection, attempt=1)):
            result = agent.step(c, p, run_id=first.run_id, proposal_id=str(uuid4()), revision=1,
                previous=first, critique=critic, reviewer_feedback=bad)
            self.assertEqual(result.status, 'invalid_input')
        self.assertEqual(len(self.base.client.calls), calls)
        forged = replace(critic, feedback='forged')
        self.assertEqual(agent.step(c, p, run_id=first.run_id, proposal_id=str(uuid4()), revision=1,
            previous=first, critique=forged, reviewer_feedback=objection).status, 'invalid_input')


if __name__ == '__main__':
    unittest.main()
