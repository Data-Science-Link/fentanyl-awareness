-- Louisiana has no T40.4 VSRR rows. The fact table must say so explicitly.
select 'Louisiana missing not_reportable row' as problem
where not exists (
    select 1
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    where state = 'Louisiana'
      and reporting_status = 'not_reportable'
)