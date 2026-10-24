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
| Supervised score | Fraud probability from a class-balanced logistic regression fitted without label leakage |
| Anomaly score | Min-max normalized Isolation Forest anomaly signal |
| Hybrid risk score | `80% × supervised score + 20% × anomaly score`, bounded from 0 to 1 |
| Model risk band | Low `< 0.25`; review `< 0.50`; high `< 0.75`; critical `>= 0.75` |
| Average precision | Area under the precision-recall curve on the chronological holdout |
| ROC AUC | Ranking quality on the chronological holdout |
| False-positive rate | False alerts divided by all legitimate holdout transactions |
| Brier score | Mean squared difference between holdout scores and labels; lower is better |
| Calibration error | Holdout-size-weighted difference between predicted and observed fraud rates |
| Expected cost | `false positives × 1 + false negatives × 25` in illustrative cost units |
| Cost savings | Reduction in expected cost versus raising no alerts |

The heuristic tier is an explainable demonstration, not a trained fraud model.
It intentionally excludes `is_fraud` from its inputs to prevent target leakage.

The Phase 2.5 model uses elapsed time, log-transformed amount, and available
anonymized PCA features. The newest transactions form an untouched holdout.
Within the earlier training period, stratified out-of-fold predictions select
each candidate's cost-aware threshold. Displayed performance is measured only
on the future holdout; the final operational model is then fitted on all rows.
The 25:1 cost ratio is a documented demonstration assumption, not a real issuer
cost estimate. The bundled seed is too small for performance claims.

