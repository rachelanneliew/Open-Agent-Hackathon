"""Contract boundaries and representation of authored cases; not an evaluator.

CSV/fixture adapters below are test-only. Production must retrieve authoritative
data through T02 and independently evaluate it in T03.
"""
import csv
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.schemas import (
    AgentProposal, CommitResult, ContextRef, ContractError, CriticResult,
    CriticVerdict, Dispute, DisputeContext, Evidence, EvidenceRequirement,
    ExecutionStatus, MovementType, Outcome, PolicyResult, PolicyRule,
    Recommendation, RuleCheck, RunPhase, RunState, Settlement, SettlementStatus,
    Transaction, from_legacy_recommendation,
)


def identifier(name):
    return str(uuid5(NAMESPACE_URL, 'synthetic-contract-test/' + name))


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def rows(name):
    with (ROOT / 'data' / 'synthetic' / (name + '.csv')).open() as stream:
        return list(csv.DictReader(stream))


def source_payload(row):
    """Explicit source CSV conversion, never contract-level coercion."""
    return {key: (int(value) if key.endswith('_minor') else value or None)
            for key, value in row.items()}


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((ROOT / 'tests' / 'fixtures' / 'expected_results.json').read_text())
        cls.disputes = {r['dispute_id']: Dispute.from_dict(source_payload(r)) for r in rows('disputes')}
        cls.transactions = [Transaction.from_dict(source_payload(r)) for r in rows('transactions')]
        cls.settlements = [Settlement.from_dict(source_payload(r)) for r in rows('settlements')]
        cls.evidence = []
        for row in rows('evidence'):
            payload = source_payload(row)
            path = payload.pop('document_path')
            payload['content'] = (ROOT / 'data' / 'synthetic' / path).read_text()
            cls.evidence.append(Evidence.from_dict(payload))
        cls.rules = []
        action_map = {'recommend_refund': 'provisional_credit', 'reject': 'decline',
                      'escalate': 'human_review', 'request_evidence': 'request_evidence'}
        for row in rows('policy_rules'):
            payload = dict(row)
            payload.pop('rule_code')
            payload['predicate'] = json.loads(payload.pop('condition_json'))['predicate']
            payload['priority'] = int(payload['priority'])
            payload['effective_to'] = payload['effective_to'] or None
            payload['action'] = action_map[payload['action']]
            cls.rules.append(PolicyRule.from_dict(payload))

    def context(self, did='DP-0014'):
        case = self.disputes[did]
        rules = tuple(p for p in self.rules if p.effective_from <= case.opened_at and
                      (p.effective_to is None or case.opened_at < p.effective_to))
        txids = {case.transaction_id, case.related_transaction_id}
        return DisputeContext(
            reference=ContextRef(dispute_id=did, snapshot_id=identifier(did + '/snapshot'),
                                 evaluation_at=case.evaluation_at, policy_version=rules[0].policy_version),
            captured_at=case.evaluation_at, source_channel='offline_test', dispute=case,
            transactions=tuple(t for t in self.transactions if t.transaction_id in txids and t.recorded_at <= case.evaluation_at),
            settlements=tuple(s for s in self.settlements if s.transaction_id in txids and s.recorded_at <= case.evaluation_at),
            evidence=tuple(e for e in self.evidence if e.dispute_id == did and e.available_at <= case.evaluation_at),
            policy_rules=rules,
        )

    def proposal(self, context=None, recommendation=None):
        context = context or self.context()
        return AgentProposal(
            proposal_id=identifier('proposal'), run_id=identifier('run'), reference=context.reference,
            recommendation=recommendation or Recommendation(outcome=Outcome.PROVISIONAL_CREDIT, currency='SGD', amount_minor=6000),
            rationale='Test proposal; not an executed policy result.',
            evidence_ids=tuple(e.evidence_id for e in context.evidence),
            policy_rule_ids=(context.reference.policy_version + '-APPROVE',),
        )

    def persisted(self, outcome=Outcome.PROVISIONAL_CREDIT, status=ExecutionStatus.COMMITTED):
        reference = replace(self.context().reference, source_revision=7)
        return CommitResult(
            run_id=identifier('run'), proposal_id=identifier('proposal'), idempotency_key=identifier('key'),
            reference=reference, status=status, message='Constructed test result; no database write.',
            decision_id=identifier('decision'), committed_at=reference.evaluation_at,
            recommendation=Recommendation(outcome=outcome, currency='SGD',
                                          amount_minor=6000 if outcome is Outcome.PROVISIONAL_CREDIT else None),
            simulated_credit_id=identifier('credit') if outcome is Outcome.PROVISIONAL_CREDIT else None,
        )

    def roundtrip(self, value):
        self.assertEqual(type(value).from_dict(json.loads(json.dumps(value.to_dict()))), value)

    def test_all_40_authored_scenarios_are_representable_without_changing_meaning(self):
        self.assertEqual(len(self.fixtures), 40)
        groups = set()
        for fixture in self.fixtures:
            with self.subTest(dispute=fixture['dispute_id']):
                context = self.context(fixture['dispute_id'])
                self.roundtrip(context)
                groups.add(fixture['scenario_id'].split(':')[0])
                self.assertEqual(context.reference.policy_version, fixture['expected_policy_version'])
                visible_ids = {e.evidence_id for e in context.evidence}
                self.assertTrue(set(fixture['required_evidence_ids']) <= visible_ids)
                self.assertFalse(set(fixture['forbidden_evidence_ids']) & visible_ids)
                recommendation = from_legacy_recommendation(fixture['expected_outcome'], fixture['expected_refund_minor'], context.dispute.currency)
                missing = ()
                if recommendation.outcome is Outcome.REQUEST_EVIDENCE:
                    missing = (EvidenceRequirement(category='refund_confirmation',
                               reason='not_yet_available' if fixture['forbidden_evidence_ids'] else 'absent',
                               policy_rule_id=context.reference.policy_version + '-MISSING_EVIDENCE'),)
                proposal = AgentProposal(
                    proposal_id=identifier(fixture['dispute_id'] + '/proposal'), run_id=identifier('run'),
                    reference=context.reference, recommendation=recommendation,
                    rationale='Authored fixture representation only; no prediction.',
                    evidence_ids=tuple(fixture['required_evidence_ids']),
                    policy_rule_ids=tuple(fixture['required_policy_rule_ids']), missing_evidence=missing,
                )
                self.roundtrip(proposal)
                self.assertEqual(proposal.recommendation.amount_minor,
                                 fixture['expected_refund_minor'] if fixture['expected_outcome'] == 'recommend_refund' else None)
        self.assertEqual(groups, {'supported', 'full_refund', 'partial_refund', 'missing_evidence',
                                 'conflicting_evidence', 'outside_window', 'policy_pair', 'settlement_anomaly'})

    def test_merchant_refund_and_new_credit_remain_distinct(self):
        context = self.context()
        self.assertEqual([(s.movement_type, s.amount_minor) for s in context.settlements],
                         [(MovementType.CAPTURE, 10000), (MovementType.REFUND, 4000)])
        self.assertEqual(self.proposal().recommendation.amount_minor, 6000)
        reversal = replace(context.settlements[1], movement_type=MovementType.REVERSAL)
        self.roundtrip(reversal)
        for movement in ('capture', 'refund', 'reversal', 'provisional_credit'):
            with self.subTest(movement=movement), self.assertRaises(ContractError):
                from_legacy_recommendation(movement, 4000, 'SGD')

    def test_legacy_non_credit_mapping_and_amount_rejection(self):
        for legacy, expected in [('reject', Outcome.DECLINE), ('escalate', Outcome.HUMAN_REVIEW),
                                 ('request_evidence', Outcome.REQUEST_EVIDENCE)]:
            self.assertEqual(from_legacy_recommendation(legacy, 0, 'SGD'), Recommendation(outcome=expected, currency='SGD'))
            with self.assertRaises(ContractError):
                from_legacy_recommendation(legacy, 100, 'SGD')
        with self.assertRaises(ContractError):
            from_legacy_recommendation('recommend_refund', 0, 'SGD')

    def test_amounts_are_strict_positive_bigint_for_credit(self):
        payload = Recommendation(outcome=Outcome.PROVISIONAL_CREDIT, currency='SGD', amount_minor=1).to_dict()
        for invalid in (True, False, 1.0, '100', -1, 0, None, 2**63, float('nan'), [], {}):
            with self.subTest(amount=invalid), self.assertRaises(ContractError):
                Recommendation.from_dict({**payload, 'amount_minor': invalid})
        self.roundtrip(Recommendation(outcome=Outcome.PROVISIONAL_CREDIT, currency='SGD', amount_minor=2**63 - 1))
        for cls, record, field in [(Dispute, self.context().dispute, 'claimed_amount_minor'),
                                   (Transaction, self.context().transactions[0], 'amount_minor'),
                                   (Settlement, self.context().settlements[0], 'amount_minor')]:
            for bad in (True, -1, 0, '10', 2**63):
                with self.subTest(record=cls.__name__, amount=bad), self.assertRaises(ContractError):
                    cls.from_dict({**record.to_dict(), field: bad})

    def test_non_credit_has_no_amount_even_zero(self):
        for outcome in (Outcome.DECLINE, Outcome.REQUEST_EVIDENCE, Outcome.HUMAN_REVIEW):
            self.roundtrip(Recommendation(outcome=outcome, currency='SGD'))
            for amount in (0, 1, -1):
                with self.subTest(outcome=outcome, amount=amount), self.assertRaises(ContractError):
                    Recommendation(outcome=outcome, currency='SGD', amount_minor=amount)

    def test_unknown_outcomes_and_invalid_currency_rejected(self):
        for outcome in ('refund', 'approve', 'recommend_refund', 'committed', 'accepted', '', None):
            with self.subTest(outcome=outcome), self.assertRaises(ContractError):
                Recommendation.from_dict({'outcome': outcome, 'currency': 'SGD'})
        for currency in ('sgd', 'SG', 'SGDD', 'SG1', ' SGD', '', None):
            with self.subTest(currency=currency), self.assertRaises(ContractError):
                Recommendation(outcome=Outcome.DECLINE, currency=currency)

    def test_malformed_source_and_runtime_ids_rejected(self):
        context = self.context()
        records = [(context.reference, 'dispute_id', 'DP'), (context.dispute, 'transaction_id', 'TX'),
                   (context.transactions[0], 'order_id', 'OR'), (context.settlements[0], 'settlement_id', 'ST'),
                   (context.evidence[0], 'evidence_id', 'EV')]
        for record, field, prefix in records:
            for invalid in ('', prefix + '-1', prefix.lower() + '-0001', prefix + '-00001', prefix + '-１２３４', 'EV-missing', None):
                with self.subTest(field=field, invalid=invalid), self.assertRaises(ContractError):
                    replace(record, **{field: invalid})
        for invalid in ('run-1', '00000000-0000-0000-0000-000000000000', identifier('run').upper(), '', None):
            with self.subTest(uuid=invalid), self.assertRaises(ContractError):
                replace(self.proposal(), run_id=invalid)
        for field, invalid in [('customer_id', 'CUST-0001'), ('merchant_id', 'MER-1')]:
            with self.assertRaises(ContractError):
                replace(context.transactions[0], **{field: invalid})

    def test_utc_time_and_chronology(self):
        ref = self.context().reference
        for invalid in ('2026-10-01', '2026-10-01T00:00:00', '2026-10-01T08:00:00+08:00',
                        '2026-10-01T00:00:00+00:00', '2026-02-30T00:00:00Z', None):
            with self.subTest(timestamp=invalid), self.assertRaises(ContractError):
                ContextRef.from_dict({**ref.to_dict(), 'evaluation_at': invalid})
        for invalid in (datetime(2026, 10, 1), datetime(2026, 10, 1, tzinfo=timezone(timedelta(hours=8)))):
            with self.assertRaises(ContractError):
                replace(ref, evaluation_at=invalid)
        self.roundtrip(replace(ref, evaluation_at=ref.evaluation_at.replace(microsecond=123456)))
        with self.assertRaises(ContractError):
            replace(self.context().dispute, evaluation_at=self.context().dispute.opened_at - timedelta(seconds=1))
        with self.assertRaises(ContractError):
            replace(self.context().settlements[0], recorded_at=datetime(2020, 1, 1, tzinfo=timezone.utc))

    def test_unknown_missing_and_fixture_only_fields_rejected(self):
        payload = self.proposal().to_dict()
        for key in ('expected_outcome', 'expected_refund_minor', 'approved', 'simulated_credit_id'):
            with self.subTest(key=key), self.assertRaises(ContractError):
                AgentProposal.from_dict({**payload, key: 'injected'})
        payload.pop('reference')
        with self.assertRaises(ContractError):
            AgentProposal.from_dict(payload)
        with self.assertRaises(ContractError):
            AgentProposal.from_dict([])
        with self.assertRaises(FrozenInstanceError):
            self.proposal().rationale = 'mutated'

    def test_context_scope_duplicates_and_version_binding(self):
        context = self.context()
        for change in (
            {'reference': replace(context.reference, dispute_id='DP-0001')},
            {'reference': replace(context.reference, evaluation_at=context.reference.evaluation_at + timedelta(seconds=1))},
            {'transactions': context.transactions * 2},
            {'settlements': context.settlements * 2},
            {'evidence': context.evidence * 2},
            {'policy_rules': context.policy_rules * 2},
            {'transactions': self.context('DP-0001').transactions},
            {'settlements': self.context('DP-0001').settlements},
            {'evidence': self.context('DP-0001').evidence},
            {'policy_rules': self.context('DP-0001').policy_rules},
        ):
            with self.subTest(fields=list(change)), self.assertRaises(ContractError):
                replace(context, **change)

    def test_context_cutoff_is_inclusive_but_future_records_rejected(self):
        context = self.context()
        cutoff = context.reference.evaluation_at
        for field, record, timestamp in [('transactions', context.transactions[0], 'recorded_at'),
                                          ('settlements', context.settlements[0], 'recorded_at'),
                                          ('evidence', context.evidence[0], 'available_at')]:
            self.roundtrip(replace(context, **{field: (replace(record, **{timestamp: cutoff}),)}))
            with self.subTest(field=field), self.assertRaises(ContractError):
                replace(context, **{field: (replace(record, **{timestamp: cutoff + timedelta(microseconds=1)}),)})
        with self.assertRaises(ContractError):
            replace(context, captured_at=cutoff - timedelta(seconds=1))

    def test_incomplete_data_is_explicit_and_anomalies_survive(self):
        context = self.context()
        with self.assertRaises(ContractError):
            replace(context, transactions=())
        with self.assertRaises(ContractError):
            replace(context, policy_rules=())
        self.roundtrip(replace(context, transactions=(), policy_rules=(), data_issues=('Source rows unavailable',)))
        self.roundtrip(replace(context, evidence=(replace(context.evidence[0], content=None),)))
        pending = self.context('DP-0038')
        self.assertTrue(any(s.settlement_status is SettlementStatus.PENDING for s in pending.settlements))
        anomaly = self.context('DP-0039')
        self.assertGreater(sum(s.amount_minor for s in anomaly.settlements if s.movement_type is MovementType.REFUND),
                           sum(s.amount_minor for s in anomaly.settlements if s.movement_type is MovementType.CAPTURE))
        # Keep an unsupported currency or source lifecycle visible; shape is not authorization.
        self.roundtrip(replace(context, transactions=(replace(context.transactions[0], currency='USD'),)))
        self.roundtrip(replace(context, dispute=replace(context.dispute, dispute_status='future_unrecognized_status')))

    def test_policy_metadata_and_boundary_fixtures_preserve_source_semantics(self):
        expected = [
            (10, 'DATA_INTEGRITY', 'data_integrity_or_pending', Outcome.HUMAN_REVIEW),
            (20, 'FILING_WINDOW', 'filing_window_exceeded', Outcome.DECLINE),
            (30, 'ALREADY_REFUNDED', 'remaining_balance_zero', Outcome.DECLINE),
            (40, 'CONFLICTING_EVIDENCE', 'material_evidence_conflict', Outcome.HUMAN_REVIEW),
            (50, 'MISSING_EVIDENCE', 'required_evidence_missing', Outcome.REQUEST_EVIDENCE),
            (60, 'UNSUPPORTED', 'claim_not_supported', Outcome.DECLINE),
            (70, 'REVIEW_THRESHOLD', 'proposed_refund_above_limit', Outcome.HUMAN_REVIEW),
            (80, 'APPROVE', 'all_preceding_checks_pass', Outcome.PROVISIONAL_CREDIT),
        ]
        for version, days in [('v1', 30), ('v2', 45)]:
            rules = sorted((r for r in self.rules if r.policy_version == version), key=lambda r: r.priority)
            self.assertEqual([(r.priority, r.policy_rule_id.split('-', 1)[1], r.predicate, r.action) for r in rules], expected)
            self.assertEqual(json.loads(rules[1].parameters_json), {'filing_window_days': days})
            self.assertEqual(json.loads(rules[6].parameters_json), {'review_threshold_minor': 20000})
            self.assertEqual(json.loads(rules[4].parameters_json), {
                'refund_missing': ['refund_confirmation'], 'not_received': ['receipt', 'delivery_record'],
                'duplicate_charge': ['receipt', 'two_completed_captures_same_order']})
        boundary = instant('2026-10-01T00:00:00Z')
        before, after = self.context('DP-0033'), self.context('DP-0034')
        self.assertEqual(before.dispute.opened_at, boundary - timedelta(seconds=1))
        self.assertEqual(after.dispute.opened_at, boundary)
        self.assertEqual(before.reference.policy_version, 'v1')
        self.assertEqual(after.reference.policy_version, 'v2')
        for case, days, seconds in [('DP-0001', 30, 0), ('DP-0002', 45, 0), ('DP-0029', 30, 1), ('DP-0030', 45, 1)]:
            context = self.context(case)
            self.assertEqual(context.dispute.opened_at - context.transactions[0].occurred_at, timedelta(days=days, seconds=seconds))
        # Policy selection uses opening, although evaluation has crossed the boundary.
        self.assertGreater(before.reference.evaluation_at, boundary)
        with self.assertRaises(ContractError):
            replace(after, policy_rules=tuple(replace(r, effective_from=boundary + timedelta(seconds=1)) for r in after.policy_rules))

    def test_policy_result_partition_and_credit_limit(self):
        ref = self.context().reference
        valid = PolicyResult(reference=ref, allowed_outcomes=(Outcome.PROVISIONAL_CREDIT,),
                             blocked_outcomes=(Outcome.DECLINE, Outcome.HUMAN_REVIEW, Outcome.REQUEST_EVIDENCE),
                             currency='SGD', credit_limit_minor=6000,
                             rule_checks=(RuleCheck(policy_rule_id='v2-APPROVE', status='matched', explanation='Test only'),))
        self.roundtrip(valid)
        for change in ({'credit_limit_minor': None}, {'credit_limit_minor': 0}, {'credit_limit_minor': True},
                       {'allowed_outcomes': ()}, {'blocked_outcomes': ()},
                       {'blocked_outcomes': tuple(Outcome)}, {'rule_checks': valid.rule_checks * 2}):
            with self.subTest(change=change), self.assertRaises(ContractError):
                replace(valid, **change)
        review = replace(valid, allowed_outcomes=(Outcome.HUMAN_REVIEW,),
                         blocked_outcomes=(Outcome.DECLINE, Outcome.PROVISIONAL_CREDIT, Outcome.REQUEST_EVIDENCE),
                         credit_limit_minor=None)
        self.roundtrip(review)
        self.roundtrip(replace(review, rule_checks=(), data_issues=('Applicable policy rows unavailable',)))
        with self.assertRaises(ContractError):
            replace(review, credit_limit_minor=0)
        with self.assertRaises(ContractError):
            replace(review, rule_checks=())
        with self.assertRaises(ContractError):
            replace(valid, data_issues=('Incomplete settlement data',))

    def test_evidence_requirements_do_not_fabricate_ids(self):
        requirement = EvidenceRequirement(category='refund_confirmation', reason='absent', policy_rule_id='v2-MISSING_EVIDENCE')
        payload = requirement.to_dict()
        self.assertNotIn('evidence_id', payload)
        with self.assertRaises(ContractError):
            EvidenceRequirement.from_dict({**payload, 'evidence_id': 'EV-9999'})
        with self.assertRaises(ContractError):
            replace(requirement, category='EV-9999')
        recommendation = Recommendation(outcome=Outcome.REQUEST_EVIDENCE, currency='SGD')
        with self.assertRaises(ContractError):
            self.proposal(recommendation=recommendation)
        proposal = replace(self.proposal(), recommendation=recommendation, evidence_ids=(),
                           policy_rule_ids=('v2-MISSING_EVIDENCE',), missing_evidence=(requirement,))
        self.roundtrip(proposal)

    def test_citation_version_duplicate_and_proposal_revision_validation(self):
        proposal = self.proposal()
        for change in ({'policy_rule_ids': ('v1-APPROVE',)}, {'policy_rule_ids': ('APPROVE',)},
                       {'evidence_ids': ('EV-missing',)}, {'evidence_ids': proposal.evidence_ids * 2},
                       {'revision': 2}, {'revision': -1}, {'revision': True}):
            with self.subTest(change=change), self.assertRaises(ContractError):
                replace(proposal, **change)
        self.roundtrip(replace(proposal, revision=1, proposal_id=identifier('correction')))

    def test_critic_acceptance_is_separate_from_persistence(self):
        proposal = self.proposal()
        critique = CriticResult(proposal_id=proposal.proposal_id, reference=proposal.reference,
                                verdict=CriticVerdict.ACCEPTED, feedback='Test acceptance only')
        self.roundtrip(critique)
        self.assertNotIn('decision_id', critique.to_dict())
        with self.assertRaises(ContractError):
            replace(critique, failed_checks=('unsupported_claim',))
        with self.assertRaises(ContractError):
            replace(critique, verdict=CriticVerdict.REVISE)
        self.roundtrip(replace(critique, verdict=CriticVerdict.HUMAN_REVIEW, failed_checks=('conflict',)))

    def test_persisted_commit_requires_revision_and_effect_for_credit_only(self):
        for status in (ExecutionStatus.COMMITTED, ExecutionStatus.REUSED):
            for outcome in Outcome:
                result = self.persisted(outcome, status)
                self.roundtrip(result)
                self.assertEqual(result.simulated_credit_id is not None, outcome is Outcome.PROVISIONAL_CREDIT)
                for change in ({'decision_id': None}, {'recommendation': None}, {'committed_at': None},
                               {'reference': replace(result.reference, source_revision=None)}):
                    with self.subTest(status=status, outcome=outcome, change=change), self.assertRaises(ContractError):
                        replace(result, **change)
        with self.assertRaises(ContractError):
            replace(self.persisted(), simulated_credit_id=None)
        with self.assertRaises(ContractError):
            replace(self.persisted(Outcome.DECLINE), simulated_credit_id=identifier('credit'))
        with self.assertRaises(ContractError):
            replace(self.persisted(), committed_at=instant('2020-01-01T00:00:00Z'))

    def test_unsuccessful_commit_cannot_claim_persistence(self):
        for status in (ExecutionStatus.REJECTED, ExecutionStatus.UNAVAILABLE, ExecutionStatus.FAILED):
            result = CommitResult(run_id=identifier('run'), proposal_id=identifier('proposal'),
                                  idempotency_key=identifier('key'), reference=self.context().reference,
                                  status=status, message='No confirmed persistence')
            self.roundtrip(result)
            for field, value in [('decision_id', identifier('decision')), ('simulated_credit_id', identifier('credit')),
                                 ('recommendation', self.proposal().recommendation),
                                 ('committed_at', self.context().reference.evaluation_at)]:
                with self.subTest(status=status, field=field), self.assertRaises(ContractError):
                    replace(result, **{field: value})

    def test_revision_is_not_snapshot_id_and_cannot_be_coerced(self):
        ref = self.context().reference
        self.assertIsNone(ref.source_revision)
        for bad in (True, -1, 1.0, '7', identifier('snapshot'), 2**63):
            with self.subTest(revision=bad), self.assertRaises(ContractError):
                replace(ref, source_revision=bad)
        self.roundtrip(replace(ref, source_revision=0))
        self.assertNotEqual(replace(ref, source_revision=7), replace(ref, source_revision=8))

    def test_run_state_distinguishes_failure_validation_and_commit(self):
        initial = RunState(run_id=identifier('run'), phase=RunPhase.CREATED)
        self.roundtrip(initial)
        with self.assertRaises(ContractError):
            replace(initial, phase=RunPhase.RETRIEVED)
        validated = replace(initial, phase=RunPhase.VALIDATED, reference=self.context().reference)
        self.roundtrip(validated)
        with self.assertRaises(ContractError):
            replace(validated, phase=RunPhase.FINISHED)
        result = self.persisted()
        finished = replace(validated, phase=RunPhase.FINISHED, reference=result.reference, commit_result=result)
        self.roundtrip(finished)
        for change in ({'run_id': identifier('different_run')}, {'reference': replace(result.reference, source_revision=8)},
                       {'phase': RunPhase.VALIDATED}, {'model_calls': True}, {'tool_calls': -1}, {'proposal_revision': 2}):
            with self.subTest(change=change), self.assertRaises(ContractError):
                replace(finished, **change)
        self.roundtrip(replace(initial, phase=RunPhase.FAILED, error='Source unavailable'))
        with self.assertRaises(ContractError):
            replace(initial, phase=RunPhase.FAILED)
        with self.assertRaises(ContractError):
            replace(initial, error='Failure without failed status')


if __name__ == '__main__':
    unittest.main()
