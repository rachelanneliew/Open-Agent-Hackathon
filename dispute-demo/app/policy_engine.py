"""Pure typed adaptation of agent.policy_engine's ordered synthetic evaluator.

Only the supplied, validated v1/v2 rules and bounded synthetic evidence templates
are supported. No I/O, model, memory, fixture lookup or action execution.
"""
from datetime import datetime, timedelta, timezone
import json

from .schemas import (DisputeContext, EvidenceRequirement, MovementType, Outcome,
                      PolicyResult, RuleCheck, SettlementStatus, require)
from .history import validate_history

# Supported executable semantics, grounded in policies/synthetic_policy_v*.md.
# Retrieved rules must match this vocabulary; unknown revisions fail closed.
_RULES = (
    ('DATA_INTEGRITY', 'data_integrity_or_pending', Outcome.HUMAN_REVIEW),
    ('FILING_WINDOW', 'filing_window_exceeded', Outcome.DECLINE),
    ('ALREADY_REFUNDED', 'remaining_balance_zero', Outcome.DECLINE),
    ('CONFLICTING_EVIDENCE', 'material_evidence_conflict', Outcome.HUMAN_REVIEW),
    ('MISSING_EVIDENCE', 'required_evidence_missing', Outcome.REQUEST_EVIDENCE),
    ('UNSUPPORTED', 'claim_not_supported', Outcome.DECLINE),
    ('REVIEW_THRESHOLD', 'proposed_refund_above_limit', Outcome.HUMAN_REVIEW),
    ('APPROVE', 'all_preceding_checks_pass', Outcome.PROVISIONAL_CREDIT),
)
_REQUIREMENTS = {'refund_missing': ['refund_confirmation'],
                 'not_received': ['receipt', 'delivery_record'],
                 'duplicate_charge': ['receipt', 'two_completed_captures_same_order']}
_START = datetime(2026, 1, 1, tzinfo=timezone.utc)
_BOUNDARY = datetime(2026, 10, 1, tzinfo=timezone.utc)


def _parameters(text):
    def pairs(items):
        require(len(items) == len(dict(items)), 'Duplicate policy parameter keys')
        return dict(items)
    def invalid(value):
        raise ValueError('Non-finite policy parameter')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def _validated_rules(context):
    version = context.reference.policy_version
    if version not in ('v1', 'v2'):
        return None
    start, end = (_START, _BOUNDARY) if version == 'v1' else (_BOUNDARY, None)
    if context.dispute.opened_at < start or (end and context.dispute.opened_at >= end):
        return None
    rules = tuple(sorted(context.policy_rules, key=lambda r: r.priority))
    if len(rules) != len(_RULES):
        return None
    for index, (rule, (code, predicate, action)) in enumerate(zip(rules, _RULES), 1):
        expected = {}
        if code == 'FILING_WINDOW':
            expected = {'filing_window_days': 30 if version == 'v1' else 45}
        elif code == 'MISSING_EVIDENCE':
            expected = _REQUIREMENTS
        elif code == 'REVIEW_THRESHOLD':
            expected = {'review_threshold_minor': 20000}
        try:
            params = _parameters(rule.parameters_json)
            # JSON canonical comparison also rejects bool/float substitutions.
            if json.dumps(params, sort_keys=True) != json.dumps(expected, sort_keys=True):
                return None
        except (ValueError, TypeError):
            return None
        if (rule.policy_rule_id != f'{version}-{code}' or rule.predicate != predicate or
                rule.action is not action or rule.priority != index * 10 or
                rule.reason_code != 'ALL' or rule.effective_from != start or rule.effective_to != end):
            return None
    return rules


