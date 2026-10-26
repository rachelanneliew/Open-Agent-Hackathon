"""Investigate a dispute: H-MEM recall, deterministic policy, then critic.

Memory is advisory only. It cannot change policy outcomes or skip critic checks.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from critic import DEFAULT_LEDGER, review_and_simulate
from hmem_client import DEFAULT_PERSIST, HmemClient
from memory_service import DEFAULT_REPEATED_CLAIM_THRESHOLD, DisputeMemory
from policy_engine import evaluate_dispute

VERIFIED_CRITIC_STATUSES = frozenset({"simulated_credit_recorded", "validated_non_credit_action"})


def _policy_proposal(policy: Mapping[str, Any]) -> dict:
    return {
        "dispute_id": policy["dispute_id"],
        "policy_version": policy["policy_version"],
        "currency": policy["currency"],
        "outcome": policy["outcome"],
        "recommended_refund_minor": policy["recommended_refund_minor"],
        "matched_policy_rule_id": policy["matched_policy_rule_id"],
        "evidence_ids": list(policy.get("evidence_ids") or []),
    }


def investigate_dispute(
    context: Mapping[str, Any],
    proposal: Mapping[str, Any] | None = None,
    *,
    repeated_claim_threshold: int = DEFAULT_REPEATED_CLAIM_THRESHOLD,
    persist_dir: str | Path = DEFAULT_PERSIST,
    ledger_path: str | Path = DEFAULT_LEDGER,
    remember: bool = True,
    hmem_client: HmemClient | None = None,
) -> dict:
    memory = DisputeMemory(
        hmem_client or HmemClient(persist_dir),
        repeated_claim_threshold=repeated_claim_threshold,
    )
    memory_view = memory.retrieve_for_investigation(context)
    policy = evaluate_dispute(context)
    submitted = dict(proposal) if proposal is not None else _policy_proposal(policy)
    critic_result = review_and_simulate(context, submitted, ledger_path=ledger_path)

    stored = None
    verified = critic_result.get("status") in VERIFIED_CRITIC_STATUSES
    if remember and verified:
        stored = memory.remember_processed_dispute(context, policy, critic_result, verified=True)

    return {
        "policy": policy,
        "memory": memory_view,
        "critic": critic_result,
        "stored_memory": stored,
        "human_review_recommended": memory_view["human_review_recommended"],
        "fraud_inferred": False,
        "policy_overridden_by_memory": False,
    }
