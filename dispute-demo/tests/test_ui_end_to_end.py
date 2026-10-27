"""UI operation layer with real disposable PostgreSQL and a scripted model."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4

from app.ui_jobs import Jobs
import test_end_to_end as workflow
import test_action_service as storage


@unittest.skipUnless(os.environ.get('DISPUTE_ACTION_TESTS') == '1',
                     'NOT RUN: UI/real PostgreSQL requires DISPUTE_ACTION_TESTS=1')
class UiDatabaseTests(unittest.TestCase):
    docker = classmethod(storage.ActionServiceTests.docker.__func__)
    sql = classmethod(storage.ActionServiceTests.sql.__func__)
    cleanup = classmethod(storage.ActionServiceTests.cleanup.__func__)
    connect = storage.ActionServiceTests.connect
    value = storage.ActionServiceTests.value
    source_write = storage.ActionServiceTests.source_write
    tearDown = storage.ActionServiceTests.tearDown
    snapshot = workflow.FreshDatabaseTests.snapshot

    @classmethod
    def setUpClass(cls):
        workflow.FreshDatabaseTests.setUpClass.__func__(cls)

    def setUp(self):
        workflow.FreshDatabaseTests.setUp(self)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.ui_directory = Path(temporary.name)
        self.journal_directory = self.controller.journal.directory
        self.jobs = self.open_jobs()
        self.addCleanup(lambda:self.jobs.close())

    def open_jobs(self):
        def factory(journal):
            self.controller.journal = journal
            return self.controller
        return Jobs(self.ui_directory, self.journal_directory,
            controller_factory=factory, memory_retry=lambda _:self.fail('Unexpected memory retry'))

    def operation(self, did='DP-0014', kind='investigate', run_id=None):
        return dict(operation_id=str(uuid4()), dispute_id=did, kind=kind, run_id=run_id)

    def finish(self, payload):
        result = self.jobs.submit(payload)
        for thread in self.jobs.threads:
            thread.join(20)
            self.assertFalse(thread.is_alive())
        return self.jobs.get(result['operation_id'])

    def test_duplicate_click_restart_and_exact_recovery_keep_one_credit(self):
        payload = self.operation()
        with ThreadPoolExecutor(6) as pool:
            results = list(pool.map(lambda _:self.jobs.submit(payload), range(6)))
        result = self.finish(payload)
        self.assertEqual({r['operation_id'] for r in results}, {payload['operation_id']})
        self.assertTrue(result['result']['persisted'])
        decision = result['result']['state']['commit_result']['decision_id']
        self.jobs.close()
        self.jobs = self.open_jobs()
        self.assertEqual(self.jobs.submit(payload), result)
        recovered = self.finish(self.operation(kind='recover',run_id=result['run_id']))
        self.assertEqual(recovered['result']['state']['commit_result']['status'], 'reused')
        self.assertEqual(recovered['result']['state']['commit_result']['decision_id'],decision)
        rerun = self.finish(self.operation())
        self.assertFalse(rerun['result']['persisted'])
        self.assertEqual(rerun['result']['state']['commit_result']['message'],'effective_credit_already_exists')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'),1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'),1)

    def test_four_outcomes_and_only_committed_review_queued(self):
        for did, outcome in [('DP-0014','provisional_credit'),('DP-0020','request_evidence'),('DP-0029','decline'),('DP-0008','human_review')]:
            result = self.finish(self.operation(did))['result']
            self.assertTrue(result['persisted'],result)
            self.assertEqual(result['state']['commit_result']['recommendation']['outcome'],outcome)
            self.assertEqual(result['mode'],'fault_injection')
        self.assertEqual(self.value('SELECT count(*) FROM public.dispute_pending_reviews'),1)
        self.assertEqual(self.value('SELECT dispute_id FROM public.dispute_pending_reviews'),'DP-0008')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'),1)

    def test_failed_commit_is_not_reported_as_a_persisted_review(self):
        def race(obj, _):
            self.source_write("UPDATE public.disputes SET dispute_status=dispute_status WHERE dispute_id='DP-0008'")
            return obj
        self.client.scripts = [race]
        result = self.finish(self.operation('DP-0008'))['result']
        self.assertFalse(result['persisted'])
        self.assertEqual(result['state']['commit_result']['status'],'rejected')
        self.assertEqual(self.value('SELECT count(*) FROM public.dispute_pending_reviews'),0)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'),0)
