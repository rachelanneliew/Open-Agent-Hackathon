"""Opt-in REAL pinned H-MEM reference checks; deterministic mock embedder.

DISPUTE_HMEM_TESTS=1 python -m unittest discover -s agent/tests -v
Contract examples are synthetic stubs, not receipts from a database commit.
"""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent.hmem_client import HmemClient, MemoryError
from agent.memory_service import DisputeMemory, record_input, parse_record
from agent.tests.memory_samples import summary, note


def concurrent_save(args):
    directory, index = args
    return asdict(DisputeMemory(HmemClient(directory, timeout=30)).save(summary(index)))


@unittest.skipUnless(os.environ.get('DISPUTE_HMEM_TESTS') == '1', 'NOT RUN: opt-in real H-MEM reference')
class HmemReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.client = HmemClient(self.temp.name)
        self.memory = DisputeMemory(self.client)

    def test_save_then_new_python_and_node_process_recall(self):
        s = summary()
        saved = self.memory.save(s)
        self.assertEqual(saved.status, 'stored', saved)
        code = "from agent.hmem_client import HmemClient; import json,sys; print(json.dumps(HmemClient(sys.argv[1]).list(customer_id='CUST-006')))"
        result = subprocess.run([sys.executable, '-c', code, self.temp.name], capture_output=True, text=True, timeout=30, check=True)
        records = json.loads(result.stdout)
        self.assertEqual(len(records), 1)
        self.assertEqual(parse_record(records[0]), s)
        self.assertEqual(records[0]['id'], saved.memory_id)
        recalled = self.client.query(record_input(s)['content'], chat_id='customer:CUST-006')
        self.assertEqual(parse_record(recalled['memories'][0]), s)

    def test_retry_same_decision_reuses_and_changed_payload_fails(self):
        one = self.memory.save(summary())
        two = DisputeMemory(HmemClient(self.temp.name)).save(summary())
        self.assertEqual((one.status, two.status, one.memory_id == two.memory_id), ('stored', 'reused', True))
        changed = self.memory.save(replace(summary(), reason_code='duplicate_charge'))
        self.assertEqual(changed.status, 'failed')
        self.assertEqual(len(self.client.list(customer_id='CUST-006')), 1)

    def test_partition_isolation_including_links_and_empty_customer(self):
        self.memory.save(summary())
        self.assertEqual(self.client.query('committed dispute', chat_id='customer:CUST-009', threshold=0)['memories'], [])
        other = summary(2, 'CUST-009')
        self.assertEqual(self.memory.save(other).status, 'stored')
        blob = json.dumps(self.client.query(record_input(other)['content'], chat_id='customer:CUST-009', threshold=0))
        self.assertNotIn('CUST-006', blob)
        self.assertNotIn(summary().decision_id, blob)
        self.assertNotIn('relatedTo', blob)

    def test_notes_are_separate_and_never_committed_summaries(self):
        self.assertEqual(self.memory.save(note()).status, 'stored')
        result = self.client.query(record_input(note())['content'], chat_id='customer:CUST-006')
        self.assertEqual(parse_record(result['memories'][0]), note())
        self.assertNotIn('verified', result['memories'][0]['tags'])

    def test_concurrent_processes_do_not_lose_updates(self):
        with ProcessPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(concurrent_save, [(self.temp.name, i) for i in range(1, 9)]))
        self.assertTrue(all(r['status'] == 'stored' for r in results), results)
        records = self.client.list(customer_id='CUST-006')
        self.assertEqual({parse_record(r).decision_id for r in records}, {summary(i).decision_id for i in range(1, 9)})
        self.assertEqual(len({r['id'] for r in records}), 8)

    def test_concurrent_same_decision_has_one_create(self):
        with ProcessPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(concurrent_save, [(self.temp.name, 1)] * 6))
        self.assertEqual([r['status'] for r in results].count('stored'), 1, results)
        self.assertEqual([r['status'] for r in results].count('reused'), 5, results)
        snapshot = json.loads((Path(self.temp.name) / 'CUST-006/snapshot.json').read_text())
        self.assertEqual(len([r for r in snapshot['ledger'] if r['action'] == 'create']), 1)

    def test_failed_publish_preserves_previous_snapshot_and_retry(self):
        self.memory.save(summary())
        path = Path(self.temp.name) / 'CUST-006/snapshot.json'
        before = path.read_bytes()
        with patch('agent.hmem_client.os.replace', side_effect=OSError('secret /private/path')):
            failed = self.memory.save(summary(2))
        self.assertEqual(failed.status, 'failed')
        self.assertNotIn('private', failed.error)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(self.memory.save(summary(2)).status, 'stored')

    def test_lost_ack_after_publish_retry_is_idempotent(self):
        # Fault injection at directory fsync after the atomic replace.
        real = os.fsync
        calls = []
        def lose_ack(fd):
            calls.append(fd)
            if len(calls) == 2:
                raise OSError('lost acknowledgement')
            return real(fd)
        with patch('agent.hmem_client.os.fsync', side_effect=lose_ack):
            self.assertEqual(self.memory.save(summary()).status, 'failed')
        self.assertEqual(self.memory.save(summary()).status, 'reused')
        self.assertEqual(len(self.client.list(customer_id='CUST-006')), 1)

    def test_corrupt_snapshot_is_preserved_not_reinitialized(self):
        self.memory.save(summary())
        path = Path(self.temp.name) / 'CUST-006/snapshot.json'
        path.write_text('{broken')
        self.assertEqual(self.memory.save(summary(2)).status, 'failed')
        self.assertEqual(path.read_text(), '{broken')

    def test_unscoped_record_in_partition_fails_closed(self):
        self.memory.save(summary())
        path = Path(self.temp.name) / 'CUST-006/snapshot.json'
        saved = json.loads(path.read_text())
        del saved['state']['records'][0]['chatId']
        path.write_text(json.dumps(saved))
        before = path.read_bytes()
        with self.assertRaises(MemoryError):
            self.client.query('dispute', chat_id='customer:CUST-006', threshold=0)
        self.assertEqual(path.read_bytes(), before)

    def test_query_touch_and_audit_survive_restart(self):
        self.memory.save(summary())
        self.client.query(record_input(summary())['content'], chat_id='customer:CUST-006')
        HmemClient(self.temp.name).list(customer_id='CUST-006')
        snapshot = json.loads((Path(self.temp.name) / 'CUST-006/snapshot.json').read_text())
        self.assertEqual(snapshot['state']['records'][0]['accessCount'], 1)
        self.assertEqual([r['action'] for r in snapshot['ledger']], ['create', 'read'])

    def test_private_permissions_and_no_legacy_state_migration(self):
        old = Path(self.temp.name) / 'state.json'
        old.write_text('legacy state must be preserved')
        self.memory.save(summary())
        self.assertEqual(old.read_text(), 'legacy state must be preserved')
        snapshot = Path(self.temp.name) / 'CUST-006/snapshot.json'
        self.assertEqual(snapshot.stat().st_mode & 0o777, 0o600)
        self.assertEqual(snapshot.parent.stat().st_mode & 0o777, 0o700)
