SHOW NAMESPACES OR TABLES IN lightning.metastore.dispute_usl_v1.dispute_resolution_usl;
LOAD USL dispute_resolution_usl NAMESPACE lightning.metastore.dispute_usl_v1;
SELECT COUNT(*) FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case;
SELECT COUNT(*) FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence;
SELECT COUNT(*) FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case;
SELECT d.dispute_id, d.claimed_amount_minor, COUNT(DISTINCT e.evidence_id) AS merchant_evidence_count,
  COUNT(DISTINCT h.history_id) AS prior_case_count
FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case d
LEFT JOIN lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence e ON e.dispute_id=d.dispute_id
LEFT JOIN lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case h ON h.current_dispute_id=d.dispute_id
WHERE d.dispute_id='DP-0020' GROUP BY d.dispute_id, d.claimed_amount_minor;
-- Query-based ownership/orphan diagnostics, not native registered DQ.
SELECT e.evidence_id FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence e
LEFT JOIN lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case d ON e.dispute_id=d.dispute_id
WHERE d.dispute_id IS NULL OR e.customer_id IS NULL OR e.customer_id <> d.customer_id;
SELECT h.history_id FROM lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case h
LEFT JOIN lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case d ON h.current_dispute_id=d.dispute_id
LEFT JOIN lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case p ON h.prior_dispute_id=p.dispute_id
WHERE d.dispute_id IS NULL OR p.dispute_id IS NULL OR h.customer_id IS NULL
OR h.customer_id <> d.customer_id OR h.customer_id <> p.customer_id OR h.current_dispute_id=h.prior_dispute_id;
