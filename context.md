# Project Context — Synthetic Card-Dispute Resolution Agent

> **Canonical project brief for all coding agents and collaborators.**
> Read this file **at the start of every task**, then consult [`ROADMAP.md`](./ROADMAP.md) for the active priorities. Read the actual code, policies, schemas, tests, and HackOS instructions before making implementation claims.
>
> **Context last reviewed:** 2026-10-27, T13 delivery verification. T00–T13 and A01 are complete against their repository acceptance gates. The submission package includes a checked deck, narrated video, walkthrough and explicit owner blockers; HackOS submission is not complete. T12 passed all 267 main tests and 16 reference/compatibility checks. T13 independently reproduced setup and two isolated replay cycles from a public clean checkout. Live evidence remains separately dated; shared state is preserved. The user authorized the full roadmap sequentially with Jira updates and a commit/push to `origin/main` per completed task.

> **Latest extension, 27 October 2026:** the user explicitly assigned all U00–U06.
> [Three-source USL](docs/zetaris-usl/README.md) now runs on Zetaris 2.4.3.1 over
> existing PostgreSQL, a new CSV FileStore and a fixed REST fixture. Real
> COMPILE/ACTIVATE, exact 40/4/3 row parity, joined DP-0020 counts and native PK/FK
> DQ are verified. A separate invalid fixture demonstrates one detected orphan.
> The bounded adapter and optional dashboard panel are off by default and have
> no action authority; freshness/atomicity remain unverified. The original
> coherent decision path, policies, sources and financial effects are preserved.
> Full isolated regression: 328 main + 16 reference tests passed. See the
> [dated evidence](docs/zetaris-usl/demo-evidence.md) for live UI limits and commands.
> U00–U06 was developed on `codex/zetaris-usl`. The user's subsequent request
> authorizes committing, opening a PR and merging it to `main`; no Jira edit or
> portal submission is included. T16 media remains unchanged. Earlier one-source/no-USL
> statements below describe historical milestones, not this optional extension.

## 1. Project identity

| Field | Context |
|---|---|
| Project | Open Agent Hackathon 2026 — synthetic card-dispute resolution agent |
| Intended track | Track 3 — Reasoning Architecture; authenticated summary verified, separate detailed page access remains B3 in the competition checklist |
| Primary user | Card-dispute operations analyst |
| User input | A synthetic `dispute_id` |
| Desired output | Evidence-grounded recommendation, policy-rule citations, critic/validation result, and recorded **simulated** outcome or human-review route |
| Development tools | Python, PostgreSQL, Zetaris (JDBC), Nightshift, reference H-MEM; Codex, Claude Code, and Cursor are **optional coding tools**, not part of runtime architecture |
| Safety boundary | Entirely synthetic records, policies, and actions — **no real bank/payment integrations** |

### One-sentence product definition

An analyst selects a dispute; the system retrieves relevant synthetic records through Zetaris, applies deterministic policy rules in code, requests a structured AI recommendation through Nightshift, validates it with a critic, safely records a sandbox-only decision, and uses H-MEM to recall source-linked context in later investigations.

### Success criteria for the first working version

1. A selected dispute can be retrieved through the **actual Zetaris read path**.
2. Executable Python policy checks determine allowed actions and hard blocks without relying on the LLM.
3. Nightshift produces a structured, evidence-linked proposal; a critic rejects invalid references, amounts, or disallowed actions.
4. A PostgreSQL transaction records the approved **simulated** result; repeated and concurrent attempts cannot create duplicate simulated credits.
5. The result exposes evidence IDs, policy-rule IDs, validation feedback, and action status.
6. The complete product demonstrates a real H-MEM save/recall sequence with verified source references and persistence. T09/T10 verify this reference implementation; A01 confirms H-MEM is an allowed engine, without formal endorsement of the exact revision.
7. The end-to-end demo and setup instructions are reproducible by another teammate.

## 2. Product scope

### Supported intended outcomes

- **Simulated provisional credit** — record a hypothetical credit action; never move actual money.
- **Request more evidence** — identify missing or contradictory required support.
- **Decline** — only when allowed by the applicable synthetic policy.
- **Human review** — route policy-required exceptions or unresolved material issues; repeated history alone remains advisory without an approved binding rule.

### Out of scope for the MVP

Real chargebacks, real bank API access, production authentication, production fund movements, live customer data, model training during demonstrations, and optional fraud-risk scoring unless the core workflow is already complete.

### Selective human review — product direction recorded 2026-10-27

The section 7 alignment assignment adopts the supplied handoff's product direction: ordinary policy-permitted `provisional_credit`, `request_evidence`, and `decline` outcomes are made, validated and recorded autonomously. `human_review` is exceptional; there is no compulsory human approval step for every case. Evidence requests mean recording/displaying missing requirements, not sending customer messages. This is project intent, not a verified HackOS requirement.

Written policy-required review excludes credit in policy evaluation, the pure critic and the PostgreSQL action service's commit-time recheck. Keep existing rule precedence: missing evidence and out-of-window claims retain their own outcomes. A critic review verdict is not a saved review case; construct and validate a safe proposal through the action service or report failure. Only confirmed persistence may appear as queued review.

Verified repeat-claim history is advisory by default. Neither source policy defines a numeric history rule; the prototype's default of three prior disputes is not approved binding policy. Raw memory tags cannot prove fraud, require review or establish credit eligibility. Verify recalled ownership, source IDs, timestamps and relevant committed outcomes through approved reads. Unavailable required authoritative facts still mean no automatic credit.

On 27 October 2026, the owner explicitly approved advisory history as the MVP acceptance scope for T10. No binding history rule or claim-count threshold is introduced. Any future binding rule needs separate approval specifying count, lookback, anchor, reasons, qualifying outcomes, exclusions and precedence.

### Distinctions that must not be blurred

- A settlement **refund**, **capture**, or **reversal** is an existing movement in synthetic transaction data.
- A newly recorded **simulated provisional credit** is a separate dispute-action record.
- A `duplicate_charge` dispute is about two charges; **idempotency** concerns accidentally applying a decision/credit *twice to the same dispute*.
- `recommend_refund` and `recommended_refund_minor` appear in existing generation/fixture terminology. Define and test an explicit compatibility mapping if those fields are still present; never silently equate a merchant refund with provisional credit.
- Agent proposals are **recommendations**, not executed decisions or financial ledger entries.

## 3. Target workflow and component responsibilities

> **Proposed architecture, not implementation status.** Section 4 records the T00 verification and remaining gaps. The task-by-task build order is in ROADMAP.md under stable IDs T00–T13 and A01.

### Runtime structure

Start with **one investigator LLM**, a **mandatory code-based critic/validator** and a **Python workflow controller**. A second LLM can later add semantic review, but it is not the safety authority or a prerequisite in this plan. Keep the small planning/checklist responsibility within the investigator and the fixed workflow, rather than introducing another manager agent.

```text
Analyst -> CLI / thin UI
                |
                v
       Python orchestrator / workflow controller
       (owns run state, limits, tool dispatch and write access)
                |
                +--> Approved read tools -> Zetaris -> source records
                |    case, settlements, evidence, policies, verified history
                |
                +--> H-MEM adapter -> source-linked recall
                |    verify recalled source facts through approved reads
                |
                +--> Python policy engine
                |    binding rules and allowed outcomes from verified facts
                |
                +--> Investigator LLM via Nightshift
                |    checklist, approved read requests, proposal, explanation
                |    new verified facts -> policy reevaluation
                |
                +--> Critic / validator (mandatory code)
                |      rejected -> at most one investigator revision
                |      unresolved -> honest no-credit failure/review path
                |      accepted -> eligible to attempt commit, not yet committed
                |
                v
       Transactional simulated decision service -> PostgreSQL
       current-state reread + policy/transition recheck + uniqueness
                |
                +--> committed decision, optional simulated credit, audit
                +--> post-commit H-MEM summary (separate success/failure status)
                v
       Analyst-visible result / review queue / public event trace
```

