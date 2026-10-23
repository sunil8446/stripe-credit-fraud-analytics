import pandas as pd

from fraud_analytics.modeling import prepare_features, risk_band, train_and_score


def training_frame() -> pd.DataFrame:
    rows = []
    for index in range(24):
        fraud = int(index % 6 == 0)
        rows.append(
            {
                "transaction_id": f"tx_{index}",
                "seconds_elapsed": index * 1_000,
                "amount": 900.0 + index if fraud else 10.0 + index,
                "is_fraud": fraud,
                "v1": -3.0 if fraud else 0.2,
                "v2": 2.4 if fraud else -0.1,
            }
        )
    return pd.DataFrame(rows)


def test_prepare_features_uses_available_pca_columns_without_label_leakage() -> None:
    features = prepare_features(training_frame())

    assert list(features.columns) == ["seconds_elapsed", "log_amount", "v1", "v2"]
    assert "is_fraud" not in features


def test_train_and_score_returns_bounded_explainable_scores() -> None:
    result = train_and_score(training_frame())

    assert result.metrics["validation_strategy"] == "4-fold stratified out-of-fold"
    assert result.scores["risk_score"].between(0, 1).all()
    assert result.scores["reason_1"].str.len().gt(0).all()
    assert set(result.scores["risk_band"]).issubset(
        {"low", "review", "high", "critical"}
    )


def test_risk_band_boundaries() -> None:
    assert risk_band(0.10) == "low"
    assert risk_band(0.25) == "review"
    assert risk_band(0.50) == "high"
    assert risk_band(0.75) == "critical"
