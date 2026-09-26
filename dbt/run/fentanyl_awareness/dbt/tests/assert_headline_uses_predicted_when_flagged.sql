
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Predicted counts are the headline for the latest six months and wherever
-- CDC flags underreporting or incomplete data. Otherwise the headline is
-- the reported count. Predicted is never invented when CDC did not publish it.
with bounds as (
    select max(month) as max_month
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
),

flagged as (
    select
        state
        , month
        , headline_deaths
        , headline_basis
        , predicted_12_month_deaths
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    cross join bounds
    where predicted_12_month_deaths is not null
      and (
          month >= bounds.max_month - interval 6 month
          or (percent_complete is not null and percent_complete < 100)
          or lower(coalesce(footnote, '')) like '%underreport%'
          or lower(coalesce(footnote, '')) like '%incomplete%'
      )
      and (
          headline_basis <> 'predicted'
          or headline_deaths <> predicted_12_month_deaths
      )
),

reported_only as (
    select
        state
        , month
        , headline_deaths
        , headline_basis
        , rolling_12_month_deaths
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    cross join bounds
    where rolling_12_month_deaths is not null
      and not (
          predicted_12_month_deaths is not null
          and (
              month >= bounds.max_month - interval 6 month
              or (percent_complete is not null and percent_complete < 100)
              or lower(coalesce(footnote, '')) like '%underreport%'
              or lower(coalesce(footnote, '')) like '%incomplete%'
          )
      )
      and (
          headline_basis <> 'reported'
          or headline_deaths <> rolling_12_month_deaths
      )
)

select state, month from flagged
union all
select state, month from reported_only
  
  
      
    ) dbt_internal_test