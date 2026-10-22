with source as (
    select
        cast(transaction_id as {{ dbt.type_string() }}) as transaction_id,
        cast(seconds_elapsed as {{ dbt.type_bigint() }}) as seconds_elapsed,
        cast(amount as {{ dbt.type_numeric() }}) as amount,
        cast(is_fraud as {{ dbt.type_int() }}) as is_fraud,
        cast(v1 as {{ dbt.type_numeric() }}) as v1,
        cast(v2 as {{ dbt.type_numeric() }}) as v2,
        cast(v3 as {{ dbt.type_numeric() }}) as v3,
        cast(v4 as {{ dbt.type_numeric() }}) as v4,
        cast(v5 as {{ dbt.type_numeric() }}) as v5
    from {{ source('raw', 'transactions') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by transaction_id
            order by seconds_elapsed desc
        ) as duplicate_rank
    from source
),

validated as (
    select
        transaction_id,
        seconds_elapsed,
        {{ timestamp_from_seconds('seconds_elapsed') }} as transaction_at,
        amount,
        is_fraud,
        v1,
        v2,
        v3,
        v4,
        v5
    from ranked
    where duplicate_rank = 1
      and amount >= 0
      and is_fraud in (0, 1)
)

select * from validated

