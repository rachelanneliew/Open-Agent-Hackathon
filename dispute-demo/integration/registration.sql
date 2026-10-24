-- Reference only: run the statements individually in the Zetaris SQL Editor.
-- First create the datasource using the instructions and your private reader password.
-- Only register connection_probe until SELECT * FROM dispute_pg.connection_probe works.
REGISTER DATASOURCE TABLE "connection_probe" FROM dispute_pg;

-- After the probe query succeeds AND full loading into project Postgres succeeds:
REGISTER DATASOURCE TABLE "transactions" FROM dispute_pg;
REGISTER DATASOURCE TABLE "settlements" FROM dispute_pg;
REGISTER DATASOURCE TABLE "disputes" FROM dispute_pg;
REGISTER DATASOURCE TABLE "evidence" FROM dispute_pg;
REGISTER DATASOURCE TABLE "policy_rules" FROM dispute_pg;
REGISTER DATASOURCE TABLE "evidence_documents" FROM dispute_pg;
