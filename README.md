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
| [Typed retrieval](./dispute-demo/docs/retrieval.md) | T02 read interfaces, case/customer scope, error statuses, live/offline checks and unsupported freshness/decision storage. |
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Background research and competition guidance. Current requirements still need verification under A01. |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Handover: what to do next

**Use [ROADMAP.md](./ROADMAP.md) as the source of truth for the next task.** It records each task's Jira issue, dependencies, required reading, work checklist, deliverable and acceptance gate. Its completion log records what was tested and any remaining blockers. Check the current task board and actual source before starting; older work-log entries describe historical states.

**Current handover, 27 October 2026:** T00 / KAN-9, T01 / KAN-10 and T02 / KAN-11 are complete against repository acceptance gates. T02 was implemented on `codex/t02-typed-retrieval` from published baseline `b850ae8`; KAN-11 is verified Done with completion evidence in comment `10003`. The next implementation task is **[T03 / KAN-12 — Implement deterministic policy evaluation](https://luijoel24.atlassian.net/browse/KAN-12)**. Recheck source, roadmap and Jira when taking over.

[Typed retrieval](./dispute-demo/docs/retrieval.md) now supplies case context, separate customer history, current source status and an explicit unsupported decision-read result. Fifty root-suite tests and six offline prototype critic tests pass, with separate live JDBC checks recorded in the roadmap. Source revisions remain null; action storage and commit freshness are not implemented.

The existing [agent prototypes](./dispute-demo/agent/) include the policy evaluator to integrate in T03, a SQLite-writing critic, deterministic resolver and H-MEM modules. Their remaining integration/acceptance work is not completed by T02. The resolver is not a Nightshift investigator; pure critic separation, PostgreSQL action storage, bounded workflow and portable memory setup remain outstanding.

The target uses one Nightshift investigator, a pure deterministic critic and one PostgreSQL action service. Policy-permitted `provisional_credit`, `request_evidence` and `decline` run autonomously; `human_review` is exceptional and creates no credit. Only confirmed persistence creates a queued review item. Verified history is advisory by default; the prototype's three-claim count is not binding policy. T10 still needs an explicit advisory-scope acceptance decision or an approved versioned history rule.

For T03, adapt [the existing evaluator](./dispute-demo/agent/policy_engine.py) to the strict [shared contracts](./dispute-demo/docs/contracts.md) and [T02 tools](./dispute-demo/app/tools.py). Return a bound `PolicyResult` with source-linked rule checks and explicit allowed/blocked outcomes. Preserve opening-date version selection, rule precedence, exact filing/review boundaries and primary-transaction settlement arithmetic. Treat missing/unusable text and malformed inputs safely; do not invent a history threshold or weaken contracts.

Acceptance requires deterministic policy tests for authored scenarios, boundaries and incomplete/malformed inputs with Nightshift disabled, plus evaluation of an actual retrieved context. Expected results stay test-only. Follow the full T03 roadmap checklist; no action writes belong to this task.

### Steps for the next teammate

1. Read [AGENTS.md](./AGENTS.md), then [context.md](./context.md), [ROADMAP.md](./ROADMAP.md) and [agent.md](./agent.md), followed by the task-specific sources they list. Use [TEAM_SETUP.md](./TEAM_SETUP.md) if your environment needs setup.
2. Confirm the single assigned task and its Jira issue. Check prerequisites against source and recorded test evidence, and preserve existing working changes.
3. Work through that task's checklist and acceptance gate. Record missing dependencies or unclear policy decisions instead of silently expanding scope.
4. Run the relevant checks and record exact commands, results and blockers in the roadmap. Label unavailable live checks **NOT RUN**. Update `context.md` if verified capabilities, contracts or architecture change.
5. When Jira updates are authorized, move the assigned issue to In Progress when starting, post completion evidence, and mark it Done only after its acceptance gate passes. Update the roadmap task board and work log together.
6. Hand over the changed files, commit/branch or PR, test results, remaining blockers and recommended next task. Stop after the assigned task; agree on ownership before starting the next one.

### Copyable task handover

```text
Work on T03 / KAN-12 only:
https://luijoel24.atlassian.net/browse/KAN-12

Follow AGENTS.md and read context.md, ROADMAP.md, agent.md and the
applicable sources before execution. Verify T01/T02 acceptance evidence.
Read the source policies, shared contracts, T02 retrieval and existing
prototype evaluator before editing.

Integrate one canonical deterministic evaluator returning PolicyResult.
Preserve source rules, opening-date version selection, exact boundaries,
integer money and primary-transaction balance semantics. Cover authored
scenarios and malformed/missing evidence with tests; fixtures remain
test-only. Do not add policy thresholds, model calls or action writes.

Update ROADMAP.md and context.md where required. Jira edits and publication
require separately authorized scope. Report changed files, exact test
results, blockers and the next recommended task, then stop.
```

After T03 passes, recommend **T06 / KAN-15: build the mandatory pure critic**, following the post-merge integration order. T04, T09 and A01 may be assigned separately when their prerequisites are satisfied. T03–T13 and A01 remain NOT_STARTED. The approved 27 October Jira description changes are retained in the change record; the separately authorized T02 Jira closure and publication preparation are recorded in ROADMAP.md.