def _ledger(context):
    """Primary balance only; companion confirms a charge, never doubles credit."""
    issues = []
    txs = {t.transaction_id: t for t in context.transactions}
    primary = txs.get(context.dispute.transaction_id)
    linked = {context.dispute.transaction_id, context.dispute.related_transaction_id} - {None}
    if set(txs) != linked:
        issues.append('missing_linked_transaction')
    if len({t.customer_id for t in txs.values()}) > 1:
        issues.append('cross_customer_transactions')
    balances = {}
    for txid, tx in txs.items():
        movements = [s for s in context.settlements if s.transaction_id == txid]
        if tx.currency != context.dispute.currency or any(s.currency != tx.currency for s in movements):
            issues.append('currency_mismatch:' + txid)
        if any(s.settlement_status is SettlementStatus.PENDING for s in movements):
            issues.append('pending_movement:' + txid)
        completed = [s for s in movements if s.settlement_status is SettlementStatus.COMPLETED]
        captures = [s for s in completed if s.movement_type is MovementType.CAPTURE]
        totals = {kind: sum(s.amount_minor for s in completed if s.movement_type is kind) for kind in MovementType}
        balance = totals[MovementType.CAPTURE] - totals[MovementType.REFUND] - totals[MovementType.REVERSAL]
        balances[txid] = (balance, totals)
        # Multi-capture/re-authorisation patterns are outside the authored scope.
        if len(captures) != 1 or totals[MovementType.CAPTURE] != tx.amount_minor:
            issues.append('inconsistent_capture:' + txid)
        if balance < 0 or any(n > 2**63 - 1 for n in totals.values()):
            issues.append('invalid_balance:' + txid)
        if tx.transaction_status not in ('captured', 'reversed') or (tx.transaction_status == 'reversed' and balance != 0):
            issues.append('inconsistent_transaction_status:' + txid)
        if any(s.occurred_at < tx.occurred_at for s in completed) or any(
                s.occurred_at < captures[0].occurred_at for s in completed
                if captures and s.movement_type is not MovementType.CAPTURE):
            issues.append('inconsistent_movement_time:' + txid)
    if any(s.transaction_id not in txs for s in context.settlements):
        issues.append('settlement_without_transaction')
    if primary and context.dispute.opened_at < primary.occurred_at:
        issues.append('opening_precedes_transaction')
    if context.dispute.reason_code == 'duplicate_charge':
        companion = txs.get(context.dispute.related_transaction_id)
        if companion and balances[companion.transaction_id][0] != companion.amount_minor:
            issues.append('duplicate_companion_balance_unsupported')
    return primary, balances, issues


def _stamp(value):
    return value.isoformat().replace('+00:00', 'Z')


def _evidence_kind(item, context, primary):
    """Recognize whole generated documents, not keywords inside arbitrary prose."""
    if item.integrity_status != 'valid' or item.content is None or primary is None:
        return None
    if item.related_settlement_id is not None and not any(
            s.settlement_id == item.related_settlement_id and s.transaction_id == primary.transaction_id
            and s.movement_type in (MovementType.REFUND, MovementType.REVERSAL)
            for s in context.settlements):
        return None
    header = '\n'.join([
        'SYNTHETIC DEMONSTRATION DOCUMENT', 'All entities and events are fictional.',
        f'evidence_id: {item.evidence_id}', f'dispute_id: {context.dispute.dispute_id}',
        f'transaction_id: {primary.transaction_id}', f'order_id: {primary.order_id}',
        f'document_type: {item.evidence_type}', f'source_type: {item.source_type}',
        f'event_at: {_stamp(item.event_at)}', f'available_at: {_stamp(item.available_at)}', '', ''])
    text = item.content.strip()
    if not text.startswith(header):
        return None
    body = text[len(header):]
    amount = f'{primary.amount_minor // 100}.{primary.amount_minor % 100:02d}'
    templates = {
        ('receipt', 'merchant'): {f'One order was purchased for SGD {amount}. Customer reference {primary.customer_id}.': 'receipt'},
        ('refund_confirmation', 'merchant'): {
            f'The merchant committed to refund the full SGD {amount}. This commitment is not confirmation that the payment movement has completed.': 'refund_confirmation'},
        ('delivery_record', 'carrier'): {
            'Carrier record: parcel was lost in transit and has not been delivered.': 'lost',
            'Carrier record for the same order: delivery completed and signed for by the customer.': 'delivered'},
        ('merchant_response', 'merchant'): {
            f'There was only one order. Charge references {primary.transaction_id} and {context.dispute.related_transaction_id} refer to that same order, not separate purchases.': 'merchant_response'},
    }
    return templates.get((item.evidence_type, item.source_type), {}).get(body)


