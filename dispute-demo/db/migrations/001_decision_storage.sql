-- PostgreSQL 16. Apply once with psql -X -v ON_ERROR_STOP=1 -f this_file.
-- Requires the six existing public source tables. No source rows are changed.
-- Run as a migration administrator, never as an application login.
BEGIN;
SET LOCAL lock_timeout = '10s';
SET LOCAL search_path = pg_catalog;
-- Prevent a source write during ownership/trigger installation.
LOCK TABLE public.transactions, public.settlements, public.disputes,
    public.evidence, public.evidence_documents, public.policy_rules IN ACCESS EXCLUSIVE MODE;

DO $$
DECLARE name text;
BEGIN
    FOREACH name IN ARRAY ARRAY['dispute_storage_owner', 'dispute_source_writer', 'dispute_action_writer'] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = name) THEN
            EXECUTE format('CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS', name);
        END IF;
        IF EXISTS (SELECT FROM pg_roles WHERE rolname = name AND
                   (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)) THEN
            RAISE EXCEPTION 'Storage roles must be unprivileged NOLOGIN roles';
        END IF;
    END LOOP;
    IF pg_has_role('dispute_source_writer', 'dispute_storage_owner', 'MEMBER')
       OR pg_has_role('dispute_action_writer', 'dispute_storage_owner', 'MEMBER') THEN
        RAISE EXCEPTION 'Runtime writer roles must not inherit the storage owner';
    END IF;
END $$;

