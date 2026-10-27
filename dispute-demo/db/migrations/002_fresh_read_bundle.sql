-- Additive read contract for T08. Requires migration 001. No source-row changes.
-- One PostgreSQL statement snapshot supplies revision, current facts and clock.
-- Register dispute_read_bundle in Zetaris; never cache this or the revision view.
BEGIN;
SET LOCAL lock_timeout = '10s';
SET LOCAL search_path = pg_catalog;
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM dispute_control.schema_migrations WHERE version = 1) THEN
        RAISE EXCEPTION 'Migration 001 required';
    END IF;
END $$;

CREATE VIEW public.dispute_read_bundle AS
SELECT d.dispute_id, jsonb_build_object(
    'schema_version', 1,
    'source_revision', r.revision,
    'evaluation_at', stamp.cutoff,
    'context', jsonb_build_object(
        'dispute', to_jsonb(d) || jsonb_build_object('evaluation_at', stamp.cutoff),
        'transactions', COALESCE((SELECT jsonb_agg(to_jsonb(t) ORDER BY t.transaction_id)
            FROM (SELECT * FROM public.transactions
                  WHERE transaction_id IN (d.transaction_id, d.related_transaction_id) LIMIT 1001) t), '[]'::jsonb),
        'settlements', COALESCE((SELECT jsonb_agg(to_jsonb(s) ORDER BY s.settlement_id)
            FROM (SELECT * FROM public.settlements
                  WHERE transaction_id IN (d.transaction_id, d.related_transaction_id) LIMIT 1001) s), '[]'::jsonb),
        'evidence', COALESCE((SELECT jsonb_agg((to_jsonb(e) - 'document_path') ||
                jsonb_build_object('content', doc.content) ORDER BY e.evidence_id)
            FROM (SELECT * FROM public.evidence WHERE dispute_id = d.dispute_id LIMIT 1001) e
            LEFT JOIN public.evidence_documents doc USING (evidence_id)), '[]'::jsonb),
        'policy_rules', COALESCE((SELECT jsonb_agg(to_jsonb(p) - 'rule_code' ORDER BY p.priority)
            FROM (SELECT * FROM public.policy_rules
                  WHERE reason_code IN ('ALL', d.reason_code) LIMIT 1001) p), '[]'::jsonb)
    ),
    'history', COALESCE((SELECT jsonb_agg(jsonb_build_object('dispute', to_jsonb(h),
                                      'transaction', to_jsonb(t)) ORDER BY h.opened_at, h.dispute_id)
        FROM (SELECT old.* FROM public.disputes old
              JOIN public.transactions old_t ON old_t.transaction_id = old.transaction_id
              JOIN public.transactions anchor ON anchor.customer_id = old_t.customer_id
              WHERE anchor.transaction_id = d.transaction_id AND old.dispute_id <> d.dispute_id
              LIMIT 1001) h
        JOIN public.transactions t ON t.transaction_id = h.transaction_id), '[]'::jsonb),
    'decisions', COALESCE((SELECT jsonb_agg(jsonb_build_object(
            'request', saved.request_payload,
            'decision_id', saved.decision_id::text,
            'committed_at', to_char(saved.committed_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
            'simulated_credit_id', c.simulated_credit_id::text) ORDER BY saved.committed_at, saved.decision_id)
        FROM (SELECT * FROM dispute_actions.decisions WHERE dispute_id = d.dispute_id LIMIT 1001) saved
        LEFT JOIN dispute_actions.simulated_credits c USING (decision_id)), '[]'::jsonb)
)::text AS payload
FROM public.disputes d CROSS JOIN dispute_control.source_revision r
CROSS JOIN (SELECT to_char(statement_timestamp() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') AS cutoff) stamp
WHERE r.singleton;

ALTER VIEW public.dispute_read_bundle OWNER TO dispute_storage_owner;
GRANT SELECT ON public.dispute_read_bundle TO dispute_reader, dispute_action_writer;
INSERT INTO dispute_control.schema_migrations (version) VALUES (2);
COMMIT;
