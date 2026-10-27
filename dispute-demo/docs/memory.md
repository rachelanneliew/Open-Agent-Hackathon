# Pinned H-MEM reference adapter (T09)

The existing Python client, memory service and TypeScript bridge now wrap the
[official reference at `1742dec56a66e58eef9dda2d2b865823758ca8cd`](https://github.com/Meterless/Meterless/tree/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem).
This is actual reference-engine execution with deterministic **mock embeddings**
and JSON persistence. It is not a production memory database or proof of
competition approval. T09 does not connect memory to `app.main`; T10 owns fresh
source verification and workflow integration. The old resolver is inert.

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
that a database row exists. T10 must verify recalled references through Zetaris.

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
instruction string or proof of history. All source references require T10 checks.

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

See [sanitized evidence](evidence/t09-reference-memory.json). The live workflow
still reports `no_memory`. Live PostgreSQL/Zetaris/Nightshift and authenticated
HackOS checks were **NOT RUN** for T09; T08's integration evidence stays dated.
