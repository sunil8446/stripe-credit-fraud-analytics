select
    transaction_date,
    count(*) as transaction_count,
    sum(is_fraud) as fraud_count,
    sum(amount) as transaction_amount,
    sum(case when is_fraud = 1 then amount else 0 end) as fraud_amount,
    avg(case when is_fraud = 1 then amount end) as avg_fraud_amount,
    avg(case when is_fraud = 0 then amount end) as avg_legitimate_amount,
    100.0 * sum(is_fraud) / nullif(count(*), 0) as fraud_rate_pct
from {{ ref('int_transaction_features') }}
group by 1