-- Deliberately fails on reapplication instead of silently accepting schema drift.
CREATE SCHEMA dispute_control AUTHORIZATION dispute_storage_owner;
CREATE SCHEMA dispute_actions AUTHORIZATION dispute_storage_owner;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE TABLE dispute_control.schema_migrations (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE dispute_control.source_revision (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    revision bigint NOT NULL CHECK (revision >= 0)
);
INSERT INTO dispute_control.source_revision VALUES (true, 0);

-- Lock first; the UPDATE both acquires the row lock and advances the revision.
-- Statement triggers cover COPY, no-op UPDATE/DELETE, and TRUNCATE too.
CREATE FUNCTION dispute_control.advance_revision() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
    UPDATE dispute_control.source_revision SET revision = revision + 1 WHERE singleton;
    IF NOT FOUND THEN RAISE EXCEPTION 'Source revision guard missing'; END IF;
    RETURN NULL;
END $$;
CREATE FUNCTION dispute_control.lock_source_revision() RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE result bigint;
BEGIN
    SELECT revision INTO STRICT result FROM dispute_control.source_revision WHERE singleton FOR UPDATE;
    RETURN result;
END $$;
CREATE FUNCTION dispute_control.reject_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'Committed storage is append-only';
END $$;

-- All relevant source DML goes through an ALWAYS statement trigger. Runtime
-- roles do not own tables, cannot disable triggers, and cannot edit the guard.
DO $$
DECLARE name text;
BEGIN
    FOREACH name IN ARRAY ARRAY['transactions', 'settlements', 'disputes', 'evidence', 'evidence_documents', 'policy_rules'] LOOP
        EXECUTE format('ALTER TABLE public.%I OWNER TO dispute_storage_owner', name);
        EXECUTE format('CREATE TRIGGER source_revision_before_write BEFORE INSERT OR UPDATE OR DELETE OR TRUNCATE ON public.%I FOR EACH STATEMENT EXECUTE FUNCTION dispute_control.advance_revision()', name);
        EXECUTE format('ALTER TABLE public.%I ENABLE ALWAYS TRIGGER source_revision_before_write', name);
        EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON public.%I TO dispute_source_writer', name);
        EXECUTE format('GRANT SELECT ON public.%I TO dispute_action_writer', name);
    END LOOP;
END $$;
ALTER TABLE public.disputes ADD CONSTRAINT disputes_primary_transaction UNIQUE (dispute_id, transaction_id);

CREATE DOMAIN dispute_actions.runtime_id AS uuid
    CHECK (VALUE <> '00000000-0000-0000-0000-000000000000'::uuid);
CREATE TABLE dispute_actions.investigations (
    run_id dispute_actions.runtime_id PRIMARY KEY,
    proposal_id dispute_actions.runtime_id NOT NULL UNIQUE,
    dispute_id text NOT NULL,
    transaction_id text NOT NULL,
    snapshot_id dispute_actions.runtime_id NOT NULL UNIQUE,
    evaluation_at timestamptz NOT NULL CHECK (isfinite(evaluation_at)),
    policy_version text NOT NULL CHECK (policy_version ~ '^v[1-9][0-9]*$'),
    source_revision bigint NOT NULL CHECK (source_revision >= 0),
    -- Preserve the exact typed proposal/critique and source bundle for audit.
    -- T05/T06 must validate their semantics and reference binding.
    context_payload jsonb NOT NULL CHECK (jsonb_typeof(context_payload) = 'object'),
    proposal_payload jsonb NOT NULL CHECK (jsonb_typeof(proposal_payload) = 'object'),
    critic_payload jsonb NOT NULL CHECK (jsonb_typeof(critic_payload) = 'object'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (run_id, dispute_id, transaction_id),
    FOREIGN KEY (dispute_id, transaction_id) REFERENCES public.disputes (dispute_id, transaction_id)
);
CREATE TABLE dispute_actions.decisions (
    decision_id dispute_actions.runtime_id PRIMARY KEY,
    run_id dispute_actions.runtime_id NOT NULL UNIQUE,
    dispute_id text NOT NULL,
    transaction_id text NOT NULL,
    idempotency_key dispute_actions.runtime_id NOT NULL UNIQUE,
    -- T05 compares canonical JSONB for identical retries; never just a hash/key.
    request_payload jsonb NOT NULL CHECK (jsonb_typeof(request_payload) = 'object'),
    previous_decision_id dispute_actions.runtime_id UNIQUE,
    outcome text NOT NULL CHECK (outcome IN ('provisional_credit', 'request_evidence', 'decline', 'human_review')),
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    amount_minor bigint,
    rationale text NOT NULL CHECK (length(btrim(rationale)) > 0),
    evidence_ids jsonb NOT NULL CHECK (jsonb_typeof(evidence_ids) = 'array'),
    policy_rule_ids jsonb NOT NULL CHECK (jsonb_typeof(policy_rule_ids) = 'array'),
    missing_evidence jsonb NOT NULL CHECK (jsonb_typeof(missing_evidence) = 'array'),
    execution_status text NOT NULL DEFAULT 'committed' CHECK (execution_status = 'committed'),
    committed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK ((outcome = 'provisional_credit' AND amount_minor IS NOT NULL AND amount_minor > 0)
        OR (outcome <> 'provisional_credit' AND amount_minor IS NULL)),
    CHECK (outcome <> 'request_evidence' OR jsonb_array_length(missing_evidence) > 0),
    CHECK (previous_decision_id IS NULL OR previous_decision_id <> decision_id),
    UNIQUE (decision_id, dispute_id),
    UNIQUE (decision_id, dispute_id, transaction_id, outcome, amount_minor, currency),
    UNIQUE (decision_id, outcome),
    FOREIGN KEY (run_id, dispute_id, transaction_id)
        REFERENCES dispute_actions.investigations (run_id, dispute_id, transaction_id),
    FOREIGN KEY (previous_decision_id, dispute_id)
        REFERENCES dispute_actions.decisions (decision_id, dispute_id)
);
CREATE UNIQUE INDEX decisions_first_per_dispute ON dispute_actions.decisions (dispute_id)
    WHERE previous_decision_id IS NULL;
-- No reversal/reissue operation in this MVP. Constraints survive new request keys.
CREATE UNIQUE INDEX decisions_one_credit_per_dispute ON dispute_actions.decisions (dispute_id)
    WHERE outcome = 'provisional_credit';
CREATE UNIQUE INDEX decisions_one_credit_per_primary_transaction ON dispute_actions.decisions (transaction_id)
    WHERE outcome = 'provisional_credit';

CREATE TABLE dispute_actions.simulated_credits (
    simulated_credit_id dispute_actions.runtime_id PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id dispute_actions.runtime_id NOT NULL UNIQUE,
    dispute_id text NOT NULL UNIQUE,
    transaction_id text NOT NULL UNIQUE,
    outcome text NOT NULL DEFAULT 'provisional_credit' CHECK (outcome = 'provisional_credit'),
    amount_minor bigint NOT NULL CHECK (amount_minor > 0),
    currency text NOT NULL,
    FOREIGN KEY (decision_id, dispute_id, transaction_id, outcome, amount_minor, currency)
        REFERENCES dispute_actions.decisions (decision_id, dispute_id, transaction_id, outcome, amount_minor, currency)
);
CREATE TABLE dispute_actions.review_queue (
    decision_id dispute_actions.runtime_id PRIMARY KEY,
    outcome text NOT NULL DEFAULT 'human_review' CHECK (outcome = 'human_review'),
    status text NOT NULL DEFAULT 'queued' CHECK (status = 'queued'),
    FOREIGN KEY (decision_id, outcome) REFERENCES dispute_actions.decisions (decision_id, outcome)
);
-- Reserve both linked charges for a duplicate-charge award. Swapping primary
-- and companion in another dispute must not reimburse the same pair twice.
CREATE TABLE dispute_actions.credit_reservations (
    transaction_id text PRIMARY KEY REFERENCES public.transactions,
    decision_id dispute_actions.runtime_id NOT NULL REFERENCES dispute_actions.simulated_credits (decision_id)
);
CREATE TABLE dispute_actions.audit_events (
    event_id dispute_actions.runtime_id PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id dispute_actions.runtime_id NOT NULL UNIQUE REFERENCES dispute_actions.decisions,
    event_type text NOT NULL DEFAULT 'decision_committed' CHECK (event_type = 'decision_committed'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- A fresh-write cutoff must include ALL currently authoritative scoped records,
-- including late refunds and not-yet-visible evidence. Never silently move time.
-- This is a storage backstop, not T05 policy/critic/freshness validation.
CREATE FUNCTION dispute_actions.check_decision() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE input dispute_actions.investigations; prior dispute_actions.investigations; case_row public.disputes;
BEGIN
    SELECT * INTO STRICT input FROM dispute_actions.investigations WHERE run_id = NEW.run_id;
    SELECT * INTO STRICT case_row FROM public.disputes WHERE dispute_id = NEW.dispute_id;
    IF input.evaluation_at > clock_timestamp() OR input.evaluation_at < case_row.opened_at::timestamptz THEN
        RAISE EXCEPTION 'Invalid fresh evaluation cutoff';
    END IF;
    IF EXISTS (SELECT FROM public.transactions t WHERE t.transaction_id IN (case_row.transaction_id, case_row.related_transaction_id)
               AND (t.recorded_at::timestamptz > input.evaluation_at OR t.occurred_at::timestamptz > input.evaluation_at))
       OR EXISTS (SELECT FROM public.settlements s WHERE s.transaction_id IN (case_row.transaction_id, case_row.related_transaction_id)
               AND (s.recorded_at::timestamptz > input.evaluation_at OR s.occurred_at::timestamptz > input.evaluation_at))
       OR EXISTS (SELECT FROM public.evidence e WHERE e.dispute_id = NEW.dispute_id
               AND (e.available_at::timestamptz > input.evaluation_at OR e.event_at::timestamptz > input.evaluation_at)) THEN
        RAISE EXCEPTION 'Post-cutoff source records require a new evaluation';
    END IF;
    IF NEW.previous_decision_id IS NOT NULL THEN
        SELECT i.* INTO STRICT prior FROM dispute_actions.investigations i
            JOIN dispute_actions.decisions d USING (run_id) WHERE d.decision_id = NEW.previous_decision_id;
        IF input.source_revision <= prior.source_revision OR input.evaluation_at < prior.evaluation_at THEN
            RAISE EXCEPTION 'Re-review requires a new snapshot and later source revision';
        END IF;
    END IF;
    -- Persistence time is database-owned; callers cannot backdate a decision.
    NEW.committed_at := clock_timestamp();
    RETURN NEW;
END $$;
CREATE TRIGGER validate_decision BEFORE INSERT ON dispute_actions.decisions
    FOR EACH ROW EXECUTE FUNCTION dispute_actions.check_decision();

-- Every committed decision gets its required sidecars in the SAME transaction.
-- Runtime roles cannot insert sidecars independently or edit any history.
CREATE FUNCTION dispute_actions.record_sidecars() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
    IF NEW.outcome = 'provisional_credit' THEN
        INSERT INTO dispute_actions.simulated_credits (decision_id, dispute_id, transaction_id, amount_minor, currency)
            VALUES (NEW.decision_id, NEW.dispute_id, NEW.transaction_id, NEW.amount_minor, NEW.currency);
        INSERT INTO dispute_actions.credit_reservations (transaction_id, decision_id)
            SELECT d.transaction_id, NEW.decision_id FROM public.disputes d WHERE d.dispute_id = NEW.dispute_id
            UNION
            SELECT d.related_transaction_id, NEW.decision_id FROM public.disputes d
            WHERE d.dispute_id = NEW.dispute_id AND nullif(d.related_transaction_id, '') IS NOT NULL;
    ELSIF NEW.outcome = 'human_review' THEN
        INSERT INTO dispute_actions.review_queue (decision_id) VALUES (NEW.decision_id);
    END IF;
    INSERT INTO dispute_actions.audit_events (decision_id) VALUES (NEW.decision_id);
    RETURN NULL;
END $$;
CREATE TRIGGER record_sidecars AFTER INSERT ON dispute_actions.decisions
    FOR EACH ROW EXECUTE FUNCTION dispute_actions.record_sidecars();

CREATE VIEW dispute_actions.current_decisions AS
    SELECT d.* FROM dispute_actions.decisions d
    WHERE NOT EXISTS (SELECT FROM dispute_actions.decisions next WHERE next.previous_decision_id = d.decision_id);
CREATE VIEW dispute_actions.pending_reviews AS
    SELECT q.decision_id, q.status, d.dispute_id, d.committed_at
    FROM dispute_actions.review_queue q JOIN dispute_actions.current_decisions d USING (decision_id);

-- Public, flattened read views for later Zetaris registration. Creation does
-- not establish JDBC cache freshness or enable T02 decision reads by itself.
CREATE VIEW public.dispute_source_revision AS SELECT revision FROM dispute_control.source_revision;
CREATE VIEW public.dispute_decision_history AS
    SELECT d.decision_id::text, d.run_id::text, i.proposal_id::text, d.dispute_id, d.transaction_id,
        d.idempotency_key::text, i.snapshot_id::text, i.evaluation_at, i.policy_version, i.source_revision,
        d.previous_decision_id::text, d.outcome, d.amount_minor, d.currency,
        d.evidence_ids::text, d.policy_rule_ids::text, d.missing_evidence::text,
        d.execution_status, d.committed_at, c.simulated_credit_id::text
    FROM dispute_actions.decisions d JOIN dispute_actions.investigations i USING (run_id)
    LEFT JOIN dispute_actions.simulated_credits c USING (decision_id);
CREATE VIEW public.dispute_pending_reviews AS SELECT * FROM dispute_actions.pending_reviews;

DO $$
DECLARE name text;
BEGIN
    FOREACH name IN ARRAY ARRAY['investigations', 'decisions', 'simulated_credits', 'review_queue', 'credit_reservations', 'audit_events'] LOOP
        EXECUTE format('CREATE TRIGGER source_revision_before_write BEFORE INSERT OR UPDATE OR DELETE OR TRUNCATE ON dispute_actions.%I FOR EACH STATEMENT EXECUTE FUNCTION dispute_control.advance_revision()', name);
        EXECUTE format('ALTER TABLE dispute_actions.%I ENABLE ALWAYS TRIGGER source_revision_before_write', name);
        EXECUTE format('CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE OR TRUNCATE ON dispute_actions.%I FOR EACH STATEMENT EXECUTE FUNCTION dispute_control.reject_mutation()', name);
        EXECUTE format('ALTER TABLE dispute_actions.%I ENABLE ALWAYS TRIGGER immutable_history', name);
        EXECUTE format('ALTER TABLE dispute_actions.%I OWNER TO dispute_storage_owner', name);
    END LOOP;
END $$;
ALTER TABLE dispute_actions.decisions ENABLE ALWAYS TRIGGER validate_decision;
ALTER TABLE dispute_actions.decisions ENABLE ALWAYS TRIGGER record_sidecars;
ALTER TABLE dispute_control.source_revision OWNER TO dispute_storage_owner;
ALTER TABLE dispute_control.schema_migrations OWNER TO dispute_storage_owner;
ALTER DOMAIN dispute_actions.runtime_id OWNER TO dispute_storage_owner;
ALTER VIEW dispute_actions.current_decisions OWNER TO dispute_storage_owner;
ALTER VIEW dispute_actions.pending_reviews OWNER TO dispute_storage_owner;
ALTER VIEW public.dispute_source_revision OWNER TO dispute_storage_owner;
ALTER VIEW public.dispute_decision_history OWNER TO dispute_storage_owner;
ALTER VIEW public.dispute_pending_reviews OWNER TO dispute_storage_owner;
ALTER FUNCTION dispute_control.advance_revision() OWNER TO dispute_storage_owner;
ALTER FUNCTION dispute_control.lock_source_revision() OWNER TO dispute_storage_owner;
ALTER FUNCTION dispute_control.reject_mutation() OWNER TO dispute_storage_owner;
ALTER FUNCTION dispute_actions.check_decision() OWNER TO dispute_storage_owner;
ALTER FUNCTION dispute_actions.record_sidecars() OWNER TO dispute_storage_owner;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA dispute_control, dispute_actions FROM PUBLIC;
GRANT USAGE ON SCHEMA public, dispute_control, dispute_actions TO dispute_source_writer, dispute_action_writer;
GRANT SELECT ON dispute_control.source_revision TO dispute_source_writer, dispute_action_writer;
GRANT EXECUTE ON FUNCTION dispute_control.lock_source_revision() TO dispute_source_writer, dispute_action_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA dispute_actions TO dispute_action_writer;
GRANT INSERT ON dispute_actions.investigations, dispute_actions.decisions TO dispute_action_writer;
-- Existing read-only account receives schema access, never write privileges.
GRANT USAGE ON SCHEMA dispute_control, dispute_actions TO dispute_reader;
GRANT SELECT ON dispute_control.source_revision TO dispute_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA dispute_actions TO dispute_reader;
GRANT SELECT ON public.dispute_source_revision, public.dispute_decision_history, public.dispute_pending_reviews TO dispute_reader;
INSERT INTO dispute_control.schema_migrations (version) VALUES (1);
COMMIT;
