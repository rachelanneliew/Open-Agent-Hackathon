# Submission package

**Synthetic Card-Dispute Resolution Agent** — team **bob the builder**, Track 3:
**Reasoning Architecture**. Final presentation refresh, 27 October 2026. All cases, policies and
financial effects are fictional.

**HackOS submission has not been created or verified by this task.** The last
authenticated check showed leader-only access. Rachel Anne Liew is the designated
leader. The recorded deadline is **27 October 2026 23:45 UTC / 28 October 07:45
SGT**; this task did not recheck the portal or obtain a receipt.

## Current presentation package

The new ten-slide edition explains the live DP-0020 evidence request, the
isolated credit/retry and one-cent fault tests, verified memory, and the
three-source Zetaris USL preview with its controlled native DQ fixture.

- [Editable ten-slide PowerPoint](./final-presentation/hackathon-presentation.pptx).
- [3:50 narrated presentation video](./final-presentation/hackathon-presentation.mp4).
- [Separate Samantha voiceover](./final-presentation/voiceover.m4a).
- [Slide-by-slide transcript and evidence sources](./final-presentation/TRANSCRIPT.md).
- [Captions timed from measured sentence audio](./final-presentation/captions.srt).
- [Production verification and final file hashes](../../dispute-demo/docs/evidence/final-presentation-checks.json).

This is an edited slide presentation using actual recorded application captures,
not a new live investigation or continuous screen recording. Each example
identifies recorded live evidence, scripted-model rehearsal or injected fault.
The recorded 328 application plus 16 reference passes are dated evidence, not
tests rerun during media production. The dedicated 30 USL tests are not added
again. Source freshness and cross-source atomicity remain unverified, and the
USL preview has no action authority.

Use this directory's final presentation package for the current edition.
Repository publication does not establish video-host or portal playback acceptance.
The two superseded presentation editions were removed from this checkout at
the owner's request. Their PowerPoints, videos, transcripts and captions remain
recoverable from Git history. Recorded implementation evidence is retained.

## Recorded implementation evidence

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

Live T16 runs used no-memory mode; real isolated
reference tests verify combined two-agent memory behavior. Earlier live memory
acceptance remains separately dated.

Historical public download checks remain recorded in the package evidence;
they do not verify publication or portal playback of the new final presentation.

| Field | Main branch URL |
|---|---|
| Repository | [Public source](https://github.com/rachelanneliew/Open-Agent-Hackathon) |
| Published package | [Submission directory](https://github.com/rachelanneliew/Open-Agent-Hackathon/tree/main/docs/submission) |

## Additional evidence

The separately dated [USL addendum](USL_ADDENDUM.md) adds a real three-source
Zetaris semantic model and native DQ evidence with an optional read-only panel.
It was developed on `codex/zetaris-usl` and is covered by the subsequent
PR-and-merge authorization. It is separate from T16 media and is not a new
portal submission.

The [T13 checks](../../dispute-demo/docs/evidence/t13-package-checks.json)
remain as dated verification of the retired one-agent presentation.

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
| Video and deck | New 3:50 narrated MP4, measured captions and ten editable slides, including USL and concrete test examples. Native PowerPoint and human listening review NOT RUN. |
| Public access | Branch source and downloads checked separately. Leader must provide an accepted unrestricted playable video-host link and inspect portal preview. |
| Submission | Leader-only form access, accepted formats/limits, roster, terms and final receipt remain owner checks. No submission claimed. |
| Scoring scope | The new presentation includes PostgreSQL + CSV + REST, actual USL preview and native DQ from the [U00–U06 addendum](USL_ADDENDUM.md). Sponsor scoring remains unverified. |
| Track and provenance | Detailed Track 3 page access, exact reference endorsement and contributor declarations retain the dated audit limitations. |

The leader should inspect the [Submission Hub](https://hackathon.genai.works/submissions),
confirm roster and declarations, verify unrestricted video playback and deck
format, review the prepared fields and submit within the applicable deadline.
Record completion only from an actual confirmation URL and time. Do not treat
this checked repository package or Jira completion as a submission receipt.
