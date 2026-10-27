# T05 atomic simulated decision service

**T08 integration update:** the [workflow guide](./workflow.md) describes the
canonical controller, fresh coherent Zetaris snapshots, guarded shared sandbox
deployment, CLI and identical-request recovery. Earlier task acceptance and
deployment statements below are dated evidence. Historical T02 reads retain
their null revisions; normal runs use the new fresh snapshot adapter.

[app/action_service.py](../app/action_service.py) provides the sole canonical
application write API, `commit_simulated_decision(CommitRequest) -> CommitResult`.
It uses the [T04 migration](./storage.md), the existing [policy evaluator](./policy.md)
and [pure critic](./critic.md). It records synthetic decisions only. It has no
model-tool registration, SQLite fallback, source mutation or memory operation.

## Request and connection ownership

The trusted controller constructs `CommitRequest` with `run_id`, `idempotency_key`,
the complete typed `context`, `policy`, `proposal` and accepted `critic`. Keep
this immutable request for recovery. All six fields are stored as JSONB for exact
retry comparison; array order and text remain part of the request. Object key
order does not matter. A changed proposal, context, critique or run needs a new
evaluation/request, never reuse of the original key. Malformed transport raises
`ContractError` before I/O; structurally valid requests receive a bound result.

Install the optional write dependency from `dispute-demo/` in an application
virtual environment:

```sh
python -m pip install -r requirements-actions.txt
```

The default connector lazily imports pinned Psycopg 3.2.10 and reads
`DISPUTE_ACTION_DSN` from the process environment. It does not load private files
or connect on import. Supply this configuration privately; never put its value in
model inputs, logs or Git. There is no fallback to the loader's credentials.
The alternative `connect=` callable is trusted application configuration,
returning a **new, idle, non-autocommit Psycopg connection** for each invocation.
The service owns its commit, rollback and close; do not pass a shared connection
or an enclosing transaction. Psycopg's [transaction documentation](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
describes the driver behavior underlying this ownership contract.

Use a separate unprivileged login granted only `dispute_action_writer`. The
service refuses administrative/source-writer/storage-owner membership and
autocommit. T04 triggers enforce the shared source guard and automatic sidecars.
The database administrator and trusted application configuration remain trusted
boundaries; the service is not a protection against an administrator changing DDL.

## Protected transaction

1. Start READ COMMITTED / READ WRITE with fixed statement, lock and idle
   transaction timeouts, a fixed search path, and `synchronous_commit=on`.
2. Acquire `dispute_control.lock_source_revision()` in a separate statement.
   Every subsequent source read occurs after that statement finishes, including
   when another writer held the guard. Retain the guard through commit/rollback.
3. Look up the idempotency key first. Identical payload returns the original
   decision, reference, timestamp and credit ID as `reused`, even if later source
   changes make the original revision stale. A changed payload is rejected.
4. Refuse unknown/stale revisions and mismatched run/proposal/policy/critic
   identities. Reject future snapshots. Reread the source dispute, both linked
   transactions, all settlements, evidence metadata/text and applicable policies
   directly from PostgreSQL under the guard. This is a commit-time check, not an
   alternative investigation reader.
5. Check every currently authoritative scoped timestamp before filtering.
   Any record later than the submitted cutoff requires a new evaluation. The
   supplied evaluation cutoff is explicit and does not update the source row's
   historical `evaluation_at`. Policy selection still uses dispute opening.
6. Compare all typed source facts with the submitted snapshot (collection order
   alone is ignored), then rerun the canonical evaluator and critic. Compare
   the complete policy and critique, not merely an accepted flag. Only source
   status `open` is supported. No other status is silently treated as a valid
   starting state, including for review.
7. Link the current predecessor, enforce existing charge reservations, and insert
   the investigation and decision. T04 atomically creates the permitted credit
   or review sidecar and required audit event; constraints reject recycled
   identities, forks and duplicate effects. Store the validated **input** revision,
   not the revision advanced by the inserts.
8. Return `committed` only after COMMIT acknowledges. Cleanup errors cannot hide
   an acknowledged commit. No failed response contains a decision/effect ID.

Ordinary eligible credit, evidence requests and declines are autonomous.
Human review is recorded only for an independently validated permitted review
proposal. A rejected credit proposal is never relabelled as queued review.
Non-credit decisions have no amount/effect. Fresh evaluations may append after
non-credit decisions, and non-credit review may follow a credit; the T04
reservation still prevents a second credit, including a swapped duplicate pair.

## Failure and recovery

`rejected` identifies invalid/stale/conflicting inputs or storage constraints;
`unavailable` identifies missing connections/permissions/guard or bounded query
availability failures. Other transaction errors return `failed`. Exception text,
SQL and DSNs are never included in the result. Every refusal rolls back and
closes its owned connection without creating a replacement review case.

If COMMIT raises, the outcome is **unconfirmed**, not proof of rollback. Resubmit
the exact request with its original key. A durable first commit returns `reused`;
otherwise the service performs the normal protected checks. Never create a new
key to recover an uncertain commit. No automatic retry or action-from-memory
retry is performed here.

## Acceptance and deployment boundary

[test_action_service.py](../tests/test_action_service.py) builds independently
assembled, explicitly `offline_test` snapshots from a real isolated PostgreSQL
database. It executes the real Python service and Psycopg driver with separate
unprivileged connections. It does not substitute SQLite or a mocked database.
Fault injection is limited to deliberate database-trigger failures, a pause
during validation, and connection wrappers for lost acknowledgement/close errors.

From `dispute-demo/`, with Docker running, the existing `postgres:16-alpine`
image and the pinned dependency installed:

```sh
DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s agent/tests -p test_critic.py -v
PYTHONDONTWRITEBYTECODE=1 python scripts/validate_synthetic_data.py
```

The T05 fixture creates a unique container and anonymous volume, publishes one
ephemeral **loopback-only** port, and creates a fresh cloned database per test.
Authentication is trust only for this disposable synthetic fixture. It never
reads project credentials. Cleanup removes only the container/volume created by
that test run. T04 keeps its separate unnetworked fixture. Without their opt-in
flags, PostgreSQL tests are explicitly skipped; missing dependencies with the
flag enabled fail the suite rather than silently skipping acceptance.

Acceptance proves the write service in isolated PostgreSQL. The existing shared
database is still unmigrated, no runtime login was granted, and the Zetaris
reader still returns `source_revision=None`. Such requests **cannot commit**.
Before enabling an end-to-end write flow, explicitly deploy/register the guarded
source and verify uncached coherent Zetaris reads at an explicit fresh cutoff.
Do not attach a revision to an old read or expose this internal PostgreSQL
rereader as a model investigation tool. T08 must retain this deployment gate.
No live Zetaris, Nightshift or H-MEM capability is established by T05 tests.
