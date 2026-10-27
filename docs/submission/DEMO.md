# Reproduce the synthetic dispute demo

All financial effects are fictional. The normal application uses live Zetaris
and Nightshift with a restricted PostgreSQL action service. The isolated
rehearsal uses scripted model responses and direct disposable PostgreSQL reads.
It executes the same policy, critic, controller and action service, plus the
real pinned H-MEM reference with mock embeddings. It does not call Zetaris or
Nightshift and is never a silent fallback for them.

## Fresh checkout: isolated rehearsal

Requirements: macOS/Linux, Git, Python 3.10+ (tested 3.13.7), Docker already
running, Node **24.13.0** and npm **11.18.0** selected on PATH. The actual
reference adapter uses POSIX file locks. Windows requires a compatible WSL
setup, which has not been tested. No provider, database or Zetaris secret is
needed for this route.

```sh
git clone https://github.com/rachelanneliew/Open-Agent-Hackathon.git
cd Open-Agent-Hackathon/dispute-demo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-runtime.txt
node --version
npm --version
export HMEM_NODE="$(command -v node)"
.venv/bin/python scripts/setup_hmem.py
npm --prefix agent/hmem_bridge ci --ignore-scripts --no-audit --no-fund
# One-time preparation if the image is absent. Runtime never pulls images.
docker pull postgres:16-alpine
.venv/bin/python scripts/validate_synthetic_data.py
.venv/bin/python -m demo.replay
.venv/bin/python -m demo.replay --reset-isolated-demo > rehearsal.json
```

The preview makes no state changes. The explicit flag creates one owned
container and two independent database/memory/journal namespaces, then removes
only those resources. It accepts no existing target. Each cycle ends with eight
decisions, four simulated credits and one pending review. Expect `status:
"passed"` and two cycles. Preserve the JSON for inspection. Never reset the
shared database to reproduce a recording. See [reset safeguards](../../dispute-demo/docs/reliability.md).

For checks from the same directory:

```sh
.venv/bin/python -m demo.verify
.venv/bin/python -m demo.verify --integrations
```

The first collects both roots with explicit skips. The second needs the same
Docker/reference setup and uses real isolated database/reference/loopback HTTP
checks. T16 recorded **298 + 16 passing tests, zero skips**. This is functional
and safety evidence, not a live model accuracy benchmark.

The outer repository records `getting-started` and `zetaris-platform` as
Git links without `.gitmodules`. A clean clone leaves them empty. The isolated
rehearsal above does not need them. Do not claim that cloning alone provisions
the live stack.

## Live CLI and analyst interface

Follow [TEAM_SETUP](../../TEAM_SETUP.md) sections 1–8 and the
[workflow deployment guide](../../dispute-demo/docs/workflow.md). Obtain the
licensed Zetaris bundle, matching JDBC JAR, private Zetaris account, Nightshift
provider/runtime access and a local project database. The bundled onboarding
workflow and JDBC preflight must pass first. `dispute` is the datasource name.
Migrations 001 then 002 and four registered read views are required for coherent
fresh reads. Provision an unprivileged LOGIN with only `dispute_action_writer`.
Never use the loader or metastore account for application decisions.

Use [the sanitized environment example](../../dispute-demo/integration/env.example)
for private `dispute-demo/.env.local`. Keep `DISPUTE_ACTION_DSN` and
`METERLESS_RUNTIME_TOKEN` blank until locally configured. JDBC settings belong
in private `getting-started/.env.local`: `ZETARIS_JDBC_URL`,
`ZETARIS_JDBC_JAR`, `ZETARIS_USERNAME`, `ZETARIS_PASSWORD`. The provider API key
stays inside Nightshift. Export `HMEM_NODE` as above and keep private files at
mode 0600. Preserve existing configuration instead of copying over it.

After setup, from `dispute-demo/`:

```sh
.venv/bin/python -m app.ui --memory-dir outputs/demo-memory
# Open http://127.0.0.1:8931 and select a case. Ctrl-C stops this local server.
# Alternatively, run one live CLI investigation:
.venv/bin/python -m app.main DP-0014 --memory-dir outputs/demo-memory
# Explicitly disable all memory work when that comparison is intended:
.venv/bin/python -m app.main DP-0014 --no-memory
```

A new live investigation can persist a simulated decision. On the team's
existing sandbox DP-0014 and DP-0017 already have credits, and DP-0020 has a saved evidence request, so fresh ordinary
runs must not add another. An empty memory directory has no seeded history.
Use the same private memory directory across related runs. The team's dated
acceptance used `outputs/t10-live-memory`, which is deliberately not in Git.
The analyst server is loopback-only and must not be exposed through a tunnel.

UI workflow: select case, inspect source facts, click **Investigate**, then
read the distinct outcome, critic, Reviewer and persistence fields. The Agent
collaboration table shows each role, correction provenance, proposal identity
and final acceptance gate. Expand evidence and
inspect policy citations. Only confirmed pending reviews appear in the queue.
There is no mandatory Approve click or manual adjudication feature.

