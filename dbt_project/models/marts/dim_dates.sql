select distinct
    transaction_date,
    extract(year from transaction_date) as year_number,
    extract(month from transaction_date) as month_number,
    extract(day from transaction_date) as day_number
from {{ ref('int_transaction_features') }}

