# Task Roadmap — Synthetic Card-Dispute Resolution Agent

> **Canonical work queue.** Read [`context.md`](./context.md) first, then [`agent.md`](./agent.md).
> **Revision:** T07 Nightshift investigator accepted, 27 October 2026: 121 passing tests, 45 PostgreSQL opt-in skips, four compatibility tests and data validation; a real Zetaris/Nightshift proposal passed the pure critic. Evidence is recorded below.
> **Current authorized goal:** complete the entire roadmap sequentially, updating Jira and committing/pushing each completed task to `origin/main`. The user explicitly expanded the earlier single-task scope on 27 October. T00–T08 are DONE; next is T09 / KAN-18. Remaining tasks retain their acceptance gates and explicit scope decisions.
> **Agent entry point:** complete the reading in [`AGENTS.md`](./AGENTS.md) before execution. A specific user request takes precedence; a documentation update does not authorize starting another task.

## 1. What changed from the earlier plan

The previous roadmap used different numbers in its summary board and detailed tickets. It also bundled investigator, critic and orchestration into one large ticket. This revision replaces that task numbering with stable IDs T00–T13 and administrative task A01.

The architecture is clarified, not claimed as implemented: one investigator LLM, one mandatory deterministic critic/validator and one Python workflow controller. A separate LLM critic or manager is not needed for the initial build. H-MEM remains part of the intended complete product, although the first working CLI slice can precede it. Exact competition obligations remain unverified until A01.

Keep the dated `Open_Agent_Hackathon_Progress_2026-10-26*.md` reports as historical evidence. Do not treat their older ticket numbers or copy-ready all-in-one policy prompt as the active task queue. The T00 completion record below now provides current-checkout evidence for the baseline and explicitly identifies unavailable checks.

## 2. How to execute this roadmap

For ordinary handovers, give the coding assistant **one task ID at a time**. The current explicit full-roadmap goal authorizes continuing to the next dependency-ready task after each verified completion and publication; it supersedes the stop-after-one-task directions for this goal only. It must inspect prerequisites, implement only that task, run relevant tests, update this file and stop. A dependency that is missing is a blocker to report, not permission to implement every prerequisite silently.

Use statuses `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`. DONE requires recorded acceptance evidence; writing code is not enough. Mark unavailable live checks NOT RUN. A local stub test does not prove a live integration or PostgreSQL concurrency guarantee.

**Recommended first sequence:** T00 -> T01 -> T02 -> T03. This produces a source-backed deterministic evaluator before any model can suggest an action. Then complete T04–T08 for a safe end-to-end CLI. Complete T09–T11 for the intended memory-backed analyst demonstration, and T12–T13 for delivery. A01 runs alongside development. T09's reference integration may be checked early to expose access/API blockers.

Every task includes its own tests. T12 is cross-component testing, not the first time testing begins.

**Post-merge integration order:** T03–T08 are complete, including shared guarded deployment and live fresh-read/model/commit acceptance. Continue with T09 under the current goal. T09 and A01 can progress separately when assigned. After T09, complete T10, then T11, T12 and T13. Existing formal dependencies below remain unchanged. T02 can represent unavailable revision/storage support and must not wait for all T04 features; T05 cannot pass without T04 synchronization and fresh typed inputs. This sequence authorizes no work beyond the assigned task.

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

**Read-only snapshot, 27 October 2026:** all 20 labelled Jira issues returned, no further page. KAN-9/KAN-10 are Done, KAN-11–KAN-23 and KAN-4–KAN-8 are To Do; all unassigned, all issue-link arrays empty. Newly created [JIRA_POST_MERGE_CHANGESET.md](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) contains the current descriptions and exact proposed description edits. No Jira write, status/assignee/epic/dependency-link change or new ticket is part of this pass. T00/T01 completion and stable mappings remain intact.

**Approved follow-up, 27 October 2026:** the user authorized the exact preview. KAN-11–KAN-23 description updates are now applied and verified; the preview retains original snapshots and an application receipt. Summaries, statuses, assignees, task IDs, epics and dependency links remain unchanged. KAN-4–KAN-10 are untouched. No implementation task started.

## 3. Task board

| ID | Task | Dependencies | Status |
|---|---|---|---|
| T00 | Verify the current repository baseline | None | DONE |
| T01 | Define shared contracts and exact policy semantics | T00 | DONE |
| T02 | Expose narrow case and history retrieval tools | T01 | DONE |
| T03 | Implement deterministic policy evaluation | T01, T02 | DONE |
| T04 | Create sandbox decision, action and audit storage | T01 | DONE |
| T05 | Implement atomic simulated decision recording | T03, T04 | DONE |
| T06 | Build the mandatory critic and validator | T02, T03 | DONE |
| T07 | Implement the investigator through Nightshift | T02, T03, T06 | DONE |
| T08 | Wire the bounded workflow and command-line runner | T02, T03, T05, T06, T07 | DONE |
| T09 | Verify and wrap the actual H-MEM integration | T00, T01; may run in parallel with T02–T08 | NOT_STARTED |
| T10 | Integrate verified memory and repeat-history review | T02, T03, T08, T09 | NOT_STARTED |
| T11 | Build the thin analyst view and review queue | T08; memory display depends on T10 | NOT_STARTED |
| T12 | Run cross-component failure tests and repeatable reset | T08, T10, T11 for the intended complete demo; feature-specific tests run earlier | NOT_STARTED |
| T13 | Package the evidence-backed demo and submission | T12, A01; documentation can be drafted alongside earlier tasks | NOT_STARTED |
| A01 | Confirm authenticated HackOS requirements | None; run alongside development | NOT_STARTED |

### PR #4 implementation evidence, separate from task status

[PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4) merged nine new prototype/test files and one retrieval change. Source inspected on 27 October at `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`; application tests NOT RUN in this pass. NOT_STARTED above records unstarted canonical integration/acceptance work, not absence of all related code.

| Existing path (repository-relative) | Reuse / remaining acceptance | Tasks |
|---|---|---|
| `dispute-demo/integration/get_dispute_context.py` | Preserve transaction `customer_id` addition; typed context/history, missing-text preservation and failure/scope tests remain. | T02 |
| `dispute-demo/agent/policy_engine.py` | Reuse dictionary evaluator; adapt to strict schemas and harden against actual policies/fixtures. | T03 |
| `dispute-demo/agent/critic.py` | Reuse validation/duplicate-test ideas; separate pure critic from canonical PostgreSQL all-outcome storage/writes. SQLite has no authoritative source freshness protocol and non-credit results are not persisted. | T04, T05, T06 |
| `dispute-demo/agent/resolver.py` | Deterministic proposal helper plus memory and SQLite critic call; no Nightshift investigator, canonical bounded controller or genuine no-memory mode. | T07, T08, T10 |
| `dispute-demo/agent/hmem_client.py`, `dispute-demo/agent/hmem_bridge/server.ts`, `dispute-demo/agent/hmem_bridge/package.json` | Existing adapter/bridge; external prerequisites, pinning, timeouts, restart/isolation and persistence concurrency remain unverified. | T09 |
| `dispute-demo/agent/memory_service.py` | Customer tags and advisory count exist; authoritative source verification, temporal filtering and decision-ID persistence remain. Three prior claims is not binding policy. | T09, T10 |
| `dispute-demo/agent/tests/test_critic.py`, `dispute-demo/agent/tests/test_hmem_integration.py` | Separate test root; test-only path injection, mocked policy/SQLite and external-reference tests require deliberate collection, import checks and scope labels. | T03–T10 as affected, T12 |

Target architecture remains one investigator, a pure deterministic critic and one PostgreSQL action service for `provisional_credit`, `request_evidence`, `decline`, `human_review`. The first three run autonomously when permitted; mandatory policy review prevents credit. Advisory verified history is not a hold, raw memory is not authority, and failed persistence is not a queued review. T10 retains its explicit advisory-scope versus versioned binding-rule acceptance decision.

`dispute-demo/app/schemas.py` is canonical. The `app/` module paths in task artifacts are proposed destinations; `agent/` modules exist now. Adapt/move one module during its assigned task, update package imports/tests and retire or delegate its old entry point. Leave one evaluator and one normal-runtime action writer, no SQLite bypass. Preserve local prototype state unless a separate migration is authorized.

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
**Status:** DONE

**Depends on:** T01  
**Deliverable:** Typed, read-only tools over the working Zetaris integration.

**Read first:** Existing integration/get_dispute_context.py, connection configuration names, source tables and T01 contracts.

**PR #4 integration requirements:**

- [x] Preserve the transaction `customer_id` addition. Map raw rows into strict `DisputeContext` with source IDs, statuses, timestamps, policy applicability and explicit input issues; never weaken T01 scope checks.
- [x] Retain evidence metadata when text is absent instead of dropping it through the inner join; `content=None` is unavailable support. Test missing/unreadable text and malformed rows.
- [x] Return customer-scoped, time-visible history in a separate typed result with source references, outside the current case's transaction/evidence collections. Stored memory tags are not source verification.
- [x] Keep `source_revision=None` until coherent freshness support exists; explicitly report unsupported decision reads until T04 tables/registration exist. Test raw-to-typed mapping, ownership, cutoff and distinct not-found/incomplete/malformed/unavailable results. Live checks are separate evidence.

**Work:**

- [x] Wrap or extend existing case retrieval rather than replacing the JDBC/Zetaris path. Return linked transactions, completed and pending settlement movements with statuses, evidence and applicable policy.
- [x] Add narrowly scoped retrieval for verified customer history, current dispute state and existing decisions as the actual tables become available. Do not claim decision reads are live before the T04 migration is applied and the required read registration exists.
- [x] Enforce case/customer scope and evaluation-time visibility. Include relevant source IDs and revision information needed for later validation.
- [x] Distinguish not-found, incomplete data and service failure; do not return an empty successful case on a connection failure.
- [x] Expose an allowlisted tool registry with validated arguments. Models may request permitted reads, but only application code executes the requests. Keep raw SQL, credentials and expected-result fixtures inaccessible to the runtime model.

**Acceptance gate:** Unit tests cover scoping, future-record filtering and failure modes. A live case can be retrieved through Zetaris when available, with live versus stubbed evidence clearly recorded.

**Not in this task:** No arbitrary SQL tool, direct model database access, source mutation or simulated action writes.

**Implemented artifacts:** [typed tools and registry](./dispute-demo/app/tools.py), [retrieval tests](./dispute-demo/tests/test_tools.py), extended [JDBC retrieval](./dispute-demo/integration/get_dispute_context.py) and [read-interface reference](./dispute-demo/docs/retrieval.md). Verified 27 October: 27 new retrieval tests and live typed context/history/state reads pass. Decision reads remain explicitly unsupported pending T04; source revisions remain null. Full evidence and limits are in the T02 completion record.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T03 — Implement deterministic policy evaluation

**Phase:** Foundation  
**Status:** DONE
**Depends on:** T01, T02  
**Deliverable:** A pure policy evaluator that returns allowed outcomes, rule results, constraints and source-linked explanations.

**Read first:** Exact versioned policies, T01 contracts, T02 context format and test-only fixtures.

**PR #4 integration requirements:**

- [x] Adapt `dispute-demo/agent/policy_engine.py` into the single canonical evaluator, returning a bound `PolicyResult` with all four outcomes explicitly allowed/blocked, rule checks, missing categories and optional credit limit. Apply the existing legacy mapping at an explicit boundary.
- [x] Preserve opening-date version selection, ascending first-terminal precedence, exact 30/45-day filing windows and review only above 20,000 SGD cents. Follow primary-transaction balance semantics; pending/failed amounts are not completed money and negative/corrupt balances must not silently become valid zero balances.
- [x] Evidence type alone cannot prove usable support. Document bounded synthetic delivery-template interpretation and reject unsupported/missing text. Normalize invalid evidence timestamps and missing transaction fields at the input boundary.
- [x] Test all applicable authored scenarios and just-inside/on/outside boundaries, malformed/incomplete/duplicate predicates, unexpected actions, mixed versions and unsupported policy/currency scope. No numeric repeat-claim rule is added.

**Work:**

- [x] Implement evaluate_policy(context, evaluation_time) without model calls. Select the version applicable under the source policy date rule; do not substitute the newest policy simply because it is available.
- [x] Implement written filing-window, evidence, amount, settlement-integrity, precedence and human-review checks. Calculate amounts from authoritative movements in integer minor units according to the actual policy.
- [x] Return rule IDs, source evidence, missing requirements, allowed/blocked outcomes and credit limit or reason that no amount can be safely calculated.
- [x] Use verified history, not raw H-MEM text, for any history-dependent rule. Reevaluate after any newly verified evidence changes the case context.
- [x] Test all applicable existing fixture scenarios and explicit boundaries. Treat fixture disagreements as a discrepancy to investigate rather than permission to rewrite expected outcomes.

**Acceptance gate:** Policy tests pass with Nightshift disabled. An actual Zetaris context can be evaluated with auditable rules. Missing or contradictory facts never default to credit.

**Not in this task:** No LLM enforcement, runtime expected-results lookup, ledger writes or invented history threshold.

**Implemented artifacts:** [typed evaluator](./dispute-demo/app/policy_engine.py), [delegating legacy adapter](./dispute-demo/agent/policy_engine.py), [policy tests](./dispute-demo/tests/test_policy_engine.py), [policy reference](./dispute-demo/docs/policy.md).

