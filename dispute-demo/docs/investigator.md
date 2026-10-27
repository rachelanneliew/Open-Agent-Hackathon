# T07 Nightshift investigator

**T08 integration update:** the [workflow guide](./workflow.md) describes the
canonical controller, fresh coherent Zetaris snapshots, guarded shared sandbox
deployment, CLI and identical-request recovery. Earlier task acceptance and
deployment statements below are dated evidence. Historical T02 reads retain
their null revisions; normal runs use the new fresh snapshot adapter.

[Investigator.step](../app/investigator.py) makes one model call and returns an
immutable `InvestigatorResult`: a typed `AgentProposal`, an unexecuted
`ReadRequest`, or a sanitized failure. It never dispatches a tool, opens a ledger,
calls the action service or saves memory. The [legacy resolver](../agent/resolver.py)
remains a labelled deterministic prototype with a retired writer, not this model
integration. The canonical T08 workflow is `app.orchestrator.Controller` / `app.main`.

## Interface and trust boundary

Supply the current typed context and canonical policy, application-generated run
and proposal IDs, and revision 0. A revision-1 turn also requires the previous
revision-0 proposal and its exact, freshly recomputed `revise` critique. The new
proposal ID must differ; references and run ID must agree. Forged policy/feedback,
reused identities, a second revision and invalid budgets fail before a model call.

The system message supplies an evidence checklist and a compact proposal draft.
The user message contains case facts, evaluated policy, explicit citation
requirements derived from its evaluated checks, allowed reads and optional typed
observations. A full JSON Schema accompanies every investigator request. Statements/documents/observations
and prior model text are explicitly untrusted. Customer history is scoped to the
case, customer and cutoff and remains advisory. A changed context must be supplied
with reevaluated policy; observations cannot silently replace it. Runtime code
never reads source CSVs or expected-result fixtures.

Two responses are permitted:

```json
{"kind":"read","proposal":null,"request":{"name":"get_dispute_context","dispute_id":"DP-0014"},"uncertainties":[]}
```

or a proposal envelope with `request: null`. Its `proposal` has exactly four
fields: `recommendation`, `evidence_ids`, `policy_rule_ids`, `missing_evidence`.
The application attaches trusted run/proposal IDs, current source reference,
revision and `policy_rationale(policy)` to form the unchanged canonical
`AgentProposal`. These fields are no longer copied by the model. Model attempts
to supply them are rejected, not overwritten. Outcome, amount, currency,
citations, missing requirements and uncertainty remain model-provided and
subject to the existing critic. Four read names
come from the [existing registry](../app/tools.py); its controller must dispatch
`request.name` with `request.arguments()`. No SQL, write, customer, connection,
cutoff or arbitrary arguments are permitted. There is no native tool invocation.

The parser rejects duplicate JSON keys, nonfinite numbers, unknown fields,
markdown wrappers, missing/invalid proposal fields, out-of-scope reads, mismatched
references, refusals, multiple choices, native tool calls and truncated responses.
It does not extract a convenient JSON substring, repair answers, or replace a
model recommendation with the evaluator's answer. The pure critic still checks
amounts, evidence, rules and the application-rendered canonical rationale.
Broader model prose has not gained approval. No invalid recommendation is
repaired or substituted with a policy answer. Private response reasoning fields are discarded.

`uncertainties` contains at most eight source-linked statements of 240 characters
each. These are untrusted model assertions, not fraud findings or verified facts.
**A nonempty list must prevent the controller from committing this proposal**;
obtain authoritative facts/re-evaluate or return an honest no-credit failure.
Missing evidence categories remain the canonical typed proposal requirements.

## Transport and limits

[NightshiftClient](../app/nightshift.py) reuses the existing probe's `.env.local`
plus process override settings: `METERLESS_BASE_URL`, `METERLESS_RUNTIME_TOKEN`,
`METERLESS_MODEL`. Configuration loads only when explicitly requested. The token
is hidden from configuration repr and never enters prompts or process arguments.
Provider keys stay in Nightshift; no token or endpoint is model-selectable.

