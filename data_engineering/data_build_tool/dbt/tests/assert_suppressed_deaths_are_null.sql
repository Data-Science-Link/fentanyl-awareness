-- Suppressed CDC values must stay null in the published fact table.
select *
from {{ ref('fact_fentanyl_deaths_over_time') }}
where is_suppressed = true
  and rolling_12_month_deaths is not null
