"""Offline contract, process-fault and persistence-boundary tests (no H-MEM)."""
from dataclasses import replace
from datetime import timedelta
import fcntl
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from app.schemas import CommitResult, ContractError, ExecutionStatus
from agent import resolver
from agent.hmem_client import HmemClient, MemoryError, bounded_process, strict_json
from agent.memory_service import CommittedSummary, DisputeMemory, parse_record, record_input
from agent.tests.memory_samples import summary, note, ident
import test_tools


class MemoryContractTests(unittest.TestCase):
    def test_roundtrip_retains_ids_times_policy_revision_and_source(self):
        s = summary()
        self.assertEqual(CommittedSummary.from_dict(s.to_dict()), s)
        record = record_input(s)
        self.assertIn(s.source_reference, record['provenance']['refs'])
        self.assertEqual(parse_record(record), s)

    def test_summary_has_no_free_model_text_or_personal_details(self):
        fields = set(summary().to_dict())
        self.assertNotIn('rationale', fields)
        self.assertNotIn('customer_statement', fields)
        self.assertNotIn('name', fields)
        self.assertNotIn('verified', record_input(summary())['tags'])

    def test_invalid_summary_source_revision_and_credit_shape_rejected(self):
        for patch_value in ({'source_reference': 'invented'}, {'reference': replace(summary().reference, source_revision=None)},
                            {'committed_at': summary().committed_at - timedelta(days=1)}, {'simulated_credit_id': None}):
            with self.assertRaises(ContractError):
                replace(summary(), **patch_value)

    def test_note_cannot_be_promoted_by_tag(self):
        n = note()
        record = record_input(n)
        self.assertEqual(parse_record(record), n)
        record['tags'].append('verified')
        with self.assertRaises(ContractError):
            parse_record(record)

    def test_fake_provenance_or_customer_rejected(self):
        for key, value in [('chatId', 'customer:CUST-009'), ('source', 'decision:' + ident('fake')),
                           ('provenance', {'refs': ['fake']}), ('content', '{"kind":"made_up","data":{}}')]:
            record = record_input(summary())
            record[key] = value
            with self.assertRaises((ContractError, ValueError)):
                parse_record(record)

    def test_save_failure_and_retry_never_access_actions(self):
        client = Mock()
        client.add.side_effect = [MemoryError('memory_timeout'), dict(storage_status='reused', memory=dict(record_input(summary()), id='mem-1'))]
        memory = DisputeMemory(client)
        with patch('app.action_service.commit_simulated_decision', side_effect=AssertionError('No action retry')):
            one, two = memory.save(summary()), memory.save(summary())
        self.assertEqual((one.status, two.status), ('failed', 'reused'))
        self.assertEqual(client.add.call_args_list[0], client.add.call_args_list[1])

    def test_refuse_failed_commit_and_context_mismatch(self):
        source = test_tools.RetrievalTests()
        source.setUp()
        self.addCleanup(source.tearDown)
        context = source.tools.get_dispute_context('DP-0014').data
        context = replace(context, reference=replace(context.reference, source_revision=3))
        failed = CommitResult(run_id=ident('run'), proposal_id=ident('proposal'), idempotency_key=ident('key'),
            reference=context.reference, status=ExecutionStatus.FAILED, message='not committed')
        client = Mock()
        with self.assertRaises(ContractError):
            DisputeMemory(client).remember_commit(context, failed)
        client.add.assert_not_called()
        s = summary()
        committed = replace(failed, status=ExecutionStatus.COMMITTED, decision_id=s.decision_id,
            recommendation=s.recommendation, committed_at=context.captured_at,
            simulated_credit_id=s.simulated_credit_id)
        built = CommittedSummary.from_commit(context, committed)
        self.assertEqual(built.customer_id, 'CUST-008')
        self.assertEqual(built.reference.dispute_id, 'DP-0014')
        reused = replace(committed, status=ExecutionStatus.REUSED)
        self.assertEqual(built, CommittedSummary.from_commit(context, reused))
        with self.assertRaises(ContractError):
            CommittedSummary.from_commit(context, replace(committed, reference=replace(context.reference, source_revision=4)))

    def test_legacy_resolver_is_inert_without_path_injection_or_threshold(self):
        with patch('subprocess.Popen', side_effect=AssertionError('No legacy I/O')):
            self.assertFalse(resolver.investigate_dispute({}, remember=True)['persisted'])
        self.assertFalse(hasattr(resolver, 'DEFAULT_REPEATED_CLAIM_THRESHOLD'))


class MemoryBoundaryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.client = HmemClient(self.root)

    def test_import_and_constructor_do_not_initialize_services_or_state(self):
        target = self.root / 'absent'
        with patch('subprocess.Popen', side_effect=AssertionError('No startup')):
            HmemClient(target)
        self.assertFalse(target.exists())

    def test_missing_dependency_error_is_sanitized(self):
        with patch.dict(os.environ, {'HMEM_REFERENCE_SRC': '/private/secret/missing.ts'}):
            with self.assertRaisesRegex(MemoryError, '^memory_dependency_missing$'):
                self.client.list(customer_id='CUST-006')
        self.assertFalse((self.root / 'CUST-006').exists())

    def test_query_rejects_unsafe_scope_and_unbounded_parameters(self):
        for args in ({'chat_id': 'customer:../../private'}, {'chat_id': 'customer:CUST-006', 'top_n': True},
                     {'chat_id': 'customer:CUST-006', 'threshold': float('nan')}):
            with self.assertRaises(MemoryError):
                self.client.query('dispute', **args)

    def test_json_rejects_duplicate_keys_nan_extra_lines(self):
        for raw in ('{"ok":true,"ok":false}', '{"n":NaN}', '{"n":1e999}', '['*2000+'0'+']'*2000, '{}\n{}', 'log\n{}'):
            with self.assertRaises(ValueError):
                strict_json(raw)

    def test_output_scope_and_extra_fields_are_rejected(self):
        rec = dict(record_input(summary()), id='mem-1', timestamp=1)
        rec = {k: rec[k] for k in ('id', 'content', 'source', 'chatId', 'tags', 'provenance', 'timestamp')}
        HmemClient._validate_result(dict(ok=True, memories=[rec]), 'query', 'CUST-006')
        with self.assertRaises(MemoryError):
            HmemClient._validate_result(dict(ok=True, memories=[rec]), 'query', 'CUST-009')
        with self.assertRaises(MemoryError):
            HmemClient._validate_result(dict(ok=True, memories=[], extra='leak'), 'query', 'CUST-006')

    def test_process_timeout_is_bounded_and_sanitized(self):
        start = time.monotonic()
        with self.assertRaisesRegex(MemoryError, '^memory_timeout$'):
            bounded_process([sys.executable, '-c', 'import time; time.sleep(10)'], b'', env={}, deadline=start+.15)
        self.assertLess(time.monotonic() - start, 2)

    def test_oversized_stdout_or_stderr_stops_process(self):
        for name in ('stdout', 'stderr'):
            with self.assertRaisesRegex(MemoryError, '^memory_output_limit$'):
                bounded_process([sys.executable, '-c', f'import sys; sys.{name}.write("x"*300000)'], b'', env={}, deadline=time.monotonic()+3)

    def test_raw_error_and_path_never_escape(self):
        with self.assertRaisesRegex(MemoryError, '^memory_reference_failed$'):
            bounded_process([sys.executable, '-c', 'import sys; sys.stderr.write("secret /private/key"); sys.exit(1)'], b'', env={}, deadline=time.monotonic()+3)

    def test_lock_timeout(self):
        with self.client._locked('CUST-006', time.monotonic()+1):
            with self.assertRaisesRegex(MemoryError, '^memory_lock_timeout$'):
                with self.client._locked('CUST-006', time.monotonic()+.05):
                    self.fail('Second lock must not succeed')

    def test_symlink_partition_is_rejected(self):
        (self.root / 'CUST-006').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(MemoryError, '^memory_store_invalid$'):
            with self.client._locked('CUST-006', time.monotonic()+1):
                self.fail('Symlink must not be followed')

    def test_source_hash_mismatch_is_rejected_before_process_start(self):
        import agent.hmem_client as module
        reference = self.root / 'index.ts'
        reference.write_text('modified reference')
        runner = self.root / 'tsx'
        runner.mkdir()
        (runner / 'package.json').write_text('{"version":"4.23.15"}')
        pin = {'runtime_sha256': {'index.ts': 'wrong'}, 'tsx': '4.23.15', 'node': '24.13.0'}
        with patch.dict(os.environ, {'HMEM_REFERENCE_SRC': str(reference), 'HMEM_TSX_PACKAGE': str(runner)}), \
                patch.object(module.json, 'loads', return_value=pin), \
                patch.object(module, 'bounded_process', side_effect=AssertionError('No execution of changed source')):
            with self.assertRaisesRegex(MemoryError, '^memory_reference_pin_mismatch$'):
                self.client._runtime(time.monotonic()+1)

    def test_nonfinite_and_boolean_timeout_rejected(self):
        for timeout in (True, float('inf'), 0, 61):
            with self.assertRaises(MemoryError):
                HmemClient(self.root, timeout=timeout)
