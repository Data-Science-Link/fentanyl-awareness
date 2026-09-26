
    
    

with all_values as (

    select
        source_dataset as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."stg_nvss_final_t40_4"
    group by source_dataset

)

select *
from all_values
where value_field not in (
    'D77','D157'
)


