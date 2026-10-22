# Architecture

## Design goals

The platform is designed to be inexpensive, reproducible, and credible as a
production-oriented analytics project. Local development and CI use DuckDB;
BigQuery is an explicit deployment target rather than a prerequisite.

## Data flow

1. `scripts/load_transactions.py` validates source columns, converts data types,
   and creates a content-derived transaction identifier.
2. `raw.transactions` stores the imported rows without business aggregation.
3. `stg_transactions` enforces types, removes exact duplicates, and creates a
   transaction timestamp.
4. `int_transaction_features` assigns amount segments, dayparts, and transparent
   heuristic risk signals. The heuristic does not use the fraud label.
5. Marts aggregate daily performance, segment performance, and risk-tier
   outcomes.
6. `scripts/export_dashboard.py` creates a static JavaScript data bundle from
   the tested marts.

## Why DuckDB and BigQuery

DuckDB makes onboarding and CI fast, deterministic, and free. BigQuery provides
a serverless production warehouse and supports the same analytical SQL through
adapter-dispatched dbt macros. Separating the targets prevents every pull request
from consuming cloud resources.

## Security boundaries

- Credentials are provided only through environment variables or GitHub Secrets.
- Service-account JSON and downloaded transaction data are ignored by Git.
- Cloud deployment is manual and has read-only repository permissions.
- The dashboard receives aggregated data, not individual transactions.

## Extension path

The next logical layer is an offline model-training workflow that writes
versioned risk scores back to the warehouse. A later streaming simulator can
publish synthetic events to a queue without changing the marts or dashboard
contract.

