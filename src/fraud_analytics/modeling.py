"""Train, validate, compare, and explain the Phase 2.5 fraud-risk model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
MODEL_VERSION = "hybrid-logit-iforest-v2.5"
FALSE_POSITIVE_COST = 1.0
FALSE_NEGATIVE_COST = 25.0
TARGET_TRAIN_FRACTION = 0.70


@dataclass
class ModelResult:
    """Fitted estimators, temporal validation outputs, and transaction scores."""

    supervised_model: Pipeline
    anomaly_model: Pipeline
    feature_names: list[str]
    metrics: dict[str, float | int | str]
    comparisons: pd.DataFrame
    calibration: pd.DataFrame
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


def _anomaly_pipeline(contamination: float) -> Pipeline:
    return Pipeline(
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
    )


def _normalize(values: np.ndarray, reference: np.ndarray | None = None) -> np.ndarray:
    basis = values if reference is None else reference
    minimum = float(basis.min())
    maximum = float(basis.max())
    if maximum == minimum:
        return np.zeros_like(values, dtype=float)
    return np.clip((values - minimum) / (maximum - minimum), 0, 1)


def _cost_threshold(labels: pd.Series, scores: np.ndarray) -> float:
    candidates = np.unique(np.concatenate(([0.0, 0.5, 1.0], scores)))
    best: tuple[float, float, float] | None = None
    best_threshold = 0.5
    for threshold in candidates:
        predictions = (scores >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
        del tn, tp
        cost = fp * FALSE_POSITIVE_COST + fn * FALSE_NEGATIVE_COST
        recall = recall_score(labels, predictions, zero_division=0)
        rank = (float(cost), -float(recall), -float(threshold))
        if best is None or rank < best:
            best = rank
            best_threshold = float(threshold)
    return best_threshold


def _temporal_split(labels: pd.Series, seconds_elapsed: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Return chronological train/holdout indices while retaining both classes."""

    order = np.argsort(seconds_elapsed.to_numpy(), kind="stable")
    row_count = len(order)
    target = round(row_count * TARGET_TRAIN_FRACTION)
    lower = max(4, round(row_count * 0.50))
    upper = min(row_count - 2, round(row_count * 0.85))
    candidates = sorted(range(lower, upper + 1), key=lambda value: abs(value - target))

    for cutoff in candidates:
        train_index = order[:cutoff]
        validation_index = order[cutoff:]
        train_labels = labels.iloc[train_index]
        validation_labels = labels.iloc[validation_index]
        if (
            train_labels.nunique() == 2
            and validation_labels.nunique() == 2
            and int(train_labels.value_counts().min()) >= 2
        ):
            return train_index, validation_index
    raise ValueError(
        "Temporal validation requires both classes in the training and holdout periods"
    )


