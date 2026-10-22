#!/usr/bin/env python3
"""Export dbt marts from DuckDB into the static dashboard data bundle."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / os.environ.get("DUCKDB_PATH", "fraud_analytics.duckdb")
OUTPUT = ROOT / "dashboard" / "data" / "dashboard-data.js"


def rows(connection: duckdb.DuckDBPyConnection, query: str) -> list[dict]:
    cursor = connection.execute(query)
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, result, strict=True)) for result in cursor.fetchall()]


def main() -> None:
    if not DATABASE.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DATABASE}. Run `make demo` first.")

    connection = duckdb.connect(str(DATABASE), read_only=True)
    try:
        summary = rows(
            connection,
            """
            select
                sum(transaction_count) as transaction_count,
                sum(fraud_count) as fraud_count,
                sum(transaction_amount) as transaction_amount,
                sum(fraud_amount) as fraud_amount,
                100.0 * sum(fraud_count) / nullif(sum(transaction_count), 0) as fraud_rate_pct
            from marts.fct_fraud_daily
            """,
        )[0]
        daily = rows(
            connection,
            "select * from marts.fct_fraud_daily order by transaction_date",
        )
        segments = rows(
            connection,
            """
            select
                amount_segment,
                sum(transaction_count) as transaction_count,
                sum(fraud_count) as fraud_count,
                sum(transaction_amount) as transaction_amount,
                sum(fraud_amount) as fraud_amount,
                100.0 * sum(fraud_count) / nullif(sum(transaction_count), 0) as fraud_rate_pct
            from marts.fct_fraud_by_segment
            group by 1
            order by case amount_segment
                when 'zero' then 1 when 'micro' then 2 when 'small' then 3
                when 'medium' then 4 else 5 end
            """,
        )
        time_of_day = rows(
            connection,
            """
            select
                time_of_day,
                sum(transaction_count) as transaction_count,
                sum(fraud_count) as fraud_count,
                100.0 * sum(fraud_count) / nullif(sum(transaction_count), 0) as fraud_rate_pct
            from marts.fct_fraud_by_segment
            group by 1
            order by case time_of_day
                when 'night' then 1 when 'morning' then 2
                when 'afternoon' then 3 else 4 end
            """,
        )
        risk_tiers = rows(
            connection,
            """
            select * from marts.fct_risk_tier
            order by case heuristic_risk_tier
                when 'low' then 1 when 'review' then 2
                when 'high' then 3 else 4 end
            """,
        )
    finally:
        connection.close()

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": "DuckDB dbt marts",
        "summary": summary,
        "daily": daily,
        "segments": segments,
        "time_of_day": time_of_day,
        "risk_tiers": risk_tiers,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "window.FRAUD_DATA = " + json.dumps(payload, default=str, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Exported dashboard data to {OUTPUT}")


if __name__ == "__main__":
    main()

