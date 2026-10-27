"""Real PostgreSQL 16 tests in a disposable, unnetworked Docker container.

Opt in with DISPUTE_STORAGE_TESTS=1. Uses the already installed postgres:16-alpine
image (--pull never), no shared container, published port, password or source DB.
The generated source files are test inputs; expected outcomes are never loaded
into a runtime action path. No action service is implemented by this test helper.
"""
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
from uuid import uuid4

from integration.load_data import make_sql

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / 'db/migrations/001_decision_storage.sql'
TABLES = ('transactions', 'settlements', 'disputes', 'evidence', 'evidence_documents', 'policy_rules')


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(os.environ.get('DISPUTE_STORAGE_TESTS') == '1',
                     'NOT RUN: opt in to isolated PostgreSQL with DISPUTE_STORAGE_TESTS=1')
class DecisionStorageTests(unittest.TestCase):
    container = None

    @classmethod
    def docker(cls, *args, **kwargs):
        return subprocess.run(['docker', *args], text=True, capture_output=True, timeout=45, **kwargs)

    @classmethod
    def sql(cls, query, *, database=None, role=None, check=True):
        login = {'dispute_source_writer': 't04_source', 'dispute_action_writer': 't04_action',
                 'dispute_reader': 't04_reader'}.get(role, 'storage_admin')
        result = cls.docker('exec', '-i', cls.container, 'psql', '-X', '-qAt',
                            '-v', 'ON_ERROR_STOP=1', '-U', login,
                            '-d', database or cls.database,
                            input=(f'SET ROLE {role};\n' if role else '') + query)
        if check and result.returncode:
            raise AssertionError(result.stderr)
        return result

    @classmethod
    def wait_ready(cls):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            # The image's temporary bootstrap server listens on a socket only.
            # Wait for TCP so we never race initial database creation/shutdown.
            if cls.docker('exec', cls.container, 'pg_isready', '-h', '127.0.0.1', '-U', 'storage_admin', '-d', 'source_template').returncode == 0:
                return
            time.sleep(.2)
        raise AssertionError('Isolated PostgreSQL did not become ready')

    @classmethod
    def setUpClass(cls):
        name = 'dispute-t04-test-' + uuid4().hex
        result = cls.docker('run', '--detach', '--pull', 'never', '--network', 'none',
                            '--name', name, '--label', 'dispute-purpose=t04-isolated-test',
                            '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', '-e', 'POSTGRES_USER=storage_admin',
                            '-e', 'POSTGRES_DB=source_template', 'postgres:16-alpine')
        if result.returncode:
            raise AssertionError('Cannot start isolated PostgreSQL: ' + result.stderr)
        cls.container = result.stdout.strip()
        # Cleanup only the exact container we just created, including its own
        # anonymous volume. Existing project/Zetaris containers are never targeted.
        cls.addClassCleanup(cls.cleanup_container)
        cls.wait_ready()
        cls.sql('CREATE ROLE dispute_reader NOLOGIN; CREATE ROLE t04_source LOGIN; '
                'CREATE ROLE t04_action LOGIN; CREATE ROLE t04_reader LOGIN;', database='source_template')
        cls.sql(make_sql('full'), database='source_template')

    @classmethod
    def cleanup_container(cls):
        result = cls.docker('rm', '-f', '-v', cls.container)
        if result.returncode:
            raise AssertionError('Failed to clean isolated test container: ' + result.stderr)

    def setUp(self):
        self.database = 't04_' + uuid4().hex
        type(self).database = self.database
        self.sql(f'CREATE DATABASE {self.database} TEMPLATE source_template;', database='postgres')
        self.sql(MIGRATION.read_text())
        self.sql('GRANT dispute_source_writer TO t04_source; GRANT dispute_action_writer TO t04_action; '
                 'GRANT dispute_reader TO t04_reader;')

    def tearDown(self):
        self.sql(f'DROP DATABASE {self.database};', database='postgres')

    def value(self, query, **kwargs):
        return self.sql(query, **kwargs).stdout.strip()

    def revision(self):
        return int(self.value('SELECT revision FROM dispute_control.source_revision'))

    def denied(self, query, message=None, role='dispute_action_writer'):
        before = self.revision()
        result = self.sql(query, role=role, check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.revision(), before, 'Failed statement/transaction must roll back revision')

    def record(self, outcome='human_review', *, dispute='DP-0014', transaction='TX-0014',
               previous=None, cutoff='2026-10-20T00:00:00Z', source_revision=None,
               key=None, amount=None, change=None):
        """Craft storage rows only; deliberately not a policy/action implementation."""
        ids = {name: str(uuid4()) for name in ('run', 'proposal', 'snapshot', 'decision')}
        ids['key'] = key or str(uuid4())
        rev = self.revision() if source_revision is None else source_revision
        investigation = dict(run_id=ids['run'], proposal_id=ids['proposal'], dispute_id=dispute,
                             transaction_id=transaction, snapshot_id=ids['snapshot'], evaluation_at=cutoff,
                             policy_version='v2', source_revision=rev,
                             context_payload={'test': 'storage constraints only'},
                             proposal_payload={'proposal_id': ids['proposal']}, critic_payload={'test': 'not a real critique'})
        decision = dict(decision_id=ids['decision'], run_id=ids['run'], dispute_id=dispute,
                        transaction_id=transaction, idempotency_key=ids['key'],
                        request_payload={'proposal_id': ids['proposal'], 'reference_revision': rev},
                        previous_decision_id=previous, outcome=outcome, currency='SGD',
                        amount_minor=6000 if outcome == 'provisional_credit' and amount is None else amount,
                        rationale='Synthetic storage test', evidence_ids=['EV-0027'],
                        policy_rule_ids=['v2-APPROVE'], missing_evidence=[{'category': 'refund_confirmation',
                            'reason': 'absent', 'policy_rule_id': 'v2-MISSING_EVIDENCE'}] if outcome == 'request_evidence' else [])
        if change:
            change(investigation, decision)
        def insert(table, row):
            return f'INSERT INTO dispute_actions.{table} ({", ".join(row)}) VALUES ({", ".join(literal(v) for v in row.values())});\n'
        return ids, 'BEGIN;\n' + insert('investigations', investigation) + insert('decisions', decision) + 'COMMIT;'

    def save(self, *args, **kwargs):
        ids, query = self.record(*args, **kwargs)
        self.sql(query, role='dispute_action_writer')
        return ids

    def test_migration_preserves_source_and_is_atomic_on_reapplication(self):
        for table in TABLES:
            sql = f'SELECT md5(string_agg(row_to_json(t)::text, CHR(10) ORDER BY row_to_json(t)::text)) FROM public.{table} t'
            self.assertEqual(self.value(sql), self.value(sql, database='source_template'))
        self.assertEqual(self.value('SELECT version FROM dispute_control.schema_migrations'), '1')
        self.assertEqual(self.revision(), 0)
        self.denied(MIGRATION.read_text(), 'already exists', role='storage_admin')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), '0')

    def test_all_four_outcomes_have_exact_sidecars_and_references(self):
        for index, outcome in enumerate(('provisional_credit', 'request_evidence', 'decline', 'human_review'), 1):
            ids = self.save(outcome, dispute=f'DP-{index:04d}', transaction=f'TX-{index:04d}')
            self.assertEqual(self.value(f"SELECT execution_status FROM dispute_actions.decisions WHERE decision_id='{ids['decision']}'"), 'committed')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.audit_events'), '4')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), '1')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.review_queue'), '1')
        self.assertEqual(self.value("SELECT count(*) FROM dispute_actions.decisions WHERE outcome <> 'provisional_credit' AND amount_minor IS NOT NULL"), '0')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions d JOIN dispute_actions.investigations i USING (run_id,dispute_id,transaction_id)'), '4')

    def test_second_credit_blocked_across_keys_and_disputes(self):
        first = self.save('provisional_credit')
        self.denied(self.record('provisional_credit', previous=first['decision'])[1], 'decisions_one_credit_per_dispute')
        self.sql("INSERT INTO public.disputes SELECT 'DP-0099', transaction_id, related_transaction_id, reason_code, claimed_amount_minor, currency, customer_statement, opened_at, evaluation_at, dispute_status FROM public.disputes WHERE dispute_id='DP-0014'", role='dispute_source_writer')
        self.denied(self.record('provisional_credit', dispute='DP-0099')[1], 'decisions_one_credit_per_primary_transaction')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), '1')

    def test_non_credit_new_evidence_rereview_and_queue_supersession(self):
        first = self.save('request_evidence')
        self.sql("UPDATE public.evidence_documents SET content = content || ' New evidence' WHERE evidence_id='EV-0028'", role='dispute_source_writer')
        second = self.save('human_review', previous=first['decision'])
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.pending_reviews'), '1')
        third = self.save('provisional_credit', previous=second['decision'])
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.pending_reviews'), '0')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.review_queue'), '1')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.audit_events'), '3')
        self.assertEqual(self.value('SELECT decision_id FROM dispute_actions.current_decisions'), third['decision'])
        # Additional non-credit audit/review is allowed after credit; never a second credit.
        self.save('human_review', previous=third['decision'])
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), '1')
        self.assertEqual(self.value("SELECT dispute_status FROM public.disputes WHERE dispute_id='DP-0014'"), 'open')

    def test_swapped_duplicate_pair_cannot_create_second_credit(self):
        self.save('provisional_credit', dispute='DP-0003', transaction='TX-0003')
        companion = self.value("SELECT related_transaction_id FROM public.disputes WHERE dispute_id='DP-0003'")
        self.sql("INSERT INTO public.disputes SELECT 'DP-0098', related_transaction_id, transaction_id, reason_code, claimed_amount_minor, currency, customer_statement, opened_at, evaluation_at, dispute_status FROM public.disputes WHERE dispute_id='DP-0003'", role='dispute_source_writer')
        self.denied(self.record('provisional_credit', dispute='DP-0098', transaction=companion)[1], 'credit_reservations_pkey')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.simulated_credits'), '1')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.credit_reservations'), '2')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.audit_events'), '1')

    def test_reader_views_expose_history_but_no_write_privileges(self):
        saved = self.save()
        self.assertEqual(self.value('SELECT decision_id FROM public.dispute_decision_history', role='dispute_reader'), saved['decision'])
        self.assertEqual(self.value('SELECT decision_id FROM public.dispute_pending_reviews', role='dispute_reader'), saved['decision'])
        self.assertEqual(int(self.value('SELECT revision FROM public.dispute_source_revision', role='dispute_reader')), self.revision())
        self.denied('UPDATE public.dispute_source_revision SET revision=0', 'permission denied', role='dispute_reader')

    def test_decline_does_not_permanently_close_dispute(self):
        first = self.save('decline')
        self.save('request_evidence', previous=first['decision'])
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), '2')

    def test_idempotency_and_proposal_identity_are_unique(self):
        first = self.save()
        self.denied(self.record(previous=first['decision'], key=first['key'])[1], 'decisions_idempotency_key_key')
        self.assertEqual(self.value(f"SELECT request_payload->>'proposal_id' FROM dispute_actions.decisions WHERE idempotency_key='{first['key']}'"), first['proposal'])
        self.denied(self.record(previous=first['decision'], change=lambda i,d: i.update(proposal_id=first['proposal']))[1], 'investigations_proposal_id_key')

    def test_chain_cannot_fork_cross_dispute_or_reuse_revision(self):
        first = self.save()
        self.denied(self.record()[1], 'decisions_first_per_dispute')
        self.denied(self.record(previous=first['decision'], source_revision=0)[1], 'later source revision')
        second = self.save('decline', previous=first['decision'])
        self.denied(self.record(previous=first['decision'])[1], 'decisions_previous_decision_id_key')
        self.denied(self.record(dispute='DP-0002', transaction='TX-0002', previous=second['decision'])[1], 'foreign key')

    def test_noncredit_amount_and_missing_requirements_rejected(self):
        for outcome in ('request_evidence', 'human_review', 'decline'):
            for amount in (0, 1):
                with self.subTest(outcome=outcome, amount=amount):
                    self.denied(self.record(outcome, amount=amount)[1], 'check constraint')
        self.denied(self.record('provisional_credit', amount=-1)[1], 'check constraint')
        self.denied(self.record('request_evidence', change=lambda i,d: d.update(missing_evidence=[]))[1], 'check constraint')

    def test_invalid_ids_revision_status_and_identity_rejected(self):
        changes = [lambda i,d: i.update(source_revision=None), lambda i,d: i.update(source_revision=-1),
                   lambda i,d: d.update(decision_id='00000000-0000-0000-0000-000000000000'),
                   lambda i,d: d.update(execution_status='reused'), lambda i,d: d.update(outcome='approve'),
                   lambda i,d: d.update(currency='usd'), lambda i,d: d.update(transaction_id='TX-0001')]
        for change in changes:
            self.denied(self.record(change=change)[1])

    def test_storage_is_append_only_and_sidecars_cannot_be_forged(self):
        self.save()
        for table in ('investigations', 'decisions', 'simulated_credits', 'review_queue', 'credit_reservations', 'audit_events'):
            for operation in (f'DELETE FROM dispute_actions.{table}', f'TRUNCATE dispute_actions.{table} CASCADE'):
                self.denied(operation, 'permission denied')
        self.denied('DELETE FROM dispute_actions.decisions', 'append-only', role='storage_admin')
        self.denied("INSERT INTO dispute_actions.review_queue(decision_id) VALUES ('" + str(uuid4()) + "')", 'permission denied')
        # Composite FK also protects against a misconfigured trusted sidecar writer.
        credit = self.save('provisional_credit', dispute='DP-0002', transaction='TX-0002')
        self.denied(f"INSERT INTO dispute_actions.review_queue(decision_id) VALUES ('{credit['decision']}')", 'foreign key', role='storage_admin')

    def test_source_writers_cannot_disable_or_bypass_guard(self):
        for role in ('dispute_source_writer', 'dispute_action_writer', 'dispute_reader'):
            for query in ('UPDATE dispute_control.source_revision SET revision=0',
                          'TRUNCATE dispute_control.source_revision',
                          'ALTER TABLE public.settlements DISABLE TRIGGER ALL',
                          "SET session_replication_role='replica'", 'SET ROLE dispute_storage_owner',
                          'DROP TABLE public.evidence_documents',
                          'CREATE TABLE public.unguarded_test(id int)'):
                with self.subTest(role=role, query=query):
                    self.denied(query, role=role)
        self.denied("UPDATE public.settlements SET amount_minor=1", 'permission denied', role='dispute_reader')
        self.denied("UPDATE public.settlements SET amount_minor=1", 'permission denied')

    def test_all_source_mutations_and_copy_advance_revision_rollback_restores(self):
        for table in TABLES:
            before = self.revision()
            # Even a no-op statement takes the guard. No write path can omit it.
            self.sql(f'DELETE FROM public.{table} WHERE false', role='dispute_source_writer')
            self.assertEqual(self.revision(), before + 1)
        before = self.revision()
        self.sql("BEGIN; UPDATE public.policy_rules SET explanation=explanation; UPDATE public.evidence_documents SET content=content; ROLLBACK;", role='dispute_source_writer')
        self.assertEqual(self.revision(), before)
        self.sql("COPY public.evidence_documents FROM STDIN WITH (FORMAT CSV);\n\\.\n", role='dispute_source_writer')
        self.assertEqual(self.revision(), before + 1)
        self.sql('TRUNCATE public.evidence_documents;', role='dispute_source_writer')
        self.assertEqual(self.revision(), before + 2)
        self.assertEqual(self.value('SELECT count(*) FROM public.evidence_documents'), '0')

    def test_initial_loader_refuses_guarded_database(self):
        self.denied(make_sql('full'), 'initial loader is disabled', role='storage_admin')
        self.denied(make_sql('probe'), 'initial loader is disabled', role='storage_admin')
        self.assertEqual(self.value('SELECT count(*) FROM public.disputes'), '40')

    def test_late_refund_is_rejected_even_with_latest_revision(self):
        self.sql("INSERT INTO public.settlements VALUES ('ST-9999','TX-0014','refund',6000,'SGD','completed','2026-10-21T00:00:00Z','2026-10-21T00:01:00Z')", role='dispute_source_writer')
        self.denied(self.record('provisional_credit')[1], 'Post-cutoff source records')
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.decisions'), '0')

    def test_late_evidence_and_future_cutoff_require_new_context(self):
        # Generated DP-0019 has late evidence excluded by its original cutoff.
        cutoff = self.value("SELECT evaluation_at FROM public.disputes WHERE dispute_id='DP-0019'")
        self.denied(self.record(dispute='DP-0019', transaction='TX-0019', cutoff=cutoff)[1], 'Post-cutoff source records')
        self.denied(self.record(cutoff='2099-01-01T00:00:00Z')[1], 'Invalid fresh evaluation cutoff')

    def test_rollback_removes_decision_sidecars_and_revision(self):
        before = self.revision()
        ids, query = self.record('provisional_credit')
        self.sql(query.replace('COMMIT;', 'ROLLBACK;'), role='dispute_action_writer')
        for table in ('investigations', 'decisions', 'simulated_credits', 'audit_events'):
            self.assertEqual(self.value(f'SELECT count(*) FROM dispute_actions.{table}'), '0')
        self.assertEqual(self.revision(), before)

    def test_review_survives_actual_server_restart(self):
        saved = self.save()
        before = self.revision()
        result = self.docker('restart', self.container)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.wait_ready()
        self.assertEqual(self.value('SELECT decision_id FROM dispute_actions.pending_reviews'), saved['decision'])
        self.assertEqual(self.value('SELECT count(*) FROM dispute_actions.audit_events'), '1')
        self.assertEqual(self.revision(), before)

    def test_independent_source_writer_waits_for_guard(self):
        # Keep a separate psql backend alive; signal readiness via pg_stat_activity.
        holder = subprocess.Popen(['docker', 'exec', '-i', self.container, 'psql', '-X', '-qAt',
            '-v', 'ON_ERROR_STOP=1', '-U', 'storage_admin', '-d', self.database],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            holder.stdin.write("SET application_name='t04_guard_holder'; SET ROLE dispute_action_writer; BEGIN; SELECT dispute_control.lock_source_revision();\n")
            holder.stdin.flush()
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if self.value("SELECT count(*) FROM pg_stat_activity WHERE application_name='t04_guard_holder' AND state='idle in transaction'") == '1':
                    break
                time.sleep(.05)
            else:
                self.fail('Guard holder did not reach its transaction')
            before = self.revision()
            for table, field in (('settlements','amount_minor'), ('evidence_documents','content'), ('policy_rules','explanation')):
                self.denied(f"SET lock_timeout='250ms'; UPDATE public.{table} SET {field}={field};", 'lock timeout', role='dispute_source_writer')
            holder.stdin.write('COMMIT;\n\\q\n')
            holder.stdin.flush()
            out, err = holder.communicate(timeout=10)
            self.assertEqual(holder.returncode, 0, err)
            self.sql('UPDATE public.settlements SET amount_minor=amount_minor;', role='dispute_source_writer')
            self.assertEqual(self.revision(), before + 1)
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.communicate(timeout=10)


if __name__ == '__main__':
    unittest.main()
