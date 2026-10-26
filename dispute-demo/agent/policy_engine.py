"""Deterministic evaluator for the team's fictional dispute policies.

Input is the dictionary returned by integration/get_dispute_context.py.
No database access, LLM call, or simulated credit is performed here.
"""
import json
from datetime import datetime, timezone


PREDICATES = {
    "data_integrity_or_pending", "filing_window_exceeded", "remaining_balance_zero",
    "material_evidence_conflict", "required_evidence_missing", "claim_not_supported",
    "proposed_refund_above_limit", "all_preceding_checks_pass",
}

REASON_CODES = {
    "data_integrity_or_pending": "DATA_INTEGRITY",
    "filing_window_exceeded": "OUT_OF_WINDOW",
    "remaining_balance_zero": "ALREADY_REFUNDED",
    "material_evidence_conflict": "CONFLICTING_EVIDENCE",
    "required_evidence_missing": "MISSING_EVIDENCE",
    "claim_not_supported": "UNSUPPORTED",
    "proposed_refund_above_limit": "REVIEW_THRESHOLD",
}


def _timestamp(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamps must include timezone")
    return dt.astimezone(timezone.utc)


def _integer(value):
    if isinstance(value, bool):
        raise ValueError("Boolean cannot be an amount")
    n = int(value)
    if str(n) != str(value).strip():
        raise ValueError("Expected an integer amount")
    return n


def evaluate_dispute(context):
    """Return an explainable, *non-executing* policy recommendation.

    Raises ValueError for malformed policy rules so the caller can fail closed.
    """
    dispute = context["dispute"]
    rules = sorted(context["policy_rules"], key=lambda row: _integer(row["priority"]))
    if not rules:
        raise ValueError("No effective policy rules returned by Zetaris")
    versions = {r["policy_version"] for r in rules}
    if len(versions) != 1:
        raise ValueError("Policy rules from multiple versions: refusing to decide")
    policy_version = versions.pop()
    parsed = []
    for rule in rules:
        predicate = json.loads(rule["condition_json"])["predicate"]
        if predicate not in PREDICATES:
            raise ValueError(f"Unrecognized policy predicate: {predicate}")
        params = json.loads(rule["parameters_json"])
        if not isinstance(params, dict):
            raise ValueError("Invalid rule parameters")
        parsed.append((rule, predicate, params))
    if len(parsed) != len(PREDICATES) or {p for _, p, _ in parsed} != PREDICATES:
        raise ValueError("Missing or duplicate policy predicates")

    transactions = context.get("transactions", [])
    settlements = context.get("settlements", [])
    usable_evidence = [
        e for e in context.get("evidence", [])
        if e.get("integrity_status") == "valid"
        and _timestamp(e["available_at"]) <= _timestamp(dispute["evaluation_at"])
    ]
    evidence_types = {e["evidence_type"] for e in usable_evidence}
    delivery_texts = [str(e.get("content", "")).lower() for e in usable_evidence
                      if e["evidence_type"] == "delivery_record"]
    lost = any("lost in transit" in body and "not been delivered" in body for body in delivery_texts)
    delivered = any("delivery completed and signed for" in body for body in delivery_texts)

    # First compute ledger facts without trusting the AI or documents as proof of payment.
    invalid = False
    completed_captures = completed_refunds = completed_reversals = 0
    completed_by_tx = {}
    try:
        currency = dispute["currency"]
        claimed = _integer(dispute["claimed_amount_minor"])
        opened_at = _timestamp(dispute["opened_at"])
        cutoff = _timestamp(dispute["evaluation_at"])
        if claimed <= 0 or opened_at > cutoff or not transactions:
            invalid = True
        tx_ids = {t["transaction_id"] for t in transactions}
        if len(tx_ids) != len(transactions) or dispute["transaction_id"] not in tx_ids:
            invalid = True
        related = dispute.get("related_transaction_id")
        if related and related not in tx_ids:
            invalid = True
        for tx in transactions:
            if tx["currency"] != currency or _integer(tx["amount_minor"]) <= 0:
                invalid = True
            if _timestamp(tx["occurred_at"]) > cutoff:
                invalid = True
        for movement in settlements:
            txid = movement["transaction_id"]
            amount = _integer(movement["amount_minor"])
            if (txid not in tx_ids or movement["currency"] != currency
                    or amount <= 0 or movement["settlement_status"] != "completed"
                    or _timestamp(movement["occurred_at"]) > cutoff
                    or _timestamp(movement["recorded_at"]) > cutoff):
                invalid = True
            kind = movement["movement_type"]
            if kind == "capture":
                completed_captures += amount
                completed_by_tx[txid] = completed_by_tx.get(txid, 0) + amount
            elif kind == "refund":
                completed_refunds += amount
            elif kind == "reversal":
                completed_reversals += amount
            else:
                invalid = True
        for tx in transactions:
            if completed_by_tx.get(tx["transaction_id"], 0) != _integer(tx["amount_minor"]):
                invalid = True
        remaining = completed_captures - completed_refunds - completed_reversals
        if remaining < 0:
            invalid = True
        proposed_amount = min(claimed, max(remaining, 0))
        age_seconds = (opened_at - min(_timestamp(t["occurred_at"]) for t in transactions)).total_seconds()
        if age_seconds < 0:
            invalid = True
    except (KeyError, TypeError, ValueError, OverflowError):
        invalid, remaining, proposed_amount, age_seconds = True, 0, 0, 0

    reason = dispute.get("reason_code")
    if reason not in {"refund_missing", "not_received", "duplicate_charge"}:
        invalid = True

    # The synthetic template uses a valid receipt/delivery record to establish the claim.
    two_captures_one_order = (
        len(transactions) >= 2
        and len({t["order_id"] for t in transactions}) == 1
        and len([tx for tx in transactions if completed_by_tx.get(tx["transaction_id"], 0) > 0]) >= 2
    )

    # Evaluate only the rules Zetaris actually returned, in their supplied priority order.
    checked_rule_ids = []
    for rule, predicate, params in parsed:
        checked_rule_ids.append(rule["policy_rule_id"])
        if predicate == "data_integrity_or_pending":
            applies = invalid
        elif predicate == "filing_window_exceeded":
            applies = age_seconds > _integer(params["filing_window_days"]) * 86400
        elif predicate == "remaining_balance_zero":
            applies = remaining == 0
        elif predicate == "material_evidence_conflict":
            applies = reason == "not_received" and lost and delivered
        elif predicate == "required_evidence_missing":
            requirements = params[reason]
            applies = any(
                (not two_captures_one_order if req == "two_completed_captures_same_order" else req not in evidence_types)
                for req in requirements
            )
            if reason == "not_received" and not (lost or delivered):
                # A document labelled delivery_record without a recognizable
                # synthetic delivery outcome is unusable evidence.
                applies = True
        elif predicate == "claim_not_supported":
            applies = reason == "not_received" and delivered and not lost
        elif predicate == "proposed_refund_above_limit":
            applies = proposed_amount > _integer(params["review_threshold_minor"])
        else:  # all_preceding_checks_pass
            applies = True
        if applies:
            outcome = rule["action"]
            amount = proposed_amount if outcome == "recommend_refund" else 0
            reason_code = REASON_CODES.get(predicate, "SUPPORTED_CLAIM")
            if predicate == "all_preceding_checks_pass" and completed_refunds + completed_reversals > 0:
                reason_code = "PARTIAL_REFUND_OUTSTANDING"
            return {
                "dispute_id": dispute["dispute_id"],
                "policy_version": policy_version,
                "outcome": outcome,
                "recommended_refund_minor": amount,
                "currency": dispute["currency"],
                "reason_codes": [reason_code],
                "matched_policy_rule_id": rule["policy_rule_id"],
                "evaluated_policy_rule_ids": checked_rule_ids,
                "evidence_ids": [e["evidence_id"] for e in usable_evidence],
                "completed_captures_minor": completed_captures,
                "completed_refunds_minor": completed_refunds,
                "remaining_balance_minor": remaining,
            }
    raise ValueError("No terminal policy action found")
