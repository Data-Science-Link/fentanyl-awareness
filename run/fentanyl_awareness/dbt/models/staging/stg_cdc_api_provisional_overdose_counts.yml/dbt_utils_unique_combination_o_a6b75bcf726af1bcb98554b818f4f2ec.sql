
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        year, month, state
    from "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts"
    group by year, month, state
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test