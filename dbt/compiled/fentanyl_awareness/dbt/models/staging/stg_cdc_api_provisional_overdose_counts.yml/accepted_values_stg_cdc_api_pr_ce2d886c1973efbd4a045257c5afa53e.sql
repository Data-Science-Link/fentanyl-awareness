
    
    

with all_values as (

    select
        geo_type as value_field,
        count(*) as n_records

    from "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts"
    group by geo_type

)

select *
from all_values
where value_field not in (
    'nation','state','city','territory'
)


