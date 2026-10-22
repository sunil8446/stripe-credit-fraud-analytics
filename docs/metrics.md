# Metric definitions

| Metric | Definition |
|---|---|
| Transaction count | Count of validated, deduplicated transactions |
| Transaction amount | Sum of `amount` across transactions |
| Fraud count | Sum of the binary `is_fraud` label |
| Fraud amount | Sum of `amount` where `is_fraud = 1` |
| Fraud rate | Fraud count divided by transaction count, expressed as a percentage |
| Amount segment | Zero; micro `< $10`; small `< $100`; medium `< $1,000`; large `>= $1,000` |
| Time of day | Night `00–05`; morning `06–11`; afternoon `12–17`; evening `18–23` |
| Heuristic risk tier | Transparent score based on amount, night activity, and extreme PCA features |

The heuristic tier is an explainable demonstration, not a trained fraud model.
It intentionally excludes `is_fraud` from its inputs to prevent target leakage.

