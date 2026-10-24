# Team setup: synthetic dispute investigation

## What is built

We are building agents that investigate fictional payment disputes, check evidence and policies, and recommend a simulated action.

**Data flow:** generated files → project PostgreSQL → Zetaris → backend retrieval function → agents.

- Generated and validated **40 disputes**, 42 transactions, 54 settlement movements, 81 evidence items and 16 rules across two fictional policy versions.
- Added reproducible generation, test fixtures, evidence documents and data-validation tests.
- Rachel has loaded the project database and registered its tables in Zetaris.
- Added `get_dispute_context.py`; it expects the Zetaris datasource name **`dispute`**
- Agent decision-making, critic loop, H-MEM, final UI and safe simulated actions are still to be built. The final connection test below verifies your own setup.

GitHub shares code and generated files. It does **not** share running containers, database contents or passwords. These instructions create your own local setup on macOS/Linux using Bash. Windows users should use WSL2 with Docker integration and adapt their local paths.

## 1. Get the project and prerequisites

```bash
git clone https://github.com/rachelanneliew/Open-Agent-Hackathon.git
cd Open-Agent-Hackathon
```

Already cloned? Run `git pull` from your checkout instead.

Install **Docker Desktop, Python 3.10+, a JDK 11+ (21 works on Rachel's machine), Git and Cursor**.  Allow Docker roughly **8 GB RAM and 4 CPUs**, following the bundled platform guide.

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

## Working together

- Reuse the committed data. No regeneration is needed for prompt, agent or UI changes.
- Keep SQL and credentials on the backend. Agents call the narrow retrieval function.
- Keep `tests/fixtures/expected_results.json` inaccessible to agents; it contains expected answers.
- Do not commit `.env`, `.env.local`, passwords, `.venv` or database volumes. Use your own credentials; share any needed secrets privately.
- Keep datasource name **`dispute`** consistent. Older `registration.sql` and `verify.sql` examples may say `dispute_pg`; substitute `dispute` before using them.
- Each teammate owns a local database. Agree on schema/data changes before regenerating; existing database tables will need a deliberate refresh, not just `git pull`.
- Use a separate Git branch for your changes and merge through a pull request.

**Troubleshooting:** `SLF4J` logging warnings alone did not prevent our connection test. `TABLE_OR_VIEW_NOT_FOUND` means check datasource naming, registration and account access. Stop on actual failures rather than recreating or deleting databases.
