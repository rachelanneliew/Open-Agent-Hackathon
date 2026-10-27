# HackOS requirements and delivery checklist — A01

Verified **27 October 2026, 07:08–07:19 UTC** (15:08–15:19 Singapore).
This is a requirements audit, not a submission receipt or a certification of
competition eligibility. The owner signed in during the audit. Authenticated
resources were read through the browser; no form, upload, team change or message
was submitted. No credentials are recorded here.

## Sources and authority

| Ref | Source actually opened | Relevant sections / observation |
|---|---|---|
| S1 | [Official event rules](https://hackathon.genai.works/event/open-agent-hackathon-2026) | Expanded sections 1–10; dates and Track 3. Public, current page. |
| S2 | [Submission Requirements](https://hackathon.genai.works/resources?id=01a08ff1-54c3-70c5-b262-31e75dfd1e60) | Authenticated; resource catalog says updated Oct 24. Sections 1–6 and final checklist. |
| S3 | [Submission Form Preview](https://hackathon.genai.works/resources?id=01a08ff1-55f6-7358-9501-cb7f1883e33c) | Authenticated preparation worksheet, **not** the actual form. |
| S4 | [Technical Execution Guide](https://hackathon.genai.works/resources?id=01a08ff1-54b1-7670-9441-a1e73ff43a6e) | Authenticated; explicitly recommendations unless the official rules require them. |
| S5 | [Meterless H MEM Agent Engine](https://hackathon.genai.works/resources?id=01a08ff1-56e0-74ed-825d-daaad9e9f534) | Authenticated version 1.0, especially sections 2, 9, 13, 18 and reference addendum. |
| S6 | [Hackathon Overview](https://hackathon.genai.works/resources?id=01a08ff1-548e-7082-b07e-b00afa88f7a6) | Authenticated Track 3 statement and current stack summary. |
| S7 | [Demo Video Guide](https://hackathon.genai.works/resources?id=01a08ff1-562f-733f-9ae0-baf2c7ac152b) | Authenticated sections 1–7, including roles, real runs, audio and access. |
| S8 | [Zetaris Scoring Methodology](https://hackathon.genai.works/resources?id=01a1792b-4f7a-7d5b-950a-26795458551c) | Catalog labels new Oct 27. One-page PDF visually inspected, enlarged to read both columns. Publisher says it will apply flexibility. |
| S9 | [Submission Hub](https://hackathon.genai.works/submissions) and [team page](https://hackathon.genai.works/team/019fd164-82b9-7382-a536-d9093c576ed2/01a15e99-3844-7dee-93ee-a22e9792014e) | Signed-in member session; no submission exists; creation/management restricted to leader. |

S2/S3/S4/S7 defer to S1 when inconsistent. The local
[22 October handbook](../Open_Agent_Hackathon_2026_Complete_Handbook.md) is retained
as historical guidance, including its superseded mandatory-Cursor language.
Resource links may require a participant login.

## Confirmed requirements for T13

| ID | Requirement | Source | Project delivery work |
|---|---|---|---|
| R1 | Submit by **2026-10-27 23:45 UTC**, equivalent to **2026-10-28 07:45 SGT**. | S1 dates; S2 §1; signed-in dashboard | Leader verifies final receipt before cutoff. |
| R2 | Choose one primary track. Track 3 concerns reliable decisions/actions informed by data, knowledge and memory. | S1 tracks; S6 §6 | Keep README, deck and video consistently labelled Reasoning Architecture. |
| R3 | Working Zetaris data layer, at least one functioning Meterless engine, and Nightshift as primary model provider. H-MEM is an allowed engine. | S2 §4 | Explain actual JDBC, memory and model paths with separate evidence. |
| R4 | Cursor is optional. NVIDIA is used where relevant; the Nemotron award additionally needs an actual Nemotron-powered feature through Nightshift and model evidence. | S1 §5; S2 §4 | Separate development tools from runtime and returned model labels from attestation. |
| R5 | Video: 1–4 minutes, real workflow, challenge fit, useful features and sponsor calls. | S2 §3.1 | Record actual input/output; identify edited waits and scripted segments. |
| R6 | Deck: users/problem, solution, workflow, stack, integrations, distinctive contribution, product visuals, future work. | S2 §3.2 | Prepare a checked deck covering all eight topics. |
| R7 | Public GitHub source repository; README explains installation, operation and dependencies. | S2 §3.3 | Verify anonymous access and clean-checkout instructions. |
| R8 | Explain sponsor contributions and engine tests; declare earlier product code/data. | S2 §§3.4–5 | Add provenance and technology evidence; never imply integration from a dependency alone. |
| R9 | Supply name, description, track and team/contact details; confirm roster before creation locks it. | S3 §§1–3 | Prepare non-sensitive project text; owner completes private participant fields. |
| R10 | Video audio is required by the guide; MP4/1080p preferred. Shared links must play without access requests. | S7 §7 | Check duration, audio, legibility, playback and hosting permissions. |

The exact S1 §5.1 clarification is: “Every submission must integrate Zetaris and
Meterless. Using Cursor for development is optional.” No replacement editor is
required. S3 still contains a Cursor-built checkbox; S1 and the updated S2
explicitly settle that discrepancy. The authenticated dashboard and S1 report
judging opening on Oct 27; S2/S3/S6 retain Oct 28 wording. This does not change
their matching submission cutoff. No inferred build-window date is used.

## Architecture and memory assessment

S5 permits policy/supervisor-controlled memory approval and treats mandatory
human UI interaction as outside its headless scope. Section 13 recommends
starting with storage and retrieval, adding dreaming/sleep after retrieval
works. Its addendum directs participants to Meterless's source/reference
implementations. These findings support this project's headless advisory
storage/retrieval choice; they do not certify a particular commit or every
optional engine feature.

The project uses the actual official reference pinned at
`1742dec56a66e58eef9dda2d2b865823758ca8cd`, with deterministic **mock embeddings**.
[Memory evidence](../dispute-demo/docs/evidence/t10-verified-memory.json) records
later-case source verification and new-process reuse; [the memory guide](../dispute-demo/docs/memory.md)
lists the omitted dreaming/sleep/conflict workflows. No source inspected
requires a numeric repeated-claim policy or blanket human approval of every
synthetic financial outcome. The owner's approved advisory MVP scope remains.

S7 §4 asks for “At least two agents with clear roles.” S6 also emphasizes
interacting roles and warns against dressing up a single prompt as a system.
T16 now demonstrates **two separately invoked Nightshift roles**, Investigator
and Evidence & Risk Reviewer, with distinct prompts and observable feedback.
The Python critic remains deterministic. [Actual acceptance](../dispute-demo/docs/evidence/t16-live-accepted.json)
and [actual correction/refusal](../dispute-demo/docs/evidence/t16-live-refusal.json)
show separate calls; using the same returned model does not make them distinct
model providers. The earlier one-model implementation gap is addressed. No
organizer ruling, waiver or formal compliance approval is claimed.

S4 recommends a programmatic entry point, bounded runs, documented setup,
observable traces, three example pairs and an offline fallback. The project
already exposes a CLI and explicit isolated scripted rehearsal; it has no
`SAMPLE_MODE` environment switch. Keep that distinction and avoid a silent live
fallback. A Dockerized application or new public service is not established as
a mandatory format by the inspected rules.

## New sponsor scoring gap

S8 outlines a Unified Semantic Layer demonstration using at least three data
sources, exploratory queries per source, a USL definition, queries over it and
a data-quality rule. It also asks for reflections on development time saved,
other useful applications and a proposed USL improvement; comparisons and
examples can earn additional credit. This is sponsor scoring guidance with an
explicit flexibility note, not evidence that this repository implements it.

The current integration uses one PostgreSQL datasource through Zetaris with
multiple tables/read views. A table is not another datasource. No USL or
three-source federation has been implemented or verified. T13 must state this
scoring limitation. Any expansion would need a separate scoped implementation;
do not relabel the existing bundle view as a USL or claim full sponsor marks.

## Owner, access and precise remaining blockers

| ID | Verified gap | Resolution owner / next evidence |
|---|---|---|
| B1 | S9 exposes no editable form to this member. Rachel Anne Liew is shown as team leader for **bob the builder**. Submission is not started. | Platform-designated submission owner: Rachel. Team should confirm she will submit; no Jira reassignment or message was sent. Leader checks actual form fields, upload limits, accepted deck format, hosting and final receipt. |
| B2 | T16 closes the one-model implementation gap with distinct live Investigator/Reviewer calls and feedback. | Owner presents the dated evidence; organizer acceptance remains unverified. The deterministic critic is not counted as a language model. |
| B3 | S6 mentions individual challenge pages. The active event link from authenticated Hackathons redirected to Dashboard; resources offered a Track 3 summary but no separate detailed challenge control. | Leader supplies the exact detailed Track 3 URL if one exists; check extra constraints before submission. Summary access is verified, exhaustive challenge-page access is not. |
| B4 | No explicit approval names this exact H-MEM reference revision. H-MEM is permitted, source references are endorsed, and storage/retrieval minimum is supported by S5. | Preserve source pin, passing tests and feature evidence; seek clarification only if a stricter version requirement is surfaced. Do not claim formal approval of the commit. |

Private access required: the leader's own HackOS session, final participant/contact
details, and a hosting account for accessible video/deck links if the form uses
links. Runtime demonstrations separately need privately configured Zetaris,
Nightshift and the restricted action database. Do not copy tokens, passwords,
participant email addresses or private recovery journals into this checklist.

No application scope was changed during A01. T13 can proceed with the now
confirmed video/deck/repository requirements and must carry these open items
into its delivery checklist. A01's gate explicitly permits precise verification
blockers; **completion of this audit does not mean the project is submitted**.

## Case/evidence handover

The [T12 rehearsal evidence](../dispute-demo/docs/evidence/t12-isolated-replay.json)
identifies DP-0014 credit/reuse, DP-0020 evidence request, DP-0029 decline,
DP-0008 review, DP-0017 verified prior history, DP-0003 injected correction and
DP-0033/DP-0034 policy versions. These are scripted-model/isolated-database
checks. The [T08](../dispute-demo/docs/evidence/t08-live-workflow.json),
[T10](../dispute-demo/docs/evidence/t10-verified-memory.json) and
[T11](../dispute-demo/docs/evidence/t11-analyst.json) receipts separately establish
dated live Zetaris/Nightshift behavior. T13 must inspect each before selecting
recording shots, and retain all mode labels and live refusals.

A01 verification is browser/source/document inspection only. Application tests,
fresh live model/database runs, final upload and submission: **NOT RUN**.
