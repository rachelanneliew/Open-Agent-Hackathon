# Verified advisory memory (T09–T10)

The existing Python client, memory service and TypeScript bridge now wrap the
[official reference at `1742dec56a66e58eef9dda2d2b865823758ca8cd`](https://github.com/Meterless/Meterless/tree/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem).
This is actual reference-engine execution with deterministic **mock embeddings**
and JSON persistence. It is not a production memory database or proof of
competition approval. T10 connects it to `app.main` with fresh source verification
and independent post-commit storage. The old resolver is inert. The owner approved
advisory history as the MVP acceptance scope on 27 October 2026; no binding
history rule or count threshold has been added.

## Reproduce setup

Prerequisites: macOS/Linux (POSIX `flock`), Python 3.10+, Node **24.13.0**, npm
**11.18.0**. Select that Node version with your existing version manager first.
Do not replace another team's Node installation. From `dispute-demo/`:

```sh
node --version
npm --version
export HMEM_NODE="$(command -v node)"
.venv/bin/python scripts/setup_hmem.py
npm --prefix agent/hmem_bridge ci --ignore-scripts --no-audit --no-fund
```

The setup script downloads a fixed public archive, verifies its SHA-256 and
extracts only `engines/hmem` to ignored `outputs/dependencies/hmem`. It verifies
an existing installation without replacing it. An already downloaded archive
can be supplied with `--archive outputs/dependencies/meterless-1742dec.tar.gz`.
The checked-in [pin](../agent/hmem_bridge/reference-pin.json) contains the source
revision, archive hash and SHA-256 for every runtime TypeScript file. The
[manifest](../agent/hmem_bridge/package.json) pins tsx 4.23.15 and Vitest 5.0.5;
its [lockfile](../agent/hmem_bridge/package-lock.json) pins their dependency tree.
Upstream runtime source has zero third-party runtime imports. It is unchanged.

`HMEM_NODE` selects the executable; otherwise `node` is found on PATH. Every call
checks the exact Node version. `HMEM_TSX_PACKAGE` selects the installed `tsx`
**package directory**, otherwise `agent/hmem_bridge/node_modules/tsx` is used.
The old `HMEM_TSX` executable setting is retired. `HMEM_REFERENCE_SRC` may select
another copy of `reference/src/index.ts`; all runtime source hashes must match.
Paths are process settings, never model inputs. No credentials, action DSN or
provider keys are forwarded to Node. Missing dependencies and pin mismatches
fail visibly with fixed error codes.

The local test initially picked up Node 22 from the application directory;
`memory_node_pin_mismatch` correctly prevented all reference writes. Setting
`HMEM_NODE` to the existing Node 24.13.0 executable resolved this. Root shell
selection alone does not guarantee a child uses the same runtime.

## Allowed records and provenance

Use [DisputeMemory](../agent/memory_service.py), not the private staging worker.
`CommittedSummary.from_commit(context, receipt)` accepts typed, matching
`committed` or `reused` receipts. It derives the primary transaction's customer,
decision/run/proposal IDs, dispute/snapshot/cutoff/revision, policy version,
reason, outcome/amount/currency, commit time and simulated-credit ID. Its source
reference names `dispute_actions.decisions/<decision_id>` in `dispute_demo`.
It omits model rationale, customer statements, evidence bodies and credentials.
Only the trusted application caller may supply a receipt; types do not prove
that a database row exists. T10 verifies recalled references through Zetaris.

`UnverifiedNote` is a separate typed record for an analyst note/correction, with
a stable note ID, customer/dispute IDs, policy version, UTC time and optional
referenced decision ID. Notes stay unverified, cannot become final decisions,
and must not contain credentials or unnecessary personal data. They never count
as claims or trigger review. There is no three-claim rule or `verified` tag.

`save(item)` returns `stored`, `reused` or `failed` independently of the decision.
Retry the **identical item/source ID**; committed summaries use `decision:<UUID>`
and notes use `unverified-note:<UUID>`. A changed payload under the same source
ID is rejected. No method imports/calls a financial action service. A failed or
uncertain memory acknowledgement is recovered by the same memory save only.
`recall(customer_id, query=...)` returns typed **unverified candidates**, not an
instruction string or proof of history. The workflow verifies these candidates
before exposing them to the policy/proposal stage.

## Persistence and bounds

Each customer has a separate directory under the configured `persist_dir`
(default ignored `outputs/hmem-v1`). Isolation occurs before ranking and graph
linking, and returned scope/provenance is checked again. This avoids the upstream
query behavior that admits records with no `chatId`. There is no global list API.
Memories are not automatically migrated from the old home-directory store.

Each operation takes an exclusive OS file lock for that customer, reconstructs
reference `state.json` and `ledger.jsonl` in a private temporary directory, and
starts a **new Node process**. The unchanged upstream `HMEM.add/query/store.all`
APIs operate on those files. The bridge also flushes query touches. Python then
validates the response and publishes state plus append-only ledger as **one
fsynced, atomically replaced snapshot**. Failed execution/publication preserves
the old snapshot; a lost acknowledgement after replace may have saved the memory,
so an identical retry detects and reuses it. Process death releases the OS lock;
leftover private staging directories are not used as durable state.

Limits: 15 seconds by default (configurable up to 60) for runtime and lock waits,
32 KiB request, 256 KiB combined stdout/stderr, 8 MiB snapshot, 100 records per
customer and at most 20 query results. Pipes are capped while the child runs;
timeout/overflow kills and reaps its process group. JSON rejects extra output,
duplicate keys, nonfinite values and excessive nesting. Corrupt snapshots fail
closed and are preserved. New partitions are mode 0700 and snapshots 0600.

Only this adapter may access its snapshot directories. Direct bridge/upstream
writers, shared network filesystems and malicious local users are outside this
single-host reference deployment. Locking and atomic publication prevent lost
updates; they do not make memory an authoritative ledger. No automatic pruning,
dreaming, sleep, conflict resolution, cross-customer graph or backup migration is
enabled. At limits, storage fails explicitly instead of silently losing history.

## Verification commands

From `dispute-demo/`, with `HMEM_NODE` set above:

```sh
# Offline boundary/contract/fault checks; no reference prerequisite.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p test_memory_adapter.py -v
# Explicit real-reference suite plus four retired-critic compatibility checks.
DISPUTE_HMEM_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s agent/tests -v
# Main suite; database/HTTP integrations remain separately opt-in.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
# Unchanged upstream conformance and example.
"$HMEM_NODE" --import ./agent/hmem_bridge/node_modules/tsx/dist/loader.mjs outputs/dependencies/hmem/conformance/runner.ts
"$HMEM_NODE" --import ./agent/hmem_bridge/node_modules/tsx/dist/loader.mjs outputs/dependencies/hmem/examples/01-add-memory/index.ts
```

For the upstream smoke test, its `reference/test` must resolve Vitest. On a new
reference installation only, link the pinned dependency directory (do not
replace an existing `node_modules`):

```sh
ln -s ../../../../agent/hmem_bridge/node_modules outputs/dependencies/hmem/reference/node_modules
"$HMEM_NODE" agent/hmem_bridge/node_modules/vitest/vitest.mjs run --root outputs/dependencies/hmem/reference
```

T09 evidence: 13/13 upstream conformance, 10/10 smoke, supplied add example;
12/12 real-reference adapter checks plus 4 compatibility checks; 20 offline
memory checks. Root collection: 218 total, 161 passed, 57 intentional opt-in
skips. The reference tests use synthetic contract receipts and isolated temporary
stores. They prove actual engine persistence, not database authenticity.

The separate [receipt probe](../integration/check_memory.py) saved the already
confirmed T08 DP-0014 receipt, then recalled it from another Python invocation.
It never calls a model, reads a live source or retries the financial action:

```sh
.venv/bin/python -m integration.check_memory --request "outputs/runs/<run_id>.request.json" --trace "outputs/runs/<run_id>.trace.json" --persist-dir outputs/receipt-memory
# Run again in a fresh process with the same arguments plus --recall-only.
```

See [T09 evidence](evidence/t09-reference-memory.json). Live
PostgreSQL/Zetaris/Nightshift and authenticated HackOS checks were **NOT RUN**
for T09; the subsequent T10 verification below supersedes its workflow limit.


## T10 workflow and source verification

The normal CLI enables `verified_advisory` memory. `--no-memory` disables recall
and saving; `--memory-dir` selects a private application directory. Select the
pinned Node before running these commands from `dispute-demo/`:

```sh
export HMEM_NODE="$(command -v node)"
.venv/bin/python -m app.main DP-0017 --memory-dir outputs/demo-memory
.venv/bin/python -m app.main DP-0017 --no-memory
```

The [controller](../app/orchestrator.py) first obtains a coherent authoritative
snapshot. [memory_workflow.py](../app/memory_workflow.py) recalls at most five
customer-partitioned candidates before policy/proposal evaluation. The mock
embedder missed structured summaries at its default relevance cutoff, so this
workflow requests ranked candidates with threshold zero. Ranking only selects
candidates; it never establishes truth or eligibility. Results are partial and
explicitly marked `complete_history: false`, including when recall is empty.

A candidate cannot grant permission to read another customer's case. Its dispute
must already appear in the selected snapshot's source customer history. Only
then can the trusted controller read that prior case through the same bounded
Zetaris snapshot adapter. The model's four read tools remain bound to its
selected case. Verification checks customer, case/primary identity, reason,
source channel, matching global source revision and cutoff visibility. It
compares every remembered summary field with the actual committed receipt,
including original snapshot, policy, outcome/amount, decision/run/proposal IDs,
commit timestamp and credit ID. Missing, false, future, cross-customer,
superseded or ambiguous receipts are ignored with fixed trace reasons. Notes
and their text never enter the prompt. Duplicate records count as one case.

Each prior-case read consumes the existing read/time budgets. With three default
read calls including initial retrieval, at most two distinct prior cases can be
verified without another model-requested read. Unverified candidates are skipped;
missing optional memory cannot authorize credit when required source facts fail.
A discovered revision change stops the run before model/action and requires a
fresh investigation. A model-requested refresh discards the earlier verified
history and verifies again. Critic correction on the same snapshot reuses the
already verified context without resetting budgets.

[VerifiedHistory](../app/history.py) binds a bounded structured projection to the
current customer/reference. Policy receives it but v1/v2 have no binding history
rule, so allowed outcomes and amounts remain identical to ordinary evaluation.
The investigator receives only this source-verified projection as untrusted,
advisory material. Critic and commit independently recompute unchanged rules;
history cannot create a fraud finding, review hold, or credit exception.

## Post-commit memory and recovery

Only a confirmed `committed`/`reused` receipt is saved. The trace reports memory
`pending`, then `stored`, `reused` or `failed` separately from the action result.
Each memory operation is capped at 15 seconds and the remaining run budget.
Failure or deadline exhaustion preserves the confirmed decision. Rejected and
unconfirmed actions produce no final memory. Normal exact-request action recovery
may save the recovered receipt after confirmation.

For an already confirmed action with missing/failed memory, use the separate path:

```sh
.venv/bin/python -m app.main --retry-memory "outputs/runs/<run_id>.trace.json" --memory-dir outputs/demo-memory
```

It loads the sibling `<run_id>.request.json`, validates the saved receipt binding,
and rereads the case through Zetaris. The original committed receipt must exist
and exactly match before saving. It has no action callback, never invokes the
writer, and reports `action_called: false`. A fresh process returns `reused` for
the same decision ID. Exit 0 means memory stored/reused; exit 1 means the confirmed
decision remains persisted but memory failed; exit 2 means input/source verification
failed and this invocation makes no new persistence claim. The output does not
rewrite the original investigation trace. Preserve both request and trace for
recovery. A lost action acknowledgement still requires `--retry-request` first;
never fabricate a confirmed receipt to retry memory.

## T10 verification — 27 October 2026

The owner explicitly approved **advisory history for the MVP**. Source policies,
fixtures, schema/migrations and the action service are unchanged.

- 16 adversarial offline memory-workflow tests cover incorrect/future/stale/cross-
  customer recall, notes, duplicate counts, source and model refresh, budgets,
  missing required facts, unconfirmed actions and action-free memory retry.
- Four tests use real disposable PostgreSQL and the pinned H-MEM reference with
  a labelled scripted model. They prove later-case recall after a new controller
  and new Node processes, false-memory refusal, actual-commit preservation after
  memory failure, idempotent memory retry, and stale-source refusal during outage.
- The complete main suite passes 238 tests with all opt-in flags enabled; the
  separate reference/compatibility suite passes 16. Generated-data validation passes.
- Live JDBC/Nightshift/guarded PostgreSQL/H-MEM: DP-0017 recalled and verified the
  T08 DP-0014 decision for CUST-008, then passed the critic and committed one
  synthetic SGD 57.60 credit. Its summary was stored and a separate Python
  invocation's memory retry reused it without an action call. Shared totals:
  two decisions, two credits, two audits, no reviews, source revision 10. All
  six source fingerprints match the T08 baseline; restricted login unchanged.

```sh
DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 DISPUTE_HMEM_TESTS=1 DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
DISPUTE_HMEM_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s agent/tests -v
```

See [sanitized T10 evidence](evidence/t10-verified-memory.json). REST remains
unconfigured; JDBC preflight passes. Authenticated HackOS approval is **NOT RUN**
for T10 and remains A01. The real model response reported
`nvidia/nemotron-3.5-bolt-e4b` on requested route `meterless/auto`; this is observed
metadata, not independent model identity certification.
