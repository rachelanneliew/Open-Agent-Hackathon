# Architecture and technology evidence

A Nightshift Investigator proposes a structured outcome. A separate Nightshift
Reviewer challenges it after the deterministic critic. Deterministic code owns
policy, validation, bounded execution and persistence. All records and effects
are synthetic.

```mermaid
flowchart TD
    A[Analyst UI or CLI] --> C[Python controller]
    C --> Z[Allowlisted fresh reads through Zetaris JDBC]
    Z --> S[(Synthetic source records)]
    C --> M[H-MEM reference recall]
    M --> V[Verify prior receipt through Zetaris]
    V --> P[Versioned Python policy]
    Z --> P
    P --> N[Nightshift investigator]
    N --> K[Deterministic critic]
    K -->|one correction maximum| N
    K -->|accepted proposal| R[Independent Nightshift Reviewer]
    R -->|shared one correction allowance| N
    R -->|accept same final proposal| F[Final critic and reviewer binding gate]
    F --> W[Restricted PostgreSQL action service]
    W --> G[Lock revision and reread source, policy and critique]
    G --> D[(Atomic decision, optional credit, audit and review)]
    D --> H[Post-commit H-MEM summary]
    D --> A
    H --> A
```

The investigator never executes SQL or writes to the database. The controller
allows six shared model requests, three reads and 300 seconds by default, with at most
one correction shared by critic and Reviewer. A failed model or required source read cannot create a
credit or fictitious review item. Rationale currently must match canonical
policy explanations. The deterministic critic remains code; the Reviewer is a
separate completion with a distinct prompt. Both roles may use the same model.
The ordinary controller enforces review acceptance; the unchanged writer does
not independently validate Reviewer feedback. Exact saved-request recovery
reuses the original accepted request without calling either agent.

The writer uses an unprivileged login and a global revision guard enforced for
source and action writers. It compares fresh facts, reevaluates policy and
critique, then commits decision/effect/audit/queue together. An identical saved
request reuses its result. New keys cannot bypass one-credit constraints.
Merchant refunds are source facts, separate from simulated provisional credits.

Memory persists only confirmed receipts. Recall candidates need customer,
source-ID, cutoff, revision and receipt checks. Recall is partial advisory
context and cannot alter the written policy. A memory failure preserves the
confirmed decision. Retrying memory cannot invoke an action.

## Actual contributions

| Technology | Working use and evidence | Limit |
|---|---|---|
| Zetaris | JDBC retrieval of source facts, policy, revision-bounded bundle and prior receipts. Separately, [U00–U06](../zetaris-usl/README.md) adds a live three-source compiled/activated USL with native PK/FK DQ. | The decision path still uses one PostgreSQL datasource. USL is optional read-only inspection, without cross-source atomicity/freshness guarantees. Platform REST-client API key remains unconfigured; the USL REST source connector is verified through JDBC. |
| Meterless Nightshift | Primary live model transport for separate proposals and independent review. [T16 accepted](../../dispute-demo/docs/evidence/t16-live-accepted.json) and [T16 refusal](../../dispute-demo/docs/evidence/t16-live-refusal.json). [T07](../../dispute-demo/docs/evidence/t07-live-DP-0014.json) and T08/T10/T11. | Malformed output can fail validation. No deterministic replacement in normal runtime. |
| NVIDIA | Requested `meterless/auto`, observed response model `nvidia/nemotron-3.5-bolt-e4b` in actual model metadata. | Returned label is not independent provider attestation. No claim of award eligibility from model discovery alone. |
| Meterless H-MEM | Official reference pinned at `1742dec56a66e58eef9dda2d2b865823758ca8cd`, actual persistent storage/retrieval and source verification. [T09](../../dispute-demo/docs/evidence/t09-reference-memory.json), T10, T12. | Deterministic mock embeddings. Dreaming/sleep/conflict workflows are not implemented. No formal approval of exact revision found. |
| PostgreSQL | Protected rereads, atomic all-outcome decisions, concurrency constraints and durable recovery. [T12 matrix](../../dispute-demo/docs/reliability.md). | Trusted administrator remains a privileged boundary. No actual banking integration. |
| Python and TypeScript | Controller/policy/critic/UI and memory bridge. Buildless HTML/CSS/JavaScript analyst page. | Local single-host reference demo, not production authentication or deployment. |

Codex, Claude Code and Cursor are development tools, not runtime agents. Current
official rules make Cursor optional. The product contribution is the complete
source-to-proposal-to-critic-to-transaction workflow, durable retry boundary and
independent source-verified memory. No measured business time saving is claimed.

## Optional USL inspection (27 October 2026)

```mermaid
flowchart LR
    P[(Existing PostgreSQL)] --> U[Compiled Zetaris USL]
    F[Independent merchant CSV FileStore] --> U
    R[Fixed customer-history REST fixture] --> U
    U --> Q[Native PK and FK quality checks]
    U --> B[Bounded case-scoped read-only adapter]
    B --> A[Optional analyst provenance panel]
    Q --> E[Dated execution receipt]
    E --> A
```

This path has no edge into the controller or writer. It does not modify
FreshSnapshot, ContextRef, PolicyResult or CommitRequest. The panel is disabled
by default; its usable status is unverified because static fixture timestamps
and independent connectors cannot establish current, atomic business facts.
The [separate addendum](USL_ADDENDUM.md) explains the live evidence and limits;
T16 recordings predate this extension and remain unchanged.

## Provenance declaration for owner review

Reachable project Git history begins on **24 October 2026**, after the rules'
22 October 00:00 UTC threshold. This establishes commit dates, not proof that
all underlying work was first authored then. The team must confirm any earlier
untracked product code or data before submitting its declaration.

Existing external work includes Zetaris's platform/driver and onboarding
helpers, Nightshift, the official Meterless reference, Python/Node dependencies
and PostgreSQL. Their names, source pin and dependency manifests are disclosed;
we do not claim authorship of those implementations. PR #4 supplied the team's
initial prototypes on 26 October. T01–T12 integrate/harden those into the
canonical workflow. The generated dataset and policies are fictional project
assets, with reproducibility evidence in the repository.

The licensed platform/JDBC bundle is obtained from the provider and is not
redistributed in this package. The repository's two Git links need separate
live setup. No standalone application license was found, so public source
access should not be read as a new license grant. The submission owner must
confirm contributor permission and any earlier-work declaration.

## Delivery limitations

The [authenticated audit](../competition.md) records leader-only submission
access, detailed Track 3 page access, organizer acceptance and exact-reference
endorsement limits. New Zetaris scoring guidance asks for three datasources and
USL demonstrations. U00–U06 now supplies separately dated three-source USL and
native DQ evidence; this does not establish an organizer score or approval.
Future work can add richer evidence interpretation, production controls and
memory lifecycle features. The accepted action path retains its one-source
coherence boundary.
