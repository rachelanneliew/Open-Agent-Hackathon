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
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 27 October 2026:** T00 / KAN-9 (baseline verification) and T01 / KAN-10 (shared contracts) remain complete. [PR #4](https://github.com/rachelanneliew/Open-Agent-Hackathon/pull/4) is merged; this documentation pass inspected local source at `76db7724ed8e32fac8b0fabaf33c556ddaa3bd29`. The next implementation task is **[T02 / KAN-11 — Expose narrow case and history retrieval tools](https://luijoel24.atlassian.net/browse/KAN-11)**, under epic KAN-4. Recheck the roadmap and Jira when taking over, because this snapshot may become outdated.

The existing [agent prototypes](./dispute-demo/agent/) include a policy evaluator, a critic with a SQLite credit writer, a deterministic resolver, and H-MEM client/bridge/memory modules with a separate [test directory](./dispute-demo/agent/tests/). They need integration with the strict [canonical schemas](./dispute-demo/app/schemas.py); the resolver is not a completed Nightshift agent. PostgreSQL action storage, pure critic separation, bounded workflow, portable memory setup and integration acceptance remain outstanding. Historical T00/T01 tests are dated evidence; application tests and live application checks were NOT RUN for this documentation pass.

The target uses one Nightshift investigator, a pure deterministic critic and one PostgreSQL action service. Policy-permitted `provisional_credit`, `request_evidence` and `decline` run autonomously; `human_review` is exceptional and creates no credit. Only confirmed persistence creates a queued review item. Verified history is advisory by default; the prototype's three-claim count is not binding policy. T10 still needs an explicit advisory-scope acceptance decision or an approved versioned history rule.

For T02, adapt the existing Zetaris/JDBC retrieval to the [T01 contracts](./dispute-demo/docs/contracts.md), preserving PR #4's transaction `customer_id` addition. Return scoped, time-visible transactions, settlements, evidence and policy; add separate typed customer-history/current-state reads as the actual tables allow. Do not put historical records into the current case's isolated collections. Preserve metadata with missing evidence text and incomplete inputs explicitly. Expose only validated, allowlisted read tools. The checked-out source has no revision guard or decision migration; report unsupported revisions/storage honestly and verify live availability separately.

T02 is complete only when tests cover scope, future-record filtering and failure modes, and a live case is retrieved through Zetaris when available, with live versus stubbed evidence clearly recorded. Follow the full roadmap checklist. This task does not implement arbitrary SQL tools, source mutation or simulated action writes.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on T02 / KAN-11 only:
https://luijoel24.atlassian.net/browse/KAN-11

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and the
task-specific sources before execution. Verify T01's completion evidence
and read dispute-demo/docs/contracts.md and the existing retrieval code.

Implement the full T02 checklist and retrieval tests. Reuse Zetaris/JDBC
and preserve the transaction customer_id addition. Enforce scope/cutoff,
preserve missing evidence text, separate typed history from current-case
collections, and distinguish missing data from service failure. Expose
only validated read tools. Do not invent source revisions or claim
decision-table reads are live before T04 storage/registration exists.

Update ROADMAP.md and context.md where required. Jira edits and publication
require separately authorized scope. Report changed files, exact test
results, blockers and the next recommended task, then stop.
```

After T02 passes, recommend **T03 / KAN-12: integrate and harden the existing policy evaluator**. T04, T09 and A01 may be assigned separately when their prerequisites are satisfied; this is not authority to start them. T02–T13 and A01 retain NOT_STARTED acceptance status despite prototype evidence. After the initial local alignment, the user approved the KAN-11–KAN-23 Jira description updates; all 13 were applied and verified on 27 October 2026 without changing summaries, statuses, assignees or task IDs. The alignment and Jira follow-up changed documentation and issue descriptions only; the separately requested Git publication is recorded in ROADMAP.md.
