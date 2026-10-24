{{ config(tags=['ml']) }}

select
    bin,
    mean_predicted_score,
    observed_fraud_rate,
    sample_count,
    model_version,
    evaluated_at
from {{ source('ml', 'model_calibration') }}
