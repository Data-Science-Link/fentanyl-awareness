
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state_name
from "fentanyl_awareness"."main"."stg_census_state_population"
where state_name is null



  
  
      
    ) dbt_internal_test