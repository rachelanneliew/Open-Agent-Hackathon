# Project Context — Synthetic Card-Dispute Resolution Agent

> **Canonical project brief for all coding agents and collaborators.**
> Read this file **at the start of every task**, then consult [`ROADMAP.md`](./ROADMAP.md) for the active priorities. Read the actual code, policies, schemas, tests, and HackOS instructions before making implementation claims.
>
> **Context last reviewed:** 2026-10-26 (Jira-tracked planning kit merged into this checkout). **Evidence basis for runtime claims:** the team's progress audit dated 2026-10-26, not a fresh integration run. Repository paths and the agent reading workflow were checked locally; this does not re-verify the reported runtime baseline. Jira mappings are supplied by the kit and are not proof of implementation. Update the factual status below whenever code or tests change.

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
- **Human review** — escalate ambiguous, risky, repeated-pattern, or otherwise policy-required cases.

### Out of scope for the MVP

Real chargebacks, real bank API access, production authentication, production fund movements, live customer data, model training during demonstrations, and optional fraud-risk scoring unless the core workflow is already complete.

### Distinctions that must not be blurred

- A settlement **refund**, **capture**, or **reversal** is an existing movement in synthetic transaction data.
- A newly recorded **simulated provisional credit** is a separate dispute-action record.
- A `duplicate_charge` dispute is about two charges; **idempotency** concerns accidentally applying a decision/credit *twice to the same dispute*.
- `recommend_refund` and `recommended_refund_minor` appear in existing generation/fixture terminology. Define and test an explicit compatibility mapping if those fields are still present; never silently equate a merchant refund with provisional credit.
- Agent proposals are **recommendations**, not executed decisions or financial ledger entries.

## 3. Target workflow and component responsibilities

> **Proposed architecture, not implementation status.** The baseline evidence in section 4 is unchanged. The task-by-task build order is in ROADMAP.md under stable IDs T00–T13 and A01.

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

Suggested contract names: `DisputeContext`, `PolicyResult`, `AgentProposal`, `CriticResult`, `CommitResult`, `RunState`. Define exact fields from the real repository in T01, not from this summary. Include IDs, source snapshot/revisions, policy identity, evaluation cutoff, cited evidence/rules and action-specific integer amounts.

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

> The following is an **audit snapshot as of 2026-10-26**. Do not assume it is still true after subsequent commits. Verify against the repository and update this section with evidence.

### Reported as working / verified in the audit

- Docker Desktop and the local Zetaris platform configured; its nine platform verification checks passed.
- Separate project PostgreSQL database running; seeded data loaded; row counts checked.
- SQL/JDBC readiness and project datasource registration in Zetaris succeeded.
- `dispute-demo/integration/get_dispute_context.py` reads a dispute and linked transactions, settlement movements, evidence text, and policy rules through Zetaris. It applies evaluation-time visibility and policy-version selection by dispute opening date.
- Nightshift M1–M4 0.92.7 was running; `dispute-demo/integration/check_nightshift.py` successfully received `READY` via `meterless/auto`.
- Reproducible synthetic generator, validation script, two generation tests, and expected-result fixtures exist.

### Not established as implemented in the audit

- Runnable deterministic policy enforcement.
- Database-backed decision/action writing and concurrent duplicate prevention.
- Structured Nightshift investigator, critic correction loop, or full orchestration.
- Actual H-MEM read/write integration or persistence proof.
- Analyst dashboard, complete application setup/README, or repeatable end-to-end demonstration.
- Exact responding NVIDIA model behind the successful `meterless/auto` probe.
- Authenticated HackOS deadline, mandatory technology details, and final upload requirements.

### Reported dataset snapshot

| Synthetic dataset | Records |
|---|---:|
| Disputes | 40 |
| Transactions | 42 |
| Settlement movements | 54 |
| Evidence metadata | 81 |
| Evidence text documents | 81 |
| Policy rules | 16 across two versions |

