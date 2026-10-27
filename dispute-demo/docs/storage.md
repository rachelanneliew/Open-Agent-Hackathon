# T04 PostgreSQL decision storage

[Migration 001](../db/migrations/001_decision_storage.sql) extends the existing
six public source tables without changing their rows. It stores all four
synthetic outcomes and enforces durable credit uniqueness. It is **storage,
not the T05 action service**: policy evaluation, exact proposal/critic binding,
identical-retry recovery and commit-time freshness validation still belong to
T05/T06. No runtime login receives writer membership from this migration.
The prototype SQLite writer remains unintegrated pending those tasks; this
migration does not read, delete or migrate its local state.

## Records and invariants

| Relation | Purpose |
|---|---|
| `dispute_control.schema_migrations` | Applied version and installation time. |
| `dispute_control.source_revision` | One nonnegative BIGINT revision and shared row lock. |
| `dispute_actions.investigations` | Run/proposal/snapshot identity, dispute/primary transaction, cutoff, policy version, validated input revision and exact JSON context/proposal/critic payloads. |
| `dispute_actions.decisions` | Immutable committed outcome, original idempotency key/request payload, rationale, source/rule citations, missing requirements and prior decision. |
| `dispute_actions.simulated_credits` | Positive BIGINT effect, uniquely tied to the matching credit decision, dispute and primary transaction. Separate from merchant settlements. |
| `dispute_actions.credit_reservations` | Each credited case reserves its primary and any linked companion charge against another award. |
| `dispute_actions.audit_events` | One immutable commit event per decision; joins retain full references and payloads. |
| `dispute_actions.review_queue` | Durable queued entry created only for a committed human-review decision. |
| `dispute_actions.current_decisions` / `pending_reviews` | Latest linked decision per dispute and currently pending review entries. |

An AFTER INSERT trigger creates the required credit/reservations or review row,
and an audit event in the decision transaction. A failure rolls them all back.
Only `provisional_credit` has a positive amount/effect. Other outcomes require
SQL NULL amount; zero is rejected. Request-evidence decisions require a nonempty
requirements array. Structural JSON and foreign-key constraints complement,
but do not replace, canonical typed validation. The migration does not validate
that cited evidence supports a conclusion or that a supplied critique is genuine.

New runtime IDs are nonzero UUIDs. A run/proposal/snapshot cannot be recycled;
one decision per run, one stored result per idempotency key. Store the full
canonical request as JSONB. T05 must compare the original full payload on retry:
identical key and payload returns the original result as `reused` **before**
stale-input rejection; a changed payload is rejected. `reused` is a response,
not a second database decision. Only `committed` is stored. Database time owns
`committed_at`; no row is proof of success until COMMIT is acknowledged or the
original key is subsequently reconciled.

## Minimum lifecycle and duplicate scope

These are conservative MVP storage choices made under T04's explicit lifecycle
assignment, not new eligibility rules or edits to synthetic v1/v2 policies:

- Preserve the source dispute's status (`open` in the generated dataset). Decision
  recording does not approve, close or reopen the source row.
- Append a new investigation and decision after `request_evidence`, `decline`
  or `human_review` when a new evaluation is justified, including new evidence.
  Link it to the previous decision, use a new snapshot/run/proposal/request key,
  a later source revision and a nondecreasing cutoff. T05 must revalidate facts,
  source status and policy; non-credit does not permanently close a dispute.
- The chain cannot fork, skip the latest decision or cross disputes. Old reviews
  remain auditable but leave the pending view once a later decision supersedes
  them. Manual adjudication, assignment and resolution writes are outside T04.
- At most one effective credit per dispute **and primary transaction**, across
  any keys or dispute IDs. For linked duplicate charges, reserve both IDs so a
  second claim with swapped primary/companion cannot reimburse the pair twice.
  The amount still applies only to the primary balance, never both charges.
- This conservative overlap rule may refuse a later credit on a linked charge;
  T05 must report the conflict and may record a separately validated non-credit
  outcome. There is no partial-credit top-up, release, reversal or reissue in the
  MVP. Non-credit reviews can still be appended after an effective credit.

History tables reject UPDATE, DELETE and TRUNCATE. No reset command is provided.
T12 may implement deliberate isolated-demo replacement; it must not erase
shared source/history or circumvent uniqueness in a running instance.

## Revision guard and writer permissions

Every INSERT, UPDATE, DELETE, COPY and TRUNCATE on the six source tables and all
six action tables takes the singleton row lock **before statement execution**
and advances the revision in the same transaction. No-op statements conservatively
advance it too; a decision with automatic sidecars may advance it several times.
Only monotonic change matters, not the number of business events. Rollback rolls
back data and revision. Triggers are `ENABLE ALWAYS`.

Tables/functions belong to `dispute_storage_owner`, an unprivileged NOLOGIN role.
`dispute_source_writer` permits source DML, not ownership/DDL or guard edits.
`dispute_action_writer` can read source, insert investigations/decisions and read
action records; it cannot forge sidecars or mutate source/history. Both can call
`dispute_control.lock_source_revision()`. `dispute_reader` remains read-only.
Security-definer functions have a fixed `pg_catalog` search path and qualified
objects; PUBLIC function execution and public-schema CREATE are revoked.