def _metric_row(
    model_name: str,
    labels: pd.Series,
    scores: np.ndarray,
    threshold: float,
    selected: bool = False,
) -> dict[str, float | int | str | bool]:
    predictions = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    return {
        "model_name": model_name,
        "selected_model": selected,
        "decision_threshold": threshold,
        "average_precision": float(average_precision_score(labels, scores)),
        "roc_auc": float(roc_auc_score(labels, scores)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1_score": float(f1_score(labels, predictions, zero_division=0)),
        "true_negative_count": int(tn),
        "false_positive_count": int(fp),
        "false_negative_count": int(fn),
        "true_positive_count": int(tp),
        "expected_cost": float(
            fp * FALSE_POSITIVE_COST + fn * FALSE_NEGATIVE_COST
        ),
    }


def _calibration_frame(labels: pd.Series, scores: np.ndarray) -> pd.DataFrame:
    values = pd.DataFrame({"label": labels.to_numpy(), "score": scores})
    values["bin"] = pd.cut(
        values["score"],
        bins=np.linspace(0, 1, 6),
        labels=False,
        include_lowest=True,
    )
    calibration = (
        values.groupby("bin", observed=True)
        .agg(
            mean_predicted_score=("score", "mean"),
            observed_fraud_rate=("label", "mean"),
            sample_count=("label", "size"),
        )
        .reset_index()
    )
    calibration["bin"] = calibration["bin"].astype(int)
    return calibration


def _out_of_fold_anomaly_scores(
    features: pd.DataFrame,
    labels: pd.Series,
    validation: StratifiedKFold,
    contamination: float,
) -> np.ndarray:
    raw_scores = np.zeros(len(features), dtype=float)
    for fit_index, score_index in validation.split(features, labels):
        model = _anomaly_pipeline(contamination).fit(features.iloc[fit_index])
        raw_scores[score_index] = -model.decision_function(features.iloc[score_index])
    return _normalize(raw_scores)


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
    """Evaluate on a temporal holdout, fit final models, and score all rows."""

    required = {"transaction_id", "is_fraud", "seconds_elapsed"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing training columns: {sorted(missing)}")

    labels = pd.to_numeric(frame["is_fraud"], errors="raise").astype(int)
    if not set(labels.unique()).issubset({0, 1}) or labels.nunique() != 2:
        raise ValueError("Training requires both legitimate and fraud labels")

    features = prepare_features(frame)
    train_index, validation_index = _temporal_split(labels, frame["seconds_elapsed"])
    train_features = features.iloc[train_index]
    validation_features = features.iloc[validation_index]
    train_labels = labels.iloc[train_index]
    validation_labels = labels.iloc[validation_index]

    folds = min(5, int(train_labels.value_counts().min()))
    validation = StratifiedKFold(
        n_splits=folds, shuffle=True, random_state=RANDOM_STATE
    )
    supervised_oof = cross_val_predict(
        _supervised_pipeline(),
        train_features,
        train_labels,
        cv=validation,
        method="predict_proba",
    )[:, 1]

    contamination = min(0.20, max(0.01, float(train_labels.mean())))
    anomaly_oof = _out_of_fold_anomaly_scores(
        train_features,
        train_labels,
        validation,
        contamination,
    )
    hybrid_oof = np.clip(0.8 * supervised_oof + 0.2 * anomaly_oof, 0, 1)

    supervised_threshold = _cost_threshold(train_labels, supervised_oof)
    anomaly_threshold = _cost_threshold(train_labels, anomaly_oof)
    hybrid_threshold = _cost_threshold(train_labels, hybrid_oof)

    evaluation_supervised = _supervised_pipeline().fit(train_features, train_labels)
    evaluation_anomaly = _anomaly_pipeline(contamination).fit(train_features)
    supervised_validation = evaluation_supervised.predict_proba(validation_features)[:, 1]
    raw_anomaly_train = -evaluation_anomaly.decision_function(train_features)
    raw_anomaly_validation = -evaluation_anomaly.decision_function(validation_features)
    anomaly_validation = _normalize(raw_anomaly_validation, reference=raw_anomaly_train)
    hybrid_validation = np.clip(
        0.8 * supervised_validation + 0.2 * anomaly_validation, 0, 1
    )

    comparison_rows = [
        _metric_row(
            "Logistic regression",
            validation_labels,
            supervised_validation,
            supervised_threshold,
        ),
        _metric_row(
            "Isolation Forest",
            validation_labels,
            anomaly_validation,
            anomaly_threshold,
        ),
        _metric_row(
            "Hybrid model",
            validation_labels,
            hybrid_validation,
            hybrid_threshold,
            selected=True,
        ),
    ]
    comparisons = pd.DataFrame(comparison_rows)
    hybrid_metrics = comparison_rows[-1]
    calibration = _calibration_frame(validation_labels, hybrid_validation)
    calibration_error = float(
        np.average(
            np.abs(
                calibration["mean_predicted_score"]
                - calibration["observed_fraud_rate"]
            ),
            weights=calibration["sample_count"],
        )
    )

    final_contamination = min(0.20, max(0.01, float(labels.mean())))
    supervised_model = _supervised_pipeline().fit(features, labels)
    anomaly_model = _anomaly_pipeline(final_contamination).fit(features)
    supervised_scores = supervised_model.predict_proba(features)[:, 1]
    raw_anomaly_scores = -anomaly_model.decision_function(features)
    anomaly_scores = _normalize(raw_anomaly_scores)
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

    validation_predictions = (hybrid_validation >= hybrid_threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(
        validation_labels, validation_predictions, labels=[0, 1]
    ).ravel()
    baseline_cost = float(validation_labels.sum() * FALSE_NEGATIVE_COST)
    expected_cost = float(fp * FALSE_POSITIVE_COST + fn * FALSE_NEGATIVE_COST)
    metrics: dict[str, float | int | str] = {
        "model_version": MODEL_VERSION,
        "validation_strategy": "chronological holdout; threshold tuned on training OOF",
        "sample_count": int(len(frame)),
        "training_count": int(len(train_index)),
        "validation_count": int(len(validation_index)),
        "fraud_count": int(labels.sum()),
        "feature_count": int(features.shape[1]),
        "validation_start_seconds": int(
            frame.iloc[validation_index]["seconds_elapsed"].min()
        ),
        "decision_threshold": hybrid_threshold,
        "false_positive_cost": FALSE_POSITIVE_COST,
        "false_negative_cost": FALSE_NEGATIVE_COST,
        "average_precision": float(hybrid_metrics["average_precision"]),
        "roc_auc": float(hybrid_metrics["roc_auc"]),
        "precision": float(hybrid_metrics["precision"]),
        "recall": float(hybrid_metrics["recall"]),
        "f1_score": float(hybrid_metrics["f1_score"]),
        "brier_score": float(brier_score_loss(validation_labels, hybrid_validation)),
        "calibration_error": calibration_error,
        "true_negative_count": int(tn),
        "false_positive_count": int(fp),
        "false_negative_count": int(fn),
        "true_positive_count": int(tp),
        "false_positive_rate": float(fp / max(fp + tn, 1)),
        "alert_rate": float(validation_predictions.mean()),
        "expected_cost": expected_cost,
        "baseline_cost": baseline_cost,
        "cost_savings_pct": float(
            100 * (baseline_cost - expected_cost) / max(baseline_cost, 1)
        ),
    }
    return ModelResult(
        supervised_model=supervised_model,
        anomaly_model=anomaly_model,
        feature_names=list(features.columns),
        metrics=metrics,
        comparisons=comparisons,
        calibration=calibration,
        scores=scores,
    )
