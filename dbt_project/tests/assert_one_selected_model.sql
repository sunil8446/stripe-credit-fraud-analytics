{{ config(tags=['ml']) }}

select count(*) as selected_model_count
from {{ ref('fct_model_comparison') }}
where selected_model
having count(*) != 1
