# Genuine USL lifecycle and parity

Model: `lightning.metastore.dispute_usl_v1.dispute_resolution_usl`.
Zetaris 2.4.3.1, driver commit `cb88df0b`, verified 27 October 2026.

The [compile file](../../dispute-demo/integration/usl/sql/01_compile_usl.sql)
contains one multi-table COMPILE statement. The bundled `run_sql.py` dry run
reported **one** statement, and JDBC returned all three table definitions,
primary keys and same-model foreign keys. The
[activation file](../../dispute-demo/integration/usl/sql/02_activate_usl.sql)
then bound each table to its independently verified source. `LOAD USL` returned
the actual `activateQuery` for all three; the saved
[live parity receipt](evidence/parity.json) contains that definition.

| USL table | Raw source | Observed rows | Exact row parity |
|---|---|---:|---|
| dispute_case | PostgreSQL disputes + transaction ownership | 40 | Passed |
| merchant_evidence | FileStore CSV | 4 | Passed |
| prior_case | REST history array, flattened with `explode` | 3 | Passed |

All primary IDs are unique. Every external row's customer matches its current
case's PostgreSQL primary transaction; history also matches the other case's
primary transaction. No orphan or mismatched customer was found in the main
model. This is query-based verification, separate from native DQ.

The actual three-source LEFT JOIN for DP-0020 returned
`["DP-0020", 11400, 2, 2]`: claim, distinct merchant records, distinct history
records. Both one-to-many joins use `COUNT(DISTINCT ...)`; counting joined rows
would inflate two records into four. This result does not prove a refund.

Reproduce from `dispute-demo/` after source registration and activation:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.usl.verify_live
```

This development verifier performs only reads and fails on missing data,
overflow, unequal row sets, duplicate keys, mismatched customer scope or joined
counts. It uses the configured JDBC helper directly with bounded fetches so a
fetch failure cannot become an empty successful result. It never calls a model
or action service. Source results and the model definition are synthetic and
sanitized; no credentials are included.

The SQL-editor equivalents are in
[03_verify_usl.sql](../../dispute-demo/integration/usl/sql/03_verify_usl.sql).
The exact parity/ownership/join checks were executed through the Python verifier;
storing that SQL file alone is not additional execution evidence.

`COALESCE` makes source key expressions non-null for Zetaris activation schema
matching. It is not a missing-key repair policy: the preview rejects empty or
malformed IDs, and DQ/uniqueness checks remain mandatory. Activation timestamps
and a monotonic model/source revision are not exposed by the inspected LOAD
response. The preview reports them as unknown. There is no materialization,
cache, or cross-source transaction guarantee.
