
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select rolling_12_month_deaths
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where rolling_12_month_deaths is null



  
  
      
    ) dbt_internal_test