def _result(context, outcome, checks=(), *, limit=None, missing=(), issues=()):
    return PolicyResult(reference=context.reference, currency=context.dispute.currency,
        allowed_outcomes=(outcome,), blocked_outcomes=tuple(o for o in Outcome if o is not outcome),
        rule_checks=tuple(checks), credit_limit_minor=limit, missing_evidence=tuple(missing),
        data_issues=tuple(dict.fromkeys(issues)))


def evaluate_policy(context: DisputeContext, evaluation_time=None, *, advisory_history=None) -> PolicyResult:
    """Evaluate the immutable cutoff; a different time requires a fresh context.

    Malformed transport values raise ContractError at the typed boundary. Valid
    but unsupported policy/data returns an explicit no-credit human-review result.
    Known unavailable evidence is resolved by rule 50; other read issues remain
    unresolved and force review. No history threshold exists in these policies.
    """
    require(type(context) is DisputeContext, 'Expected DisputeContext')
    # v1/v2 have no binding history rule. Validate the supplied source-verified
    # scope, then evaluate exactly the same current-case rules as critic/commit.
    validate_history(context, advisory_history)
    if evaluation_time is not None:
        require(type(evaluation_time) is datetime and evaluation_time.utcoffset() == timedelta(0),
                'Expected UTC evaluation time')
        require(evaluation_time == context.reference.evaluation_at, 'Changed cutoff requires fresh retrieval')
    rules = _validated_rules(context)
    if rules is None:
        return _result(context, Outcome.HUMAN_REVIEW, issues=('unsupported_or_incomplete_policy',))
    if context.dispute.currency != 'SGD':
        return _result(context, Outcome.HUMAN_REVIEW, issues=('unsupported_currency',))
    primary, balances, issues = _ledger(context)
    if context.dispute.dispute_status != 'open':
        issues.append('unsupported_dispute_status')
    # Only precisely identified missing-text diagnostics are handled as evidence
    # requirements. Unknown issues cannot be erased to enable credit.
    known_missing = {'evidence_text_unavailable:' + e.evidence_id for e in context.evidence
                     if e.content is None or e.integrity_status != 'valid'}
    issues.extend(i for i in context.data_issues if i not in known_missing)
    balance = balances[primary.transaction_id][0] if primary else None
    proposed = min(context.dispute.claimed_amount_minor, balance) if balance is not None and balance > 0 else None
    age = context.dispute.opened_at - primary.occurred_at if primary else timedelta(0)
    recognized = {e.evidence_id: _evidence_kind(e, context, primary) for e in context.evidence}
    usable = tuple(e for e in context.evidence if recognized[e.evidence_id] is not None)
    citations = tuple(e.evidence_id for e in usable)
    lost = any(recognized[e.evidence_id] == 'lost' for e in usable)
    delivered = any(recognized[e.evidence_id] == 'delivered' for e in usable)
    reason = context.dispute.reason_code
    txs = context.transactions
    two_charges = (len(txs) == 2 and len({t.order_id for t in txs}) == 1 and
                   len({t.merchant_id for t in txs}) == 1 and len({t.customer_id for t in txs}) == 1 and
                   all(balances[t.transaction_id][1][MovementType.CAPTURE] == t.amount_minor for t in txs))
    missing = []
    requirements = _parameters(rules[4].parameters_json)[reason]
    for category in requirements:
        present = two_charges if category == 'two_completed_captures_same_order' else any(e.evidence_type == category for e in usable)
        if not present:
            missing.append(EvidenceRequirement(category=category,
                reason='unusable' if any(e.evidence_type == category for e in context.evidence) else 'absent',
                policy_rule_id=rules[4].policy_rule_id))
    # Unknown additional material cannot silently negate known support. Required
    # but unusable documents instead produce an explicit evidence request.
    supported_types = {e.evidence_type for e in usable}
    uncertain_extra = any(recognized[e.evidence_id] is None and
                          (e.evidence_type not in requirements or e.evidence_type in supported_types)
                          for e in context.evidence)
    conflict = (reason == 'not_received' and lost and delivered) or uncertain_extra
    checks, terminal = [], None
    for rule in rules:
        if terminal is not None:
            checks.append(RuleCheck(policy_rule_id=rule.policy_rule_id, status='not_evaluated',
                                    explanation='Earlier terminal rule matched.'))
            continue
        predicate = rule.predicate
        if predicate == 'data_integrity_or_pending':
            applies = bool(issues)
            detail = '; '.join(issues) if issues else 'Linked captures and completed balances are consistent; failed movements excluded.'
        elif predicate == 'filing_window_exceeded':
            days = _parameters(rule.parameters_json)['filing_window_days']
            applies = age > timedelta(days=days)
            detail = f'Primary transaction {primary.transaction_id}: filing age {age}; inclusive limit {days} days.'
        elif predicate == 'remaining_balance_zero':
            applies = balance == 0
            source_ids = ', '.join(s.settlement_id for s in context.settlements
                                  if s.transaction_id == primary.transaction_id and
                                  s.settlement_status is SettlementStatus.COMPLETED)
            detail = (f'Primary transaction {primary.transaction_id}, completed movements {source_ids}: '
                      f'remaining balance {balance} minor units.')
        elif predicate == 'material_evidence_conflict':
            applies = conflict
            detail = 'Conflicting delivery outcomes or unsupported additional evidence.' if applies else 'No recognized material contradiction; refund promises do not prove settlement.'
        elif predicate == 'required_evidence_missing':
            applies = bool(missing)
            detail = 'Missing/unusable: ' + ', '.join(m.category for m in missing) if applies else 'Required synthetic support verified against case and source fields.'
        elif predicate == 'claim_not_supported':
            applies = reason == 'not_received' and delivered and not lost
            detail = 'Complete delivery evidence contradicts non-receipt.' if applies else 'No complete unambiguous contradiction of the claim.'
        elif predicate == 'proposed_refund_above_limit':
            limit = _parameters(rule.parameters_json)['review_threshold_minor']
            applies = proposed > limit
            detail = f'Eligible primary-transaction amount {proposed}; review only above {limit} SGD minor units.'
        else:
            applies = True
            detail = f'Supported claim; min(claimed, primary completed balance) = {proposed} SGD minor units.'
        checks.append(RuleCheck(policy_rule_id=rule.policy_rule_id,
            status='matched' if applies else 'not_matched', explanation=detail,
            evidence_ids=citations if rule.priority >= 40 else ()))
        if applies:
            terminal = rule.action
    return _result(context, terminal, checks, limit=proposed if terminal is Outcome.PROVISIONAL_CREDIT else None,
                   missing=missing if terminal is Outcome.REQUEST_EVIDENCE else (), issues=issues)


def main():
    """Read-only live acceptance runner; no fixture fallback or action writes."""
    import argparse
    from .tools import ReadTools
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dispute_id')
    args = parser.parse_args()
    read = ReadTools().get_dispute_context(args.dispute_id)
    if not isinstance(read.data, DisputeContext):
        print(json.dumps(read.to_dict(), indent=2))
        return 1
    print(json.dumps({'source_channel': read.data.source_channel, 'read_status': read.status.value,
                      'policy_result': evaluate_policy(read.data).to_dict()}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
