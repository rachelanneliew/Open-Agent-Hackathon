-- Send this entire multi-table COMPILE as ONE command. Never split the DDL.
COMPILE USL dispute_resolution_usl DEPLOY NAMESPACE lightning.metastore.dispute_usl_v1 DDL
CREATE TABLE dispute_case (
    dispute_id varchar(16) NOT NULL PRIMARY KEY,
    transaction_id varchar(16),
    customer_id varchar(20),
    claimed_amount_minor bigint,
    currency varchar(3),
    opened_at varchar(40)
);
CREATE TABLE merchant_evidence (
    evidence_id varchar(16) NOT NULL PRIMARY KEY,
    dispute_id varchar(16) NOT NULL FOREIGN KEY REFERENCES dispute_case(dispute_id),
    customer_id varchar(20),
    evidence_type varchar(64),
    integrity_status varchar(40),
    source_updated_at varchar(40),
    source_version varchar(32)
);
CREATE TABLE prior_case (
    history_id varchar(32) NOT NULL PRIMARY KEY,
    current_dispute_id varchar(16) NOT NULL FOREIGN KEY REFERENCES dispute_case(dispute_id),
    customer_id varchar(20),
    prior_dispute_id varchar(16),
    prior_outcome varchar(40),
    observed_at varchar(40),
    source_version varchar(32)
);
