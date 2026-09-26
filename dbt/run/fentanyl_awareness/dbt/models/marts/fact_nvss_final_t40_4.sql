
  
  create view "fentanyl_awareness"."main"."fact_nvss_final_t40_4__dbt_tmp" as (
    -- Final NVSS incident deaths for T40.4 drug overdoses.
-- Kept separate from the VSRR rolling series. Do not add these rows to
-- rolling_12_month_deaths.



select
    year
    , month
    , state
    , geo_type
    , period_type
    , incident_deaths
    , is_suppressed
    , data_source
    , source_dataset
    , extracted_at
from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
  );
