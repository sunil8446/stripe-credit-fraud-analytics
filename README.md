# Fraud Analytics Platform

[![CI](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/ci.yml)
[![Dashboard](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/pages.yml/badge.svg)](https://github.com/sunil8446/stripe-credit-fraud-analytics/actions/workflows/pages.yml)

[View the live dashboard](https://sunil8446.github.io/stripe-credit-fraud-analytics/)
· [Explore dbt lineage docs](https://sunil8446.github.io/stripe-credit-fraud-analytics/dbt-docs/)

An end-to-end credit-card fraud analytics project inspired by Stripe-style risk
monitoring. It turns the public ULB transaction dataset into tested analytical
models and an interactive dashboard.

**Phase 2.5 is now implemented:** a class-balanced logistic model and Isolation
Forest produce reproducible hybrid risk scores, temporal holdout metrics,
cost-aware alert thresholds, candidate comparisons, calibration diagnostics,
operational risk bands, and per-transaction explanations.

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
- **Model-aware risk ranking:** supervised fraud probability is blended with an
  unsupervised anomaly score without using the label as an input feature.
- **Explainable alerts:** each scored transaction includes its strongest local
  model reasons for analyst triage.
- **Honest evaluation:** the newest transactions are kept outside training, and
  the alert threshold is selected from training-period predictions only.
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
        │                       raw features + labels
        ├───────────────┐                 │
        ▼               ▼                 ▼
  KPI marts       heuristic mart    train_model.py
        │               │           temporal validation + cost tuning
        │               │                 │
        │               └─────────┬───────┘
        │                         ▼
        └──────────────► ML score + performance marts
                                  │
                                  ▼
                       Chart.js dashboard / BI
```

## Stack

| Layer | Local / CI | Cloud |
|---|---|---|
| Warehouse | DuckDB | BigQuery |
| Transformation | dbt Core | dbt Core |
| ML | scikit-learn + joblib | Optional extension |
| Quality | dbt tests + Pytest | dbt tests |
| Dashboard | Chart.js | GitHub Pages / Looker Studio |
| Automation | GitHub Actions | Manual BigQuery workflow |

## Quick start

Prerequisites: `uv`, Python 3.11–3.13, and `make`.

```bash
make setup
make phase2-5
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

3. Run `make dashboard` again. It builds the analytics layer, retrains the model,
   validates the ML marts, and exports the dashboard without reseeding the raw
   table.

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
  --target bigquery \
  --exclude tag:ml
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
- Temporal holdout average precision, ROC AUC, precision, recall, and F1
- False-positive rate, Brier score, calibration error, and confusion matrix
- Cost-aware threshold using a documented 25:1 missed-fraud/review cost ratio
- Like-for-like logistic, Isolation Forest, and hybrid model comparison
- Hybrid supervised/anomaly risk score and operational risk band
- Top local model reasons for every scored transaction
- Deduplication and data-quality statistics

The bundled 30-row seed demonstrates the complete workflow, but its model
metrics are **illustrative rather than statistically meaningful**. Load the
full ULB dataset before interpreting model performance.

The hybrid remains the active operational candidate because it combines
ranking, anomaly coverage, and local explanations. The comparison table reports
holdout results transparently; it does not auto-promote a winner from the tiny
demo holdout.

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

- Phase 1: batch analytics and dashboard — complete
- Phase 2: hybrid scoring, explainable reasons, and model monitoring — complete
- Phase 2.5: temporal validation, model comparison, calibration, and cost tuning — complete
- Phase 3: event streaming, threshold simulation, and drift monitoring
- Phase 4: analyst case management and a feedback-driven retraining loop

This project is educational and must not be used as the sole basis for blocking
real financial transactions.

## License

MIT
