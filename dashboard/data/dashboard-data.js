window.FRAUD_DATA = {
  "generated_at": "2026-10-22T22:10:10+00:00",
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
  ]
};
