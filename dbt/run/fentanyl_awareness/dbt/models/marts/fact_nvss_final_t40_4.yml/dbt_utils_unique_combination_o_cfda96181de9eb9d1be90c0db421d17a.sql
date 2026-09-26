
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        year, month, state, period_type
    from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
    group by year, month, state, period_type
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test