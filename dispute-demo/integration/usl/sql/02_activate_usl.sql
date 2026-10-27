ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.dispute_case AS
SELECT COALESCE(d.dispute_id, '') AS dispute_id, d.transaction_id, t.customer_id,
  d.claimed_amount_minor, d.currency, d.opened_at
FROM dispute.disputes d JOIN dispute.transactions t ON t.transaction_id = d.transaction_id;
ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence AS
SELECT COALESCE(evidence_id, '') AS evidence_id, COALESCE(dispute_id, '') AS dispute_id,
  customer_id, evidence_type, integrity_status, source_updated_at, source_version
FROM dispute_merchant_v1.evidence;
ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case AS
SELECT COALESCE(h.history_id, '') AS history_id, COALESCE(h.current_dispute_id, '') AS current_dispute_id,
  h.customer_id, h.prior_dispute_id, h.prior_outcome, h.observed_at, h.source_version
FROM dispute_customer_v1.history_raw LATERAL VIEW explode(history) AS h;
