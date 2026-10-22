select
    heuristic_risk_tier,
    count(*) as transaction_count,
    sum(is_fraud) as fraud_count,
    sum(amount) as transaction_amount,
    100.0 * sum(is_fraud) / nullif(count(*), 0) as observed_fraud_rate_pct
from {{ ref('int_transaction_features') }}
group by 1

