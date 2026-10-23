import pandas as pd
import pytest

from fraud_analytics.data import PCA_COLUMNS, normalize_transactions, validate_transactions


def source_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Time": [0, 10],
            "Amount": [10.5, 900.0],
            "Class": [0, 1],
            "V1": [0.1, -2.9],
            "V2": [0.2, 1.8],
            "V3": [0.3, -3.2],
            "V4": [0.4, 4.1],
            "V5": [0.5, -1.4],
        }
    )


def test_normalize_transactions_uses_case_insensitive_source_columns() -> None:
    normalized = normalize_transactions(source_frame())

    assert list(normalized.columns) == [
        "transaction_id",
        "seconds_elapsed",
        "amount",
        "is_fraud",
        *PCA_COLUMNS,
    ]
    assert normalized["is_fraud"].tolist() == [0, 1]
    assert normalized["v28"].tolist() == [0.0, 0.0]


def test_exact_duplicates_receive_the_same_stable_identifier() -> None:
    source = source_frame().iloc[[0, 0]].reset_index(drop=True)

    normalized = normalize_transactions(source)

    assert normalized.loc[0, "transaction_id"] == normalized.loc[1, "transaction_id"]


def test_missing_required_source_column_is_rejected() -> None:
    with pytest.raises(ValueError, match="amount"):
        normalize_transactions(source_frame().drop(columns="Amount"))


def test_negative_amount_is_rejected() -> None:
    normalized = normalize_transactions(source_frame())
    normalized.loc[0, "amount"] = -1

    with pytest.raises(ValueError, match="amount"):
        validate_transactions(normalized)

