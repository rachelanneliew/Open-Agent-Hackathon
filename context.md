# Project Context — Synthetic Card-Dispute Resolution Agent

> **Canonical project brief for all coding agents and collaborators.**
> Read this file **at the start of every task**, then consult [`ROADMAP.md`](./ROADMAP.md) for the active priorities. Read the actual code, policies, schemas, tests, and HackOS instructions before making implementation claims.
>
> **Context last reviewed:** 2026-10-27, documentation alignment against PR #4 and local HEAD `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`. T00 and T01 remain complete; merged prototypes have integration acceptance outstanding. **Evidence basis:** current source inspection plus the dated T00 source/live checks and T01 local contract checks in `ROADMAP.md`. Application tests and live application integrations were NOT RUN for this alignment. Nightshift discovery failed in T00; its earlier READY result remains historical. Jira status and file presence do not prove implementation acceptance.

## 1. Project identity

| Field | Context |
|---|---|
| Project | Open Agent Hackathon 2026 — synthetic card-dispute resolution agent |
| Intended track | Track 3 — Reasoning Architecture; verify the precise challenge requirements in HackOS |
| Primary user | Card-dispute operations analyst |
| User input | A synthetic `dispute_id` |
| Desired output | Evidence-grounded recommendation, policy-rule citations, critic/validation result, and recorded **simulated** outcome or human-review route |
| Development tools | Python, PostgreSQL, Zetaris (JDBC), Nightshift; H-MEM planned; Codex, Claude Code, and Cursor are **optional coding tools**, not part of runtime architecture |
| Safety boundary | Entirely synthetic records, policies, and actions — **no real bank/payment integrations** |

### One-sentence product definition

An analyst selects a dispute; the system retrieves relevant synthetic records through Zetaris, applies deterministic policy rules in code, requests a structured AI recommendation through Nightshift, validates it with a critic, safely records a sandbox-only decision, and uses H-MEM to recall source-linked context in later investigations.

### Success criteria for the first working version

1. A selected dispute can be retrieved through the **actual Zetaris read path**.
2. Executable Python policy checks determine allowed actions and hard blocks without relying on the LLM.
3. Nightshift produces a structured, evidence-linked proposal; a critic rejects invalid references, amounts, or disallowed actions.
4. A PostgreSQL transaction records the approved **simulated** result; repeated and concurrent attempts cannot create duplicate simulated credits.
5. The result exposes evidence IDs, policy-rule IDs, validation feedback, and action status.
6. The intended complete product demonstrates a real H-MEM save/recall sequence with verified source references and persistence. The first CLI slice may precede it; actual competition obligations remain to be checked in A01.
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

T10 retains an explicit acceptance decision: confirm advisory MVP scope or approve a separately versioned binding rule with count, lookback, anchor, reasons, qualifying outcomes, exclusions and precedence. This does not block T02 or this documentation pass; it does not mark the original history-rule acceptance requirement complete.

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

H-MEM is part of the **intended complete product**. The initial CLI milestone may run without memory while T09/T10 are unfinished; it must say so. This is a project-scope choice, not a claim that the authenticated challenge requires H-MEM. Confirm official obligations in A01.

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

All stages carry the same dispute/snapshot/cutoff/policy/source-revision reference. A snapshot UUID is identity only; `source_revision=None` means freshness is unavailable and cannot support a successful commit result. The documented future protocol uses a global source-revision guard shared by **all** relevant writers, including settlement inserts, evidence/policy changes and actions. No guard, migration or concurrency protection is implemented yet. Source policies define no business lifecycle beyond generated `open` disputes; later action tasks must resolve that explicitly.

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

No canonical PostgreSQL decision/action/audit/review migrations or action service, source-revision guard, structured Nightshift investigator, bounded controller, analyst UI or complete end-to-end/reset runner is implemented in this checkout. Live database contents were NOT RUN/reinspected here; the seven-table inventory remains dated T00 evidence. Lifecycle/re-review, cross-dispute duplicate scope and historical replay versus current-state commit semantics remain T04/T05 decisions. T02 may honestly return `source_revision=None` and unsupported decision reads before T04; successful commits may not use unknown revisions.

`registration.sql` and `verify.sql` use historical datasource `dispute_pg`; current setup/retrieval use `dispute`. The root has gitlinks without `.gitmodules`, so a fresh clone needs the onboarding/platform setup steps in `TEAM_SETUP.md`.

### Located H-MEM reference and current adapter limits

The handbook's [Meterless Engines](https://meterless.ai/engines.html) link resolved to the official H-MEM specification and reference under [Meterless/Meterless/engines/hmem](https://github.com/Meterless/Meterless/tree/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem), inspected on 2026-10-26. That reference uses deterministic mock embeddings and optional JSON persistence; it is not a production runtime library. The historical pinned links are in the T00 work log. PR #4 now supplies the project bridge/client above, but does not pin the external installation. No installation, reference execution or save/restart/recall was performed in this alignment; reproducibility and persistence acceptance remain T09 work. Competition approval is still subject to A01.

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

- What does the authenticated HackOS Track 3 challenge explicitly require, and what is the actual submission cutoff?
- Is a named NVIDIA/Nemotron responder mandatory, and how can its identity be recorded during the demo?
- What are the exact policy predicates, precedence, effective-date rules, allowed transitions, and amount semantics in the repo files?
- How should the located official H-MEM specification/reference be adapted to this Python project, and can the actual adapter prove save/restart/recall in T09? Competition approval remains unverified.
- Which fixture IDs best demonstrate supported credit, duplicate prevention, critic correction, and version boundaries?
- T10: confirm advisory history acceptance scope or approve an exact versioned binding rule; T04/T05: settle lifecycle, cross-dispute duplicate scope and historical replay/fresh commits. No such new policy or lifecycle is approved by this documentation pass.
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
