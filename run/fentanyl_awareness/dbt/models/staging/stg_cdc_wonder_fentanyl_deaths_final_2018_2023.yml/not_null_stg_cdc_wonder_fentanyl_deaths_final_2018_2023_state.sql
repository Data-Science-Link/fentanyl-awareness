
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state
from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_final_2018_2023"
where state is null



  
  
      
    ) dbt_internal_test