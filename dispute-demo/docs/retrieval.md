# T02 typed read tools

[app/tools.py](../app/tools.py) is the canonical application read boundary over
[the existing Zetaris/JDBC integration](../integration/get_dispute_context.py).
It uses the unchanged [T01 contracts](./contracts.md). No policy evaluation,
model call, source mutation, action write or memory operation occurs here.

## Interfaces

| Tool | Result |
|---|---|
| `get_dispute_context` | A strict `DisputeContext`: source dispute/status, linked transactions including customer IDs, settlement movements/statuses, visible evidence and applicable policy metadata. |
| `get_customer_history` | A separate `CustomerHistory`, containing source disputes and their primary transactions for the current customer's scope. No inferred decisions or memory tags. |
| `get_dispute_state` | The currently stored source dispute row and capture time. This is not a historical status reconstruction or a locked commit-time reread. |
| `get_existing_decisions` | Explicit `unsupported`, without querying nonexistent decision tables. T04 storage and registration are prerequisites. |

Trusted application code constructs the registry for the authorized dispute:

```python
from app.tools import ReadToolRegistry

registry = ReadToolRegistry('DP-0014')
definitions = registry.definitions()
result = registry.dispatch('get_dispute_context', {'dispute_id': 'DP-0014'})
payload = result.to_dict()
```

Only those four names and exactly one matching `dispute_id` argument are allowed.
Unknown tools, another dispute ID, SQL, paths, customer IDs, evaluation cutoffs,
credentials, callbacks and extra fields are rejected before opening a connection.
The registry is a case scope boundary; a future UI must authorize the initial case
selection before constructing it. Direct `ReadTools` use and source injection are
for trusted backend code. Neither is a model tool for arbitrary access.

`ReadResult` is immutable and JSON-round-trippable. Inspect its status before
using its data:

| Status | Meaning |
|---|---|
| `ok` | Typed read completed. This does not establish policy eligibility or commit freshness. Empty optional evidence/history is a valid read, not a policy result. |
| `incomplete` | Missing primary/companion transaction, unavailable evidence text, missing applicable policy or query limit. A representable partial context carries the same issues in `data_issues`; otherwise `data` is null. |
| `not_found` | The source returned no matching dispute. |
| `malformed` | Invalid/duplicate/source-crossing rows, money, timestamps, JSON or overlapping policy versions. No data is exposed. |
| `unavailable` | Connection, query, fetch or close failed. Backend exception text, SQL and credentials are not returned. |
| `unsupported` | The requested capability has no implemented storage/read support. |
| `invalid_request` | Tool name/arguments do not match the registry or ID contract. |

## Visibility, missing inputs and authority

- Case scope includes only its primary and explicit companion transaction.
  Transactions must agree on customer ownership; settlements and evidence must
  belong to the requested case. IDs and metadata remain source-derived.
- Transactions require `recorded_at <= evaluation_at`; settlements require both
  occurrence and recording at/before cutoff; evidence requires availability
  at/before cutoff. Policy intervals are selected at dispute **opening**, and
  rule reason scope must match. UTC text timestamps are parsed before comparison,
  including fractional seconds. SQL restricts source scope; backend filtering
  occurs before returning dictionaries, with independent typed checks afterward.
- Evidence metadata uses a left join to text. Missing/blank/unreadable/incomplete
  text becomes `content=None` with an explicit issue, retaining the evidence ID,
  source, integrity and timestamps. Missing required evidence categories and
  substantive support are T03/T06 policy/critic work, not guesses by retrieval.
- Legacy policy action names map explicitly to the canonical four outcomes.
  Rules are transported, not executed. T03 must enforce complete rule semantics,
  predicates and support; retrieval cannot establish a policy result.
- Missing applicable policy returns incomplete with no context: the strict
  `ContextRef` needs a real policy version, so no placeholder version is invented.
- History ownership comes from the current primary transaction's customer ID.
  It excludes the current dispute and records opened/recorded after the current
  case cutoff. Historical disputes and primary transactions stay outside the
  current context's transaction/evidence collections. Their source IDs, original
  timestamps and statuses are preserved; stored outcomes are unavailable.
- Source dispute rows have no update history or recorded-at field. Their present
  status/text cannot prove what those values were at a past cutoff. History uses
  source opening and transaction recording visibility; it is advisory evidence,
  not a reconstructed ledger or fraud finding.
- Every query is capped at 1,000 scoped candidate rows plus one overflow sentinel,
  before temporal filtering. Overflow returns incomplete, never truncated success.
  There is no pagination or automatic retry. Oversized cases need a deliberate
  retrieval extension before relying on their completeness.
- `source_revision` always remains null. Snapshot UUIDs identify bundles only;
  multiple JDBC reads have no verified atomic snapshot or cache-freshness guard.
  Current source-state reads do not fix that. T04/T05 must implement the all-writer
  synchronization protocol before actions can commit.

The adapter reuses the bundled helper's environment loading, configured JAR and
JDBC connection. It fetches through that connection's cursor because the helper's
`run` method converts fetch errors into empty results. This dependency is tested
and must be rechecked if the onboarding helper changes. Imports do not read
private configuration, initialize JDBC or modify `sys.path`. Runtime tools never
read local CSVs, expected-result fixtures or arbitrary files.

## Run and verify

Complete the JDBC preflight in [TEAM_SETUP.md](../../TEAM_SETUP.md) and the scoped
[onboarding instructions](../../getting-started/AGENTS.md) before live use. The
existing configured JDBC route needs no REST key. From `dispute-demo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.tools DP-0014
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.tools DP-0014 --tool get_customer_history
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.tools DP-0014 --tool get_dispute_state
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.tools DP-0014 --tool get_existing_decisions
```

The CLI emits a structured result; exit 0 means `ok`, exit 1 means another read
status. Invalid CLI arguments exit 2. The decision command intentionally returns
`unsupported`. The older dictionary retrieval function/CLI remains compatible
for prototypes; canonical integrations should use the typed interface.

Offline checks, from the same directory:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p 'test_critic.py' -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py
```

Verified 27 October 2026 on Python 3.13.7: 50 root-suite tests (27 retrieval,
21 contracts, 2 generation), plus 6 offline prototype critic tests; zero
failures/errors/skips. The 13 prototype tests collect; the 7 external H-MEM tests
were **NOT RUN**. SQLite in retrieval tests is an isolated SQL test double,
not evidence of live Zetaris or PostgreSQL action safety.

Separate live JDBC checks passed: typed DP-0014 (1 transaction, 2 settlements,
2 evidence items, 8 v2 rules), DP-0019's late evidence exclusion, v1/v2 selection
for DP-0033/DP-0034, current source status, a missing case and customer history.
DP-0014's source customer is CUST-008; visible prior disputes were DP-0030 and
DP-0017. Decision reads returned unsupported without a query. No live data was
changed. Full commands and limitations are in [ROADMAP.md](../../ROADMAP.md).

## T04 storage handoff — 27 October 2026

[PostgreSQL storage](./storage.md) now has a tested migration and public views
`dispute_source_revision`, `dispute_decision_history`, `dispute_pending_reviews`.
Only isolated test databases were migrated; the existing demo datasource is
unchanged. T02's runtime behavior remains null revisions/unsupported decisions.
Before enabling non-null revisions, deploy/register the guarded source and prove
uncached committed reads across the entire revision-before/bundle/revision-after
sequence, with bounded retry on change. Matching revisions alone cannot establish
cache freshness. T05 must additionally perform protected authoritative rereads
and cutoff/policy/critic validation. T04's PostgreSQL tests are not JDBC evidence.
