





with validation_errors as (

    select
        year, month, state
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    group by year, month, state
    having count(*) > 1

)

select *
from validation_errors


