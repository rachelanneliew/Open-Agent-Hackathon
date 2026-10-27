SHOW LIGHTNING TABLES dispute_merchant_v1;
SHOW LIGHTNING TABLES dispute_customer_v1;
SELECT * FROM dispute_merchant_v1.evidence ORDER BY evidence_id;
SELECT h.history_id, h.current_dispute_id, h.customer_id, h.prior_dispute_id, h.prior_outcome, h.observed_at, h.source_version
FROM dispute_customer_v1.history_raw LATERAL VIEW explode(history) AS h
ORDER BY h.history_id;
SELECT d.dispute_id, t.customer_id FROM dispute.disputes d JOIN dispute.transactions t ON t.transaction_id=d.transaction_id
WHERE d.dispute_id IN ('DP-0020','DP-0004','DP-0032','DP-0014','DP-0017') ORDER BY d.dispute_id;
