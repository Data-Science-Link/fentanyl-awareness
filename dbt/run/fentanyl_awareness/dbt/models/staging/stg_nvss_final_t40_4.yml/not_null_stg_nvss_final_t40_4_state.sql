
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state
from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
where state is null



  
  
      
    ) dbt_internal_test