**Acceptance state, 27 October 2026:** **DONE**. 70 root-suite tests (20 policy tests including all 40 authored cases), 6 prototype critic regressions and data validation pass. After user-authorized startup of the existing local stack, JDBC preflight and the live policy CLI passed. Eight live contexts cover all four outcomes, partial refunds, review threshold and v1/v2 boundaries with bound rules/citations and JSON round-trips. No source data was reloaded, reset or mutated. The initial blocked attempt and successful follow-up are retained in the work log.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T04 — Create sandbox decision, action and audit storage

**Phase:** Controls  
**Status:** DONE
**Depends on:** T01  
**Deliverable:** A tracked PostgreSQL migration with enforceable uniqueness and traceable non-credit decisions.

**Read first:** Current project database schema, migration conventions and T01 action/status contracts.

**PR #4 integration requirements:**

- [x] Persist all four outcomes, review queue, idempotency and audit in PostgreSQL; only credit has an amount/effect. Test review persistence across restart. The prototype's SQLite transaction uniqueness does not define canonical cross-dispute policy.
- [x] Implement the T01 global source-revision guard with enforced participation by all relevant writers, including settlement/evidence/policy/decision changes and loaders/resets. Coordinate coherent T02 reads without creating a circular prerequisite.
- [x] Resolve minimum non-credit/new-evidence lifecycle, cross-dispute duplicate scope and historical replay versus fresh commit semantics before enabling writes. A frozen evaluation cutoff cannot hide a later authoritative refund; isolate replay or explicitly document/test fresh-write behavior.

**Work:**

- [x] Create or reuse storage for investigation/decision records, simulated credit effects, audit events and review-queue status. Keep these separate from source settlement refunds.
- [x] Define a stable request idempotency key and a separate business constraint that permits at most one effective simulated provisional credit per dispute in the MVP sandbox.
- [x] Allow a later legitimate review after a request-for-evidence outcome when new evidence arrives, without permitting another credit. Do not treat every previous non-credit decision as permanent closure.
- [x] Persist policy/source references, proposal identity and committed execution state. Non-credit outcomes must not create a money-effect row.
- [x] Apply migration tests to an isolated test database. Preserve the source dataset and keep any live/sample state explicitly separated.

**Acceptance gate:** Migration is reproducible in a test database. Constraint tests block a second effective credit and permit valid non-credit lifecycle records. No production or shared source data is reset.

**Not in this task:** No LLM workflow or claim that uniqueness alone proves all commit-time safety.

**Implemented artifacts:** [migration 001](./dispute-demo/db/migrations/001_decision_storage.sql), [PostgreSQL tests](./dispute-demo/tests/test_decision_storage.py), guarded [initial loader](./dispute-demo/integration/load_data.py), and [storage/lifecycle reference](./dispute-demo/docs/storage.md).

**Acceptance, 27 October 2026:** 20 real PostgreSQL tests pass in a disposable, unnetworked container: all outcomes/sidecars, duplicate and swapped-pair constraints, non-credit re-review, permissions, revision/rollback, writer blocking, late refunds and actual server restart. The 70 offline tests and 6 prototype critic tests pass; data validates unchanged. Applied only to isolated test databases. Deployment, Zetaris registration/read coherence and T05 action validation remain separate; T02 still returns null revisions and unsupported decisions.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T05 — Implement atomic simulated decision recording

**Phase:** Controls  
**Status:** DONE
**Depends on:** T03, T04  
**Deliverable:** One backend write service that validates and commits allowed sandbox decisions safely.

**Read first:** T01 synchronization/transition contract, T03 evaluator, T04 storage and actual source-state schema.

**PR #4 integration requirements:**

- [x] Make the PostgreSQL action service the sole normal-runtime decision/effect writer; replace the SQLite critic path. Validate exact proposal/critic/reference binding and refuse unknown as well as stale revisions inside the protected transaction.
- [x] Same key + identical payload returns the original result as `reused`; same key + changed payload is rejected; a new key cannot create a second effective credit. Commit decision, optional effect, audit and idempotency together.
- [x] Test all four persisted outcomes, required-review exclusion of credit, request/decline without effects, rollback, lost-acknowledgement recovery with the original key and independent-connection PostgreSQL concurrency. SQLite tests do not satisfy this gate.

**Work:**

- [x] Implement a narrow commit_simulated_decision interface callable by the orchestrator, not by model tools.
- [x] In one database transaction, validate the request, lock/reload relevant authoritative state, select the applicable policy using its documented date anchor and reevaluate binding checks before writing.
- [x] Reject stale source versions, changed settlements, invalid status transitions and disallowed amounts. A lock on a dispute row alone is not sufficient unless relevant source writers follow the same synchronization protocol; implement and test the documented protocol.
- [x] Commit decision, optional simulated effect and required audit event atomically. Only report committed after commit succeeds. On a lost acknowledgement, retry the same idempotency key and return the existing result.
- [x] Keep provisional credit, evidence request, decline and human-review outcomes distinct. If the database is unavailable, return not committed; do not pretend a human-review queue entry was saved.

**Acceptance gate:** Real PostgreSQL integration tests use independent transactions/connections. A valid case commits once; retries reuse it; two simultaneous attempts produce at most one credit; rollback and state/settlement changes cause no partial or stale effect.

**Not in this task:** No real payment, model write tool, memory write inside the decision transaction or mocked-only claim of concurrency safety.

**Implemented artifacts:** [action service](./dispute-demo/app/action_service.py), [action tests](./dispute-demo/tests/test_action_service.py), [pinned dependency](./dispute-demo/requirements-actions.txt), and [action-service reference](./dispute-demo/docs/actions.md).

**Acceptance, 27 October 2026:** 138 tests pass with zero skips, including 25 real PostgreSQL action tests and all 20 T04 storage tests. Four compatibility tests and data validation pass. Verified all outcomes, exact binding, full protected source rereads, identical retry reuse, changed-payload rejection, duplicate reservations, concurrent requests/source writers, rollback and lost-ack recovery. Only isolated databases were migrated/written. Shared deployment, runtime login and coherent fresh Zetaris reads remain pending; null revisions still cannot commit.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T06 — Build the mandatory critic and validator

**Phase:** Agent workflow  
**Status:** DONE
**Depends on:** T02, T03  
**Deliverable:** A code-first review gate that accepts, requests correction or routes an unsupported proposal to review.

**Read first:** T01 AgentProposal/CriticResult, T02 sources, T03 PolicyResult and fixture scenarios.

**PR #4 integration requirements:**

- [x] Reuse checks from `dispute-demo/agent/critic.py` as a pure function accepting `DisputeContext`, `PolicyResult`, `AgentProposal` and returning bound `CriticResult`; no ledger creation, database writes or action-service calls.
- [x] Enforce identity/snapshot/revision, policy version, outcome, amount/currency and required citations/support; requesting missing evidence must not require invented evidence IDs. Mandatory policy review blocks credit; advisory memory is not policy.
- [x] Replace prototype tests that expect critic-created credit with purity checks across every branch. Write/duplicate storage assertions are already covered by T04 PostgreSQL tests; full action-service assertions remain explicitly assigned to T05, whose service does not yet exist. Test real typed policy outputs as well as crafted invalid proposals.

**Work:**

- [x] Validate structure, supported outcome, amount/currency, policy version, context revision, cited rule IDs and time-visible evidence IDs.
- [x] Check binding policy constraints, human-review requirements and source scope. A real evidence ID alone does not prove the evidence supports a claim; use structured corroboration where available and route unresolved substantive contradictions to review.
- [x] Return structured feedback with failed checks, required evidence or corrections, and whether a bounded revision is permitted. The critic does not execute actions.
- [x] Test crafted invalid proposals: invented/cross-case evidence, future evidence, excessive credit, ignored policy blocks, stale snapshots and unsupported conclusions.
- [x] Keep any future LLM semantic reviewer separate. It may add concerns but cannot override a deterministic rejection or approve an action independently.

**Acceptance gate:** Invalid proposals are rejected in deterministic tests, valid source-backed proposals pass, and no critic path writes a credit. These tests do not need Nightshift.

**Not in this task:** No requirement for a second LLM, independent critic service deployment or action execution.

**Implemented artifacts:** [pure critic](./dispute-demo/app/critic.py), [canonical tests](./dispute-demo/tests/test_proposal_critic.py), [retired writer shim](./dispute-demo/agent/critic.py), [compatibility tests](./dispute-demo/agent/tests/test_critic.py), and [critic reference](./dispute-demo/docs/critic.md).

**Acceptance, 27 October 2026:** 22 new critic tests cover all 40 authored scenarios and adversarial proposals using real typed policy outputs; every result branch runs with I/O blocked. Full main suite: 112 collected, 92 passed, 20 PostgreSQL opt-in skips. Four compatibility tests and data validation pass. No critic action writes; existing SQLite state is preserved. Rationale support is deliberately limited to deterministic policy explanations. No live service or action integration is claimed.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T07 — Implement the investigator through Nightshift

**Phase:** Agent workflow  
**Status:** DONE
**Depends on:** T02, T03, T06  
**Deliverable:** A reasoning agent that proposes a supported outcome and can request approved evidence.

**Read first:** Existing check_nightshift.py and actual supported client/API, T01 schemas, T02 tools and T06 feedback.

**PR #4 integration requirements:**

- [x] `dispute-demo/agent/resolver.py::_policy_proposal()` is deterministic, not a Nightshift investigator. Reuse only as a labelled test/fallback helper; build genuine typed model proposals/tool requests for all four outcomes and one correction.
- [x] Record a separately labelled real structured inference result when available; mocks/probes do not establish the live investigator or actual responder identity. Retain untrusted-text handling and no direct writes/policy overrides.

**Work:**

- [x] Reuse working authentication and connection conventions. Confirm the actual supported structured-response/tool interface; do not assume an API feature from the connectivity probe.
- [x] Give the investigator case facts, deterministic policy results and authorized source-linked context. Include a small investigation-plan/checklist in this role rather than adding a separate manager LLM.
- [x] Accept either a typed request for an allowlisted read tool or a typed final proposal. If native tool calling is unavailable, use an explicit structured request envelope validated and executed by the orchestrator.
- [x] Require outcome, proposed amount when relevant, evidence/rule IDs, uncertainty or missing requirements, and a concise source-grounded rationale. Do not request or expose hidden chain-of-thought.
- [x] Handle malformed output, timeouts and unsupported tool requests without side effects. Treat evidence documents and recalled text as untrusted case material, not operational instructions.
- [x] Record requested route and actual responding provider/model only when returned or independently evidenced. Do not label meterless/auto as proof of a particular model.

**Acceptance gate:** Stubbed tests cover schema failures, unauthorized tool requests and correction feedback. A separately labelled live Nightshift test returns a usable proposal when available. Expected-result fixtures never enter prompts.

**Not in this task:** No arbitrary SQL, direct writes, hard-policy overrides, separate planner agent or claimed model identity without evidence.

**Implemented artifacts:** [investigator](./dispute-demo/app/investigator.py), [bounded transport](./dispute-demo/app/nightshift.py), [investigator tests](./dispute-demo/tests/test_investigator.py), [transport tests](./dispute-demo/tests/test_nightshift.py), [read-only live probe](./dispute-demo/integration/check_investigator.py), [interface guide](./dispute-demo/docs/investigator.md) and [live evidence](./dispute-demo/docs/evidence/t07-live-DP-0014.json).

**Acceptance, 27 October 2026:** 16 stubbed investigator tests plus 12 transport tests pass, including five real local HTTP fixture checks. Full suite: 166 collected, 121 passed, 45 PostgreSQL opt-in skips; four compatibility tests/data validation pass. Real Zetaris DP-0014 → Nightshift proposal → pure critic accepted 6,000 SGD minor units; response model label `nvidia/nemotron-3.5-bolt-e4b`, requested route `meterless/auto`. No persistence, fixture fallback or hidden reasoning. Shared deployment/freshness and the bounded write workflow remain T08.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T08 — Wire the bounded workflow and command-line runner

**Phase:** Agent workflow  
**Status:** DONE
**Depends on:** T02, T03, T05, T06, T07  
**Deliverable:** The first working end-to-end investigation with an observable audit trail.

**Read first:** All tested interfaces from T01–T07 and the repository entrypoint conventions.

**PR #4 integration requirements:**

- [x] Replace the prototype resolver as the normal-runtime path with one canonical controller and explicit run/proposal/reference identities. Handle all four outcomes without blanket manual approval and invalidate earlier results when verified facts change.
- [x] A critic review verdict cannot commit its rejected credit proposal. Validate a safe allowed review proposal through the action boundary or report no-credit failure; show queued review only after successful persistence.
- [x] Support a labelled no-memory milestone until T10. `remember=False` currently disables saving only; neither mode may silently call the SQLite writer. Configure tool/model/duration limits and at most one correction.
- [x] Return confirmed commit independently of optional post-commit work. Memory saving errors must not hide the action result or trigger a repeated action.

**Work:**

- [x] Implement a Python workflow controller: retrieve -> evaluate -> investigate -> validate -> commit -> display. The controller, not an LLM, controls transitions and write access.
- [x] Execute only validated allowlisted tool requests. Merge newly verified facts into context and rerun the policy evaluator before validating a proposal based on them.
- [x] Use at most one proposal-correction pass for the MVP. Define explicit tool-call, timeout and total-run budgets in configuration; no endless retries or loop resets.
- [x] On unresolved critique or unavailable required facts, construct an honest no-credit error/review outcome. Persist a review decision only when the write service confirms it. Never relabel failed persistence as saved.
- [x] Add a CLI accepting a real synthetic dispute ID. Show facts, rules, proposal, critic feedback and commit status; differentiate reused results from new simulated effects.
- [x] Record a public event trace with source and rule IDs, versions, actions and errors. Use scripted faulty proposals only in explicitly labelled fault-injection tests/demos.

