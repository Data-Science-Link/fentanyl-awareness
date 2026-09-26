
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Suppressed CDC values must stay null in the published fact table.
select *
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where is_suppressed = true
  and rolling_12_month_deaths is not null
  
  
      
    ) dbt_internal_test