The application must use separate unprivileged logins, granted only their intended
writer role by an administrator after T05 acceptance. Do not grant the owner or
superuser credentials to loaders, runtime or models. The Compose bootstrap
`dispute_loader` is a PostgreSQL administrator, **not** an enforced application
role. PostgreSQL cannot protect against its own superuser deliberately altering
DDL/triggers; administrators remain trusted for migrations. The legacy initial
loader now refuses a guarded database, including when invoked by that bootstrap
administrator. Source changes after installation must use the restricted source
writer; database triggers enforce participation without trusting caller SQL.

The migration takes exclusive source-table locks during installation, then
transfers ownership and installs triggers atomically. It contains no drops,
source-row updates, truncation or reload. It fails on reapplication instead of
silently accepting a partly changed schema. Check the migration version and
review drift before applying later versions. If installation fails, PostgreSQL
rolls back role/schema/ownership/trigger changes with the transaction.

## Fresh writes and historical evaluation

Historical T02/T03 evaluation remains read-only. A source revision alone must
never make a frozen cutoff safe for a current credit. The storage INSERT guard
rejects decisions if any currently authoritative primary/companion transaction,
settlement or case evidence has occurrence/recording/availability after the
proposed cutoff, even when the supplied revision is the latest one. It also
rejects future cutoffs and cutoffs preceding opening. This includes a later
refund, pending movement and late evidence; do not silently advance time or
relabel the old proposal. Tests insert a later refund, then verify that a request
using the latest revision and old cutoff still leaves no decision/effect.

For T05, explicitly obtain a new context at a fresh cutoff with all current
scoped facts; retain opening-date policy selection, reevaluate and revalidate.
In a READ COMMITTED transaction, acquire `lock_source_revision()` in a separate
statement **before** authoritative rereads. Hold the lock through validation and
commit, compare the request's input revision, and refuse stale/unknown revisions.
Do not compare it after investigation/decision inserts, since those also advance
the guard. The stored reference retains the validated input revision. Under
REPEATABLE READ/SERIALIZABLE, serialization failures require a full fresh retry;
an earlier transaction snapshot cannot be assumed current after waiting.

The storage cutoff backstop is not full T05 revalidation: backdated corrections,
policy/text changes and amounts still need revision comparison, authoritative
rereads and deterministic policy/critic checks under that same lock. No successful
runtime `CommitResult` is enabled by T04. Historical replay writes, if later
needed, require a separate database/source copy and explicit replay identity;
there is no replay bypass flag in this schema.

## T02 handoff and deployment boundary

The migration provides read-only public views for future Zetaris registration:
`dispute_source_revision`, `dispute_decision_history`, `dispute_pending_reviews`.
The history view includes the original run/proposal/snapshot/revision/cutoff,
outcome, citations and optional effect ID. Registration is separate from migration.
A guarded database does not prove uncached JDBC reads: T02 must still read the
revision before and after the **whole** bundle, establish uncached committed source
reads, retry boundedly on revision changes and otherwise return unavailable.
Do not infer coherence from matching revisions around independently cached data.
Until deployment, registration and that read verification are complete, the
existing T02 tools continue returning `source_revision=None` and unsupported
decision reads. T04 acceptance uses only isolated PostgreSQL, with no claim of
new live Zetaris behavior and no circular prerequisite on T05.

## Reproduce the isolated acceptance checks

From `dispute-demo/`, with Docker running and the existing `postgres:16-alpine`
image available (no pull or installation is performed):

```sh
DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_decision_storage.py -v
```

The harness creates a uniquely named container with no network or published
ports and its own anonymous data volume. It loads the committed synthetic inputs
into a test template, creates a fresh database per test, applies the actual SQL
migration, and tests real PostgreSQL permissions/constraints/transactions. The
restart test restarts **only that container** and reads the durable review back.
Cleanup removes only the container/volume created by this invocation. Tests use
separate unprivileged source/action/reader logins. Crafted proposals are storage
fixtures, not approved business decisions. Without the opt-in, these tests are
explicitly skipped with a NOT RUN reason; offline test success is not PG evidence.

For a separately reviewed deployment on a deliberately selected project database,
apply the SQL file with `psql -X -v ON_ERROR_STOP=1 -f` as its migration administrator.
The six source tables and `dispute_reader` role must already exist. Inspect
`SELECT version FROM dispute_control.schema_migrations` after application.
Do not apply to the Zetaris metastore. T04 does not migrate the existing demo
source database, alter its credentials, register views, or grant a runtime login.

## T05 implementation follow-up — 27 October 2026

The [atomic action service](./actions.md) now implements protected authoritative
rereads, exact request/policy/critic binding, all-outcome persistence and recovery
using the existing T04 migration and unchanged T01 contracts. Twenty-five real
PostgreSQL action tests and all 20 storage tests pass; the full suite has 138
passing tests with no skips. SQLite execution remains retired.

This supersedes earlier notes that the action service is absent. Shared
migration, runtime credentials and coherent fresh Zetaris reads remain pending;
T02 still returns null revisions and unsupported decision reads. The service
refuses unknown revisions. No live deployment or model/memory result is claimed.
