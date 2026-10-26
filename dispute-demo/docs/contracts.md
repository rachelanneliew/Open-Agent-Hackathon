# T01 shared contracts and policy semantics

Implemented in [app/schemas.py](../app/schemas.py); tested in
[tests/test_schemas.py](../tests/test_schemas.py). These are immutable transport
types and structural validation, not a policy evaluator, factual critic,
database migration, workflow runner or action service. Python 3.10+; standard
library only. Constructors accept typed values; `from_dict` accepts JSON-shaped
objects and `to_dict` returns JSON-serializable values. Unknown fields, missing
required fields and implicit numeric/string/bool coercions are rejected.

The authority for business rules is [policy v1](../policies/synthetic_policy_v1.md)
and [policy v2](../policies/synthetic_policy_v2.md), with source representations in
[the generator](../scripts/generate_synthetic_data.py) and
[policy_rules.csv](../data/synthetic/policy_rules.csv). The
[existing retrieval](../integration/get_dispute_context.py) shows current SQL
visibility and version selection. [Expected results](../tests/fixtures/expected_results.json)
are development/test references only; application contracts never load them.
None of these source files was changed by T01.

## Shared payloads

| Contract | Meaning and essential fields |
| --- | --- |
| `DisputeContext` | `reference`, capture time, source channel, dispute, linked transactions, settlement movements with statuses, visible evidence and applicable rules. Explicit `data_issues` preserve incomplete inputs. Evidence `content=None` means text was unavailable; the evidence row must not disappear. |
| `PolicyResult` | Same reference, explicit allowed/blocked partition of all four outcomes, rule checks/citations, currency, optional positive credit limit and missing evidence categories. Explicit `data_issues` restrict the allowed outcome to human_review. This is a future evaluator's output, not proof that evaluation happened. |
| `AgentProposal` | Proposal/run IDs, reference, recommendation, rationale, existing evidence/rule IDs, missing categories and revision 0 or 1. A valid shape is not approval. |
| `CriticResult` | Proposal ID, reference, accepted/revise/human_review verdict, feedback and failed checks. Acceptance requires no failures and does not mean committed. |
| `CommitResult` | Run/proposal/idempotency IDs, reference and a separate execution status. Only committed/reused may contain a persisted decision ID, recommendation, commit timestamp and optional simulated credit ID. |
| `RunState` | Run ID, technical phase, counters, proposal revision, reference, optional commit result and failure. Finished means an explicit commit result exists; inspect its status to determine whether persistence succeeded. |

`ContextRef` carries dispute ID, snapshot ID, evaluation cutoff, selected policy
version and optional source revision. Carry the **same** reference through policy,
proposal, critic and commit; never relabel an old result with a new reference.
`captured_at` records when the read was assembled, not the historical cutoff.
`source_channel` is `zetaris` or explicitly `offline_test`.

Source IDs retain the generator's formats: `DP-0001`, `TX-0001`, `OR-0001`,
`ST-0001`, `EV-0001` (four digits), `CUST-001` and `MER-001` (three digits).
Rules use versioned IDs such as `v2-APPROVE`. New run, snapshot, proposal,
idempotency, decision and simulated credit IDs are canonical nonzero UUID
strings. Their namespaces and meaning are separate even when all use UUIDs.
IDs are identifiers, never evidence of authorization or factual support.

Amounts are exact integer minor units within signed BIGINT range; no floats,
strings, booleans, currency conversion or rounding. Source amounts, credit amounts
and credit limits must be positive. The currency format is three uppercase
letters; existing policies/fixtures authorize **SGD only**. A syntactically valid
other currency must not inherit the SGD threshold. Currency mismatches remain
representable for the evaluator to escalate. Negative calculated balance is an
integrity error, never a negative credit.

JSON timestamps use UTC ISO 8601 ending in `Z`, with optional microseconds.
Python values must be timezone-aware UTC datetimes. Transaction/settlement
recording cannot precede occurrence; evidence availability cannot precede its
event. Evaluation cannot precede dispute opening. Context rejects records after
the cutoff, policies outside the opening-date interval, duplicate IDs and records
outside the primary/explicit companion transaction or dispute scope. Missing
primary transaction/policy needs an explicit data issue. These shape checks do
not verify source completeness, resolve contradictions or establish truth.

