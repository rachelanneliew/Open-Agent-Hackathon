# Synthetic Card-Dispute Resolution Agent

An analyst selects a fictional card dispute. The application reads evidence through Zetaris, applies versioned policy, obtains a Nightshift Investigator proposal, checks it with a deterministic critic and a separate Nightshift Reviewer and records a simulated outcome atomically in PostgreSQL. Source-verified H-MEM history supplies advisory context.

**Track 3: Reasoning Architecture. Team: bob the builder.** All data, policies and financial effects are synthetic. Ordinary eligible credit, evidence requests and declines run autonomously. Policy-required review has no credit effect.

- [Run the demo](./docs/submission/DEMO.md): clean-checkout rehearsal, live setup, exact cases and recovery.
- [Architecture and sponsor evidence](./docs/submission/ARCHITECTURE.md): component roles, source links, provenance and limitations.
- [Submission package](./docs/submission/README.md): deck, narrated video, requirements and remaining owner checks.
- [Current implementation status](./context.md) and [task evidence](./ROADMAP.md).

## Quick start

Use macOS/Linux, Python 3.10+, Docker and the pinned Node 24.13.0/npm 11.18.0. The [walkthrough](./docs/submission/DEMO.md) provides first-time dependency/image setup. With that setup complete, run from `dispute-demo/`:

```sh
.venv/bin/python -m demo.replay                # preview only
.venv/bin/python -m demo.replay --reset-isolated-demo
.venv/bin/python -m demo.verify               # both roots, explicit skips
.venv/bin/python -m demo.verify --integrations
```

The rehearsal uses real disposable PostgreSQL and reference H-MEM with **scripted model responses and direct isolated reads**. It makes no live Zetaris/Nightshift call and resets no shared state. T16 passed **298 main + 16 reference tests, zero skips**. Dated live receipts separately establish actual integration behavior.

For the normal live app, follow [TEAM_SETUP](./TEAM_SETUP.md), then run `.venv/bin/python -m app.ui` from `dispute-demo/` and open `http://127.0.0.1:8931`. It needs private service credentials, the licensed Zetaris/JDBC bundle, restricted action access and pinned reference setup. A clone alone does not provision these services. Malformed model output fails visibly without a sample fallback.

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
| [Independent Reviewer](./dispute-demo/docs/reviewer.md) | Separate role, strict feedback and bounded correction with no write authority. |
| [Canonical workflow](./dispute-demo/docs/workflow.md) | T08 CLI, coherent fresh reads, bounded transitions, recovery and real persisted acceptance. |
| [Reliability and reset](./dispute-demo/docs/reliability.md) | Both test roots, failure coverage, explicit isolated reset/replay and evidence labels. |
| [Analyst workbench](./dispute-demo/docs/analyst-ui.md) | Local UI, persisted review queue, exact-request recovery and memory-only retry. |
| [Zetaris USL extension](./docs/zetaris-usl/README.md) | U00–U06: three independent sources, genuine semantic model, native DQ and optional read-only preview. |
| [H-MEM reference](./dispute-demo/docs/memory.md) | T09/T10 pinned engine, source-verified advisory history, post-commit storage and action-free memory retries. |
| [Atomic actions](./dispute-demo/docs/actions.md) | T05 write interface, protected rereads, recovery, PostgreSQL test setup and deployment limits. |
| [Decision storage](./dispute-demo/docs/storage.md) | T04 PostgreSQL migration, revision guard, lifecycle/duplicate scope and isolated integration tests; deployment boundary. |
| [Policy evaluation](./dispute-demo/docs/policy.md) | T03 typed evaluator, supported synthetic evidence/ledger semantics, offline and live acceptance results. |
| [Typed retrieval](./dispute-demo/docs/retrieval.md) | T02 read interfaces, case/customer scope, error statuses, live/offline checks and unsupported freshness/decision storage. |
| [Shared contracts](./dispute-demo/docs/contracts.md) | T01 types, outcome mapping, policy boundaries, workflow/synchronization requirements and unresolved decisions for later tasks. |
| [Jira post-merge change record](./docs/planning/JIRA_POST_MERGE_CHANGESET.md) | Created 27 October 2026: approved preview, pre-edit snapshots and verified application receipt for KAN-11–KAN-23. |
| [Hackathon handbook](./Open_Agent_Hackathon_2026_Complete_Handbook.md) | Historical background; current requirements and access gaps are in the [A01 checklist](./docs/competition.md). |

For the current task and its Jira issue, start with the task board in [ROADMAP.md](./ROADMAP.md). Coding assistants must first follow [AGENTS.md](./AGENTS.md).

## Delivery status

T00–T16 and A01 are complete against their repository acceptance gates after the T16 checks recorded in the roadmap. The current [submission package](./docs/submission/README.md) includes a two-agent deck, narrated video and dated real acceptance/refusal traces. Historical one-agent artifacts remain available as fallback evidence.

**HackOS submission remains unverified and leader-only.** The last authenticated deadline was **27 October 2026 23:45 UTC / 28 October 07:45 SGT**. Two separate live model roles are demonstrated; organizer acceptance is not claimed. The new [USL addendum](./docs/submission/USL_ADDENDUM.md) supplies separately dated PostgreSQL/CSV/REST federation and native DQ evidence. The original media is unchanged; the USL extension was developed on `codex/zetaris-usl` and is covered by the user's subsequent PR-and-merge authorization.

The completed T14–T16 source and package are published on `main`. Coding assistants must follow [AGENTS.md](./AGENTS.md) and the stable Jira mappings in the roadmap.
