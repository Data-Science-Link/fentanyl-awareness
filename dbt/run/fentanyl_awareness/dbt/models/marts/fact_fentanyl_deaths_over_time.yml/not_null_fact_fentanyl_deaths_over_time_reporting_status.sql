
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select reporting_status
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where reporting_status is null



  
  
      
    ) dbt_internal_test