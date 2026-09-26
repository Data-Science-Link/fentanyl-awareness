
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select population_is_carried_forward
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where population_is_carried_forward is null



  
  
      
    ) dbt_internal_test