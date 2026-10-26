# Hackathon Repository Instructions

This is the agent entry point for the entire Open Agent Hackathon repository. Keep the filename exactly `AGENTS.md`. All paths below are relative to this repository root, even when working in a subdirectory.

## Required reading before execution

At the start of every task/session, complete these steps **before planning implementation, editing files, running project code or tests, starting services, or making API/database calls**. Read-only tools needed to locate and read these instructions and their referenced files are allowed during this bootstrap.

1. Read [`context.md`](./context.md) in full for the canonical project brief, architecture, and safety boundaries.
2. Read [`ROADMAP.md`](./ROADMAP.md) in full for the single assigned task ID (T00–T13 or A01), its Jira mapping, dependencies, status, and acceptance gate. Dated progress reports and older ticket numbering are historical evidence, not the active backlog.
3. Read [`agent.md`](./agent.md) in full for shared operating rules and the task-specific reading map. Complete the applicable reading in that map before executing the task.
4. Read any more-specific `AGENTS.md` governing the files or tooling involved. In particular, [`getting-started/AGENTS.md`](./getting-started/AGENTS.md) governs the bundled Zetaris onboarding project; preserve its instructions and follow its connection workflow when using its tooling.
5. Inspect the relevant current source, policies, schemas, and tests. Documentation and roadmap checkboxes are not proof of implementation or live service availability.

If a required file is missing or unreadable, report the specific path and resolve that gap before proceeding with work that depends on it. Do not substitute a similarly named file from Downloads or another checkout.

The user's explicit task takes precedence over the roadmap's suggested next task. For roadmap work, complete **one assigned task only** and verify its prerequisites against source and test evidence. Report missing dependencies instead of silently implementing the whole roadmap. If asked to choose and implement the next task, select one dependency-ready task. A specific user request outside the roadmap can be completed without inventing a task ID. Preserve existing user changes and project-specific instructions.

## Before finishing

Run checks appropriate to the change and report exact commands, results, and blockers; label unavailable live checks NOT RUN. Update the assigned task and work log in [`ROADMAP.md`](./ROADMAP.md) with factual acceptance evidence; mark DONE only when its gate is satisfied. Update [`context.md`](./context.md) when scope, architecture, contracts, or verified capabilities materially change. For documentation-only work, validate links and paths without claiming that application integrations were tested. **Stop after the assigned task:** recommend the next task but do not start it automatically. Importing Jira links does not verify issue status or authorize Jira changes.
