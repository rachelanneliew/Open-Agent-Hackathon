# U00–U06 acceptance evidence

Dated 27 October 2026; baseline `232945a1015381561785f092cbe95bba917429d7`,
work branch `codex/zetaris-usl`. User requested all seven tasks. No task was
accepted merely because a SQL file or roadmap checkbox existed.

| Task | Evidence category | Acceptance evidence |
|---|---|---|
| U00 | Live Zetaris | [Preflight](preflight.md): 2.4.3.1, inspected schemas/inventory, genuine smoke COMPILE/ACTIVATE, 40 rows |
| U01 | Live Zetaris | [Sources](sources.md): unchanged PostgreSQL, actual FileStore CSV and REST registrations, separately queried 40/4/3 rows |
| U02 | Live Zetaris | [Parity receipt](evidence/parity.json): actual loaded definition, three activation queries, exact raw/USL parity, ownership and DP-0020 join `[DP-0020,11400,2,2]` |
| U03 | Live Zetaris | [DQ receipt](../../dispute-demo/integration/usl/dq_receipt.json), [native PK output](evidence/native-primary-keys.txt), [invalid-fixture output](evidence/native-invalid-fixture.txt): all main keys pass, separate orphan detected |
| U04 | Live Zetaris + isolated tests | [Final adapter output](evidence/preview-DP-0020.json), four actual SELECTs, bounded case/customer checks, disabled default and no writer dependency |
| U05 | Local browser + isolated HTTP | Optional provenance panel, independent case-ID input, visible unverified/unavailable states, dated DQ receipt; no investigation needed |
| U06 | Isolated full regression + read-only live checks | [344-test report](evidence/regression.json), [30 dedicated tests](evidence/dedicated-tests.json), equal [before](evidence/database-before.txt)/[after](evidence/database-after.txt) source/financial state |

## Commands and results

From `getting-started/`, `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python
scripts/preflight.py --jdbc`: JDBC, driver and SELECT passed; overall exit 1
only for the absent REST-client API key. Initial sandbox socket denial was
resolved with approved network access. No credentials were changed.

`scripts/run_sql.py --dry-run <file>` and the corresponding `--channel jdbc
<file>` were used for provisioning and DQ. Files under
`dispute-demo/integration/usl/sql/`: smoke five statements; source registration;
independent source verification; main COMPILE one intact statement; three
activations; two main FK runs with invalid-row inspection; three primary-key
runs; separate quality fixture seven statements. Native output and query
receipts are linked above. A registration/inventory read overlap briefly
returned an empty inventory; a subsequent read confirmed actual connector
registrations (CSV table id 919, REST table id 936).

From `dispute-demo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.usl.verify_live
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m integration.usl_reads DP-0020 --enable
HMEM_NODE=/Users/joellui/.nvm/versions/node/v24.13.0/bin/node PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m demo.verify --integrations
DISPUTE_UI_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p test_usl_reads.py -v
```

All passed. Full matrix: **328 main + 16 reference, zero skips/failures/errors**.
Dedicated suite: **30 passed**, rerun after the independent panel change.
The full verifier uses disposable PostgreSQL, isolated H-MEM and scripted
model responses; its live Zetaris/Nightshift fields correctly say NOT RUN.
The separate live receipts establish Zetaris behavior. Disconnected CSV/REST,
schema errors, overflow, duplicate keys, ownership failures and timeouts are
injected/isolated failure tests, not deliberate outages of the shared stack.

From repository root: `node --check dispute-demo/app/web/app.js` and
`git diff --check` passed. Protected paths were compared with the baseline via
`git diff --exit-code 232945a1015381561785f092cbe95bba917429d7 --` followed by
`dispute-demo/app/{action_service,policy_engine,critic,orchestrator,reviewer}.py`,
`dispute-demo/integration/fresh_reads.py`, migrations, policies, data and both
accepted two-agent media files: no differences.

`python3 /private/tmp/usl-final-db-check.py` used read-only psql queries through
the existing container. Six full-table fingerprints and all financial counts
match the preflight: 4 decisions, 2 simulated credits, 4 audits, 1 review and
revision 17. Restricted action role remains non-superuser with writer membership
but no source-writer/storage-owner membership. The script's core fingerprint is
`md5(string_agg(row_to_json(t)::text, CHR(10) ORDER BY row_to_json(t)::text))`.
No shared case, memory or financial-state reset was performed.

## Operational limits and publication

Actual browser verification queried DP-0020 at
`2026-10-27T13:14:30.518583Z`. The [preview screenshot](evidence/dashboard-preview.png)
shows the read-only label, unverified status and matching two/two joined counts.
The [DQ screenshot](evidence/dashboard-dq.png) shows the dated five-rule receipt
and the controlled orphan. These are fresh screenshots of the live preview,
not images from the preserved T16 video. No Investigate/Recover action was used.
The subsequent real DP-9999 read displayed [unavailable](evidence/dashboard-unavailable.png)
with no case data and no inferred quality pass. The temporary loopback UI server
was stopped after verification; the reproduction command restarts it.

The local driver became slow during concurrent reads. The existing inventory
endpoint showed unavailable under its unchanged 45-second deadline; a separate
retry passed with 40 cases in 30.08 seconds. The panel accepts a canonical case
ID independently of inventory and has its own 180-second worker bound. No
freshness or query-plan guard was relaxed. Missing live data never becomes
an empty success or a recorded DQ pass.

The static source fixture service and dedicated `dispute_usl_v1` objects remain
available. The original five services were not restarted. Model activation time
and revision were not supplied by the inspected metadata; no cross-source
snapshot, source freshness, accuracy/time-saving benchmark or sponsor score is
claimed. The [addendum](../submission/USL_ADDENDUM.md) includes comparisons,
proposed uses and an improvement suggestion.

New live Nightshift calls/financial commits, new combined live H-MEM runs,
clean-machine licensed provisioning, portal submission and final receipt:
**NOT RUN**. Public event deadline rechecked. Anonymous retrieval of the
submission hub/requirements resource was inaccessible; authenticated form
requirements remain the leader's pre-submission check. Original T16 video/deck
are preserved.
The implementation phase included no Jira change, Git push or portal publication.
The subsequent user request authorizes committing this evidence with the code,
opening a PR and merging to `main`; it does not authorize a portal submission.
