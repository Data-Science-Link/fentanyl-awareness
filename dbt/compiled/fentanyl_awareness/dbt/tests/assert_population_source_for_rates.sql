-- State and national rates use Census PEP. A carried-forward denominator
-- must name the population year.
select
    state
    , year
    , population_source
    , population_year
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where geo_type in ('state', 'nation', 'territory')
  and population is not null
  and (
      population_source <> 'Census PEP'
      or population_year is null
      or (population_year <> year) <> population_is_carried_forward
  )