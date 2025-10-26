





with validation_errors as (

    select
        year, state_code
    from "fentanyl_awareness"."main"."stg_census_state_economic"
    group by year, state_code
    having count(*) > 1

)

select *
from validation_errors


