-- A published final count must stay the official count.
select monthly.month
from {{ ref('fact_deaths_by_month') }} as monthly
inner join {{ ref('fact_nvss_final_t40_4') }} as final
    on monthly.month = final.month
where final.geo_type = 'nation'
  and final.period_type = 'month'
  and final.is_suppressed = false
  and final.incident_deaths is not null
  and (
      monthly.how_produced <> 'Official final count'
      or monthly.estimated_deaths <> final.incident_deaths
  )
