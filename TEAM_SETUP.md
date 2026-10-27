# Team setup: synthetic dispute investigation

## What is built

We are building one Nightshift investigator with a Python controller, deterministic policy evaluator, pure critic and PostgreSQL action service for fictional payment disputes. Policy-permitted credit, evidence request and decline are autonomous; policy-required human review is exceptional and has no credit effect.

**Target data flow:** generated files → project PostgreSQL → Zetaris → approved backend reads → policy/investigator/critic/controller → PostgreSQL simulated decision service.

- Generated and validated **40 disputes**, 42 transactions, 54 settlement movements, 81 evidence items and 16 rules across two fictional policy versions.
- Added reproducible generation, test fixtures, evidence documents and data-validation tests.
- Rachel has loaded the project database and registered its tables in Zetaris.
- Added `get_dispute_context.py`; it expects the Zetaris datasource name **`dispute`**
- PR #4 supplied prototypes in `dispute-demo/agent/`. T02/T03 now provide typed retrieval/policy, T04 provides isolated-tested PostgreSQL storage, and T06 provides the pure critic and retires SQLite execution. T05 now provides the isolated-tested atomic action service. T07 now provides a tested real Nightshift investigator. Shared deployment/coherent reads, bounded workflow, verified portable memory setup and UI remain outstanding. See [context.md](./context.md) and [ROADMAP.md](./ROADMAP.md).

**Evidence date:** T02 verified typed retrieval and live JDBC reads on 27 October 2026, with 50 root-suite tests and 6 offline critic tests passing. See [the retrieval reference](./dispute-demo/docs/retrieval.md) and ROADMAP for exact evidence. Nightshift discovery failure remains dated T00 evidence; Nightshift and H-MEM were NOT RUN for T02. Setup/start/load commands below are instructions for a new environment; no service startup, installation or source loading was performed in T02.

**T03 follow-up, 27 October:** the canonical [policy evaluator](./dispute-demo/docs/policy.md)
is accepted with 70 main tests, 6 offline critic regressions and eight live JDBC
case evaluations passing. The prototype policy entry point delegates to it.
The initial connection-refused blocker was resolved by user-authorized launch of
the existing Docker Desktop and start of the existing dispute database container.
All persistent services are healthy and left running. No install, configuration
change, source reload or reset was needed. REST has no API key; JDBC passed.

GitHub shares code and generated files. It does **not** share running containers, database contents or passwords. These instructions create your own local setup on macOS/Linux using Bash. Windows users should use WSL2 with Docker integration and adapt their local paths.

## 1. Get the project and prerequisites

```bash
git clone https://github.com/rachelanneliew/Open-Agent-Hackathon.git
cd Open-Agent-Hackathon
```

Already cloned? Run `git pull` from your checkout instead.