## Legacy and canonical outcomes

| Existing recommendation | Canonical business outcome | Amount in canonical recommendation | Future persisted effect |
| --- | --- | --- | --- |
| `recommend_refund` / `recommended_refund_minor` | `provisional_credit` | Positive integer `amount_minor` | One simulated provisional-credit entry |
| `reject` | `decline` | `None` / JSON `null` | Decision/audit only |
| `request_evidence` | `request_evidence` | `None` / JSON `null` | Decision/audit and requirements only |
| `escalate` | `human_review` | `None` / JSON `null` | Decision/audit and review routing only |

`from_legacy_recommendation` is the explicit adapter for recommendation payloads.
Tests pass fixture `expected_refund_minor` into its amount argument. Existing
non-credit zero amounts map to null; nonzero non-credit amounts are rejected.
Canonical non-credit payloads reject even zero: they have **no monetary amount**.
This deliberately does not rename fixture fields or change their values.

Existing settlement `capture`, `refund` and `reversal` movements retain their
meaning and `completed`/`pending`/`failed` statuses. They are not recommendations.
Never feed a merchant refund into the recommendation adapter or turn it into a
new credit. DP-0014 retains a completed 10,000 capture and 4,000 merchant refund;
its authored recommendation maps to a **new simulated** 6,000 provisional credit.
No money moves in T01 or in the planned sandbox action path.

Evidence citations reference existing `EV-*` IDs. A missing requirement instead
uses `EvidenceRequirement(category, reason, policy_rule_id)`: category is receipt,
delivery_record, refund_confirmation or two_completed_captures_same_order;
reason is absent, unusable or not_yet_available. It has no evidence ID. Two
completed captures is a source-data requirement, not a fabricated document.
Evidence requests require categories; critic/evaluator must verify they are
actually missing. ID syntax alone cannot prove that a citation supports a claim.

Execution is independent of the recommendation:

| Execution status | Contract |
| --- | --- |
| `committed` | Transaction durably stored the decision and any permitted simulated effect. |
| `reused` | Return the original stored result for the same idempotency key and identical request; create no new effect. |
| `rejected` | Stale/conflicting/invalid request was refused before persistence. |
| `unavailable` | Required storage or verification is unavailable; persistence is not confirmed. |
| `failed` | Operation failed or its outcome is unconfirmed; recover by the same idempotency key. |

Only committed/reused can claim a decision, commit time or effect. They require
a non-null source revision; provisional credit also requires a simulated credit
ID. Non-credit results forbid that ID. A timeout is not proof of rollback: later
tasks must reconcile the original idempotency key, not issue a fresh action.
Transport objects cannot themselves verify durability or prevent duplicates.

## Exact version, visibility and rule precedence

Choose policy by **dispute `opened_at`**, not evaluation time, run time or newest
version. v1 applies `[2026-01-01T00:00:00Z, 2026-10-01T00:00:00Z)`;
v2 applies `[2026-10-01T00:00:00Z, infinity)`. Missing, overlapping or incomplete
applicable rules are an input problem; never silently choose another version.

Use only records visible at `evaluation_at`, inclusive: transactions must have
`recorded_at <= cutoff`; settlements require both occurrence and recording at or
before cutoff; evidence requires `available_at <= cutoff`. Late evidence stays
excluded even if a file can be read now. Filing age is exact UTC elapsed time
from the primary transaction occurrence to dispute opening, as encoded in the
generator and boundary fixtures; do not truncate to whole calendar days.

Evaluate ascending priority; **the first applicable terminal rule wins**.
Every later rule is `not_evaluated`, not falsely reported as passing. `matched`
means applicable; `not_matched` means checked and inapplicable. An evaluator may
return a fail-closed human-review result when inputs cannot be evaluated, with
the input failures explicitly reported rather than fabricated rule success.

