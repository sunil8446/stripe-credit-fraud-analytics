"""Normalize and validate transaction data before warehouse loading."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

REQUIRED_SOURCE_COLUMNS = {"time", "amount", "class"}
PCA_COLUMNS = [f"v{index}" for index in range(1, 29)]
OUTPUT_COLUMNS = [
    "transaction_id",
    "seconds_elapsed",
    "amount",
    "is_fraud",
    *PCA_COLUMNS,
]


def _missing(columns: Iterable[str], required: set[str]) -> set[str]:
    return required.difference({column.lower() for column in columns})


def validate_transactions(frame: pd.DataFrame) -> None:
    """Raise ``ValueError`` when a normalized transaction frame is invalid."""

    missing = set(OUTPUT_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing normalized columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("The transaction file contains no rows")
    if frame[OUTPUT_COLUMNS].isnull().any().any():
        raise ValueError("Required transaction values cannot be null")
    if (frame["seconds_elapsed"] < 0).any():
        raise ValueError("Time values must be zero or greater")
    if (frame["amount"] < 0).any():
        raise ValueError("Transaction amounts must be zero or greater")
    if not set(frame["is_fraud"].unique()).issubset({0, 1}):
        raise ValueError("Fraud labels must be either 0 or 1")


def normalize_transactions(source: pd.DataFrame) -> pd.DataFrame:
    """Return a warehouse-ready subset of the ULB transaction dataset.

    Source column names are handled case-insensitively. A content-based ID is
    generated so exact duplicate input rows receive the same identifier and are
    deterministically removed in the staging model.
    """

    missing = _missing(source.columns, REQUIRED_SOURCE_COLUMNS)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")

    frame = source.copy()
    frame.columns = [column.strip().lower() for column in frame.columns]

    for column in PCA_COLUMNS:
        if column not in frame:
            frame[column] = 0.0

    selected = frame[["time", "amount", "class", *PCA_COLUMNS]].copy()
    selected = selected.rename(
        columns={"time": "seconds_elapsed", "class": "is_fraud"}
    )

    numeric_columns = ["seconds_elapsed", "amount", "is_fraud", *PCA_COLUMNS]
    for column in numeric_columns:
        selected[column] = pd.to_numeric(selected[column], errors="raise")

    selected["seconds_elapsed"] = selected["seconds_elapsed"].astype("int64")
    selected["is_fraud"] = selected["is_fraud"].astype("int64")

    row_hash = pd.util.hash_pandas_object(selected, index=False)
    selected.insert(
        0,
        "transaction_id",
        row_hash.map(lambda value: f"tx_{int(value):016x}"),
    )

    normalized = selected[OUTPUT_COLUMNS].reset_index(drop=True)
    validate_transactions(normalized)
    return normalized

