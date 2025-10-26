
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state_code
from "fentanyl_awareness"."main"."stg_census_state_economic"
where state_code is null



  
  
      
    ) dbt_internal_test