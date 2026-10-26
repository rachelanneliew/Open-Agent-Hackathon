"""Offline SQL/typed boundary tests using isolated SQLite, not live Zetaris.

Only tests load source CSV/documents. No runtime fixture or filesystem reader.
"""
import copy
import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from app.schemas import ContractError, DisputeContext, SettlementStatus
from app.tools import CustomerHistory, ReadResult, ReadStatus, ReadTools, ReadToolRegistry
from integration import get_dispute_context as source

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)


class QueryChannel:
    def __init__(self, db):
        self.db, self.closed, self.queries = db, False, []

    def run(self, query, limit):
        assert query.startswith('SELECT ') and ';' not in query
        self.queries.append(query)
        return SimpleNamespace(rows=self.db.execute(query).fetchmany(limit))

    def close(self):
        self.closed = True


class Backend:
    def __init__(self, factory):
        self.factory = factory

    def get_dispute_context(self, did):
        return source.get_dispute_context(did, channel_factory=self.factory)

    def get_dispute_state(self, did):
        return source.get_dispute_state(did, channel_factory=self.factory)

    def get_customer_history(self, did):
        return source.get_customer_history(did, channel_factory=self.factory)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute("ATTACH DATABASE ':memory:' AS dispute")
        self.channels, self.tables = [], {}
        for name in ('disputes', 'transactions', 'settlements', 'evidence', 'policy_rules'):
            with (ROOT / f'data/synthetic/{name}.csv').open() as stream:
                reader = csv.DictReader(stream)
                columns, rows = reader.fieldnames, list(reader)
            definitions = ', '.join(c + (' INTEGER' if c.endswith('_minor') or c == 'priority' else ' TEXT') for c in columns)
            self.db.execute(f'CREATE TABLE dispute.{name} ({definitions})')
            self.db.executemany(f"INSERT INTO dispute.{name} VALUES ({','.join('?' for c in columns)})",
                                [[row[c] or None for c in columns] for row in rows])
            self.tables[name] = rows
        self.db.execute('CREATE TABLE dispute.evidence_documents (evidence_id TEXT, content TEXT)')
        self.db.executemany('INSERT INTO dispute.evidence_documents VALUES (?, ?)',
            [(r['evidence_id'], (ROOT / 'data/synthetic' / r['document_path']).read_text()) for r in self.tables['evidence']])
        self.backend = Backend(self.factory)
        self.tools = ReadTools(backend=self.backend, source_channel='offline_test', clock=lambda: NOW)

    def tearDown(self):
        self.db.close()

    def factory(self):
        channel = QueryChannel(self.db)
        self.channels.append(channel)
        return channel

    def raw(self):
        return self.backend.get_dispute_context('DP-0014')

    def from_raw(self, raw, method='get_dispute_context'):
        backend = Mock()
        getattr(backend, method).return_value = raw
        tools = ReadTools(backend=backend, source_channel='offline_test', clock=lambda: NOW)
        return getattr(tools, method)('DP-0014')

    def roundtrip(self, result):
        self.assertEqual(ReadResult.from_dict(json.loads(json.dumps(result.to_dict()))), result)

    def test_all_40_cases_map_to_strict_contexts_with_source_metadata(self):
        for row in self.tables['disputes']:
            with self.subTest(dispute=row['dispute_id']):
                result = self.tools.get_dispute_context(row['dispute_id'])
                self.assertEqual(result.status, ReadStatus.OK)
                self.assertIsInstance(result.data, DisputeContext)
                self.assertIsNone(result.data.reference.source_revision)
                self.assertEqual(result.data.source_channel, 'offline_test')
                self.assertEqual(result.data.dispute.dispute_status, 'open')
                self.assertTrue(all(t.customer_id and t.merchant_id and t.recorded_at for t in result.data.transactions))
                self.assertTrue(all(e.dispute_id == row['dispute_id'] and e.event_at for e in result.data.evidence))
                self.roundtrip(result)
        self.assertTrue(all(c.closed for c in self.channels))
        self.assertTrue(all(' LIMIT 1001' in q for c in self.channels for q in c.queries))

    def test_refunds_pending_and_failed_movements_preserved(self):
        self.assertEqual([s.amount_minor for s in self.tools.get_dispute_context('DP-0014').data.settlements], [10000, 4000])
        self.assertTrue(any(s.settlement_status is SettlementStatus.PENDING for s in self.tools.get_dispute_context('DP-0038').data.settlements))
        self.db.execute("UPDATE dispute.settlements SET settlement_status='failed' WHERE transaction_id='TX-0014'")
        self.assertTrue(all(s.settlement_status is SettlementStatus.FAILED for s in self.tools.get_dispute_context('DP-0014').data.settlements))

    def test_policy_selected_by_opening_not_evaluation(self):
        before, after = (self.tools.get_dispute_context(d).data for d in ('DP-0033', 'DP-0034'))
        self.assertEqual((before.reference.policy_version, after.reference.policy_version), ('v1', 'v2'))
        self.assertGreater(before.reference.evaluation_at, after.dispute.opened_at)
        self.assertEqual([p.priority for p in after.policy_rules], list(range(10, 81, 10)))

    def test_left_join_keeps_missing_text_metadata(self):
        eid = self.raw()['evidence'][0]['evidence_id']
        self.db.execute('DELETE FROM dispute.evidence_documents WHERE evidence_id=?', (eid,))
        result = self.tools.get_dispute_context('DP-0014')
        self.assertEqual(result.status, ReadStatus.INCOMPLETE)
        self.assertEqual(len(result.data.evidence), 2)
        self.assertIsNone(next(e for e in result.data.evidence if e.evidence_id == eid).content)
        self.assertIn('evidence_text_unavailable:' + eid, result.issues)
        self.roundtrip(result)

    def test_unreadable_incomplete_blank_null_text_is_not_support(self):
        for integrity, content in [('unreadable', 'text'), ('incomplete', 'partial'), ('valid', '  '), ('valid', None)]:
            raw = self.raw()
            raw['evidence'][0].update(integrity_status=integrity, content=content)
            result = self.from_raw(raw)
            self.assertEqual(result.status, ReadStatus.INCOMPLETE)
            self.assertIsNone(result.data.evidence[0].content)

    def test_missing_primary_and_companion_are_explicit(self):
        raw = self.raw()
        raw['transactions'] = []
        result = self.from_raw(raw)
        self.assertEqual(result.status, ReadStatus.INCOMPLETE)
        self.assertIn('transaction_unavailable:TX-0014', result.issues)
        raw = self.raw()
        raw['dispute']['related_transaction_id'] = 'TX-9999'
        self.assertIn('transaction_unavailable:TX-9999', self.from_raw(raw).issues)

    def test_missing_policy_does_not_invent_version(self):
        raw = self.raw()
        raw['policy_rules'] = []
        result = self.from_raw(raw)
        self.assertEqual(result.status, ReadStatus.INCOMPLETE)
        self.assertIsNone(result.data)
        self.roundtrip(result)

    def test_not_found_is_distinct_from_empty_optional_evidence(self):
        self.assertEqual(self.tools.get_dispute_context('DP-9999').status, ReadStatus.NOT_FOUND)
        self.db.execute("DELETE FROM dispute.evidence WHERE dispute_id='DP-0014'")
        result = self.tools.get_dispute_context('DP-0014')
        self.assertEqual(result.status, ReadStatus.OK)
        self.assertEqual(result.data.evidence, ())

    def test_scope_violations_expose_no_data(self):
        for collection, field, value in [('transactions', 'transaction_id', 'TX-0001'), ('settlements', 'transaction_id', 'TX-0001'), ('evidence', 'dispute_id', 'DP-0001')]:
            raw = self.raw()
            raw[collection][0][field] = value
            result = self.from_raw(raw)
            self.assertEqual(result.status, ReadStatus.MALFORMED)
            self.assertIsNone(result.data)
        raw = self.raw()
        raw['dispute']['dispute_id'] = 'DP-0001'
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)
        raw = self.raw()
        raw['dispute']['related_transaction_id'] = 'TX-9999'
        raw['transactions'].append({**raw['transactions'][0], 'transaction_id': 'TX-9999', 'customer_id': 'CUST-999'})
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)

    def test_inclusive_cutoff_and_defense_against_future_rows(self):
        raw = self.raw()
        cutoff = raw['dispute']['evaluation_at']
        later = (datetime.fromisoformat(cutoff.replace('Z', '+00:00')) + timedelta(microseconds=1)).isoformat().replace('+00:00', 'Z')
        for collection, field in [('transactions', 'recorded_at'), ('settlements', 'recorded_at'), ('evidence', 'available_at')]:
            changed = copy.deepcopy(raw)
            changed[collection][0][field] = cutoff
            self.assertEqual(len(getattr(self.from_raw(changed).data, collection)), len(raw[collection]))
            changed[collection][0][field] = later
            self.assertEqual(len(getattr(self.from_raw(changed).data, collection)), len(raw[collection]) - 1)
        self.assertEqual(len(self.tools.get_dispute_context('DP-0019').data.evidence), 1)

    def test_backend_filters_future_records(self):
        for table, field, key in [('transactions', 'recorded_at', 'transaction_id'), ('settlements', 'recorded_at', 'transaction_id'), ('evidence', 'available_at', 'dispute_id')]:
            value = 'DP-0014' if key == 'dispute_id' else 'TX-0014'
            self.db.execute(f"UPDATE dispute.{table} SET {field}='2026-12-01T00:00:00Z' WHERE {key}=?", (value,))
        result = self.tools.get_dispute_context('DP-0014')
        self.assertEqual(result.status, ReadStatus.INCOMPLETE)
        self.assertEqual((result.data.transactions, result.data.settlements, result.data.evidence), ((), (), ()))

    def test_malformed_fields_numbers_times_json_and_duplicate_ids(self):
        cases = [('transactions', 'amount_minor', v) for v in (True, 100.5, '10000', -1)] + [
            ('transactions', 'expected_outcome', 'credit'), ('evidence', 'event_at', 'not-a-date'),
            ('evidence', 'content', 123), ('policy_rules', 'condition_json', 'not-json'),
            ('policy_rules', 'condition_json', '{"predicate":"x","predicate":"y"}'),
            ('policy_rules', 'action', 'write_credit'), ('policy_rules', 'parameters_json', '[]')]
        for collection, field, value in cases:
            with self.subTest(collection=collection, field=field, value=value):
                raw = self.raw()
                raw[collection][0][field] = value
                self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)
        raw = self.raw()
        raw['transactions'][0].pop('recorded_at')
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)
        raw = self.raw()
        raw['settlements'].append(raw['settlements'][0])
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)

    def test_overlapping_versions_and_duplicate_priorities_rejected(self):
        raw = self.raw()
        raw['policy_rules'].append({**raw['policy_rules'][0], 'policy_rule_id': 'v3-DATA_INTEGRITY', 'policy_version': 'v3'})
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)
        raw = self.raw()
        raw['policy_rules'][1]['priority'] = raw['policy_rules'][0]['priority']
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)

    def test_history_for_all_cases_is_separate_customer_scoped_and_visible(self):
        for row in self.tables['disputes']:
            result = self.tools.get_customer_history(row['dispute_id'])
            self.assertEqual(result.status, ReadStatus.OK)
            history = result.data
            self.assertIsInstance(history, CustomerHistory)
            self.assertFalse(history.decisions_supported)
            self.assertIsNone(history.source_revision)
            expected = {d['dispute_id'] for d in self.tables['disputes'] if d['dispute_id'] != row['dispute_id']
                and d['opened_at'] <= row['evaluation_at'] and any(t['transaction_id'] == d['transaction_id']
                    and t['customer_id'] == history.customer_id and t['recorded_at'] <= row['evaluation_at'] for t in self.tables['transactions'])}
            self.assertEqual({c.dispute.dispute_id for c in history.cases}, expected)
            self.assertFalse(hasattr(history, 'evidence'))
            self.roundtrip(result)

    def test_history_rejects_cross_customer_current_case_duplicates_and_wrong_anchor(self):
        raw = self.backend.get_customer_history('DP-0014')
        self.assertTrue(raw['history'])
        for change in ('customer', 'current', 'duplicate', 'anchor'):
            changed = copy.deepcopy(raw)
            if change == 'customer':
                changed['history'][0]['transaction']['customer_id'] = 'CUST-999'
            elif change == 'current':
                changed['history'][0] = {'dispute': changed['dispute'], 'transaction': changed['anchor_transaction']}
            elif change == 'duplicate':
                changed['history'].append(changed['history'][0])
            else:
                changed['anchor_transaction']['transaction_id'] = 'TX-9999'
            result = self.from_raw(changed, 'get_customer_history')
            self.assertEqual(result.status, ReadStatus.MALFORMED)
            self.assertIsNone(result.data)

    def test_history_future_record_filter_and_missing_anchor(self):
        raw = self.backend.get_customer_history('DP-0014')
        for target, field in [('dispute', 'opened_at'), ('transaction', 'recorded_at')]:
            changed = copy.deepcopy(raw)
            changed['history'][0][target][field] = '2026-11-01T00:00:00Z'
            if target == 'dispute':
                changed['history'][0][target]['evaluation_at'] = '2026-11-02T00:00:00Z'
            result = self.from_raw(changed, 'get_customer_history')
            self.assertEqual(result.status, ReadStatus.OK)
            self.assertEqual(len(result.data.cases), len(raw['history']) - 1)
        self.db.execute("DELETE FROM dispute.transactions WHERE transaction_id='TX-0014'")
        self.assertEqual(self.tools.get_customer_history('DP-0014').status, ReadStatus.INCOMPLETE)

    def test_current_state_preserves_unknown_status_without_freshness_claim(self):
        self.db.execute("UPDATE dispute.disputes SET dispute_status='unknown_new_state' WHERE dispute_id='DP-0014'")
        result = self.tools.get_dispute_state('DP-0014')
        self.assertEqual(result.status, ReadStatus.OK)
        self.assertEqual(result.data.dispute.dispute_status, 'unknown_new_state')
        self.assertIsNone(result.data.source_revision)
        self.roundtrip(result)

    def test_decisions_unsupported_without_querying(self):
        result = self.tools.get_existing_decisions('DP-0014')
        self.assertEqual(result.status, ReadStatus.UNSUPPORTED)
        self.assertIsNone(result.data)
        self.assertEqual(self.channels, [])
        self.roundtrip(result)

    def test_registry_rejects_injection_extra_arguments_unknown_tools_and_cross_case(self):
        registry = ReadToolRegistry('DP-0014', tools=self.tools)
        attempts = [('run_sql', {'dispute_id': 'DP-0014'}), ('get_dispute_context', {'dispute_id': 'DP-0001'}),
                    ('get_dispute_context', {'dispute_id': "DP-0014'; DELETE FROM disputes"}),
                    ('get_dispute_context', {}), ('get_dispute_context', []), ([], {}), ('__dict__', {'dispute_id': 'DP-0014'})]
        attempts += [('get_dispute_context', {'dispute_id': 'DP-0014', extra: 'untrusted'})
                     for extra in ('sql', 'customer_id', 'evaluation_at', 'source_revision', 'path', 'channel_factory', 'expected_outcome')]
        for name, args in attempts:
            self.assertEqual(registry.dispatch(name, args).status, ReadStatus.INVALID_REQUEST)
        self.assertEqual(self.channels, [])
        self.assertEqual(registry.dispatch('get_dispute_context', {'dispute_id': 'DP-0014'}).status, ReadStatus.OK)
        for definition in registry.definitions():
            self.assertEqual(definition['parameters']['properties']['dispute_id']['enum'], ['DP-0014'])
            self.assertFalse(definition['parameters']['additionalProperties'])

    def test_invalid_id_never_opens_connection(self):
        for bad in (None, True, 'DP-１４００', 'DP-1', "DP-0014' OR 1=1"):
            for method in ('get_dispute_context', 'get_customer_history', 'get_dispute_state', 'get_existing_decisions'):
                self.assertEqual(getattr(self.tools, method)(bad).status, ReadStatus.INVALID_REQUEST)
            with self.assertRaises(ValueError):
                source.get_dispute_context(bad, channel_factory=self.factory)
        self.assertEqual(self.channels, [])

    def test_row_limit_is_incomplete_not_truncated_success(self):
        with patch.object(source, 'MAX_ROWS', 1):
            result = self.tools.get_dispute_context('DP-0014')
        self.assertEqual(result.status, ReadStatus.INCOMPLETE)
        self.assertIsNone(result.data)
        self.assertTrue(all(c.closed for c in self.channels))

    def test_each_query_and_close_failure_is_sanitized_unavailable(self):
        for stage in range(1, 6):
            channel = self.factory()
            original, calls = channel.run, 0
            def run(query, limit):
                nonlocal calls
                calls += 1
                if calls == stage:
                    raise RuntimeError('SECRET SQL and credentials')
                return original(query, limit)
            channel.run = run
            result = ReadTools(backend=Backend(lambda: channel), clock=lambda: NOW).get_dispute_context('DP-0014')
            self.assertEqual(result.status, ReadStatus.UNAVAILABLE)
            self.assertNotIn('SECRET', json.dumps(result.to_dict()))
            self.assertIsNone(result.data)
            self.assertTrue(channel.closed)
        channel = self.factory()
        channel.close = Mock(side_effect=RuntimeError('SECRET'))
        self.assertEqual(ReadTools(backend=Backend(lambda: channel), clock=lambda: NOW).get_dispute_context('DP-0014').status, ReadStatus.UNAVAILABLE)

    def test_connection_and_fetch_failures_not_empty_success(self):
        self.assertEqual(ReadTools(backend=Backend(Mock(side_effect=RuntimeError('SECRET')))).get_dispute_context('DP-0014').status, ReadStatus.UNAVAILABLE)
        adapter = source._ReadChannel.__new__(source._ReadChannel)
        adapter.channel = Mock()
        adapter.channel._cur.fetchmany.side_effect = RuntimeError('SECRET')
        with self.assertRaises(source.ReadUnavailable):
            source.records(adapter, 'SELECT 1', ('one',))
        adapter.channel._cur.fetchmany.assert_called_once_with(source.MAX_ROWS + 1)

    def test_malformed_responses_and_duplicate_case_not_not_found(self):
        for rows in ([[1]], [self.raw()['dispute']], None):
            channel = Mock()
            channel.run.return_value = SimpleNamespace(rows=rows)
            result = ReadTools(backend=Backend(lambda: channel)).get_dispute_context('DP-0014')
            self.assertEqual(result.status, ReadStatus.MALFORMED)
            channel.close.assert_called_once()
        self.db.execute("INSERT INTO dispute.disputes SELECT * FROM dispute.disputes WHERE dispute_id='DP-0014'")
        self.assertEqual(self.tools.get_dispute_context('DP-0014').status, ReadStatus.MALFORMED)

    def test_result_contract_forbids_data_on_failure_or_empty_success(self):
        result = self.tools.get_dispute_context('DP-0014')
        with self.assertRaises(ContractError):
            ReadResult(status=ReadStatus.UNAVAILABLE, message='failed', data=result.data)
        with self.assertRaises(ContractError):
            ReadResult(status=ReadStatus.OK, message='empty')

    def test_backend_error_text_and_non_finite_json_are_not_exposed(self):
        for error, status in [(source.ReadIncomplete('SECRET'), ReadStatus.INCOMPLETE),
                              (RuntimeError('SECRET'), ReadStatus.UNAVAILABLE)]:
            backend = Mock()
            backend.get_customer_history.side_effect = error
            result = ReadTools(backend=backend).get_customer_history('DP-0014')
            self.assertEqual(result.status, status)
            self.assertNotIn('SECRET', json.dumps(result.to_dict()))
        raw = self.raw()
        raw['policy_rules'][0]['parameters_json'] = '{"limit":NaN}'
        self.assertEqual(self.from_raw(raw).status, ReadStatus.MALFORMED)

    def test_source_text_timestamps_compare_as_instants_with_fractional_seconds(self):
        cutoff = self.raw()['dispute']['evaluation_at']
        self.db.execute("UPDATE dispute.disputes SET evaluation_at=? WHERE dispute_id='DP-0014'", (cutoff.replace('Z', '.000001Z'),))
        self.db.execute("UPDATE dispute.evidence SET available_at=? WHERE dispute_id='DP-0014'", (cutoff,))
        self.assertEqual(len(self.tools.get_dispute_context('DP-0014').data.evidence), 2)
        self.db.execute("UPDATE dispute.evidence SET available_at=? WHERE dispute_id='DP-0014'", (cutoff.replace('Z', '.000002Z'),))
        self.assertEqual(len(self.tools.get_dispute_context('DP-0014').data.evidence), 0)


if __name__ == '__main__':
    unittest.main()
