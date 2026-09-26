
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        reporting_status as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    group by reporting_status

)

select *
from all_values
where value_field not in (
    'reported','suppressed','not_reportable'
)



  
  
      
    ) dbt_internal_test