# Three synthetic sources

These are independent storage/connectors in a local demonstration, not three
real organizations or three production systems. They share the local Docker
host. Existing business IDs were selected from the canonical synthetic dataset;
the new merchant-contact records and API history index were authored separately.
Neither is copied into PostgreSQL or used by the decision workflow.

| Source | Mechanism / location | Data and scope |
|---|---|---|
| `dispute` | Existing PostgreSQL JDBC, `dispute-postgres:5432/dispute_demo` | 40 cases and transaction ownership; unchanged existing reader |
| `dispute_merchant_v1` | FileStore CSV, dedicated `shared/dispute-usl-v1/merchant_evidence.csv` in driver storage | Four merchant-contact metadata records, version `merchant-v1` |
| `dispute_customer_v1` | REST JSON, `dispute-usl-customer-api-v1:8090/v1/history` on the existing Docker network | Three history-index records, version `customer-v1`; outcomes explicitly `unknown` |

Multiple PostgreSQL tables still count as one datasource. CSV and REST use
separate Lightning databases and actual connector registrations.

## Prepare on a configured local Zetaris instance

Run JDBC preflight first. These commands create new resources; inspect names
before use and never replace an existing source silently. From repository root:

```sh
docker compose -f dispute-demo/integration/usl_sources/compose.yml config --quiet
docker compose -f dispute-demo/integration/usl_sources/compose.yml up -d
docker exec zetaris-driver-1 mkdir /home/zetaris/customer-data/shared/dispute-usl-v1
docker cp dispute-demo/integration/usl/fixtures/merchant_evidence.csv zetaris-driver-1:/home/zetaris/customer-data/shared/dispute-usl-v1/merchant_evidence.csv
docker exec zetaris-driver-1 sha256sum /home/zetaris/customer-data/shared/dispute-usl-v1/merchant_evidence.csv
docker exec zetaris-driver-1 curl --fail --max-time 10 http://dispute-usl-customer-api-v1:8090/v1/history
```

Container names apply to this inspected bundle. Adapt to the verified deployment,
not a guessed path. `mkdir` deliberately fails on an existing directory. Compare
existing bytes before reuse. The Python image must already exist (`pull_policy:
never`); no dependency install is needed. The service runs as UID 65534, with a
read-only filesystem and mounts, no Linux capabilities, no host port, bounded
memory/processes, and no write/query/URL-input endpoint. Requests with extra
paths or query strings return 404; unsupported methods return 501.

The local files are checked in under
[fixtures](../../dispute-demo/integration/usl/fixtures/).
Merchant CSV SHA-256:
`aa3c45db0ccda1566d316b543617822e5b7582c9bef7d5f5f5ff19a15ec38e6c`.
After preparing them, preview then run the
[registration SQL](../../dispute-demo/integration/usl/sql/00_source_registration.sql)
through `getting-started/scripts/run_sql.py --channel jdbc`, followed by
[independent reads](../../dispute-demo/integration/usl/sql/00_source_verify.sql).

## Meaning and freshness

Merchant refund promises are not completed settlements. All merchant records
are `received_unverified`. History membership can be checked against current
PostgreSQL ownership, but `prior_outcome=unknown` is not an inferred decision.
For DP-0020 the other cases share its opening timestamp; history means other
cases observed by the fixture's timestamp, not claims filed before this case.

Fixture times are synthetic historical event times, not connector health or
freshness timestamps. Serving an old static file now does not make its business
facts current. Preserve versions and timestamps; the preview must state that
source freshness and cross-source atomicity are unverified. Do not refresh
timestamps merely to obtain a green freshness label.
