
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where state is null



  
  
      
    ) dbt_internal_test