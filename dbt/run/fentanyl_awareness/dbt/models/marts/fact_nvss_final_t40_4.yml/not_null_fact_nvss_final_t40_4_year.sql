
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select year
from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
where year is null



  
  
      
    ) dbt_internal_test