"""Adversarial coherent-read checks using a labelled JDBC result stub."""
from copy import deepcopy
from datetime import timedelta
import json
from types import SimpleNamespace
import unittest

from app.fresh_tools import FreshSnapshot, snapshot_from_bundle
from integration import get_dispute_context as source
from integration.fresh_reads import read_bundle
import test_tools


class FreshReadTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_tools.RetrievalTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        raw = self.fixture.raw()
        raw['dispute']['evaluation_at'] = test_tools.NOW.isoformat().replace('+00:00', 'Z')
        self.bundle = dict(schema_version=1, source_revision=7,
            evaluation_at=raw['dispute']['evaluation_at'], context=raw, history=[], decisions=[])
        self.plan = 'Scan InsertableJDBCTableRelation(...) DISPUTE.dispute_read_bundle'
        self.revisions = [7, 7]
        self.channels, self.queries = [], []

    def factory(self):
        outer = self
        class Channel:
            closed = False
            def run(self, query, limit):
                outer.queries.append(query)
                if query.startswith('EXPLAIN '):
                    return SimpleNamespace(rows=[(outer.plan,)])
                if 'SELECT revision' in query:
                    return SimpleNamespace(rows=[(outer.revisions.pop(0),)])
                payload = outer.bundle if isinstance(outer.bundle, str) else json.dumps(outer.bundle)
                return SimpleNamespace(rows=[(payload,)])
            def close(self):
                self.closed = True
        channel = Channel()
        self.channels.append(channel)
        return channel

    def read(self):
        return read_bundle('DP-0014', channel_factory=self.factory, clock=lambda: test_tools.NOW)

    def test_fresh_typed_snapshot_and_direct_plan_for_every_select(self):
        bundle, captured = self.read()
        snapshot = snapshot_from_bundle(bundle, captured, source_channel='offline_test')
        self.assertEqual(snapshot, FreshSnapshot.from_dict(snapshot.to_dict()))
        self.assertEqual(snapshot.context.reference.source_revision, 7)
        self.assertEqual(len(self.queries), 6)
        self.assertTrue(all(c.closed for c in self.channels))

    def test_cached_unknown_or_wrong_datasource_fails_before_select(self):
        for plan in ('InMemoryTableScan', 'Scan JDBCRelation(...) DISPUTE.x',
                     'Scan InsertableJDBCTableRelation(...) OTHER.x', '',
                     self.plan + '\nScan CachedRelation X'):
            self.plan = plan
            self.queries.clear()
            with self.assertRaises(source.ReadUnavailable):
                self.read()
            self.assertEqual(len(self.queries), 1)

    def test_stale_cached_bundle_and_future_clock_fail_closed(self):
        for delta in (-1, 1):
            self.bundle['evaluation_at'] = (test_tools.NOW + timedelta(seconds=delta)).isoformat().replace('+00:00', 'Z')
            self.revisions = [7, 7]
            with self.assertRaises(source.ReadUnavailable):
                self.read()

    def test_revision_race_retries_only_twice(self):
        self.revisions = [6, 7, 7, 7]
        self.assertEqual(self.read()[0]['source_revision'], 7)
        self.assertEqual(len(self.channels), 2)
        self.revisions = [1, 2, 3, 4]
        with self.assertRaises(source.ReadIncomplete):
            self.read()
        self.assertEqual(len(self.channels), 4)

    def test_bundle_revision_mismatch_and_duplicate_json_rejected(self):
        self.bundle['source_revision'] = 6
        with self.assertRaises(source.InvalidSource):
            self.read()
        self.revisions = [7, 7]
        self.bundle = '{"schema_version":1,"schema_version":1}'
        with self.assertRaises(source.InvalidSource):
            self.read()

    def test_source_overflow_not_silently_truncated(self):
        self.bundle['history'] = [{}] * 1001
        with self.assertRaises(source.ReadIncomplete):
            self.read()

    def test_cross_case_and_cutoff_identity_mismatch_rejected(self):
        for field, value in (('dispute_id', 'DP-0001'), ('evaluation_at', '2026-01-01T00:00:00Z')):
            old = deepcopy(self.bundle)
            self.bundle['context']['dispute'][field] = value
            self.revisions = [7, 7]
            with self.assertRaises(source.InvalidSource):
                self.read()
            self.bundle = old
