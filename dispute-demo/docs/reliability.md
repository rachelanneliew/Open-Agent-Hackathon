# Reliability matrix and isolated reset/replay (T12)

The normal [CLI](./workflow.md) and [analyst UI](./analyst-ui.md) use live
Zetaris/Nightshift and the configured synthetic action database. Their state is
durable and is **never reset by this rehearsal**. Repeated live processing uses
the database duplicate safeguards; uncertain actions use the original request.

## One command for both test roots

From `dispute-demo/`, use the existing application environment:

```sh
# Offline by default; reports explicit PostgreSQL/reference/HTTP skips.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.verify

# Requires Docker already running, existing postgres:16-alpine, and pinned
# Node/H-MEM setup from memory.md. Set HMEM_NODE to that Node executable.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.verify --integrations

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/validate_synthetic_data.py
```

[demo.verify](../demo/verify.py) runs `tests/` and `agent/tests/` in separate
Python processes. Both always collect; the offline mode clears inherited
integration flags. Integration mode enables the existing five PostgreSQL,
H-MEM and local HTTP opt-ins. It reports the interpreter and per-root
collected/run/pass/fail/error/skip counts as JSON on stdout; detailed unittest
logs go to stderr. Missing setup produces a failure, never a passing empty suite.
No suite calls a real model or the configured live Zetaris instance.

Runtime imports are smoke-tested in a fresh Python process, without test paths,
with network/process creation blocked. The normal runtime modules, legacy
compatibility shims and demo entry points leave `sys.path` unchanged and do not
initialize JDBC, Psycopg, SQLite or the reference engine. Test fixtures may use
their existing test-only import paths; they never enter normal runtime imports.

## Deliberate reset/replay

```sh
# Prints the scope and prerequisites; no Docker calls or state changes.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.replay

# Intentionally starts two fresh isolated rehearsals and cleans its own state.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.replay --reset-isolated-demo
```

This is an automated **scripted rehearsal**, not another application mode or a
live-model fallback. It invokes the established disposable PostgreSQL harness
and the canonical controller with explicitly canned model responses. Reads
come directly from the isolated database's real bundle view and carry
`offline_test`; the controller carries `fault_injection`. Zetaris transport and
Nightshift are **NOT RUN**. H-MEM is the actual pinned reference with mock
embeddings. Test answers are used only to assert results; the scripted client
constructs responses from evaluated policy, never an expected-results lookup.

The command accepts no DSN, existing container, source path or memory path.
It creates a uniquely named `dispute-t05-test-*` container using the already
installed PostgreSQL image (`--pull never`), an ephemeral loopback port and its
own anonymous volume. A source template loads copies of committed synthetic
files and applies migrations 001/002. The normal runtime uses a restricted
action login; the fixture administrator is only for isolated setup/assertions.

Each of two cycles starts with a new database cloned from the pristine template,
zero decisions/revision and a new private temporary memory/journal namespace.
Between cycles, the harness drops only its own generated database. Temporary
memory directories are never reused and are removed by their owning cleanup
callbacks. Final container cleanup verifies its exact created ID, purpose
label, expected image/name and absence of host bind mounts before removal.
The shared Compose project, shared database/volume, `outputs/runs`, UI history,
`outputs/hmem-v1` and `outputs/t10-live-memory` are never targets.

The rehearsal asserts, in each cycle:

| Case / operation | Expected evidence |
|---|---|
| DP-0014 | Partial merchant refund leaves one new 6,000 SGD-minor-unit credit. |
| DP-0020 | Persisted evidence request, no monetary effect. |
| DP-0029 | Persisted filing-window decline, no monetary effect. |
| DP-0008 | Persisted policy-required review, no credit; one actual queue item. |
| DP-0017 | Prior DP-0014 decision recalled through fresh Node processes and verified against the isolated authoritative receipt before a credit. |
| DP-0033 / DP-0034 | Opening-date v1/v2 comparison: decline / permitted credit. |
| DP-0003 | Explicit +1 amount fault; one critic correction, then exact 20,000-minor-unit credit. |
| Original DP-0014 request | Same decision returned as `reused`; no new credit. |
| New DP-0014 investigation | `effective_credit_already_exists`; no new credit. |

Each completed cycle has eight decisions, four credits and one pending review.
The two cycles have disjoint decision IDs and independent database/memory state.
Six source-table hashes and repository source/policy/fixture bytes stay unchanged.
JSON output includes receipts and memory verification, not hidden model reasoning.
It prints `passed` only after the test and all fixture cleanup succeed. Missing
dependencies or failed checks produce exit 1 and test diagnostics. Abrupt OS
termination can leave an owned disposable container; inspect its exact identity
before cleanup. Never repair this by resetting a shared database.

## Coverage map

Paths below are relative to `dispute-demo/`. PostgreSQL/reference checks require
their explicit flags; HTTP checks use actual loopback fixtures, not a provider.

