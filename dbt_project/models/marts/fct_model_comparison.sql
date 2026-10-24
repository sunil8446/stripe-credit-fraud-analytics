{{ config(tags=['ml']) }}

select
    model_name,
    selected_model,
    decision_threshold,
    average_precision,
    roc_auc,
    precision,
    recall,
    f1_score,
    true_negative_count,
    false_positive_count,
    false_negative_count,
    true_positive_count,
    expected_cost,
    model_version,
    evaluated_at
from {{ source('ml', 'model_comparison') }}