The audit says `DP-0014` was retrieved with a **10,000 minor-unit capture** and **4,000 minor-unit completed refund**. This proves retrieval, **not** a final policy decision for `DP-0014`.

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
8. **Memory is advisory.** Verify H-MEM recall against current source records; repeated claims warrant review according to policy, not an automatic fraud finding.
9. **Auditable trace.** Record observable tool use, cited sources/rules, proposal, critic feedback, and committed result. Do not expose model-private chain-of-thought.
10. **Test/production separation.** Never load `expected_results.json` into runtime investigation tools, prompts, or orchestration.
11. **Honest demo modes.** Label offline/sample fixtures; do not imply they used live Zetaris or Nightshift.
12. **Credentials stay private.** Keep `.env` and keys out of commits, examples, screenshots, and model prompts; provide redacted `.env.example` placeholders only.

## 7. Demo story to build toward

A strong minimum demonstration shows:

1. **Supported case:** read actual synthetic data via Zetaris → policy evaluation → Nightshift proposal → critic validation → single recorded simulated outcome.
2. **Repeat processing:** submit the same dispute again; demonstrate no second effective simulated credit (also test two concurrent attempts).
3. **Critic catches a mistake:** provide or simulate a malformed/excessive/unsupported proposed action; critic blocks it and leads to one corrected proposal or safe human review.
4. **Memory case (when integrated):** a later investigation retrieves H-MEM context with source IDs; source records confirm history before a human-review recommendation.
5. **Policy-version comparison (time permitting):** identical decision logic honors the correct effective synthetic policy based on defined date rules.

Choose actual dispute IDs only after inspecting fixture and policy files; do not assume a specific outcome for `DP-0014`.

## 8. Open questions — resolve from source, not guesses

- What does the authenticated HackOS Track 3 challenge explicitly require, and what is the actual submission cutoff?
- Is a named NVIDIA/Nemotron responder mandatory, and how can its identity be recorded during the demo?
- What are the exact policy predicates, precedence, effective-date rules, allowed transitions, and amount semantics in the repo files?
- What is the approved H-MEM package/reference implementation and persistence behavior?
- Which fixture IDs best demonstrate supported credit, duplicate prevention, critic correction, and version boundaries?
- Which components already exist in later commits beyond the 2026-10-26 progress audit?

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
| 2026-10-26 | Established baseline context from progress audit; infrastructure working, agent workflow pending | `Open_Agent_Hackathon_Progress_2026-10-26.md` (external/source report) |
| 2026-10-26 | Installed the four root instruction/context files, verified referenced repository paths, and documented scoped reading requirements; no runtime capabilities re-verified | `AGENTS.md`, `agent.md`, this section's path inventory, and the documentation setup entry in `ROADMAP.md` |
| 2026-10-26 | Planning clarification only: one investigator, code-first critic, Python controller; memory remains in full target; stable task IDs added | Supplied context/roadmap review; no live code verification or tests in this revision |
| 2026-10-26 | Merged the Jira-tracked kit, preserved repository-specific reading links and prior work history, and added the root Claude Code entry point; no runtime tasks completed | `Open_Agent_Hackathon_Jira_Tracked_Context_Kit.zip`, `AGENTS.md`, `agent.md`, `CLAUDE.md`, and `ROADMAP.md` |

## Jira issue tracking (supplied kit dated 2026-10-26)

The supplied kit reports that the work queue is tracked in Jira project `KAN` (`My Data Science Team`) at https://luijoel24.atlassian.net, with five hackathon epics `KAN-4`–`KAN-8` and tasks `KAN-9`–`KAN-23`. The exact imported mapping is in `ROADMAP.md`. Importing this kit does not itself verify the current account connection, issue existence, or live status. These tickets represent **planned work, not completed implementation**. Keep the repository code/tests authoritative for real status; do not mistake Jira status or issue descriptions for proof of functionality.
