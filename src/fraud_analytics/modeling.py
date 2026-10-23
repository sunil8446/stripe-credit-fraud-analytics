"""Train and explain the Phase 2 fraud-risk model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
MODEL_VERSION = "hybrid-logit-iforest-v1"


@dataclass
class ModelResult:
    """Fitted estimators, validation metrics, and transaction-level scores."""

    supervised_model: Pipeline
    anomaly_model: Pipeline
    feature_names: list[str]
    metrics: dict[str, float | int | str]
    scores: pd.DataFrame


def _pca_columns(frame: pd.DataFrame) -> list[str]:
    columns = [
        column
        for column in frame.columns
        if column.startswith("v") and column[1:].isdigit()
    ]
    return sorted(columns, key=lambda column: int(column[1:]))


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build label-free numeric features from raw ULB-style transactions."""

    required = {"seconds_elapsed", "amount"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing model features: {sorted(missing)}")

    features = pd.DataFrame(index=frame.index)
    features["seconds_elapsed"] = pd.to_numeric(
        frame["seconds_elapsed"], errors="raise"
    ).astype(float)
    features["log_amount"] = np.log1p(
        pd.to_numeric(frame["amount"], errors="raise").astype(float)
    )
    for column in _pca_columns(frame):
        features[column] = pd.to_numeric(frame[column], errors="raise").astype(float)

    if features.isnull().any().any():
        raise ValueError("Model features cannot contain null values")
    return features


def _supervised_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2_000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _best_threshold(labels: pd.Series, probabilities: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(labels, probabilities)
    if not len(thresholds):
        return 0.5
    f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(
        precision[:-1] + recall[:-1], 1e-12
    )
    return float(thresholds[int(np.nanargmax(f1_values))])


def _normalize(values: np.ndarray) -> np.ndarray:
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum == minimum:
        return np.zeros_like(values, dtype=float)
    return (values - minimum) / (maximum - minimum)


def risk_band(score: float) -> str:
    """Map a zero-to-one model score to an operational triage band."""

    if score >= 0.75:
        return "critical"
    if score >= 0.50:
        return "high"
    if score >= 0.25:
        return "review"
    return "low"


def _reason_label(feature: str, value: float) -> str:
    if feature == "log_amount":
        return "elevated amount pattern" if value >= 0 else "amount pattern"
    if feature == "seconds_elapsed":
        return "transaction timing pattern"
    return f"anomalous {feature.upper()} signal"


def _explain(
    features: pd.DataFrame,
    supervised_model: Pipeline,
    anomaly_scores: np.ndarray,
) -> list[list[str]]:
    scaler = supervised_model.named_steps["scale"]
    classifier = supervised_model.named_steps["model"]
    standardized = scaler.transform(features)
    contributions = standardized * classifier.coef_[0]
    explanations: list[list[str]] = []

    for row_index, row in enumerate(contributions):
        ranked = np.argsort(row)[::-1]
        reasons = [
            _reason_label(features.columns[index], row[index])
            for index in ranked
            if row[index] > 0
        ][:3]
        if anomaly_scores[row_index] >= 0.65:
            reasons.insert(0, "unusual multivariate pattern")
        reasons = list(dict.fromkeys(reasons))[:3]
        while len(reasons) < 3:
            reasons.append("baseline model signal")
        explanations.append(reasons)
    return explanations


def train_and_score(frame: pd.DataFrame) -> ModelResult:
    """Train with out-of-fold evaluation and score every transaction."""

    required = {"transaction_id", "is_fraud"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing training columns: {sorted(missing)}")

    labels = pd.to_numeric(frame["is_fraud"], errors="raise").astype(int)
    if not set(labels.unique()).issubset({0, 1}) or labels.nunique() != 2:
        raise ValueError("Training requires both legitimate and fraud labels")

    minimum_class_size = int(labels.value_counts().min())
    if minimum_class_size < 2:
        raise ValueError("Training requires at least two rows in each class")

    features = prepare_features(frame)
    folds = min(5, minimum_class_size)
    validation = StratifiedKFold(
        n_splits=folds, shuffle=True, random_state=RANDOM_STATE
    )
    out_of_fold = cross_val_predict(
        _supervised_pipeline(),
        features,
        labels,
        cv=validation,
        method="predict_proba",
    )[:, 1]
    threshold = _best_threshold(labels, out_of_fold)
    predictions = (out_of_fold >= threshold).astype(int)

    supervised_model = _supervised_pipeline().fit(features, labels)
    supervised_scores = supervised_model.predict_proba(features)[:, 1]

    contamination = min(0.20, max(0.01, float(labels.mean())))
    anomaly_model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                IsolationForest(
                    contamination=contamination,
                    n_estimators=300,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    ).fit(features)
    raw_anomaly = -anomaly_model.decision_function(features)
    anomaly_scores = _normalize(raw_anomaly)
    combined_scores = np.clip(0.8 * supervised_scores + 0.2 * anomaly_scores, 0, 1)
    explanations = _explain(features, supervised_model, anomaly_scores)

    scores = pd.DataFrame(
        {
            "transaction_id": frame["transaction_id"].astype(str),
            "supervised_score": supervised_scores,
            "anomaly_score": anomaly_scores,
            "risk_score": combined_scores,
            "risk_band": [risk_band(score) for score in combined_scores],
            "reason_1": [reason[0] for reason in explanations],
            "reason_2": [reason[1] for reason in explanations],
            "reason_3": [reason[2] for reason in explanations],
        }
    )

    metrics: dict[str, float | int | str] = {
        "model_version": MODEL_VERSION,
        "validation_strategy": f"{folds}-fold stratified out-of-fold",
        "sample_count": int(len(frame)),
        "fraud_count": int(labels.sum()),
        "feature_count": int(features.shape[1]),
        "decision_threshold": threshold,
        "average_precision": float(average_precision_score(labels, out_of_fold)),
        "roc_auc": float(roc_auc_score(labels, out_of_fold)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1_score": float(f1_score(labels, predictions, zero_division=0)),
    }
    return ModelResult(
        supervised_model=supervised_model,
        anomaly_model=anomaly_model,
        feature_names=list(features.columns),
        metrics=metrics,
        scores=scores,
    )
