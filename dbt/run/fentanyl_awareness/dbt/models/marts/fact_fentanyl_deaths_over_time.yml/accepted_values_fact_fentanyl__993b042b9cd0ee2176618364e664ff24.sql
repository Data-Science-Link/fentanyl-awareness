
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        geo_type as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    group by geo_type

)

select *
from all_values
where value_field not in (
    'nation','state','city','territory'
)



  
  
      
    ) dbt_internal_test