
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select geo_type
from "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts"
where geo_type is null



  
  
      
    ) dbt_internal_test