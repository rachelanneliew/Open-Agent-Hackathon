"""Real disposable PostgreSQL + pinned H-MEM, explicitly scripted test model."""
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from agent.hmem_client import HmemClient
from agent.memory_service import DisputeMemory, CommittedSummary, source_reference
from app.investigator import Investigator
from app.reviewer import Reviewer
from app.journal import FileJournal
from app.memory_workflow import retry_memory
from app.orchestrator import Budgets, Controller
import test_end_to_end as fixture
from test_orchestrator import ScriptedClient, ScriptedReviewerClient


@unittest.skipUnless(os.environ.get('DISPUTE_ACTION_TESTS') == '1' and os.environ.get('DISPUTE_HMEM_TESTS') == '1',
                     'NOT RUN: requires DISPUTE_ACTION_TESTS=1 and DISPUTE_HMEM_TESTS=1')
class MemoryDatabaseTests(unittest.TestCase):
    docker = classmethod(fixture.FreshDatabaseTests.docker.__func__)
    sql = classmethod(fixture.FreshDatabaseTests.sql.__func__)
    cleanup = classmethod(fixture.FreshDatabaseTests.cleanup.__func__)
    setUpClass = classmethod(fixture.FreshDatabaseTests.setUpClass.__func__)
    connect = fixture.FreshDatabaseTests.connect
    value = fixture.FreshDatabaseTests.value
    source_write = fixture.FreshDatabaseTests.source_write
    tearDown = fixture.FreshDatabaseTests.tearDown
    snapshot = fixture.FreshDatabaseTests.snapshot

    def setUp(self):
        fixture.FreshDatabaseTests.setUp(self)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.controller.memory_factory = lambda seconds: DisputeMemory(HmemClient(self.root, timeout=seconds))

    def test_later_investigation_recalls_after_fresh_controller_and_node_processes(self):
        first = self.controller.run('DP-0014')
        self.assertTrue(first.persisted, first.to_dict())
        self.assertEqual(first.events[-1]['status'], 'stored')
        new_client = ScriptedClient()
        second_controller = Controller(investigator=Investigator(new_client), reviewer=Reviewer(ScriptedReviewerClient()), read_snapshot=self.snapshot,
            commit=self.controller.commit, journal=FileJournal(self.root / 'new-runs'), mode='fault_injection',
            memory_factory=lambda seconds: DisputeMemory(HmemClient(self.root, timeout=seconds)))
        second = second_controller.run('DP-0017')
        self.assertTrue(second.persisted, second.to_dict())
        history = new_client.calls[0]['verified_advisory_history_untrusted']
        self.assertEqual([r['decision_id'] for r in history['records']], [first.state.commit_result.decision_id])
        self.assertEqual(len(HmemClient(self.root).list(customer_id='CUST-008')), 2)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 2)

    def test_memory_failure_then_source_verified_retry_never_reexecutes_action(self):
        factory = self.controller.memory_factory
        bad = Mock()
        bad.recall.return_value = ()
        bad.save.side_effect = OSError('Injected storage failure')
        self.controller.memory_factory = lambda seconds: bad
        first = self.controller.run('DP-0014')
        self.assertTrue(first.persisted)
        self.assertEqual(first.events[-1]['status'], 'failed')
        trace = Path(first.recovery_request).with_suffix('').with_suffix('.trace.json')
        with patch('app.action_service.commit_simulated_decision', side_effect=AssertionError('No action retry')):
            saved = retry_memory(trace, read_snapshot=self.snapshot, memory_factory=factory, budgets=Budgets())
            reused = retry_memory(trace, read_snapshot=self.snapshot, memory_factory=factory, budgets=Budgets())
        self.assertEqual((saved['memory_save']['status'], reused['memory_save']['status']), ('stored', 'reused'))
        self.assertEqual(saved['decision_id'], first.state.commit_result.decision_id)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)
        self.assertEqual(len(HmemClient(self.root).list(customer_id='CUST-008')), 1)

    def test_false_memory_has_no_binding_effect_and_real_receipt_is_required(self):
        first = self.controller.run('DP-0014')
        from app.journal import load_request
        item = CommittedSummary.from_commit(load_request(first.recovery_request).context, first.state.commit_result)
        fake = replace(item, decision_id=(ident := str(uuid4())), source_reference=source_reference(ident))
        self.assertEqual(DisputeMemory(HmemClient(self.root)).save(fake).status, 'stored')
        second = self.controller.run('DP-0017')
        self.assertTrue(second.persisted, second.to_dict())
        ignored = [e.get('code') for e in second.events if e['kind'] == 'memory_ignored']
        self.assertIn('missing_source_decision', ignored)
        records = self.client.calls[-1]['verified_advisory_history_untrusted']['records']
        self.assertEqual([r['decision_id'] for r in records], [item.decision_id])

    def test_memory_unavailable_and_stale_source_still_refuses_action(self):
        bad = Mock()
        bad.recall.side_effect = OSError('Memory offline')
        self.controller.memory_factory = lambda seconds: bad
        def change(obj, _):
            self.source_write("UPDATE public.disputes SET dispute_status=dispute_status WHERE dispute_id='DP-0014'")
            return obj
        self.client.scripts = [change]
        result = self.controller.run('DP-0014')
        self.assertFalse(result.persisted)
        self.assertEqual(result.state.commit_result.message, 'source_revision_stale')
        bad.save.assert_not_called()
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 0)
