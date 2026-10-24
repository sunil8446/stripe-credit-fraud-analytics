window.FRAUD_DATA = {
  "generated_at": "2026-10-24T18:02:45+00:00",
  "source": "DuckDB dbt marts",
  "summary": {
    "transaction_count": 30,
    "fraud_count": 5,
    "transaction_amount": "15965.950000",
    "fraud_amount": "7680.000000",
    "fraud_rate_pct": 16.666666666666668
  },
  "daily": [
    {
      "transaction_date": "2013-09-01",
      "transaction_count": 20,
      "fraud_count": 4,
      "transaction_amount": "11140.700000",
      "fraud_amount": "7000.000000",
      "avg_fraud_amount": 1750.0,
      "avg_legitimate_amount": 258.79375,
      "fraud_rate_pct": 20.0
    },
    {
      "transaction_date": "2013-09-02",
      "transaction_count": 10,
      "fraud_count": 1,
      "transaction_amount": "4825.250000",
      "fraud_amount": "680.000000",
      "avg_fraud_amount": 680.0,
      "avg_legitimate_amount": 460.5833333333333,
      "fraud_rate_pct": 10.0
    }
  ],
  "segments": [
    {
      "amount_segment": "micro",
      "transaction_count": 4,
      "fraud_count": 0,
      "transaction_amount": "24.930000",
      "fraud_amount": "0.000000",
      "fraud_rate_pct": 0.0
    },
    {
      "amount_segment": "small",
      "transaction_count": 11,
      "fraud_count": 1,
      "transaction_amount": "547.400000",
      "fraud_amount": "60.000000",
      "fraud_rate_pct": 9.090909090909092
    },
    {
      "amount_segment": "medium",
      "transaction_count": 9,
      "fraud_count": 1,
      "transaction_amount": "3843.620000",
      "fraud_amount": "680.000000",
      "fraud_rate_pct": 11.11111111111111
    },
    {
      "amount_segment": "large",
      "transaction_count": 6,
      "fraud_count": 3,
      "transaction_amount": "11550.000000",
      "fraud_amount": "6940.000000",
      "fraud_rate_pct": 50.0
    }
  ],
  "time_of_day": [
    {
      "time_of_day": "night",
      "transaction_count": 16,
      "fraud_count": 3,
      "fraud_rate_pct": 18.75
    },
    {
      "time_of_day": "morning",
      "transaction_count": 5,
      "fraud_count": 0,
      "fraud_rate_pct": 0.0
    },
    {
      "time_of_day": "afternoon",
      "transaction_count": 5,
      "fraud_count": 1,
      "fraud_rate_pct": 20.0
    },
    {
      "time_of_day": "evening",
      "transaction_count": 4,
      "fraud_count": 1,
      "fraud_rate_pct": 25.0
    }
  ],
  "risk_tiers": [
    {
      "heuristic_risk_tier": "low",
      "transaction_count": 10,
      "fraud_count": 0,
      "transaction_amount": "1787.740000",
      "observed_fraud_rate_pct": 0.0
    },
    {
      "heuristic_risk_tier": "review",
      "transaction_count": 13,
      "fraud_count": 0,
      "transaction_amount": "5385.710000",
      "observed_fraud_rate_pct": 0.0
    },
    {
      "heuristic_risk_tier": "high",
      "transaction_count": 4,
      "fraud_count": 2,
      "transaction_amount": "2412.500000",
      "observed_fraud_rate_pct": 50.0
    },
    {
      "heuristic_risk_tier": "critical",
      "transaction_count": 3,
      "fraud_count": 3,
      "transaction_amount": "6380.000000",
      "observed_fraud_rate_pct": 100.0
    }
  ],
  "model": {
    "performance": {
      "model_version": "hybrid-logit-iforest-v2.5",
      "validation_strategy": "chronological holdout; threshold tuned on training OOF",
      "sample_count": 30,
      "training_count": 21,
      "validation_count": 9,
      "fraud_count": 5,
      "feature_count": 7,
      "validation_start_seconds": 90000,
      "decision_threshold": 0.14063146369978263,
      "false_positive_cost": 1.0,
      "false_negative_cost": 25.0,
      "average_precision": 1.0,
      "roc_auc": 1.0,
      "precision": 0.3333333333333333,
      "recall": 1.0,
      "f1_score": 0.5,
      "brier_score": 0.011260295829299442,
      "calibration_error": 0.10115535301542988,
      "true_negative_count": 6,
      "false_positive_count": 2,
      "false_negative_count": 0,
      "true_positive_count": 1,
      "false_positive_rate": 0.25,
      "alert_rate": 0.3333333333333333,
      "expected_cost": 2.0,
      "baseline_cost": 25.0,
      "cost_savings_pct": 92.0,
      "trained_at": "2026-10-23 01:35:52.656979"
    },
    "risk_bands": [
      {
        "risk_band": "low",
        "transaction_count": 25,
        "fraud_count": 0,
        "average_risk_score": 0.07046565974956658
      },
      {
        "risk_band": "critical",
        "transaction_count": 5,
        "fraud_count": 5,
        "average_risk_score": 0.9186940890694825
      }
    ],
    "top_alerts": [
      {
        "transaction_id": "tx_0020",
        "transaction_at": "2013-09-01 23:00:00",
        "amount": "3200.000000",
        "is_fraud": 1,
        "risk_score": 0.996782627031245,
        "risk_band": "critical",
        "reason_1": "unusual multivariate pattern",
        "reason_2": "anomalous V4 signal",
        "reason_3": "anomalous V3 signal"
      },
      {
        "transaction_id": "tx_0025",
        "transaction_at": "2013-09-02 04:00:00",
        "amount": "680.000000",
        "is_fraud": 1,
        "risk_score": 0.9146820344573972,
        "risk_band": "critical",
        "reason_1": "unusual multivariate pattern",
        "reason_2": "anomalous V4 signal",
        "reason_3": "anomalous V1 signal"
      },
      {
        "transaction_id": "tx_0016",
        "transaction_at": "2013-09-01 15:00:00",
        "amount": "60.000000",
        "is_fraud": 1,
        "risk_score": 0.9056395597853901,
        "risk_band": "critical",
        "reason_1": "unusual multivariate pattern",
        "reason_2": "anomalous V4 signal",
        "reason_3": "anomalous V1 signal"
      },
      {
        "transaction_id": "tx_0009",
        "transaction_at": "2013-09-01 02:30:00",
        "amount": "2500.000000",
        "is_fraud": 1,
        "risk_score": 0.8985428113171126,
        "risk_band": "critical",
        "reason_1": "unusual multivariate pattern",
        "reason_2": "anomalous V1 signal",
        "reason_3": "anomalous V4 signal"
      },
      {
        "transaction_id": "tx_0005",
        "transaction_at": "2013-09-01 00:45:00",
        "amount": "1240.000000",
        "is_fraud": 1,
        "risk_score": 0.8778234127562675,
        "risk_band": "critical",
        "reason_1": "anomalous V4 signal",
        "reason_2": "anomalous V1 signal",
        "reason_3": "anomalous V3 signal"
      },
      {
        "transaction_id": "tx_0001",
        "transaction_at": "2013-09-01 00:00:00",
        "amount": "12.500000",
        "is_fraud": 0,
        "risk_score": 0.13947374483668123,
        "risk_band": "low",
        "reason_1": "anomalous V1 signal",
        "reason_2": "anomalous V4 signal",
        "reason_3": "transaction timing pattern"
      },
      {
        "transaction_id": "tx_0013",
        "transaction_at": "2013-09-01 09:00:00",
        "amount": "189.900000",
        "is_fraud": 0,
        "risk_score": 0.12809260349012497,
        "risk_band": "low",
        "reason_1": "anomalous V1 signal",
        "reason_2": "anomalous V2 signal",
        "reason_3": "transaction timing pattern"
      },
      {
        "transaction_id": "tx_0008",
        "transaction_at": "2013-09-01 02:00:00",
        "amount": "96.300000",
        "is_fraud": 0,
        "risk_score": 0.12164072350448688,
        "risk_band": "low",
        "reason_1": "transaction timing pattern",
        "reason_2": "anomalous V1 signal",
        "reason_3": "anomalous V3 signal"
      }
    ],
    "score_by_outcome": [
      {
        "outcome": "Legitimate",
        "average_risk_score": 0.07046565974956658,
        "average_supervised_score": 0.0398715847605348,
        "average_anomaly_score": 0.1928419597056936
      },
      {
        "outcome": "Fraud",
        "average_risk_score": 0.9186940890694825,
        "average_supervised_score": 0.9601237729472236,
        "average_anomaly_score": 0.7529753535585177
      }
    ],
    "comparison": [
      {
        "model_name": "Logistic regression",
        "selected_model": false,
        "decision_threshold": 0.03893131035156636,
        "average_precision": 1.0,
        "roc_auc": 1.0,
        "precision": 0.16666666666666666,
        "recall": 1.0,
        "f1_score": 0.2857142857142857,
        "true_negative_count": 3,
        "false_positive_count": 5,
        "false_negative_count": 0,
        "true_positive_count": 1,
        "expected_cost": 5.0,
        "model_version": "hybrid-logit-iforest-v2.5",
        "evaluated_at": "2026-10-23 01:35:52.656979"
      },
      {
        "model_name": "Isolation Forest",
        "selected_model": false,
        "decision_threshold": 0.5196550631323827,
        "average_precision": 1.0,
        "roc_auc": 1.0,
        "precision": 0.5,
        "recall": 1.0,
        "f1_score": 0.6666666666666666,
        "true_negative_count": 7,
        "false_positive_count": 1,
        "false_negative_count": 0,
        "true_positive_count": 1,
        "expected_cost": 1.0,
        "model_version": "hybrid-logit-iforest-v2.5",
        "evaluated_at": "2026-10-23 01:35:52.656979"
      },
      {
        "model_name": "Hybrid model",
        "selected_model": true,
        "decision_threshold": 0.14063146369978263,
        "average_precision": 1.0,
        "roc_auc": 1.0,
        "precision": 0.3333333333333333,
        "recall": 1.0,
        "f1_score": 0.5,
        "true_negative_count": 6,
        "false_positive_count": 2,
        "false_negative_count": 0,
        "true_positive_count": 1,
        "expected_cost": 2.0,
        "model_version": "hybrid-logit-iforest-v2.5",
        "evaluated_at": "2026-10-23 01:35:52.656979"
      }
    ],
    "calibration": [
      {
        "bin": 0,
        "mean_predicted_score": 0.10522215591265231,
        "observed_fraud_rate": 0.0,
        "sample_count": 8,
        "model_version": "hybrid-logit-iforest-v2.5",
        "evaluated_at": "2026-10-23 01:35:52.656979"
      },
      {
        "bin": 4,
        "mean_predicted_score": 0.9313790701623496,
        "observed_fraud_rate": 1.0,
        "sample_count": 1,
        "model_version": "hybrid-logit-iforest-v2.5",
        "evaluated_at": "2026-10-23 01:35:52.656979"
      }
    ]
  }
};