The [published Meterless provider contract](https://meterless.ai/engines.html)
(checked 27 October 2026) documents authenticated `/v1/models` and text chat
completions with the app/scope headers. T08 additionally inspected installed
Nightshift 0.92.7 (`proxy.js`, `orchestrator.js`, `providers.js`,
`structured-output.js`) and verified its JSON-object request path live. Calls
now send `response_format={"type":"json_schema", "json_schema": ...}` with
`strict: true`, `tool_choice="none"`,
`temperature=0`, `stream=false`, `max_tokens=4096`, and
`meterless-tier-split: off`. No native tools are supplied. This path disables
runtime semantic response caching and skips its answer-memory and reasoning
scaffold injection. Unsupported providers fail rather than dropping the
contract. The 27 October follow-up verified JSON Schema on the actual auto
route. Nightshift reports its NVIDIA adapter capability as `unverified` even
when runtime schema validation passes; provider-side enforcement is not claimed.
The schema uses the verified subset, including nullable objects, enums and array
bounds. A separate `uniqueItems` probe returned HTTP 502; its precise cause was
not established, so uniqueness stays in mandatory local contract checks.

The [draft schema](../app/investigator_contract.py) restricts citation IDs/counts
to the current evaluated policy checks and scopes read requests to the case.
For a filing-window decline with no document support, evidence must be empty.
This prevents the observed live model tendency to cite all present documents.
The schema does not select the outcome or credit amount. Local strict
JSON/schema/binding checks and the pure critic remain mandatory. Runtime review requirements
or reported native-tool execution also fail validation. `discover()` checks
advertised availability during setup; a listing alone does not prove inference.

Each HTTP request runs in a fresh Python child, using the current interpreter and
project working directory. The parent kills and waits for it at the supplied
wall-clock timeout (maximum/default 180 seconds), covering DNS, connection,
headers and slow bodies. The child also uses a socket timeout. Requests and
responses are bounded to 256 KiB; prompts reserve overhead. Proxies and redirects
are disabled; HTTP is restricted to loopback by the existing URL normalizer.
Authentication, transport, malformed response and timeout failures are sanitized.
There is no automatic retry or deterministic fallback. Killing the client cannot
cancel provider-side computation already accepted, but it cannot execute actions.

`requested_route` records configuration. `response_model` records only a bounded
model label actually returned in the response. A `meterless/*` response is still
a routing label, not evidence of a named responder. Provider identity is unknown
unless independently observed; assistant prose and advertised model lists do not
establish it. No named NVIDIA/Nemotron responder is inferred from `meterless/auto`.

The T08 controller owns total model/tool/duration limits, consumes a model-call allowance on
every attempt, permits at most one correction, reevaluates new facts and validates
the result before the sole action boundary. T07 enforces one call per step and
the correction input contract, but has no persistent run history. Repeating
revision 0 calls cannot be used to reset the controller's budget.

## Verification

From `dispute-demo/`, using Python 3.10+:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_investigator.py -v
DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_nightshift.py -v
```

Investigator tests stub the model and forbid I/O during each turn. Local HTTP
tests start only an ephemeral loopback fixture and exercise the real worker,
headers, authentication errors, no-redirect behavior, size/JSON limits and the
hard deadline. They are **not live Nightshift**; without opt-in those five checks
are skipped. No application dependency or existing environment is modified.

Failures now retain `validation_failure` with a stage, declared field path and
fixed code, for example `$.proposal.recommendation.amount_minor` /
`noncredit_amount_must_be_null`. Known provider refusals also retain a bounded
`provider_error` code. Unknown property names, submitted values, raw response
content, exception prose and private reasoning are never copied into diagnostics.
The controller includes these fields in its existing investigator trace event.
There is no new automatic retry or schema downgrade.

After the documented JDBC preflight and Nightshift setup, this separate probe
uses real Zetaris facts, deterministic policy, a real model call and the critic:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.check_investigator DP-0029 --fresh
```

The [probe](../integration/check_investigator.py) has no fallback, tool-dispatch
loop or writer. It succeeds only for a critic-accepted proposal without unresolved
uncertainties and always prints `persisted: false`. A read request is reported
honestly but does not satisfy this usable-proposal probe. `--fresh` uses the same coherent snapshot adapter as the UI, with a 45-second
read deadline. Omitting it retains the historical null-revision T02 probe.
Both modes are read-only and cannot commit. A read failure is reported as a
sanitized error before any model call. Exact dated results, test counts and
remaining deployment limits are recorded in [ROADMAP.md](../../ROADMAP.md).


## 27 October diagnostic follow-up

[Evidence and attempt history](./evidence/nightshift-schema-followup.json) retain
both successes and failures. The old prompt produced an accepted DP-0029 decline
on the fresh reproduction, so the original T13 field error remains unknown.
The first compact drafts exposed missing/unsupported citations; explicit text
alone did not resolve the extra evidence IDs. Case-bound schema constraints did:
the final DP-0029 proposal passed the unchanged critic without persistence.
Intermediate credit/evidence probes passed; a review probe requested correction
for invented missing requirements. This is not a claim of universal live-model
reliability. The original recording and its transcript remain historical evidence.
