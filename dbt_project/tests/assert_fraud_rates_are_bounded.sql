select *
from {{ ref('fct_fraud_by_segment') }}
where fraud_rate_pct < 0 or fraud_rate_pct > 100

