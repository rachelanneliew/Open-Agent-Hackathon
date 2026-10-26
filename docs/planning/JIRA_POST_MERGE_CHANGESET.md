# Jira post-merge change preview

New planning file created 27 October 2026 (Asia/Singapore). **APPROVED AND APPLIED — 13 description updates verified on 27 October 2026.** The original preview and pre-edit snapshots below are retained as the exact change record.

Prepared for the user's section 7 local documentation/alignment assignment. [context.md](../../context.md) remains the project brief and [ROADMAP.md](../../ROADMAP.md) the active task queue. The external `CODEX_POST_MERGE_ALIGNMENT_2026-10-27.md` supplied scope; its later implementation instructions were not executed.

## Evidence and exact mutation scope

- Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merged 26 October 2026; local clean `main` HEAD equals reviewed merge `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`. GitHub connector confirms merged status and merge SHA; local source and all ten changed paths inspected.
- Jira: authenticated read on 27 October 2026 using `searchJiraIssuesUsingJql`, JQL `project = KAN AND labels = open-agent-hackathon ORDER BY key ASC`, fields `summary, description, status, assignee, parent, issuelinks, updated`, HTML response, maximum 100. Returned 20 issues, `isLast=true`.
- Proposed field changes: **description only on KAN-11–KAN-23**. All summaries stay exactly as shown below. No status, assignee, resolution, epic membership, task ID, dependency link, label, comment, attachment or new-issue changes. KAN-4–KAN-10 are untouched.
- Proposed descriptions equal the captured current HTML plus the corresponding exact Markdown-worded addendum below, converted to equivalent rich-text blocks. For KAN-14 only, also apply the single exact phrase replacement specified below to remove ambiguous retry wording. Nothing else in the original body is replaced.
- This approval would not authorize runtime implementation, new policy/data, publication or task completion. Application tests and Zetaris/PostgreSQL/Nightshift/H-MEM checks are NOT RUN for this documentation pass.

## Pre-edit issue inventory

