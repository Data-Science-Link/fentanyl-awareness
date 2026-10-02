-- The national month series should move one month at a time.
with ordered as (
    select
        month
        , lag(month) over (order by month) as previous_month
    from {{ ref('fact_deaths_by_month') }}
)

select month
from ordered
where previous_month is not null
  and month <> previous_month + interval 1 month
