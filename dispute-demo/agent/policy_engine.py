"""Legacy dictionary adapter to the single canonical typed policy evaluator.

Retained for the unintegrated prototypes. No independent policy logic or I/O.
Run/import from dispute-demo so app and integration are normal packages.
"""
from app.policy_engine import evaluate_policy
from app.schemas import Outcome
from app.tools import context_from_rows
from integration.get_dispute_context import _time


def evaluate_dispute(context):
    """Validate legacy rows, then delegate; malformed inputs fail closed by raising.

    Output naming is compatibility only: recommend_refund means a proposed new
    simulated provisional credit, never an existing merchant settlement refund.
    """
    case = context['dispute']
    typed = context_from_rows(context, case['dispute_id'],
        captured_at=_time(case['evaluation_at']), source_channel='offline_test').data
    result = evaluate_policy(typed)
    matched = next((c for c in result.rule_checks if c.status == 'matched'), None)
    outcome = result.allowed_outcomes[0]
    legacy = {Outcome.PROVISIONAL_CREDIT: 'recommend_refund', Outcome.DECLINE: 'reject',
              Outcome.REQUEST_EVIDENCE: 'request_evidence', Outcome.HUMAN_REVIEW: 'escalate'}
    code = matched.policy_rule_id.split('-', 1)[1] if matched else 'DATA_INTEGRITY'
    reasons = {'FILING_WINDOW': 'OUT_OF_WINDOW', 'APPROVE': 'SUPPORTED_CLAIM'}
    code = reasons.get(code, code)
    completed = [s for s in typed.settlements if s.transaction_id == typed.dispute.transaction_id
                 and s.settlement_status.value == 'completed']
    totals = {kind: sum(s.amount_minor for s in completed if s.movement_type.value == kind)
              for kind in ('capture', 'refund', 'reversal')}
    if outcome is Outcome.PROVISIONAL_CREDIT and totals['refund'] + totals['reversal']:
        code = 'PARTIAL_REFUND_OUTSTANDING'
    return {'dispute_id': case['dispute_id'], 'policy_version': result.reference.policy_version,
            'outcome': legacy[outcome], 'recommended_refund_minor': result.credit_limit_minor or 0,
            'currency': result.currency, 'reason_codes': [code],
            'matched_policy_rule_id': matched.policy_rule_id if matched else None,
            'evaluated_policy_rule_ids': [c.policy_rule_id for c in result.rule_checks if c.status != 'not_evaluated'],
            'evidence_ids': list(dict.fromkeys(e for c in result.rule_checks for e in c.evidence_ids)),
            'completed_captures_minor': totals['capture'], 'completed_refunds_minor': totals['refund'],
            'remaining_balance_minor': totals['capture'] - totals['refund'] - totals['reversal'],
            'data_issues': list(result.data_issues)}
