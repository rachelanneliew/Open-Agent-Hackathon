"""Customer-scoped dispute memories on top of the official H-MEM engine.

Repeated prior claims can recommend human review. They are never treated as
proof of fraud, and they never replace policy evaluation.
"""
from __future__ import annotations

import re
import time
from typing import Any, Mapping

from hmem_client import HmemClient

CUSTOMER_RE = re.compile(r"^CUST-\d{3,}$")
DISPUTE_RE = re.compile(r"^DP-\d{4}$")
KIND_PROCESSED = "kind:processed-dispute"
TAG_VERIFIED = "verified"
DEFAULT_REPEATED_CLAIM_THRESHOLD = 3
NOT_FRAUD_NOTE = (
    "Repeated prior claims recommend human review only; they are not proof of fraud "
    "and do not change deterministic policy or critic results."
)


def customer_scope(customer_id: str) -> str:
    if not isinstance(customer_id, str) or not CUSTOMER_RE.fullmatch(customer_id):
        raise ValueError("A canonical customer_id such as CUST-006 is required for memory isolation")
    return f"customer:{customer_id}"


def customer_id_from_context(context: Mapping[str, Any]) -> str:
    dispute = context.get("dispute") or {}
    direct = dispute.get("customer_id")
    if isinstance(direct, str) and direct:
        return _require_customer(direct)
    ids = {
        tx.get("customer_id")
        for tx in context.get("transactions", [])
        if isinstance(tx, Mapping) and tx.get("customer_id")
    }
    if len(ids) != 1:
        raise ValueError("Cannot associate memory without a unique customer_id")
    return _require_customer(next(iter(ids)))


def _require_customer(customer_id: str) -> str:
    if not CUSTOMER_RE.fullmatch(customer_id):
        raise ValueError("A canonical customer_id such as CUST-006 is required for memory isolation")
    return customer_id


def _customer_owned(memory: Mapping[str, Any], customer_id: str) -> bool:
    scope = customer_scope(customer_id)
    tags = memory.get("tags") or []
    return memory.get("chatId") == scope and scope in tags and f"customer:{customer_id}" in tags


def _dispute_id_from_tags(tags: list[str]) -> str | None:
    for tag in tags:
        if tag.startswith("dispute:"):
            value = tag.split(":", 1)[1]
            if DISPUTE_RE.fullmatch(value):
                return value
    return None


class DisputeMemory:
    def __init__(self, client: HmemClient, *, repeated_claim_threshold: int = DEFAULT_REPEATED_CLAIM_THRESHOLD):
        if type(repeated_claim_threshold) is not int or repeated_claim_threshold < 1:
            raise ValueError("repeated_claim_threshold must be a positive integer")
        self.client = client
        self.repeated_claim_threshold = repeated_claim_threshold

    def remember_processed_dispute(
        self,
        context: Mapping[str, Any],
        policy: Mapping[str, Any],
        critic: Mapping[str, Any],
        *,
        verified: bool,
    ) -> dict:
        customer_id = customer_id_from_context(context)
        dispute = context["dispute"]
        dispute_id = str(dispute["dispute_id"])
        if not DISPUTE_RE.fullmatch(dispute_id):
            raise ValueError("Expected a dispute ID such as DP-0014")
        reason = str(dispute.get("reason_code") or "unknown")
        outcome = str(policy.get("outcome") or critic.get("policy_outcome") or "unknown")
        amount = policy.get("recommended_refund_minor", 0)
        scope = customer_scope(customer_id)
        content = (
            f"Processed dispute {dispute_id} for {customer_id}. "
            f"Claim reason {reason}. Policy outcome {outcome}. "
            f"Recommended refund minor units {amount}."
        )
        tags = [
            scope,
            f"dispute:{dispute_id}",
            KIND_PROCESSED,
            f"reason:{reason}",
            f"outcome:{outcome}",
        ]
        if verified:
            tags.append(TAG_VERIFIED)
        return self.client.add({
            "content": content,
            "type": "factual",
            "layer": "working",
            "tags": tags,
            "confidence": 1.0,
            "source": f"dispute-agent:{dispute_id}",
            "chatId": scope,
            "provenance": {
                "origin": "plan_completion",
                "learnedAt": int(time.time() * 1000),
                "label": f"processed dispute {dispute_id} after policy and critic",
                "refs": [dispute_id, customer_id],
            },
        })

    def verified_previous_dispute_ids(self, customer_id: str, *, exclude_dispute_id: str | None = None) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()
        for memory in self.client.list():
            if not _customer_owned(memory, customer_id):
                continue
            tags = [str(t) for t in (memory.get("tags") or [])]
            if KIND_PROCESSED not in tags or TAG_VERIFIED not in tags:
                continue
            dispute_id = _dispute_id_from_tags(tags)
            if not dispute_id or dispute_id == exclude_dispute_id or dispute_id in seen:
                continue
            seen.add(dispute_id)
            found.append(dispute_id)
        found.sort()
        return found

    def retrieve_for_investigation(self, context: Mapping[str, Any]) -> dict:
        customer_id = customer_id_from_context(context)
        dispute = context["dispute"]
        dispute_id = str(dispute["dispute_id"])
        reason = str(dispute.get("reason_code") or "")
        statement = str(dispute.get("customer_statement") or "")
        query = f"Processed dispute for {customer_id}. Claim reason {reason}. {statement}".strip()
        raw = self.client.query(query, chat_id=customer_scope(customer_id))
        owned = []
        leaked = []
        for item in raw.get("memories") or []:
            memory = item.get("memory") or {}
            if _customer_owned(memory, customer_id):
                owned.append(item)
            else:
                leaked.append(memory.get("id"))
        if leaked:
            raise RuntimeError("H-MEM query returned memories outside the requesting customer scope")
        previous_ids = self.verified_previous_dispute_ids(customer_id, exclude_dispute_id=dispute_id)
        count = len(previous_ids)
        human_review = count >= self.repeated_claim_threshold
        return {
            "customer_id": customer_id,
            "retrieved": owned,
            "reinjection": raw.get("context") or "",
            "trace": raw.get("trace") or {},
            "verified_previous_dispute_ids": previous_ids,
            "verified_previous_count": count,
            "repeated_claim_threshold": self.repeated_claim_threshold,
            "human_review_recommended": human_review,
            "fraud_inferred": False,
            "note": NOT_FRAUD_NOTE if human_review else "No repeated-claim human review recommended.",
        }
