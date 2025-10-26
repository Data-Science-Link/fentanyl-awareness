
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state
from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_provisional_2018_current"
where state is null



  
  
      
    ) dbt_internal_test