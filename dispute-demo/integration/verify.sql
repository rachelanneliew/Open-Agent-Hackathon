-- Run each SELECT individually in Zetaris SQL Editor, without a trailing semicolon.
SELECT 'transactions' AS dataset, COUNT(*) AS row_count FROM dispute_pg.transactions
UNION ALL SELECT 'settlements', COUNT(*) FROM dispute_pg.settlements
UNION ALL SELECT 'disputes', COUNT(*) FROM dispute_pg.disputes
UNION ALL SELECT 'evidence', COUNT(*) FROM dispute_pg.evidence
UNION ALL SELECT 'policy_rules', COUNT(*) FROM dispute_pg.policy_rules
UNION ALL SELECT 'evidence_documents', COUNT(*) FROM dispute_pg.evidence_documents;

-- Separate one-to-many joins: combining movements and evidence in a single aggregate would multiply rows.
SELECT d.dispute_id, t.transaction_id, t.amount_minor, s.settlement_id, s.movement_type, s.amount_minor AS movement_amount, s.settlement_status
FROM dispute_pg.disputes d
JOIN dispute_pg.transactions t ON t.transaction_id = d.transaction_id
JOIN dispute_pg.settlements s ON s.transaction_id = t.transaction_id
WHERE d.dispute_id = 'DP-0014'
AND s.recorded_at <= d.evaluation_at
AND s.occurred_at <= d.evaluation_at;

SELECT d.dispute_id, e.evidence_id, e.evidence_type, e.available_at, doc.content
FROM dispute_pg.disputes d
JOIN dispute_pg.evidence e ON e.dispute_id = d.dispute_id
JOIN dispute_pg.evidence_documents doc ON doc.evidence_id = e.evidence_id
WHERE d.dispute_id = 'DP-0014'
AND e.available_at <= d.evaluation_at;
