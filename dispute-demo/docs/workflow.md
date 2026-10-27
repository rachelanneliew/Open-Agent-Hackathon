# Bounded workflow and recovery (T08)

The normal runtime is `python -m app.main` from `dispute-demo/`. It runs one
Nightshift investigator, the canonical policy evaluator and pure critic, then
the restricted PostgreSQL action service. All outcomes use the same boundary.
T08 was explicitly `no_memory`. T10 now enables verified advisory memory by
default; `--no-memory` preserves that mode. See the [memory guide](./memory.md)
for source verification, partial-history bounds and memory-only recovery.
The old `agent/resolver.py` is inert after T09 and cannot recall, save or act.

## Setup and invocation

Use Python 3.10+ with a dedicated application environment. Preserve the bundled
Zetaris environment, JAR, private credentials and existing containers.

```sh
cd dispute-demo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-runtime.txt
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.main DP-0014 --no-memory
```

Nightshift uses the existing private `METERLESS_*` settings, with actual provider
keys retained in Nightshift. Strict JSON Schema draft output, native-tool refusal and disabled
tier splitting use the installed 0.92.7 contract verified live. Application code
attaches identities and the canonical explanation; the model supplies the
recommendation, citations and missing requirements. See the
[investigator guide](./investigator.md) for the verified schema subset and diagnostics. The response
still undergoes local strict parsing and validation; this request path disables
semantic response caching and skips runtime answer-memory/scaffold injection.
The worker reads private `DISPUTE_ACTION_DSN` from the process or
`dispute-demo/.env.local`. It must connect to the project database with an
unprivileged LOGIN granted only `dispute_action_writer`; admin, storage-owner and
source-writer logins are refused. The default Compose port is loopback
`127.0.0.1:55432`, configurable with `DISPUTE_DB_PORT`. Port 55000 belongs to the
Zetaris metastore and is not an action database.

For a new sandbox, back up its source data, apply
[migration 001](../db/migrations/001_decision_storage.sql) then
[migration 002](../db/migrations/002_fresh_read_bundle.sql) as its migration
administrator using `psql -X -v ON_ERROR_STOP=1`. Both are one-time migrations,
not resets. Create the restricted LOGIN with a private random password, grant
`dispute_action_writer`, and save its DSN privately. Neither migration changes
source rows. The initial loader intentionally refuses an already guarded DB.
Do not restore an old backup over existing decisions as a routine reset.

Use the bundled onboarding connection workflow/preflight, preview
[action_registration.sql](../integration/action_registration.sql) with
`getting-started/scripts/run_sql.py --dry-run`, then apply it with `--channel jdbc`
against the existing read-only `dispute` datasource. Registration adds four
views; it changes neither source credentials nor data. Do not cache these views.

## Coherent reads

[fresh_reads.py](../integration/fresh_reads.py) reads through the existing
approved Zetaris JDBC path. Migration 002 exposes one per-case JSON bundle
containing source facts, source revision, source-side statement timestamp,
customer-scoped historical cases and that case's stored decision receipts.
The bundle is computed in **one PostgreSQL statement snapshot**. All collections
are bounded to 1,001 rows, allowing detection and refusal above the 1,000-row
limit; the payload is limited to 2 MiB.

Each SELECT must first have a recognized direct `InsertableJDBCTableRelation`
physical scan in datasource `DISPUTE`. Cached or unknown plans fail closed.
Before/bundle/after revisions must agree. The source timestamp must fall between
the local start and capture times; clock skew or stale cached results fail
closed. A revision race permits only two attempts inside the same read deadline.
This is verified for the current Zetaris plan format; a platform change may need
an explicitly tested adapter update, never a silent fallback.

[fresh_tools.py](../app/fresh_tools.py) strictly maps the bundle into a
`FreshSnapshot`: context, customer history and observed decision receipts share
one reference/cutoff/revision. Historical `app.tools` commands retain their
original stored cutoff and null revisions; they are read-only diagnostics and
cannot supply a committable snapshot. Internal PostgreSQL rereads remain solely
inside the action service's protected commit transaction.

## Transitions and budgets

[Controller](../app/orchestrator.py) owns retrieve → evaluate → investigate →
validate → commit → display. Model requests are limited to the four case-bound
read projections. Each requested read gets a new coherent snapshot; old
observations are discarded and policy is reevaluated before another proposal.
The model cannot supply SQL, a customer, a cutoff, a revision or write arguments.
Stored decisions are observations, not new effects attributed to this run.

Defaults: four model calls, three read calls including initial retrieval,
300 seconds total, 120 seconds per model call, 45 per read, 25 per commit.
The CLI exposes `--model-calls`, `--tool-calls`, `--total-seconds`,
`--model-seconds`, `--read-seconds`, `--commit-seconds`, with hard upper bounds.
Attempts consume budgets before dispatch. Runtime JDBC/Psycopg workers and
Nightshift transport run in separate processes terminated at their deadlines.

Only one critic correction is allowed. Revision 1 carries the original proposal
and actual deterministic critique, with a new proposal ID and the same run and
reference. A request for new facts during correction ends that run safely; it
cannot reset the correction budget. Unresolved critique, malformed output,
uncertainty or unavailable required facts produces an honest no-credit failure.
A rejected credit is never relabelled as a saved review. Policy-required review
must itself be proposed, accepted and committed before a queue entry is shown.

## Commit and recovery

Before dispatching any action, the controller writes the **exact complete
CommitRequest** to `outputs/runs/<run_id>.request.json` (exclusive creation,
mode 0600, file/directory fsync). If this fails, no action is called. The single
action service rechecks source revision, facts, policy and critique under the
PostgreSQL guard. It owns all four outcomes and all simulated effects.

```sh
.venv/bin/python -m app.main --retry-request "outputs/runs/<run_id>.request.json"
```

Recovery submits that identical payload/key without model calls or replacement
facts/identities. Confirmed existing decisions return `reused`. A fresh ordinary
case run obtains new facts; an existing effective credit is rejected and cannot
produce an extra credit. A timeout, broken response or lost acknowledgement is
**unconfirmed**, never proof of rollback: retain and retry the original request.
Do not generate a new key to recover an uncertain commit.

CLI JSON includes facts, source/rule IDs, versions, typed proposals, critic
feedback, explicit commit status, new-credit flag and recovery path. It never
prints private model reasoning or credentials. Exit 0 means confirmed persisted
result (`committed` or `reused`); exit 1 is a workflow refusal/failure; exit 2 is
invalid input/configuration. Public traces are saved under ignored `outputs/`.
Trace-save or optional post-commit callback errors preserve confirmed action
results and never repeat the action. T10 adds bounded advisory recall and
confirmed-receipt storage; memory status is separate from decision success.
`--retry-memory <trace.json>` verifies the receipt and retries only its memory
save. It never calls the action service; see the memory guide for exit codes.

## Verification

```sh
DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 \
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s agent/tests -p test_critic.py -v
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/validate_synthetic_data.py
```

The new suites cover cache/freshness failures, correction and budget exhaustion,
changed facts, exact recovery, source races, duplicate prevention, all four
outcomes and post-commit failure. `test_end_to_end.py` uses real isolated
PostgreSQL and an explicitly scripted test model; it is **not** live Zetaris or
Nightshift evidence. Live acceptance and deployment receipts are recorded
separately in the [roadmap](../../ROADMAP.md). H-MEM and HackOS checks are not
established by this milestone.