H-MEM is part of the **intended complete product**. The initial CLI milestone may run without memory while T09/T10 are unfinished; it must say so. This is a project-scope choice. A01 confirms H-MEM as one allowed Meterless engine; see the competition checklist for the current obligations.

### Who is an agent, and who is ordinary code?

| Component | Implementation in this plan | Owns | Not permitted |
|---|---|---|---|
| Orchestrator | Python workflow/state machine; not an extra LLM | Sequence, run state, time/tool/revision limits, tool dispatch and final service calls | Treat an unchecked model instruction as executable authority |
| Investigator | LLM role called through Nightshift | Small evidence plan, supported tool requests, recommendation and source-grounded rationale | Decide binding rules, access arbitrary SQL, directly commit or invent evidence |
| Critic/validator | Mandatory deterministic Python checks; optional separate LLM reviewer later | Schema, case/source scope, evidence/rule references, amounts, policy compliance, correction feedback | Override hard blocks or execute actions |
| Policy engine | Deterministic Python service | Versioned filing, evidence, settlement, amount and review rules | Infer new policy thresholds from prompts or expected labels |
| Retrieval tools | Backend read-only adapters over Zetaris | Authorized, time-visible authoritative records and verified history | Expose credentials, raw write access or expected-result fixtures |
| Action service | Transactional PostgreSQL-backed code | Recheck current state and atomically record sandbox effects/audit | Accept stale/unvalidated state or create duplicate effective credit |
| H-MEM adapter | Integration service, not an independent decision-maker | Persist/recall permitted source-linked context after verification | Replace ledger, current source facts or policy; allege fraud from memory alone |
| Analyst interface | CLI then thin UI | Display evidence, checks, proposals, final status and review queue | Create a second rule/write path or pretend sample calls are live |

A single Python application may contain all these modules; separate deployed services or separate models are not required by this proposal. The model's actual API/tool capabilities must be checked against the working integration before implementation.

### Minimal workflow contract

Implemented T01 types: `DisputeContext`, `PolicyResult`, `AgentProposal`, `CriticResult`, `CommitResult`, `RunState` in [`dispute-demo/app/schemas.py`](./dispute-demo/app/schemas.py). The [contract reference](./dispute-demo/docs/contracts.md) specifies fields, exact source-policy precedence/boundaries, workflow transitions, synchronization requirements and unresolved business lifecycle decisions. These are strict, immutable transport types with JSON conversion; they do not execute policy, validate factual support or write decisions.

`recommend_refund` maps explicitly to a new simulated `provisional_credit`; existing merchant refund/reversal movements are preserved. Non-credit outcomes (`decline`, `request_evidence`, `human_review`) have no amount/effect. Missing evidence uses categories rather than invented document IDs. Business outcomes, critic verdicts and persistence statuses are separate.

All stages carry the same dispute/snapshot/cutoff/policy/source-revision reference. A snapshot UUID is identity only; `source_revision=None` means freshness is unavailable and cannot support a successful commit result. The synchronization protocol uses a global source-revision guard shared by **all** relevant writers, including settlement inserts, evidence/policy changes and actions. T04 now implements the guarded PostgreSQL migration and tests it in isolated databases. Source policies define no lifecycle beyond generated `open` disputes; [T04 storage](./dispute-demo/docs/storage.md) defines append-only re-review and conservative duplicate scope without changing source status. T05 now validates under that guard in isolated PostgreSQL; shared deployment and verified coherent Zetaris reads remain pending.

Keep **business outcome** (credit, evidence request, decline, human review) separate from **execution status** (committed, reused, rejected, unavailable, failed). The critic can approve a proposal for commit, but only the database service can confirm persistence. A failed database call is not a saved review item.

### Trust boundaries and review behavior

- Source reads for investigation use the approved Zetaris path. Commit-time checks must reread authoritative state inside the PostgreSQL write transaction; an earlier Zetaris snapshot cannot provide that guarantee.
- The action service must use a synchronization/version-validation scheme shared by relevant source writers. Merely locking the dispute row does not protect against unrelated concurrent settlement inserts unless those writers participate in that scheme.
- Recheck the policy applicable under the documented date anchor, not blindly the newest version. Any changed authoritative fact that invalidates a proposal requires reevaluation or rejection.
- The investigator may request an allowlisted read. Application code validates the tool name/arguments and executes it; native tool-calling support is not assumed. New verified facts require a new policy evaluation.
- The critic is code-first. A valid source ID is necessary but does not by itself prove that a document supports the model's claim. Unresolved material contradictions should route to review rather than unsupported credit.
- Permit at most one proposal-correction pass for the MVP and explicit configured limits on tool calls, model calls and duration. On exhaustion, no automatic credit.
- Memory is recalled before final policy evaluation or causes reevaluation after source verification. Save final source-linked summaries after successful commit. Retry memory by decision ID; never repeat the action because a memory write failed.
- Evidence text and memory are case material, not trusted operational instructions. Do not let either change tool permissions or bypass validation.
- Keep non-credit decisions in the audit trail without creating monetary effects. Allow a later legitimate new-evidence review through the agreed lifecycle without permitting another effective credit.
- Display observable tool activity, cited facts, policy results and critique, not hidden model chain-of-thought. Label fault-injected proposals, mocks and sample responses truthfully.

## 4. Known implementation state

> **Verified baseline, 2026-10-26 — T00 / KAN-9.** Source at `a5ab88a` on `codex/dispute-investigation-agent`; exact commands, outcomes and NOT RUN checks are in the T00 completion record in `ROADMAP.md`. This supersedes the historical audit where fresh evidence exists; it does not complete T01–T13 or A01.

### Verified in the T00 audit

- Seeded synthetic generation, manifest/document/fixture validation and both generation tests pass using the existing Python 3.13.7 venv. The initial non-login shell selected Python 3.9.6 and produced two test errors; use the documented Python 3.10+ runtime. These tests validate data, not agent decisions.
- All nine existing Zetaris platform verification checks passed. The separate project PostgreSQL container is healthy; its public schema contains the six source tables plus `connection_probe`, with no decision/action/audit/review tables.
- The configured JDBC path passed `SELECT 1`, listed datasource `dispute` and Lightning databases `NY_TAXI` / `TPCDS_DB`, and ran all three existing verification queries using a temporary datasource-name correction. REST checks could not run because `ZETARIS_API_KEY` is unset; this did not prevent JDBC access.
- `dispute-demo/integration/get_dispute_context.py` retrieved `DP-0014`: one transaction, a completed 10,000-minor-unit capture, a completed 4,000-minor-unit refund, two evidence documents and eight v2 rules. The SQL applies visibility filters and selects policy by dispute opening date. This proves retrieval, not an approved policy result or persisted credit.
- The existing loader, source schema and read-only retrieval were inspected. The loader's `--apply` operation was NOT RUN; no data was reloaded or reset.
- GitHub now contains the tracked branch, and authenticated Jira access to KAN-9 in project `Open-Agent` was verified. Source/data bytes tested before publication were unchanged by that publication.

### Current unavailable checks and historical evidence

- `check_nightshift.py` failed authenticated model discovery with “Nightshift is unreachable or timed out” despite approved local networking. Chat inference is **NOT RUN**. The earlier audit's Nightshift 0.92.7 / `meterless/auto` / READY result is historical and was not reproduced. No actual responding model identity is established.
- The sandbox initially blocked JDBC networking; an approved retry passed. The overall preflight still exits 1 for two REST-only failures. Its initial “port closed” output must not be interpreted as a service outage.
- External dated progress reports are absent from this checkout. Authenticated HackOS requirements and deadlines remain unverified under A01.

### Verified in T01 (local contract checks only)

