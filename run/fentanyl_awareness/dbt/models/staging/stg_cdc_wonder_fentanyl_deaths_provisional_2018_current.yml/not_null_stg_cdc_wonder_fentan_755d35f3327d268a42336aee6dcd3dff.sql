
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select month
from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_provisional_2018_current"
where month is null



  
  
      
    ) dbt_internal_test