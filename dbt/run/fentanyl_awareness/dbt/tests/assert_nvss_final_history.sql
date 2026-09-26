
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Final incident deaths start in 1999, stay labeled, and do not publish 1-9 counts.
select 'missing 1999 United States annual row' as problem
where not exists (
    select 1
    from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
    where year = 1999
      and state = 'United States'
      and period_type = 'year'
      and data_source = 'NVSS final'
      and source_dataset = 'D77'
)

union all

select 'published count below 10' as problem
from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
where incident_deaths is not null
  and incident_deaths > 0
  and incident_deaths < 10

union all

select 'suppressed row has a count' as problem
from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
where is_suppressed
  and incident_deaths is not null

union all

select 'Louisiana missing from final series' as problem
where not exists (
    select 1
    from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
    where state = 'Louisiana'
      and period_type = 'year'
      and year >= 2018
      and source_dataset = 'D157'
)
  
  
      
    ) dbt_internal_test