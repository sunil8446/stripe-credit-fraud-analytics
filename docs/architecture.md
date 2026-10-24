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
5. `scripts/train_model.py` keeps the newest transactions as a chronological
   holdout. Training-period out-of-fold scores tune a cost-aware threshold;
   logistic, Isolation Forest, and hybrid candidates are then compared on the
   untouched future window.
6. ML marts join scores to analytics features and validate score bounds,
   coverage, risk bands, confusion totals, calibration, candidate comparisons,
   and model-performance metadata.
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

The next logical layer is a streaming simulator with feature-drift checks and
an analyst feedback loop. It can publish synthetic events without changing the
current marts or dashboard contract.

