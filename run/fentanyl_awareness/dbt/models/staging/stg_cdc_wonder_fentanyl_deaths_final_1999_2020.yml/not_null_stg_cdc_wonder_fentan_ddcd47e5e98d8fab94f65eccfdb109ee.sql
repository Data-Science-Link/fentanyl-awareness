
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select multiple_cause_of_death
from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_final_1999_2020"
where multiple_cause_of_death is null



  
  
      
    ) dbt_internal_test