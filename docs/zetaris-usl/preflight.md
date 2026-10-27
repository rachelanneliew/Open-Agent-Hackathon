# U00 — Zetaris USL preflight

Verified 27 October 2026 (Singapore). Clean starting branch `main` at
`232945a1015381561785f092cbe95bba917429d7`; work branch `codex/zetaris-usl`.
Bundled onboarding revision `6a2fbaa47c32c9ac33f6584c64b43b146c621bed`.

The user's request authorizes U00–U06 sequentially. The supplied plan's
copyable U00-only handoff is reference material, not the current assignment.
No Jira mutation or portal submission is included.

## Actual checks

Commands run from `getting-started/`, using its existing Python environment:

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/preflight.py --jdbc`:
  sandbox socket denied initially; approved local-network retry passed JDBC,
  `SELECT 1`, datasource `dispute`, Lightning databases `NY_TAXI`/`TPCDS_DB`.
  Empty USL inventory. Overall exit 1: two REST-client checks lack an API key.
  This does not prevent JDBC or a data-source REST connector.
- `SHOW SERVER VERSION`: `2.4.3.1`, production, build `10/2/26, 4:30 AM`,
  tag `2.4.3.1`, commit `cb88df0b`.
- `DESCRIBE DATASOURCE TABLE dispute.disputes` and `.transactions`:
  IDs/customer/currency/timestamps are strings; amounts are long integers.
  Joined anchors: DP-0020/TX-0020/CUST-013/11400/SGD;
  DP-0014/TX-0014/CUST-008/10000/SGD;
  DP-0017/TX-0017/CUST-008/9600/SGD.
- `scripts/run_sql.py --dry-run ../dispute-demo/integration/usl/sql/00_smoke.sql`
  previewed five statements. The same runner with `--channel jdbc` executed
  all five successfully: dedicated namespace, genuine COMPILE/ACTIVATE and
  **40** rows queried from `lifecycle_probe.case_probe`.

The [smoke SQL](../../dispute-demo/integration/usl/sql/00_smoke.sql) was sent
through the existing statement-aware runner. A failed shell-quoted exploratory
command executed no SQL; it was replaced by a SQL file. No guessed command was
counted as successful.

## Source and platform boundaries

Five existing persistent containers were healthy. The driver mounts the existing
`zetaris_customer-data` volume at `/home/zetaris/customer-data`; its empty shared
directory is writable by driver UID 1001. New files use only `shared/dispute-usl-v1`.
Existing images include `python:3.9.16-slim`, permitting an isolated fixed REST
fixture without installing packages, pulling images or restarting Zetaris.

Shared source counts are 42 transactions, 54 settlements, 40 disputes,
81 evidence metadata, 81 documents and 16 rules. Before work: four decisions,
two simulated credits, four audits, one pending review, revision 17. Six source
fingerprints were recorded read-only for final comparison.

Option A lifecycle is verified. **Proceed with Option B** under the user's
authorization; FileStore/REST capabilities require independent registration and
query evidence before they count as delivered. Existing samples and documentation
alone are not connector acceptance. The action database, canonical source rows,
credentials and financial workflow remain outside this extension.
