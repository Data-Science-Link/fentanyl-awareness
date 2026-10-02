-- One national series of deaths in each month.
-- Final NVSS months are the count on the death certificate.
-- Later months are estimated from the change in the provisional
-- 12-month total plus the count 12 months earlier.
-- See docs/methods/monthly_deaths.md.

{{ config(
    materialized='table'
    , post_hook=[
        """
        COPY (
            SELECT
                strftime(month, '%Y-%m') AS {{ adapter.quote('Month') }}
                , estimated_deaths AS {{ adapter.quote('Estimated deaths') }}
                , how_produced AS {{ adapter.quote('How this number was produced') }}
                , deaths_per_100k AS {{ adapter.quote('Deaths per 100,000') }}
                , change_from_previous_month AS {{ adapter.quote('Change from the previous month') }}
                , change_from_year_earlier AS {{ adapter.quote('Change from the same month a year earlier') }}
                , change_in_12_month_total AS {{ adapter.quote('Change in the 12-month total') }}
                , official_actions AS {{ adapter.quote('Official actions that month') }}
                , source AS {{ adapter.quote('Source') }}
                , note AS {{ adapter.quote('Note') }}
            FROM {{ this }}
            ORDER BY month
        )
        TO '../../Final_Datasets/deaths_by_month.csv'
        (HEADER, DELIMITER ',')
        """
    ]
) }}

with recursive headline as (
    select
        cast(month as date) as month
        , headline_deaths
    from {{ ref('fact_fentanyl_deaths_over_time') }}
    where geo_type = 'nation'
      and headline_deaths is not null
),

headline_lag as (
    select
        month
        , headline_deaths
        , case
            when lag(month) over (order by month) = month - interval 1 month
                then headline_deaths - lag(headline_deaths) over (order by month)
          end as change_in_12_month_total
    from headline
),

final_months as (
    select
        cast(month as date) as month
        , incident_deaths as deaths
    from {{ ref('fact_nvss_final_t40_4') }}
    where geo_type = 'nation'
      and period_type = 'month'
      and is_suppressed = false
      and incident_deaths is not null
),

pep as (
    select
        year
        , population
    from {{ ref('stg_census_pep_state_population') }}
    where state_name = 'United States'
),

built as (
    select
        final_months.month
        , final_months.deaths as estimated_deaths
        , 'Official final count' as how_produced
        , headline_lag.change_in_12_month_total
        , false as is_negative_estimate
        , 0 as step
    from final_months
    left join headline_lag
        on final_months.month = headline_lag.month

    union all

    select
        headline_lag.month
        , headline_lag.change_in_12_month_total + built.estimated_deaths as estimated_deaths
        , 'Estimated from the change in the 12-month total' as how_produced
        , headline_lag.change_in_12_month_total
        , (headline_lag.change_in_12_month_total + built.estimated_deaths) < 0 as is_negative_estimate
        , built.step + 1 as step
    from built
    inner join headline_lag
        on headline_lag.month = built.month + interval 12 month
    where headline_lag.change_in_12_month_total is not null
      and built.step < 24
      and not exists (
          select 1
          from final_months
          where final_months.month = headline_lag.month
      )
),

monthly as (
    select
        month
        , estimated_deaths
        , how_produced
        , change_in_12_month_total
        , is_negative_estimate
    from built
),

with_population as (
    select
        monthly.*
        , pop.population
        , pop.population_year
    from monthly
    left join lateral (
        select
            pep.population
            , pep.year as population_year
        from pep
        where pep.year <= year(monthly.month)
           or pep.year = (select min(year) from pep)
        order by
            case when pep.year <= year(monthly.month) then 0 else 1 end
            , case when pep.year <= year(monthly.month) then pep.year end desc
            , pep.year
        limit 1
    ) as pop on true
),

with_changes as (
    select
        with_population.*
        , case
            when lag(month) over (order by month) = month - interval 1 month
                then estimated_deaths - lag(estimated_deaths) over (order by month)
          end as change_from_previous_month
        , estimated_deaths - lag(estimated_deaths, 12) over (order by month) as change_from_year_earlier_raw
        , lag(month, 12) over (order by month) as month_one_year_earlier
    from with_population
),

actions as (
    select
        cast(date_trunc('month', cast(action_date as date)) as date) as month
        , string_agg(title, '; ' order by action_date, title) as official_actions
    from {{ ref('policy_actions') }}
    group by 1
)

select
    with_changes.month
    , year(with_changes.month) as year
    , with_changes.estimated_deaths
    , with_changes.how_produced
    , case
        when with_changes.estimated_deaths >= 0 and with_changes.population > 0
            then round(with_changes.estimated_deaths * 100000.0 / with_changes.population, 2)
      end as deaths_per_100k
    , with_changes.change_from_previous_month
    , case
        when with_changes.month_one_year_earlier = with_changes.month - interval 12 month
            then with_changes.change_from_year_earlier_raw
      end as change_from_year_earlier
    , with_changes.change_in_12_month_total
    , actions.official_actions
    , case
        when with_changes.how_produced = 'Official final count'
            then 'CDC WONDER final multiple-cause death data'
        else 'CDC provisional 12-month totals, plus an earlier month in this file'
      end as source
    , concat_ws(
        ' '
        , case
            when with_changes.how_produced = 'Official final count'
                then 'Deaths recorded on final death certificates for this month. The count is synthetic opioids other than methadone, a group that includes fentanyl and is not fentanyl alone.'
            else 'CDC has not published a final count for this month. Estimated as the change in the 12-month total plus deaths from the same month one year earlier.'
          end
        , case
            when with_changes.is_negative_estimate
                then 'This estimate is below zero because provisional totals were revised. It is not a count of deaths.'
          end
        , case
            when with_changes.population_year is not null
                and with_changes.population_year <> year(with_changes.month)
                then 'Population is the July 1 ' || with_changes.population_year || ' Census estimate.'
          end
    ) as note
    , with_changes.is_negative_estimate
    , with_changes.population
    , with_changes.population_year
from with_changes
left join actions
    on with_changes.month = actions.month
