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
5. `scripts/train_model.py` evaluates a class-balanced logistic classifier with
   stratified out-of-fold predictions, then fits it alongside an Isolation
   Forest and publishes versioned transaction scores.
6. ML marts join the scores to analytics features and validate score bounds,
   coverage, risk bands, and model-performance metadata.
7. `scripts/export_dashboard.py` creates a static JavaScript data bundle from
   the tested analytics and ML marts.

## Why DuckDB and BigQuery

DuckDB makes onboarding and CI fast, deterministic, and free. BigQuery provides
a serverless production warehouse and supports the same analytical SQL through
adapter-dispatched dbt macros. Separating the targets prevents every pull request
from consuming cloud resources.

## Security boundaries

- Credentials are provided only through environment variables or GitHub Secrets.
- Service-account JSON and downloaded transaction data are ignored by Git.
- Cloud deployment is manual and has read-only repository permissions.
- Dashboard alerts use only content-derived transaction IDs and anonymized ULB
  features; the source dataset contains no cardholder identity fields.

## Extension path

The next logical layer is a streaming simulator with temporal validation,
threshold tuning, feature-drift checks, and an analyst feedback loop. It can
publish synthetic events without changing the current marts or dashboard
contract.

