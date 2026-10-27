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
| [Pure critic](./dispute-demo/docs/critic.md) | T06 validation, supported rationale/citations, correction limits and retired SQLite writer. |
| [Nightshift investigator](./dispute-demo/docs/investigator.md) | T07 typed model/read envelopes, bounded transport, correction and real read-only inference evidence. |
| [Atomic actions](./dispute-demo/docs/actions.md) | T05 write interface, protected rereads, recovery, PostgreSQL test setup and deployment limits. |
| [Decision storage](./dispute-demo/docs/storage.md) | T04 PostgreSQL migration, revision guard, lifecycle/duplicate scope and isolated integration tests; deployment boundary. |
| [Policy evaluation](./dispute-demo/docs/policy.md) | T03 typed evaluator, supported synthetic evidence/ledger semantics, offline and live acceptance results. |
| [Typed retrieval](./dispute-demo/docs/retrieval.md) | T02 read interfaces, case/customer scope, error statuses, live/offline checks and unsupported freshness/decision storage. |
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 27 October 2026:** T00–T07 are complete against repository gates. The [Nightshift investigator](./dispute-demo/docs/investigator.md) returns typed proposals or approved read requests with strict binding, one correction and bounded transport. **121 tests pass**, with 45 PostgreSQL opt-in skips; four compatibility tests and data validation pass. [Live evidence](./dispute-demo/docs/evidence/t07-live-DP-0014.json) records real Zetaris facts, a 6,000-minor-unit model proposal and an accepted pure critique. Requested route: `meterless/auto`; reported response model: `nvidia/nemotron-3.5-bolt-e4b`. No action was persisted.

T05's atomic action service and T04 storage are tested in isolated PostgreSQL. Shared deployment, runtime writer credentials and coherent fresh Zetaris reads remain pending. Current reads return null revisions and cannot commit. T08 must resolve that deployment gate and implement the bounded controller before claiming a live end-to-end flow.

The target uses one Nightshift investigator, a pure deterministic critic and one PostgreSQL action service. Policy-permitted `provisional_credit`, `request_evidence` and `decline` run autonomously; `human_review` is exceptional and creates no credit. Only confirmed persistence creates a queued review item. Verified history remains advisory; no numeric history policy has been introduced. T10 still needs an explicit advisory-scope acceptance decision or an approved versioned history rule.

Next: **[T08 / KAN-17 — Bounded workflow and command-line runner](https://luijoel24.atlassian.net/browse/KAN-17)**. The current user goal explicitly authorizes proceeding through the full roadmap sequentially, with Jira completion evidence and a commit/push to `origin/main` after every accepted task. Individual handovers below remain single-task templates.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on T08 / KAN-17 only:
https://luijoel24.atlassian.net/browse/KAN-17

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and applicable
sources. Verify T02/T03/T05/T06/T07 interfaces. Resolve shared deployment,
restricted runtime credentials and coherent fresh Zetaris reads. Build the
bounded controller/CLI, consume every model/tool attempt from run budgets,
allow one correction, reject unresolved model uncertainties and preserve
confirmed commits independently of optional post-commit work. Label no-memory
mode. Prove actual Zetaris + Nightshift + persisted synthetic result, duplicate
prevention and correction/safe failure. Update docs/Jira, commit and push only
after acceptance; never claim queued review without confirmed persistence.

```

Next task: **T08 / KAN-17: bounded workflow and command-line runner**.
T09 and A01 are independently ready. T08–T13 and A01 remain NOT_STARTED.
