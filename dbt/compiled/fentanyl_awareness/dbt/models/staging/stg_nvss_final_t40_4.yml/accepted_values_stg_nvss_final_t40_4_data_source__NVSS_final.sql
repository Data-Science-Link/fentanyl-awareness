
    
    

with all_values as (

    select
        data_source as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
    group by data_source

)

select *
from all_values
where value_field not in (
    'NVSS final'
)


