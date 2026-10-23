{{ config(tags=['ml']) }}

select *
from {{ ref('fct_ml_risk_scores') }}
where risk_score < 0
   or risk_score > 1
   or supervised_score < 0
   or supervised_score > 1
   or anomaly_score < 0
   or anomaly_score > 1
