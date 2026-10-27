# Synthetic Card-Dispute Resolution Agent

Open Agent Hackathon project for investigating fictional card disputes and recommending simulated outcomes. See [context.md](./context.md) for the project scope and verified implementation status.

## Documentation guide

| File | What it explains |
| --- | --- |
| [AGENTS.md](./AGENTS.md) | Entry instructions for coding assistants: required reading, verification and scope rules. |
| [context.md](./context.md) | **What we are building:** product scope, architecture, safety boundaries, implemented capabilities and gaps. |
| [ROADMAP.md](./ROADMAP.md) | **What to do next:** Jira mappings, task dependencies, implementation checklists, acceptance criteria and completion evidence. |
| [agent.md](./agent.md) | **How to work:** which source files to inspect for each task, operating rules and completion requirements. |
| [CLAUDE.md](./CLAUDE.md) | Directs Claude Code to the same shared instructions. |
| [TEAM_SETUP.md](./TEAM_SETUP.md) | Environment setup: Docker, PostgreSQL, Zetaris/JDBC and Nightshift. |
| [Policy v1](./dispute-demo/policies/synthetic_policy_v1.md) / [Policy v2](./dispute-demo/policies/synthetic_policy_v2.md) | Exact fictional dispute rules that the implementation must follow. |
| [Policy evaluation](./dispute-demo/docs/policy.md) | T03 typed evaluator, supported synthetic evidence/ledger semantics, offline and live acceptance results. |
| [Typed retrieval](./dispute-demo/docs/retrieval.md) | T02 read interfaces, case/customer scope, error statuses, live/offline checks and unsupported freshness/decision storage. |
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 27 October 2026:** T00–T03 are complete against repository acceptance gates. T03 / KAN-12 is implemented locally on `codex/t03-policy-evaluation` from `3106cd5`: **70 main tests, 6 prototype critic tests, data validation and eight live JDBC policy evaluations pass**. All 40 authored cases match offline. User-authorized startup of the existing local stack resolved the initial live blocker. Jira is unchanged. Next: **[T06 / KAN-15 — Build the mandatory pure critic](https://luijoel24.atlassian.net/browse/KAN-15)**, only when assigned.

[Typed retrieval](./dispute-demo/docs/retrieval.md) supplies source context and history. The [canonical policy evaluator](./dispute-demo/docs/policy.md) now evaluates that context; the old prototype policy module delegates. Source revisions remain null, and canonical action storage/freshness is not implemented. The SQLite-writing critic, deterministic resolver and H-MEM adapters remain unintegrated prototypes.

The target uses one Nightshift investigator, a pure deterministic critic and one PostgreSQL action service. Policy-permitted `provisional_credit`, `request_evidence` and `decline` run autonomously; `human_review` is exceptional and creates no credit. Only confirmed persistence creates a queued review item. Verified history is advisory by default; the prototype's three-claim count is not binding policy. T10 still needs an explicit advisory-scope acceptance decision or an approved versioned history rule.

For T06, adapt [the existing critic](./dispute-demo/agent/critic.py) into a pure function over `DisputeContext`, `PolicyResult` and `AgentProposal`, returning a bound `CriticResult`. Use the real [T03 evaluator](./dispute-demo/app/policy_engine.py), preserve mandatory-review exclusion of credit, and check source/rule citations, identity/cutoff/version, amounts and factual support. No critic path may write a credit or call the action service. Keep action persistence and duplicate prevention in their T04/T05 scope.

Acceptance requires valid typed proposals passing and crafted invalid proposals failing, with purity checks across all branches. Follow T06's full roadmap checklist. T03's read-only CLI remains documented in [policy.md](./dispute-demo/docs/policy.md); it evaluates eligibility without persisting decisions.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on T06 / KAN-15 only:
https://luijoel24.atlassian.net/browse/KAN-15

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and the
applicable sources. Verify T02/T03 prerequisites; preserve existing changes.
Reuse the prototype critic's checks, canonical schemas and actual typed
policy outputs. Return a pure CriticResult with reference/proposal binding,
source/rule citations, amount and policy checks, and structured feedback.
Mandatory review blocks credit. No critic branch may write an action.

Replace critic-write expectations with purity tests; do not implement the
PostgreSQL action service in this task. Report exact checks and update the
roadmap/context. Jira edits and publication require authorized scope.
Stop after T06 and recommend the next dependency-ready task.

```

Next recommended task: **T06 / KAN-15: build the mandatory pure critic**.
T04, T09 and A01 may be assigned separately when prerequisites are satisfied.
T04–T13 and A01 remain NOT_STARTED; no next task was begun.
