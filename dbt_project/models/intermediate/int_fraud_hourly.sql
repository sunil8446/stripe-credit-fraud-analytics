select
    transaction_date,
    transaction_hour,
    time_of_day,
    count(*) as transaction_count,
    sum(is_fraud) as fraud_count,
    sum(amount) as transaction_amount,
    sum(case when is_fraud = 1 then amount else 0 end) as fraud_amount,
    100.0 * sum(is_fraud) / nullif(count(*), 0) as fraud_rate_pct
from {{ ref('int_transaction_features') }}
group by 1, 2, 3