| Priority / rule | Source predicate | Canonical result and exact boundary |
| --- | --- | --- |
| 10 DATA_INTEGRITY | `data_integrity_or_pending` | human_review for missing/inconsistent capture, negative balance, currency mismatch or pending movement. |
| 20 FILING_WINDOW | `filing_window_exceeded` | decline if elapsed age **> 30 days v1 / > 45 days v2**. Exactly the limit is eligible. |
| 30 ALREADY_REFUNDED | `remaining_balance_zero` | decline when validated remaining balance is exactly zero. |
| 40 CONFLICTING_EVIDENCE | `material_evidence_conflict` | human_review for unresolved material contradiction. Full refund promise plus partial actual refund is compatible. |
| 50 MISSING_EVIDENCE | `required_evidence_missing` | request_evidence: refund_missing requires refund_confirmation; not_received requires receipt + delivery_record; duplicate_charge requires receipt + two completed captures for the same order. |
| 60 UNSUPPORTED | `claim_not_supported` | decline only with complete, unambiguous evidence contradicting the claim; conflicting evidence already escalated at 40. |
| 70 REVIEW_THRESHOLD | `proposed_refund_above_limit` | human_review if otherwise eligible amount **> 20,000 SGD cents**; exactly 20,000 remains eligible. |
| 80 APPROVE | `all_preceding_checks_pass` | provisional_credit of min(claimed amount, completed captures minus completed refunds and reversals). |

For the existing fixtures, compute the balance on the disputed **primary**
transaction. Its explicit companion supports the duplicate-charge claim; do not
combine two charges into a double credit. Failed movements do not count as
completed money; pending movements trigger rule 10. Do not clamp a negative
balance to zero and accidentally turn an integrity review into a decline.
Future/generalized ledger patterns require the decisions listed below.

## Workflow and business-state boundaries

This table specifies the future T08 controller protocol; T01 validates individual
state shapes and does not execute transitions or enforce call/time budgets.

| From | To | Required condition |
| --- | --- | --- |
| created | retrieved | A scoped context was retrieved; retain any input issues. |
| retrieved | evaluated | Deterministic policy output belongs to that exact context. |
| evaluated | proposed | Investigator or safe fallback supplies a typed proposal. |
| proposed | validated | Mandatory critic accepts the exact proposal and reference. |
| proposed | proposed | One correction only: revision 0 -> 1, new proposal ID, then critic runs again. |
| proposed | evaluated | Newly verified source facts require a fresh context/reference and policy evaluation; previous approval is discarded. |
| validated | finished | Safe action boundary returns an explicit CommitResult, successful or refused. A stale rejection requires a fresh run before another proposal. |
| any unfinished phase | failed | Retrieval/model/validation/budget failure prevents reaching the action boundary. Record the error; do not claim persistence. |

A critic's human_review verdict is not permission to persist the rejected
proposal: form a safe human-review proposal, evaluate/validate it and send it
through the same action boundary, or stop failed. Finished/failed runs are
terminal; a new run gets a new run ID. An idempotent commit retry keeps the same
request/key and returns the stored original result.

**Business lifecycle is unresolved by the source policies.** All generated
disputes are `open`; no authorized open -> approved/closed/reopened transition
table exists. `Dispute.dispute_status` preserves a nonblank source value without
granting permission to act. T04/T05 must agree on and test the lifecycle before
enabling commits: permitted starting states, persisted decision/review states,
new-evidence review after non-credit outcomes and prevention of another effective
credit. Do not interpret a business `decline` as technical `rejected`, or a
critic acceptance as a completed business transition.

## Snapshot, invalidation and synchronization contract for T02/T04/T05

`snapshot_id` identifies an immutable read bundle. It is **not** a hash, database
lock or source revision. `source_revision=None` explicitly means that freshness
cannot yet be verified. The existing six-table loader/retriever has no revision
protocol; nothing in T01 establishes live concurrency safety.

The chosen future sandbox protocol uses one monotonically increasing **global
project source revision**, protected by one database guard row. Its deliberately
coarse scope includes all dispute, transaction, settlement, evidence metadata
and text, policy and decision/effective-credit changes relevant to validation.

