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
| [Canonical workflow](./dispute-demo/docs/workflow.md) | T08 CLI, coherent fresh reads, bounded transitions, recovery and real persisted acceptance. |
| [Reliability and reset](./dispute-demo/docs/reliability.md) | Both test roots, failure coverage, explicit isolated reset/replay and evidence labels. |
| [Analyst workbench](./dispute-demo/docs/analyst-ui.md) | Local UI, persisted review queue, exact-request recovery and memory-only retry. |
| [H-MEM reference](./dispute-demo/docs/memory.md) | T09/T10 pinned engine, source-verified advisory history, post-commit storage and action-free memory retries. |
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

**Current handover, 27 October 2026:** T00–T12 are complete against repository gates. The [analyst workbench](./dispute-demo/docs/analyst-ui.md) uses the canonical workflow, and the [reliability guide](./dispute-demo/docs/reliability.md) now provides complete test collection and an explicit isolated reset/replay command.

**267 main tests and 16 reference/compatibility tests pass with no skips.** The [two-cycle rehearsal](./dispute-demo/docs/evidence/t12-isolated-replay.json) covers all four outcomes, duplicate refusal, bounded correction, policy versions and real source-verified reference memory. Models are scripted and reads use isolated PostgreSQL; [dated live evidence](./dispute-demo/docs/evidence/t11-analyst.json) remains separately labelled. Shared totals remain three decisions, two credits, three audits and one review at revision 14; source fingerprints are unchanged.

From `dispute-demo/`, run `python -m demo.verify --integrations` with the documented dependencies. `python -m demo.replay` previews its scope; `--reset-isolated-demo` creates/replays/cleans only disposable state. Normal CLI/UI state is durable and is never reset by this command. The owner-approved advisory history remains nonbinding. Live model output can fail strict validation; such failures remain visible without effects.

Next: **[A01 / KAN-23 — Authenticated HackOS requirements](https://luijoel24.atlassian.net/browse/KAN-23)**, then **[T13 / KAN-22 — Demo and submission packaging](https://luijoel24.atlassian.net/browse/KAN-22)**. The current goal authorizes sequential completion with Jira updates and a commit/push to `origin/main` after each accepted task.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on A01 / KAN-23 only:
https://luijoel24.atlassian.net/browse/KAN-23

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and applicable
sources. Verify current authenticated challenge/submission requirements,
required technologies, formats, deadline/timezone and submission ownership.
Record unavailable portal details as explicit blockers; do not guess.
Update Jira and commit/push after the acceptance gate is satisfied.
```

Next: **A01 / KAN-23**, then **T13 / KAN-22**. Both remain NOT_STARTED.
