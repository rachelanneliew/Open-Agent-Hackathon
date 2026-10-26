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
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 26 October 2026:** T00 / KAN-9 (baseline verification) and T01 / KAN-10 (shared contracts) are complete. The next implementation task is **[T02 / KAN-11 — Expose narrow case and history retrieval tools](https://luijoel24.atlassian.net/browse/KAN-11)**, under epic KAN-4. Recheck the roadmap and Jira when taking over, because this snapshot may become outdated.

For T02, adapt the existing Zetaris/JDBC retrieval to the [T01 contracts](./dispute-demo/docs/contracts.md). Return scoped, time-visible transactions, settlements, evidence and policy; add narrow customer-history/current-state reads as the actual tables allow. Preserve missing evidence text and incomplete inputs explicitly. Expose only validated, allowlisted read tools. Source revisions and decision tables are currently unavailable; report that honestly rather than fabricating support.

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

Implement the full T02 checklist and retrieval tests. Reuse Zetaris/JDBC;
enforce scope and cutoff, distinguish missing data from service failure,
and expose only validated read tools. Do not invent source revisions or
claim decision-table reads are live before T04 storage exists.

You may update KAN-11 to In Progress when starting and add test evidence
and transition it to Done only when its acceptance gate is satisfied.
Update ROADMAP.md and context.md where required. Report changed files,
exact test results, blockers and the next recommended task, then stop.
```

After T02 passes, the next recommended implementation task is **T03 / KAN-12: deterministic policy evaluation**. Separately, **A01 / KAN-23** can be assigned to a teammate with HackOS access to verify competition and submission requirements alongside development. T02 and all later implementation tasks remain unstarted until assigned.
