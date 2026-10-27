-- Apply after migrations 001/002. Existing datasource `dispute` remains read-only.
-- No cache policy: the application verifies every physical scan and source clock.
REGISTER DATASOURCE TABLE "dispute_source_revision" FROM dispute;
REGISTER DATASOURCE TABLE "dispute_read_bundle" FROM dispute;
REGISTER DATASOURCE TABLE "dispute_decision_history" FROM dispute;
REGISTER DATASOURCE TABLE "dispute_pending_reviews" FROM dispute;
