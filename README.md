# Fraud Analytics Platform

[![CI](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/ci.yml)
[![Dashboard](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/pages.yml/badge.svg)](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/pages.yml)

[View the live dashboard](https://sunil8446.github.io/stripe-credit-fraud-analytics/)
· [Explore dbt lineage docs](https://sunil8446.github.io/stripe-credit-fraud-analytics/dbt-docs/)

An end-to-end credit-card fraud analytics project inspired by Stripe-style risk
monitoring. It turns the public ULB transaction dataset into tested analytical
models and an interactive dashboard.

This implementation is intentionally **local-first**: contributors can run the
complete pipeline with DuckDB at no cost, while the same dbt project can deploy
to BigQuery for a cloud portfolio demo.

## What makes this version stronger

- **Free local development:** DuckDB powers development and pull-request CI.
- **Production target:** environment-driven BigQuery configuration with no
  hard-coded project IDs or credential paths.
- **Layered warehouse design:** raw → staging → intermediate → marts.
- **Trustworthy metrics:** automated schema, relationship, accepted-value, and
  business-rule tests.
- **Cost-aware automation:** cloud builds are manual; ordinary CI never spends
  BigQuery credits.
- **Portfolio-ready delivery:** responsive dashboard, architecture docs, data
  dictionary, GitHub Actions, and dbt lineage documentation.

## Architecture

```text
ULB CSV / sample seed
        │
        ▼
  raw.transactions
        │
        ▼
  stg_transactions          validation, typing, deduplication
        │
        ▼
  int_transaction_features  amount bands, time bands, risk signals
        │
        ├───────────────┐
        ▼               ▼
  daily mart       segment mart      hourly mart
        │               │                 │
        └───────────────┴─────────────────┘
                        │
                        ▼
             Chart.js dashboard / BI
```

## Stack

| Layer | Local / CI | Cloud |
|---|---|---|
| Warehouse | DuckDB | BigQuery |
| Transformation | dbt Core | dbt Core |
| Quality | dbt tests + Pytest | dbt tests |
| Dashboard | Chart.js | GitHub Pages / Looker Studio |
| Automation | GitHub Actions | Manual BigQuery workflow |

## Quick start

Prerequisites: `uv`, Python 3.11–3.13, and `make`.

```bash
make setup
make demo
make serve
```

Open <http://localhost:8000>. The default build uses a small synthetic seed, so
it works without downloading data or creating a cloud account.

## Use the full ULB dataset

1. Download `creditcard.csv` from the
   [Kaggle ULB dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).
2. Load it into the local raw schema:

   ```bash
   .venv/bin/python scripts/load_transactions.py \
     --input /path/to/creditcard.csv \
     --target duckdb
   ```

3. Run `make dashboard` again. Unlike the demo target, this does not reseed the
   raw table, so the full dataset remains in place.

The dataset contains 284,807 anonymized transactions from September 2013,
including 492 labeled fraud cases. The source file is intentionally not stored
in Git.

## BigQuery deployment

Copy `.env.example` to `.env`, set the project and dataset values, and configure
Google Application Default Credentials. Then run:

```bash
.venv/bin/python scripts/load_transactions.py \
  --input /path/to/creditcard.csv \
  --target bigquery

.venv/bin/dbt build \
  --project-dir dbt_project \
  --profiles-dir dbt_project \
  --target bigquery
```

For GitHub Actions, configure these repository secrets:

- `GCP_PROJECT_ID`
- `GCP_CREDENTIALS` (the service-account JSON document)

The cloud workflow is manual by design. Set a BigQuery query quota and a Cloud
Billing budget before running it.

## Core metrics

- Transactions and payment volume
- Fraud cases, fraud amount, and fraud rate
- Fraud rate by amount segment and time of day
- Average fraud amount versus legitimate amount
- Highest-risk hour and segment
- Deduplication and data-quality statistics

## Repository layout

```text
dashboard/          Static interactive dashboard
dbt_project/        Models, tests, seeds, and profiles
docs/               Architecture and metric definitions
scripts/            Data loading and dashboard export tools
src/                Reusable Python data validation code
tests/              Python tests
```

## Roadmap

- Phase 1: batch analytics and dashboard (this repository)
- Phase 2: anomaly scoring with Isolation Forest and explainable risk reasons
- Phase 3: event streaming and alert simulation
- Phase 4: analyst case-management workflow and model monitoring

This project is educational and must not be used as the sole basis for blocking
real financial transactions.

## License

MIT
