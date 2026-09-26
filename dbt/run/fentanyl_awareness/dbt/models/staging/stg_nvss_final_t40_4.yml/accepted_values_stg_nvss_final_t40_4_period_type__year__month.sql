
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        period_type as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
    group by period_type

)

select *
from all_values
where value_field not in (
    'year','month'
)



  
  
      
    ) dbt_internal_test