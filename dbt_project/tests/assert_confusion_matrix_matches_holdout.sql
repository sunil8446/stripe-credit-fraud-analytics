{{ config(tags=['ml']) }}

select *
from {{ ref('fct_model_performance') }}
where true_negative_count
    + false_positive_count
    + false_negative_count
    + true_positive_count != validation_count
