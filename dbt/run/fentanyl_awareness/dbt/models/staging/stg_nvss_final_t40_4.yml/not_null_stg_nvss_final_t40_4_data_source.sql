
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select data_source
from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
where data_source is null



  
  
      
    ) dbt_internal_test