## Case walkthrough and evidence labels

| Case | Source-defined demonstration | Recorded evidence |
|---|---|---|
| DP-0014 | SGD 100 capture, SGD 40 merchant refund, SGD 60 simulated credit under v2. | Live T08 commit and same-request reuse, isolated rehearsal. |
| DP-0020 | Missing `refund_confirmation`, evidence request with no amount. | Isolated committed rehearsal. T16 live two-agent acceptance committed this evidence request with no credit. T11 earlier output failed validation. |
| DP-0029 | Outside the 30-day v1 filing window, decline with no amount. | Isolated committed rehearsal. T16 real Reviewer requested revision twice; one correction then safe refusal, no write. T13 earlier schema refusal is historical. |
| DP-0008 | Otherwise eligible amount above SGD 200 requires review, no credit. | Live T11 saved review and actual queue, isolated rehearsal. |
| DP-0017 | SGD 57.60 credit with source-verified earlier DP-0014 context for CUST-008. | Live T10 commit/memory-only reuse and isolated reference rehearsal. |
| DP-0003 | Exactly SGD 200 is eligible. Inject +1 minor unit, reject, correct once. | Labelled scripted fault with real isolated PostgreSQL. Live T08 fault instead stopped safely after malformed correction. |
| DP-0033 / DP-0034 | Opening immediately before/at v2 selects v1/v2: 30-day decline versus 45-day allowed SGD 100. | Inspected source/fixtures, T03 live read-only evaluation and isolated committed rehearsal. |

These outcomes come from the inspected source policies and test evidence.
Expected-result fixtures stay test-only and never enter a live prompt or tool.
A normal model can produce malformed output or a conservative Reviewer objection
and fail visibly. DP-0029 demonstrates a false-positive semantic challenge after
a terminal filing-window rule; its refusal is preserved, not silently overridden. Do not edit a
trace, change policy or retry indefinitely to force a desired recording.

Recovery uses the original full request, after inspecting the saved run ID:

```sh
.venv/bin/python -m app.main --retry-request "outputs/runs/<run_id>.request.json"
.venv/bin/python -m app.main --retry-memory "outputs/runs/<run_id>.trace.json" --memory-dir outputs/demo-memory
```

The first returns the original acknowledged decision as `reused` and cannot
create a second effective credit. The second verifies its source receipt and
only retries memory. Preserve both private request and trace. Never invent a
new idempotency key after an uncertain acknowledgement. CLI exit 0 means
confirmed persistence, exit 1 a refusal/failure, exit 2 invalid input/config.
Memory status is separate from action success.

## T16 two-agent evidence

- [Actual accepted workflow](../../dispute-demo/docs/evidence/t16-live-accepted.json): DP-0020, two separate live calls, critic/Reviewer acceptance and committed evidence request.
- [Actual feedback loop and refusal](../../dispute-demo/docs/evidence/t16-live-refusal.json): DP-0029, four real calls, one correction, no write.
- [Exact recovery](../../dispute-demo/docs/evidence/t16-recovery.json): same DP-0020 decision, zero model calls.
- [Isolated replay](../../dispute-demo/docs/evidence/t16-isolated-replay.json): DP-0020 uses an explicitly scripted Reviewer objection, revised proposal, critic and Reviewer recheck, then real isolated commit. DP-0003 retains the separate critic fault. Both cycles keep all four outcomes and memory verification.
- [Full matrix](../../dispute-demo/docs/evidence/t16-verification.json): 298 application + 16 reference tests.

Current runtime is on feature branch `codex/t14-t16-two-agent-reviewer`; check out that branch for this revision until it is reviewed and merged. Live T16 used `--no-memory`; combined two-agent memory behavior is verified by isolated reference tests. Earlier live memory evidence remains dated separately.

## Historical evidence to inspect

- [Live workflow](../../dispute-demo/docs/evidence/t08-live-workflow.json): source, proposal, critic, commit, recovery and safe refusal.
- [Live advisory memory](../../dispute-demo/docs/evidence/t10-verified-memory.json): verified prior receipt, new result and action-free memory retry.
- [Analyst UI](../../dispute-demo/docs/evidence/t11-analyst.json): real review queue/reuse and model failures.
- [Full verification](../../dispute-demo/docs/evidence/t12-verification.json) and [isolated replay](../../dispute-demo/docs/evidence/t12-isolated-replay.json): explicit real/scripted boundaries and all required safety demonstrations.
- [Authenticated requirements](../competition.md): actual deadline, required deliverables and unresolved B1–B4.

The source-verified H-MEM history is advisory and partial. No claim count implies
fraud or a mandatory hold. Rationale validation currently requires canonical
policy explanations and bounded synthetic document templates. General documents,
production authentication, real financial rails, advanced memory lifecycle and
three-source/USL federation remain outside the implementation.
