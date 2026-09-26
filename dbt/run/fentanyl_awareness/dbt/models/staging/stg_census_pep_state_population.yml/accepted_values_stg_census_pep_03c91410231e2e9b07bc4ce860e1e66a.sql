
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        population_source as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."stg_census_pep_state_population"
    group by population_source

)

select *
from all_values
where value_field not in (
    'Census PEP'
)



  
  
      
    ) dbt_internal_test