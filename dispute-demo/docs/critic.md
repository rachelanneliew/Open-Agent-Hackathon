# T06 pure critic and validator

[app/critic.py](../app/critic.py) exposes
`review_proposal(context, policy, proposal) -> CriticResult` over the unchanged
[T01 types](./contracts.md). It has no filesystem, database, network, model,
memory, clock or action-service access. It neither creates a ledger nor persists
any of the four business outcomes. Acceptance means the proposal is consistent
with the supplied snapshot; it does not mean committed or queued for review.

## Trusted inputs and validation

The controller supplies a scoped `DisputeContext`, the corresponding T03
`PolicyResult`, and an `AgentProposal`. Models must not select or replace the
context or policy input. JSON proposals first pass `AgentProposal.from_dict`.
Malformed types, IDs, amounts, outcomes, future/out-of-case context records and
mixed versions raise `ContractError`; no proposal identity is invented to make
an invalid payload look reviewed. The critic revalidates nested contracts too.

For valid transport objects, the result always retains the submitted proposal's
ID and reference, even on rejection. It requires exact agreement of dispute ID,
snapshot ID, evaluation cutoff, policy version and nullable source revision.
It then reruns the **same canonical** [T03 evaluator](./policy.md) and compares the
entire result. A fabricated policy result, or changed source facts under a reused
reference, cannot grant permission. This is local corroboration, not a fresh read
of the database. The T05 action service still must protect and reread current
state in its PostgreSQL transaction, refuse unknown/stale revisions and bind the
exact run/proposal/critic. A null revision permits read-only critique only.

The critic checks:

- Outcome is permitted, currency matches, and credit equals the written
  `min(claimed, completed primary balance)` amount. Smaller arbitrary awards also
  contradict APPROVE; non-credit amounts are forbidden by the contract.
- Every evaluated rule is cited, including earlier precedence gates. Invented,
  wrong-version or `not_evaluated` rules cannot support a proposal.
- Every evidence ID is present in this case at the cutoff. Required citations
  include all supporting IDs from evaluated policy checks. Corroboration uses
  T03's complete synthetic document templates and metadata, never ID membership
  or a keyword alone. Non-review proposals may cite only that supported set.
  Review proposals may additionally cite visible unusable/contradictory material
  for examination; that is no assertion that it supports credit.
- Missing requirements match the evaluator's exact categories, reasons and rule
  IDs, without duplicates. An absent document never needs an invented ID.
  A request with no usable documents can have an empty evidence-ID list.
- The rationale matches `policy_rationale(policy)` after stripping surrounding
  whitespace. This helper renders the evaluated rule explanations in order, or
  a safe review explanation when policy/input validation produced no checks.

## Bounded rationale support

T01 has a free-text rationale and no structured claim representation. A
code-only critic cannot establish that arbitrary prose is entailed by cited
sources. This implementation therefore accepts the deterministic explanation
vocabulary above; new prose, appended instructions, allegations from memory and
false conclusions route to review even with real source IDs. This is a deliberate
synthetic MVP limitation, not general semantic understanding. T07 can supply
`policy_rationale(policy)` in its structured proposal; the critic still validates
all other fields independently. Supporting broader prose requires a separately
scoped claim/corroboration design, not a substring heuristic or silent approval.

Missing evidence, filing-window and review-threshold precedence remain exactly
T03's. Ordinary eligible credit, evidence requests and declines pass without a
mandatory approval step. Mandatory policy review blocks credit. No repeat-claim
count or memory tag is an input to this critic.

## Feedback and correction

`failed_checks` contains stable codes; `feedback` gives corrections and exact
required rule/evidence IDs or missing categories when relevant.

| Verdict | Meaning |
| --- | --- |
| `accepted` | No failed checks; safe to attempt the separate action boundary only after its own prerequisites are met. |
| `revise` | Initial proposal has a correctable outcome, amount, currency, citation or requirement error. At most one correction, revision 1 with a new proposal ID. |
| `human_review` | Reference/policy mismatch, required-review conflict, unsupported evidence/rationale, or invalid revision 1. Do not commit the rejected proposal. No queue entry was saved. |

The pure function has no run history. T08 must enforce the expected run ID,
revision sequence, new proposal identity and total call/time limits; repeatedly
submitting revision 0 does not reset the controller's budget. Stale reference
failures need fresh retrieval/evaluation, not edited reference fields. A safe
review proposal must itself be policy-permitted, validated and persisted through
T05, or the controller must report an honest failure.

## Prototype retirement and verification

[agent/critic.py](../agent/critic.py) re-exports the canonical validator. The old
`review_and_simulate` entry point always returns `unavailable` with
`LEGACY_ACTION_PATH_RETIRED` and `simulated_credit_created=False`. It does not
read arguments as authority, touch `ledger_path`, create directories, open or
migrate/delete existing SQLite files. `DEFAULT_LEDGER=None` preserves the old
resolver's optional parameter without resolving a private state path. The
unintegrated resolver cannot produce its old success statuses through this shim;
its memory recall/setup remains T08–T10 work.

Run from `dispute-demo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py
```

[Canonical tests](../tests/test_proposal_critic.py) use actual T02 typed reads
from isolated test data and real T03 evaluations, including all 40 independently
authored cases and crafted attacks. Critic calls execute with filesystem,
SQLite, network, subprocess and service imports blocked; inputs remain unchanged
and repeated results/JSON round-trips match. [Compatibility tests](../agent/tests/test_critic.py)
replace credit-writing expectations with no-I/O checks and preservation of
existing/absent state. Canonical and compatibility test modules have distinct
names for discovery. External H-MEM tests are collected separately, not executed.

Write, duplicate and restart assertions already live in T04's real
[PostgreSQL storage tests](../tests/test_decision_storage.py). Full action retries,
concurrency and proposal-to-commit validation remain T05; deleting SQLite tests
is not a claim that these action-service tests have passed. No new service or
live integration is needed for T06's pure acceptance gate. Exact current commands,
counts and NOT RUN boundaries are in [ROADMAP.md](../../ROADMAP.md).
