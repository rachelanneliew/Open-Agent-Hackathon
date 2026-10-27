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
| [Decision storage](./dispute-demo/docs/storage.md) | T04 PostgreSQL migration, revision guard, lifecycle/duplicate scope and isolated integration tests; deployment boundary. |
| [Policy evaluation](./dispute-demo/docs/policy.md) | T03 typed evaluator, supported synthetic evidence/ledger semantics, offline and live acceptance results. |
| [Typed retrieval](./dispute-demo/docs/retrieval.md) | T02 read interfaces, case/customer scope, error statuses, live/offline checks and unsupported freshness/decision storage. |
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 27 October 2026:** T00–T04 and T06 are complete against repository gates. T06 delivers the [pure critic](./dispute-demo/docs/critic.md) with exact context/policy/proposal binding, corroborated citations and bounded feedback. **92 offline tests, 4 compatibility tests and data validation pass**; 20 PostgreSQL tests are explicitly skipped in this run. All 40 authored scenarios pass. No live service or deployment check was run for T06. [KAN-15](https://luijoel24.atlassian.net/browse/KAN-15) is verified Done with completion evidence.

[Typed retrieval](./dispute-demo/docs/retrieval.md) and the [canonical evaluator](./dispute-demo/docs/policy.md) provide the critic's inputs. The old SQLite write entry point now returns unavailable without touching local state. Rationale validation is deliberately limited to deterministic policy explanations; arbitrary prose routes to review. The [T04 migration](./dispute-demo/docs/storage.md) exists, but shared deployment/coherent reads and the T05 action service remain pending; runtime source revisions still return null.

The target uses one Nightshift investigator, a pure deterministic critic and one PostgreSQL action service. Policy-permitted `provisional_credit`, `request_evidence` and `decline` run autonomously; `human_review` is exceptional and creates no credit. Only confirmed persistence creates a queued review item. Verified history remains advisory; no numeric history policy has been introduced. T10 still needs an explicit advisory-scope acceptance decision or an approved versioned history rule.

Next: **[T05 / KAN-14 — Implement atomic simulated decision recording](https://luijoel24.atlassian.net/browse/KAN-14)**, only when assigned. Use the T04 guard/storage and real T03/T06 evaluator/critic. Recheck fresh authoritative state in one protected PostgreSQL transaction, bind the exact proposal/critic, record all four outcomes, reconcile identical retries and block duplicate credits. Follow T05's full roadmap gate, including real independent-connection tests; no T05 implementation has started.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on T05 / KAN-14 only:
https://luijoel24.atlassian.net/browse/KAN-14

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and applicable
sources. Verify T03/T04 prerequisites and the completed T06 critic.
Implement one canonical PostgreSQL simulated-decision service, with
protected current-state policy/critic rechecks, all four outcomes,
identical-payload retry reuse and changed-payload/duplicate rejection.
Unknown source revisions cannot commit. A failed write is not queued review.

Run real PostgreSQL independent-connection, rollback and retry tests;
preserve shared data and existing state. Record exact checks and update
roadmap/context. Jira edits and publication require authorized scope.
Stop after T05 and recommend the next dependency-ready task.

```

Next recommended task: **T05 / KAN-14: atomic simulated decision recording**.
T09 and A01 may be assigned separately. T05, T07–T13 and A01 remain NOT_STARTED.
