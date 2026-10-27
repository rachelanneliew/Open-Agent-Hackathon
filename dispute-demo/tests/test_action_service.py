"""T05 real Psycopg/PostgreSQL gate; only this suite's disposable DB is mutated.

DISPUTE_ACTION_TESTS=1 requires requirements-actions.txt, Docker and the existing
postgres:16-alpine image. No shared config or credentials are read. Faults are
explicit injections around real commits, triggers and independent connections.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
import os
from pathlib import Path
import subprocess
from threading import Barrier, Event
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from app import action_service as actions
from app.action_service import CommitRequest, commit_simulated_decision
from app.critic import policy_rationale, review_proposal
from app.policy_engine import evaluate_policy
from app.schemas import (AgentProposal, CommitResult, ContractError, CriticVerdict,
                         ExecutionStatus, Outcome, Recommendation)
from app.tools import context_from_rows
from integration import get_dispute_context as source

ROOT = Path(__file__).resolve().parents[1]


def proposal_for(context):
    policy = evaluate_policy(context)
    proposal = AgentProposal(proposal_id=str(uuid4()), run_id=str(uuid4()), reference=context.reference,
        recommendation=Recommendation(outcome=policy.allowed_outcomes[0], currency=policy.currency,
                                      amount_minor=policy.credit_limit_minor),
        rationale=policy_rationale(policy),
        evidence_ids=tuple(sorted({eid for c in policy.rule_checks for eid in c.evidence_ids})),
        policy_rule_ids=tuple(c.policy_rule_id for c in policy.rule_checks if c.status != 'not_evaluated'),
        missing_evidence=policy.missing_evidence)
    return CommitRequest(run_id=proposal.run_id, idempotency_key=str(uuid4()), context=context,
        policy=policy, proposal=proposal, critic=review_proposal(context, policy, proposal))


class ActionBoundaryTests(unittest.TestCase):
    def test_malformed_request_does_not_connect(self):
        with patch.object(actions, '_connect', side_effect=AssertionError('Unexpected I/O')):
            for value in ({}, None, 'credit'):
                with self.assertRaises(ContractError):
                    commit_simulated_decision(value)


class ConnectionProxy:
    """Fault injection only; all statements and transaction effects remain real."""
    def __init__(self, connection, *, lost_ack=False, bad_close=False):
        self.connection, self.lost_ack, self.bad_close = connection, lost_ack, bad_close

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def commit(self):
        self.connection.commit()
        if self.lost_ack:
            raise OSError('Injected lost acknowledgement')

    def close(self):
        self.connection.close()
        if self.bad_close:
            raise OSError('Injected close failure')


@unittest.skipUnless(os.environ.get('DISPUTE_ACTION_TESTS') == '1',
                     'NOT RUN: opt in to real PostgreSQL with DISPUTE_ACTION_TESTS=1')
class ActionServiceTests(unittest.TestCase):
    @classmethod
    def docker(cls, *args, **kwargs):
        return subprocess.run(['docker', *args], text=True, capture_output=True, timeout=45, **kwargs)

    @classmethod
    def sql(cls, query, database='source_template'):
        result = cls.docker('exec', '-i', cls.container, 'psql', '-XqAt', '-v', 'ON_ERROR_STOP=1',
                           '-U', 'action_admin', '-d', database, input=query)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    @classmethod
    def setUpClass(cls):
        import psycopg
        from integration.load_data import make_sql
        cls.psycopg = psycopg
        name = 'dispute-t05-test-' + uuid4().hex
        result = cls.docker('run', '--detach', '--pull', 'never', '--name', name,
            '--label', 'dispute-purpose=t05-isolated-test', '-p', '127.0.0.1::5432',
            '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', '-e', 'POSTGRES_USER=action_admin',
            '-e', 'POSTGRES_DB=source_template', 'postgres:16-alpine')
        if result.returncode:
            raise AssertionError('Cannot start isolated PostgreSQL: ' + result.stderr)
        cls.container = result.stdout.strip()
        cls.addClassCleanup(cls.cleanup)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if cls.docker('exec', cls.container, 'pg_isready', '-h', '127.0.0.1',
                          '-U', 'action_admin', '-d', 'source_template').returncode == 0:
                break
            time.sleep(.2)
        else:
            raise AssertionError('Isolated PostgreSQL not ready')
        cls.port = int(cls.docker('port', cls.container, '5432').stdout.strip().rsplit(':', 1)[1])
        cls.sql('CREATE ROLE dispute_reader NOLOGIN; CREATE ROLE t05_action LOGIN; CREATE ROLE t05_source LOGIN;')
        cls.sql(make_sql('full'))
        cls.sql((ROOT / 'db/migrations/001_decision_storage.sql').read_text())
        cls.sql('GRANT dispute_action_writer TO t05_action; GRANT dispute_source_writer TO t05_source;')

    @classmethod
    def cleanup(cls):
        result = cls.docker('rm', '-f', '-v', cls.container)
        if result.returncode:
            raise AssertionError('Test container cleanup failed: ' + result.stderr)

    def setUp(self):
        self.database = 't05_' + uuid4().hex
        self.sql(f'CREATE DATABASE {self.database} TEMPLATE source_template;', 'postgres')

    def tearDown(self):
        self.sql(f'DROP DATABASE {self.database};', 'postgres')

    def connect(self, user='t05_action', **kwargs):
        return self.psycopg.connect(host='127.0.0.1', port=self.port, dbname=self.database,
                                   user=user, connect_timeout=5, **kwargs)

    def value(self, query, params=()):
        with self.connect('action_admin') as conn:
            return conn.execute(query, params).fetchone()[0]

    def source_write(self, query, params=()):
        with self.connect('t05_source') as conn:
            conn.execute(query, params)

    def request(self, did='DP-0014', *, cutoff=None):
        # Independent test-only snapshot assembly over real DB source rows.
        # Not the service's rereader and never a runtime investigation shortcut.
        with self.connect() as conn:
            revision = conn.execute('SELECT dispute_control.lock_source_revision()').fetchone()[0]
            now = conn.execute('SELECT clock_timestamp()').fetchone()[0]
            def rows(table, columns, where, params):
                return [dict(zip(columns, r)) for r in conn.execute(
                    f'SELECT {", ".join(columns)} FROM public.{table} WHERE {where}', params).fetchall()]
            case = rows('disputes', source.DISPUTE_COLUMNS, 'dispute_id=%s', (did,))[0]
            case['evaluation_at'] = (cutoff or now).isoformat().replace('+00:00', 'Z')
            ids = (case['transaction_id'], case['related_transaction_id'])
            raw = dict(dispute=case,
                transactions=rows('transactions', source.TRANSACTION_COLUMNS, 'transaction_id IN (%s,%s)', ids),
                settlements=rows('settlements', source.SETTLEMENT_COLUMNS, 'transaction_id IN (%s,%s)', ids),
                evidence=rows('evidence', source.EVIDENCE_COLUMNS, 'dispute_id=%s', (did,)),
                policy_rules=rows('policy_rules', source.POLICY_COLUMNS, 'true', ()))
            for e in raw['evidence']:
                doc = conn.execute('SELECT content FROM public.evidence_documents WHERE evidence_id=%s',
                                   (e['evidence_id'],)).fetchone()
                e['content'] = doc[0] if doc else None
            context = context_from_rows(raw, did, captured_at=max(now, cutoff or now),
                                        source_channel='offline_test').data
            context = replace(context, reference=replace(context.reference, source_revision=revision))
        return proposal_for(context)

    def commit(self, request, **kwargs):
        result = commit_simulated_decision(request, connect=kwargs.get('connect', self.connect))
        self.assertEqual(CommitResult.from_dict(result.to_dict()), result)
        return result

    def empty(self):
        for table in ('investigations', 'decisions', 'simulated_credits', 'credit_reservations',
                      'audit_events', 'review_queue'):
            self.assertEqual(self.value(f'SELECT count(*) FROM dispute_actions.{table}'), 0, table)

    def test_all_four_outcomes_and_source_status_are_persisted_correctly(self):
        for did, outcome in (('DP-0014', Outcome.PROVISIONAL_CREDIT), ('DP-0020', Outcome.REQUEST_EVIDENCE),
                             ('DP-0029', Outcome.DECLINE), ('DP-0008', Outcome.HUMAN_REVIEW)):
            req = self.request(did)
            result = self.commit(req)
            self.assertEqual(result.status, ExecutionStatus.COMMITTED, result)
            self.assertEqual(result.recommendation.outcome, outcome)
            self.assertEqual(result.reference, req.context.reference)
            self.assertEqual(result.recommendation.amount_minor, 6000 if outcome is Outcome.PROVISIONAL_CREDIT else None)
        for table, count in (('decisions', 4), ('investigations', 4), ('audit_events', 4),
                             ('simulated_credits', 1), ('pending_reviews', 1)):
            self.assertEqual(self.value(f'SELECT count(*) FROM dispute_actions.{table}'), count)
        self.assertEqual(self.value("SELECT count(*) FROM public.disputes WHERE dispute_status <> 'open'"), 0)

    def test_identical_retry_reuses_original_even_after_source_changes(self):
        req = self.request()
        first = self.commit(req)
        self.source_write("UPDATE public.settlements SET amount_minor=5000 WHERE settlement_id='ST-0022'")
        reused = self.commit(CommitRequest.from_dict(req.to_dict()))
        self.assertEqual(reused.status, ExecutionStatus.REUSED, reused)
        self.assertEqual(replace(reused, status=first.status, message=first.message), first)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.audit_events'), 1)

    def test_same_key_changed_payload_rejected(self):
        req = self.request()
        self.assertEqual(self.commit(req).status, ExecutionStatus.COMMITTED)
        for changed in (replace(req, run_id=str(uuid4())),
                        replace(req, critic=replace(req.critic, feedback='changed')),
                        replace(req, proposal=replace(req.proposal, rationale='changed')),
                        replace(req, context=replace(req.context, captured_at=req.context.captured_at+timedelta(microseconds=1)))):
            self.assertEqual(self.commit(changed).message, 'idempotency_payload_conflict')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)

    def test_new_key_with_fresh_inputs_cannot_credit_again(self):
        self.assertEqual(self.commit(self.request()).status, ExecutionStatus.COMMITTED)
        self.assertEqual(self.commit(self.request()).message, 'effective_credit_already_exists')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_linked_charge_reservation_blocks_another_dispute(self):
        self.assertEqual(self.commit(self.request('DP-0003')).status, ExecutionStatus.COMMITTED)
        self.source_write("INSERT INTO public.disputes SELECT 'DP-0098', related_transaction_id, "
            "transaction_id, reason_code, claimed_amount_minor, currency, customer_statement, "
            "opened_at, evaluation_at, dispute_status FROM public.disputes WHERE dispute_id='DP-0003'")
        # No new documentary support is fabricated. Copy the genuine source
        # receipt into this isolated case with its new identity/primary IDs.
        self.source_write("INSERT INTO public.evidence SELECT 'EV-9999','DP-0098',NULL,evidence_type, "
            "source_type,'evidence_documents/EV-9999.txt',event_at,available_at,integrity_status "
            "FROM public.evidence WHERE dispute_id='DP-0003' AND evidence_type='receipt'")
        old = self.value("SELECT doc.content FROM public.evidence_documents doc JOIN public.evidence e USING(evidence_id) "
                         "WHERE e.dispute_id='DP-0003' AND e.evidence_type='receipt'")
        companion = self.value("SELECT transaction_id FROM public.disputes WHERE dispute_id='DP-0098'")
        eid = self.value("SELECT evidence_id FROM public.evidence WHERE dispute_id='DP-0003' AND evidence_type='receipt'")
        new = old.replace(eid, 'EV-9999').replace('DP-0003', 'DP-0098').replace('TX-0003', companion)
        self.source_write("INSERT INTO public.evidence_documents VALUES ('EV-9999',%s)", (new,))
        request = self.request('DP-0098')
        self.assertEqual(request.proposal.recommendation.outcome, Outcome.PROVISIONAL_CREDIT)
        self.assertEqual(self.commit(request).message, 'effective_credit_already_exists')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_duplicate_run_identity_rolls_back_new_investigation(self):
        first = self.request()
        self.assertEqual(self.commit(first).status, ExecutionStatus.COMMITTED)
        request = self.request('DP-0020')
        request = replace(request, run_id=first.run_id, proposal=replace(request.proposal, run_id=first.run_id))
        self.assertEqual(self.commit(request).message, 'storage_constraint_rejected')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.investigations'), 1)

    def test_commit_requires_synchronous_durability_even_if_session_default_is_off(self):
        self.sql("CREATE FUNCTION public.check_test_sync() RETURNS trigger LANGUAGE plpgsql AS $$ "
                 "BEGIN IF current_setting('synchronous_commit') <> 'on' THEN RAISE EXCEPTION 'not durable'; "
                 "END IF; RETURN NEW; END $$; CREATE TRIGGER test_sync BEFORE INSERT ON dispute_actions.decisions "
                 "FOR EACH ROW EXECUTE FUNCTION public.check_test_sync();", self.database)
        result = self.commit(self.request(), connect=lambda: self.connect(options='-c synchronous_commit=off'))
        self.assertEqual(result.status, ExecutionStatus.COMMITTED)

    def test_post_cutoff_evidence_and_unavailable_text_never_enable_credit(self):
        cutoff = self.value("SELECT evaluation_at::timestamptz FROM public.disputes WHERE dispute_id='DP-0019'")
        request = self.request('DP-0019', cutoff=cutoff)
        self.assertEqual(self.commit(request).message, 'post_cutoff_source_requires_new_evaluation')
        self.source_write("DELETE FROM public.evidence_documents WHERE evidence_id='EV-0028'")
        request = self.request()
        self.assertEqual(request.proposal.recommendation.outcome, Outcome.REQUEST_EVIDENCE)
        self.assertEqual(self.commit(request).status, ExecutionStatus.COMMITTED)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 0)

    def test_concurrent_identical_requests_reuse_one_credit(self):
        req = self.request()
        barrier, pids = Barrier(2), []
        def run():
            conn = self.connect()
            pids.append(conn.info.backend_pid)
            barrier.wait(timeout=5)
            return self.commit(req, connect=lambda: conn)
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        self.assertEqual(len(set(pids)), 2)
        self.assertEqual({r.status for r in results}, {ExecutionStatus.COMMITTED, ExecutionStatus.REUSED})
        self.assertEqual(results[0].decision_id, results[1].decision_id)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_concurrent_different_requests_cannot_both_credit(self):
        requests, barrier = [self.request(), self.request()], Barrier(2)
        def run(req):
            barrier.wait(timeout=5)
            return self.commit(req)
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(run, requests))
        self.assertEqual({r.status for r in results}, {ExecutionStatus.COMMITTED, ExecutionStatus.REJECTED})
        self.assertIn('source_revision_stale', {r.message for r in results})
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.investigations'), 1)

    def test_unknown_and_stale_revisions_leave_no_records(self):
        req = self.request()
        unknown = proposal_for(replace(req.context, reference=replace(req.context.reference, source_revision=None)))
        self.assertEqual(self.commit(unknown).message, 'source_revision_unknown')
        self.source_write('UPDATE public.policy_rules SET explanation=explanation')
        self.assertEqual(self.commit(req).message, 'source_revision_stale')
        self.empty()

    def test_changed_source_refund_text_policy_status_each_invalidates_request(self):
        queries = ["UPDATE public.settlements SET amount_minor=5000 WHERE settlement_id='ST-0022'",
                   "UPDATE public.evidence_documents SET content=content || ' changed' WHERE evidence_id='EV-0028'",
                   "UPDATE public.policy_rules SET parameters_json='{}' WHERE policy_rule_id='v2-FILING_WINDOW'",
                   "UPDATE public.disputes SET dispute_status='closed' WHERE dispute_id='DP-0014'"]
        for query in queries:
            req = self.request()
            self.source_write(query)
            self.assertEqual(self.commit(req).message, 'source_revision_stale')
        self.empty()

    def test_forged_current_revision_does_not_validate_old_facts(self):
        req = self.request()
        self.source_write("UPDATE public.settlements SET amount_minor=5000 WHERE settlement_id='ST-0022'")
        revision = self.value('SELECT revision FROM dispute_control.source_revision')
        forged = proposal_for(replace(req.context, reference=replace(req.context.reference, source_revision=revision)))
        self.assertEqual(self.commit(forged).message, 'authoritative_context_mismatch')
        self.empty()

    def test_post_cutoff_refund_is_not_hidden_by_latest_revision(self):
        req = self.request()
        late = req.context.reference.evaluation_at + timedelta(microseconds=1)
        self.source_write("INSERT INTO public.settlements VALUES ('ST-9999','TX-0014','refund',6000,'SGD','completed',%s,%s)",
                          (late.isoformat().replace('+00:00','Z'),)*2)
        # Latest revision and a separately reconstructed historical context still
        # cannot hide the later authoritative row from the commit-time reread.
        old = self.request(cutoff=req.context.reference.evaluation_at)
        self.assertEqual(self.commit(old).message, 'post_cutoff_source_requires_new_evaluation')
        self.empty()

    def test_invalid_binding_policy_amount_and_forged_accepted_critic(self):
        req = self.request()
        bad_amount = replace(req.proposal, recommendation=replace(req.proposal.recommendation, amount_minor=6001))
        mutations = [replace(req, run_id=str(uuid4())),
                     replace(req, critic=replace(req.critic, proposal_id=str(uuid4()))),
                     replace(req, proposal=replace(req.proposal, reference=replace(req.proposal.reference, snapshot_id=str(uuid4())))),
                     replace(req, policy=replace(req.policy, credit_limit_minor=9999)),
                     replace(req, proposal=bad_amount),
                     replace(req, critic=replace(req.critic, feedback='Forged acceptance'))]
        for mutation in mutations:
            self.assertEqual(self.commit(mutation).status, ExecutionStatus.REJECTED)
        self.empty()

    def test_mandatory_review_cannot_credit_with_forged_approval(self):
        req = self.request('DP-0008')
        proposal = replace(req.proposal, recommendation=Recommendation(outcome=Outcome.PROVISIONAL_CREDIT,
                                                                       currency='SGD', amount_minor=25000))
        self.assertEqual(self.commit(replace(req, proposal=proposal)).message, 'current_critic_rejected')
        self.empty()
        self.assertEqual(self.commit(req).status, ExecutionStatus.COMMITTED)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.pending_reviews'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 0)

    def test_noncredit_new_evidence_rereview_and_review_supersession(self):
        text = self.value("SELECT content FROM public.evidence_documents WHERE evidence_id='EV-0028'")
        self.source_write("DELETE FROM public.evidence_documents WHERE evidence_id='EV-0028'")
        first = self.commit(self.request())
        self.assertEqual(first.recommendation.outcome, Outcome.REQUEST_EVIDENCE)
        self.source_write("INSERT INTO public.evidence_documents VALUES ('EV-0028',%s)", (text,))
        second = self.commit(self.request())
        self.assertEqual(second.recommendation.outcome, Outcome.PROVISIONAL_CREDIT)
        self.assertEqual(self.value('SELECT previous_decision_id::text FROM dispute_actions.current_decisions'), first.decision_id)
        self.source_write("UPDATE public.evidence_documents SET content=content || ' uncertain' WHERE evidence_id='EV-0027'")
        third = self.commit(self.request())
        self.assertEqual(third.recommendation.outcome, Outcome.HUMAN_REVIEW)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.pending_reviews'), 1)
        self.source_write("UPDATE public.settlements SET amount_minor=10000 WHERE settlement_id='ST-0022'")
        fourth = self.commit(self.request())
        self.assertEqual(fourth.recommendation.outcome, Outcome.DECLINE)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.pending_reviews'), 0)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.review_queue'), 1)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_database_trigger_failure_rolls_back_every_record_and_revision(self):
        req = self.request()
        self.sql("CREATE FUNCTION public.test_fail_audit() RETURNS trigger LANGUAGE plpgsql AS $$ "
                 "BEGIN RAISE EXCEPTION 'injected audit failure'; END $$; "
                 "CREATE TRIGGER test_failure BEFORE INSERT ON dispute_actions.audit_events "
                 "FOR EACH ROW EXECUTE FUNCTION public.test_fail_audit();", self.database)
        self.assertEqual(self.commit(req).status, ExecutionStatus.REJECTED)
        self.empty()
        self.assertEqual(self.value('SELECT revision FROM dispute_control.source_revision'), req.context.reference.source_revision)

    def test_lost_ack_recovers_original_commit_without_second_effect(self):
        req = self.request()
        result = self.commit(req, connect=lambda: ConnectionProxy(self.connect(), lost_ack=True))
        self.assertEqual(result.status, ExecutionStatus.FAILED)
        self.assertIsNone(result.decision_id)
        self.assertIsNone(result.simulated_credit_id)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), 1)
        self.assertEqual(self.commit(req).status, ExecutionStatus.REUSED)
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), 1)

    def test_close_error_does_not_hide_acknowledged_commit(self):
        result = self.commit(self.request(), connect=lambda: ConnectionProxy(self.connect(), bad_close=True))
        self.assertEqual(result.status, ExecutionStatus.COMMITTED)

    def test_unavailable_database_does_not_claim_queued_review_or_leak_error(self):
        def unavailable():
            raise OSError('password=DO_NOT_EXPOSE')
        result = self.commit(self.request('DP-0008'), connect=unavailable)
        self.assertEqual(result.status, ExecutionStatus.UNAVAILABLE)
        self.assertNotIn('DO_NOT_EXPOSE', str(result.to_dict()))
        self.assertIsNone(result.decision_id)
        self.empty()

    def test_runtime_admin_source_writer_and_autocommit_are_refused(self):
        req = self.request()
        for factory in (lambda: self.connect('action_admin'), lambda: self.connect('t05_source'),
                        lambda: self.connect(autocommit=True)):
            self.assertEqual(self.commit(req, connect=factory).status, ExecutionStatus.UNAVAILABLE)
        self.empty()

    def test_nonopen_status_and_future_snapshots_rejected(self):
        req = self.request(cutoff=self.request().context.captured_at + timedelta(days=1))
        self.assertEqual(self.commit(req).message, 'future_snapshot')
        self.source_write("UPDATE public.disputes SET dispute_status='closed' WHERE dispute_id='DP-0014'")
        self.assertEqual(self.commit(self.request()).message, 'unsupported_dispute_status')
        self.empty()

    def test_source_writer_cannot_change_facts_during_validation(self):
        req, entered, release = self.request(), Event(), Event()
        real_evaluate = actions.evaluate_policy
        def paused(context):
            entered.set()
            if not release.wait(5):
                raise AssertionError('Test did not release validation')
            return real_evaluate(context)
        with patch.object(actions, 'evaluate_policy', side_effect=paused), ThreadPoolExecutor(1) as pool:
            future = pool.submit(self.commit, req)
            try:
                self.assertTrue(entered.wait(5))
                with self.connect('t05_source') as writer:
                    writer.execute("SET LOCAL lock_timeout='250ms'")
                    with self.assertRaises(self.psycopg.errors.LockNotAvailable):
                        writer.execute("UPDATE public.settlements SET amount_minor=5000 WHERE settlement_id='ST-0022'")
            finally:
                release.set()
            self.assertEqual(future.result(timeout=10).status, ExecutionStatus.COMMITTED)
        self.assertEqual(self.value("SELECT amount_minor FROM public.settlements WHERE settlement_id='ST-0022'"), 4000)

    def test_waiting_action_reads_revision_after_source_writer_commits(self):
        req = self.request()
        with self.connect('t05_source') as writer, ThreadPoolExecutor(1) as pool:
            writer.execute("UPDATE public.settlements SET amount_minor=5000 WHERE settlement_id='ST-0022'")
            future = pool.submit(self.commit, req)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if self.value("SELECT count(*) FROM pg_stat_activity WHERE datname=%s AND usename='t05_action' AND wait_event_type='Lock'", (self.database,)):
                    break
                time.sleep(.02)
            else:
                self.fail('Action did not wait on source guard')
            writer.commit()
            self.assertEqual(future.result(timeout=10).message, 'source_revision_stale')
        self.empty()


if __name__ == '__main__':
    unittest.main()
