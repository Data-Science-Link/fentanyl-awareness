
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- The newest month must include a United States (nation) row.
select 1 as missing_national_row
where not exists (
    select 1
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    where geo_type = 'nation'
      and month = (
          select max(month)
          from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
      )
)
  
  
      
    ) dbt_internal_test