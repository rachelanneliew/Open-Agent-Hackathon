# T07 Nightshift investigator

[Investigator.step](../app/investigator.py) makes one model call and returns an
immutable `InvestigatorResult`: a typed `AgentProposal`, an unexecuted
`ReadRequest`, or a sanitized failure. It never dispatches a tool, opens a ledger,
calls the action service or saves memory. The [legacy resolver](../agent/resolver.py)
remains a labelled deterministic prototype with a retired writer, not this model
integration. T08 owns its replacement and the complete workflow.

## Interface and trust boundary

Supply the current typed context and canonical policy, application-generated run
and proposal IDs, and revision 0. A revision-1 turn also requires the previous
revision-0 proposal and its exact, freshly recomputed `revise` critique. The new
proposal ID must differ; references and run ID must agree. Forged policy/feedback,
reused identities, a second revision and invalid budgets fail before a model call.

The system message supplies a short evidence checklist and an exact JSON envelope.
The user message contains case facts, evaluated policy, the supported rationale,
allowed reads and optional typed observations. Statements/documents/observations
and prior model text are explicitly untrusted. Customer history is scoped to the
case, customer and cutoff and remains advisory. A changed context must be supplied
with reevaluated policy; observations cannot silently replace it. Runtime code
never reads source CSVs or expected-result fixtures.

Two responses are permitted:

```json
{"kind":"read","request":{"name":"get_dispute_context","dispute_id":"DP-0014"},"uncertainties":[]}
```

or `{"kind":"proposal","proposal":{...complete AgentProposal...},"uncertainties":[]}`.
The model must echo the supplied identities/reference/revision. Four read names
come from the [existing registry](../app/tools.py); its controller must dispatch
`request.name` with `request.arguments()`. No SQL, write, customer, connection,
cutoff or arbitrary arguments are permitted. There is no native tool invocation.

The parser rejects duplicate JSON keys, nonfinite numbers, unknown fields,
markdown wrappers, missing/invalid proposal fields, out-of-scope reads, mismatched
references, refusals, multiple choices, native tool calls and truncated responses.
It does not extract a convenient JSON substring, repair answers, or replace a
model recommendation with the evaluator's answer. The pure critic still checks
amounts, evidence, rules and rationale. `policy_rationale(policy)` is supplied to
meet T06's deliberately bounded explanation vocabulary; broader model prose has
not gained approval. Private response reasoning fields are discarded.

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
completions with the app/scope headers. It does not establish native tools or JSON
schema support for this installed runtime. We therefore send text-only messages,
`stream=false`, `max_tokens=4096` and validate the JSON envelope locally. No
`tools` or `response_format` fields are assumed. Explicit `discover()` checks the
configured route is advertised; the controller should do this before a run.

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

T08 must own total model/tool/duration limits, consume a model-call allowance on
every attempt, permit at most one correction, reevaluate new facts and validate
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

After the documented JDBC preflight and Nightshift setup, this separate probe
uses real Zetaris facts, deterministic policy, a real model call and the critic:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m integration.check_investigator DP-0014
```

The [probe](../integration/check_investigator.py) has no fallback, tool-dispatch
loop or writer. It succeeds only for a critic-accepted proposal without unresolved
uncertainties and always prints `persisted: false`. A read request is reported
honestly but does not satisfy this usable-proposal probe. Current T02 revisions
remain null, so this is read-only evidence. Exact dated results, test counts and
remaining deployment limits are recorded in [ROADMAP.md](../../ROADMAP.md).
