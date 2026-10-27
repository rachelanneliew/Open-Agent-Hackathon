# Local analyst workbench (T11)

The analyst page is a thin client of the [canonical workflow](./workflow.md).
It presents source facts, policy checks, the investigator proposal, critic
feedback and the acknowledged persistence result separately. Its only action
paths are `Controller.run`, `Controller.retry`, and the existing action-free
memory retry. It contains no policy evaluator or financial writer of its own.

## Start

Use the existing application environment and complete the bundled JDBC
preflight described in [TEAM_SETUP](../../TEAM_SETUP.md). Keep Nightshift and
the project database running. From `dispute-demo/`:

```sh
# Select the pinned Node 24.13.0 using HMEM_NODE if it is not on PATH.
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.ui
# Or explicitly disable advisory memory:
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m app.ui --no-memory
```

Open `http://127.0.0.1:8931`. `--port` selects another local port;
`--memory-dir outputs/demo-memory` selects a private memory store. The default
store is the same `outputs/hmem-v1` as the CLI. Different stores may contain
different history; an empty recall is not proof of no prior customer cases.
The T10/T11 live acceptance store is `outputs/t10-live-memory` on the tested
checkout, not a bundled sample or required teammate path.

The server binds only to IPv4 loopback, checks Host/Origin and a per-process
same-origin POST token, sends no-store/CSP headers, and serves only three fixed
assets. All source/evidence text is rendered as text, never executable HTML.
Money beyond JavaScript's exact integer range is transported as decimal text.
This is a trusted local synthetic demo, without production authentication or
public hosting. Stop the owned preview with Ctrl-C; the server waits for owned job threads
before releasing its operation-store lock. Interrupted transport or uncertain
action acknowledgement still requires saved-request recovery. Do not expose it through a public tunnel.

## Follow a case

1. Select a source-backed dispute. Inspect its source status, timestamps,
   transactions, settlement movements and expandable evidence text.
2. Click **Investigate**. Live Zetaris/Nightshift calls produce a real proposal;
   every financial effect remains synthetic. Ordinary permitted outcomes need
   no Approve button. Failed calls are shown without a sample fallback.
3. Read the three distinct result columns: business outcome, critic verdict,
   and persistence. Policy rows show matched/skipped rules and evidence links;
   evidence requests show exact missing categories and reasons.
4. Advisory history shows only T10 source-verified records with original
   decision/source references. Recall availability and summary storage are
   separate. History is partial context, never a fraud finding or policy hold.
5. **Saved decisions** comes from a fresh authoritative case read. The
   **Human review queue** comes from persisted, currently pending reviews.
   A rejected proposal or unavailable queue query never invents a queued item.

The source facts shown with a finished operation are its original investigation
snapshot, labelled with revision and cutoff. Saved decisions/queue are separately
refreshed observations; they are not attributed as new effects of that run.
Source `open` status is separate from decision and queue lifecycle. The four
business outcomes remain credit, evidence request, decline and human review.
There is no assignment, approval, resolution or source writeback UI.

## Click safety, recovery and restart

The browser retains the selected case and latest operation ID. A private
`outputs/ui/<operation_id>.json` is durably written before dispatch. Duplicate
operation IDs replay the saved operation; conflicting inputs are rejected.
Simultaneous clicks for the same in-flight operation coalesce. A different
operation is refused while another is running. An OS lock prevents two servers
from using the same operation store.

The canonical journal still writes the complete action request before dispatch.
The UI records its run ID durably before allowing that action call. After an
interruption, it does not automatically rerun a model or mint a replacement
action key. Refresh and use **Recover / reuse result** for the saved run. This
submits the identical request and may return the original `reused` decision.
An uncertain acknowledgement is not proof of rollback. **Retry memory only**
freshly verifies the receipt and saves its summary without calling an action.
Local saved requests from CLI runs are also available for recovery.

**Investigate again** intentionally obtains new facts and a new proposal. The
canonical database safeguards still block a second effective credit, even with
a new UI ID, a new browser, or a different process. Neither page refresh nor
memory retry is a reset. There is no shared-data reset control. T12 owns a
deliberate isolated demo reset; do not delete shared decisions or source rows.

Private operation/request records are owner-only and ignored by Git. The MVP
caps inventories at 1,000 rows/requests/operations and fails explicitly above
the limit. Archive handling and multi-user scheduling are outside this task.

## Read projection and verification

The [inventory adapter](../integration/analyst_reads.py) uses the existing
Zetaris connection and verifies each direct JDBC scan. Before/after revisions
must match; at most two attempts are allowed inside a process deadline. It
lists source cases and reads the actual pending-review view. The current
registration omits that view's UUID-typed decision ID, so the adapter resolves
the textual ID from the existing history view by case and commit instant.
An independent membership read must match the join exactly one-to-one; a
missing/ambiguous join, unsupported plan or overflow fails the whole read.
No migrations, registration edits or inferred queue membership are used.

```sh
DISPUTE_UI_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p test_ui.py -v
DISPUTE_ACTION_TESTS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p test_ui_end_to_end.py -v
```

HTTP tests use loopback fixtures; UI/database tests use real disposable
PostgreSQL with an explicitly scripted model. These are separate from live
browser acceptance recorded in [ROADMAP](../../ROADMAP.md). The shared-source
policy, action, critic, schema and database lifecycle remain canonical.

## Acceptance evidence

[T11 operation receipts](./evidence/t11-analyst.json) and the
[browser capture](./evidence/t11-analyst.png) show live review persistence,
credit reuse, source-verified history and refused model output. All four outcomes
also pass disposable PostgreSQL UI tests using a scripted model. Live model
schema/rationale reliability is imperfect; a refusal is visible and creates no
queue entry. The observed shared state is 3 decisions, 2 credits, 3 audits and
1 pending review at revision 14. The owned acceptance preview was stopped.
