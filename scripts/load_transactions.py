#!/usr/bin/env python3
"""Load the ULB credit-card transaction CSV into DuckDB or BigQuery."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from fraud_analytics.data import normalize_transactions


def load_duckdb(frame: pd.DataFrame, database_path: Path) -> str:
    import duckdb

    connection = duckdb.connect(str(database_path))
    try:
        connection.execute("create schema if not exists raw")
        connection.register("_incoming_transactions", frame)
        connection.execute(
            "create or replace table raw.transactions as "
            "select * from _incoming_transactions"
        )
    finally:
        connection.close()
    return f"DuckDB table raw.transactions in {database_path}"


def load_bigquery(frame: pd.DataFrame) -> str:
    from google.cloud import bigquery

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID is required for the BigQuery target")

    dataset_name = os.environ.get("BIGQUERY_RAW_DATASET", "raw")
    location = os.environ.get("GCP_LOCATION", "US")
    client = bigquery.Client(project=project_id, location=location)

    dataset_id = f"{project_id}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)

    table_id = f"{dataset_id}.transactions"
    config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    client.load_table_from_dataframe(frame, table_id, job_config=config).result()
    return f"BigQuery table {table_id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to creditcard.csv")
    parser.add_argument("--target", choices=("duckdb", "bigquery"), default="duckdb")
    parser.add_argument(
        "--duckdb-path",
        type=Path,
        default=Path(os.environ.get("DUCKDB_PATH", "fraud_analytics.duckdb")),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    print(f"Reading {args.input} ...")
    frame = normalize_transactions(pd.read_csv(args.input))
    print(
        f"Validated {len(frame):,} rows; "
        f"{int(frame['is_fraud'].sum()):,} labeled fraud"
    )

    destination = (
        load_duckdb(frame, args.duckdb_path)
        if args.target == "duckdb"
        else load_bigquery(frame)
    )
    print(f"Loaded {len(frame):,} rows into {destination}")


if __name__ == "__main__":
    main()