**Acceptance gate:** A live Zetaris + Nightshift case reaches a persisted sandbox result; reprocessing causes no extra credit; a faulty proposal is corrected once or routed safely. Unit/mocked runs are clearly distinguished from live integration evidence.

**Acceptance, 27 October 2026:** 198 tests pass with no skips (52 real isolated PostgreSQL checks and five local HTTP fixtures), plus four compatibility tests and data validation. Live Zetaris → Nightshift → critic → PostgreSQL committed DP-0014 for 6,000 SGD minor units. Identical recovery reused the original decision; ordinary rerun rejected an existing credit; a labelled faulty proposal consumed one correction then failed safely on invalid output. Shared counts remain one decision/credit/audit. [Live evidence](./dispute-demo/docs/evidence/t08-live-workflow.json), [deployment receipt](./dispute-demo/docs/evidence/t08-deployment.json), [workflow guide](./dispute-demo/docs/workflow.md).

**Not in this task:** No dashboard requirement, autonomous agent swarm, unlimited loop or claim of memory use before T10.

**Suggested paths/artifacts:** Proposed: dispute-demo/app/orchestrator.py, dispute-demo/app/main.py, dispute-demo/tests/test_orchestrator.py, dispute-demo/tests/test_end_to_end.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T09 — Verify and wrap the actual H-MEM integration

**Phase:** Memory and presentation  
**Status:** NOT_STARTED  
**Depends on:** T00, T01; may run in parallel with T02–T08  
**Deliverable:** A tested adapter to the selected real H-MEM implementation, with source-linked persistence.

**Read first:** Approved H-MEM specification/reference example discovered in T00 and current installed configuration.

**PR #4 integration requirements:**

- [ ] Reuse `hmem_client.py`, `hmem_bridge/server.ts` and relevant tests under `dispute-demo/agent/`. Verify/pin the selected reference source, Node/tsx runner and dependency setup; document configurable paths and sanitized examples rather than assuming a sibling install.
- [ ] Bound subprocess time; validate JSON/output and sanitize errors. Report missing dependencies explicitly, without exposing private paths/credentials or raw stderr to analysts.
- [ ] Prove actual save → new process/restart → recall and customer isolation. Test/document serialized or otherwise safe access to the file-backed reference against concurrent lost updates; subprocess-per-operation alone is insufficient.
- [ ] Retain decision/dispute/customer IDs, source reference, policy version and timestamps; distinguish committed summaries from unverified notes. Offline mocks and reference-dependent integration tests must be separately selectable and labelled.

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
**Deliverable:** A later case uses source-verified memory under the advisory default; binding history-rule behavior and the final acceptance scope require the explicit decision below.

**Read first:** H-MEM adapter, authoritative customer-history tools, both existing policies (no numeric history rule), the explicit scope decision below and orchestrator.

**PR #4 integration requirements and pending scope decision:**

- [ ] Reuse `memory_service.py` but verify remembered IDs, ownership, cutoff and committed outcomes through T02 tools. Ignore/reject false, stale, future or cross-customer references with a visible trace. A stored `verified` tag is insufficient.
- [ ] Keep verified history advisory; do not adopt the three-claim default. Before closing T10, confirm an advisory MVP acceptance revision or obtain an explicit binding rule specifying distinct-case count, lookback, anchor, reason categories, qualifying outcomes, exclusions and precedence. A new rule needs separate approval, versioned policy and tests; existing v1/v2 fixtures retain their meaning.
- [ ] Save final summaries only from confirmed `committed`/`reused` decisions, idempotently by decision ID. Critic acceptance alone cannot authorize a final memory. Repeated runs must not inflate distinct counts; memory retry never calls the action service.

**Work:**

- [ ] Recall permitted context before the final policy/proposal stage, then resolve its source references through approved authoritative retrieval. Raw memory must not alter eligibility by itself.
- [ ] Pass verified history into policy evaluation. If no repeated-claims threshold is defined in the policy, record the gap and obtain an explicit synthetic-policy design decision rather than guessing a count.
- [ ] Demonstrate verified history as advisory context, or enforce a separately approved binding rule across policy, critic and commit-time checks. Repeated claims alone do not establish fraud.
- [ ] After a successful decision commit, save its permitted source-linked summary. Report pending/failed memory persistence separately from decision success; retries reuse the decision ID.
- [ ] Test stale/incorrect memory and missing source references. When memory is unavailable, continue only if required authoritative facts and policy gates are still satisfied; otherwise fail safely without credit.

**Acceptance gate:** A second investigation visibly recalls/verifies prior records, remains safe with false/stale/missing memory, and survives restart. Memory-save failure leaves the confirmed decision result intact and never reruns the action; recall failure permits automation only when all required authoritative policy facts remain available. The original source-defined history-rule requirement is unresolved until a binding rule is explicitly approved or an advisory-scope acceptance revision is approved. This alignment adopts an advisory working default but does not close that gate.

**Not in this task:** No automatic fraud finding, memory-defined policy, duplicate action during memory retries or unsupported rule threshold.

**Suggested paths/artifacts:** Proposed: changes to dispute-demo/app/orchestrator.py, dispute-demo/app/memory_adapter.py, dispute-demo/app/policy_engine.py as needed; dispute-demo/tests/test_memory_workflow.py. Reuse existing equivalents; these paths are not verified as present.

**Stop:** report evidence, update this task's status and the work log, then stop. Do not automatically start the next task.

### T11 — Build the thin analyst view and review queue

**Phase:** Memory and presentation  
**Status:** NOT_STARTED  
**Depends on:** T08; memory display depends on T10  
**Deliverable:** A simple analyst-facing page over the tested workflow, not a second implementation.

**Read first:** The CLI/orchestrator interface, stored decision/review data and existing UI conventions.

**Post-merge alignment requirements:**

- [ ] Show four business outcomes, critic verdict and persistence status separately, with citations and missing categories. Do not add a fifth business outcome for queue lifecycle.
- [ ] Show advisory history as context rather than a mandatory hold or fraud finding. No compulsory Approve click for ordinary policy-permitted outcomes; only actually persisted review cases are queued. Keep manual adjudication/writeback outside the MVP unless assigned.

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

**PR #4 integration requirements:**

- [ ] Explicitly collect `dispute-demo/tests/` and `dispute-demo/agent/tests/` during migration and smoke-test runtime package imports without test-only path injection. Consolidate deliberately; a green root suite must not hide uncollected prototype tests. Establish offline collection in earlier affected tasks too.
- [ ] Include four-outcome serialization/persistence, missing/unusable evidence, mandatory-review no-credit behavior, source-verified history, false/cross-customer/future recall, non-credit re-review, changed-payload retries, source-writer concurrency, lost acknowledgement and post-commit memory failure/retry.
- [ ] Keep reference-dependent H-MEM and live PostgreSQL/Zetaris/Nightshift checks separate from offline mocks; record exact interpreter, collection/pass/fail/error/skip counts and NOT RUN blockers. Reset only intentional isolated demo state, never source/shared data.

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

**Post-merge alignment requirements:**

- [ ] Demonstrate autonomous eligible credit, evidence request and decline, plus policy-required no-credit review using inspected fixture/source IDs. Add duplicate prevention, one bounded correction and real memory continuity when verified.
- [ ] Label prototype, live/model, reference H-MEM, sample, mock, fault-injection and no-memory modes truthfully. Merged source or a connectivity probe does not prove a complete agent or named responder. Cursor remains an optional development tool unless A01 records a conflicting requirement.

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
- [ ] Explicitly check whether human approval or a specific memory implementation/behavior is mandated. Selective review is the project's product direction, not a confirmed competition rule; reconcile any conflict before claiming compliance.
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

### 2026-10-27 — Post-merge documentation alignment only (section 7)

- Scope/owner: Codex, following the user's explicit local-only section 7 assignment from external `CODEX_POST_MERGE_ALIGNMENT_2026-10-27.md`. This is not a new roadmap task and does not reopen T00. Later implementation/run instructions in the handoff were not executed.
- Baseline: clean `main`, HEAD `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`, exactly the reviewed PR #4 merge. `git diff --stat 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29 HEAD` was empty. No newer local changes needed reconciliation. GitHub `fetch_pr` confirmed PR #4 merged to `main` with that merge SHA, nine new files and the retrieval modification (10 paths). No fetch/reset/checkout, commit, push or merge was performed.
- Reading/source evidence: completed root `AGENTS.md` → full context/roadmap/agent reading, supplied handoff, README/TEAM_SETUP and scoped onboarding instructions. Inspected all PR #4 modules/tests/bridge files, current retrieval, T01 schema/reference and relevant source-policy/generator/test definitions. Findings are source observations; no prototype was executed. The initial `rg --files dispute-demo docs ...` reported missing `docs/`, confirming the planning directory/file was new, not a missing pre-existing prerequisite; it was created for this deliverable.
- Files changed: `context.md`, `ROADMAP.md`, `README.md`, `agent.md`, `TEAM_SETUP.md`; newly created `docs/planning/JIRA_POST_MERGE_CHANGESET.md`. Root `AGENTS.md`/`CLAUDE.md` required no changes. No runtime, policy, data, fixture, configuration or nested checkout edits.
- Alignment delivered: recorded selective human review and four autonomous/permitted business outcomes with mandatory-review exclusion of credit; qualified PR #4 as existing prototypes with integration acceptance outstanding; mapped modules to stable tasks; added typed retrieval/history, pure critic, PostgreSQL all-outcome persistence/synchronization, bounded real investigator/controller, memory portability/provenance and complete test-discovery requirements. Cursor is optional. No policy threshold, new lifecycle or integration capability was claimed.
- Jira read-only evidence: `getAccessibleAtlassianResources`, then `searchJiraIssuesUsingJql` with `project = KAN AND labels = open-agent-hackathon ORDER BY key ASC`, fields `summary, description, status, assignee, parent, issuelinks, updated`, `maxResults=100`, `responseContentFormat=html`, `view=full`. Returned all 20 labelled issues, `isLast=true`. KAN-9/KAN-10 Done; KAN-11–KAN-23 and epics KAN-4–KAN-8 To Do; all unassigned, no issue links. Current descriptions/timestamps and exact proposed deltas are in the new preview. Proposed fields: descriptions only, with one explicit KAN-14 retry phrase replacement plus 13 addenda; summaries and all other fields unchanged. Jira edits are NOT APPLIED and require explicit approval, immediate fresh reads, rich-text preservation and read-back verification.

Verification from the repository root (documentation only; Python 3.12.5, standard library, no application imports):

