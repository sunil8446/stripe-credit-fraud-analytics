select *
from {{ ref('fct_fraud_daily') }}
where fraud_count > transaction_count

