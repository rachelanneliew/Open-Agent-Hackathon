# Synthetic card-dispute resolution: final presentation

10 slides, 3:50. Edited slide presentation with actual recorded application
captures and dated test evidence. All records and financial effects are synthetic.
Samantha is a synthetic female English narrator, generated locally at 145 words
per minute. No participant voice is imitated. No background music.

- [Editable presentation](hackathon-presentation.pptx)
- [Narrated video](hackathon-presentation.mp4)
- [Separate voiceover](voiceover.m4a)
- [Timed captions](captions.srt)

Captions use measured, separately generated sentence audio. The presentation
uses existing recorded evidence; no application integrations or financial actions
were rerun for this media production. The live two-agent case disabled memory.
Memory and credit examples use the labelled isolated rehearsal with scripted
models and the real H-MEM reference with mock embeddings. Native DQ is recorded
live execution against a separate controlled fixture.

## 00:00 — Slide 1: Synthetic card-dispute resolution

**Evidence:** All records and financial effects are synthetic.

We are team bob the builder, presenting synthetic card dispute resolution for Track Three. The workbench helps analysts investigate disputes and record auditable outcomes. All records and financial effects are fictional.

Sources: [ARCHITECTURE.md](../../../docs/submission/ARCHITECTURE.md), [competition.md](../../../docs/competition.md).

## 00:14 — Slide 2: How a decision reaches the database

**Evidence:** Two separate Nightshift roles; deterministic code controls persistence.

Zetaris retrieves source facts. The Investigator proposes an outcome through Nightshift. A code based critic checks policy, amounts and citations. A separate Reviewer challenges the evidence. Both checks must accept the same proposal before the database writer rechecks current facts and commits.

Sources: [workflow.md](../../../dispute-demo/docs/workflow.md), [reviewer.md](../../../dispute-demo/docs/reviewer.md).

## 00:34 — Slide 3: DP-0020: missing refund confirmation

**Evidence:** Recorded live run, 27 Oct 2026. Memory disabled.

Case D P twenty has a captured transaction of one hundred and fourteen Singapore dollars. A merchant promise is present, but the required refund confirmation is missing. In this recorded live run, the Investigator requested evidence and the critic and Reviewer accepted. Two Nightshift calls produced a saved evidence request with no credit effect. Recovery reused the same decision with zero model calls. Memory was disabled for this run.

Sources: [t16-live-accepted.json](../../../dispute-demo/docs/evidence/t16-live-accepted.json), [t16-recovery.json](../../../dispute-demo/docs/evidence/t16-recovery.json), [live-accepted-trace.png](../../../docs/submission/assets/t16/live-accepted-trace.png).

## 01:07 — Slide 4: DP-0014: calculate the remaining amount

**Evidence:** Scripted models, real isolated PostgreSQL. Recorded rehearsal, 27 Oct 2026.

Case D P fourteen makes the arithmetic clear. One hundred Singapore dollars was captured, and the merchant already refunded forty. The remaining amount is sixty dollars, recorded as a separate simulated credit. This rehearsal uses scripted models and a real isolated database. An identical request reuses the original decision. A fresh attempt is rejected, so processing the case again cannot create a second effective credit.

Sources: [t16-isolated-replay.json](../../../dispute-demo/docs/evidence/t16-isolated-replay.json), [test_reliability.py](../../../dispute-demo/tests/test_reliability.py), [settlements.csv](../../../dispute-demo/data/synthetic/settlements.csv).

## 01:37 — Slide 5: DP-0003: reject one extra cent

**Evidence:** Injected fault in an isolated test. Scripted model responses.

For D P three, the allowed credit is two hundred Singapore dollars. The test deliberately proposes two hundred dollars and one cent. The critic rejects the extra cent and allows one correction. The corrected proposal passes the critic and Reviewer before the write. This is an injected test fault, not a spontaneous live model mistake.