| Risk / invariant | Executed source of evidence | Mode |
|---|---|---|
| All 40 authored cases, partial refunds, filing/review boundaries, version selection and precedence | `tests/test_policy_engine.py`; schema/proposal critic tests | Offline synthetic source fixtures |
| Missing, unusable, contradictory, invented, future and cross-case evidence | `test_tools.py`, `test_policy_engine.py`, `test_proposal_critic.py` | Offline SQLite/read fixtures and pure checks |
| Four outcomes serialize and persist; mandatory review cannot credit | `test_schemas.py`, `test_action_service.py::test_all_four_outcomes_and_source_status_are_persisted_correctly`, `test_mandatory_review_cannot_credit_with_forged_approval`, `test_ui_end_to_end.py` | Strict contracts + real PostgreSQL/scripted model |
| Non-credit re-review and queue supersession | `test_action_service.py::test_noncredit_new_evidence_rereview_and_review_supersession`, `test_decision_storage.py` | Real PostgreSQL |
| Identical/changed-payload retry, fresh duplicate, swapped charge-pair protection | `test_action_service.py`, `test_end_to_end.py` | Real PostgreSQL, independent transactions |
| Concurrent independent requests and all-writer source guard | `test_action_service.py::test_concurrent_different_requests_cannot_both_credit`, `test_source_writer_cannot_change_facts_during_validation`, `test_waiting_action_reads_revision_after_source_writer_commits` | Real PostgreSQL connections |
| Stale/forged facts, later refunds, cached or incoherent snapshots | `test_action_service.py`, `test_fresh_reads.py`, `test_end_to_end.py::test_changed_source_refuses_stale_model_proposal` | Real PostgreSQL + separately mocked Zetaris plans |
| Actual audit-trigger failure rolls back every effect and revision | `test_action_service.py::test_database_trigger_failure_rolls_back_every_record_and_revision`; `test_reliability.py::test_real_audit_failure_rolls_back_through_ui_and_memory_is_not_saved` | Real PostgreSQL trigger fault; scripted model; memory spy |
| Lost acknowledgement is unconfirmed; exact recovery reuses durable result | `test_end_to_end.py::test_lost_commit_ack_then_exact_recovery_no_duplicate`; `test_reliability.py::test_lost_review_ack_is_unconfirmed_then_recovers_actual_queue` | Real COMMIT followed by injected transport error |
| Provider/data timeout cannot create a decision or queue; budgets remain bounded | `test_reliability.py::test_provider_and_required_data_timeouts_create_no_decision_or_queue`, `test_orchestrator.py`, `test_nightshift.py::test_total_deadline_kills_worker_even_before_headers` | Real isolated database; injected provider/data failure; actual HTTP worker timeout |
| Verified history, false/missing/cross-customer/future/stale recall and notes | `test_memory_workflow.py`, `test_memory_end_to_end.py` | Offline fault cases; actual PostgreSQL/reference where flagged |
| Save failure preserves commit; retry never calls action; restart/concurrency/isolation | `test_memory_end_to_end.py`, `agent/tests/test_hmem_integration.py` | Real PostgreSQL/reference; injected storage failures |
| Double-click, refresh/restart, recovery, only persisted reviews queued | `test_ui.py`, `test_ui_end_to_end.py`, `test_reliability.py` | Offline jobs, real local HTTP and real PostgreSQL |
| Source/reference reset isolation and cleanup refusal on ownership mismatch | `test_reliability.py::test_reset_replay_twice`, `RuntimeImportTests::test_cleanup_refuses_unowned_container_or_bound_host_directory` | Real PostgreSQL/reference replay; mocked unsafe target |
| Retired SQLite writer remains inert and existing state preserved | `agent/tests/test_critic.py` | I/O forbidden, isolated pre-existing test file |

Model wording and success rates are not deterministic acceptance criteria.
T11's live model sometimes returned invalid schemas or changed rationale
formatting. Those attempts failed visibly without effects; the stricter scripted
matrix proves safety transitions independently. Dated live evidence remains in
[T08](./evidence/t08-live-workflow.json), [T10](./evidence/t10-verified-memory.json)
and [T11](./evidence/t11-analyst.json). Fresh live Zetaris/Nightshift and portal
checks are separate from this T12 rehearsal.

## Recorded acceptance — 27 October 2026

[Verification counts/environment](./evidence/t12-verification.json) and
[two-cycle replay receipts](./evidence/t12-isolated-replay.json): 267 main and
16 reference/compatibility tests pass with no failures, errors or skips.
The offline run reports 194/4 passed and 73/12 explicit integration skips.
The standalone reset/replay command also passes sequentially; owned resources
are cleaned and shared totals/fingerprints remain unchanged. Exact commands,
timings and initial failed attempts are retained in [ROADMAP](../../ROADMAP.md).