| Exact command | Result / scope |
|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git log -3 --oneline` | Initial clean `main` at reviewed `76db772`; final status contains only the five modified documents and new planning file. |
| `git show --stat --oneline 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`; `git diff --stat 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29 HEAD` | 10 PR paths (1,023 insertions, 2 deletions); local HEAD equals reviewed source. |
| `python3 --version` | Python 3.12.5. This is the documentation-check interpreter, not a new application-runtime verification. |
| `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_post_merge_docs.py` | PASS after removing a trailing blank line from the new preview: 6 documents, 100 local Markdown links, 18 inventory paths and 10 PR paths; balanced fences/final newlines; unchanged 15-task IDs/mappings/statuses/dependencies and all prior work-log text; 13 exact Jira HTML description snapshots and all 20 summaries/timestamps checked against the read response; only six authorized documentation files changed. The temporary checker and response snapshot are session validation artifacts outside the repository. |
| `git diff --check` | PASS, exit 0; no changed-line whitespace errors. |
| `git diff --no-index --check -- /dev/null docs/planning/JIRA_POST_MERGE_CHANGESET.md` | No diagnostics after removing the initial extra EOF blank line. Exit 1 is the expected added-file difference, not a remaining whitespace error. |
| `git diff --exit-code HEAD -- dispute-demo getting-started zetaris-platform AGENTS.md CLAUDE.md` | PASS, exit 0; runtime/source/policy/data/tests/integration files, nested checkout references and entry points unchanged. |

- Application validation/tests, both application test roots, import execution, Zetaris/JDBC, PostgreSQL/SQLite, Nightshift inference/discovery, H-MEM reference/persistence, HackOS portal checks, migrations/reset and service startup: **NOT RUN** for this documentation-only scope. T00/T01 passing counts and service outcomes retain their 26 October dates; no new integration acceptance is asserted. External H-MEM prerequisites were documented from source, not installed or checked for availability.
- Remaining decisions: T10 must confirm advisory acceptance scope or an exact approved versioned history rule; T04/T05 must settle lifecycle/new-evidence re-review, cross-dispute duplicate scope and replay/freshness semantics; T09 must verify portable reference setup/persistence; A01 must confirm portal obligations. These do not block this local alignment or T02's typed retrieval with explicit unsupported states.
- `context.md` changed to reflect the assigned product direction and verified prototype locations, without altering historical evidence. T00/T01 remain DONE; T02–T13 and A01 remain NOT_STARTED. No new checkboxes marked complete.
- Recommended next implementation task: **T02 / KAN-11 only**, preserving JDBC and transaction `customer_id`, adapting scoped typed case/history reads and testing missing text, cutoff and failures. Not started. Stop after reporting this local alignment and requesting approval for the exact Jira preview.

### 2026-10-27 — Apply approved Jira description alignment

- Scope: the user answered “yes u may” to the exact KAN-11–KAN-23 description/acceptance preview, preserving summaries, statuses, assignees, task IDs and completed T00/T01. Authorization covers these descriptions only; no implementation, policy decision or Git publication was started.
- Preflight: re-read the required root guidance and approved change set; `git status --short --branch` showed the six existing alignment documents on `main`, and `git diff --exit-code HEAD -- dispute-demo getting-started zetaris-platform AGENTS.md CLAUDE.md` passed. Preserved all prior local edits. Runtime sources already inspected in the preceding alignment remained unchanged.
- API sequence: `getAccessibleAtlassianResources`; `executeRead(name=getContentFormatGuide, inputs={toolName: editJiraIssue})`; fresh `searchJiraIssuesUsingJql` with `project = KAN AND labels = open-agent-hackathon ORDER BY key ASC`, fields `summary, description, status, assignee, parent, issuelinks, updated, resolution, labels`, `maxResults=100`, HTML/full response. All 20 issues returned, no further page; 13 descriptions matched the preview.
- Each issue: `getJiraIssue` immediately before its edit; compare description/summary/updated timestamp; `editJiraIssue` with only `fields.description`, HTML input/output; `getJiraIssue` read-back. Appended the exact approved addendum once, preserving original rich text; KAN-14 additionally received the approved `retry reuse/block` → `identical-payload retry reuse; changed-payload rejection` replacement. No comments, assignments, transitions, links or other fields were submitted.
- Verification: all 13 saved descriptions match approved wording and structure. The first byte comparison for KAN-13 paused because Jira encodes apostrophes as `&#039;`; inspection confirmed equivalent serialization, and entity-normalized comparison passed. No corrective rewrite or duplicate addendum was needed. A final identical JQL read verified all 20 issues: protected fields unchanged, and KAN-4–KAN-10 descriptions/updated timestamps unchanged. T00/T01 remain Done; KAN-11–KAN-23 remain To Do. Per-issue timestamps are in `docs/planning/JIRA_POST_MERGE_CHANGESET.md`.
- Local records updated: the existing preview/application receipt, this work log, README's pending-approval text and context's Jira follow-up note. Task board/statuses/dependencies and all historical completion records retained.
- Local checks: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_post_merge_docs.py` — PASS, 6 documents, 100 local links, 18 inventory paths, 10 PR paths, fences/newlines and unchanged 15-task board/statuses/dependencies/history; `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/verify_jira_alignment_application.py` — PASS, 13 approved descriptions/single addenda/KAN-14 correction, 20 unchanged protected-field sets and 7 untouched issues, receipts matching read-backs. `git diff --check` and `git diff --exit-code HEAD -- dispute-demo getting-started zetaris-platform AGENTS.md CLAUDE.md` — PASS, exit 0. `git diff --no-index --check -- /dev/null docs/planning/JIRA_POST_MERGE_CHANGESET.md` — no whitespace diagnostics, expected exit 1 for an added file. Temporary validation scripts/read-response records remain outside the repository.
- Application tests, Zetaris/PostgreSQL/SQLite/Nightshift/H-MEM and HackOS live checks: **NOT RUN**; not needed for these approved Jira description edits. No runtime, policies, data, configuration, services, commits, pushes or merges changed.
- Remaining policy/lifecycle/portability/portal questions are unchanged. Recommended next implementation task: **T02 / KAN-11 only**, not started. Stop after this Jira follow-up.

### 2026-10-27 — Publish post-merge alignment and Jira change record

- Scope: the user's follow-up request to write a detailed commit message and push the completed documentation to `origin/main`. This separately authorizes Git publication; no implementation task or further Jira edit is included.
- Remote baseline: `git fetch origin` passed after the sandbox denied writing `.git/FETCH_HEAD` and the authorized retry succeeded. `git rev-list --left-right --count origin/main...HEAD` returned `0 0`; local `main` and `origin/main` both remain at reviewed merge `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29` before publication.
- Files prepared: `README.md`, `ROADMAP.md`, `TEAM_SETUP.md`, `agent.md`, `context.md` and new `docs/planning/JIRA_POST_MERGE_CHANGESET.md`. The detailed commit describes the prototype inventory, integration acceptance requirements, setup clarifications, exact approved Jira changes and verification evidence. Temporary validation scripts and Jira response records stay outside the repository.
- Documentation validation: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_post_merge_docs.py` — PASS: six documents, 100 local links, 18 inventory paths and 10 PR paths; unchanged task IDs, statuses, dependencies and prior history. `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/verify_jira_alignment_application.py` — PASS against the saved API read-backs: 13 approved descriptions, 20 unchanged protected-field sets, seven excluded issues untouched and receipts matching. This is a local evidence check, not a new live Jira audit.
- Whitespace/scope checks: `git diff --check` — PASS, exit 0; `git diff --no-index --check -- /dev/null docs/planning/JIRA_POST_MERGE_CHANGESET.md` — no diagnostics, expected exit 1 for the added file; `git diff --exit-code HEAD -- dispute-demo getting-started zetaris-platform AGENTS.md CLAUDE.md` — PASS, exit 0. Application source, policies, data, tests, configuration and nested checkout references are unchanged.
- Application tests and live Zetaris/PostgreSQL/SQLite/Nightshift/H-MEM/HackOS checks: **NOT RUN** for this documentation publication. No new runtime capability is claimed. `context.md` needs no further architecture/status change.
- Publication uses an explicit six-file commit and normal `git push origin main`, without force. The commit identity, staged checks, push result and remote verification are reported after execution rather than asserted in advance.
- Recommended next implementation task: **T02 / KAN-11 only**, not started. T00/T01 remain DONE; all remaining task statuses and acceptance gates are preserved.

### 2026-10-27 — T02 / KAN-11: typed case and history retrieval

- Status: **DONE** against the repository T02 acceptance gate. Owner: Codex, following the user's explicit “move on to T02” assignment. T03 was not started. Jira was not transitioned or edited, and no commit, push or merge was performed for this implementation.
- Baseline: clean `main` at `b850ae8775d61ecb3b3e6737ed84f58861d45bbc`; created local branch `codex/t02-typed-retrieval` per TEAM_SETUP. Read root/scoped instructions, T01 contracts/tests, retrieval/schema/loader, source policies, generator/validator, memory prototype and applicable JDBC guides. The 21 T01 contract tests passed before editing.
- Runtime files: extended `dispute-demo/integration/get_dispute_context.py`; added `dispute-demo/app/tools.py`. Tests: added `dispute-demo/tests/test_tools.py`. Documentation: added `dispute-demo/docs/retrieval.md`; updated `README.md`, `TEAM_SETUP.md`, `context.md`, this roadmap and the T01 reference's follow-up note. T01 schemas, prototype runtime modules, source policies/data/fixtures, generators, configurations and nested checkouts are unchanged.
- Delivered: strict typed case mapping with source metadata and transaction customer IDs; separate authoritative customer history; current source-state reads; explicit unsupported decision reads. Four allowlisted tool names are bound to a trusted application-selected dispute, with exact argument validation and no model SQL/customer/cutoff/path/connection controls.
- Visibility/input handling: SQL restricts record scope; parsed UTC timestamps preserve inclusive cutoffs and fractional-second correctness before raw dictionaries are returned, with independent typed checks afterward. Policy selection is by opening date. Evidence text is left-joined; absent/blank/unreadable/incomplete text retains metadata as `content=None` and explicit issues. Missing policy cannot create a fabricated context version. Query overflow, malformed data, not-found and backend failures are distinct.
- JDBC behavior: reuses the configured bundled helper/connection. Its `run` method swallows fetch errors, so the adapter uses its cursor directly for bounded fetches and preserves sanitized failure status. Each query requests at most 1,001 scoped candidates; more than 1,000 is incomplete, not truncated success. All paths close the connection; no installs, service startup, source writes, migrations or resets occurred.

Exact verification commands, Python 3.13.7; working directory `dispute-demo/` unless specified:

| Command | Actual result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p 'test_schemas.py' -v` | Baseline PASS: 21 tests, zero failures/errors/skips. |
| From `getting-started/`: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/preflight.py --jdbc` | JDBC PASS: configured JAR/JDK/venv, port, `SELECT 1`, datasource `dispute`, Lightning databases NY_TAXI/TPCDS_DB. Overall exit 1 is two REST-only failures (unset API key and REST initialization); the connection guide explicitly permits JDBC to proceed. No endpoint/credential changes. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` | Final PASS: **50 tests**, zero failures/errors/skips: 27 retrieval, 21 contracts and 2 generation. All 40 source cases map/round-trip; all 40 customer histories checked against isolated source data. Covers cutoff, fractional seconds, ownership, missing text, malformed rows/money/JSON, policy version selection, query/fetch/close failures, overflow, unsupported decisions and tool rejection. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p 'test_critic.py' -v` | PASS: **6 tests**, zero failures/errors/skips. Existing prototype tests use mocked policy and temporary SQLite; this is regression evidence, not PostgreSQL action acceptance. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | PASS: 42 transactions, 54 settlements, 40 disputes, 81 evidence rows, 16 rules; document/manifest hashes and fixture references unchanged. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -c "exec(compile(open('/private/tmp/verify_t02_live.py').read(), '/private/tmp/verify_t02_live.py', 'exec'))"` | Live read-only PASS: DP-0014, DP-0019, DP-0033/DP-0034 contexts, source history/state, missing DP-9999, strict JSON round-trips and unsupported decision response. The temporary checker imports only the runtime read tools, not source CSVs or expected-result fixtures. Its assertions are summarized below. |
| From repository root: `git diff --exit-code b850ae8 -- dispute-demo/app/schemas.py dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/tests/fixtures dispute-demo/agent getting-started zetaris-platform AGENTS.md CLAUDE.md` | PASS, exit 0: protected contracts/source/policy/data/prototype/entry-point paths unchanged. |
| From repository root: `git diff --check` | PASS, exit 0. New-file whitespace and local documentation-link checks also passed before handover. |
| From repository root: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t02_docs.py` | PASS: 6 documents, 80 local links, balanced fences/final newlines; only T02 status advanced; all prior history retained; exactly 9 task files changed. `git diff --no-index --check` on the three new files had no diagnostics (expected exit 1). |

Additional import/collection check, run from `dispute-demo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python - <<'PYCODE'
import sys
before = list(sys.path)
import app.tools
import integration.get_dispute_context
assert sys.path == before
assert 'jaydebeapi' not in sys.modules
assert not any('expected_results' in name for name in sys.modules)
print('PASS: package imports without path injection, JDBC initialization or fixture imports')
import unittest
suite = unittest.defaultTestLoader.discover('agent/tests')
assert not unittest.defaultTestLoader.errors, unittest.defaultTestLoader.errors
print('Prototype collection:', suite.countTestCases(), 'tests; external H-MEM tests collected only, NOT RUN')
PYCODE
```

- Result: package import checks PASS; 13 prototype tests collected with no import errors. Six offline critic tests ran separately; seven external-reference H-MEM tests were **NOT RUN**. The current prototype imports/test setup remains T09/T12 integration work; T02's runtime packages import without test path injection.
- Live assertions: DP-0014 has 1 transaction, 2 settlements (10,000 capture, 4,000 refund), 2 evidence items and 8 v2 rules. DP-0019 exposes only 1 visible evidence item. DP-0033 selects v1 and DP-0034 v2 at the opening boundary. DP-0014 history identifies CUST-008 and prior DP-0030/DP-0017 with ownership/cutoff checks; current status is `open`. Unknown DP-9999 yields `not_found`. Decision read returns `unsupported` without SQL. All typed source revisions remain null. The separate initial DP-0014 typed live probe also passed.
- Initial tooling correction: the first test-file write used a duplicated relative directory, so discovery found zero tests and exited 5; the path was corrected before any passing test claim. A failed patch attempt made no changes. Final counts above supersede intermediate runs.
- Remaining limits: no revision guard/coherent multi-read snapshot, no decision storage/registration, no historical versioning of source dispute status/text. History is advisory source data, not committed decisions or fraud inference. These are explicit T04/T05/T10 boundaries and do not block T02's read acceptance. Policy evaluation/complete-rule semantics remain T03 work.
- Nightshift, H-MEM reference execution, direct PostgreSQL action/concurrency tests and HackOS checks: **NOT RUN**; outside T02. SQLite writes occurred only in isolated test databases, never source/shared state.
- `context.md` updated for verified T02 capability and limitations; README now hands over T03. T00/T01 remain DONE; T03–T13 and A01 remain NOT_STARTED. Recommended next task: **T03 / KAN-12 only**, not started.

### 2026-10-27 — Close KAN-11 and prepare T02 publication to main

