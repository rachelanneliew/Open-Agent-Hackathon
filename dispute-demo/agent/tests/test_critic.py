"""Offline unit tests for the critic; no database server, model, or Zetaris needed."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import critic

DECISION = {
    "dispute_id": "DP-0014",
    "policy_version": "v2",
    "currency": "SGD",
    "outcome": "recommend_refund",
    "recommended_refund_minor": 6000,
    "matched_policy_rule_id": "v2-APPROVE",
    "evidence_ids": ["EV-0027", "EV-0028"],
}
CONTEXT = {
    "dispute": {"dispute_id": "DP-0014", "transaction_id": "TX-0014"},
    "transactions": [{"transaction_id": "TX-0014"}],
}


class CriticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "test.sqlite3"
        self.patch = patch.object(critic, "evaluate_dispute", return_value=copy.deepcopy(DECISION))
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_first_credit_succeeds_second_blocked(self):
        one = critic.review_and_simulate(CONTEXT, DECISION, ledger_path=self.ledger)
        two = critic.review_and_simulate(CONTEXT, DECISION, ledger_path=self.ledger)
        self.assertEqual(one["status"], "simulated_credit_recorded")
        self.assertTrue(one["simulated_credit_created"])
        self.assertEqual(two["reason_code"], "DUPLICATE_CREDIT")
        self.assertFalse(two["simulated_credit_created"])

    def test_overcredit_blocked(self):
        forged = {**DECISION, "recommended_refund_minor": 10000}
        result = critic.review_and_simulate(CONTEXT, forged, ledger_path=self.ledger)
        self.assertEqual(result["reason_code"], "POLICY_MISMATCH")
        self.assertFalse(self.ledger.exists())

    def test_wrong_action_blocked(self):
        forged = {**DECISION, "outcome": "reject", "recommended_refund_minor": 0}
        result = critic.review_and_simulate(CONTEXT, forged, ledger_path=self.ledger)
        self.assertEqual(result["reason_code"], "POLICY_MISMATCH")

    def test_fabricated_evidence_blocked(self):
        forged = {**DECISION, "evidence_ids": ["EV-FAKE"]}
        result = critic.review_and_simulate(CONTEXT, forged, ledger_path=self.ledger)
        self.assertEqual(result["reason_code"], "UNVERIFIED_EVIDENCE")

    def test_non_credit_proposal_is_advisory(self):
        other = {**DECISION, "outcome": "escalate", "recommended_refund_minor": 0}
        critic.evaluate_dispute.return_value = other
        result = critic.review_and_simulate(CONTEXT, other, ledger_path=self.ledger)
        self.assertEqual(result["status"], "validated_non_credit_action")
        self.assertFalse(result["simulated_credit_created"])
        self.assertFalse(self.ledger.exists())

    def test_other_dispute_same_transaction_blocked(self):
        critic.review_and_simulate(CONTEXT, DECISION, ledger_path=self.ledger)
        new_case = {"dispute": {"dispute_id": "DP-0041", "transaction_id": "TX-0014"},
                    "transactions": [{"transaction_id": "TX-0014"}]}
        next_decision = {**DECISION, "dispute_id": "DP-0041"}
        critic.evaluate_dispute.return_value = next_decision
        result = critic.review_and_simulate(new_case, next_decision, ledger_path=self.ledger)
        self.assertEqual(result["reason_code"], "DUPLICATE_CREDIT")


if __name__ == "__main__":
    unittest.main()
