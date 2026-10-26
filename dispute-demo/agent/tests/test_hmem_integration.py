"""Offline H-MEM integration tests. No Zetaris, env files, or expected-result fixtures."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hmem_client import HmemClient
from memory_service import DisputeMemory, NOT_FRAUD_NOTE
import resolver


POLICY = {
    "dispute_id": "DP-0014",
    "policy_version": "v2",
    "currency": "SGD",
    "outcome": "recommend_refund",
    "recommended_refund_minor": 6000,
    "matched_policy_rule_id": "v2-APPROVE",
    "evidence_ids": ["EV-0027"],
}
CRITIC_OK = {
    "status": "simulated_credit_recorded",
    "reason_code": "POLICY_CONFIRMED",
    "dispute_id": "DP-0014",
    "policy_outcome": "recommend_refund",
    "simulated_credit_created": True,
    "recommended_refund_minor": 6000,
}


def _context(dispute_id: str, customer_id: str, reason: str = "not_received") -> dict:
    return {
        "dispute": {
            "dispute_id": dispute_id,
            "transaction_id": f"TX-{dispute_id[3:]}",
            "customer_id": customer_id,
            "reason_code": reason,
            "customer_statement": "I paid for this order, but it has not arrived.",
            "claimed_amount_minor": 6000,
            "currency": "SGD",
        },
        "transactions": [{"transaction_id": f"TX-{dispute_id[3:]}", "customer_id": customer_id}],
    }


class HmemMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.client = HmemClient(Path(self.temp.name) / "hmem")
        self.memory = DisputeMemory(self.client, repeated_claim_threshold=2)

    def tearDown(self):
        self.temp.cleanup()

    def _remember(self, dispute_id: str, customer_id: str, reason: str = "not_received") -> dict:
        policy = {**POLICY, "dispute_id": dispute_id}
        critic = {**CRITIC_OK, "dispute_id": dispute_id}
        return self.memory.remember_processed_dispute(
            _context(dispute_id, customer_id, reason), policy, critic, verified=True
        )

    def test_memory_creation_is_provenance_backed(self):
        record = self._remember("DP-0014", "CUST-006")
        self.assertTrue(record["id"].startswith("mem-"))
        self.assertEqual(record["source"], "dispute-agent:DP-0014")
        self.assertEqual(record["chatId"], "customer:CUST-006")
        self.assertIn("customer:CUST-006", record["tags"])
        self.assertEqual(record["provenance"]["origin"], "plan_completion")
        self.assertTrue(record["provenance"]["label"])
        listed = self.client.list()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["id"], record["id"])

    def test_retrieval_returns_relevant_customer_memories(self):
        stored = self._remember("DP-0014", "CUST-006")
        view = self.memory.retrieve_for_investigation(_context("DP-0015", "CUST-006"))
        ids = [item["memory"]["id"] for item in view["retrieved"]]
        self.assertIn(stored["id"], ids)
        self.assertEqual(view["verified_previous_dispute_ids"], ["DP-0014"])
        self.assertFalse(view["fraud_inferred"])

    def test_customer_isolation(self):
        secret = self._remember("DP-0014", "CUST-006")
        view = self.memory.retrieve_for_investigation(_context("DP-0020", "CUST-009"))
        ids = [item["memory"]["id"] for item in view["retrieved"]]
        self.assertNotIn(secret["id"], ids)
        self.assertEqual(view["verified_previous_count"], 0)
        self.assertEqual(view["customer_id"], "CUST-009")
        blob = json.dumps(view)
        self.assertNotIn("CUST-006", blob)
        self.assertNotIn(secret["id"], blob)
        self.assertNotIn("DP-0014", blob)

    def test_repeated_claims_recommend_review_not_fraud(self):
        self._remember("DP-0014", "CUST-006")
        self._remember("DP-0016", "CUST-006")
        view = self.memory.retrieve_for_investigation(_context("DP-0017", "CUST-006"))
        self.assertEqual(view["verified_previous_count"], 2)
        self.assertTrue(view["human_review_recommended"])
        self.assertFalse(view["fraud_inferred"])
        self.assertEqual(view["note"], NOT_FRAUD_NOTE)

    def test_below_threshold_does_not_escalate(self):
        self._remember("DP-0014", "CUST-006")
        view = self.memory.retrieve_for_investigation(_context("DP-0015", "CUST-006"))
        self.assertEqual(view["verified_previous_count"], 1)
        self.assertFalse(view["human_review_recommended"])


class ResolverGuardrailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.persist = Path(self.temp.name) / "hmem"
        self.client = HmemClient(self.persist)

    def tearDown(self):
        self.temp.cleanup()

    def test_memory_does_not_override_policy_or_critic(self):
        mem = DisputeMemory(self.client, repeated_claim_threshold=1)
        mem.remember_processed_dispute(_context("DP-0014", "CUST-006"), POLICY, CRITIC_OK, verified=True)
        policy = copy.deepcopy(POLICY)
        policy["dispute_id"] = "DP-0018"
        critic = {
            "status": "simulated_credit_recorded",
            "reason_code": "POLICY_CONFIRMED",
            "dispute_id": "DP-0018",
            "policy_outcome": "recommend_refund",
            "simulated_credit_created": True,
        }
        with patch.object(resolver, "evaluate_dispute", return_value=policy) as policy_fn, \
             patch.object(resolver, "review_and_simulate", return_value=critic) as critic_fn:
            result = resolver.investigate_dispute(
                _context("DP-0018", "CUST-006"),
                repeated_claim_threshold=1,
                persist_dir=self.persist,
                ledger_path=Path(self.temp.name) / "credits.sqlite3",
                hmem_client=self.client,
            )
        self.assertEqual(result["policy"]["outcome"], "recommend_refund")
        self.assertTrue(result["human_review_recommended"])
        self.assertFalse(result["fraud_inferred"])
        self.assertFalse(result["policy_overridden_by_memory"])
        self.assertEqual(result["critic"]["policy_outcome"], "recommend_refund")
        submitted = critic_fn.call_args.args[1]
        self.assertEqual(submitted["outcome"], "recommend_refund")
        self.assertNotEqual(submitted["outcome"], "reject")
        policy_fn.assert_called_once()

    def test_forged_memory_based_reject_still_goes_to_critic(self):
        policy = copy.deepcopy(POLICY)
        blocked = {
            "status": "blocked",
            "reason_code": "POLICY_MISMATCH",
            "simulated_credit_created": False,
            "policy_outcome": "recommend_refund",
        }
        forged = {**POLICY, "outcome": "reject", "recommended_refund_minor": 0}
        with patch.object(resolver, "evaluate_dispute", return_value=policy), \
             patch.object(resolver, "review_and_simulate", return_value=blocked) as critic_fn:
            result = resolver.investigate_dispute(
                _context("DP-0014", "CUST-006"),
                forged,
                persist_dir=self.persist,
                ledger_path=Path(self.temp.name) / "credits.sqlite3",
                hmem_client=self.client,
                remember=True,
            )
        self.assertEqual(critic_fn.call_args.args[1]["outcome"], "reject")
        self.assertIsNone(result["stored_memory"])
        self.assertEqual(result["critic"]["reason_code"], "POLICY_MISMATCH")


if __name__ == "__main__":
    unittest.main()
