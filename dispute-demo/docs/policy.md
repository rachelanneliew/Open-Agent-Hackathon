# T03 deterministic policy evaluation

[app/policy_engine.py](../app/policy_engine.py) adapts the original prototype into
one pure evaluator: `evaluate_policy(context, evaluation_time=None) -> PolicyResult`.
The [legacy entry point](../agent/policy_engine.py) only validates dictionary
rows through T02, delegates, and translates the result back to legacy names.
There is no second evaluator, fixture lookup, model call, memory lookup or write.

## Contract and rule support

Pass a canonical immutable `DisputeContext` from [T02](./retrieval.md). The result
retains the exact reference, including cutoff and nullable source revision.
An explicit evaluation time must be UTC and equal that cutoff; changed facts/time
require fresh retrieval and evaluation. Malformed transport values raise
`ContractError` before an eligible result exists. A structurally valid context
with unsupported policy/data returns human review.

Only the complete supplied v1/v2 sets defined by [policy v1](../policies/synthetic_policy_v1.md),
[v2](../policies/synthetic_policy_v2.md) and the generator are implemented.
Rule IDs, predicates, actions, priorities, scope, periods and exact parameters
are checked before evaluation. Unknown versions, duplicate/missing predicates,
changed actions/parameters or unsupported currencies return explicit input
failures without fabricated checks. New policies require new executable support.
Source explanations never execute as instructions.

Rules run in ascending priority; the first terminal match wins. Earlier checks
are `not_matched`, the selected check is `matched`, later checks are
`not_evaluated`. All four outcomes are partitioned into one allowed and three
blocked outcomes. Non-credit results have no credit limit. Evidence requests
carry missing categories, never fabricated IDs. Mandatory review blocks credit.
A policy result is neither an executed decision nor a saved review item.

Opening date selects v1/v2 even when evaluation crosses the version boundary.
Filing uses exact elapsed time from the primary transaction: 30/45 days inclusive.
Review is required only **above** 20,000 SGD minor units. History does not affect
these policies; there is no numeric repeated-claims rule or memory input.

## Ledger interpretation

Only the primary transaction determines the credit cap:
`min(claimed, completed captures - completed refunds - completed reversals)`.
The companion supports duplicate-charge evidence and never doubles that cap.
Completed movement IDs and primary transaction ID appear in the balance check.
Failed movements are excluded from completed money; pending movements trigger
integrity review. Negative balances are errors, never clamped to zero.

Supported synthetic ledgers have one completed capture per linked transaction,
matching its amount. Missing/inconsistent captures, cross-customer records,
currency mismatches, invalid transaction states, impossible movement chronology
and aggregate BIGINT overflow require review. Reversed transactions require zero
balance. Multiple-capture/re-authorisation patterns and refunded companions in
duplicate claims are conservatively unsupported, not new binding business rules.
Same-order duplicate support also checks merchant/customer identity. Only source
status `open` is supported; T04/T05 still own lifecycle and synchronization.

## Bounded synthetic evidence interpretation

Evidence labels or keyword substrings cannot establish support. The evaluator
recognizes the complete generated document format: banner, exact metadata
(ID, dispute, primary transaction, order, type/source and event/availability times)
and a complete body template from [the generator](../scripts/generate_synthetic_data.py).
Surrounding whitespace is ignored. Receipt amount/customer and refund-promise
amount must match the primary source record. A linked refund/reversal must belong
to that primary transaction. Delivery recognizes exactly the generated
lost/not-delivered or signed-delivery body. Both together require review;
signed delivery alone with all requirements present permits decline.

This is a bounded synthetic-template interpreter, not general natural-language
understanding or document authentication. Unknown prose, changed metadata,
negations, appended instructions, missing text and invalid integrity markers are
not usable support. Missing/unusable required categories request evidence at
rule 50. Unknown additional evidence, including another unrecognized document
of an otherwise supported category, requires review at rule 40 because a possible
contradiction cannot be resolved. A full refund promise and partial actual refund
remain compatible.

T02's exact `evidence_text_unavailable:EV-*` diagnostics are classified as unusable
evidence when the retained row is actually unavailable. They are resolved into
rule 40/50 handling rather than copied as generic failures that override
filing/missing-evidence precedence. All other read issues remain explicit
integrity-review failures; T01 contracts are unchanged. Future documents are
filtered by T02 and rejected by direct context construction. Filtered future
metadata is absent, so requirements say `absent`, not `not_yet_available`.

## Verification and use

Run from `dispute-demo/` using the existing Python 3.13.7 environment:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py
```

Offline: 70 main tests (20 policy, 27 retrieval, 21 contracts, 2 generation),
6 prototype critic tests and data validation pass. All 40 authored cases match
canonical/legacy outcomes, amounts, rules and citations/reasons without changing
source data or expected results. Added checks cover microsecond filing boundaries,
threshold ±1, malformed policy, evidence, precedence, ledger anomalies, cutoff and
purity. SQLite tests use isolated databases and do not prove live integrations.

After the required JDBC preflight succeeds, the read-only live runner is:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.policy_engine DP-0014
```

It reads through T02/JDBC and prints source/read status and the bound result,
without a fixture fallback. Retrieval without a typed context exits 1 with a
structured failure. Exit 0 means evaluation, not credit or persistence.

Live acceptance passed on 27 October after user-authorized startup of the existing
local stack. JDBC preflight passed; REST-only failures remain because its API key
is unset. The CLI evaluated DP-0014 at a 6,000 SGD-minor-unit cap. A separate
read-only assertion run passed eight live contexts: DP-0014, DP-0019, DP-0024,
DP-0029, DP-0008, DP-0003, DP-0033 and DP-0034. These cover all four outcomes,
partial refund, threshold and policy-version boundaries, exact reference/rule
binding, citation membership and JSON round-trips. No fixture fallback, model,
action or memory calls occurred; source data was preserved. See
[ROADMAP.md](../../ROADMAP.md) for commands and the initial failed attempt.

T03 is DONE; source revisions remain null and no commit freshness is established.
Pure critic integration remains T06; the unchanged SQLite-writing critic/resolver
remain unintegrated prototypes. Services are left running; no source reset,
configuration change or dependency installation was required.
