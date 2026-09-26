
    
    

with all_values as (

    select
        period_type as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."fact_nvss_final_t40_4"
    group by period_type

)

select *
from all_values
where value_field not in (
    'year','month'
)


