
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select population_source
from "fentanyl_awareness"."main"."stg_census_pep_state_population"
where population_source is null



  
  
      
    ) dbt_internal_test