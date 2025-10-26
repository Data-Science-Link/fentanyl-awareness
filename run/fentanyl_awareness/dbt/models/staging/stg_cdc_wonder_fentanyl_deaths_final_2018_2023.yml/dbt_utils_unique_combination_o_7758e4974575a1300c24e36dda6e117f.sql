
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        year, month, state, multiple_cause_of_death_code
    from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_final_2018_2023"
    group by year, month, state, multiple_cause_of_death_code
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test