- Scope: the user's explicit follow-up to update Jira, write a detailed commit message and push completed T02 to `origin/main`. No new implementation task started; the nine T02 files are the entire publication scope.
- Remote check: `git fetch origin` passed with authorized Git/network access. `git rev-list --left-right --count origin/main...HEAD` returned `0 0`; local `main`, `origin/main` and the task branch still share baseline `b850ae8775d61ecb3b3e6737ed84f58861d45bbc` before committing.
- Fresh verification from `dispute-demo/`, using Python 3.13.7: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` — PASS, 50 tests; `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p 'test_critic.py' -v` — PASS, 6 tests; both zero failures/errors/skips. `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` — PASS: 42 transactions, 54 settlements, 40 disputes, 81 evidence rows/documents, 16 rules and integrity/fixture checks.
- Repository-root checks: `git diff --check`; `git diff --exit-code b850ae8 -- dispute-demo/app/schemas.py dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/tests/fixtures dispute-demo/agent getting-started zetaris-platform AGENTS.md CLAUDE.md`; `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t02_docs.py` — all PASS. Documentation validation checked six documents, 80 local links, balanced fences/newlines, only T02 status advanced, retained prior history and exactly nine task paths. New-file whitespace checks produced no diagnostics.
- Jira: authenticated pre-read confirmed KAN-11 To Do, unassigned, no comments, with its approved description intact. Added implementation/test/live-evidence comment `10003`, then used available transition `31` to Done. The response and read-back confirmed status and resolution Done at `2026-10-27T02:40:02.402+0800`, one comment, and unchanged summary, description, assignee, parent, labels and issue links. No other issue was edited.
- Current handover/context notes now record the verified Jira closure. Earlier implementation and alignment entries retain their historical states. Runtime code did not change during this publication follow-up; the preceding T02 live JDBC evidence applies to the same sources. Live Zetaris/PostgreSQL/Nightshift/H-MEM/HackOS checks were **NOT RUN** again for publication.
- Publication uses an explicit nine-file commit with a detailed behavior/validation/limitations message, followed by a fast-forward of local `main` and normal `git push origin main`. Commit identity, staged checks, push outcome and remote verification are reported after execution rather than asserted in advance. Temporary check scripts and API receipts remain outside the repository.
- Recommended next task: **T03 / KAN-12 only**, not started. Source revisions and decision reads remain explicitly unsupported; no policy, source data, action storage or memory behavior changed in this follow-up.

### 2026-10-27 — T03 / KAN-12: deterministic evaluator; live acceptance blocked

- Status: **BLOCKED**, implementation/offline verification complete; actual Zetaris-context evaluation remains required. Owner: Codex, user-assigned T03 only. Baseline clean `main` / `origin/main` at `3106cd5`; branch `codex/t03-policy-evaluation`. T01/T02 prerequisites inspected against schemas, retrieval, source policies, generator and tests; baseline 50 tests passed.
- Changed runtime: added `dispute-demo/app/policy_engine.py`; replaced the prototype `agent/policy_engine.py` with a dictionary-to-typed delegating adapter. Added `tests/test_policy_engine.py` and `docs/policy.md`; updated README, TEAM_SETUP, context, contract reference and this log. No schema, source-data, fixture, retrieval, critic/resolver writer or memory changes.
- Behavior: exact supplied v1/v2 policy validation; immutable reference/cutoff binding; first-terminal precedence and explicit dispositions for all four outcomes; primary-only integer balance/claim cap; failed movements excluded, pending/negative/inconsistent balances reviewed; precise 30/45-day and 20,000-cent boundaries. Legacy output names are translated at the adapter, not treated as merchant refunds. No history threshold, fixture lookup, model call, action write or extra evaluator.
- Evidence interpretation: recognize complete generated templates and source metadata, not labels/substrings. Missing required text becomes an explicit category request; additional uninterpretable evidence requires review. Known T02 unavailable-text diagnostics are resolved through evidence rules, while all other input issues remain fail-closed. Multiple captures, refunded duplicate companions and non-open lifecycle states are conservatively unsupported; these limits are documented rather than treated as new policies. Contracts and source policies are unchanged.
- Exact commands from `dispute-demo/`, Python 3.13.7: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` — **PASS, 70 tests**, 0 failures/errors/skips; `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` — **PASS, 6 tests**, 0 failures/errors/skips; `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` — **PASS**, 42 transactions, 54 settlements, 40 disputes, 81 evidence rows/documents, 16 rules, unchanged hashes/fixture integrity.
- The 20 new tests cover all 40 independently authored outcomes/amounts/citations/reasons, microsecond filing boundaries in both versions, threshold ±1, primary/companion arithmetic, pending/failed/refund/reversal data, malformed policy/inputs, contradictory/missing/unusable/injected text, cutoff/version rules, serialization and purity. Offline SQL tests use isolated SQLite, not live Zetaris. Existing critic tests mock policy and use temporary SQLite, not PostgreSQL action acceptance.
- Import/collection command from `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -` with assertions that importing `app.policy_engine` and `agent.policy_engine` leaves `sys.path` unchanged and does not import `jaydebeapi` or `sqlite3`, then `unittest.TestLoader().discover('agent/tests')` — **PASS**; 13 prototype tests collected, no import errors. The 7 external H-MEM tests were collected only, **NOT RUN**.
- Live preflight from `getting-started/`: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/preflight.py --jdbc` — initial sandbox attempt failed with Operation not permitted; approved retry failed with **connection refused** on local port 10000. Driver JAR, JDK, venv and JayDeBeApi present. REST also failed because API key is unset. This is current unavailability, not T02 live acceptance regression evidence. The scoped connection instructions require stopping live work; startup of the existing stack was requested, pending response.
- Live policy evaluation command, **NOT RUN** until preflight passes: from `dispute-demo/`, `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.policy_engine DP-0014`. The runner uses real T02/JDBC only and reports structured retrieval failure without a fixture fallback. No source records changed. Nightshift, H-MEM execution, action/concurrency tests and HackOS checks: **NOT RUN**, outside T03.
- Final repository checks: `git diff --check` — PASS after removing a newly edited status line's trailing Markdown spaces. `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t03_docs.py` — PASS: 6 documents, 90 local links, balanced fences/final newlines, all 15 task mappings/dependencies retained, only T03 status changed, prior work log preserved. `git diff --no-index --check -- /dev/null` for each new evaluator/test/reference file produced no diagnostics (expected exit 1 for new-file differences).
- Protected-source check: `git diff --exit-code 3106cd5 -- dispute-demo/app/schemas.py dispute-demo/app/tools.py dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/integration dispute-demo/tests/fixtures dispute-demo/agent/critic.py dispute-demo/agent/resolver.py dispute-demo/agent/memory_service.py dispute-demo/agent/hmem_client.py dispute-demo/agent/hmem_bridge getting-started zetaris-platform AGENTS.md CLAUDE.md` — PASS, exit 0. Exactly nine task paths changed; no source or prototype state migration.
- Tooling corrections: an initial test-file write and initial documentation write used a duplicated relative directory and wrote nothing. Corrected paths before validation; the first test command collected zero tests (exit 5), superseded by the passing final 70-test run above.
- Jira and Git publication: no Jira edits, commits, pushes or PRs authorized/performed. Existing sources, prototype state and services preserved. `context.md` records implemented versus acceptance-blocked capability. Finish T03 live acceptance next; recommend T06 / KAN-15 only afterward, not started.

### 2026-10-27 — T03 live acceptance completed after authorized service startup

- Status: **DONE** against the T03 repository gate. The user explicitly approved starting the existing local stack. This completes the preceding blocked attempt; no next task, Jira edit or Git publication started. Runtime sources are unchanged from the passing 70-test / 6-test offline run.
- Startup: `docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'` initially failed because Docker Desktop was stopped. `open -a Docker` launched the existing installation; the four persistent Zetaris services automatically restarted. `bash dispute-demo/integration/db.sh start dispute-postgres` started the existing source PostgreSQL container. Subsequent `docker ps -a --format '{{.Names}}\t{{.Status}}'` confirmed the dispute database and Zetaris postgres/driver/api/ui healthy; init/bootstrap remained exited successfully. No pulls, installs, container recreation, config changes, source loads, migrations or resets.
- From `getting-started/`: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/preflight.py --jdbc` — **JDBC PASS**: port, Java/JAR/Python dependencies, `SELECT 1`, datasource `dispute`, Lightning databases NY_TAXI and TPCDS_DB. Overall exit 1 is the two REST-only checks for the unset API key; the connection guide explicitly permits JDBC to proceed. Existing SLF4J no-binding warnings did not affect queries.
- From `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m app.policy_engine DP-0014` — **PASS, exit 0**, source channel `zetaris`, read status `ok`, v2, 6,000-minor-unit credit cap, matched `v2-APPROVE`, evidence EV-0027/EV-0028, completed movements ST-0021/ST-0022 (10,000 capture, 4,000 refund). This is read-only eligibility, not a recorded credit.
- From `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -c "exec(compile(open('/private/tmp/verify_t03_live.py').read(), '/private/tmp/verify_t03_live.py', 'exec'))"` — **PASS, exit 0, eight actual JDBC contexts**. The temporary assertion script imports only runtime read tools/evaluator/schemas, not CSVs or expected-result fixtures. It checks all four outcome partitions, exact credit caps, selected version/rule, later rules not evaluated, citation membership, exact reference binding and JSON round-trip. Source revisions remain null; no freshness or persistence claim.

| Live case | Result | Matched rule / amount |
|---|---|---|
| DP-0014 | provisional_credit | v2-APPROVE / 6,000 SGD minor units |
| DP-0019 | request_evidence | v2-MISSING_EVIDENCE / absent refund_confirmation |
| DP-0024 | human_review | v2-CONFLICTING_EVIDENCE |
| DP-0029 | decline | v1-FILING_WINDOW |
| DP-0008 | human_review | v2-REVIEW_THRESHOLD |
| DP-0003 | provisional_credit | v2-APPROVE / exactly 20,000 SGD minor units |
| DP-0033 | decline | v1-FILING_WINDOW, opening immediately before v2 |
| DP-0034 | provisional_credit | v2-APPROVE / 10,000 SGD minor units, opening at v2 boundary |

- Updated current README, context, roadmap, setup notes and policy/contract references to reflect acceptance. The earlier blocked log remains historical evidence. Existing local stack is left running as authorized. Offline suites were not redundantly rerun because runtime files did not change; their recorded 70 + 6 passing results and data validation remain applicable.
- NOT RUN: Nightshift, H-MEM execution, PostgreSQL action/concurrency checks and HackOS. These are outside T03. REST remains unconfigured; JDBC acceptance is complete. No model calls, action writes or memory writes occurred.
- Final documentation/scope checks: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t03_docs.py` — PASS, 6 documents, 91 local links, balanced fences/newlines, unchanged 15 task mappings/dependencies and prior history, only T03 advanced to DONE. `git diff --check` and the preceding protected-source `git diff --exit-code 3106cd5 -- ...` command both passed. Still exactly nine T03 paths changed; no runtime edits in this service-startup follow-up.
- Remaining limits: bounded synthetic evidence interpretation; unsupported generalized ledger/lifecycle cases require review; source revision/commit freshness and canonical persistence remain T04/T05. Recommended next task: **T06 / KAN-15**, not started. All T03 changes remain local and uncommitted; Jira is unchanged.

### 2026-10-27 — Publish and merge T03 through a pull request

- Scope: the user explicitly requested a commit on `codex/t03-policy-evaluation`, a PR targeting `main`, and its merge. This authorizes publication/merge only; no next roadmap task or Jira edit.
- Remote baseline: `git fetch origin` passed; `git rev-list --left-right --count origin/main...HEAD` returned `0 0` at `3106cd5`. GitHub confirmed push permission and no existing open PR for this head/base pair.
- Fresh checks from `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` — PASS, 70 tests; `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` — PASS, 6 tests; both zero failures/errors/skips. `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` — PASS, all source counts/hashes/fixture checks.
- Repository checks: `git diff --check`, the protected-source check recorded above, and `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t03_docs.py` passed (six documents, 91 local links, task mappings/dependencies and historical logs preserved). Only the nine T03 implementation/test/documentation paths are included.
- Runtime sources are unchanged from the eight successful live JDBC evaluations above. Live application checks were NOT RUN again for publication; no new integration capability is claimed.
- Publication uses an explicit nine-file commit, `git push --set-upstream origin codex/t03-policy-evaluation`, then a GitHub PR and normal merge with an expected-head check after reviewing CI/mergeability. Commit/PR/merge identifiers and remote verification are reported after execution rather than asserted in advance. T03 remains DONE; T06 / KAN-15 is recommended and not started.

### 2026-10-27 — T04 / KAN-13: PostgreSQL decision, action and audit storage

