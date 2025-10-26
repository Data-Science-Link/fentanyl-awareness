
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select data_source
from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
where data_source is null



  
  
      
    ) dbt_internal_test