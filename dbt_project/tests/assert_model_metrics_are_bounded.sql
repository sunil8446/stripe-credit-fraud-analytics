{{ config(tags=['ml']) }}

select *
from {{ ref('fct_model_performance') }}
where average_precision not between 0 and 1
   or roc_auc not between 0 and 1
   or precision not between 0 and 1
   or recall not between 0 and 1
   or f1_score not between 0 and 1
   or brier_score not between 0 and 1
   or calibration_error not between 0 and 1
   or false_positive_rate not between 0 and 1
   or alert_rate not between 0 and 1
   or decision_threshold not between 0 and 1