- Status: **DONE** against the T04 repository gate. User explicitly assigned T04; no other roadmap task was started. Baseline clean `main` at `b64c21d18df1ccd8cc93e507eeb937ea5fb7e7c1` (merged T03 PR #5); local branch `codex/t04-decision-storage`. T01 source/contracts inspected and its 21 tests passed before edits. No Jira edits, commits, pushes or PRs in this task.
- Added `dispute-demo/db/migrations/001_decision_storage.sql`, `tests/test_decision_storage.py`, `docs/storage.md`; modified `integration/load_data.py` to refuse initial loading into a guarded database. Updated README, TEAM_SETUP, context, roadmap and contract/retrieval handoffs. No changes to source data, policies, fixtures, canonical schemas/evaluator/retrieval, prototype runtime/state, private configs or nested checkouts.
- Delivered: append-only investigations and decisions with run/proposal/snapshot/cutoff/policy/revision references, full request JSONB and unique idempotency key; automatic transactional credit/reservations or review sidecars and audit events; non-credit NULL amounts, durable pending-review view, read-only public registration views. Composite FKs bind case/primary transaction and prevent credit/review sidecars on the wrong outcome. Identical-payload retry response logic remains T05, not a claimed storage feature.
- Lifecycle decisions under T04's assignment: source `open` status is preserved; new evaluations can append after evidence requests, declines or reviews, with a new snapshot, later revision, nondecreasing cutoff and a nonforking predecessor chain. Old reviews remain in history and leave the pending view when superseded. At most one credit per dispute/primary transaction; both linked charge IDs are reserved to block swapped duplicate-pair claims. No top-up/reversal/reissue; later non-credit review remains allowed. These are conservative storage safeguards, not changes to v1/v2 eligibility or an invented history threshold.
- Global guard: ALWAYS statement triggers lock/increment one revision before every covered source/action INSERT/UPDATE/DELETE/COPY/TRUNCATE, with atomic rollback. Dedicated unprivileged NOLOGIN owner/writer roles, fixed-search-path definer functions and restricted table/DDL/guard permissions enforce normal writer participation. The Compose bootstrap superuser remains a trusted migration administrator, never a permitted runtime credential; its initial loader refuses migrated databases. Tests use actual separate unprivileged logins.
- Freshness boundary: inserting a decision rejects future/pre-opening cutoffs and any currently authoritative scoped transaction, settlement or evidence after the cutoff. A test adds a later refund and supplies the latest revision with the old cutoff: zero decisions/effects. Backdated corrections, full policy/critic/source binding, stale-revision comparison and identical retry recovery remain T05 checks under the shared lock. No replay bypass or normal runtime write login is enabled. T02 remains null/unsupported until deployment, registration and uncached coherent reads are verified; read views plus the explicit handoff coordinate that work without claiming live JDBC freshness.

Exact verification from `dispute-demo/`, existing Python 3.13.7:

| Command | Actual result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_schemas.py -v` | Baseline PASS: 21 tests, zero failures/errors/skips. |
| `DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_decision_storage.py -v` | Final PASS: **20 real PostgreSQL tests**, zero failures/errors/skips, 30.130s. Existing `postgres:16-alpine` image, `--pull never`, unique container, no network/ports, own anonymous volume, fresh DB per test. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` | PASS: 90 collected, **70 passed, 20 explicitly skipped** without the PostgreSQL opt-in; zero failures/errors. The separate preceding run executes all 20, so skips are not substituted for PG acceptance. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` | PASS: **6** prototype regressions, zero failures/errors/skips. Mock policy/temporary SQLite, not canonical action-service evidence. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | PASS: 42 transactions, 54 settlements, 40 disputes, 81 evidence rows/documents, 16 policy rules; manifest/fixture validation unchanged. |

- PostgreSQL evidence: migration reproduces on every test database and preserves all six source tables byte-for-byte by sorted row hashes against the pristine test template. Reapplication fails atomically. Tests prove all four outcome sidecars, unique request/proposal/credit scopes, swapped-pair protection, no chain forks, non-credit/new-evidence re-review, queue supersession, immutable history, role/DDL/guard restrictions, COPY/TRUNCATE participation, rollback and old-cutoff rejection. Independent backend tests hold the guard and show settlement/text/policy writers timing out until release. A real restart of **only the disposable test container** retains the queued review, audit and revision. No claim of T05 full action concurrency/validation acceptance.
- Initial harness corrections retained as evidence: the first run collected zero tests and errored because readiness saw PostgreSQL's temporary socket-only bootstrap server before DB creation; switched to TCP readiness. The next 18-test run had three failed role-escalation subcases because a superuser session retains SET ROLE capability; replaced role-only impersonation with separate unprivileged logins. Final 20-test run above passed. Test containers/anonymous volumes were cleaned after each run.
- Live shared-source inventory command before/after (repository root): `bash dispute-demo/integration/db.sh exec -T dispute-postgres psql -X -U dispute_loader -d dispute_demo -At -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename; SELECT count(*) FROM transactions; SELECT count(*) FROM settlements; SELECT count(*) FROM disputes; SELECT count(*) FROM evidence; SELECT count(*) FROM evidence_documents; SELECT count(*) FROM policy_rules;"` — unchanged seven public tables and counts 42/54/40/81/81/16. Post-test schema check `SELECT count(*) FROM pg_namespace WHERE nspname IN ('dispute_control','dispute_actions')` returned **0**. These are read-only observations; no shared migration/load/reset/start/restart.
- `docker ps -a --filter label=dispute-purpose=t04-isolated-test --format '{{.Names}}'` returned no containers after cleanup. `docker ps --format '{{.Names}}\t{{.Status}}'` confirmed the five original persistent services still healthy. No images pulled or dependencies installed.
- NOT RUN: shared/demo migration, Zetaris registration/cache-coherence/read integration, Nightshift, H-MEM execution, T05 action-service/proposal validation and full concurrent-credit workflow. Those capabilities remain unavailable or outside T04; source revisions returned by current T02 remain null.
- Acceptance evidence and limits are documented in `docs/storage.md`; context updated for implemented storage and explicit deployment boundary. Recommended next task: **T06 / KAN-15**, not started. T05 will use this schema plus verified fresh reads and the pure critic.
- Final checks from repository root: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t04_docs.py` — PASS, seven documents, 103 local links, balanced fences/newlines, Python syntax, only T04 status advanced and all prior work-log text retained. `git diff --check` — PASS. `git diff --no-index --check -- /dev/null` for each new migration/test/storage-reference file — no diagnostics (expected exit 1 for new files). `git diff --exit-code b64c21d -- dispute-demo/app dispute-demo/agent dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/integration/get_dispute_context.py dispute-demo/integration/compose.yml dispute-demo/integration/registration.sql dispute-demo/integration/verify.sql dispute-demo/tests/fixtures dispute-demo/tests/test_generation.py getting-started zetaris-platform AGENTS.md CLAUDE.md` — PASS, protected source/state/config paths unchanged. Ten T04 paths changed; temporary validation helpers stay outside Git.
- Import/collection check from `dispute-demo/`: `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -` with assertions that importing `app.schemas`, `app.tools`, `app.policy_engine` preserves `sys.path` and does not initialize `jaydebeapi`, then `unittest.TestLoader().discover('agent/tests')` — PASS, 13 prototype tests collected without import errors. Six critic tests ran separately above; seven external H-MEM tests were collected only, NOT RUN.

### 2026-10-27 — Publish T04 for review against main

- Scope: the user's request to commit completed T04 on `codex/t04-decision-storage`, push the branch and create a PR targeting `main` on the existing origin. No new implementation task, database deployment or Jira edit.
- Remote baseline: `git fetch origin` passed; `git rev-list --left-right --count origin/main...HEAD` returned `0 0` at `b64c21d18df1ccd8cc93e507eeb937ea5fb7e7c1`. GitHub search found no open PR for this head/base pair.
- The ten T04 paths are the publication scope. The detailed commit/PR describes all-outcome storage, revision guards, conservative duplicate/re-review rules, isolated PostgreSQL tests and pending T05/T06/deployment boundaries. Existing source/policy/data/configuration and prototype runtime/state are preserved.
- Checks: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t04_docs.py` passed (seven documents, 103 local links, syntax and preserved task/history checks); `git diff --check` and the protected-source comparison recorded above passed. The preceding 20 PostgreSQL, 70 offline and 6 prototype passing tests plus data validation apply to the unchanged implementation. Application/live tests were NOT RUN again for this publication-only follow-up; only this work-log entry is added.
- Publication uses an explicit ten-file commit and `git push --set-upstream origin codex/t04-decision-storage`, then a PR targeting `main`. Commit/PR identifiers and remote state are verified and reported after execution. T04 remains DONE; T06 is recommended and not started.

### 2026-10-27 — Authorized Jira closure for T03 and T04

- Scope: the user explicitly requested marking the completed T03/T04 Jira tickets. Read current KAN-12/KAN-13 descriptions, statuses, comments and available transitions; both were To Do with no comments. Their acceptance criteria match the source and recorded T03/T04 verification above.
- Added completion comment `10004` to [KAN-12](https://luijoel24.atlassian.net/browse/KAN-12) and `10005` to [KAN-13](https://luijoel24.atlassian.net/browse/KAN-13), recording implementation, exact test commands/results, PRs and remaining integration limits. Transition `31` moved each to Done. Read-back verified both statuses, one comment each, and unchanged descriptions, summaries, assignees, parents, labels and issue links. No other issue was edited.
- GitHub verified [PR #5](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/5) merged (implementation `beb8a42aadee9282e6af0a52a490a6de139f3f30`, merge `b64c21d18df1ccd8cc93e507eeb937ea5fb7e7c1`). [PR #6](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/6) is now also merged to `main`, with head `8ad7230214f33376a66b2e9948d6d8e07431d8c2` and merge `7e7faaaf81877448c63f9778dc36d194c4a88529`. This follow-up observed the T04 merge; it did not perform it.
- Updated current README/roadmap handover and context tracking note. Repository task statuses remain unchanged. Application/live checks were NOT RUN again for this administrative follow-up; previously recorded acceptance applies to unchanged runtime source. Shared deployment and T05/T06 integration remain pending. No commits, pushes, branch deletion or service changes in this follow-up; documentation remains local.
- Documentation checks: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t04_docs.py` — PASS, seven documents, 103 local links, balanced fences/newlines, syntax and preserved task/history checks. `git diff --check` — PASS. Only README, roadmap and context changed. Recommended next task: T06 / KAN-15, not started.

### 2026-10-27 — Publish completion documentation to main

- The user authorized committing and pushing the README, roadmap and context closure updates directly to `origin/main`. Fetched origin at `7e7faaaf81877448c63f9778dc36d194c4a88529`; its tree matches the tested T04 head. Local main had no unpushed commits, and the three documentation edits were carried onto that baseline.
- Scope remains documentation only: record merged PRs and verified Jira completion. T05 is pending; the existing recommended integration order remains T06 then T05. No new implementation, Jira edit or service operation.
- Validation: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t04_docs.py` and `git diff --check`. Application/live checks are NOT RUN for this documentation-only publication. Commit and remote push results are verified after execution and reported to the user. Next recommended task: T06 / KAN-15, not started.

### 2026-10-27 — T06 / KAN-15: pure critic and retired SQLite action path

- Status: **DONE** against the T06 acceptance gate. Owner: Codex, user-assigned T06 only, with explicit Jira/commit/push authorization to `origin/main`. Baseline clean `main` at `32b38a9`; fetched origin and verified `git rev-list --left-right --count origin/main...HEAD` = `0 0`. No branch/worktree was created. T02/T03 source/contracts and prerequisite tests were inspected before implementation.
- Runtime: added `dispute-demo/app/critic.py`; replaced `agent/critic.py` with a canonical import and fail-closed legacy shim. Added `tests/test_proposal_critic.py`; replaced the six SQLite-writing prototype tests with four no-I/O compatibility tests in `agent/tests/test_critic.py`. Added `docs/critic.md`; updated README, TEAM_SETUP, agent reading map, context, roadmap and policy/contract handoffs. Source policies/data/fixtures, schemas, evaluator, retrieval, migrations, resolver/memory code, private configuration and local ledger files are preserved.
- Delivered: exact proposal/context/policy reference binding, full canonical reevaluation to detect forged/stale policy outputs, permitted outcomes, exact integer credit amount/currency, evaluated rule and corroborated evidence citations, exact missing categories/reasons/rules, stable failed-check codes and bounded-correction feedback. Mandatory review blocks credit; missing-evidence/filing precedence and ordinary autonomous outcomes remain intact. A rejected proposal is never persisted or described as a queued review.
- Semantic boundary: T01 has no structured claim representation. Accepted rationale is `policy_rationale(policy)` (ordered deterministic rule explanations, surrounding whitespace ignored); arbitrary prose, false conclusions or memory allegations route to review. Evidence support reuses T03's whole-template/metadata interpretation. This is conservative synthetic validation, not general semantic understanding or a new business policy. No schema weakening, invented history rule or second evaluator/LLM.
- Pure state boundary: no files, databases, network, subprocesses, clock, action calls or memory writes. Every typed result binds the submitted proposal/reference; malformed transport raises `ContractError` without inventing identity. Revision 1 failures cannot request another correction; T08 still must enforce run identity and budgets across calls. Null source revisions permit read-only validation, never commit freshness. T05 must reread/recheck under the guard and persist all four outcomes.
- Prototype retirement: `review_and_simulate` now always returns `unavailable` / `LEGACY_ACTION_PATH_RETIRED`, never validated/recorded. `ledger_path` is ignored without touching it; `DEFAULT_LEDGER=None`. Existing SQLite files are neither opened, migrated nor deleted. Duplicate/write assertions already exist in T04's real PostgreSQL suite; T05 owns service retry/concurrency assertions. No placeholder action service or mocked concurrency acceptance was introduced.

Exact verification from `dispute-demo/`, Python 3.13.7, unless stated otherwise:

| Command | Actual result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` | Baseline: 90 collected, 70 passed, 20 explicit PostgreSQL opt-in skips. Final: **112 collected, 92 passed, 20 explicit skips**, zero failures/errors. Includes 22 critic tests, all 40 authored cases, reference/policy/amount/citation failures, false rationale, missing requirements, malformed/future/cross-case inputs and one correction. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` | **4 passed**, zero failures/errors/skips. Legacy calls for all outcomes/malformed input, repeat calls, absent state and existing-state preservation; all calls forbid I/O. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | **PASS**, counts 42/54/40/81/16, document/manifest hashes and fixture integrity unchanged. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -` with `sys.path` snapshot, `import app.critic; import agent.critic`, canonical function identity and absent SQLite/JDBC/PG/action/H-MEM module assertions, then `unittest.TestLoader().discover('agent/tests')` | **PASS**, imports preserve path and initialize no services; 11 prototype tests collect without errors. Four compatibility tests ran above; seven external H-MEM tests were collected only, **NOT RUN**. |
| Repository root: `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python /private/tmp/validate_t06_docs.py`; `git diff --check` | **PASS**: 8 documents, 167 local links, Python syntax, only T06 status/section changed, historical log preserved; whitespace clean. |

- Purity evidence: each canonical result test repeats the call under forbidden file open/create, SQLite connection, socket, subprocess and service-import hooks; checks input immutability, exact proposal/reference binding and JSON round-trip. Exception paths are also guarded. No critic imports action storage; canonical and legacy test module names differ, avoiding discovery collisions.
- Initial test invocation from the repository root failed with `ModuleNotFoundError: app` before collecting the new suite; corrected to the documented `dispute-demo/` working directory. Final results above supersede that invocation. No application dependency was installed.
- **NOT RUN:** PostgreSQL integration (20 explicit skips; storage unchanged), live Zetaris/JDBC, Nightshift, H-MEM reference execution, HackOS, shared migration/registration or T05 action/concurrency tests. T06 needs no live services. No service startup/restart/reset or source mutation occurred. Existing dated T02–T04 integration evidence was not refreshed.
- `context.md` updated for verified T06 capability and rationale/legacy-path limits. Recommended next task: **T05 / KAN-14**, not started. Stop after T06 publication.
- Jira closure: live KAN-15 matched the assigned acceptance criteria, moved through In Progress, received completion comment `10006`, then transition `31` moved it to **Done**. Read-back verified Done, exactly one comment and unchanged summary, description, assignee, parent, labels and issue links. No other Jira issue was changed.
- Publication: user-authorized direct `main` commit with the 12 explicit T06 implementation/test/documentation paths, followed by normal `git push origin main`. Final commit/remote identity and clean-tree results are reported after execution; no force push or next task.


### 2026-10-27 — T05 / KAN-14: atomic PostgreSQL simulated decisions

- Status: **DONE** against the T05 repository acceptance gate. Owner: Codex, executing the user's roadmap goal with Jira updates and a direct completion commit to `main`. Selected the next dependency-ready task only. Initial clean `main` at `1b7a3cb`; `git fetch origin` and `git rev-list --left-right --count origin/main...HEAD` verified `0 0`. T03/T04/T06 prerequisites were inspected in source and exercised by the final full suite. No subagents or next task were started.
- Added `dispute-demo/app/action_service.py`, `tests/test_action_service.py`, `requirements-actions.txt` and `docs/actions.md`. Updated root README, TEAM_SETUP, agent reading map, context, roadmap and contract/retrieval/storage handoffs. Existing schemas, critic, policy evaluator, retrieval, migration, source policies/data/fixtures, generator, private configuration, prototype state and nested repositories remain unchanged.
- Delivered one application-only `CommitRequest` / `commit_simulated_decision` interface using the existing `CommitResult`. New idle restricted Psycopg connections use READ COMMITTED, bounded SQL/lock waits, synchronous commit and the T04 all-writer guard. Identical full-payload retry is reconciled before stale-input checks; changed payload is rejected. Unknown/stale references, mismatched run/proposal/critic, future snapshots, non-open source status and post-cutoff facts cannot commit.
- Under the same protected transaction, rereads current source records and left-joined evidence text, selects policy at dispute opening, compares typed source facts, reruns canonical policy and critic, then inserts investigation/decision and automatic effect/review/audit sidecars. All four outcomes persist; non-credit has no effect. Existing lifecycle/reservations prevent second credit and swapped duplicate-pair awards while allowing later validated non-credit/new-evidence review. No source status changes or invented policy/history rules.
- Recovery: report committed only after acknowledgement; lost acknowledgement returns unconfirmed failure without persisted IDs and an exact original-key retry recovers the original result. Cleanup errors cannot hide confirmed persistence. Database errors never become fabricated queued reviews, and exception text/DSNs are not exposed. No SQLite fallback, model write tool, memory transaction or runtime fixture lookup.
- Runtime dependency: pinned `psycopg[binary]==3.2.10`. Installed only in a new disposable `/private/tmp/dispute-t05-venv` using Python 3.12.5; existing Python 3.13.7 JDBC environment unchanged. Initial sandbox pip networking failed; approved retry of `/private/tmp/dispute-t05-venv/bin/python -m pip install --no-cache-dir -r dispute-demo/requirements-actions.txt` succeeded. Initial read-only Docker inspection was sandbox-denied; approved inspection confirmed existing services healthy. No shared services were started/restarted/reconfigured.

Exact verification from `dispute-demo/`, unless noted:

| Command | Actual result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v` | Baseline: 112 collected, 92 passed, 20 PG opt-in skips. Final: **138 collected, 93 passed, 45 PG opt-in skips**, zero failures/errors; Python 3.13.7. |
| `DISPUTE_ACTION_TESTS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python -m unittest discover -s tests -p test_action_service.py -v` | Initial action gate: **22 passed** (21 PostgreSQL plus one transport check), zero skips/failures/errors; 13.547s. Subsequent durability and duplicate/late-evidence coverage is included in the full run below. |
| `DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python -m unittest discover -s tests -v > /private/tmp/t05-full-tests.log 2>&1` | **138 passed, zero skips/failures/errors**, 37.864s: 25 real PostgreSQL action tests, all 20 real storage tests, 93 offline tests. Python 3.12.5 / Psycopg 3.2.10 / existing PostgreSQL 16 image. |
| `PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` | **4 passed**, zero skips/failures/errors. Retired SQLite writer remains inert and existing/absent state is preserved. |
| `PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python scripts/validate_synthetic_data.py` | **PASS**, unchanged 42 transactions / 54 settlements / 40 disputes / 81 evidence / 16 rules; document/manifest hashes and fixtures validate. |
| `PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python -` with `sys.path` snapshot, imports of `app.action_service`, `app.critic`, `agent.critic`, absence of psycopg/SQLite/JDBC/H-MEM imports, then `unittest.TestLoader().discover('agent/tests')` | **PASS**, no import-time connection/path mutation; 11 prototype tests collect without errors. Seven external H-MEM tests collected only, **NOT RUN**. |

- Real PostgreSQL evidence: independent backend PIDs for concurrent identical requests; one committed/one reused with the same decision. Competing distinct requests produce one commit/one stale rejection. A source writer holding the guard makes the action wait then reject its now-stale revision. During validation, an independent source writer times out on the guard. A real audit-trigger fault rolls back every record and the revision. A wrapper loses acknowledgement only after real COMMIT; retry returns the durable original with one credit. Tests cover four outcomes, forged current revisions/source facts/critic flags/amounts, future cutoffs, later refunds/evidence, unusable text, fresh duplicate requests, swapped linked charges, duplicate run IDs, restricted login/autocommit rejection, synchronous durability, new-evidence review and queue supersession. T04's real restart/permissions/constraints tests also pass.
- Isolation: only unique test containers/databases and their anonymous volumes were created/migrated/written. T05 uses an ephemeral loopback-only port; T04 remains unnetworked. `docker ps -a --filter label=dispute-purpose=t05-isolated-test --format '{{.Names}}'` and the corresponding T04 command returned no containers after cleanup. `docker ps --format '{{.Names}}\t{{.Status}}'` confirmed the original five services healthy. No source/shared reset or migration occurred.
- **NOT RUN:** live Zetaris/JDBC, Nightshift, H-MEM reference execution, HackOS, shared migration/registration/runtime grants or complete agent workflow. Current T02 revisions remain null and cannot commit. Test-only snapshots came from protected isolated PostgreSQL reads and are labelled `offline_test`; they are not live Zetaris evidence. T08 must resolve shared deployment and verified uncached fresh Zetaris reads before live end-to-end persistence. These deployment limits do not replace or weaken T05's real PostgreSQL acceptance gate.
- Shared-source read-only check: `docker exec dispute-data-dispute-postgres-1 psql -X -U dispute_loader -d dispute_demo -At -c "SELECT count(*) FROM pg_namespace WHERE nspname IN ('dispute_control','dispute_actions'); SELECT count(*) FROM transactions; SELECT count(*) FROM settlements; SELECT count(*) FROM disputes; SELECT count(*) FROM evidence; SELECT count(*) FROM evidence_documents; SELECT count(*) FROM policy_rules;"` returned **0** action/control schemas and source counts **42/54/40/81/81/16**. This is source inventory only, not live agent/retrieval acceptance.
- Final repository checks: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/validate_t05_docs.py` passed (nine documents, 178 local links, Python syntax, only T05 task status changed, historical log preserved). `git diff --check` passed. `git diff --exit-code 1b7a3cb -- dispute-demo/app/schemas.py dispute-demo/app/critic.py dispute-demo/app/policy_engine.py dispute-demo/app/tools.py dispute-demo/agent dispute-demo/data dispute-demo/policies dispute-demo/scripts dispute-demo/integration dispute-demo/db dispute-demo/tests/fixtures dispute-demo/tests/test_generation.py getting-started zetaris-platform AGENTS.md CLAUDE.md` passed, confirming protected source/state paths unchanged.
- Jira closure: KAN-14 moved through In Progress, received completion comment **10007**, then transition 31 moved it to **Done**. Read-back verified Done, one comment and unchanged summary, description, assignee, parent, labels and issue links. No other issue changed.
- Publication scope: user-authorized completion commit directly to local `main`, containing exactly the 12 implementation/test/dependency/documentation paths above. Commit identity and clean-tree verification are reported after execution. No remote push was requested or performed.
- Context updated for the verified writer and its deployment limit. Recommended next task: **T07 / KAN-16**, not started. Stop after the authorized T05 commit.

### 2026-10-27 — T07 / KAN-16: bounded Nightshift investigator

- Status: **DONE** against the T07 repository gate. Owner: Codex. The user expanded the goal to the entire roadmap, sequentially, with Jira updates and a commit/push to `origin/main` per completed task. This explicitly supersedes stop-after-one-task instructions for the current goal; acceptance gates remain unchanged. Baseline: clean `main` at `29eb6ae7460ea704ebd846a11f3171cd04e2e8c6`. First fetched and normally pushed that already-completed T05 commit; local/origin IDs match. KAN-14 publication comment `10008` supersedes its prior local-only note. KAN-16 was read and moved to In Progress; dependencies were inspected in source and exercised by regression tests.
- Added `app/investigator.py`, `app/nightshift.py`, `tests/test_investigator.py`, `tests/test_nightshift.py`, `integration/check_investigator.py`, `docs/investigator.md` and `docs/evidence/t07-live-DP-0014.json` under `dispute-demo/`. Labelled the existing resolver/helper as a deterministic legacy prototype. Updated README, TEAM_SETUP, agent reading map, context and roadmap. Canonical schemas, policy, critic, tools, action service, migration, source/data/fixtures, private settings, memory and nested repositories are unchanged.
- Delivered: one real text-completion turn returning a strict typed proposal or unexecuted case-bound read request; exact run/proposal/reference/revision binding; canonical-policy and typed observation checks; one correction with a new proposal ID and freshly corroborated critic feedback. Four outcomes and exact missing categories are supported. Model errors fail without a deterministic substitute. No tool dispatch, database/action/memory write, native tool/schema assumption or expected-answer prompt.
- Transport: reused private configuration and auth conventions after checking the published [Meterless provider contract](https://meterless.ai/engines.html). Text messages with app/scope headers, no streaming, max 4,096 output tokens. Requests/responses capped at 256 KiB; redirects/proxies disabled. A short-lived child receives secrets through stdin and is killed/waited at the configurable maximum 180-second total request deadline. Error text is sanitized; no automatic retries. Metadata reports requested route and returned model only; no identity inferred from advertised models or assistant prose.
- Trust/correction boundary: case text and observations remain untrusted; typed history is customer/cutoff scoped and advisory. Unknown JSON fields, duplicate keys, invalid money/IDs, cross-case/SQL/write requests, native tools, refusals, truncation and malformed output are rejected. T06's deterministic rationale vocabulary remains binding; no new policy or generalized semantic approval. Response reasoning is discarded. Model uncertainty is explicitly bounded and must prevent T08 from committing the proposal. T08 still owns total call/tool/duration budgets, dispatch, reevaluation and persistence; this step has no persistent run history.

Exact verification from `dispute-demo/`, existing Python 3.13.7, unless noted:

| Command | Actual result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_investigator.py -v` | **16 passed**, zero failures/errors/skips; 3.821s. Model stubs, real typed source/policy/critic, all four outcomes, correction, malicious inputs and I/O forbidden during model turns. |
| `DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_nightshift.py -v` | Initial 12-test run: 11 passed, one test-harness error from case-sensitive HTTP header lookup. Changed fixture assertions to case-insensitive names; final full run below passes all 12, including five real loopback HTTP fixtures. These are not Nightshift/model calls. |
| `DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v > /private/tmp/t07-tests.log 2>&1` | **166 collected, 121 passed, 45 explicit PostgreSQL opt-in skips**, zero failures/errors, 18.115s. Includes the final investigator/transport implementation and all unchanged offline regressions. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v` | **4 passed**, zero failures/errors/skips; retired writer remains inert. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python scripts/validate_synthetic_data.py` | **PASS**, source counts 42/54/40/81/16, keys/timestamps/documents/manifest hashes/fixture references unchanged. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -` with imports of `app.investigator`, `app.nightshift`, `integration.check_investigator`, a `sys.path` snapshot, absent JDBC/PG/SQLite/action/memory assertions, then `unittest.TestLoader().discover('agent/tests')` | **PASS**, no path mutation or service initialization; 11 prototype tests collect without errors. Seven external H-MEM checks collected only, **NOT RUN**. |
| Repository root: `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python dispute-demo/integration/check_nightshift.py` | Initial approved-network attempt failed unreachable. After `open -a '/Applications/Nightshift M1-M4.app'`, authenticated discovery **PASS**, 19 advertised IDs. Opened the existing installation only; no install/config/token/provider changes. |
| From `getting-started/`: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/preflight.py --jdbc` | **JDBC PASS**: port/JAR/Java/Python, SELECT 1, datasource dispute, Lightning databases NY_TAXI/TPCDS_DB. Overall exit 1 is two REST-only missing-key failures; the connection guide permits JDBC to proceed. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m integration.check_investigator DP-0014 > /private/tmp/t07-live-DP-0014.json` | **Live PASS, exit 0**: actual Zetaris source channel, Nightshift structured proposal for 6,000 SGD minor units, EV-0027/EV-0028 and all evaluated v2 rules, empty uncertainties, pure critic accepted. Requested route `meterless/auto`; response reported `nvidia/nemotron-3.5-bolt-e4b`. No hidden reasoning or fixture labels in evidence. Snapshot revision null; `persisted: false`. Exact public result copied to the tracked evidence file. |

- Local HTTP evidence: the actual child sends the required bearer/app/scope headers; 401 is distinct, redirect is not followed, duplicate/oversized JSON fails, and a delayed response causes parent deadline termination before headers. Stubbed provider errors do not leak exception/stdout/stderr secrets. No automatic retries or fallback action.
- **NOT RUN:** real PostgreSQL integration (45 explicit skips; storage/action code unchanged), H-MEM reference, HackOS, shared migration/runtime grants/registration, full controller and live correction loop. Prior T05 138-pass/45-real-PG evidence remains dated. No source/shared reset or mutation. No claim of persistence or actual tool dispatch from the read-only probe. Live non-credit/correction cases are stub-tested in T07; T08/T12 retain full integrated gates.
- Repository checks: `git diff --check` and protected-source comparison against `29eb6ae` passed. `PYTHONDONTWRITEBYTECODE=1 getting-started/.venv/bin/python /private/tmp/validate_t07_docs.py` checks local links, syntax, task status scope, retained history and sanitized live evidence. No packages installed; the existing Nightshift app is left open for subsequent live work.
- Jira: KAN-16 received completion comment **10009** and transition 31 confirmed **Done**. Its summary, description, assignee, parent, labels and links were checked unchanged before closure. Publication uses an explicit 13-path commit and normal push to `origin/main`; the final commit and remote match are verified after execution.
- Context updated for verified T07 capabilities, returned model metadata, explicit persistence/budget limits and the authorized sequential full-roadmap scope. Next task: **T08 / KAN-17**, after this task's Jira closure and commit/push.

### 2026-10-27 — T08 / KAN-17: prerequisite inspection and deployment preparation

- Status: **IN_PROGRESS**, continuing the authorized full-roadmap goal. T07 commit `87267ed9ba6e8078a15db7700d4d5b945d260251` is pushed to `origin/main`; KAN-16 is Done with acceptance comment `10009` and publication receipt `10010`. Initial working tree clean. KAN-17 description/dependencies read and transition 21 confirmed In Progress.
- Inspected current T01–T07 interfaces, root/scoped instructions, source policies/schema/generator, JDBC helper, storage migration/action service/tests, Compose and SQL/cache guides. T07's current-session preflight passes JDBC; no new credentials or endpoint change.
- Read-only Docker/PG inventory confirms the original five persistent services healthy, source database internal port 5432 only, no `dispute_control`/`dispute_actions` schemas, source counts 42/54/40/81/81/16. No deployment or source write yet.
- Previewed and executed read-only registration/cache/query-plan checks through the approved JDBC path: existing seven source tables registered; per-table cache policies unset; `OFFSITE CACHE TABLE DETAILS dispute.disputes` empty. `EXPLAIN SELECT dispute_id FROM dispute.disputes WHERE dispute_id = 'DP-0014'` shows `Scan InsertableJDBCTableRelation` with pushed case filter and masked source connection metadata. No in-memory scan. This is scoped observation, not yet a verified coherent read protocol or write readiness.
- T08 must provide bounded fresh reads, deployment/restricted action access, controller/CLI and real end-to-end acceptance before DONE. No task acceptance or persistence is claimed from the inspection.

### 2026-10-27 — T08 / KAN-17: accepted bounded live workflow

- **DONE gate satisfied.** Normal runtime is `python -m app.main`, with `app.orchestrator.Controller`, coherent fresh read projections, process-bounded read/write adapters and a private pre-dispatch recovery journal. Four outcomes use the same pure policy/critic and sole PostgreSQL writer. No application H-MEM import/recall/save, deterministic model fallback, SQLite writer or arbitrary SQL/model write tool.
- Default budgets: four model requests, three reads including initial retrieval, 300 seconds total; 120/45/25 seconds per model/read/commit. Every attempt consumes its budget. One correction only; new facts invalidate prior observations and force reevaluation. New reads during correction stop safely without resetting the allowance. Uncertainty or unresolved/malformed proposals cannot write. A failed proposal is not relabelled as a queued review.
- Migration 002's `dispute_read_bundle` view computes case facts, source revision, current source-side clock, customer history and stored decision receipts in one PostgreSQL statement snapshot. The approved Zetaris channel checks every SELECT's direct `InsertableJDBCTableRelation` plan, before/bundle/after revision agreement, source clock and bounded collections/2 MiB envelope. Unknown/cached plans or incoherence fail closed. Historical T02 reads preserve their null-revision behavior. Internal PostgreSQL rereads remain exclusive to commit validation.
- Shared deployment: a private `pg_dump` backup precedes migrations 001/002. Both apply without source-row changes. A new restricted `dispute_app` LOGIN receives only `dispute_action_writer`; its random credential/DSN stays in mode-0600 `.env.local`. The project container alone was recreated with its existing volume to publish loopback port 55432. Existing Zetaris services/metastore were preserved. Four read-only views were previewed and registered through the approved JDBC workflow. [Sanitized receipt](./dispute-demo/docs/evidence/t08-deployment.json). All six source fingerprints still match; counts 42/54/40/81/81/16.
- Nightshift integration finding: four initial `meterless/auto` runs failed strict output parsing, and one advertised Lightning route was unavailable. All stopped before writes. Installed Nightshift 0.92.7 source inspection (`proxy.js`, `orchestrator.js`, `providers.js`, `structured-output.js`; hashes in evidence) showed JSON-object forwarding/validation, semantic-cache bypass and tier-split controls. Final requests use `response_format=json_object`, `tool_choice=none`, temperature 0 and `meterless-tier-split: off`; this structured path skips runtime answer-memory/scaffold injection. No app/provider credential or saved model-setting change. Local validation still rejects malformed JSON, unsupported schema/binding, reported native-tool execution or runtime review. No provider-enforced schema claim.

Exact checks (commands run from `dispute-demo/` unless specified):

| Command / operation | Result |
|---|---|
| `../getting-started/.venv/bin/python -m venv .venv`; `.venv/bin/python -m pip install -r requirements-runtime.txt` | Dedicated Python 3.13.7 environment created; Psycopg/binary 3.2.10, JayDeBeApi 1.2.3, JPype1 1.7.1 installed. Initial sandbox network lookup failed; approved network retry passed. Bundled environment unchanged; `.venv/` ignored. |
| `PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_orchestrator.py -v` | Initial 16 pass/1 test-fixture error used nonexistent `settlement_type`; corrected to actual `movement_type`. Final 17/17 pass. Seven new coherent-read adversarial tests pass. |
| `DISPUTE_ACTION_TESTS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/dispute-t05-venv/bin/python -m unittest discover -s tests -p test_end_to_end.py -v` | Seven real isolated PostgreSQL + explicitly scripted-model workflow tests pass: four outcomes, exact reuse/ordinary rerun, corrected/terminal faults, changed revision, lost acknowledgement and additive view/role scope. No live-model claim from these tests. |
| `DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v > /private/tmp/t08-acceptance-tests.log 2>&1` | **198/198 PASS, zero skips**, 46.285 seconds: 52 real isolated PostgreSQL checks, five real loopback HTTP fixtures, 141 other tests. Earlier full runs passed 177 with 20 storage skips, then 197 with all flags; final count includes the new runtime-review/native-tool refusal test. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s agent/tests -p test_critic.py -v`; `.venv/bin/python scripts/validate_synthetic_data.py` | Four compatibility tests PASS; generated data/keys/timestamps/policy coverage/documents/hashes/fixture references PASS. Source files, policies and fixtures unchanged. One targeted investigator invocation from repository root failed import `app`; rerun through the final correctly scoped suite passes. |
| `.venv/bin/python /private/tmp/t08-deploy.py`; `bash integration/db.sh up -d --no-deps dispute-postgres` | Private backup and additive migrations/restricted login PASS; loopback publication retained the project volume. No loader/reset or source edits. |
| From `getting-started/`: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/run_sql.py --dry-run ../dispute-demo/integration/action_registration.sql`, then same command with `--channel jdbc` instead of `--dry-run` | Four-statement preview PASS; four registrations PASS. Current-session JDBC preflight passed; two REST-only missing-key checks remain unrelated to this JDBC path. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.main DP-0014 --no-memory > outputs/t08-live-DP-0014-structured.json` | **Live PASS, exit 0**: fresh Zetaris reference revision 0; actual Nightshift proposal, accepted pure critic, confirmed 6,000 SGD minor-unit credit. Run `7238450e-5c65-4829-a1a6-fcd3657fddf0`; decision `b2d7a3ef-b7a7-4546-ac93-183a672ef41d`; credit `4ca53387-7b50-422c-9c40-d507685394a3`. Requested `meterless/auto`, response label `nvidia/nemotron-3.5-bolt-e4b` (metadata, not independent provider attestation). |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.main --retry-request outputs/runs/7238450e-5c65-4829-a1a6-fcd3657fddf0.request.json` | **Live PASS, exit 0**: `reused`, identical original decision/credit, zero model/read calls. No new effect. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.main DP-0014 --no-memory > outputs/t08-live-DP-0014-rerun.json` | **Expected safe refusal, exit 1**: fresh revision 5, real proposal/accepted critique; writer returns `effective_credit_already_exists`. No duplicate. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.check_workflow_fault DP-0014 --inject-credit-overstatement` | **Live labelled fault safely contained, exit 1**: +1 minor unit injected after actual initial model proposal; critic REVISE; exactly one real correction attempt fails proposal schema. Two model calls, one read, revision 1; no action or invented queued review. Successful correction is separately proven by real-PG/scripted-model tests. |
| `.venv/bin/python /private/tmp/t08-final-db-check.py` | PASS: source fingerprints unchanged; exactly 1 decision, 1 credit, 1 audit, 0 reviews, revision 5; action login has no superuser/create/replication/bypass/owner/source-writer rights. |
| `.venv/bin/python /private/tmp/validate_t08_docs.py`; `git diff --check`; canonical import check | PASS: changed Markdown local links and Python ASTs valid; protected source/policy/fixture/platform paths unchanged. Importing canonical CLI/controller/fresh adapters preserves `sys.path` and initializes no JDBC/Psycopg/SQLite/legacy resolver/H-MEM. |

- [Public live traces](./dispute-demo/docs/evidence/t08-live-workflow.json) contain only source facts, rules, typed proposals/critique and explicit execution statuses. No secrets, raw model reasoning, authored expected labels or private backup contents are tracked. Original full recovery requests and traces remain in ignored `outputs/`.
- Confirmed commit acknowledgement survives optional post-commit callback/trace-save failures; no second action occurs. Uncertain commits retain their exact saved request/key for recovery. The no-memory milestone is explicit and does not claim actual H-MEM persistence.
- **NOT RUN:** actual external H-MEM conformance/save-restart-recall; authenticated HackOS requirements; live all-four-outcome commits (covered in isolated PostgreSQL), shared database restart after action (isolated restart test passes). No real payment integration.
- Jira KAN-17 received completion comment **10011**; transition 31 and a fresh read confirm status/resolution **Done**. Summary, description, assignee, parent, labels and links were checked unchanged before closure. Direct-main commit/push and remote equality are verified after publication. Next under the authorized goal: **T09 / KAN-18**, after publishing this completed task.

## 11. Deferred scope

An independent manager/planner LLM, a second semantic-review LLM, a fraud-risk model, longer agent loops, advanced UI and production integrations are not prerequisites for this proposed build. A confirmed competition requirement or explicit scope decision can add a separately scoped task. Do not add them silently during a task above.

## 12. Document maintenance

- Update `context.md` for agreed scope/architecture changes or verified factual corrections, preserving the distinction between historical audit claims and current execution evidence.
- Update this roadmap's task board, detailed status, and completion record together when acceptance evidence or dependencies change. Use stable T00–T13/A01 IDs; retain earlier records as history.
- Update `agent.md` when shared operating rules change, and keep the root `AGENTS.md` and `CLAUDE.md` entry points aligned with the same pre-execution reading order.
- Verify repository links after documentation edits. Proposed implementation paths are not claims that those files exist; imported Jira links are not proof of live access or issue completion.