Sources: [t16-isolated-replay.json](../../../dispute-demo/docs/evidence/t16-isolated-replay.json), [test_reliability.py](../../../dispute-demo/tests/test_reliability.py), [test_orchestrator.py](../../../dispute-demo/tests/test_orchestrator.py).

## 02:01 — Slide 6: DP-0017: verify remembered history

**Evidence:** Scripted-model rehearsal; real H-MEM reference with mock embeddings.

A later investigation, D P seventeen, recalls the earlier D P fourteen decision through H mem. The workflow verifies the committed receipt and customer ownership against source records. Memory supplies context, while policy determines eligibility. This rehearsal uses the real reference engine with mock embeddings and scripted models. Retrying memory storage never repeats the financial action.

Sources: [t16-isolated-replay.json](../../../dispute-demo/docs/evidence/t16-isolated-replay.json), [test_reliability.py](../../../dispute-demo/tests/test_reliability.py), [memory.md](../../../dispute-demo/docs/memory.md).

## 02:27 — Slide 7: Zetaris joins three independent sources

**Evidence:** Recorded live Zetaris preview, 27 Oct 2026. Read-only enrichment.

The new Unified Semantic Layer joins three independent connectors: PostgreSQL with forty cases, a CSV file with four merchant records, and a REST source with three history records. For D P twenty, the join returns two merchant records and two history records. This optional preview cannot authorize financial actions. Source freshness and a shared cross-source snapshot remain unverified.

Sources: [parity.json](../../../docs/zetaris-usl/evidence/parity.json), [preview-DP-0020.json](../../../docs/zetaris-usl/evidence/preview-DP-0020.json), [sources.md](../../../docs/zetaris-usl/sources.md), [dashboard-preview.png](../../../docs/zetaris-usl/evidence/dashboard-preview.png).

## 02:57 — Slide 8: A quality check catches a broken reference

**Evidence:** Recorded native Zetaris DQ execution on a separate controlled fixture.

This separate quality test contains two records. One references an existing case. The orphan references a nonexistent case. Zetaris detects exactly one invalid record. The result proves that the foreign key check catches broken relationships. It does not prove document truth or source freshness.

Sources: [native-invalid-fixture.txt](../../../docs/zetaris-usl/evidence/native-invalid-fixture.txt), [data-quality.md](../../../docs/zetaris-usl/data-quality.md), [dashboard-dq.png](../../../docs/zetaris-usl/evidence/dashboard-dq.png).

## 03:17 — Slide 9: Test coverage and the current limit

**Evidence:** Recorded 27 Oct 2026. Isolated suite uses scripted model responses.

The latest recorded suite passed three hundred and twenty eight application tests and sixteen reference checks, with no failures or skips. Rehearsals cover all four outcomes shown here. Real models still vary: the Reviewer appeared overly conservative on D P twenty nine and stopped without writing.

Sources: [regression.json](../../../docs/zetaris-usl/evidence/regression.json), [t16-isolated-replay.json](../../../dispute-demo/docs/evidence/t16-isolated-replay.json), [t16-live-refusal.json](../../../dispute-demo/docs/evidence/t16-live-refusal.json).

## 03:36 — Slide 10: Evidence-backed decisions, controlled actions

**Evidence:** bob the builder / Track 3: Reasoning Architecture.

The contribution combines observable agent collaboration, duplicate prevention, verified memory and inspectable source quality. Next steps are broader document support and source freshness metadata.

Sources: [ARCHITECTURE.md](../../../docs/submission/ARCHITECTURE.md), [USL_ADDENDUM.md](../../../docs/submission/USL_ADDENDUM.md).

## Evidence limits

The 328 application and 16 reference checks are the recorded 27 October result,
not a new run or an accuracy benchmark. The 30 dedicated USL tests are already
part of the application suite and are not added again. The real DP-0029 Reviewer
objection appears overly conservative about policy precedence; no successful
decline or saved review is claimed for that live run. USL preview data cannot
authorize financial actions, and cross-source freshness/atomicity is unverified.
The package does not claim production readiness, organizer acceptance or a
HackOS submission receipt.
