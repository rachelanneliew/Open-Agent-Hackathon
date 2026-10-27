# Submission package

**Synthetic Card-Dispute Resolution Agent** — team **bob the builder**, Track 3:
**Reasoning Architecture**. Prepared on 27 October 2026. All cases, policies and
financial effects are fictional.

This is the checked repository delivery package. **HackOS submission has not
been created or verified.** The signed-in member sees a leader-only submission
screen. Rachel Anne Liew is the platform-designated leader; she must confirm
responsibility and complete the owner steps below. The authenticated deadline
is **27 October 2026 23:45 UTC / 28 October 2026 07:45 SGT**.

## Artifacts

- [Eight-slide editable deck](./dispute-agent-deck.pptx).
- [Narrated MP4 demo](./dispute-agent-demo.mp4), [transcript](./VIDEO.md) and
  [optional captions](./dispute-agent-demo.srt).
- [Reproduce the demo](./DEMO.md): fresh-checkout rehearsal, separately configured
  live UI/CLI, exact source cases, tests and safe recovery.
- [Architecture, technology evidence and provenance](./ARCHITECTURE.md).
- [Package checks](../../dispute-demo/docs/evidence/t13-package-checks.json),
  [fresh-checkout replay](../../dispute-demo/docs/evidence/t13-clean-replay.json),
  [actual live refusal](../../dispute-demo/docs/evidence/t13-live-refusal.json),
  and [same-request recovery](../../dispute-demo/docs/evidence/t13-recovery.json).

The video is an edited walkthrough of actual application captures and dated
evidence slides, not a continuous screen recording. Waiting time is removed.
The DP-0029 input, running state and schema refusal are from one actual live
run. DP-0014 recovery reuses an earlier live commit. All four committed outcomes
and the injected correction are separately labelled isolated scripted-model
rehearsals. Narration uses the installed macOS Samantha synthetic voice. No
participant voice or likeness is imitated. Captions use approximate sentence
timing; the full transcript is authoritative.

Published public URLs (anonymous HTTP 200 and exact-byte matches verified):

| Field | URL |
|---|---|
| Repository | <https://github.com/rachelanneliew/Open-Agent-Hackathon> |
| Package and evidence index | <https://github.com/rachelanneliew/Open-Agent-Hackathon/tree/main/docs/submission> |
| Video download (hosting check still required) | <https://raw.githubusercontent.com/rachelanneliew/Open-Agent-Hackathon/main/docs/submission/dispute-agent-demo.mp4> |
| Deck download | <https://raw.githubusercontent.com/rachelanneliew/Open-Agent-Hackathon/main/docs/submission/dispute-agent-deck.pptx> |

Both binary artifacts return `application/octet-stream`. The MP4 is publicly
downloadable, but the in-app browser blocked inline playback of its raw GitHub
URL. Local playback completed successfully. **B1 therefore includes providing
a verified playable video-host link** for the actual portal. The leader must
upload the same MP4 to an unrestricted video host accepted by the form and
check it signed out. Portal preview, accepted deck formats, upload limits and
final receipt remain **NOT RUN**. No speculative form limits or submission URL
are invented here.

## Prepared project text

**Short description:** A synthetic dispute workbench that turns verified
source evidence and versioned policy into bounded, auditable simulated actions.

**Project description:** An analyst selects a synthetic card dispute. Zetaris
retrieves source facts and the applicable policy. A Nightshift investigator
proposes an outcome, a deterministic critic checks it, and a restricted
PostgreSQL service rechecks the source before atomically recording the decision,
optional credit, audit and review entry. The controller bounds calls and permits
one correction. Exact-request recovery prevents duplicate effects. The pinned
Meterless H-MEM reference stores confirmed summaries and supplies prior cases
only after source verification. The workbench exposes evidence, policy,
critique, persistence and the actual review queue. An isolated rehearsal
reproduces all four outcomes without provider credentials. All effects are
simulated; history remains advisory.

**Sponsor explanation:** Zetaris is the live JDBC data layer. Nightshift is the
primary live model transport. H-MEM provides actual persistent reference
storage/recall with mock embeddings. Live response metadata returned
`nvidia/nemotron-3.5-bolt-e4b`; this is not independent provider attestation or a
claim of award eligibility. Cursor, Codex and Claude Code are development tools.
The [architecture](./ARCHITECTURE.md) links concrete sponsor evidence.