Install **Docker Desktop, Python 3.10+, a JDK 11+ (21 works on Rachel's machine), and Git**. Cursor, Codex and Claude Code are optional development tools; none is a runtime component or a verified competition requirement. Allow Docker roughly **8 GB RAM and 4 CPUs**, following the bundled platform guide.

Check that these folders contain files:

```text
Open-Agent-Hackathon/
  dispute-demo/       # Our generated data, scripts and integration code
  getting-started/    # Official Zetaris connection helpers
  zetaris-platform/  # Downloaded platform bundle and matching JDBC driver
```

**If `dispute-demo` is missing, ask Rachel to push it before continuing.** The original outer repository stored the other two folders as nested repository references; they may be empty after cloning.

If `getting-started` is missing or empty, run from the project root:

```bash
git clone https://github.com/zetaris/getting-started.git getting-started
```

For `zetaris-platform`, download your own bundle from [Zetaris Cloud → Run locally](https://cloud.enterprise.zetaris.com/dashboard/download). Extract its contents into `zetaris-platform/`. Obtain the **matching Zetaris JDBC driver JAR** from the bundle/provider; do not substitute a generic Hive driver. If access or the driver is missing, contact the organisers/provider.

## 2. Start Zetaris

```bash
cd zetaris-platform
```

Follow the downloaded bundle's instructions to sign in to its image registry. Keep its image settings and set your own administrator password in its private `.env` before first startup.

```bash
./preflight.sh
docker compose pull
docker compose up -d
docker compose ps
```

Resolve preflight failures first. Initial startup can take several minutes; setup containers exiting successfully is normal.

Open **http://localhost:3000**, sign in with your local administrator account, then open **SQL Editor** and run:

```sql
SELECT 1
```

Continue only when it succeeds. The supplied platform uses Docker network `zetaris_default`; our project database joins that network.

## 3. Start the separate project database

In Terminal:

```bash
cd ../dispute-demo
python3 scripts/validate_synthetic_data.py
cp integration/env.example .env.local
nano .env.local
```

Set `DISPUTE_DB_PASSWORD` to your own private password. Save and exit. These are first-time setup steps; do not overwrite an existing configuration.

```bash
chmod 600 .env.local
bash integration/db.sh config --quiet
bash integration/db.sh up -d
bash integration/db.sh ps
```

This creates a separate PostgreSQL container, database `dispute_demo` and persistent volume. It does not use Zetaris's internal metastore for project data. Wait for the container to be healthy.

Create its read-only Zetaris account:

```bash
bash integration/db.sh exec dispute-postgres psql -U dispute_loader -d dispute_demo
```

Inside this PostgreSQL console, run:

```sql
CREATE ROLE dispute_reader LOGIN;
```

Then enter `\password dispute_reader` and follow the hidden password prompts. Keep this **reader password** for the next step. Finish with:

```sql
GRANT CONNECT ON DATABASE dispute_demo TO dispute_reader;
GRANT USAGE ON SCHEMA public TO dispute_reader;
```

Enter `\q` to return to Terminal.

## 4. Prove one small table works

In Terminal, preview the changes, then apply them after review:

```bash
python3 integration/load_data.py probe
python3 integration/load_data.py probe --apply
```

The printed SQL is the preview; there is no separate window.

In **Zetaris SQL Editor**, run the following with your reader password substituted. Do not run this in Terminal or save a password-filled copy to GitHub.

```sql
CREATE DATASOURCE dispute DESCRIBE BY "Synthetic dispute project" OPTIONS (
  jdbcdriver "org.postgresql.Driver",
  jdbcurl "jdbc:postgresql://dispute-postgres:5432/dispute_demo",
  username "dispute_reader",
  password "YOUR_READER_PASSWORD",
  fetchsize "1000"
)
```

Run these separately:

```sql
REGISTER DATASOURCE TABLE "connection_probe" FROM dispute
```

```sql
SELECT * FROM dispute.connection_probe
```

Expected: `PROBE-001` and `Synthetic dispute database connected`. Stop here if it fails. If the datasource/table already exists, query it instead of recreating it.

## 5. Load the generated data

In Terminal, still in `dispute-demo`:

```bash
python3 integration/load_data.py full
python3 integration/load_data.py full --apply
```

Review the preview before applying. This loads the five input datasets plus actual evidence text into `evidence_documents`. It excludes test answers. Existing tables cause an error rather than being overwritten.

In **Zetaris SQL Editor**, run **each line separately**:

```sql
REGISTER DATASOURCE TABLE "transactions" FROM dispute
REGISTER DATASOURCE TABLE "settlements" FROM dispute
REGISTER DATASOURCE TABLE "disputes" FROM dispute
REGISTER DATASOURCE TABLE "evidence" FROM dispute
REGISTER DATASOURCE TABLE "policy_rules" FROM dispute
REGISTER DATASOURCE TABLE "evidence_documents" FROM dispute
```

Check:

```sql
SELECT COUNT(*) FROM dispute.disputes
```

Expected: **40**. Registration is separate from loading: a table can exist in PostgreSQL without being available in Zetaris.

## 6. Connect Python through JDBC

In Terminal:

```bash
cd ../getting-started
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
nano .env.local
```

Add these settings using **your own local Zetaris login and absolute JAR path**:

```dotenv
ZETARIS_JDBC_URL=jdbc:zetaris:lightning@localhost:10000
ZETARIS_JDBC_JAR="/absolute/path/to/your/zetaris-driver.jar"
ZETARIS_USERNAME=YOUR_ZETARIS_LOGIN
ZETARIS_PASSWORD=YOUR_ZETARIS_PASSWORD
```

This login is different from PostgreSQL's `dispute_reader`. Preserve any existing settings. No REST API key is needed for this JDBC route.

```bash
chmod 600 .env.local
.venv/bin/python scripts/run_sql.py --channel jdbc -e "SELECT 1"
.venv/bin/python ../dispute-demo/integration/get_dispute_context.py DP-0014
```

**Ready when:** the last command returns JSON containing the dispute, transactions, settlements, evidence text and policy rules. For `DP-0014`, the capture is **10,000 cents** and completed refund **4,000 cents**.

For the canonical typed interface, follow [T02 retrieval](./dispute-demo/docs/retrieval.md): from `dispute-demo`, run `../getting-started/.venv/bin/python -m app.tools DP-0014`. It returns structured read status and typed data; history/state use named `--tool` options. Decision reads remain unsupported and source revisions remain null.

## 7. Connect Nightshift for the investigation agent

Install the Nightshift edition for your machine from [Meterless](https://meterless.ai/), then keep the app open. In the M1–M4 0.92.7 app, click **Open the cockpit → Setup → Providers**.

Under **Cloud provider keys**, use **NVIDIA → Get key** to create your own provider key, then **Add → Save** it in Nightshift. A cloud provider is the practical choice on an 8 GB Mac already running Zetaris. Provider usage is subject to your account's allowance; a paid subscription to a chat app is not a provider API key.

The **Runtime endpoint → Auth token** on the same page is a separate credential: it connects our Python code to Nightshift. Copy that runtime token, then run from the project root:

```bash
python3 dispute-demo/integration/check_nightshift.py --set-token
```

Paste at the hidden prompt and press Enter. This saves the token in the ignored `dispute-demo/.env.local` with owner-only permissions, preserving existing database settings. Never paste either key into chat or commit it.

The default runtime URL is `http://127.0.0.1:8088/v1`. If needed, set `METERLESS_BASE_URL` and `METERLESS_MODEL` in that private file; see `dispute-demo/integration/env.example`. Model discovery lists the IDs this runtime actually advertises.

After saving a provider key in Nightshift, run one small real inference check:

```bash
python3 dispute-demo/integration/check_nightshift.py --chat
```

**Ready when:** authenticated model discovery passes and the script receives a non-empty text reply through Nightshift. A running app or healthy endpoint alone does not prove a model can answer. This verifies only the connection; the structured investigator and prototype integration still need implementation and acceptance tests. The check follows the [Meterless provider contract](https://meterless.ai/engines.html).

## 8. H-MEM prototype prerequisites — setup not yet reproduced

The existing [Python client](./dispute-demo/agent/hmem_client.py) invokes the [TypeScript bridge](./dispute-demo/agent/hmem_bridge/server.ts) in a subprocess for each operation. It needs Node.js, a `tsx` runner and the selected official H-MEM reference source with its dependencies installed externally. The [bridge manifest](./dispute-demo/agent/hmem_bridge/package.json) declares none of those dependencies and pins no reference revision; installing that manifest alone is not a complete setup.

| Existing configuration/fallback | Source-visible behavior; not a verified setup |
|---|---|
| `HMEM_TSX` | Explicit path to the `tsx` executable; otherwise the client checks `../hmem-reference/reference/node_modules/.bin/tsx` relative to the repository root, then `tsx` on PATH. |
| `HMEM_REFERENCE_SRC` | Explicit path to the reference TypeScript entry point; otherwise the bridge resolves `../hmem-reference/reference/src/index.ts` relative to the repository root. |
| `persist_dir` / legacy `ledger_path` parameters | Memory defaults beneath the user's `.local/state/dispute-demo`; use isolated temporary test directories. Since T06, the critic ignores `ledger_path`, defaults it to None and never opens/creates SQLite state. Existing local ledgers are preserved. |

The sibling `hmem-reference` tree is an external prerequisite, not supplied by this repository or guaranteed to exist on another machine. T00 located upstream revision `1742dec56a66e58eef9dda2d2b865823758ca8cd`; this is a historical reference anchor, not proof that PR #4's external installation matches it. T09 must verify/pin the chosen source, runner/dependencies and portable setup, add bounded subprocess/error handling, and demonstrate real save → new process/restart → recall with customer isolation and safe serialized/concurrent persistence access. No install command or successful reference run is claimed here. A01 must still verify competition approval.

The [prototype H-MEM tests](./dispute-demo/agent/tests/test_hmem_integration.py) use the external reference even though their docstring says offline. They were NOT RUN in this alignment. The [compatibility critic tests](./dispute-demo/agent/tests/test_critic.py) now prove the retired writer cannot touch state; [canonical critic tests](./dispute-demo/tests/test_proposal_critic.py) use real policy outputs with I/O forbidden. These do not prove PostgreSQL action safety or a complete agent. Both test roots require explicit collection during implementation. Do not start services, reinstall teammates' environments, or use the resolver as a setup probe: it can write local state. Further tested setup instructions belong to T09.

## Working together

- Reuse the committed data. No regeneration is needed for prompt, agent or UI changes.
- Keep SQL and credentials on the backend. Agents call the narrow retrieval function.
- Keep `tests/fixtures/expected_results.json` inaccessible to agents; it contains expected answers.
- Do not commit `.env`, `.env.local`, passwords, `.venv` or database volumes. Use your own credentials; share any needed secrets privately.
- Keep datasource name **`dispute`** consistent. Older `registration.sql` and `verify.sql` examples may say `dispute_pg`; substitute `dispute` before using them.
- Each teammate owns a local database. Agree on schema/data changes before regenerating; existing database tables will need a deliberate refresh, not just `git pull`.
- Use a separate Git branch for your changes and merge through a pull request.

**Troubleshooting:** `SLF4J` logging warnings alone did not prevent our connection test. `TABLE_OR_VIEW_NOT_FOUND` means check datasource naming, registration and account access. Stop on actual failures rather than recreating or deleting databases.

## T04 storage acceptance — isolated PostgreSQL only

The [storage guide](./dispute-demo/docs/storage.md) describes migration 001,
role/guard enforcement, four-outcome persistence and minimum re-review/duplicate
scope. Twenty real PostgreSQL tests pass, including actual isolated-container
restart persistence. The normal 70 offline and 6 prototype tests still pass.

From `dispute-demo/`, run the separate integration gate with Docker already
running and the existing `postgres:16-alpine` image available:

```sh
DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -p test_decision_storage.py -v
```

It creates and removes only its own unnetworked test container/anonymous volume.
No existing database or Zetaris container is reset/restarted. Without the flag,
root discovery reports those 20 tests as explicitly skipped. The existing demo
database was **not migrated**; T02 revisions stay null and decision reads stay
unsupported. Deploy/register and verify fresh reads as part of action integration.
Do not use `dispute_loader` superuser credentials for runtime writes. No model,
canonical action service or H-MEM integration is established by these tests.

## T06 pure critic acceptance

See [the critic guide](./dispute-demo/docs/critic.md) for the typed interface,
citation/rationale vocabulary and correction semantics. Fresh T06 evidence:
92 offline tests, 4 compatibility tests and data validation pass; 20 PostgreSQL
tests skipped and 7 external H-MEM tests collected only. No live services were
checked or changed. The old SQLite action entry point is disabled. The next
assigned implementation should be T05, which must provide protected fresh reads
and the canonical PostgreSQL action service before any persisted runtime claim.

## T05 action-service acceptance and setup

The [action-service guide](./dispute-demo/docs/actions.md) documents the typed
interface, restricted connection ownership, retries and failure semantics.
138 tests pass, including 25 real PostgreSQL action tests and all 20 storage
tests. Four compatibility tests and data validation pass. T05 uses pinned
Psycopg 3.2.10; install `dispute-demo/requirements-actions.txt` in a dedicated
application virtual environment, preserving the existing JDBC environment.

The default connector reads private process setting `DISPUTE_ACTION_DSN` and
requires an unprivileged login granted only `dispute_action_writer`. Do not use
the loader/admin login. No shared migration, login grant or Zetaris registration
was performed. Current null-revision reads cannot commit; deployment and verified
coherent fresh Zetaris reads remain an explicit T08 prerequisite.

From `dispute-demo/` with the dependency installed, Docker running and the
existing PostgreSQL image:

```sh
DISPUTE_ACTION_TESTS=1 DISPUTE_STORAGE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

This creates/cleans only disposable test containers and volumes. T05 publishes an
ephemeral loopback-only test port; T04 uses its existing unnetworked fixture.
Without opt-in, 45 PostgreSQL checks are explicitly skipped. Nightshift, live
Zetaris and H-MEM were NOT RUN for T05. Next implementation task: T07 / KAN-16.

## T07 investigator acceptance and live read-only check

See [the investigator guide](./dispute-demo/docs/investigator.md). The existing
Nightshift installation was opened without configuration changes; discovery and
one real structured proposal now pass. Requested route `meterless/auto`; the
response reported `nvidia/nemotron-3.5-bolt-e4b`. JDBC preflight passed (REST remains
unconfigured). This supersedes historical unavailability for this dated check,
not a guarantee the app is always running. Keep it open for model calls.

From `dispute-demo/`, after JDBC preflight:

```sh
PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m integration.check_investigator DP-0014
DISPUTE_NIGHTSHIFT_HTTP_TESTS=1 PYTHONDONTWRITEBYTECODE=1 ../getting-started/.venv/bin/python -m unittest discover -s tests -v
```

The probe is read-only and prints `persisted: false`; the current null revision
cannot commit. It has no fixture fallback or tool-dispatch loop. The test flag
enables five ephemeral local HTTP fixture checks, not real model calls. T07's
full suite passed 121 tests with 45 PostgreSQL opt-in skips; four compatibility
tests and data validation passed. No package installation or private setting
changes. T08 owns deployment, coherent reads and the complete bounded workflow.
