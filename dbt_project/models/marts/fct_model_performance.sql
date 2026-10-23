{{ config(tags=['ml']) }}

select
    model_version,
    validation_strategy,
    sample_count,
    fraud_count,
    feature_count,
    decision_threshold,
    average_precision,
    roc_auc,
    precision,
    recall,
    f1_score,
    trained_at
from {{ source('ml', 'model_metrics') }}