**Distinctive contribution:** A complete source/proposal/critic/transaction
boundary, durable exact-request recovery and independent receipt-verified memory.
The system refuses malformed output and preserves confirmed decisions when
memory fails. No measured business time saving is claimed.

**Earlier-work declaration for owner review:** Reachable Git history begins
24 October 2026, but commit dates alone cannot establish when every contribution
was first authored. The team must confirm product code/data predating
22 October 00:00 UTC and contributor permissions. Provider platforms, the
Meterless reference, onboarding helpers and open-source dependencies are
pre-existing external work and are credited. Do not submit an unqualified
“no earlier work” declaration from Git dates alone.

## Requirement-to-evidence checklist

The source audit and source identifiers are in [competition.md](../competition.md).
“Checked” describes the named artifact/test, not organizer acceptance.

| Requirement | Checked artifact or precise remaining blocker |
|---|---|
| R1 Deadline and submission | Cutoff recorded above from authenticated instructions. **B1:** leader has not created/verified submission or final receipt. |
| R2 Primary Track 3 | README, deck and video use Reasoning Architecture. **B3:** separate detailed challenge page remains unavailable; authenticated summary is verified. |
| R3 Required working technology | Dated T08/T10/T11 live evidence, reference tests and architecture document actual Zetaris/Nightshift/H-MEM use. **B4:** no formal endorsement of the exact reference commit was found. |
| R4 Cursor/NVIDIA | Development tools are separated from runtime. Returned Nemotron model metadata is recorded with its limitation. No award eligibility claim. |
| R5 Workflow video | MP4 and transcript show real UI input/running/refusal and confirmed recovery, plus labelled rehearsal/memory evidence. **B2:** guide's two-agent wording needs clarification for one model plus deterministic critic. |
| R6 Deck | Eight editable slides cover users/problem, solution, workflow, stack, integrations, contribution, actual product capture and future work. Rendered and inspected slide by slide. **B1:** actual form's accepted deck formats remain unavailable. |
| R7 Public repository/setup | Anonymous clone with disabled credential helper succeeded. A separate checkout installed fresh pinned dependencies and passed two replay cycles and offline tests without private configuration. Live licensed-stack bootstrap on a clean machine: **NOT RUN**, prerequisites documented. |
| R8 Technology/provenance | Architecture and linked evidence distinguish real calls, scripted responses, reference/mock memory and development tools. Owner must confirm pre-event contributions and rights before submitting. |
| R9 Project/team fields | Name, descriptions, track and sponsor copy are prepared above. **B1:** leader completes private contact fields and confirms roster before creation locks it. No participant email or phone is published. |
| R10 Video/audio/access | MP4 contains H.264 video and non-silent AAC narration at 1080p within 1–4 minutes; exact checks are in package evidence. **B1:** raw GitHub MP4 is a verified public download; inline playback was blocked, so a playable video-host link and portal visibility need leader verification. |

The new Zetaris scoring guide asks for three datasources and USL demonstrations.
This implementation has **one PostgreSQL datasource and no USL**. Tables and
views are not presented as separate datasources. This scoring gap is explicitly
disclosed and has not been hidden by changing the implemented roadmap scope.

## Owner steps before submitting

1. Sign in as the authorized leader at the
   [Submission Hub](https://hackathon.genai.works/submissions), confirm the roster
   and responsibility, and inspect the actual form before creating a submission.
2. Resolve or explicitly disclose B2/B3/B4 from the requirements audit, the USL
   scoring gap, and the earlier-work/contributor declaration above.
3. Use the prepared project text and public artifact links. Check video sound,
   playback and deck download from a signed-out browser and the actual portal
   preview. If required, upload the same MP4/deck to a permitted unrestricted
   host. Confirm the form's limits rather than assuming them.
4. Review applicable submission terms, complete private participant fields,
   submit before the cutoff and retain the actual confirmation URL/time.
5. Only after that confirmation, record submission completion. No receipt or
   successful upload is claimed by this repository package.
