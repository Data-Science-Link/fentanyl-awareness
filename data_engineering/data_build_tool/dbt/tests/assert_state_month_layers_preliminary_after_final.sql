-- Final certificates stay final. Later national months are preliminary
-- estimates. A state does not receive an invented monthly count.
with last_final as (
    select max(month) as month
    from {{ ref('fact_nvss_final_t40_4') }}
    where geo_type = 'nation'
      and period_type = 'month'
      and is_suppressed = false
      and incident_deaths is not null
),

layered as (
    select *
    from {{ ref('fact_deaths_by_state_month') }}
),

final_cutoff as (
    select month from last_final
)

select layered.month, layered.state, layered.confidence
from layered
cross join final_cutoff
where layered.state = 'United States'
  and layered.month <= final_cutoff.month
  and layered.confidence <> 'Final death certificate'

union all

select layered.month, layered.state, layered.confidence
from layered
cross join final_cutoff
where layered.state = 'United States'
  and layered.month > final_cutoff.month
  and layered.confidence not in ('Preliminary estimate', 'Preliminary estimate below zero')

union all

select month, state, confidence
from layered
where geo_type = 'state'
  and confidence in ('Preliminary estimate', 'Preliminary estimate below zero')

union all

select
    cast(null as date) as month
    , 'United States' as state
    , 'missing preliminary national months' as confidence
where (
    select count(*)
    from layered
    where state = 'United States'
      and confidence = 'Preliminary estimate'
) = 0