1. **Every relevant writer** must lock the guard row before mutating any covered
   data, increment its revision and commit data + revision atomically. This
   includes inserts/deletes, loaders/resets, late refunds, evidence availability
   or content changes, backdated corrections, policy edits and action writes.
   Database permissions/triggers must enforce participation; a convention used
   only by the agent is insufficient. No in-place unversioned evidence-file edit.
2. T02 must read revision before and after assembling context through Zetaris,
   including policy and evidence text, and return a revision only if both agree
   and read freshness is established. The mechanism requires uncached committed
   reads from the guarded source; a cached or independently replicated read must
   not be presented as coherent just because two revisions agree. Retry boundedly
   on change or report incomplete/unavailable. Missing guard support yields null.
3. At commit, T05 locks the same guard **before** checking current source and
   decision state, holds it through the write, and compares the request's source
   revision. Recheck policy applicability at opened_at, amounts, evidence,
   lifecycle, critic/proposal binding and existing effects. All reads and writes
   needed for that final check must share the protected transaction/visibility
   boundary. If this is not available, refuse to commit.
4. Any revision mismatch invalidates the old context, policy result, proposal and
   critique. Return rejected without effect; retrieve/re-evaluate under a fresh
   snapshot. Do not merely update the revision field. Even unrelated source
   changes conservatively invalidate proposals with this global scheme.
5. Store decision, permitted effect, audit and idempotency mapping atomically,
   then advance the revision. The stored result retains the **validated input**
   reference. An identical retry returns that original result before stale-input
   rejection; a reused key with a different payload is rejected. Enforce a
   separate uniqueness rule against multiple effective credits for the same
   dispute across different keys. Later legitimate non-credit re-review is a
   lifecycle decision, not a reason to bypass credit uniqueness.

These are requirements for later storage/retrieval implementation. They need
real PostgreSQL concurrent-writer/rollback/retry tests in T04/T05. A snapshot
UUID, a local stub test or a lock on only the dispute row cannot prove them.

## Open decisions and implementation handover

| Gap in current authority/implementation | Required treatment / owner |
| --- | --- |
| No business lifecycle or re-review rules; no definition of duplicate effective-credit scope beyond a dispute | Preserve source status; no assumed transition. T04/T05 must settle lifecycle and cross-dispute duplicate safeguards before action writes. |
| No repeated-claims numeric threshold or memory-based fraud policy | Do not invent one. T03/T10 may expose verified history or route unresolved risk to human review without alleging fraud. |
| General treatment of multiple/failed/reversed captures beyond authored scenarios | Preserve movements/statuses and fail closed on uncertain balance. T03 must document any additional interpretation and test it; do not rewrite fixtures. |
| No exhaustive machine-readable definition of material contradiction, complete support or unusable evidence | T03/T06 must ground deterministic checks in available evidence and require review when support cannot be established. Text is untrusted case material. |
| No rule for currencies other than SGD or policy before v1 | No extrapolated threshold/default version. Treat unsupported policy scope as incomplete input/review. |
| No revision guard, immutable evidence-content revisions, protected writer protocol or verified uncached multi-read behavior | T02 reports revision unavailable honestly. T04/T05 must implement and verify the protocol before successful action writes. Existing loader cannot remain an uncoordinated writer. |
| No agreed handling of new post-cutoff records for a historical evaluation at live commit | They invalidate the revision. Preserve the original cutoff; obtain an explicit new evaluation context if required. T03/T05 must not silently advance time or ignore current payment conflicts. |
| Current SQL omits some customer/status fields and inner-joins evidence text; decision tables do not exist | T02 must adapt the existing path to these contracts and expose missing text/incomplete reads. Do not claim those read tools or future decisions are already live. |

Run local verification from `dispute-demo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py
```

The schema tests encode all 40 authored scenarios and check rejection boundaries;
they do **not** predict outcomes or prove live retrieval, model, memory, database
durability or concurrency behavior. Next assigned work is T02 / KAN-11.
