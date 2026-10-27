# Zetaris three-source USL extension

U00–U06 implement Option B: a real compiled and activated Zetaris USL over
PostgreSQL, FileStore CSV and REST JSON. Verified against Zetaris 2.4.3.1 on
27 October 2026. All records are synthetic. The optional adapter and dashboard
panel are disabled by default and do not feed the financial decision workflow.

Read the [preflight](preflight.md), [source setup](sources.md), [model/parity](model.md),
[native quality checks](data-quality.md) and [acceptance evidence](demo-evidence.md).
The [submission addendum](../submission/USL_ADDENDUM.md) is separate from the
preserved T16 video and deck.

## Reproduce

Use the repository's existing configured, licensed Zetaris stack and follow
[getting-started instructions](../../getting-started/AGENTS.md). Do not recreate
the application databases or reset existing services. Source registration and
COMPILE are provisioning operations: inspect existing names first, and do not
rerun blindly over an existing model. No private configuration is shipped.

For a new isolated namespace, first follow [sources.md](sources.md), then from
`getting-started/` preview each file before executing the same file with JDBC:

```sh
.venv/bin/python scripts/run_sql.py --dry-run ../dispute-demo/integration/usl/sql/00_smoke.sql
.venv/bin/python scripts/run_sql.py --channel jdbc ../dispute-demo/integration/usl/sql/00_smoke.sql
```

Continue in this order: `00_source_registration.sql`, `00_source_verify.sql`,
`01_compile_usl.sql`, `02_activate_usl.sql`, `04_quality.sql`,
`06_primary_keys.sql`, then `05_quality_fixture.sql`. Use the same dry-run and
JDBC commands for each filename. The compile file must remain one statement;
the bundled runner understands its internal semicolons. The quality fixture is
separate from the real three-source model and intentionally contains an orphan.

On the already provisioned local stack, these commands from `dispute-demo/`
perform reads and start the optional local dashboard:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.usl.verify_live
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.usl_reads DP-0020 --enable
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.ui --port 8933 --no-memory --usl-preview
```

Open `http://127.0.0.1:8933`, enter DP-0020 in **Preview case ID** (or select
the source case) and choose **Load USL preview**. The preview remains available
when the independent main inventory is slow or unavailable.
No investigation is necessary. Without `--usl-preview`, the endpoint does not
open a connector. Native DQ is a dated execution receipt; loading a preview does
not rerun it. Reproduce native DQ with the SQL files above.

## Boundaries

Four fixed SELECTs validate the current case against PostgreSQL, read the scoped
merchant and history rows, and compare actual joined counts. Canonical IDs,
ownership, row shape, duplicate keys, versions and timestamps are checked.
Each query is limited to 101 rows to detect overflow beyond 100; cells are
bounded, total output is capped at 256 KiB and a child process enforces a
180-second wall deadline. Errors reveal no connection credentials or SQL logs.
Missing/malformed sources return unavailable without partial data.

A usable result is **unverified**, because these are static external fixtures
with historical timestamps and no shared transaction across connectors. Unknown
model revision/activation time are explicit nulls. A refund promise is not a
settlement, and unknown history outcomes are not decisions. Preview output has
no payment authority and never becomes FreshSnapshot, ContextRef, PolicyResult
or CommitRequest. Existing model calls, correction budget, critic, writer and
exact-request recovery are unchanged.

The new REST container and dedicated Zetaris objects remain available for
reproduction. Original five services were not restarted. No global teardown,
Jira change or portal submission is part of this extension. The user's subsequent
request authorizes publishing the completed work through a PR merged to `main`.