| Issue | Current summary (proposed: unchanged) | Status | Parent | Updated at (+08:00) |
|---|---|---|---|---|
| [KAN-4](https://luijoel24.atlassian.net/browse/KAN-4) | [Open Agent Hackathon] Setup, contracts and data access | To Do | — | 2026-10-26T16:59:36.504+0800 |
| [KAN-5](https://luijoel24.atlassian.net/browse/KAN-5) | [Open Agent Hackathon] Policy enforcement and safe actions | To Do | — | 2026-10-26T16:59:39.035+0800 |
| [KAN-6](https://luijoel24.atlassian.net/browse/KAN-6) | [Open Agent Hackathon] Investigator, critic and workflow | To Do | — | 2026-10-26T16:59:41.992+0800 |
| [KAN-7](https://luijoel24.atlassian.net/browse/KAN-7) | [Open Agent Hackathon] H-MEM and analyst experience | To Do | — | 2026-10-26T16:59:44.733+0800 |
| [KAN-8](https://luijoel24.atlassian.net/browse/KAN-8) | [Open Agent Hackathon] Reliability, demo and submission | To Do | — | 2026-10-26T16:59:47.365+0800 |
| [KAN-9](https://luijoel24.atlassian.net/browse/KAN-9) | [T00] Verify current repository baseline | Done | KAN-4 | 2026-10-26T18:28:29.328+0800 |
| [KAN-10](https://luijoel24.atlassian.net/browse/KAN-10) | [T01] Define shared contracts and exact policy semantics | Done | KAN-4 | 2026-10-26T19:06:42.984+0800 |
| [KAN-11](https://luijoel24.atlassian.net/browse/KAN-11) | [T02] Expose narrow case and history retrieval tools | To Do | KAN-4 | 2026-10-26T17:00:48.848+0800 |
| [KAN-12](https://luijoel24.atlassian.net/browse/KAN-12) | [T03] Implement deterministic policy evaluation | To Do | KAN-5 | 2026-10-26T17:00:52.444+0800 |
| [KAN-13](https://luijoel24.atlassian.net/browse/KAN-13) | [T04] Create sandbox decision, action and audit storage | To Do | KAN-5 | 2026-10-26T17:00:55.258+0800 |
| [KAN-14](https://luijoel24.atlassian.net/browse/KAN-14) | [T05] Implement atomic simulated decision recording | To Do | KAN-5 | 2026-10-26T17:00:57.955+0800 |
| [KAN-15](https://luijoel24.atlassian.net/browse/KAN-15) | [T06] Build mandatory critic and validator | To Do | KAN-6 | 2026-10-26T17:01:00.487+0800 |
| [KAN-16](https://luijoel24.atlassian.net/browse/KAN-16) | [T07] Implement investigator through Nightshift | To Do | KAN-6 | 2026-10-26T17:01:03.550+0800 |
| [KAN-17](https://luijoel24.atlassian.net/browse/KAN-17) | [T08] Wire bounded workflow and command-line runner | To Do | KAN-6 | 2026-10-26T17:01:06.084+0800 |
| [KAN-18](https://luijoel24.atlassian.net/browse/KAN-18) | [T09] Verify and wrap actual H-MEM integration | To Do | KAN-7 | 2026-10-26T17:01:08.418+0800 |
| [KAN-19](https://luijoel24.atlassian.net/browse/KAN-19) | [T10] Integrate verified memory and repeat-history review | To Do | KAN-7 | 2026-10-26T17:01:11.008+0800 |
| [KAN-20](https://luijoel24.atlassian.net/browse/KAN-20) | [T11] Build thin analyst view and review queue | To Do | KAN-7 | 2026-10-26T17:01:13.248+0800 |
| [KAN-21](https://luijoel24.atlassian.net/browse/KAN-21) | [T12] Run cross-component failure tests and repeatable reset | To Do | KAN-8 | 2026-10-26T17:01:16.148+0800 |
| [KAN-22](https://luijoel24.atlassian.net/browse/KAN-22) | [T13] Package evidence-backed demo and submission | To Do | KAN-8 | 2026-10-26T17:01:18.912+0800 |
| [KAN-23](https://luijoel24.atlassian.net/browse/KAN-23) | [A01] Confirm authenticated HackOS challenge and submission requirements | To Do | KAN-4 | 2026-10-26T17:01:21.700+0800 |

All 20 issues are unassigned and have empty issue-link arrays. Existing dependencies remain in descriptions/ROADMAP; no link creation is proposed. T00/T01 remain Done; other statuses remain To Do.

## Exact per-issue description changes

### KAN-11 — [T02] Expose narrow case and history retrieval tools

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-4**; updated `2026-10-26T17:00:48.848+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T02
Epic: KAN-4
Dependencies: T01</p><p>IMPLEMENTATION
Wrap existing read-only Zetaris/JDBC retrieval in typed allowlisted backend tools for dispute, settlement, evidence, policy and verified history. Preserve evaluation-time visibility and policy version. Deny arbitrary model SQL; no secrets in prompts. Handle missing/invalid case and backend failures distinctly.</p><p>DEFINITION OF DONE
Retrieval tests pass with verified source IDs, cutoff behavior, no leaked credentials and documented live connectivity result.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4 preserves the existing Zetaris/JDBC path and adds transaction customer_id in dispute-demo/integration/get_dispute_context.py. Typed integration acceptance remains outstanding.
- Adapt raw rows to canonical DisputeContext with IDs, statuses, timestamps, policy applicability and explicit input issues. Preserve evidence metadata when text is absent; content=None must not become usable support. Preserve strict T01 contracts.
- Return authoritative customer-scoped, time-visible history in a separate typed result with source references; do not place historical records in current-case transaction/evidence collections. Memory tags alone are not verification.
- Keep source_revision=None until coherent revision/freshness support is available; report decision reads as unsupported until T04 storage and read registration exist. T02 does not depend on every T04 feature.
- Acceptance additions: test raw-to-typed mapping, current-case/customer ownership, cutoff filtering, missing/unreadable text, malformed data and distinct not-found/incomplete/backend-unavailable results. Keep validated read allowlists, no model SQL/credentials/writes/fixture access, and label live Zetaris evidence separately.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-12 — [T03] Implement deterministic policy evaluation

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-5**; updated `2026-10-26T17:00:52.444+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T03
Epic: KAN-5
Dependencies: T01, T02</p><p>IMPLEMENTATION
Read synthetic policy versions and implement pure Python eligibility, filing-window, evidence, completed-refund, amount, anomaly, precedence and review checks as written. Never call Nightshift. Return supported/missing evidence, rule IDs, allowed outcomes and hard blocks. Do not use test expected_results.json in runtime.</p><p>DEFINITION OF DONE
Fixture and boundary tests cover both policy versions and partial refunds; same inputs produce same result without model calls.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: dispute-demo/agent/policy_engine.py exists from PR #4 as a dictionary-based evaluator. Reuse and harden it into one canonical evaluator; prototype presence is not acceptance.
- Consume typed DisputeContext and return PolicyResult bound to the same reference, with allowed/blocked disposition for all four outcomes, rule checks, missing categories and optional credit limit. Apply the explicit legacy recommendation mapping; existing settlement refunds/reversals remain source movements.
- Preserve opening-date policy selection, ascending first-terminal precedence, exact 30/45-day filing windows and the above-20,000-SGD-cent review rule (exactly 20,000 stays eligible if preceding checks pass). Calculate primary-transaction balances in integer minor units; pending/failed movements are not completed money and corrupt/negative balances cannot silently become valid zero balances.
- Missing/unreadable text must not pass solely on evidence type. Treat delivery-template parsing as a bounded synthetic interpretation; unsupported content does not establish favorable facts. Normalize malformed evidence timestamps and missing transaction fields at the input boundary.
- Acceptance additions: applicable authored scenarios plus boundary/adversarial tests for missing content, malformed records, incomplete/duplicate predicates, unexpected actions, mixed versions and unsupported currency/policy scope. Fixtures remain test-only; no new binding repeat-claim threshold or policy change is authorized.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-13 — [T04] Create sandbox decision, action and audit storage

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-5**; updated `2026-10-26T17:00:55.258+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T04
Epic: KAN-5
Dependencies: T01</p><p>IMPLEMENTATION
Add tracked PostgreSQL schema/migrations for decisions, effective simulated provisional_credit, idempotency key, status transitions and audit events. Include DB-level uniqueness (including concurrent retries). Keep existing settlements separate from new actions.</p><p>DEFINITION OF DONE
Migration and constraint tests pass; duplicate effective simulated credits cannot be stored; action can be traced to decision.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4's SQLite ledger in dispute-demo/agent/critic.py is a prototype, not canonical PostgreSQL storage or proof of source freshness.
- Persist all four outcomes through PostgreSQL decision, optional credit-effect, audit, idempotency and minimal review-queue storage. Non-credit outcomes have no amount/effect; source settlement movements stay separate.
- Implement the documented T01 global source-revision guard and enforce all relevant writers' participation, including settlement/evidence/policy/decision changes and loaders/resets. Coordinate coherent T02 reads; null revision is valid as an unsupported retrieval state but cannot support a successful commit.
- Document and test minimum lifecycle for new evidence after non-credit decisions, cross-dispute duplicate scope and historical replay versus fresh execution. Do not inherit SQLite transaction uniqueness as business policy or ignore later authoritative refunds merely because evaluation_at is frozen.
- Acceptance additions: isolated PostgreSQL migration/constraint tests, four-outcome round trips, non-credit effect exclusion, persisted review across restart, source-writer synchronization and documented lifecycle/duplicate semantics. Never reset shared/source data.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-14 — [T05] Implement atomic simulated decision recording

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-5**; updated `2026-10-26T17:00:57.955+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T05
Epic: KAN-5
Dependencies: T03, T04</p><p>IMPLEMENTATION
Implement one narrow transactionally safe action service. Reload and lock/reconcile authoritative dispute/settlement state; reevaluate policies/amount and status transitions; reject stale proposals. Commit decision, optional simulated effect and audit record together; no success response before commit.</p><p>DEFINITION OF DONE
Tests show single eligible commit, retry reuse/block, rollback, stale-state rejection, and at most one effective credit for concurrent requests.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

One exact replacement in the existing DEFINITION OF DONE paragraph:

```text
Before: retry reuse/block
After: identical-payload retry reuse; changed-payload rejection
```

Preserve the rest of that paragraph and the remaining original HTML. This clarifies existing retry behavior; the appended acceptance requirements below are also part of the proposal.

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: the PR #4 SQLite-writing critic does not satisfy the PostgreSQL action-service gate. The canonical action service must be the sole normal-runtime writer for decisions/effects, with no SQLite fallback.
- Within one protected transaction, validate proposal/critic/reference binding, re-read current authoritative state, re-evaluate applicable policy/lifecycle and reject stale or unknown revisions. A lock on only the dispute row cannot substitute for the T04 all-writer guard.
- Same idempotency key and identical payload returns the original committed result as reused. Same key with changed payload is rejected; another key cannot create a second effective credit. Commit decision, optional effect, audit and idempotency mapping atomically.
- Persist request_evidence, decline and human_review without credit effects. Mandatory policy review prevents automatic credit. Database failure is not a committed action or queued review; recover a lost acknowledgement with the original idempotency key.
- Acceptance additions: all-outcome persistence, required-review no-credit checks, changed-payload rejection, stale/current-source changes, rollback and independent-connection concurrency in real PostgreSQL. SQLite or mocked-only tests cannot satisfy this acceptance.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-15 — [T06] Build mandatory critic and validator

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-6**; updated `2026-10-26T17:01:00.487+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T06
Epic: KAN-6
Dependencies: T02, T03</p><p>IMPLEMENTATION
Create deterministic proposal validation checking typed schema, referenced evidence/rules, time visibility, amount, permitted outcome and policy hard blocks. Return actionable rejection reasons for one bounded correction attempt. No independent action rights; optional second LLM is out of scope.</p><p>DEFINITION OF DONE
Crafted fabricated-evidence, excessive-credit, disallowed-outcome and malformed-proposal cases are blocked; valid reference passes.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: dispute-demo/agent/critic.py combines validation with SQLite credit recording. Reuse validation while removing execution from the canonical critic.
- Accept DisputeContext, PolicyResult and AgentProposal; return a correctly bound CriticResult. Validate identity, snapshot/revision, policy version, outcome, amount/currency and required source/rule support. A real evidence ID alone does not prove a claim.
- Require appropriate citations without inventing evidence IDs for missing-evidence requests. Enforce mandatory policy review; advisory memory is not binding policy. Return actionable bounded-correction feedback.
- Acceptance additions: test every critic branch for no ledger creation, database writes or action-service calls. Test typed policy/proposal/reference mismatches, missing required citations, unsupported evidence and required-review rejection of credit. Replace critic-write expectations and move duplicate/write tests into the action-service suite.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-16 — [T07] Implement investigator through Nightshift

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-6**; updated `2026-10-26T17:01:03.550+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T07
Epic: KAN-6
Dependencies: T02, T03, T06</p><p>IMPLEMENTATION
Implement Nightshift-based investigator with small evidence checklist, approved retrieval tools and structured JSON AgentProposal. Treat retrieved documents as untrusted case material; enforce response parsing, tool limits and timeout. Record exact model/provider only when observable.</p><p>DEFINITION OF DONE
Live or truthfully labeled mocked tests show source-grounded proposal, missing-evidence request, malformed-output/timeout handling and no direct action write.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: resolver._policy_proposal() in dispute-demo/agent/resolver.py is deterministic proposal construction, not a Nightshift model call. It may remain only as a clearly labelled test/fallback helper.
- Build the genuine Nightshift investigator with approved read tools and typed proposals for all four outcomes, source-grounded explanations and at most one correction. Keep evidence/memory untrusted and parsing, tool/model limits and timeout handling explicit.
- Acceptance additions: record an actual structured model proposal in a separately labelled live test when available; mark unavailable live inference NOT RUN and keep mocks distinct. A connectivity probe or routing ID does not establish investigator acceptance or responding model identity. No direct writer or hard-policy override.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-17 — [T08] Wire bounded workflow and command-line runner

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-6**; updated `2026-10-26T17:01:06.084+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T08
Epic: KAN-6
Dependencies: T02, T03, T05, T06, T07</p><p>IMPLEMENTATION
Build Python orchestrator and CLI: select dispute -&gt; approved retrieval -&gt; deterministic policy -&gt; investigator -&gt; critic -&gt; at most one correction -&gt; safe transaction -&gt; public audit trace. Reevaluate after newly retrieved evidence; fail closed without unsafe write.</p><p>DEFINITION OF DONE
End-to-end real sandbox flow works from a dispute ID with no manual database edits; retry cannot double credit; invalid proposal correction or safe review shown.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: dispute-demo/agent/resolver.py calls memory, a deterministic proposal helper and review_and_simulate. It is not the canonical bounded controller.
- Integrate one controller for approved retrieval -> policy -> Nightshift investigator -> pure critic -> PostgreSQL action service -> display. Carry canonical run/proposal/reference identities and invalidate prior results after newly verified facts.
- Handle all four outcomes; policy-permitted credit, evidence request and decline need no compulsory human approval. A critic review verdict cannot commit its rejected credit proposal: validate a safe allowed review proposal or return an honest no-credit failure. Show queued review only after confirmed persistence.
- Support an explicitly labelled no-memory milestone until T10, with no hidden SQLite fallback. The prototype remember=False disables saving, not recall. Enforce one correction and explicit tool/model/duration budgets.
- Acceptance additions: all-outcome persistence status, bounded correction/failure, prior-result reuse and absence of the SQLite bypass. Return the confirmed commit independently of optional post-commit work; memory failures must not obscure or repeat the action.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-18 — [T09] Verify and wrap actual H-MEM integration

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-7**; updated `2026-10-26T17:01:08.418+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T09
Epic: KAN-7
Dependencies: T00, T01 (parallel eligible)</p><p>IMPLEMENTATION
Locate actual permitted H-MEM implementation/spec; run reference checks. Create adapter to save and recall source-linked case summaries and analyst corrections. Preserve source IDs, timestamps and restart persistence. Do not relabel a dictionary H-MEM.</p><p>DEFINITION OF DONE
Real H-MEM API write/read survives restart, provenance returned, failure independently reported; missing access remains BLOCKED not fabricated.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4 supplies dispute-demo/agent/hmem_client.py, hmem_bridge/server.ts and reference-dependent tests. Reuse them; do not treat the adapter as absent or accepted.
- Verify and pin the actual reference source/revision, runner and dependencies. Configure/document paths and sanitized examples; the current bridge manifest installs no dependencies and its sibling hmem-reference assumption is not portable setup.
- Add bounded subprocess calls, JSON/output validation and clear sanitized missing-dependency/errors. Do not expose private paths/credentials or full untrusted stderr to analysts.
- Retain decision/dispute/customer IDs, source reference, policy version and timestamps; distinguish committed summaries from unverified notes. Use decision-ID retries without re-executing actions.
- Acceptance additions: real save -> new process/restart -> recall, customer isolation and a documented/tested serialized or otherwise safe persistence strategy against concurrent lost updates. Separate offline mocks from reference-dependent integration tests; subprocess-per-operation alone does not prove concurrency safety.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-19 — [T10] Integrate verified memory and repeat-history review

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-7**; updated `2026-10-26T17:01:11.008+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T10
Epic: KAN-7
Dependencies: T02, T03, T08, T09</p><p>IMPLEMENTATION
Recall H-MEM before investigation; verify all remembered source records via Zetaris; re-evaluate rules if facts change. Detect repeated relevant claims only under documented policy to route to review, without alleging fraud. Save summary after successful commit; do not retry action on memory failure.</p><p>DEFINITION OF DONE
Later case uses verified historical context and provenance, incorrect memory has no binding effect; post-commit memory failure leaves committed action unchanged.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4's memory_service.py scopes tags and counts distinct remembered disputes; stored verified tags are not authoritative revalidation and the default count of three is not a source-policy rule.
- Resolve recalled IDs, customer ownership, evaluation-time visibility and relevant committed outcomes through T02 tools. Ignore/reject false, stale, cross-customer and future references with an explicit trace. Raw memory cannot require review, establish fraud or create credit eligibility.
- Working scope: verified repeat history remains advisory. Existing written policy-required review stays mandatory and excludes credit. Before closing T10, obtain explicit approval of advisory MVP acceptance scope or an exact versioned binding rule (distinct-case count, lookback, time anchor, reasons, qualifying outcomes, exclusions and precedence). The original history-rule acceptance requirement is not completed by this documentation alignment.
- Save final summaries only from confirmed committed/reused decisions, idempotently by decision ID; critic acceptance alone is insufficient. Repeated runs must not inflate history counts.
- Acceptance additions: incorrect memory has no binding effect; post-commit memory failure preserves the confirmed result and reports memory failure/pending retry separately; memory retry never calls the action service. Recall failure permits automation only when authoritative facts required by the active policy remain available, otherwise no automatic credit. Verify restart persistence under the approved acceptance scope.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-20 — [T11] Build thin analyst view and review queue

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-7**; updated `2026-10-26T17:01:13.248+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T11
Epic: KAN-7
Dependencies: T08 (memory display requires T10)</p><p>IMPLEMENTATION
Build one thin interface (e.g. Streamlit) using the existing orchestrator, with dispute selector, source facts, policy version, investigator recommendation, critic feedback, final simulated status, duplicate result and human-review queue. Label live/sample data honestly.</p><p>DEFINITION OF DONE
Judge can follow case and reasoning without terminal SQL; UI does not duplicate policy or action implementation; safe rerun/reset described.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4 prototypes do not supply the canonical analyst UI or persisted review queue.
- Show four business outcomes, critic verdict and separate persistence status, source/rule citations and missing-evidence categories. Display only actually persisted review items as queued; failed persistence is review recommended, not persisted.
- Advisory history notices are not mandatory holds or fraud findings. Ordinary policy-permitted credit, evidence requests and declines run without a compulsory Approve button. Full manual adjudication/approval/writeback stays outside the MVP unless separately assigned.
- Acceptance additions: thin UI over the existing controller/action service, no duplicate policy/write path, duplicate-click safety and truthful persisted-queue/no-memory/live/sample labels. A queue lifecycle label is not a fifth business outcome.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-21 — [T12] Run cross-component failure tests and repeatable reset

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-8**; updated `2026-10-26T17:01:16.148+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T12
Epic: KAN-8
Dependencies: T08, T10, T11 for full demo</p><p>IMPLEMENTATION
Run integration matrix covering eligible case, duplicate sequential and concurrent attempts, partial refund, policy boundary, missing evidence, stale commit, fabricated references, provider failure, H-MEM restart and isolated demo reset. Separate not-run live tests from passed unit mocks.</p><p>DEFINITION OF DONE
Repeatable end-to-end runs with no unintended credit or manual repair; sanitized traces and actual commands/pass/fail/skip counts recorded.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4 adds dispute-demo/agent/tests/ outside the documented dispute-demo/tests/ discovery root; prototype imports depend on test sys.path injection. Green root tests alone do not collect all prototype tests.
- Collect both roots during migration and smoke-test normal runtime package imports without test-only path injection. Consolidate deliberately; establish offline collection in affected earlier tasks, not only at T12.
- Extend the integrated matrix with four-outcome round trips/persistence, missing/unusable evidence, mandatory-review no-credit behavior, non-credit new-evidence lifecycle, changed-payload reuse rejection, independent PostgreSQL source-writer concurrency, stale commits, rollback and lost-acknowledgement recovery.
- Include source-verified history and false/stale/cross-customer/future memory, recall failure, restart, and post-commit save failure. A memory retry must never repeat the action. Cover duplicate UI clicks and persisted review display.
- Acceptance additions: no hidden uncollected suite; exact interpreter/environment and collected/pass/fail/error/skip counts; separately labelled unit/mock/reference/live evidence and NOT RUN blockers. Reset only intentionally selected isolated demo state/memory, never source/shared data.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-22 — [T13] Package evidence-backed demo and submission

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-8**; updated `2026-10-26T17:01:18.912+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: T13
Epic: KAN-8
Dependencies: T12, A01</p><p>IMPLEMENTATION
Produce accurate README/setup, .env.example (no secrets), architectural diagram, tracked demo IDs, sanitized trace, slides/video and submission links following authenticated HackOS rules. Check team access and uploaded artifact visibility.</p><p>DEFINITION OF DONE
A teammate can reproduce the demo; security check passes; portal formats and links verified; no unsupported sponsor integration claims.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: PR #4 is reusable prototype work, not a completed agent or evidence of genuine Nightshift/H-MEM execution in the final workflow.
- Demonstrate autonomous policy-permitted provisional_credit, request_evidence and decline, plus policy-required human_review with no credit, using inspected source/fixture-backed IDs. Include duplicate prevention, one bounded critic correction and real memory continuity when verified.
- Acceptance additions: label simulated effects, live model/data calls, reference H-MEM, prototypes, mocks, sample/fault-injection and no-memory modes truthfully. Claim a named responding model or persistence only with evidence. Another teammate can reproduce tested commands; deliverables follow A01's authenticated requirements.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

### KAN-23 — [A01] Confirm authenticated HackOS challenge and submission requirements

Snapshot: status **To Do**; assignee **Unassigned**; parent **KAN-4**; updated `2026-10-26T17:01:21.700+0800`; links **none**. Summary remains unchanged.

Current description, exact HTML returned by Jira:

```html
<p>Roadmap task: A01
Epic: KAN-4
Dependencies: None; parallel throughout</p><p>IMPLEMENTATION
Open authenticated HackOS Track 3 and submission instructions. Record actual deadline/timezone, required sponsor technologies (including H-MEM/NVIDIA if applicable), repo/slide/video formats, uploading procedure and chosen fixture IDs. Distinguish public course build-window timing from confirmed portal submission cutoff.</p><p>DEFINITION OF DONE
Authenticated checklist and screenshot/notes recorded; ambiguous requirements are not guessed; T13 references confirmed requirements.</p><p>EXECUTION RULE
Read repository context.md, ROADMAP.md and agent.md. Inspect actual source. Work on only this task, run tests, record exact results in ROADMAP.md, and stop. Never mark complete without verification; no real payments or secrets.</p>
```

Append exactly this content (preserve its wording and list structure when converting to Jira rich text):

```markdown
## Post-merge alignment — 27 October 2026

- Implementation evidence: neither PR #4 nor this alignment verifies authenticated HackOS requirements.
- Explicitly check whether human approval or a specific memory implementation/behavior is mandated, alongside existing technology/model, deadline/timezone and submission-format checks. Selective human review is project product direction, not a confirmed competition requirement.
- Cursor is optional under current team guidance; record and reconcile any contrary portal requirement rather than inventing a mandatory editor.
- Acceptance additions: dated authenticated evidence for actual requirements, or precise access/verification blockers. Do not infer obligations from prototypes, old public summaries or this handoff.

Source: [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4), merge 76db7724ed8e32fac8b0fabaf33c556ddaa3bd29; repository context.md and ROADMAP.md. Source inspection only in this alignment; no task acceptance is claimed.
```

## Approval gate and application protocol

The user's explicit request and supplied handoff sections 6.4/7 required approval. The initial documentation pass made no Jira changes. The user subsequently approved the question below with “yes u may”; the description-only updates have now been applied and verified. This approval did not authorize implementation, status changes or publication.

> May I apply these Jira description/acceptance updates to KAN-11–KAN-23, leaving summaries, statuses, assignees, existing task IDs and completed T00/T01 unchanged?

Application protocol followed: each issue was re-read immediately before its edit in lossless HTML. Its description, summary and updated timestamp matched the approved snapshot. The original HTML was preserved, apart from the approved KAN-14 phrase replacement, and each addendum was appended once. Every saved description was read back and compared to the approved content; no concurrent conflicting edit was found. A final 20-issue read verified the protected fields and excluded issues.

T10 remains conditional: this pass records advisory history as the working default but does not approve a binding numeric rule or close the original history-rule acceptance gate. Confirm advisory acceptance scope or the exact versioned rule during its assigned implementation. T04/T05 lifecycle/duplicate/replay decisions, T09 portability and A01 portal requirements remain open.

Recommended next implementation assignment: **T02 / KAN-11 only**. Stop after this alignment; no next task has started.

## Application receipt — 27 October 2026

Applied through `editJiraIssue` with `fields={description: ...}`, `contentFormat=html`, and `responseContentFormat=html`. No summary, status, assignee, resolution, parent, label, link, comment or attachment field was submitted. Fresh pre-edit reads and individual post-edit reads used `getJiraIssue`; the final audit repeated the original 20-issue JQL search.

All 13 descriptions match the approved content and structure. Jira serialized apostrophes as `&#039;` in some additions; comparison normalized that equivalent entity without changing wording or rewriting an already-correct issue. KAN-14 contains the approved retry phrase correction. Every issue has exactly one alignment addendum.

| Issue | Saved updated timestamp (+08:00) | Verification |
|---|---|---|
| KAN-11 | 2026-10-27T02:06:30.222+0800 | Description matches; protected fields unchanged |
| KAN-12 | 2026-10-27T02:07:10.141+0800 | Description matches; protected fields unchanged |
| KAN-13 | 2026-10-27T02:07:12.936+0800 | Description matches; protected fields unchanged |
| KAN-14 | 2026-10-27T02:07:49.017+0800 | Description and retry correction match; protected fields unchanged |
| KAN-15 | 2026-10-27T02:07:52.541+0800 | Description matches; protected fields unchanged |
| KAN-16 | 2026-10-27T02:07:56.818+0800 | Description matches; protected fields unchanged |
| KAN-17 | 2026-10-27T02:08:00.140+0800 | Description matches; protected fields unchanged |
| KAN-18 | 2026-10-27T02:08:02.899+0800 | Description matches; protected fields unchanged |
| KAN-19 | 2026-10-27T02:08:17.297+0800 | Description matches; protected fields unchanged |
| KAN-20 | 2026-10-27T02:08:20.444+0800 | Description matches; protected fields unchanged |
| KAN-21 | 2026-10-27T02:08:23.498+0800 | Description matches; protected fields unchanged |
| KAN-22 | 2026-10-27T02:08:26.232+0800 | Description matches; protected fields unchanged |
| KAN-23 | 2026-10-27T02:08:29.468+0800 | Description matches; protected fields unchanged |

Final audit: 20 issues, no further page. Summaries, statuses, assignees, IDs, epic membership, labels and issue links match the pre-edit read. KAN-4–KAN-10 also retain their exact descriptions and updated timestamps; KAN-9/KAN-10 remain Done. KAN-11–KAN-23 remain To Do. No issue was assigned, transitioned or completed. T10's policy/scope decision remains open. Application tests and live application integrations were NOT RUN; no runtime/policy/data edits, commits, pushes or merges occurred.
