-- Separate task-owned DQ fixture. Does not mutate any source case or main USL.
COMPILE USL quality_fixture DEPLOY NAMESPACE lightning.metastore.dispute_usl_v1 DDL
CREATE TABLE parent_case (
    dispute_id varchar(16) NOT NULL PRIMARY KEY
);
CREATE TABLE merchant_record (
    evidence_id varchar(16) NOT NULL PRIMARY KEY,
    dispute_id varchar(16) NOT NULL FOREIGN KEY REFERENCES parent_case(dispute_id)
);
ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.quality_fixture.parent_case AS
SELECT COALESCE(dispute_id, '') AS dispute_id FROM dispute.disputes;
ACTIVATE USL TABLE lightning.metastore.dispute_usl_v1.quality_fixture.merchant_record AS
SELECT 'DQ-VALID' AS evidence_id, 'DP-0020' AS dispute_id
UNION ALL SELECT 'DQ-ORPHAN', 'DP-9999';
RUN DQ dispute_id TABLE lightning.metastore.dispute_usl_v1.quality_fixture.merchant_record;
LIST DQ USL lightning.metastore.dispute_usl_v1.quality_fixture;
SHOW DQ INVALID RECORD dispute_id TABLE lightning.metastore.dispute_usl_v1.quality_fixture.merchant_record;
SHOW DQ ALL INVALID TABLE lightning.metastore.dispute_usl_v1.quality_fixture.merchant_record;
