{{ config(tags=['ml']) }}

select transactions.transaction_id
from {{ ref('int_transaction_features') }} as transactions
left join {{ ref('fct_ml_risk_scores') }} as scores using (transaction_id)
where scores.transaction_id is null
