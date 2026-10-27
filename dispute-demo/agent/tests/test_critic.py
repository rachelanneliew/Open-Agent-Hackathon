"""Offline regression for the retired SQLite writer; no external reference."""
from contextlib import ExitStack
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from agent import critic
from app.critic import policy_rationale, review_proposal


class CriticCompatibilityTests(unittest.TestCase):
    def call_without_io(self, context, proposal, path=None):
        with ExitStack() as stack:
            for target in ('builtins.open', 'io.open', 'os.open', 'os.mkdir', 'sqlite3.connect',
                           'socket.socket', 'subprocess.Popen'):
                stack.enter_context(patch(target, side_effect=AssertionError('Legacy critic I/O')))
            result = critic.review_and_simulate(context, proposal, ledger_path=path)
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['reason_code'], 'LEGACY_ACTION_PATH_RETIRED')
        self.assertFalse(result['simulated_credit_created'])
        return result

    def test_legacy_calls_cannot_write_any_outcome_or_malformed_input(self):
        for outcome in ('recommend_refund', 'reject', 'request_evidence', 'escalate', 'invalid'):
            self.call_without_io({}, {'outcome': outcome})
        self.call_without_io(None, None)

    def test_existing_local_state_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'existing.sqlite3'
            ledger.write_bytes(b'Existing user state: do not open or migrate.')
            before = ledger.read_bytes()
            self.call_without_io({}, {}, ledger)
            self.assertEqual(ledger.read_bytes(), before)

    def test_absent_state_stays_absent_and_retries_do_not_create_it(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / 'new' / 'credits.sqlite3'
            one = self.call_without_io({}, {}, ledger)
            self.assertEqual(one, self.call_without_io({}, {}, ledger))
            self.assertFalse(ledger.parent.exists())

    def test_old_module_delegates_only_to_canonical_pure_validator(self):
        self.assertIs(critic.review_proposal, review_proposal)
        self.assertIs(critic.policy_rationale, policy_rationale)
        self.assertIsNone(critic.DEFAULT_LEDGER)


if __name__ == '__main__':
    unittest.main()
