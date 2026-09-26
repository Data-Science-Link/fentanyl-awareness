
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select is_suppressed
from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
where is_suppressed is null



  
  
      
    ) dbt_internal_test