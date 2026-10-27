-- Additive lifecycle smoke test. Dedicated task-owned namespace.
CREATE NAMESPACE IF NOT EXISTS lightning.metastore;
CREATE NAMESPACE IF NOT EXISTS lightning.metastore.dispute_usl_v1;
COMPILE USL lifecycle_probe DEPLOY NAMESPACE lightning.metastore.dispute_usl_v1 DDL
CREATE TABLE case_probe (
    dispute_id varchar(16) NOT NULL PRIMARY KEY
);
ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.lifecycle_probe.case_probe AS
SELECT COALESCE(dispute_id, '') AS dispute_id FROM dispute.disputes;
SELECT COUNT(*) FROM lightning.metastore.dispute_usl_v1.lifecycle_probe.case_probe;
