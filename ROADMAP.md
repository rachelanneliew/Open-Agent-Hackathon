# Task Roadmap — Synthetic Card-Dispute Resolution Agent

> **Canonical work queue.** Read [`context.md`](./context.md) first, then [`agent.md`](./agent.md).
> **Revision:** task-based plan, 26 October 2026; T00 baseline audit and T01 shared contracts completed on 26 October 2026. The completion records below distinguish source inspection, passing local/live checks, failed checks, and NOT RUN checks.
> **Next roadmap task:** T02 / KAN-11, only when assigned. T00 / KAN-9 and T01 / KAN-10 are DONE against their acceptance gates; T02–T13 and A01 remain NOT_STARTED.
> **Agent entry point:** complete the reading in [`AGENTS.md`](./AGENTS.md) before execution. A specific user request takes precedence; a documentation update does not authorize starting another task.

## 1. What changed from the earlier plan

The previous roadmap used different numbers in its summary board and detailed tickets. It also bundled investigator, critic and orchestration into one large ticket. This revision replaces that task numbering with stable IDs T00–T13 and administrative task A01.

The architecture is clarified, not claimed as implemented: one investigator LLM, one mandatory deterministic critic/validator and one Python workflow controller. A separate LLM critic or manager is not needed for the initial build. H-MEM remains part of the intended complete product, although the first working CLI slice can precede it. Exact competition obligations remain unverified until A01.

Keep the dated `Open_Agent_Hackathon_Progress_2026-10-26*.md` reports as historical evidence. Do not treat their older ticket numbers or copy-ready all-in-one policy prompt as the active task queue. The T00 completion record below now provides current-checkout evidence for the baseline and explicitly identifies unavailable checks.

## 2. How to execute this roadmap

Give the coding assistant **one task ID at a time**. It must inspect prerequisites, implement only that task, run relevant tests, update this file and stop. A dependency that is missing is a blocker to report, not permission to implement every prerequisite silently.

Use statuses `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`. DONE requires recorded acceptance evidence; writing code is not enough. Mark unavailable live checks NOT RUN. A local stub test does not prove a live integration or PostgreSQL concurrency guarantee.

**Recommended first sequence:** T00 -> T01 -> T02 -> T03. This produces a source-backed deterministic evaluator before any model can suggest an action. Then complete T04–T08 for a safe end-to-end CLI. Complete T09–T11 for the intended memory-backed analyst demonstration, and T12–T13 for delivery. A01 runs alongside development. T09's reference integration may be checked early to expose access/API blockers.

Every task includes its own tests. T12 is cross-component testing, not the first time testing begins.

## Jira tracking (supplied kit dated 2026-10-26)

The supplied kit reports that the Jira issues below were created in project `KAN` (`My Data Science Team`) under the label `open-agent-hackathon`, with existing generic `KAN-1`–`KAN-3` issues left unchanged. These mappings are imported records; the document update itself does not verify live Jira access or current issue status. Jira describes planned work; the repository and passing tests remain the truth of implementation status. Do not mark Jira issues Done automatically from this document.

