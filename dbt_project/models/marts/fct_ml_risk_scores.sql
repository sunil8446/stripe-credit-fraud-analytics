{{ config(tags=['ml']) }}

with scores as (
    select * from {{ source('ml', 'transaction_risk_scores') }}
),

transactions as (
    select * from {{ ref('int_transaction_features') }}
)

select
    transactions.transaction_id,
    transactions.transaction_at,
    transactions.amount,
    transactions.amount_segment,
    transactions.time_of_day,
    transactions.is_fraud,
    scores.supervised_score,
    scores.anomaly_score,
    scores.risk_score,
    scores.risk_band,
    scores.reason_1,
    scores.reason_2,
    scores.reason_3,
    scores.model_version,
    scores.scored_at
from transactions
inner join scores using (transaction_id)
