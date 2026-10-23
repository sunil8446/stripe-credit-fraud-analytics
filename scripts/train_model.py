#!/usr/bin/env python3
"""Train the Phase 2 model and publish scores into DuckDB."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import joblib

from fraud_analytics.modeling import train_and_score

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / os.environ.get("DUCKDB_PATH", "fraud_analytics.duckdb")
ARTIFACT = ROOT / "artifacts" / "fraud_model.joblib"


def main() -> None:
    if not DATABASE.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DATABASE}. Run `make seed` first.")

    connection = duckdb.connect(str(DATABASE))
    try:
        transactions = connection.execute(
            """
            select * from raw.transactions
            qualify row_number() over (
                partition by transaction_id order by transaction_id
            ) = 1
            order by transaction_id
            """
        ).fetchdf()
        result = train_and_score(transactions)
        generated_at = datetime.now(UTC).replace(tzinfo=None)

        scores = result.scores.copy()
        scores["model_version"] = result.metrics["model_version"]
        scores["scored_at"] = generated_at

        metrics = transactions.iloc[:1, :0].copy()
        for key, value in result.metrics.items():
            metrics[key] = [value]
        metrics["trained_at"] = generated_at

        connection.execute("create schema if not exists ml")
        connection.register("scores_frame", scores)
        connection.register("metrics_frame", metrics)
        connection.execute(
            "create or replace table ml.transaction_risk_scores as "
            "select * from scores_frame"
        )
        connection.execute(
            "create or replace table ml.model_metrics as select * from metrics_frame"
        )
    finally:
        connection.close()

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model_version": result.metrics["model_version"],
            "feature_names": result.feature_names,
            "supervised_model": result.supervised_model,
            "anomaly_model": result.anomaly_model,
        },
        ARTIFACT,
    )
    print(
        "Trained {model_version} on {sample_count} rows: AP={average_precision:.3f}, "
        "ROC AUC={roc_auc:.3f}, recall={recall:.3f}".format(**result.metrics)
    )
    print(f"Published scores to {DATABASE} and model artifact to {ARTIFACT}")


if __name__ == "__main__":
    main()