| Epic | Jira issue | Tasks |
|---|---|---|
| Setup, contracts and retrieval | [KAN-4](https://luijoel24.atlassian.net/browse/KAN-4) | T00, T01, T02, A01 |
| Policy and safe actions | [KAN-5](https://luijoel24.atlassian.net/browse/KAN-5) | T03, T04, T05 |
| Investigator, critic and workflow | [KAN-6](https://luijoel24.atlassian.net/browse/KAN-6) | T06, T07, T08 |
| H-MEM and analyst interface | [KAN-7](https://luijoel24.atlassian.net/browse/KAN-7) | T09, T10, T11 |
| Reliability and submission | [KAN-8](https://luijoel24.atlassian.net/browse/KAN-8) | T12, T13 |

| Roadmap ID | Jira task |
|---|---|
| T00 | [KAN-9](https://luijoel24.atlassian.net/browse/KAN-9) |
| T01 | [KAN-10](https://luijoel24.atlassian.net/browse/KAN-10) |
| T02 | [KAN-11](https://luijoel24.atlassian.net/browse/KAN-11) |
| T03 | [KAN-12](https://luijoel24.atlassian.net/browse/KAN-12) |
| T04 | [KAN-13](https://luijoel24.atlassian.net/browse/KAN-13) |
| T05 | [KAN-14](https://luijoel24.atlassian.net/browse/KAN-14) |
| T06 | [KAN-15](https://luijoel24.atlassian.net/browse/KAN-15) |
| T07 | [KAN-16](https://luijoel24.atlassian.net/browse/KAN-16) |
| T08 | [KAN-17](https://luijoel24.atlassian.net/browse/KAN-17) |
| T09 | [KAN-18](https://luijoel24.atlassian.net/browse/KAN-18) |
| T10 | [KAN-19](https://luijoel24.atlassian.net/browse/KAN-19) |
| T11 | [KAN-20](https://luijoel24.atlassian.net/browse/KAN-20) |
| T12 | [KAN-21](https://luijoel24.atlassian.net/browse/KAN-21) |
| T13 | [KAN-22](https://luijoel24.atlassian.net/browse/KAN-22) |
| A01 | [KAN-23](https://luijoel24.atlassian.net/browse/KAN-23) |

**Working convention:** Assign one dependency-ready roadmap task and provide its Jira link. When Jira tracking actions are authorized, mark that assigned issue In Progress; after implementation, require exact test commands/results and changed paths, update the repo documents, then move the issue to Done only after acceptance verification. Do not transition issues merely because this kit was imported. Jira links are not secret credentials. Keep team members unassigned until ownership is agreed.

## 3. Task board

| ID | Task | Dependencies | Status |
|---|---|---|---|
| T00 | Verify the current repository baseline | None | DONE |
| T01 | Define shared contracts and exact policy semantics | T00 | DONE |
| T02 | Expose narrow case and history retrieval tools | T01 | NOT_STARTED |
| T03 | Implement deterministic policy evaluation | T01, T02 | NOT_STARTED |
| T04 | Create sandbox decision, action and audit storage | T01 | NOT_STARTED |
| T05 | Implement atomic simulated decision recording | T03, T04 | NOT_STARTED |
| T06 | Build the mandatory critic and validator | T02, T03 | NOT_STARTED |
| T07 | Implement the investigator through Nightshift | T02, T03, T06 | NOT_STARTED |
| T08 | Wire the bounded workflow and command-line runner | T02, T03, T05, T06, T07 | NOT_STARTED |
| T09 | Verify and wrap the actual H-MEM integration | T00, T01; may run in parallel with T02–T08 | NOT_STARTED |
| T10 | Integrate verified memory and repeat-history review | T02, T03, T08, T09 | NOT_STARTED |
| T11 | Build the thin analyst view and review queue | T08; memory display depends on T10 | NOT_STARTED |
| T12 | Run cross-component failure tests and repeatable reset | T08, T10, T11 for the intended complete demo; feature-specific tests run earlier | NOT_STARTED |
| T13 | Package the evidence-backed demo and submission | T12, A01; documentation can be drafted alongside earlier tasks | NOT_STARTED |
| A01 | Confirm authenticated HackOS requirements | None; run alongside development | NOT_STARTED |

## 4. Milestones and dependency order

| Milestone | Required tasks | Demonstrable result |
|---|---|---|
| Source-backed rule checker | T00–T03 | A real retrieved context gets deterministic rule results without Nightshift |
| Safe write boundary | T04–T05 | Atomic simulated recording, tested retry and concurrent duplicate prevention |
| First working agent | T06–T08 plus prerequisites | Retrieve -> policy -> proposal -> critic/correction -> safe commit -> CLI trace |
| Intended complete product | T09–T11 plus prerequisites | Verified persistent memory and analyst-facing case/review display |
| Submission-ready demonstration | T12–T13 and A01 | Repeated safe runs, accurate documentation and verified required artifacts |

T04 can start after T01 while T02/T03 are developed. T06 can be tested with crafted proposals before the investigator exists. T09 can be explored after T00/T01. Parallel contributors must use the same contracts, separate task branches where appropriate and integrate tested changes; multiple contributors do not imply multiple deployed agents.

Do not silently remove a chosen feature when shortening scope. Record any scope decision in context.md and check A01 before omitting a required feature.

## 5. Individual build tasks

### T00 — Verify the current repository baseline

**Phase:** Foundation  
**Status:** DONE  
**Depends on:** None  
**Deliverable:** A factual baseline and a source-backed list of gaps; no application redesign.

**Read first:** context.md, this roadmap, agent.md, existing integrations, policies, generator, fixtures and tests. The dated progress reports are external historical sources and are not currently present in this checkout; record that limitation and consult them when available without treating their absence as proof that local code is missing.

**Work:**

- [x] Inspect the current tree and working changes. Reuse working modules; do not reinstall platforms or overwrite uncommitted work merely because the old report lists gaps.
- [x] Run the existing data-validation and generation tests. Run the existing Zetaris and Nightshift checks only when their configured services are available; inspect their actual arguments first.
- [x] Record what is implemented, what is only defined in data or documentation, and what could not be tested. Locate the approved H-MEM reference/specification without guessing a package or API.
- [x] Map already-completed work to the stable task IDs below using actual code and test evidence. Record dependencies, missing source policy detail and unavailable services.

**Acceptance gate:** Baseline commands and actual results are recorded. Unavailable integration checks are explicitly NOT RUN, not passed. No pending feature is marked complete from prose alone.

**Verified 2026-10-26:** Data validation and 2 generation tests passed on Python 3.13.7; all 9 platform checks and live JDBC verification passed. Nightshift discovery failed (configured endpoint unreachable or timed out); inference is NOT RUN. See the T00 completion record for exact commands, source gaps, and the H-MEM reference. Completion records the baseline, not completion of the planned application.

**Closure revalidation, 2026-10-26:** Authenticated Jira read confirmed KAN-9 already has status and resolution Done. Data validation and both generation tests passed again at `8883e5c`; application/data/integration paths are unchanged from the audited `a5ab88a` baseline. Live services were NOT RUN in this closure follow-up; earlier integration results remain dated audit evidence.

**Not in this task:** No policy implementation, refactor, new infrastructure, database reset or UI.

**Suggested paths/artifacts:** ROADMAP.md work log; context.md only for verified factual corrections. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T01 — Define shared contracts and exact policy semantics

**Phase:** Foundation  
**Status:** DONE

**Depends on:** T00  
**Deliverable:** Typed data contracts plus an explicit mapping between settlement movements, recommendations, decisions and simulated actions.

**Read first:** Existing schemas, synthetic_policy_v1.md, synthetic_policy_v2.md, generator, test-only expected_results.json and get_dispute_context.py.

**Work:**

- [x] Define or reuse DisputeContext, PolicyResult, AgentProposal, CriticResult, CommitResult and RunState. Implemented in `dispute-demo/app/schemas.py` with strict supporting types and JSON conversion.
- [x] Resolve legacy recommend_refund/recommended_refund_minor terminology. Preserve merchant refunds and reversals as source movements; explicitly map only the intended new action to simulated provisional credit.
- [x] Specify IDs, currency, integer minor units, evaluation cutoff, policy selection anchor, source revision/snapshot information, source references and allowed outcome/status vocabulary. Distinguish business outcome from execution status such as committed, reused, rejected, unavailable or failed.
- [x] Derive policy thresholds, rule precedence, filing boundaries and status transitions from source files. The contract reference documents workflow transitions and records absent business lifecycle rules as open decisions; source policies and fixtures are unchanged.
- [x] Specify invalidation of a stale proposal and the write-side synchronization contract. All writers that can change relevant dispute/settlement state must participate in the chosen locking or version-validation scheme. The documented global revision guard is a requirement for T02/T04/T05, not an implemented lock.
- [x] Represent missing evidence by requirement/category when no document exists, not by a fabricated evidence ID. Define credit amounts only for credit actions and keep non-credit records effect-free.

**Acceptance gate:** Contract tests reject malformed IDs/amounts/outcomes and represent existing scenarios without changing their meaning. A documented transition/precedence mapping and unresolved questions are available.

**Not in this task:** No new policy numbers, LLM calls, migrations or action execution.

**Implemented artifacts:** [schemas.py](./dispute-demo/app/schemas.py), [test_schemas.py](./dispute-demo/tests/test_schemas.py), [contract reference](./dispute-demo/docs/contracts.md) and updated [context.md](./context.md). Acceptance evidence is in the T01 work log below.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T02 — Expose narrow case and history retrieval tools

**Phase:** Foundation  
**Status:** NOT_STARTED  
**Depends on:** T01  
**Deliverable:** Typed, read-only tools over the working Zetaris integration.

**Read first:** Existing integration/get_dispute_context.py, connection configuration names, source tables and T01 contracts.

**Work:**

- [ ] Wrap or extend existing case retrieval rather than replacing the JDBC/Zetaris path. Return linked transactions, completed and pending settlement movements with statuses, evidence and applicable policy.
- [ ] Add narrowly scoped retrieval for verified customer history, current dispute state and existing decisions as the actual tables become available. Do not claim decision reads are live before the T04 migration is applied and the required read registration exists.
- [ ] Enforce case/customer scope and evaluation-time visibility. Include relevant source IDs and revision information needed for later validation.
- [ ] Distinguish not-found, incomplete data and service failure; do not return an empty successful case on a connection failure.
- [ ] Expose an allowlisted tool registry with validated arguments. Models may request permitted reads, but only application code executes the requests. Keep raw SQL, credentials and expected-result fixtures inaccessible to the runtime model.

**Acceptance gate:** Unit tests cover scoping, future-record filtering and failure modes. A live case can be retrieved through Zetaris when available, with live versus stubbed evidence clearly recorded.

**Not in this task:** No arbitrary SQL tool, direct model database access, source mutation or simulated action writes.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/tools.py, dispute-demo/tests/test_tools.py; extend the existing integration module where appropriate. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T03 — Implement deterministic policy evaluation

**Phase:** Foundation  
**Status:** NOT_STARTED  
**Depends on:** T01, T02  
**Deliverable:** A pure policy evaluator that returns allowed outcomes, rule results, constraints and source-linked explanations.

**Read first:** Exact versioned policies, T01 contracts, T02 context format and test-only fixtures.

**Work:**

- [ ] Implement evaluate_policy(context, evaluation_time) without model calls. Select the version applicable under the source policy date rule; do not substitute the newest policy simply because it is available.
- [ ] Implement written filing-window, evidence, amount, settlement-integrity, precedence and human-review checks. Calculate amounts from authoritative movements in integer minor units according to the actual policy.
- [ ] Return rule IDs, source evidence, missing requirements, allowed/blocked outcomes and credit limit or reason that no amount can be safely calculated.
- [ ] Use verified history, not raw H-MEM text, for any history-dependent rule. Reevaluate after any newly verified evidence changes the case context.
- [ ] Test all applicable existing fixture scenarios and explicit boundaries. Treat fixture disagreements as a discrepancy to investigate rather than permission to rewrite expected outcomes.

**Acceptance gate:** Policy tests pass with Nightshift disabled. An actual Zetaris context can be evaluated with auditable rules. Missing or contradictory facts never default to credit.

**Not in this task:** No LLM enforcement, runtime expected-results lookup, ledger writes or invented history threshold.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/policy_engine.py, dispute-demo/tests/test_policy_engine.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T04 — Create sandbox decision, action and audit storage

**Phase:** Controls  
**Status:** NOT_STARTED  
**Depends on:** T01  
**Deliverable:** A tracked PostgreSQL migration with enforceable uniqueness and traceable non-credit decisions.

**Read first:** Current project database schema, migration conventions and T01 action/status contracts.

**Work:**

- [ ] Create or reuse storage for investigation/decision records, simulated credit effects, audit events and review-queue status. Keep these separate from source settlement refunds.
- [ ] Define a stable request idempotency key and a separate business constraint that permits at most one effective simulated provisional credit per dispute in the MVP sandbox.
- [ ] Allow a later legitimate review after a request-for-evidence outcome when new evidence arrives, without permitting another credit. Do not treat every previous non-credit decision as permanent closure.
- [ ] Persist policy/source references, proposal identity and committed execution state. Non-credit outcomes must not create a money-effect row.
- [ ] Apply migration tests to an isolated test database. Preserve the source dataset and keep any live/sample state explicitly separated.

**Acceptance gate:** Migration is reproducible in a test database. Constraint tests block a second effective credit and permit valid non-credit lifecycle records. No production or shared source data is reset.

**Not in this task:** No LLM workflow or claim that uniqueness alone proves all commit-time safety.

**Suggested paths/artifacts:** Proposed: dispute-demo/db/migrations/, dispute-demo/tests/test_decision_storage.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T05 — Implement atomic simulated decision recording

**Phase:** Controls  
**Status:** NOT_STARTED  
**Depends on:** T03, T04  
**Deliverable:** One backend write service that validates and commits allowed sandbox decisions safely.

**Read first:** T01 synchronization/transition contract, T03 evaluator, T04 storage and actual source-state schema.

**Work:**

- [ ] Implement a narrow commit_simulated_decision interface callable by the orchestrator, not by model tools.
- [ ] In one database transaction, validate the request, lock/reload relevant authoritative state, select the applicable policy using its documented date anchor and reevaluate binding checks before writing.
- [ ] Reject stale source versions, changed settlements, invalid status transitions and disallowed amounts. A lock on a dispute row alone is not sufficient unless relevant source writers follow the same synchronization protocol; implement and test the documented protocol.
- [ ] Commit decision, optional simulated effect and required audit event atomically. Only report committed after commit succeeds. On a lost acknowledgement, retry the same idempotency key and return the existing result.
- [ ] Keep provisional credit, evidence request, decline and human-review outcomes distinct. If the database is unavailable, return not committed; do not pretend a human-review queue entry was saved.

**Acceptance gate:** Real PostgreSQL integration tests use independent transactions/connections. A valid case commits once; retries reuse it; two simultaneous attempts produce at most one credit; rollback and state/settlement changes cause no partial or stale effect.

**Not in this task:** No real payment, model write tool, memory write inside the decision transaction or mocked-only claim of concurrency safety.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/action_service.py, dispute-demo/tests/test_action_service.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T06 — Build the mandatory critic and validator

**Phase:** Agent workflow  
**Status:** NOT_STARTED  
**Depends on:** T02, T03  
**Deliverable:** A code-first review gate that accepts, requests correction or routes an unsupported proposal to review.

**Read first:** T01 AgentProposal/CriticResult, T02 sources, T03 PolicyResult and fixture scenarios.

**Work:**

- [ ] Validate structure, supported outcome, amount/currency, policy version, context revision, cited rule IDs and time-visible evidence IDs.
- [ ] Check binding policy constraints, human-review requirements and source scope. A real evidence ID alone does not prove the evidence supports a claim; use structured corroboration where available and route unresolved substantive contradictions to review.
- [ ] Return structured feedback with failed checks, required evidence or corrections, and whether a bounded revision is permitted. The critic does not execute actions.
- [ ] Test crafted invalid proposals: invented/cross-case evidence, future evidence, excessive credit, ignored policy blocks, stale snapshots and unsupported conclusions.
- [ ] Keep any future LLM semantic reviewer separate. It may add concerns but cannot override a deterministic rejection or approve an action independently.

**Acceptance gate:** Invalid proposals are rejected in deterministic tests, valid source-backed proposals pass, and no critic path writes a credit. These tests do not need Nightshift.

**Not in this task:** No requirement for a second LLM, independent critic service deployment or action execution.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/critic.py, dispute-demo/tests/test_critic.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T07 — Implement the investigator through Nightshift

**Phase:** Agent workflow  
**Status:** NOT_STARTED  
**Depends on:** T02, T03, T06  
**Deliverable:** A reasoning agent that proposes a supported outcome and can request approved evidence.

**Read first:** Existing check_nightshift.py and actual supported client/API, T01 schemas, T02 tools and T06 feedback.

**Work:**

- [ ] Reuse working authentication and connection conventions. Confirm the actual supported structured-response/tool interface; do not assume an API feature from the connectivity probe.
- [ ] Give the investigator case facts, deterministic policy results and authorized source-linked context. Include a small investigation-plan/checklist in this role rather than adding a separate manager LLM.
- [ ] Accept either a typed request for an allowlisted read tool or a typed final proposal. If native tool calling is unavailable, use an explicit structured request envelope validated and executed by the orchestrator.
- [ ] Require outcome, proposed amount when relevant, evidence/rule IDs, uncertainty or missing requirements, and a concise source-grounded rationale. Do not request or expose hidden chain-of-thought.
- [ ] Handle malformed output, timeouts and unsupported tool requests without side effects. Treat evidence documents and recalled text as untrusted case material, not operational instructions.
- [ ] Record requested route and actual responding provider/model only when returned or independently evidenced. Do not label meterless/auto as proof of a particular model.

**Acceptance gate:** Stubbed tests cover schema failures, unauthorized tool requests and correction feedback. A separately labelled live Nightshift test returns a usable proposal when available. Expected-result fixtures never enter prompts.

**Not in this task:** No arbitrary SQL, direct writes, hard-policy overrides, separate planner agent or claimed model identity without evidence.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/investigator.py, dispute-demo/tests/test_investigator.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T08 — Wire the bounded workflow and command-line runner

**Phase:** Agent workflow  
**Status:** NOT_STARTED  
**Depends on:** T02, T03, T05, T06, T07  
**Deliverable:** The first working end-to-end investigation with an observable audit trail.

**Read first:** All tested interfaces from T01–T07 and the repository entrypoint conventions.

**Work:**

- [ ] Implement a Python workflow controller: retrieve -> evaluate -> investigate -> validate -> commit -> display. The controller, not an LLM, controls transitions and write access.
- [ ] Execute only validated allowlisted tool requests. Merge newly verified facts into context and rerun the policy evaluator before validating a proposal based on them.
- [ ] Use at most one proposal-correction pass for the MVP. Define explicit tool-call, timeout and total-run budgets in configuration; no endless retries or loop resets.
- [ ] On unresolved critique or unavailable required facts, construct an honest no-credit error/review outcome. Persist a review decision only when the write service confirms it. Never relabel failed persistence as saved.
- [ ] Add a CLI accepting a real synthetic dispute ID. Show facts, rules, proposal, critic feedback and commit status; differentiate reused results from new simulated effects.
- [ ] Record a public event trace with source and rule IDs, versions, actions and errors. Use scripted faulty proposals only in explicitly labelled fault-injection tests/demos.

**Acceptance gate:** A live Zetaris + Nightshift case reaches a persisted sandbox result; reprocessing causes no extra credit; a faulty proposal is corrected once or routed safely. Unit/mocked runs are clearly distinguished from live integration evidence.

**Not in this task:** No dashboard requirement, autonomous agent swarm, unlimited loop or claim of memory use before T10.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/orchestrator.py, dispute-demo/app/main.py, dispute-demo/tests/test_orchestrator.py, dispute-demo/tests/test_end_to_end.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T09 — Verify and wrap the actual H-MEM integration

**Phase:** Memory and presentation  
**Status:** NOT_STARTED  
**Depends on:** T00, T01; may run in parallel with T02–T08  
**Deliverable:** A tested adapter to the selected real H-MEM implementation, with source-linked persistence.

**Read first:** Approved H-MEM specification/reference example discovered in T00 and current installed configuration.

**Work:**

- [ ] Run the supplied reference example and applicable tests. Record the actual supported save/recall/persistence interface; do not guess method names or substitute a similarly named package.
- [ ] Expose a project adapter for allowed summary storage and relevant recall. Include source case/decision IDs, timestamps, policy version and provenance.
- [ ] Keep final committed summaries separate from unverified model text. Do not store credentials, unnecessary personal data or fabricated facts.
- [ ] Test save -> process restart -> recall against the real implementation. Mark dictionary/mocked tests as mocks, not H-MEM integration.
- [ ] Define retries keyed to a committed decision ID and visible storage status. A memory write failure must never cause the financial-action service to run again.

**Acceptance gate:** Actual H-MEM save/recall is demonstrated after restart with source references, or the task remains BLOCKED with exact missing dependency/access evidence.

**Not in this task:** No H-MEM-as-ledger, invented API or completed memory claim from in-process storage.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/memory_adapter.py, dispute-demo/tests/test_memory_adapter.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T10 — Integrate verified memory and repeat-history review

**Phase:** Memory and presentation  
**Status:** NOT_STARTED  
**Depends on:** T02, T03, T08, T09  
**Deliverable:** A later case uses relevant memory, verifies it against source records and applies the actual history rule.

**Read first:** H-MEM adapter, authoritative customer-history tools, actual policy history rule and orchestrator.

**Work:**

- [ ] Recall permitted context before the final policy/proposal stage, then resolve its source references through approved authoritative retrieval. Raw memory must not alter eligibility by itself.
- [ ] Pass verified history into policy evaluation. If no repeated-claims threshold is defined in the policy, record the gap and obtain an explicit synthetic-policy design decision rather than guessing a count.
- [ ] Demonstrate how verified relevant history affects human review without labelling the customer fraudulent merely because claims repeat.
- [ ] After a successful decision commit, save its permitted source-linked summary. Report pending/failed memory persistence separately from decision success; retries reuse the decision ID.
- [ ] Test stale/incorrect memory and missing source references. When memory is unavailable, continue only if required authoritative facts and policy gates are still satisfied; otherwise fail safely without credit.

**Acceptance gate:** A second investigation visibly recalls and verifies a prior record, honors a source-defined review rule, and remains safe with false/stale/missing memory. Persistence survives restart.

**Not in this task:** No automatic fraud finding, memory-defined policy, duplicate action during memory retries or unsupported rule threshold.

**Suggested paths/artifacts:** Proposed: changes to dispute-demo/app/orchestrator.py, dispute-demo/app/memory_adapter.py, dispute-demo/app/policy_engine.py as needed; dispute-demo/tests/test_memory_workflow.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T11 — Build the thin analyst view and review queue

**Phase:** Memory and presentation  
**Status:** NOT_STARTED  
**Depends on:** T08; memory display depends on T10  
**Deliverable:** A simple analyst-facing page over the tested workflow, not a second implementation.

**Read first:** The CLI/orchestrator interface, stored decision/review data and existing UI conventions.

**Work:**

- [ ] Add dispute selection and Investigate, plus source facts, policy results, investigator recommendation, critic feedback and final persisted status.
- [ ] Expose prior-result reuse, requested evidence and human-review queue items. A full manual adjudication/writeback workflow is out of scope unless separately agreed.
- [ ] Display recalled memory with source references only after integration is real. Use no-memory/not-available labels where appropriate.
- [ ] Make live/synthetic/sample distinctions explicit. Every financial effect is synthetic, even when model and data calls are live.
- [ ] Call the existing orchestrator and action service; do not duplicate rule evaluation or create a UI-only write shortcut.

**Acceptance gate:** A teammate can explain a case, its rules, critique and action status without terminal logs. Double-click/retry behavior cannot create a second credit.

**Not in this task:** No complex frontend, external notifications, production authentication or new independent business logic.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/ui.py and UI smoke tests; reuse an existing frontend when present. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T12 — Run cross-component failure tests and repeatable reset

**Phase:** Delivery  
**Status:** NOT_STARTED  
**Depends on:** T08, T10, T11 for the intended complete demo; feature-specific tests run earlier  
**Deliverable:** A reproducible, isolated demonstration with tested failure behavior and no silent shortcuts.

**Read first:** Existing task tests, seeded dataset, integration configs and the chosen demonstration cases.

**Work:**

- [ ] Run the integrated matrix: policy boundaries/versions, partial refunds, absent/conflicting evidence, rejected proposals, duplicate retries, independent concurrent attempts and proposal-to-commit changes.
- [ ] Exercise actual database failure/rollback and simulated provider/data timeouts. Assert zero unintended effects and honest persisted/not-persisted statuses.
- [ ] Test H-MEM failure/restart and a bad recalled source. Distinguish model rationale variability from stable safety outcomes; do not require identical wording on repeated LLM calls.
- [ ] Create an explicit sandbox reset/replay operation that targets only demo state, including its memory namespace. Require an intentional reset flag and verify the target; do not reset source/shared data by default.
- [ ] If sample mode is implemented, isolate its state and label canned model responses. Report the live/demo/test modes and exact checks that were skipped.

**Acceptance gate:** Repeated runs and documented reset work without manual database repair. Full test results include commands, environment, pass/fail/skips and live-versus-mocked labels.

**Not in this task:** No destructive global reset, relabelled sample calls, or postponed unit tests that should already exist per task.

**Suggested paths/artifacts:** Proposed: dispute-demo/tests/test_failures.py, additional integration tests, dispute-demo/demo/run_demo.py or existing equivalent. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T13 — Package the evidence-backed demo and submission

**Phase:** Delivery  
**Status:** NOT_STARTED  
**Depends on:** T12, A01; documentation can be drafted alongside earlier tasks  
**Deliverable:** A truthful README, demonstration walkthrough and all verified portal deliverables.

**Read first:** Actual implementation/test logs, A01 competition checklist and chosen source-backed demo cases.

**Work:**

- [ ] Document installation, private configuration names, sanitized env example, run/test/reset commands, architecture, limits and the exact working features.
- [ ] Select fixture-backed demonstration cases. Show one valid outcome, duplicate prevention, a labelled critic-correction test, source-verified memory and a policy-version example as appropriate to the confirmed requirements.
- [ ] Prepare only the slide/video/upload formats actually required by the authenticated portal. Do not assume an old public build-window date is the upload deadline.
- [ ] Explain actual technology contributions and pre-existing work; distinguish development assistants from runtime services. Claim a named model only with evidence.
- [ ] Check repository access, secrets in current files/history/logs/recordings, links and uploads. Record submission completion only after the owner verifies it.

**Acceptance gate:** Another teammate can run the documented demo, required features have evidence, and every A01 submission item has a checked accessible artifact or an explicitly recorded blocker.

**Not in this task:** No unsupported compliance/deadline claims, manufactured model failures or submissions claimed without confirmation.

**Suggested paths/artifacts:** README.md, sanitized .env.example, demo walkthrough and confirmed submission artifacts. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

## 6. Parallel administrative task

### A01 — Confirm authenticated HackOS requirements

**Status:** NOT_STARTED  
**Owner:** team member with portal access  
**Depends on:** none; do not block safe local engineering while awaiting portal access.

- [ ] Read the authenticated Track 3 challenge and submission instructions. Record source, access date and exact wording needed to resolve scope.
- [ ] Confirm required runtime technologies, approved H-MEM implementation, any specific model requirement, deliverable formats and actual submission cutoff with timezone.
- [ ] Treat Cursor as optional under the team's latest guidance; do not invent a mandatory replacement editor. Record any explicit portal rule that needs reconciliation.
- [ ] Assign a submission owner and identify required private credentials/access without copying secret values into documentation.
- [ ] Update dependencies/scope explicitly if the real requirements differ from this proposed plan.

**Acceptance gate:** a source-backed checklist of required deliverables and constraints exists, or unavailable portal details are recorded as blockers. No guessed deadline or sponsor obligation is presented as confirmed.

## 7. Development roles versus runtime roles

| Development workstream | Tasks it may own | Runtime responsibility built |
|---|---|---|
| Policy/data | T01–T03 | Contracts, narrow reads and binding rule evaluation |
| Storage/safety | T04–T06 | Atomic write service and mandatory critic |
| Agent integration | T07–T08 | Investigator and deterministic orchestrator |
| Memory/presentation | T09–T11 | H-MEM adapter and analyst view |
| Reliability/submission | T00, T12–T13, A01 | Verified baseline, testing and delivery evidence |

These are task ownership suggestions, not five autonomous LLMs and not an assumption about team size. One person or coding-assistant session can perform several roles sequentially.

## 8. Reusable single-task prompt

```text
Read context.md, ROADMAP.md, agent.md and the applicable repository instructions.

Work on TASK_ID only. Start by inspecting the actual code and verifying that
its prerequisites are complete. Reuse working integrations and existing
conventions; the suggested paths in the roadmap are not proof files exist.

Implement the task's deliverable and acceptance tests. Keep all actions
synthetic. Do not invent policy thresholds or APIs, expose secrets, put
expected-result fixtures in runtime context, or let model output bypass
code-based policy/validation and transactional safeguards.

Run the relevant tests and report exact commands, actual pass/fail/skipped
results, files changed and any live checks you could not run. Update this
task and the work log in ROADMAP.md. Update context.md only for a genuine
architecture, scope or verified-status change.

Stop after TASK_ID. Do not start the next task. If a prerequisite is missing,
report the blocker and the smallest needed prerequisite rather than silently
expanding scope.
```

Replace TASK_ID with a single stable ID such as T00 or T03. Do not use the old report's ticket numbers without the mapping below.

## 9. Mapping from the previous detailed roadmap

| Old detailed ticket | New task IDs |
|---|---|
| Ticket 0: challenge constraints/demo data | A01, T00, T13 |
| Ticket 1: contracts | T01 |
| Ticket 2: deterministic policy | T03; supported by T02 |
| Ticket 3: decision storage/action | T04, T05 |
| Ticket 4: investigator, critic, orchestration | T02, T06, T07, T08 |
| Ticket 5: H-MEM | T09, T10 |
| Ticket 6: analyst view | T11; CLI now explicitly in T08 |
| Ticket 7: reliability and submission | T12, T13; tests also required in every earlier task |

The older summary board used different numbers; this mapping refers only to its **detailed ticket headings**. New references should use T00–T13/A01 exclusively.

## 10. Task completion record

Append one block per completed task or meaningful blocked attempt:

```md
### YYYY-MM-DD — TASK_ID: title
- Status: DONE / BLOCKED / IN_PROGRESS
- Owner:
- Source commit/baseline (if available):
- Files changed:
- Behavior delivered:
- Policy/design decisions and their source:
- Tests: exact commands and actual pass/fail/skipped counts
- Live integrations tested:
- Mocked-only checks / checks not run:
- Acceptance evidence:
- Remaining blockers or limitations:
- context.md changed? why:
- Recommended next task (not started):
```

### 2026-10-26 — Planning revision only

Historical entry supplied by the kit: its planning pass reviewed the original/updated progress reports and five-file context kit, split combined tickets, reconciled numbering, and clarified runtime responsibilities. That pass did not inspect or modify repository source or run application tests. T00 remains the first roadmap task.

### Retained history from the previous roadmap

The following entries describe earlier work. Their old ticket references and the then-absent root `CLAUDE.md` are historical; the stable task board and current file inventory above supersede those notes.

### 2026-10-26 — Initial planning baseline

- Prepared roadmap using the progress audit and its proposed architecture.
- This does **not** verify implementation of any pending ticket in the live Git repository.
- Next: portal verification plus contracts/policy-engine implementation.

### 2026-10-26 — Repository agent instructions installed

- Owner/agent: Codex, following the user's documentation setup request.
- Files created: `AGENTS.md`, `agent.md`, `context.md`, and `ROADMAP.md` at the repository root, adapted from the four supplied documents.
- Changes: required pre-execution reading order (`context.md` → `ROADMAP.md` → `agent.md`), task-specific source links, scoped onboarding instructions, and repository-relative path handling. Removed assumptions about a root `CLAUDE.md` wrapper; preserved the existing scoped instructions and unrelated working-tree changes.
- Validation commands: `python3 -` with inline standard-library assertions for local Markdown links, inventory paths, required reading order, exact filename case, and final newlines; `git diff --no-index --check -- /dev/null AGENTS.md`; `git diff --no-index --check -- /dev/null agent.md`; `git diff --no-index --check -- /dev/null context.md`; `git diff --no-index --check -- /dev/null ROADMAP.md`; `git status --short`.
- Results: all four documents passed; 35 local Markdown links and 17 inventory file paths resolved. Whitespace checks produced no diagnostics (`--no-index` returns 1 for added-file differences). No application tests, database operations, or integration calls were run for this documentation-only task; the reported runtime baseline remains unverified in this session.
- Remaining blockers: none for this documentation task. Competition verification and implementation tickets remain open.
- Next suggested task when implementation is requested: Ticket 1, then Ticket 2; inspect `dispute-demo/policies/synthetic_policy_v1.md`, `dispute-demo/policies/synthetic_policy_v2.md`, `dispute-demo/scripts/generate_synthetic_data.py`, and `dispute-demo/integration/get_dispute_context.py`. Acceptance: unambiguous typed action contracts, then deterministic fixture and boundary tests passing without Nightshift calls.
- `context.md` updated: yes, to record the verified file inventory and reading workflow; no new runtime capabilities claimed.

### 2026-10-26 — Jira-tracked context kit merged

- Scope: the user's documentation update and subsequent Jira connection check; no implementation task started.
- Files changed: `AGENTS.md`, `agent.md`, `context.md`, `ROADMAP.md`; added `CLAUDE.md` from the kit and aligned it with the shared root reading workflow.
- Behavior delivered: stable T00–T13/A01 tasks, dependencies, acceptance gates, five epic links and 15 task mappings; one assigned task at a time; clarified investigator/critic/controller roles and intended H-MEM scope. Preserved repository-specific reading links, scoped instructions, prior work history, and unrelated user changes.
- Validation: `python3 -` with inline standard-library checks for local Markdown links, file inventory, balanced code fences, task headings, Jira mappings against the ZIP, unchanged task statuses, reading order, and retained history; `git status --short` for change scope.
- Results: five documents checked; 40 local links and 18 inventory paths resolved; all 15 Jira task mappings matched the kit, and every roadmap task remains NOT_STARTED. Intentional Markdown hard-break spaces are retained.
- Jira connection check: plugin discovery reports Atlassian installed and enabled. No Jira/Atlassian tools are exposed in this session, and the browser fallback returned `No browser is available`; authenticated access to project KAN and live issue status therefore remain unverified. No Jira issues were created, edited, assigned, transitioned, or commented on.
- Application tests and live integrations: NOT RUN for this documentation-only update. No new runtime capabilities claimed.
- Remaining limits: live Jira access requires the connector's tools or an available authenticated browser; this does not block the completed local documentation update.
- `context.md` changed: yes, for the supplied planning revision, current entry points, and evidence-qualified Jira mapping provenance.
- Recommended next roadmap task, not started: T00 / KAN-9. Its acceptance gate requires actual baseline commands/results and explicit NOT RUN labels for unavailable checks.

### 2026-10-26 — GitHub publication preparation

- Scope: the user's request to commit and push the current work and configure branch upstream tracking; no roadmap implementation task started.
- Source baseline: `25d322b` on `codex/dispute-investigation-agent`; destination is the existing `origin`, `rachelanneliew/Open-Agent-Hackathon`. GitHub repository metadata confirmed push permission.
- Changes prepared: root agent/context/roadmap documents and `CLAUDE.md`, Nightshift setup instructions, sanitized integration environment example, Nightshift connectivity script, and the existing `getting-started` reference update from `44668b2` to `6a2fbaa`. The nested checkout is clean and its HEAD matches its recorded `origin/main`.
- Preserved locally: the unrelated `.DS_Store` modification. Private environment files are ignored and are excluded from the commit.
- Validation: `python3 dispute-demo/integration/check_nightshift.py --help` passed; `python3 -` with standard-library assertions checked syntax, final newlines, balanced fences, and local links across six Markdown documents (40 links resolved). A separate `python3 -` credential-pattern check passed for eight pending text files and confirmed blank example credential values. `git check-ignore -v dispute-demo/.env.local` and `git -C getting-started check-ignore -v .env.local` passed; the initial combined ignore check could not traverse the nested repository and was rerun separately.
- Application tests and live Zetaris/Nightshift checks: NOT RUN for this Git publication task. No new runtime capability is claimed; `context.md` receives no additional architecture/status change.
- Staged whitespace checks: the initial `git -c core.whitespace=blank-at-eof,space-before-tab diff --cached --check` reported existing intentional Markdown hard-break spaces. `git -c core.whitespace=-blank-at-eol diff --cached --check` passed, and `git diff --cached --check -- dispute-demo/integration/check_nightshift.py dispute-demo/integration/env.example getting-started` passed with standard whitespace rules.
- Publication uses `git push --set-upstream origin codex/dispute-investigation-agent`; its outcome and remote/tracking verification are reported in the task response rather than asserted before the push occurs.
- Recommended next roadmap task, not started: T00 / KAN-9. All roadmap task statuses remain unchanged.

### 2026-10-26 — T00 / KAN-9: verified repository baseline

- Status: DONE. The live KAN-9 definition of done requires verified commands/results, an implemented-versus-planned inventory, documented blockers and this work log; it permits unavailable integrations to be recorded explicitly. No application feature was added.
- Owner/agent: Codex, executing the user's T00-only request. KAN-9 was read from Jira and moved from To Do to In Progress during the audit; the completion evidence is also recorded on that issue. Live project name: `Open-Agent` (the supplied kit used `My Data Science Team`).
- Source baseline: `a5ab88a5e736ea2f53953cdbd1886e930df71ef0` on `codex/dispute-investigation-agent`, tracking `origin/codex/dispute-investigation-agent`. Initial checks ran against `25d322b` plus the user's existing working changes; those changes were published as `a5ab88a` during the audit. Hash comparison confirmed that all audited application sources, data, fixtures and policy files were unchanged by publication. The new publication-history entry above is preserved.
- Files changed by T00: `ROADMAP.md` and `context.md` only. Existing `.DS_Store` changes, source files, private configurations, generated data, nested checkouts and service state were preserved. No installs, source reloads, migrations, resets or application refactors were performed.
- Environment: macOS, repository venv Python 3.13.7, JayDeBeApi 1.2.3, JPype1 1.7.1, Temurin OpenJDK 21.0.8. `getting-started` HEAD is `6a2fbaa47c32c9ac33f6584c64b43b146c621bed`. Commands below use the existing venv where indicated; `PYTHONDONTWRITEBYTECODE=1` prevents cache writes.

#### Exact commands and observed results

| Working directory | Command | Actual result |
|---|---|---|
| Repository root | `git status --short --branch`; `git branch -vv`; `git remote -v`; `git log -1 --format='%H %s'` | Confirmed the local branch and matching GitHub upstream at `a5ab88a`; only the existing root `.DS_Store` modification remained before T00 edits. |
| `dispute-demo` | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_synthetic_data.py` | PASS, exit 0, even with the first non-login shell's Python 3.9.6; counts 42 transactions, 54 settlements, 40 disputes, 81 evidence rows and 16 policy rules. |
| `dispute-demo` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_generation.py' -v` | Initial non-login-shell attempt: FAIL, exit 1, 2 tests / 2 errors, `Path.write_text(..., newline=...)` unsupported by Python 3.9.6. The documented minimum is Python 3.10; this was an interpreter mismatch, not a passing run. |
| `dispute-demo` | `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python --version` | Python 3.13.7. |
| `dispute-demo` | `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | PASS, exit 0. Keys, timestamps, policy coverage, all 81 evidence documents, manifest hashes and all 40 fixture references validated. |
| `dispute-demo` | `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p 'test_generation.py' -v` | PASS, exit 0: 2 tests, 0 failures, 0 errors, 0 skipped. Covers deterministic generation, supported dataset sizes, authored scenario boundaries, amount fixtures and tamper detection. Test generation uses temporary directories; committed data was not regenerated. |
| `getting-started` | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/preflight.py --jdbc` | Initial sandbox run failed with `Operation not permitted` on local networking; its printed “closed” port was not evidence of an unavailable service. Approved retry: JDBC port, configured JAR, Java, venv, JayDeBeApi and `SELECT 1` PASS; datasource `dispute`, Lightning databases `NY_TAXI` and `TPCDS_DB`, no USL namespaces. Overall exit 1 reports 2 REST-only failures: missing `ZETARIS_API_KEY` and REST initialization. REST queries NOT RUN; JDBC is usable. |
| Repository root | `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python dispute-demo/integration/get_dispute_context.py DP-0014` | Live JDBC PASS, exit 0: 1 dispute, 1 transaction, 2 completed movements (10,000 capture; 4,000 refund), 2 evidence documents and 8 v2 rules. Retrieval is not a policy decision or recorded credit. |
| Repository root | `bash zetaris-platform/verify.sh` | First non-login-shell attempt: exit 1, Docker not on PATH. Retry with the existing login-shell PATH: live PASS, exit 0, all 9 checks, including container health, setup-job completion, UI, login and query. No software installed or services started. |
| Repository root | `bash dispute-demo/integration/db.sh ps` | PASS, exit 0: existing `dispute-postgres` container running and healthy. |
| Repository root | `sed 's/dispute_pg\./dispute./g' dispute-demo/integration/verify.sql > /private/tmp/kan9-t00-audit/verify-dispute.sql` | Created only a temporary copy using the datasource required by `TEAM_SETUP.md`; repository SQL remains unchanged. Create the temporary directory first when reproducing elsewhere. |
| Repository root | `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python getting-started/scripts/run_sql.py --channel jdbc --dry-run /private/tmp/kan9-t00-audit/verify-dispute.sql` | PASS, exit 0: previewed 3 SELECT statements, nothing sent. |
| Repository root | `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python getting-started/scripts/run_sql.py --channel jdbc /private/tmp/kan9-t00-audit/verify-dispute.sql` | Live PASS, exit 0: 3/3 statements, no skips. Counts: transactions 42, settlements 54, disputes 40, evidence 81, policy rules 16, evidence documents 81. DP-0014 movements and source text agree with the retrieval result. |
| Repository root | `bash dispute-demo/integration/db.sh exec -T dispute-postgres psql -X -U dispute_loader -d dispute_demo -c '\dt public.*'` | Live read-only PASS, exit 0: exactly 7 public tables: `connection_probe`, `disputes`, `evidence`, `evidence_documents`, `policy_rules`, `settlements`, `transactions`. No decision/action/audit/review tables in this schema. |
| Repository root | `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python dispute-demo/integration/check_nightshift.py` | FAIL, exit 1 with approved local network access: “Nightshift is unreachable or timed out. Keep the app open and check its endpoint.” No successful model discovery in this audit. |
| Repository root | `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python dispute-demo/integration/check_nightshift.py --chat` | NOT RUN: model discovery could not reach the configured runtime. No inference or responder identity claimed. |

Local network checks used approved execution outside the sandbox. The existing SLF4J no-binding warning did not prevent successful JDBC queries. No credential values were printed or added to documentation.

#### Implemented versus planned; mapping to stable tasks

| Source evidence | Verified capability / limit | Roadmap mapping |
|---|---|---|
| `scripts/generate_synthetic_data.py`, `scripts/validate_synthetic_data.py`, `tests/test_generation.py`, source CSVs, policies and test-only fixtures (all under `dispute-demo/`) | Reproducible synthetic inputs and integrity checks are implemented. All 40 fixtures cover eight scenario groups; expected outcomes are authored fixtures, not agent evaluations. | Verified baseline for T00; supports future T01/T03 tests without completing either task. |
| `integration/load_data.py`, `compose.yml`, live public table inventory | Loader and separate source PostgreSQL database exist. Loader supports preview and transactional creation; its `--apply` path was inspected, NOT RUN. `FIELDS['decisions']` is only a column-name definition; generation excludes it and the live schema has no decision tables. | T04/T05 remain NOT_STARTED; no durable decisions, safe action service or concurrency proof. |
| `integration/get_dispute_context.py`, existing JDBC helper, live DP-0014 and verification SQL | Read-only case, transaction, settlement, evidence-text and applicable-policy retrieval works. Visibility filters and opening-date policy selection exist in SQL. No typed tool registry, customer-history interface, source revisions or retrieval failure/scoping test suite exists. | Partial prerequisite for T02; T01/T02 remain NOT_STARTED. |
| Policy Markdown, `policy_rules.csv`, generator `policy_rows()` | Two versions, filing windows 30/45 days, first applicable terminal rule by ascending priority, and review above 20,000 SGD minor units are defined. Predicate names are data; no executable runtime evaluator exists. | T03 remains NOT_STARTED. |
| `integration/check_nightshift.py` | Auth/model-discovery and optional one-word chat probe exist. Current discovery failed; previous READY evidence is historical. No structured investigator, critic or bounded orchestrator exists. | T06–T08 remain NOT_STARTED. |
| Repository file inventory and official H-MEM reference below | No H-MEM adapter, persistent project memory, analyst UI, end-to-end runner or reset workflow is present. | T09–T13 remain NOT_STARTED; no task marked complete from the architecture or fixtures. |
| Local handbook and absent external progress reports | Handbook is historical; external progress audit files are not in this checkout. No authenticated HackOS requirements were checked. | A01 remains NOT_STARTED. |

#### Located H-MEM source (reference discovery only)

The local handbook section 7.4 points to [Meterless Engines](https://meterless.ai/engines.html). Its live “Give my agent memory” entry points to `Meterless/Meterless/engines/hmem`. Inspected on 2026-10-26 at upstream commit `1742dec56a66e58eef9dda2d2b865823758ca8cd`: [specification](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem/AGENTS.md), [engine README](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem/README.md), [reference README](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem/reference/README.md), and [conformance directory](https://github.com/Meterless/Meterless/tree/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/hmem/conformance). The reference README describes deterministic mock embeddings and optional JSON persistence, not a production runtime library. No package/API was guessed. Installation, reference/conformance execution and project save/restart/recall are NOT RUN; those belong to T09. Authenticated competition approval remains an A01 question.

#### Gaps and acceptance decision

- Nightshift is currently unavailable to its configured discovery check. Restore/check that existing runtime before the next live inference test; do not assume the older READY result still applies. REST is unconfigured, while the selected JDBC path passed.
- T01 must resolve legacy `recommend_refund`/`recommended_refund_minor` versus simulated provisional credit, business outcomes versus persistence statuses, lifecycle transitions and the source-version/write synchronization contract. Neither policy defines a repeated-claims threshold or a decision lifecycle. No new threshold or contract was invented in T00.
- `registration.sql` / `verify.sql` still use `dispute_pg`; the live datasource and retrieval use `dispute`, as already documented in `TEAM_SETUP.md`. The audit adapted a temporary read-only copy only.
- Source retrieval omits customer/dispute-status/revision fields needed by later tasks, uses an inner join for evidence text and has no completeness/failure tests. Its policy rows are not executed. These are recorded T01–T03 prerequisites, not fixed as part of this audit.
- The root tracks `getting-started` and `zetaris-platform` as gitlinks but has no `.gitmodules`; a fresh clone must follow the existing setup instructions to obtain populated onboarding/platform directories. Private configs and running services are local prerequisites, not supplied by GitHub.
- Acceptance gate met: exact successful and unsuccessful commands, explicit NOT RUN checks, source inventory, stable-task mapping and blockers recorded. Only T00 is DONE; this does not claim a functioning investigation/decision application.
- `context.md` changed: yes, to replace historical-only runtime claims with dated T00 evidence, record current Nightshift unavailability, identify the official H-MEM reference and verify KAN-9 access. Architecture and intended scope are unchanged.
- Recommended next task, NOT STARTED: T01 / KAN-10, only after a new instruction. Work stops after T00.

### 2026-10-26 — Ignore Finder metadata and prepare the main-branch PR

- Scope: the user's follow-up request to ignore `.DS_Store`, commit/push the cleanup and prepare a detailed pull request from `codex/dispute-investigation-agent` to `main` on the existing `origin`; no roadmap implementation task started.
- Changes: added the root `.gitignore` rule `.DS_Store`, which also matches nested paths, and used `git rm --cached -- .DS_Store` to remove the already-tracked Finder metadata from the index while retaining the local file. Added this work-log entry; application source and context architecture are unchanged.
- Validation: `git check-ignore -v -- .DS_Store probe/nested/.DS_Store` passed and matched the root rule; `git ls-files -- .DS_Store` returned no tracked file; an inline Python check confirmed the local file still exists. `git diff --cached --check` passed for the metadata removal. An initial byte-for-byte preservation assertion failed because local metadata bytes changed between the snapshot and check; no command wrote or restored those bytes, and the subsequent presence/ignore/index checks passed.
- PR preparation: inspected the complete branch diff, confirmed the branch was ahead of `main` with no missing base commits, and found no existing open PR for this head/base pair. The description covers all branch changes, the verified T00 results and explicit failed/NOT RUN integrations, including the existing onboarding gitlink update.
- Runtime tests: not rerun for this metadata/documentation-only follow-up. The T00 commands and outcomes above apply to the unchanged application files; this entry makes no additional integration claim.
- Task statuses: T00 remains DONE; T01–T13 and A01 remain NOT_STARTED. Publication/PR creation results are reported after the remote operations complete.

### 2026-10-26 — T00 / KAN-9: closure revalidation

- Scope: the user's request to verify T00, rerun tests and close Jira with the correct evidence. Authenticated Jira inspection found KAN-9 already Done, resolved at 18:13:45 +08:00, with the original audit comment (10000). No duplicate transition is needed.
- Source: `8883e5c6743ffa6b1c6279a4b4262c8014d43e7f` on `codex/dispute-investigation-agent`; initial working tree clean. Re-read the required documents, generator, validator, tests, policies, fixtures and integration sources. Existing implemented-versus-planned inventory remains accurate.
- Exact commands from `dispute-demo`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` — PASS, exit 0; 42 transactions, 54 settlements, 40 disputes, 81 evidence rows/documents, 16 rules, manifest hashes and fixture references validated. `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p 'test_generation.py' -v` — PASS, exit 0; 2 tests, 0 failures/errors/skips.
- Exact commands from root: `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python --version` — Python 3.13.7; `git diff a5ab88a --exit-code -- dispute-demo getting-started zetaris-platform` — PASS, exit 0, no differences from the audited application/data/integration baseline.
- Live Zetaris, PostgreSQL, Nightshift discovery/inference and H-MEM checks: NOT RUN in this closure follow-up. The original audit above retains the prior passing JDBC/platform results, failed Nightshift discovery, unset REST key and explicit NOT RUN checks; this follow-up does not refresh service availability claims.
- Acceptance: the existing source inventory, gap list and command log satisfy KAN-9's baseline-audit definition of done; fresh local checks pass. T00 remains DONE. T01–T13 and A01 remain NOT_STARTED.
- Files changed: `ROADMAP.md` and `context.md` only, to record revalidation and the verified Jira state. No application or generated data changes. Documentation validation passed: inline Python checked 4 local Markdown links, balanced fences and final newlines across both files; `git diff --check` passed.
- Jira result: revalidation comment `10001` successfully added to KAN-9; status remains Done. The first comment request timed out; a read-back showed only the original comment, then the retry succeeded. These documentation edits were local at the end of the revalidation; publication is covered by the follow-up below.
- Recommended next task, not started: T01 / KAN-10, only on a new instruction.

### 2026-10-26 — Publish T00 revalidation to main

- Scope: the user's explicit request to commit and push the revalidation notes to `main`. Changes are limited to `ROADMAP.md` and `context.md`; no roadmap implementation task started.
- Remote inspection: `git fetch origin` confirmed `origin/main` at `cdb1cc9`, the merge of PR #2, with the same file tree as the audited branch tip `8883e5c`. Preserve that merge and apply only the documentation follow-up on top.
- Validation: `git diff --check` and inline Python checks for local Markdown links, balanced fences and final newlines across the two changed documents passed. The preceding data validation and 2 passing generation tests apply to unchanged application files; live integration checks are NOT RUN for this documentation publication.
- Publication uses a normal, non-forced push to `origin/main`; commit identity and remote verification are reported after execution. T00 remains DONE; T01 / KAN-10 is the recommended next task and is not started.

### 2026-10-26 — Add the root README documentation guide

- Scope: the user's request to put the Markdown-file guide in the repository README. No root README existed; added `README.md` with the supplied table and repository-relative links suitable for GitHub and teammate checkouts.
- Files changed: `README.md` and this work log. No implementation, architecture or task-status changes; `context.md` unchanged. This documentation index does not complete T13's demo/submission deliverables.
- Validation: `python3 -` with inline standard-library assertions passed for 15 local Markdown link targets in `README.md` and `ROADMAP.md`, final newlines and absence of machine-specific paths in the README. `git diff --check` passed; `git diff --no-index --check -- /dev/null README.md` produced no whitespace diagnostics (exit 1 indicates the added-file difference).
- Application tests and live integrations: NOT RUN for this documentation-only change. Next implementation task remains T01 / KAN-10, not started.

### 2026-10-26 — Add README task handover instructions

- Scope: the user's request to explain how another teammate can identify and carry out the next Jira task. Extended `README.md` with the roadmap's role, a dated T01 / KAN-10 handover, its deliverable and acceptance gate, execution/completion steps and a copyable task assignment.
- Preserved the existing documentation guide and local README/work-log changes. No task started or Jira status changed; `context.md` unchanged. T02 / KAN-11 remains the recommendation after T01, and A01 / KAN-23 can be assigned separately.
- Validation: `python3 -` with inline assertions passed for 21 local links, balanced fences, final newlines and portable README paths. `git diff --check` passed; `git diff --no-index --check -- /dev/null README.md` produced no whitespace diagnostics (exit 1 indicates the added-file difference). Application tests and live integrations: NOT RUN for this documentation-only change.

### 2026-10-26 — T01 / KAN-10: shared contracts and source-policy semantics

- Status: DONE against the T01 acceptance gate. Prerequisite T00 was verified against its completion record and unchanged baseline sources; the existing two generation tests and data validator passed before implementation. Started from `27d50bdb1ea07a7edd088ebbce2239c71877da72` on task branch `codex/t01-shared-contracts`.
- Added `dispute-demo/app/__init__.py`, `dispute-demo/app/schemas.py`, `dispute-demo/tests/test_schemas.py` and `dispute-demo/docs/contracts.md`. Updated this roadmap and `context.md`; preserved the earlier README/work-log edits and advanced README's handover to T02. Changes were local and uncommitted at task completion; publication is covered by the follow-up below.
- Implemented all six immutable shared contracts, supporting source types and strict JSON conversion. Tests reject malformed source/runtime IDs, unknown fields/outcomes, invalid currencies/times, coercible/negative/overflow amounts, future/out-of-scope records, mixed policy versions, fabricated missing-evidence IDs and invalid commit/run combinations.
- The explicit legacy adapter maps only recommendation `recommend_refund` to `provisional_credit`; merchant refunds/reversals remain source movements. DP-0014 still represents 10,000 captured, 4,000 already refunded and a separate authored 6,000 credit recommendation. Non-credit outcomes have no amount or simulated effect. Policy, proposal, critic and persistence results have distinct meanings.
- Documented opening-date version selection, exact 30/45-day filing boundaries, the 20,000 SGD-cent threshold, ascending first-terminal rule precedence and workflow phase transitions. No source policy defines persisted dispute lifecycle/reopening rules; those are explicitly unresolved for T04/T05. No new policy number, fixture meaning or source record was introduced.
- Documented stale-result invalidation and a future global source-revision guard requiring participation by **all** relevant writers, including settlement inserts, evidence/policy edits, loaders and action writes. Snapshot UUIDs do not establish freshness; unavailable source revision is null and cannot appear in a successful commit result. Real synchronization, durability and uniqueness remain T04/T05 work.

Verification from `dispute-demo/` (existing Python 3.13.7 venv):

| Exact command | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` | PASS, 23 tests (21 schema + 2 generation), 0 failures/errors/skips. All 40 authored scenarios across eight groups are representable. This is not policy prediction or integration execution. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | PASS: 42 transactions, 54 settlements, 40 disputes, 81 evidence rows, 16 rules; keys, timestamps, policy coverage, documents, hashes and fixture references checked. |

Repository-root verification:

- `git diff --exit-code 27d50bd -- dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/integration dispute-demo/tests/fixtures dispute-demo/tests/test_generation.py`: PASS (exit 0); existing source/data/fixture/test paths unchanged.
- `git diff --check`: PASS after correcting the newly edited status line's Markdown whitespace.
- Local link validation: PASS, 39 targets across README, context, roadmap and contract reference, using the exact command below. External URLs were not treated as live integration checks.

```sh
PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python - <<'PY'
import re
from pathlib import Path
files = [Path(p) for p in ('README.md', 'context.md', 'ROADMAP.md', 'dispute-demo/docs/contracts.md')]
checked = 0
for path in files:
    for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', path.read_text()):
        if target.startswith(('https://', 'http://', '#')):
            continue
        resolved = path.parent / target.split('#')[0]
        assert resolved.exists(), f'{path}: broken target {target}'
        checked += 1
print(f'PASS: {checked} local Markdown link targets across {len(files)} files')
PY
```

- Live Zetaris/PostgreSQL/Nightshift/H-MEM integration checks, migrations, writes and concurrency tests: **NOT RUN** in T01; no service capability is claimed from these local tests. T00's dated evidence remains historical.
- Open implementation decisions are recorded in `dispute-demo/docs/contracts.md`: business lifecycle/re-review and duplicate scope, broader ledger/evidence interpretations, unsupported currency/policy scope, historical-cutoff handling at commit and revision/read-coherence implementation. These are explicit handover requirements, not a missing T01 acceptance artifact.
- Jira: read the live KAN-10 description, moved it to In Progress, posted completion/test evidence as comment `10002`, then transitioned it to Done. The transition response confirmed status **Done** and resolution **Done**. No other issue was changed.
- Recommended next task: T02 / KAN-11. T02–T13 and A01 remain NOT_STARTED; no next task was begun.

### 2026-10-26 — Publish T01 and README handover for review

- Scope: the user's request to commit and push the completed work to GitHub and open a PR targeting `origin/main`. Includes the T01 contracts/tests/reference, root README guide/handover and context/roadmap evidence; no new implementation task started.
- `git fetch origin` passed. `git rev-list --left-right --count origin/main...HEAD` returned `0 0` before the commit: the task branch starts at current `origin/main`, `27d50bdb1ea07a7edd088ebbce2239c71877da72`.
- Fresh checks from `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` — PASS, 23 tests, zero failures/errors/skips; `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` — PASS, 42 transactions, 54 settlements, 40 disputes, 81 evidence rows and 16 rules.
- `git diff --exit-code origin/main -- dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/integration dispute-demo/tests/fixtures dispute-demo/tests/test_generation.py` passed: existing data, policies, generators, integrations and fixtures are unchanged. `git diff --check` passed. The T01 inline local-link command above is used again for the four documentation files.
- Publication uses `git push --set-upstream origin codex/t01-shared-contracts` and a PR from that branch to `main` in `rachelanneliew/Open-Agent-Hackathon`. Commit identity, remote verification and the resulting PR URL are reported after execution. No merge is part of this request.
- Live application integrations: NOT RUN for this publication. T01 remains DONE; T02 / KAN-11 is the recommended next task and remains NOT_STARTED.

## 11. Deferred scope

An independent manager/planner LLM, a second semantic-review LLM, a fraud-risk model, longer agent loops, advanced UI and production integrations are not prerequisites for this proposed build. A confirmed competition requirement or explicit scope decision can add a separately scoped task. Do not add them silently during a task above.

## 12. Document maintenance

- Update `context.md` for agreed scope/architecture changes or verified factual corrections, preserving the distinction between historical audit claims and current execution evidence.
- Update this roadmap's task board, detailed status, and completion record together when acceptance evidence or dependencies change. Use stable T00–T13/A01 IDs; retain earlier records as history.
- Update `agent.md` when shared operating rules change, and keep the root `AGENTS.md` and `CLAUDE.md` entry points aligned with the same pre-execution reading order.
- Verify repository links after documentation edits. Proposed implementation paths are not claims that those files exist; imported Jira links are not proof of live access or issue completion.
