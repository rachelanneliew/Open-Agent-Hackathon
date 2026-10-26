"""Deterministic critic and atomic, SIMULATED-only credit ledger.

This module is deliberately not a payment integration. It re-evaluates policy
from the trusted Zetaris context before accepting a proposed action. It does
not rely on an LLM's stated eligibility, amount, or policy rule.

All amounts are integers in minor currency units (SGD cents for demo data).
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Mapping

from policy_engine import evaluate_dispute

DEFAULT_LEDGER = Path.home() / ".local" / "state" / "dispute-demo" / "simulated_credits.sqlite3"
SUPPORTED_OUTCOMES = frozenset({"recommend_refund", "reject", "request_evidence", "escalate"})


def _blocked(dispute_id: str, code: str, explanation: str, expected: Mapping[str, Any] | None = None) -> dict:
    return {
        "status": "blocked",
        "reason_code": code,
        "explanation": explanation,
        "dispute_id": dispute_id,
        "simulated_credit_created": False,
        "policy_outcome": expected.get("outcome") if expected else None,
    }


def _check_proposal(context: Mapping[str, Any], proposal: Mapping[str, Any], expected: Mapping[str, Any]) -> dict | None:
    dispute_id = str(context["dispute"]["dispute_id"])
    if expected.get("dispute_id") != dispute_id:
        return _blocked(dispute_id, "CONTEXT_MISMATCH", "Policy result refers to a different dispute", expected)
    if not isinstance(proposal, Mapping):
        return _blocked(dispute_id, "INVALID_PROPOSAL", "AI proposal must be a structured object", expected)

    # Require complete, typed fields. The AI cannot pick its own policy, result, or money amount.
    for field in ("dispute_id", "policy_version", "currency", "outcome"):
        if not isinstance(proposal.get(field), str):
            return _blocked(dispute_id, "INVALID_PROPOSAL", f"Missing or invalid {field}", expected)

    amount = proposal.get("recommended_refund_minor")
    if type(amount) is not int or amount < 0:
        return _blocked(dispute_id, "INVALID_PROPOSAL", "Amount must be a nonnegative integer of minor units", expected)

    if proposal["outcome"] not in SUPPORTED_OUTCOMES:
        return _blocked(dispute_id, "INVALID_PROPOSAL", "Unknown proposed outcome", expected)

    for field in ("dispute_id", "policy_version", "currency", "outcome", "recommended_refund_minor"):
        if proposal[field] != expected[field]:
            return _blocked(dispute_id, "POLICY_MISMATCH", f"Proposed {field} does not match deterministic policy evaluation", expected)

    if "matched_policy_rule_id" in proposal and proposal["matched_policy_rule_id"] != expected["matched_policy_rule_id"]:
        return _blocked(dispute_id, "POLICY_MISMATCH", "Proposed matched rule is incorrect", expected)

    if "evidence_ids" in proposal:
        claimed = proposal["evidence_ids"]
        if not isinstance(claimed, list) or any(not isinstance(x, str) for x in claimed):
            return _blocked(dispute_id, "INVALID_PROPOSAL", "evidence_ids must be a list of strings", expected)
        if not set(claimed).issubset(set(expected["evidence_ids"])):
            return _blocked(dispute_id, "UNVERIFIED_EVIDENCE", "Proposal references evidence absent from validated context", expected)

    return None


def review_and_simulate(context: Mapping[str, Any], proposal: Mapping[str, Any], *, ledger_path: str | Path = DEFAULT_LEDGER) -> dict:
    """Review a proposed action and, if permitted, record ONE simulated credit.

    Re-running the same claim or another claim for the same transaction blocks
    duplicate simulation. sqlite BEGIN IMMEDIATE + UNIQUE(transaction_id)
    makes the check and insert atomic across concurrent local processes.
    """
    dispute_id = str(context["dispute"]["dispute_id"])
    expected = evaluate_dispute(context)  # trusted code; never ask the AI to run this
    denial = _check_proposal(context, proposal, expected)
    if denial is not None:
        return denial

    if expected["outcome"] != "recommend_refund":
        return {
            "status": "validated_non_credit_action",
            "reason_code": "POLICY_CONFIRMED",
            "dispute_id": dispute_id,
            "policy_outcome": expected["outcome"],
            "simulated_credit_created": False,
            "recommended_refund_minor": 0,
        }

    amount = expected["recommended_refund_minor"]
    if type(amount) is not int or amount <= 0:
        return _blocked(dispute_id, "INVALID_AMOUNT", "A credit must have a positive integer amount", expected)

    tx_id = context["dispute"].get("transaction_id")
    if not isinstance(tx_id, str) or not tx_id:
        return _blocked(dispute_id, "CONTEXT_MISMATCH", "Missing primary transaction identifier", expected)
    if tx_id not in {tx.get("transaction_id") for tx in context.get("transactions", [])}:
        return _blocked(dispute_id, "CONTEXT_MISMATCH", "Primary transaction absent from retrieved context", expected)

    path = Path(ledger_path).expanduser()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(str(path), timeout=15, isolation_level=None)) as db:
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("""
            CREATE TABLE IF NOT EXISTS simulated_credits (
                transaction_id TEXT PRIMARY KEY,
                dispute_id TEXT NOT NULL UNIQUE,
                amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
                currency TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
        """)
        db.execute("BEGIN IMMEDIATE")
        try:
            existing = db.execute(
                "SELECT dispute_id, amount_minor FROM simulated_credits WHERE transaction_id = ? OR dispute_id = ?",
                (tx_id, dispute_id),
            ).fetchone()
            if existing:
                db.execute("ROLLBACK")
                return _blocked(
                    dispute_id,
                    "DUPLICATE_CREDIT",
                    f"A simulated credit is already recorded for this dispute/transaction (original dispute: {existing[0]})",
                    expected,
                )
            db.execute(
                "INSERT INTO simulated_credits (transaction_id, dispute_id, amount_minor, currency, policy_version) VALUES (?, ?, ?, ?, ?)",
                (tx_id, dispute_id, amount, expected["currency"], expected["policy_version"]),
            )
            db.execute("COMMIT")
        except sqlite3.IntegrityError:
            db.execute("ROLLBACK")
            return _blocked(dispute_id, "DUPLICATE_CREDIT", "Unique credit constraint prevents repeating this action", expected)
        except Exception:
            db.execute("ROLLBACK")
            raise

    return {
        "status": "simulated_credit_recorded",
        "reason_code": "POLICY_CONFIRMED",
        "dispute_id": dispute_id,
        "transaction_id": tx_id,
        "policy_outcome": expected["outcome"],
        "policy_rule_id": expected["matched_policy_rule_id"],
        "recommended_refund_minor": amount,
        "currency": expected["currency"],
        "simulated_credit_created": True,
        "note": "SIMULATION ONLY: no bank account or payment gateway was contacted",
    }
