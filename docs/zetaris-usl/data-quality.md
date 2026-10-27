# Native Zetaris DQ and its limits

Verified live on 27 October 2026, Zetaris 2.4.3.1. The
[dated receipt](../../dispute-demo/integration/usl/dq_receipt.json) is also shown
in the optional analyst panel, clearly labelled as recorded evidence rather
than a new DQ execution on every preview.

`LIST DQ USL` returned five main-model rules: three primary keys and two foreign
keys. Their names are constrained columns, not invented `fk_*` names. LIST
returned four columns (rule, table, description, empty result); it did **not**
return cached counts even after execution. `RUN DQ <rule> TABLE <table>` returned
six columns: rule, table, constraint type, total, valid, invalid.

| Native rule | Total | Valid | Invalid |
|---|---:|---:|---:|
| dispute_case.dispute_id — PK | 40 | 40 | 0 |
| merchant_evidence.evidence_id — PK | 4 | 4 | 0 |
| merchant_evidence.dispute_id — FK | 4 | 4 | 0 |
| prior_case.history_id — PK | 3 | 3 | 0 |
| prior_case.current_dispute_id — FK | 3 | 3 | 0 |

Both main external tables returned no rows from `SHOW DQ ALL INVALID TABLE`.
Reproduce with [04_quality.sql](../../dispute-demo/integration/usl/sql/04_quality.sql)
and [06_primary_keys.sql](../../dispute-demo/integration/usl/sql/06_primary_keys.sql)
through the existing JDBC runner. No optional custom DQ expression is claimed.

## Controlled invalid fixture

The separate `quality_fixture` USL has its own `parent_case` and
`merchant_record` entities. Its two constant synthetic rows are explicitly
test fixtures, not a substitute external source or a production query result:

- `DQ-VALID → DP-0020` exists in the read-only source parent projection.
- `DQ-ORPHAN → DP-9999` does not exist.

The actual native `dispute_id` foreign-key execution returned **2 total,
1 valid, 1 invalid**. `SHOW DQ INVALID RECORD` returned ordinary columns
`["DQ-ORPHAN", "DP-9999"]`. `SHOW DQ ALL INVALID TABLE` returned a JSON-record
column `{"evidence_id":"DQ-ORPHAN","dispute_id":"DP-9999"}`.
The [fixture SQL](../../dispute-demo/integration/usl/sql/05_quality_fixture.sql)
was previewed as seven statements and all seven completed successfully. It
does not insert, update, delete or reset any shared case. Its dedicated model
is retained for reproducibility; it is disposable, not part of the preview.

## Enforcement boundaries

Native DQ detects key/referential errors. The separate parity verifier and
preview check customer ownership, scope, source shape, timestamps, versions,
duplicate IDs and joined counts in application code. Neither set certifies
freshness, completed settlement, document truth or policy eligibility.

Cross-source customer/orphan diagnostics are plain SQL checks, not registered
DQ expressions. Historical source times and unknown prior outcomes stay visible.
The canonical Python policy, critic, independent Reviewer and protected database
writer remain unchanged and receive none of this preview data.
