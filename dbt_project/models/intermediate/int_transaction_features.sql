with transactions as (
    select * from {{ ref('stg_transactions') }}
),

features as (
    select
        *,
        cast(transaction_at as date) as transaction_date,
        extract(hour from transaction_at) as transaction_hour,
        case
            when amount = 0 then 'zero'
            when amount < 10 then 'micro'
            when amount < 100 then 'small'
            when amount < 1000 then 'medium'
            else 'large'
        end as amount_segment,
        case
            when extract(hour from transaction_at) < 6 then 'night'
            when extract(hour from transaction_at) < 12 then 'morning'
            when extract(hour from transaction_at) < 18 then 'afternoon'
            else 'evening'
        end as time_of_day,
        (
            case when amount >= 1000 then 2 else 0 end
            + case when extract(hour from transaction_at) < 6 then 1 else 0 end
            + case when abs(v1) >= 2.5 then 2 else 0 end
            + case when abs(v3) >= 2.5 then 2 else 0 end
        ) as heuristic_risk_points
    from transactions
),

classified as (
    select
        *,
        case
            when heuristic_risk_points >= 5 then 'critical'
            when heuristic_risk_points >= 3 then 'high'
            when heuristic_risk_points >= 1 then 'review'
            else 'low'
        end as heuristic_risk_tier
    from features
)

select * from classified

