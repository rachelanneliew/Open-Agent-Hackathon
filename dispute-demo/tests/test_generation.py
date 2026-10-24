"""Tests for reproducibility and meaningful scenario boundaries; no agent is implemented."""
import csv
import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from generate_synthetic_data import generate
from validate_synthetic_data import instant, validate


class GenerationTests(unittest.TestCase):
    def test_reproducibility_and_scenario_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a', Path(temp) / 'b'
            a.mkdir(); b.mkdir()
            expected, _ = generate(2026, '2026-10-20', 40, a)
            second, _ = generate(2026, '2026-10-20', 40, b)
            self.assertEqual(expected, second)
            self.assertEqual({str(p.relative_to(a)): p.read_bytes() for p in a.rglob('*') if p.is_file()},
                             {str(p.relative_to(b)): p.read_bytes() for p in b.rglob('*') if p.is_file()})
            counts = validate(a, expected)
            self.assertEqual(counts['disputes'], 40)
            self.assertGreater(counts['transactions'], 40)  # Real second charge for duplicate cases.
            self.assertEqual(len(expected), 40)
            by_id = {f['dispute_id']: f for f in expected}
            self.assertEqual(by_id['DP-0014']['expected_refund_minor'], 6000)
            self.assertEqual(by_id['DP-0033']['expected_outcome'], 'reject')
            self.assertEqual(by_id['DP-0034']['expected_outcome'], 'recommend_refund')
            self.assertEqual(by_id['DP-0003']['expected_refund_minor'], 20000)
            self.assertEqual(by_id['DP-0008']['expected_outcome'], 'escalate')
            self.assertEqual(by_id['DP-0008']['required_reason_codes'], ['REVIEW_THRESHOLD'])
            self.assertEqual(len(by_id['DP-0019']['forbidden_evidence_ids']), 1)
            with (a / 'transactions.csv').open() as f:
                txs = {r['transaction_id']: r for r in csv.DictReader(f)}
            with (a / 'disputes.csv').open() as f:
                disputes = {r['dispute_id']: r for r in csv.DictReader(f)}
            for did, days, seconds in [('DP-0001', 30, 0), ('DP-0002', 45, 0), ('DP-0029', 30, 1), ('DP-0030', 45, 1)]:
                case = disputes[did]
                elapsed = instant(case['opened_at']) - instant(txs[case['transaction_id']]['occurred_at'])
                self.assertEqual(elapsed, timedelta(days=days, seconds=seconds))
            # A tampered file must be detected, even when it remains parseable CSV.
            with (a / 'transactions.csv').open('a') as file:
                file.write('\n')
            with self.assertRaisesRegex(ValueError, 'File changed since generation'):
                validate(a, expected)

    def test_supported_sizes_and_different_seed(self):
        with tempfile.TemporaryDirectory() as temp:
            for count in (20, 50):
                path = Path(temp) / str(count)
                path.mkdir()
                fixtures, _ = generate(2027, '2026-10-20', count, path)
                self.assertEqual(validate(path, fixtures)['disputes'], count)
                self.assertEqual(sum(f['scenario_id'].startswith('policy_pair:') for f in fixtures), 4)
                self.assertEqual(sum(f['scenario_id'].startswith('settlement_anomaly:') for f in fixtures), 4)


if __name__ == '__main__':
    unittest.main()
