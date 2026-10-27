# Submission package

**Synthetic Card-Dispute Resolution Agent** — team **bob the builder**, Track 3:
**Reasoning Architecture**. T16 refresh, 27 October 2026. All cases, policies and
financial effects are fictional.

**HackOS submission has not been created or verified by this task.** The last
authenticated check showed leader-only access. Rachel Anne Liew is the designated
leader. The recorded deadline is **27 October 2026 23:45 UTC / 28 October 07:45
SGT**; this task did not recheck the portal or obtain a receipt.

## Current two-agent package

- [Eight-slide editable deck](./dispute-two-agent-deck.pptx).
- [Narrated demo](./dispute-two-agent-demo.mp4), [transcript](./VIDEO_TWO_AGENT.md)
  and [captions](./dispute-two-agent-demo.srt).
- [Reproduction guide](./DEMO.md) and [architecture](./ARCHITECTURE.md).
- [Real accepted workflow](../../dispute-demo/docs/evidence/t16-live-accepted.json):
  DP-0020, two independent Nightshift calls, accepted missing-evidence request,
  committed decision and audit, no credit effect.
- [Real feedback/refusal](../../dispute-demo/docs/evidence/t16-live-refusal.json):
  DP-0029, Reviewer objection, one Investigator revision, second objection,
  four calls and no write. The objection appears overly conservative about
  first-terminal policy ordering; it is not presented as a policy defect.
- [Request reconstruction](../../dispute-demo/docs/evidence/t16-request-reconstruction.json):
  both role prompts, schemas and exact accepted inputs, reconstructed from the
  private saved request and current builders. This is **not a raw HTTP capture**.
- [Exact recovery](../../dispute-demo/docs/evidence/t16-recovery.json),
  [314 passing integration tests](../../dispute-demo/docs/evidence/t16-verification.json),
  [labelled scripted replay](../../dispute-demo/docs/evidence/t16-isolated-replay.json),
  [fresh-clone replay](../../dispute-demo/docs/evidence/t16-clean-replay.json) and
  [package checks](../../dispute-demo/docs/evidence/t16-package-checks.json).

The video uses actual UI captures and evidence slides, with wait time removed.
It is not continuous screen recording. The successful scripted correction is
explicitly separate from both real runs. Narration uses the installed macOS
Samantha synthetic voice, without imitating a participant. Captions use
approximate sentence timing. Live T16 runs used no-memory mode; real isolated
reference tests verify combined two-agent memory behavior. Earlier live memory
acceptance remains separately dated.

Current source and artifacts are published on **`main`**. Public download checks are
recorded in the package evidence; a GitHub download is not verified portal
playback or a final submission.

| Field | Main branch URL |
|---|---|
| Repository | [Public source](https://github.com/rachelanneliew/Open-Agent-Hackathon) |
| Current package | [Two-agent package](https://github.com/rachelanneliew/Open-Agent-Hackathon/tree/main/docs/submission) |
| Video download | [Current MP4](https://raw.githubusercontent.com/rachelanneliew/Open-Agent-Hackathon/refs/heads/main/docs/submission/dispute-two-agent-demo.mp4) |
| Deck download | [Current PPTX](https://raw.githubusercontent.com/rachelanneliew/Open-Agent-Hackathon/refs/heads/main/docs/submission/dispute-two-agent-deck.pptx) |

## Historical fallback

The original [one-agent deck](./dispute-agent-deck.pptx),
[3:46 video](./dispute-agent-demo.mp4), [transcript](./VIDEO.md),
[captions](./dispute-agent-demo.srt) and
[T13 checks](../../dispute-demo/docs/evidence/t13-package-checks.json) are preserved
unchanged. They do not depict the new Reviewer runtime.

## Prepared project text

**Short description:** Two separately invoked agents connect verified dispute
evidence and versioned policy to bounded, auditable simulated actions.

**Project description:** An analyst selects a synthetic dispute. Zetaris supplies
fresh facts and applicable policy. A Nightshift Investigator proposes an outcome,
a deterministic critic checks it, and a separate Nightshift Reviewer challenges
the evidence. The controller permits one shared correction and requires both
checks to accept the final proposal. A restricted PostgreSQL writer rechecks the
source and records the decision, optional credit, audit and review entry
atomically. Exact-request recovery prevents duplicate effects. Source-verified
H-MEM supplies advisory context and stores confirmed summaries. The workbench
shows each role, correction and actual persistence. Isolated scripted rehearsals
reproduce all four outcomes without private credentials.

**Sponsor explanation:** Zetaris is the live JDBC data layer. Nightshift invokes
both model roles independently. H-MEM uses the pinned official reference with
mock embeddings. Both live roles returned `nvidia/nemotron-3.5-bolt-e4b` metadata;
this is not independent provider attestation or an award eligibility claim.
Codex, Cursor and Claude Code are development tools.

**Contribution:** Observable model-to-model feedback inside mandatory policy and
transaction checks, durable exact recovery and receipt-verified memory. No
measured business time savings or model accuracy improvement is claimed.

**Earlier-work declaration:** Reachable Git history starts 24 October 2026, but
commit dates do not prove when every contribution was authored. The team must
confirm work predating 22 October 00:00 UTC and contributor rights. External
platforms, the Meterless reference, onboarding helpers and dependencies are
pre-existing work, credited in the architecture.

## Requirement and owner checks

See [competition.md](../competition.md) for the dated source audit.

| Requirement | Evidence or remaining limit |
|---|---|
| Distinct collaborating agents | Real separate Investigator/Reviewer calls, correction trace and acceptance. The deterministic critic remains code. Organizer acceptance is unverified. |
| Working integrations | Dated live Zetaris/Nightshift plus prior live H-MEM evidence; current combined reference tests. Exact reference endorsement remains unverified. |
| Reproducibility | Fresh clone of runtime commit, independent dependencies, no private config, two replay cycles and both offline test roots passed. Clean-machine licensed live bootstrap NOT RUN. |
| Video and deck | Current narrated MP4, captions and eight editable slides; historical fallback preserved. Media checks are in package evidence. Native PowerPoint and human listening review NOT RUN. |
| Public access | Branch source and downloads checked separately. Leader must provide an accepted unrestricted playable video-host link and inspect portal preview. |
| Submission | Leader-only form access, accepted formats/limits, roster, terms and final receipt remain owner checks. No submission claimed. |
| Scoring scope | **One PostgreSQL datasource and no USL.** Multiple tables are not multiple datasources. A second agent does not close this scoring gap. |
| Track and provenance | Detailed Track 3 page access, exact reference endorsement and contributor declarations retain the dated audit limitations. |

The leader should inspect the [Submission Hub](https://hackathon.genai.works/submissions),
confirm roster and declarations, verify unrestricted video playback and deck
format, review the prepared fields and submit within the applicable deadline.
Record completion only from an actual confirmation URL and time. Do not treat
this checked repository package or Jira completion as a submission receipt.
