# Optional Zetaris segment — fresh evidence, 27 October 2026

This addendum accompanies the preserved T16 two-agent video/deck. Neither
historical recording contains this extension. It is a CLI/dashboard walkthrough,
not a claim that a new narrated video has been produced or submitted.

## Demonstration script

1. Show the [three registered sources](../zetaris-usl/sources.md): existing
   PostgreSQL, actual CSV FileStore and a fixed REST fixture on independent
   storage/connectors. All are synthetic and local.
2. Show the intact COMPILE and three ACTIVATE statements, then the stored
   live [definition and parity result](../zetaris-usl/evidence/parity.json).
   The raw and USL row sets match: 40 cases, four merchant records and three
   history records. DP-0020 joins to 11400 minor units, two distinct merchant
   records and two distinct history records.
3. Show [native DQ](../zetaris-usl/data-quality.md): all five main PK/FK checks
   pass. The separate two-row fixture has one valid and one invalid FK;
   Zetaris identifies `DQ-ORPHAN → DP-9999`. This is actual native execution.
4. Open the optional dashboard preview for DP-0020, or run
   `.venv/bin/python -m integration.usl_reads DP-0020 --enable` from
   `dispute-demo/`. Show record provenance, historical timestamps, versions,
   unknown activation/model revisions and the dated DQ receipt. Usable data
   remains labelled unverified for freshness/atomicity.
5. Explain that the USL preview cannot authorize a financial action. The accepted
   Investigator/Reviewer/critic/writer workflow still uses its original coherent
   PostgreSQL reads. No new live decision was created for this demonstration.

## Sponsor comparison

| Existing JDBC decision path | New actual USL inspection |
|---|---|
| Several tables from one PostgreSQL datasource | Three separate PostgreSQL/FileStore/REST connectors |
| Application-specific coherent bundle and revision checks | Compiled typed semantic entities with PK/FK relationships |
| Python policy/critic and transactional writer enforce action correctness | Native key DQ plus separately labelled application ownership/parity diagnostics |
| Source revision supports protected reread before a commit | Cross-source atomicity, activation timestamp and monotonic revision are unverified |

Query latency, developer time saved, business savings and accuracy improvement
were **not measured**. These are different workloads; the live read timeouts
are an operational observation, not a benchmark. Genuine USL gives the analyst
one semantic model across heterogeneous sources and an inspectable key-quality
surface. It does not replace policy, freshness checks or settlement verification.

Potential further applications include support evidence triage, inventory
reconciliation and cross-system incident analysis, each requiring separate
domain policy and source-freshness design. A proposed improvement is a structured
USL metadata response carrying activation time, immutable definition revision,
source observation times and DQ execution IDs/times. These capabilities are not
claimed to exist in the inspected response.

## Submission status

The [official public event page](https://hackathon.genai.works/event/open-agent-hackathon-2026)
was rechecked on 27 October: submission deadline remains 23:45 UTC, Track 3 is
Reasoning Architecture, and sponsor technology is part of judging. Authenticated
form limits, leader access, declarations, accepted video hosting and final
receipt still require the submission owner's check. No terms were accepted,
files uploaded, Jira issues changed or portal submission created here.
See the dated [competition audit](../competition.md) and the
[acceptance evidence](../zetaris-usl/demo-evidence.md). This extension supplies
three-source/USL evidence; organizer scoring and acceptance remain unverified.
