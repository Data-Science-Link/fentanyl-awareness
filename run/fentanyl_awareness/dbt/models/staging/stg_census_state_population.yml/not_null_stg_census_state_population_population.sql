
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select population
from "fentanyl_awareness"."main"."stg_census_state_population"
where population is null



  
  
      
    ) dbt_internal_test