# Independent Evidence & Risk Reviewer

`app/reviewer.py` makes a separate Nightshift completion with a distinct system
prompt. It challenges source support, contradictions and omissions after the
pure Python critic accepts a proposal. It has no read dispatch, action or memory
write interface, and cannot change policy.

The strict model contract is `ReviewerFeedback`: `accept | revise | escalate`,
predefined issue codes, current visible evidence IDs, evaluated rule IDs,
1–500 characters of feedback and at most eight 240-character uncertainties.
Acceptance requires no issues or uncertainties. Objections require an issue code.
Unknown fields (including model-supplied identities/actions) fail closed.
The application attaches run/proposal IDs, exact ContextRef, attempt, requested
route and observed response-model metadata in `ReviewerResult`. Every downstream
boundary must revalidate the binding and citation scope with `validate_review`.
A typed review is evidence from a trusted application dependency, not a signature
or proof of semantic truth. Feedback remains untrusted correction material.

The existing Nightshift structured transport is reused unchanged, including its
historical `dispute_investigator` schema request name. Role identity comes from
the separate invocation and prompt, not that transport label. Runtime schema
validation does not establish provider-side enforcement or responder attestation.
Timeouts, refusals, malformed responses, native tools and runtime-review flags
fail closed with fixed diagnostics. Raw responses and private reasoning are not
logged. No retry or permissive fallback is supplied by this module.

T14 verification is offline model-stub evidence only. Live Reviewer inference:
**NOT RUN** at T14 acceptance. T15 owns controller routing and the shared correction
budget; T16 owns separately recorded live evidence and updated media.

```sh
cd dispute-demo
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p 'test_reviewer*.py' -v
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.verify
```

## T16 live evidence

Separate real calls are now verified: [DP-0020 accepted](./evidence/t16-live-accepted.json)
committed a missing-evidence request after two calls. [DP-0029](./evidence/t16-live-refusal.json)
used four calls: Reviewer revise, Investigator revision, Reviewer revise, no
action. Both roles returned `nvidia/nemotron-3.5-bolt-e4b` via `meterless/auto`.
These are metadata labels, not independent provider attestation. The second
objection appears inconsistent with first-terminal policy ordering; this is a
known conservative-refusal limitation, not authority to change policy or bypass
the Reviewer. Exact-request recovery used zero calls. Live runs disabled memory;
combined memory behavior is covered by the real isolated reference suite.
