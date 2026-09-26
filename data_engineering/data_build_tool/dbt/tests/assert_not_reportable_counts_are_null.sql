-- A not_reportable row is a coverage flag, not a death count.
select
    state
    , month
from {{ ref('fact_fentanyl_deaths_over_time') }}
where reporting_status = 'not_reportable'
  and (
      rolling_12_month_deaths is not null
      or predicted_12_month_deaths is not null
      or headline_deaths is not null
  )
