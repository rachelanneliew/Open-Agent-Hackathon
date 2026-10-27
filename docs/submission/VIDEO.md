# Demo video transcript

The [MP4](./dispute-agent-demo.mp4) is an edited walkthrough of actual UI captures and dated evidence slides. Duration: approximately **3:46**, 1920×1080 at 30 fps, H.264 with AAC audio. Narration uses the installed macOS Samantha synthetic voice. No speaker identity is claimed. Waits between captured states are removed; this is not continuous screen recording.

The recording shows the real DP-0029 schema failure, the earlier DP-0014 live receipt recovered during T13, and separately labelled scripted rehearsal evidence. All records and effects are synthetic. See the [source/evidence index](./README.md) and [captions](./dispute-agent-demo.srt). Captions have approximate sentence timing.

**Later engineering update (27 October 2026; not part of the narration):**
The investigator now uses a compact draft, a full JSON Schema and safe validation
diagnostics. A fresh read-only DP-0029 proposal passed the critic after those
changes. The original malformed field remains unknown; this video accurately
preserves the earlier run. See the [follow-up evidence](../../dispute-demo/docs/evidence/nightshift-schema-followup.json)
and [current investigator contract](../../dispute-demo/docs/investigator.md).

## 00:00 — Synthetic card-dispute resolution

This is the synthetic card dispute workbench from team bob the builder, for Track Three, Reasoning Architecture. It connects source evidence to policy, a model proposal, independent validation, and an auditable simulated decision. This edited walkthrough uses real application captures and dated test evidence. All records and financial effects are fictional.

## 00:21 — A bounded workflow

Zetaris supplies fresh facts and policy. One investigator uses Nightshift to propose a structured outcome. A deterministic critic checks that proposal. The controller permits at most one correction. Before any action, the restricted PostgreSQL service rechecks the source and commits the decision, effect, audit, and any review entry atomically. Confirmed results can then enter memory.

## 00:45 — The same request returns the same credit

Here is an actual live recovery of case D P fourteen. Its original source snapshot contains a hundred dollar capture and a forty dollar merchant refund. The accepted result is a sixty Singapore dollar simulated credit. Recovery returns the same saved decision and credit identifiers, with zero model calls. The interface separates the proposal's critic verdict from the persistence result. Repeated recovery does not create another effective credit.

## 01:12 — A new live investigation

Next, we select case D P twenty nine and start a new live investigation. Its claim is one hundred and thirty Singapore dollars. The application reads the case through Zetaris and selects policy version one from the opening time.

## 01:25 — The controller is working

The workbench shows the investigation in progress. The source policy places this case outside its thirty day filing window. A valid decline still needs a correctly structured proposal and a confirmed commit. The running screen reports no financial effect.

## 01:40 — Invalid output stops safely

In this actual run, Nightshift returned an invalid proposal schema. The application stopped before critique or persistence. No decision or credit was created. A model failure does not invent a human review entry. This recording preserves that failure. The repository separately contains successful isolated decline evidence, clearly labelled as a scripted model rehearsal.

## 02:03 — Memory retains source references

The earlier live memory demonstration links D P fourteen to a later investigation of D P seventeen for the same synthetic customer. H MEM recalls a candidate, and Zetaris verifies the original committed receipt before the investigator sees it. The later case received a fifty seven dollar sixty cent simulated credit under policy. Memory is advisory and partial. The pinned reference uses mock embeddings, and memory retries cannot execute an action.

## 02:30 — All four outcomes and recovery

A fresh public checkout reproduced two isolated rehearsal cycles. Each produced eight decisions, four credits, and one review. The cases cover all four outcomes, duplicate prevention, one injected amount correction, and the policy version boundary. These runs use real disposable PostgreSQL and the pinned H MEM reference, with scripted model responses. They do not call live Zetaris or Nightshift.

## 02:55 — Working integrations and evidence

The repository includes dated live sponsor evidence and two hundred and sixty seven main tests plus sixteen reference checks that passed in the full verification matrix. Nightshift response metadata reported the Nemotron model shown here. That label is recorded evidence, not independent provider attestation. Setup instructions include a clean checkout route and a separately configured live route.

## 03:18 — Current limits and next work

This is a local reference demo using synthetic documents. It currently has one PostgreSQL datasource, no universal semantic layer, and one model investigator with a deterministic critic. Broader evidence handling and production controls remain future work. The public submission package includes the deck, video, transcript, architecture, and evidence. The team leader still needs to verify portal requirements and complete the final submission.

## Production and verification

Eight evidence slides were authored as editable native PowerPoint content with the first-party artifact tool. Actual workbench screenshots were captured through the in-app browser on 27 October 2026 and are preserved in `assets/`. The four UI video frames place those unaltered captures beside explanatory text. macOS `say -v Samantha -r 165` rendered narration, and FFmpeg 7.1 encoded H.264/AAC segments and concatenated them with faststart metadata. No image or model-generated UI was substituted for the product.

Full decoding, dimensions, duration and audio levels are recorded in [package checks](../../dispute-demo/docs/evidence/t13-package-checks.json). Native PowerPoint execution and a human audio listening review are not claimed. The leader should perform the final audiovisual and portal review before submitting.