- Added six shared contracts and supporting source/recommendation types with strict IDs, UTC times, integer money, scope/version binding, explicit missing inputs and effect-free non-credit results.
- All 23 local tests pass: 21 contract tests plus the two existing generation tests. All 40 authored scenarios round-trip without changing fixture meaning; these are representation checks, not agent predictions. The synthetic-data validator also passes. Source policies, data, fixtures, generator and integrations are unchanged.
- The [contract reference](./dispute-demo/docs/contracts.md) records opening-date version selection, 30/45-day filing windows, inclusive 20,000 SGD-cent review boundary, ordered rule precedence, workflow protocol, stale-result invalidation and all-writer synchronization. Unspecified business lifecycle, broader ledger/evidence semantics, history rules and revision support remain explicit decisions for later tasks.
- Live Zetaris/PostgreSQL/Nightshift/H-MEM checks are NOT RUN for T01. Next recommended task is T02 / KAN-11; it is not started.

### Verified in T02 — typed reads, 2026-10-27

- [Typed tools and registry](./dispute-demo/app/tools.py) adapt the existing JDBC path into strict `DisputeContext`, separate customer-scoped history and current source-state reads. The registry accepts four named reads bound to one authorized dispute; extra arguments, arbitrary SQL and cross-case requests are rejected before connecting.
- [Retrieval](./dispute-demo/integration/get_dispute_context.py) preserves transaction `customer_id` and source metadata, left-joins evidence text and filters parsed UTC instants. Missing/unusable text stays as `content=None` with explicit issues. Missing, incomplete, malformed and unavailable results are distinct; query overflow is incomplete, not silently truncated.
- Live JDBC passed for DP-0014, DP-0019 and the DP-0033/DP-0034 policy boundary. DP-0014 has 1 transaction, 2 settlements, 2 evidence items and 8 v2 rules; its source customer CUST-008 has visible prior cases DP-0030 and DP-0017. Current source status and missing-case behavior passed. No source data was changed.
- Python 3.13.7: 50 root-suite tests pass (27 new retrieval, 21 contracts, 2 generation), 6 offline prototype critic tests pass and data validation passes. All 13 prototype tests collect; 7 external H-MEM tests were NOT RUN. Offline SQLite query tests are not live integration evidence.
- `source_revision=None` remains explicit; decision reads return `unsupported` without querying nonexistent storage. There is no coherent multi-read snapshot or commit freshness guarantee. Source dispute status/text is unversioned and cannot reconstruct past values. History is advisory and contains no inferred decision, credit or memory verification. See the [retrieval reference](./dispute-demo/docs/retrieval.md) for limits and commands.
- T02 added no policy implementation, action writes or memory operations. Its separately authorized closure verified KAN-11 Done with completion comment `10003`; publication preparation is recorded in the roadmap. T03 / KAN-12 is recommended next and not started. The dated prototype table below describes the earlier PR #4 inspection; this T02 entry supersedes its retrieval gap list.

### Verified in T03 — deterministic policy evaluation, 27 October 2026

- [Canonical policy evaluator](./dispute-demo/app/policy_engine.py) now returns bound `PolicyResult` with all four outcomes, ordered rule checks, citations, missing categories and an optional credit cap. The old [dictionary entry point](./dispute-demo/agent/policy_engine.py) delegates to it; no second evaluator remains.
- Exact supplied v1/v2 semantics, opening-date selection, first-terminal precedence, elapsed filing/review boundaries and primary-transaction completed balance are implemented. Unknown policy/currency, inconsistent ledger and unresolved input issues require review; no history threshold exists. No writes or model calls occur.
- Whole synthetic document templates/metadata establish bounded support; missing required text requests evidence, and unknown additional material requires review. Known T02 missing-text diagnostics are classified through evidence rules without weakening T01. See [policy interpretation and limits](./dispute-demo/docs/policy.md).
- 70 main tests (20 new policy tests covering all 40 authored cases), 6 offline critic regressions and data validation pass. After user-authorized startup of the existing stack, JDBC preflight, the read-only DP-0014 CLI and eight live case evaluations passed. All four outcomes, primary-balance/review boundaries and v1/v2 selection are verified. T03 is **DONE**. No source data was reloaded, reset or mutated; the stack is left running.
- Pure critic, canonical PostgreSQL actions, investigator/controller and memory integration remain outstanding. Recommended next implementation task is T06 / KAN-15, not started. No Jira edits or publication performed.

### PR #4 prototypes — inspected 2026-10-27, integration acceptance outstanding

[PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merged on 2026-10-26, adds nine files and modifies retrieval. The local clean checkout matched its merge commit `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`; no older source was restored. These are source observations, not new passing test or live-service claims.

| Existing source | Capability and integration gap | Owning tasks |
|---|---|---|
| [policy_engine.py](./dispute-demo/agent/policy_engine.py) | Executable dictionary-based evaluator exists. Adapt to canonical `DisputeContext`/`PolicyResult`; harden missing text, malformed input, amount semantics and support checks against source policies. | T03 |
| [critic.py](./dispute-demo/agent/critic.py) | Validation is combined with a local SQLite credit writer. Non-credit results return without durable decisions; no PostgreSQL source reread/revision guard. Extract a pure critic and centralize all four outcomes in the action service. SQLite uniqueness is not the T04/T05 acceptance guarantee. | T04–T06 |
| [resolver.py](./dispute-demo/agent/resolver.py) | Recalls memory, builds a deterministic proposal and calls the SQLite-writing critic. No Nightshift investigator, bounded canonical workflow or genuine no-memory mode; `remember=False` only disables saving. A later memory exception can obscure a successful credit response. | T07, T08, T10 |
| [memory_service.py](./dispute-demo/agent/memory_service.py) | Customer-scoped tags and advisory history exist. Stored `verified` tags are not authoritative revalidation; non-persisted non-credit validation can be saved as processed memory. Three claims is a prototype default, not a policy rule. | T09, T10 |
| [hmem_client.py](./dispute-demo/agent/hmem_client.py), [bridge](./dispute-demo/agent/hmem_bridge/server.ts), [manifest](./dispute-demo/agent/hmem_bridge/package.json) | Python/subprocess and TypeScript adapters exist. External reference/runner setup is not pinned or installed by the manifest; timeout, output/error handling and safe concurrent persistence need verification/hardening. | T09 |
| [get_dispute_context.py](./dispute-demo/integration/get_dispute_context.py) | Preserve PR #4's transaction `customer_id` addition and JDBC path. Still returns dictionaries, inner-joins evidence text, and lacks typed history, revision support and required metadata. | T02 |
| [critic tests](./dispute-demo/agent/tests/test_critic.py), [H-MEM tests](./dispute-demo/agent/tests/test_hmem_integration.py) | Separate from `dispute-demo/tests/`; bare runtime imports depend on test `sys.path` injection. Critic tests mock policy and use temporary SQLite; memory tests require an external reference. Source inspected only; NOT RUN here. | Affected integration tasks, T12 |

The 40 expected-result fixtures remain test-only authored answers. Shared contracts are implemented under `app/`; module locations under `agent/` are real prototypes, not absent components. Adapt/move each under its assigned task, preserve strict schemas and leave one canonical evaluator and one normal-runtime PostgreSQL action writer. No alternate SQLite bypass should survive that integration; do not delete or migrate local state implicitly.

T04 now supplies canonical PostgreSQL storage and a source-revision guard, tested only in isolated databases; its verified details follow below. The existing demo database was reinspected read-only and still has its original seven public tables, no storage migration. T05 now supplies the canonical action service with protected source/policy/critic validation, verified in isolated PostgreSQL. A structured Nightshift investigator, bounded controller, analyst UI and complete end-to-end/reset runner remain unimplemented. T04 resolves minimum re-review, conservative duplicate scope and fresh-write cutoff handling. T02 continues returning `source_revision=None` and unsupported decision reads until deployment, registration and read coherence are verified; successful commits may not use unknown revisions.

`registration.sql` and `verify.sql` use historical datasource `dispute_pg`; current setup/retrieval use `dispute`. The root has gitlinks without `.gitmodules`, so a fresh clone needs the onboarding/platform setup steps in `TEAM_SETUP.md`.

### Verified in T04 — PostgreSQL storage, 27 October 2026

- [Migration 001](./dispute-demo/db/migrations/001_decision_storage.sql) stores investigations, all four outcomes, exact request/proposal/source references, idempotency, automatic credit/review/audit sidecars and a durable review queue. Merchant settlement rows remain separate. Non-credit amounts are NULL; no credit effect is permitted.
- Global revision triggers and restricted unprivileged writer roles cover source and action mutations, including COPY/TRUNCATE and evidence text/policy changes. The initial loader refuses migrated databases. Administrative superusers remain trusted for DDL, not normal runtime credentials. No runtime login is granted writer membership by T04.
- [Lifecycle reference](./dispute-demo/docs/storage.md): preserve source status; append later non-credit/new-evidence evaluations with fresh identities/revision and a nonforking predecessor chain. Enforce one credit per dispute/primary transaction and reserve both linked charges against swapped duplicate-pair awards. No top-up/reversal/reissue. Later reviews remain possible; superseded queues remain in audit history.
- The storage cutoff guard rejects later authoritative transactions/settlements/evidence and future/pre-opening cutoffs. A latest revision cannot rescue a frozen cutoff that hides a refund. Historical evaluation stays read-only; T05 must validate an explicitly fresh context, policy and critic under the shared lock and reconcile identical request retries.
- **20 real PostgreSQL tests pass**, including migration preservation, permissions, rollback, source-writer blocking, all outcomes, duplicate scopes, new-evidence review, late refunds and review persistence after actual isolated-server restart. Root discovery: 90 tests, 70 passed/20 opt-in skips; the 20 ran separately with no skips. Six offline critic regressions and data validation pass.
- Shared source data/services were preserved: same seven tables and 42/54/40/81/81/16 counts; no control/action schemas in the demo DB. Test containers/volumes were removed. Source policies, data/fixtures, canonical schemas/evaluator and current retrieval are unchanged. No new live Zetaris/model/memory capability, action-service acceptance, Jira update or publication. Next recommended T06, not started.

### Verified in T06 — pure critic, 27 October 2026

- [Canonical critic](./dispute-demo/app/critic.py) accepts typed context/policy/proposal and returns a bound `CriticResult`. It checks structure, exact references, canonical reevaluation, permitted outcome/amount/currency, evaluated-rule citations, source-supported evidence and exact missing categories. Mandatory review excludes credit; ordinary permitted outcomes need no blanket approval.
- Rationale is restricted to `policy_rationale(policy)`, the deterministic evaluated-rule explanations. Arbitrary prose cannot be proved by IDs alone and routes to review. This conservative synthetic limitation and correction/error semantics are in [the critic reference](./dispute-demo/docs/critic.md); no T01 schema or source-policy changes.
- [Legacy critic](./dispute-demo/agent/critic.py) re-exports pure validation; `review_and_simulate` always reports unavailable with no effect. It cannot create/open a ledger or migrate/delete existing SQLite state. The resolver and memory prototypes remain unintegrated; T05/T08 will provide the canonical write workflow.
- 22 new critic tests cover all 40 authored cases and adversarial inputs, with I/O blocked and immutable inputs/results checked. Main suite: 112 collected, 92 passed, 20 PostgreSQL opt-in skips; 4 compatibility tests and data validation pass. Both critic modules import without path changes/service initialization; 11 prototype tests collect (7 external H-MEM tests NOT RUN). No live service checks, source mutations or migration were performed.
- Acceptance is read-only, including with null source revision. T05 must verify freshness and exact proposal/run binding under the shared PostgreSQL guard before any persistence; T08 owns run/revision/call budgets. A critic review verdict never creates a queue entry. Next: **T05 / KAN-14**, not started.

### Verified in T05 — atomic simulated decisions, 27 October 2026

- [Action service](./dispute-demo/app/action_service.py) accepts a strict complete `CommitRequest` and returns the existing `CommitResult`. It owns a fresh restricted Psycopg connection, holds the T04 global guard, rereads every current scoped source, compares facts and reevaluates the canonical policy/critic before writing. Source status must remain `open`; unknown/stale revisions and post-cutoff records are rejected.
- All four outcomes persist atomically with required audit/sidecars. Identical key/payload returns the original decision before stale checks; changed payload rejects. Fresh new keys still respect dispute/transaction/linked-pair uniqueness. A lost COMMIT acknowledgement returns unconfirmed failure and recovers with the original request. Acknowledged persistence survives cleanup errors. No model write tool, SQLite fallback, source-status mutation or memory write.
- [25 real PostgreSQL action tests](./dispute-demo/tests/test_action_service.py), all 20 storage tests and 93 offline tests pass together (138 total, zero skips); four compatibility tests and data validation also pass. Independent connections verify concurrent commits and source-writer exclusion; real trigger faults prove complete rollback. Seven external H-MEM tests were collected only. See [the action reference](./dispute-demo/docs/actions.md) and the roadmap log for commands, limits and dependency setup.
- Acceptance uses fresh test-only snapshots from isolated PostgreSQL. Existing shared database/credentials/registration remain unchanged; no runtime login is enabled. Investigation remains on the approved Zetaris path, whose null revision cannot commit. T08 must resolve deployment and verified uncached fresh reads before an end-to-end write flow. T07 / KAN-16 is recommended next, not started.

### Verified in T07 — Nightshift investigator, 27 October 2026

- [Investigator](./dispute-demo/app/investigator.py) makes a real bounded text-model turn and validates a strict JSON proposal/read envelope. Typed references/identities, scoped observations, canonical policy and one genuine critic correction are enforced. No read dispatch or writes occur; the controller retains budgets, reevaluation, uncertainty handling and persistence.
- [Transport](./dispute-demo/app/nightshift.py) reuses private configuration and the documented text API, with no native tools/schema assumption. A short-lived child enforces the total request deadline; redirects/proxies are disabled, payloads bounded and errors sanitized. No automatic retries or deterministic model fallback. Response reasoning fields are discarded.
- 16 model-stub tests and 12 transport tests pass, including five real loopback HTTP fixture tests. Full main suite: 166 collected, 121 passed, 45 PostgreSQL opt-in skips; four compatibility tests and data validation pass. PG code is unchanged and its T05 evidence remains dated, not rerun here. Seven H-MEM tests collect only.
- Opening the existing Nightshift app restored authenticated discovery. JDBC preflight passed; two REST-only missing-key failures remain. The [live read-only probe evidence](./dispute-demo/docs/evidence/t07-live-DP-0014.json) records actual Zetaris DP-0014 facts → model proposal → accepted pure critique for 6,000 SGD minor units. Requested `meterless/auto`; response reported `nvidia/nemotron-3.5-bolt-e4b`. This is returned metadata, not independent provider attestation. No hidden reasoning or expected labels were logged or prompted.
- No decision was persisted; source revision remains null. T08 must implement coherent fresh reads, deploy restricted action storage and own the bounded workflow. Nonempty model uncertainty prevents committing its proposal. Broader arbitrary rationale remains outside the T06 support vocabulary. The legacy resolver is explicitly labelled and remains unintegrated until T08.

### Verified in T08 — canonical bounded workflow, 27 October 2026

- [Controller](./dispute-demo/app/orchestrator.py), [CLI](./dispute-demo/app/main.py), [fresh snapshot adapter](./dispute-demo/app/fresh_tools.py), [bounded workers](./dispute-demo/app/runtime_io.py) and [recovery journal](./dispute-demo/app/journal.py) replace the prototype as the normal runtime. Defaults are four model requests, three reads including initial retrieval, 300 seconds total, and one critic correction. New reads invalidate earlier facts/observations and reevaluate policy; a new read during correction ends safely without resetting its budget. Uncertainty and unresolved critique cannot reach the writer.
- Migration 002 supplies a single PostgreSQL statement snapshot through a registered read-only Zetaris view. Every SELECT requires a verified direct scan; before/bundle/after revisions and a fresh source clock must agree. Historical T02 commands remain null-revision diagnostics. Investigation never reads directly from PostgreSQL; the writer's protected reread is internal commit validation.
- Migrations 001/002 are applied to the project sandbox, with unchanged fingerprints for all six source tables and a private pre-migration backup. A restricted `dispute_app` LOGIN has only action-writer membership; its DSN is private. Compose publishes project PostgreSQL only on `127.0.0.1:55432`; the metastore and existing Zetaris services are preserved. Four read views are registered. [Deployment receipt](./dispute-demo/docs/evidence/t08-deployment.json).
- The [live trace](./dispute-demo/docs/evidence/t08-live-workflow.json) records DP-0014 committing 6,000 SGD minor units as decision `b2d7a3ef-b7a7-4546-ac93-183a672ef41d`. Exact saved-request recovery returns the same decision/credit without a model/read call. A fresh run sees revision 5 and rejects `effective_credit_already_exists`. Shared totals remain one decision, credit and audit event; source rows are unchanged.
- Four earlier auto-route runs returned invalid prose and one advertised Lightning route was unavailable; all stopped before writes. Read-only inspection of installed Nightshift 0.92.7 identified the supported JSON-object path and tier-split control. The verified request uses JSON-object output, `tool_choice=none`, temperature 0 and tier splitting off; runtime semantic cache and answer-memory/scaffold injection are skipped. Local JSON/schema/reference/critic checks remain authoritative, and runtime review or reported native-tool execution is rejected. Requested `meterless/auto`, response label `nvidia/nemotron-3.5-bolt-e4b`; this label is not independent provider attestation.
- The labelled live fault demo overstated the model's credit by one minor unit. The critic requested one correction; that response failed proposal-schema validation and the controller stopped without another action or fabricated review. Tests additionally prove a successful correction with real isolated PostgreSQL and a scripted model.
- All 198 tests pass (52 real isolated PostgreSQL tests, five local HTTP fixtures, 141 other tests), plus four compatibility tests, import/AST/link checks and data validation. No application H-MEM recall/save, fixture fallback, SQLite action path or hidden reasoning. Exact requests are fsynced privately before action dispatch; uncertain commits recover only with the same request/key. Confirmed action results survive optional post-commit/trace-save failures. See the [workflow guide](./dispute-demo/docs/workflow.md).
- **NOT RUN:** actual H-MEM reference/save-restart-recall and authenticated HackOS requirements. Next: T09 / KAN-18; T10 still requires an explicit advisory-history scope decision or an approved exact versioned rule.

### T09 verified reference adapter — 27 October 2026

The [memory guide](./dispute-demo/docs/memory.md) documents the actual official
reference at `1742dec56a66e58eef9dda2d2b865823758ca8cd`, pinned Node/tsx dependencies,
and unchanged upstream source hashes. This is a deterministic reference with
mock embeddings, not a production engine. Competition approval remains A01.

The existing Python/TypeScript bridge now bounds subprocess output/time, hides
raw errors, partitions customers before retrieval/graph linking, and serializes
atomic state-plus-ledger publication under an OS lock. Typed committed summaries
retain decision/customer/dispute/source references, policy/revision and times;
analyst notes remain separate and unverified. Identical decision-ID retries reuse
memory; failures cannot invoke financial actions. The former resolver and its
three-claim default are retired; legacy state is preserved without migration.

Thirteen upstream conformance checks, ten smoke tests and the supplied add
example pass. Twelve real-reference adapter tests plus four compatibility checks
pass, including new Python/Node process recall, concurrent saves, lost-ack retry,
corrupt-state preservation and customer isolation. Main suite: 218 collected,
161 passed, 57 separately opt-in checks skipped; 20 new offline memory checks.
The saved T08 DP-0014/CUST-008 receipt was stored and recalled in a new Python
invocation with its original decision ID. This is saved-receipt evidence, not a
fresh source verification or another credit. See [evidence](./dispute-demo/docs/evidence/t09-reference-memory.json).

Live PostgreSQL/Zetaris/Nightshift and HackOS were NOT RUN for T09. T08's canonical
workflow remains explicitly `no_memory`; T10 owns fresh source verification and
integration and still needs its explicit advisory-scope acceptance decision.

### T10 verified advisory workflow — 27 October 2026

- The owner approved advisory history for the MVP, resolving T10's explicit scope gate. The [memory workflow](./dispute-demo/app/memory_workflow.py) reuses T09 and the current authoritative Zetaris snapshot adapter. Only cases already in source customer history can be read for verification; the model remains limited to its selected case.
- Up to five ranked candidates are checked against actual committed receipts, customer ownership, original IDs/reference/outcome, current global revision and selected-case cutoff. False/missing/future/cross-customer/superseded references and notes are ignored visibly. Repeated memories count as one case; recall is partial, never a complete claim count. A known source revision change stops the run for fresh investigation.
- Strict [advisory history](./dispute-demo/app/history.py) reaches policy and the proposal prompt without changing v1/v2 outcomes. Required source failures still block credit; no memory-only fraud finding or review hold is introduced. New model-requested reads invalidate prior verified history. Verification shares existing read/time budgets.
- Confirmed receipts alone produce final summaries. Memory pending/failed status is independent of decision persistence. `--retry-memory <trace.json>` rechecks the sibling request and actual Zetaris receipt, then saves by decision ID without an action callback. The CLI enables advisory memory by default; `--no-memory` disables it.
- Live DP-0017/CUST-008 recalled and source-verified the prior DP-0014 receipt, passed the critic and committed one synthetic 5,760-minor-unit credit. Its memory was stored and reused by a fresh Python invocation. Shared totals are now 2 decisions, 2 credits, 2 audits, 0 reviews, revision 10. All six source fingerprints and restricted login rights are unchanged. [Sanitized evidence](./dispute-demo/docs/evidence/t10-verified-memory.json).
- All 238 main tests pass, including 16 new offline memory workflow tests and 4 real PostgreSQL/pinned-reference tests with a scripted model. The separate 16 reference/compatibility tests and generated-data validation pass. JDBC passes; REST remains unconfigured. Authenticated HackOS is **NOT RUN** for T10. Next: T11 / KAN-20, the analyst view.

### Verified dataset snapshot

| Synthetic dataset | Records |
|---|---:|
| Disputes | 40 |
| Transactions | 42 |
| Settlement movements | 54 |
| Evidence metadata | 81 |
| Evidence text documents | 81 |
| Policy rules | 16 across two versions |

Counts agree between local validation and the live Zetaris verification queries. The dataset and expected-result fixtures were preserved.

### Verified in T11 — local analyst workbench, 2026-10-27

- [Local UI and guide](./dispute-demo/docs/analyst-ui.md) use the existing controller, critic and sole action service. Source facts, policy/citations, proposal, critic verdict, persistence, verified advisory history and independent memory status are visible. Only persisted pending reviews are queued; there is no manual approval/writeback workflow.
- Durable private UI operation IDs, an OS lock, exact journal association and saved-request recovery preserve retry safety across double-clicks, refresh and restart. Memory-only retry cannot call an action. Display inventory uses bounded direct Zetaris reads and a revision guard; its queue/history join is checked one-to-one against independently read queue membership.
- Live DP-0008 committed one review with no credit; DP-0014 recovery reused its original credit. DP-0020 schema/rationale failures and DP-0030's verified history followed by schema refusal were visibly not persisted. Prompt clarifications do not repair invalid output or weaken safety checks. Shared totals: 3 decisions, 2 credits, 3 audits, 1 queued review, revision 14; source fingerprints unchanged.
- 260 main tests and 16 reference/compatibility tests pass with no skips; 18 investigator tests pass after the final prompt clarification. UI PostgreSQL tests cover all four outcomes with a scripted model. [Sanitized evidence](./dispute-demo/docs/evidence/t11-analyst.json) and [screenshot](./dispute-demo/docs/evidence/t11-analyst.png) distinguish actual browser checks from scripted tests. Desktop-width visual inspection and authenticated HackOS NOT RUN. T12 owns isolated reset/replay; the UI has no shared reset.

### Verified in T12 — complete failure matrix and isolated reset, 2026-10-27

- [Reliability guide](./dispute-demo/docs/reliability.md) maps acceptance risks to existing and new tests. `python -m demo.verify` collects both roots in separate processes; `--integrations` enables real disposable PostgreSQL, pinned H-MEM and local HTTP fixtures. All 267 main/16 reference-compatibility checks pass without skips. Offline collection explicitly reports 73/12 integration skips; 19 runtime packages import without path changes or service initialization.
- `python -m demo.replay --reset-isolated-demo` deliberately rehearses twice in fresh disposable database/memory/journal namespaces. Default is preview only, no user-supplied target accepted. Exact container ownership is verified before cleanup. Shared source/actions/memory remain outside reset scope. Both cycles produce eight decisions/four credits/one pending review, verify real reference history, correct one injected amount fault and reject duplicates. Source hashes/bytes are preserved.
- [Evidence](./dispute-demo/docs/evidence/t12-verification.json) separates scripted model/direct isolated PostgreSQL reads from real reference and database behavior. New UI-composed tests prove provider/data failure, actual trigger rollback and lost-review-ack recovery. Shared state stays 3 decisions/2 credits/3 audits/1 review at revision 14; restricted login unchanged. Fresh live Zetaris/Nightshift/browser/HackOS checks NOT RUN. No normal application logic, source policies or contracts changed. Next: A01, then T13.

### Verified in A01 — authenticated competition requirements, 2026-10-27

- [Competition checklist](./docs/competition.md) records nine opened official/authenticated sources. Required deliverables are a public repository, deck, 1–4 minute workflow video with audio and sponsor/provenance explanations. Deadline: **27 October 2026 23:45 UTC / 28 October 07:45 SGT**. Zetaris, a Meterless engine and primary Nightshift inference are required; Cursor is optional. Named Nemotron evidence is an additional award condition.
- H-MEM guidance supports code-controlled approval and storage/retrieval as a starting scope. The current reference uses mock embeddings; no exact-revision approval is claimed. The one-model investigator plus deterministic critic remains accurately described; the video guide's two-agent wording is an unresolved interpretation, not a reason to invent another model.
- New Zetaris scoring guidance asks for three datasources and a USL. This project has one PostgreSQL datasource and no USL; T13 must disclose that scoring gap. The signed-in member cannot manage submissions; platform leader Rachel Anne Liew must verify the actual form, upload/access limits and final receipt. Separate detailed Track 3 page access is also unresolved. These precise blockers satisfy A01's audit gate, not submission completion. No runtime or policy change occurred.

### Verified in T13 — reproducible delivery package, 2026-10-27

- [Submission package](./docs/submission/README.md) maps every authenticated R1–R10 item to an artifact or precise blocker. It includes an eight-slide editable deck, a 226.15-second 1080p narrated MP4, transcript/captions, architecture, sponsor/provenance explanation and prepared project text. Actual UI captures and dated live evidence are distinguished from scripted isolated rehearsals. Native deck structure/import/render checks and video decode/audio/browser playback checks passed.
- An anonymous clone of `937b642` installed fresh pinned Python/Node/H-MEM dependencies without copying private configuration. Both explicit replay cycles passed with unchanged sources. Fresh offline verification collected 267 + 16 tests: 194 + 4 passed, 73 + 12 explicit integration skips, zero errors/failures. T12's complete integration matrix remains separately dated; it was not rerun for this documentation/media-only change.
- The current live DP-0029 run used Zetaris and Nightshift but failed proposal-schema validation without persistence. DP-0014 exact-request recovery reused its original decision/credit and memory summary. The final read-only database check retained six source fingerprints, restricted action login, 3 decisions/2 credits/3 audits/1 review and revision 14. The owned preview server was stopped; no shared service was restarted or reset.
- [Package evidence](./dispute-demo/docs/evidence/t13-package-checks.json) records security, clean setup, media and access checks. B1 leader-only form/upload/final receipt, B2 two-agent interpretation, B3 detailed challenge access, B4 exact-reference endorsement and owner provenance confirmation remain explicit. One datasource/no USL is disclosed. Completing the repository gate does not claim organizer acceptance, an upload or a submitted entry.

### Nightshift response-contract follow-up — 27 October 2026

The user authorized diagnosis and hardening after the recorded T13 schema failure.
The investigator now sends a compact draft with full JSON Schema; application
code supplies identities/reference/revision and the canonical policy explanation.
Recommendations, citations, missing requirements and uncertainty remain model
outputs subject to the unchanged critic and transaction checks. Citation schema
bounds come from current evaluated policy checks, not fixtures. Safe field/code
and known provider-error diagnostics survive in traces without raw responses,
unknown property names or private reasoning. No schema downgrade or extra retry.

The old prompt passed a fresh DP-0029 reproduction, so the original recording's
exact field error remains unknown. Intermediate drafts exposed unrelated-document
citations; the final case-bound schema yielded a critic-accepted decline at source
revision 14 without persistence. Final verification passed 274 main and 16
reference/compatibility tests with zero skips; shared source hashes, restricted
role and 3 decisions/2 credits/3 audits/1 review remained unchanged.
Actual Nightshift JSON Schema validation passed;
provider-side enforcement remains labelled unverified. A uniqueItems capability
probe failed with HTTP 502, so uniqueness remains local. See the
[investigator guide](./dispute-demo/docs/investigator.md) and
[attempt evidence](./dispute-demo/docs/evidence/nightshift-schema-followup.json).

## 5. Repository paths and reading entry points

The paths below were checked for existence in the current checkout on 2026-10-26. This verifies their presence, not their behavior or live integrations. Inspect source before relying on APIs or fields. All paths are relative to the repository root.

| Path | Expected role |
|---|---|
| `AGENTS.md` | Repository-wide agent entry point and mandatory pre-execution reading order |
| `CLAUDE.md` | Claude Code entry point referencing the same root reading workflow |
| `agent.md` | Shared operating rules and task-specific reading map |
| `context.md` | Canonical project brief and evidence-qualified implementation status |
| `ROADMAP.md` | Priorities, acceptance gates, and verified work log |
| `TEAM_SETUP.md` | Environment and local setup notes |
| `Open_Agent_Hackathon_2026_Complete_Handbook.md` | Historic hackathon planning and requirements notes; verify current portal rules |
| `dispute-demo/INSTRUCTIONS.txt` | Data-generation instructions; adapt its old local path to this checkout |
| `getting-started/AGENTS.md` | Scoped instructions for bundled Zetaris onboarding tools |
| `zetaris-platform/README.md` | Local Zetaris platform/container setup |
| `dispute-demo/scripts/generate_synthetic_data.py` | Seeded synthetic data and source field definitions |
| `dispute-demo/scripts/validate_synthetic_data.py` | Synthetic-data validation |
| `dispute-demo/tests/test_generation.py` | Existing generation/reproducibility tests |
| `dispute-demo/tests/fixtures/expected_results.json` | **Test-only** expected results — never feed into live agent context |
| `dispute-demo/policies/synthetic_policy_v1.md` | Fictional policy version 1 |
| `dispute-demo/policies/synthetic_policy_v2.md` | Fictional policy version 2 |
| `dispute-demo/integration/get_dispute_context.py` | Approved Zetaris read-only retrieval |
| `dispute-demo/integration/check_nightshift.py` | Nightshift connectivity probe |

**Important:** Future file paths in `ROADMAP.md` are proposals; do not report them as implemented until they are created and tested. This context document should not contain credentials, local absolute home-directory paths, or sensitive configuration values.

## 6. Non-negotiable implementation invariants

1. **Synthetic only.** No real payment operations, bank secrets, or production customer information.
2. **Policy in executable code.** Version selection, filing windows, evidence checks, review thresholds, priorities, and amount limits come from the existing **synthetic policy source**, not invented in prompts.
3. **Authoritative record checks.** Model-provided IDs are untrusted until matched to actual retrieved, time-visible evidence and rules.
4. **Integer money units.** Store and calculate amounts in minor units; account for completed settlement movements according to the actual synthetic policy.
5. **No double credit.** Enforce idempotency and one effective simulated credit per dispute at the **database** level, with safe handling of parallel requests.
6. **Commit-time validation.** In the write transaction, recheck current state, relevant settlements, policy, and allowed transitions; reject stale proposals.
7. **Safe failure.** On unavailable data/model, invalid JSON, bad evidence, or unresolved critic failure, record/recommend review or evidence collection — **never credit by default**.
8. **Memory is advisory.** Verify H-MEM recall against current source records. Repeat history is contextual unless an explicit versioned policy makes it binding; no prototype count or memory tag establishes fraud or required review.
9. **Auditable trace.** Record observable tool use, cited sources/rules, proposal, critic feedback, and committed result. Do not expose model-private chain-of-thought.
10. **Test/production separation.** Never load `expected_results.json` into runtime investigation tools, prompts, or orchestration.
11. **Honest demo modes.** Label offline/sample fixtures; do not imply they used live Zetaris or Nightshift.
12. **Credentials stay private.** Keep `.env` and keys out of commits, examples, screenshots, and model prompts; provide redacted `.env.example` placeholders only.

## 7. Demo story to build toward

A strong minimum demonstration shows:

1. **Supported case:** read actual synthetic data via Zetaris → policy evaluation → Nightshift proposal → critic validation → single recorded simulated outcome.
2. **Repeat processing:** submit the same dispute again; demonstrate no second effective simulated credit (also test two concurrent attempts).
3. **Critic catches a mistake:** provide or simulate a malformed/excessive/unsupported proposed action; critic blocks it and leads to one corrected proposal or safe human review.
4. **Memory case (when integrated):** a later investigation retrieves H-MEM source IDs and verifies history; show advisory context or a separately approved policy-required review, without inventing a history threshold.
5. **Policy-version comparison (time permitting):** identical decision logic honors the correct effective synthetic policy based on defined date rules.

Choose actual dispute IDs only after inspecting fixture and policy files; do not assume a specific outcome for `DP-0014`.

## 8. Open questions — resolve from source, not guesses

- A01 confirms the cutoff and main requirements; resolve B1–B4 in the [competition checklist](./docs/competition.md) before claiming full eligibility or submission.
- Preserve the named-model distinction: returned Nightshift metadata is evidence, not independent responder attestation; Nemotron-specific award requirements are separate.
- What are the exact policy predicates, precedence, effective-date rules, allowed transitions, and amount semantics in the repo files?
- H-MEM is an allowed engine and official references are supported; no explicit endorsement of the exact pin was found. T10 source verification and advisory acceptance are complete.
- Which fixture IDs best demonstrate supported credit, duplicate prevention, critic correction, and version boundaries?
- The owner approved T10 advisory history. A future binding history policy requires a new explicit versioned decision. T04/T05 lifecycle, protected validation and retries and T08 shared deployment/live freshness have passed their gates.
- PR #4 source is inspected at `76db772`; recheck source and live services when later tasks begin. The integration checklist is in `ROADMAP.md`.

## 9. Source-of-truth and maintenance rules

- **For project intent, goals, trust boundaries, and agreed architecture:** start here in `context.md`.
- **For current next tasks, owners, priorities, and completion evidence:** consult `ROADMAP.md` using IDs T00–T13 and A01. The dated progress reports are historical snapshots, not parallel task queues.
- **For implemented behavior:** inspect the checked-out code, migrations, actual configuration, and passing/failing tests. Documentation never overrides them.
- **For exact fictional policy semantics:** read the versioned files under `dispute-demo/policies/` and the generator; do not invent numbers from this summary.
- **For competition/submission rules:** use current authenticated HackOS instructions over older handbooks or public summaries.
- **For session rules:** start with the root `AGENTS.md` (also referenced by `CLAUDE.md`), which requires `context.md` → `ROADMAP.md` → `agent.md` and applicable task-specific sources before execution. Use one assigned roadmap task at a time and stop after it; explicit user requests outside the roadmap retain their own scope.

**When to update `context.md`:** after a verified architectural decision, scope change, rule/terminology clarification, important integration change, or change in what is actually built. Date the change and cite relevant code paths/test commands in the note. Move completed tasks in `ROADMAP.md` only after their acceptance evidence is recorded.

### Context change log

| Date | Change and verification status | Evidence / file reference |
|---|---|---|
| 2026-10-27 | T07 accepted with 121 tests, four compatibility checks/data validation and a real critic-accepted Nightshift proposal; full-roadmap sequential publication now authorized | `app/investigator.py`, `app/nightshift.py`, `docs/investigator.md`, live evidence and T07 work log |
| 2026-10-27 | T05 atomic action service accepted: 138 tests including 45 real PostgreSQL; 4 compatibility tests/data validation; shared deployment still pending | `app/action_service.py`, `tests/test_action_service.py`, `docs/actions.md`; T05 work log |
| 2026-10-27 | T06 pure critic accepted: 92 offline/4 compatibility tests and data validation; SQLite execution retired; no live checks | `app/critic.py`, `tests/test_proposal_critic.py`, `docs/critic.md`, legacy shim; T06 work log |
| 2026-10-27 | T04 storage accepted in isolated PostgreSQL: 20 integration tests, 70 offline/6 prototype regressions and data validation; shared source unmigrated | `db/migrations/001_decision_storage.sql`, `tests/test_decision_storage.py`, `docs/storage.md`, guarded loader; T04 work log |
| 2026-10-27 | T03 typed policy evaluator accepted: 70 main tests, 6 critic regressions, data validation and 8 live JDBC cases; authorized existing-stack startup resolved initial blocker | `app/policy_engine.py`, `agent/policy_engine.py`, `tests/test_policy_engine.py`, `docs/policy.md`; T03 work log |
| 2026-10-27 | T02 typed case/history/state reads accepted with 50 root tests, 6 offline critic tests and separate live JDBC checks; source revision/decision support remain unavailable | `app/tools.py`, `integration/get_dispute_context.py`, `docs/retrieval.md` under `dispute-demo/`; T02 work log in `ROADMAP.md` |
| 2026-10-27 | Section 7 documentation alignment: recorded selective review/advisory history, mapped PR #4 prototypes and outstanding acceptance; no runtime tests or live application checks | PR #4 / local `76db772`; `ROADMAP.md` alignment log and new `docs/planning/JIRA_POST_MERGE_CHANGESET.md` preview |
| 2026-10-26 | Established baseline context from progress audit; infrastructure working, agent workflow pending | `Open_Agent_Hackathon_Progress_2026-10-26.md` (external/source report) |
| 2026-10-26 | Installed the four root instruction/context files, verified referenced repository paths, and documented scoped reading requirements; no runtime capabilities re-verified | `AGENTS.md`, `agent.md`, this section's path inventory, and the documentation setup entry in `ROADMAP.md` |
| 2026-10-26 | Planning clarification only: one investigator, code-first critic, Python controller; memory remains in full target; stable task IDs added | Supplied context/roadmap review; no live code verification or tests in this revision |
| 2026-10-26 | Merged the Jira-tracked kit, preserved repository-specific reading links and prior work history, and added the root Claude Code entry point; no runtime tasks completed | `Open_Agent_Hackathon_Jira_Tracked_Context_Kit.zip`, `AGENTS.md`, `agent.md`, `CLAUDE.md`, and `ROADMAP.md` |

| 2026-10-26 | T00 audit: validated data and 2 generation tests, 9 platform checks, live JDBC retrieval/counts and public-table inventory; Nightshift discovery failed and inference NOT RUN; official H-MEM reference located; T01 not started | `ROADMAP.md` T00 / KAN-9 completion record; source baseline `a5ab88a` |

## Jira issue tracking (supplied kit dated 2026-10-26)

The supplied kit reports that the work queue is tracked in Jira project `KAN` (`My Data Science Team`) at https://luijoel24.atlassian.net, with five hackathon epics `KAN-4`–`KAN-8` and tasks `KAN-9`–`KAN-23`. The exact imported mapping is in `ROADMAP.md`. Importing this kit does not itself verify the current account connection, issue existence, or live status. These tickets represent **planned work, not completed implementation**. Keep the repository code/tests authoritative for real status; do not mistake Jira status or issue descriptions for proof of functionality.

**Live verification, 2026-10-26:** Authenticated access confirmed KAN-9, `[T00] Verify current repository baseline`, under KAN-4 in project `Open-Agent`. The issue was To Do when read and moved to In Progress for this audit. The T00 completion record and Jira evidence document its acceptance; no other issue's status or implementation was verified or changed. The kit's former project display name is historical.

**Closure revalidation, 2026-10-26:** A fresh authenticated read confirmed KAN-9 already has status and resolution Done (resolved at 18:13:45 +08:00), with the original completion evidence attached. At checkout `8883e5c`, data validation and both generation tests passed again on Python 3.13.7; application/data/integration paths match the audited `a5ab88a` baseline. Live integrations were NOT RUN in this follow-up, so the dated service results above remain unchanged. See the closure revalidation entry in `ROADMAP.md` for exact commands.

**Read-only alignment snapshot, 2026-10-27:** Jira returned all 20 labelled issues with no further page. KAN-9/KAN-10 remain Done; KAN-11–KAN-23 and epics KAN-4–KAN-8 are To Do; all are unassigned with no issue links. Exact current descriptions and proposed description deltas are saved in the newly created [Jira change preview](./docs/planning/JIRA_POST_MERGE_CHANGESET.md). Jira edits are pending explicit approval; none were applied. No task status changed locally.

**Approved Jira follow-up, 2026-10-27:** the user explicitly approved that preview. Applied only the 13 description updates to KAN-11–KAN-23, including the specified KAN-14 retry correction. Immediate pre-edit reads matched the snapshots; individual read-backs and a final 20-issue audit verified content and unchanged summaries, statuses, assignees, task IDs, epic membership, labels and links. KAN-4–KAN-10 retained their descriptions and updated timestamps; T00/T01 remain Done. The preview file now records the application receipt. No implementation/policy decision was completed, no application integrations were checked, and T02 remains unstarted.

**T02 closure, 2026-10-27:** after typed retrieval acceptance, the user separately authorized Jira updates and publication to `origin/main`. Fresh 50-test and 6-test offline runs plus data validation passed. Completion comment `10003` records implementation and dated live JDBC evidence; KAN-11 status and resolution are verified Done. Its description, summary, assignee, parent, labels and links are unchanged; no other issue was edited. Live application checks were NOT RUN again for this follow-up. T03 remains unstarted.

**T03/T04 closure, 2026-10-27:** after their implementation acceptance, the user separately authorized Jira completion. KAN-12 and KAN-13 are verified Done with completion comments `10004` and `10005`; descriptions, summaries, assignees, parents, labels and links are unchanged. GitHub confirms T03 PR #5 and T04 PR #6 merged to `main` (merge commits `b64c21d18df1ccd8cc93e507eeb937ea5fb7e7c1` and `7e7faaaf81877448c63f9778dc36d194c4a88529`). This supersedes earlier publication/Jira snapshots without changing acceptance scope: the T04 migration was tested only in isolated databases, and shared deployment/coherent reads plus T05/T06 integration remain pending. Application/live checks were NOT RUN again for this administrative follow-up. Local closure documentation is uncommitted; T06 is recommended and not started.

**T06 closure, 27 October 2026:** KAN-15 is verified Done with completion comment `10006` containing fresh 92-main/4-compatibility test evidence and explicit skipped/NOT RUN limits. Its summary, description, assignee, parent, labels and links are unchanged; no other issue was edited. The user authorized the completed T06 commit/push directly to `origin/main`. Next task is T05, not started.

**T05 closure, 27 October 2026:** KAN-14 is verified Done with completion comment `10007`, recording 138 passing tests (45 real PostgreSQL), four compatibility tests and data validation. Protected Jira fields remain unchanged. The user authorized the completed task's commit directly to local `main`. Shared deployment/coherent Zetaris reads remain pending; next is T07, not started.

**T07 closure, 27 October 2026:** KAN-16 is Done with completion comment `10009`, covering 121 passing tests, four compatibility tests/data validation and the actual critic-accepted Nightshift proposal. T05 commit `29eb6ae` is now pushed to `origin/main` (KAN-14 follow-up `10008`). The expanded full-roadmap goal authorizes a direct completion commit/push per task; next is T08.

**T08 closure, 27 October 2026:** KAN-17 is Done with acceptance comment `10011`. The gate includes 198 passing tests, actual persisted/reused live processing, ordinary duplicate refusal and a labelled fault that fails safely after one correction attempt. Next under the authorized full-roadmap goal is T09 / KAN-18 after the completion commit/push.

**T09 closure, 27 October 2026:** KAN-18 is Done with acceptance comment `10013`. Actual pinned-reference persistence, restart/isolation/concurrency and source-linked summaries are accepted. T10 remains the next task under the full-roadmap goal, after this completion commit/push.

**T10 closure, 27 October 2026:** KAN-19 is Done with owner advisory approval `10016` and acceptance `10017`. Source-verified later-case processing, actual reference restart/retry and independent memory failure handling passed. Next under the authorized full-roadmap goal: T11 / KAN-20 after completion publication.

### T14 additive reviewer module — 27 October 2026

The user authorized T14–T16 sequentially, with Jira tracking first. T14 adds a
separately invoked Nightshift Evidence & Risk Reviewer with strict bounded
feedback and application-owned run/proposal/ContextRef binding. It has no tools,
writes or policy authority. Ten new offline tests pass; the full offline matrix
is 210 main + 4 compatibility passed, with 74 + 12 integration/reference skips.
Live Reviewer inference is NOT RUN at this milestone. The normal controller
remains unchanged until T15; source policies, critic and writer are preserved.
See [Reviewer guide](./dispute-demo/docs/reviewer.md) and ROADMAP T14–T16 entries.

## T15 two-agent controller (27 October 2026)

Normal CLI/UI now require separate Investigator and Reviewer Nightshift calls.
Every proposal passes the pure critic before review. One shared correction token
can respond to either role; the revised proposal must pass both again. Reviewer
escalation, malformed feedback, mismatched identity or missing service prevents
writing. Six shared model calls by default; source and atomic action protection
remain unchanged. Exact-request recovery calls neither agent. The full isolated
regression passed 298 application and 16 reference tests, zero skips. Live
two-agent verification is still pending T16; this supersedes earlier one-model
runtime descriptions without retroactively relabelling historical evidence.

## T16 live two-agent evidence (27 October 2026)

Two distinct Nightshift role calls now have real observed evidence. DP-0020
completed Investigator proposal, pure critic acceptance, independent Reviewer
acceptance and the same-proposal final gate before committing an evidence
request. Decision `fa29319b-8749-4f55-a9a2-42f5d1c8a9c6`; no credit. Exact recovery
returned reused with zero model calls. Both roles returned the same Nemotron
label; separate prompts/invocations do not imply separate model providers.
DP-0029 demonstrated four real calls and one correction, then safe refusal after
a second Reviewer objection. That objection appears overly conservative about
first-terminal filing-window precedence. It is preserved as a known limitation.

Live T16 used no-memory mode. Two-agent verified memory and all four outcomes
passed two isolated scripted-model rehearsal cycles with real PostgreSQL and
pinned H-MEM. Full matrix: 298 application + 16 reference tests, no skips. Fresh
clone of runtime commit b6d71f2 reproduced both cycles with independent dependency
setup and no private configuration. The UI exposes role feedback, revision,
model metadata and final persistence separately. Six source fingerprints and
restricted role are unchanged; shared totals are 4 decisions, 2 credits, 4 audits,
1 review, revision 17.

New eight-slide deck and 3:18 narrated video are in the current submission index;
historical one-agent media remains unchanged. Distinct live agent roles address
the implementation gap behind B2, not formal organizer approval. One PostgreSQL
datasource/no USL, exact-reference endorsement, contributor declarations and
leader-only portal submission/receipt remain explicit limitations. This feature
branch was pending review at acceptance. The user subsequently authorized
publication of the completed T14–T16 work to main; see the roadmap publication log.
