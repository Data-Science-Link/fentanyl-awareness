-- Provisional VSRR T40.4 12-month ending counts.
-- Rates use Census PEP July 1 population. ACS stays on income and unemployment.
-- New York City has no PEP total, so its population stays null.
-- Jurisdictions with no VSRR row get an explicit not_reportable row.
-- headline_deaths uses CDC predicted counts for recent or flagged months.

{{ config(
    materialized='view'
    , order_by=['year', 'month', 'state']
    , post_hook=[
        """
        COPY (SELECT * FROM {{ this }} ORDER BY year, month, state)
        TO '../../Final_Datasets/fact_fentanyl_deaths_over_time.csv'
        (HEADER, DELIMITER ',')
        """
    ]
) }}

with stg_census_pep_state_population as (
    select
        year
        , state_name as state
        , population
        , population_source
    from {{ ref('stg_census_pep_state_population') }}
),

stg_census_state_population as (
    select
        year
        , state_name as state
        , population
    from {{ ref('stg_census_state_population') }}
),

stg_census_state_economic as (
    select
        year
        , state_name as state
        , median_household_income
        , unemployment_rate
    from {{ ref('stg_census_state_economic') }}
),

api_data as (
    select
        year
        , month
        , state
        , geo_type
        , rolling_12_month_deaths
        , predicted_12_month_deaths
        , is_suppressed
        , footnote
        , footnote_symbol
        , percent_complete
        , percent_pending_investigation
        , extracted_at
        , 'CDC SODA API' as data_source
        , case
            when is_suppressed then 'suppressed'
            else 'reported'
          end as reporting_status
    from {{ ref('stg_cdc_api_provisional_overdose_counts') }}
),

latest as (
    select max(month) as max_month
    from api_data
),

expected_states(state) as (
    values
        ('Alabama'), ('Alaska'), ('Arizona'), ('Arkansas'), ('California'),
        ('Colorado'), ('Connecticut'), ('Delaware'), ('District of Columbia'),
        ('Florida'), ('Georgia'), ('Hawaii'), ('Idaho'), ('Illinois'),
        ('Indiana'), ('Iowa'), ('Kansas'), ('Kentucky'), ('Louisiana'),
        ('Maine'), ('Maryland'), ('Massachusetts'), ('Michigan'), ('Minnesota'),
        ('Mississippi'), ('Missouri'), ('Montana'), ('Nebraska'), ('Nevada'),
        ('New Hampshire'), ('New Jersey'), ('New Mexico'), ('New York'),
        ('North Carolina'), ('North Dakota'), ('Ohio'), ('Oklahoma'),
        ('Oregon'), ('Pennsylvania'), ('Rhode Island'), ('South Carolina'),
        ('South Dakota'), ('Tennessee'), ('Texas'), ('Utah'), ('Vermont'),
        ('Virginia'), ('Washington'), ('West Virginia'), ('Wisconsin'),
        ('Wyoming')
),

months as (
    select distinct year, month
    from api_data
),

not_reportable as (
    select
        months.year
        , months.month
        , expected_states.state
        , 'state' as geo_type
        , cast(null as integer) as rolling_12_month_deaths
        , cast(null as integer) as predicted_12_month_deaths
        , false as is_suppressed
        , 'CDC VSRR does not publish T40.4 for this jurisdiction.' as footnote
        , cast(null as varchar) as footnote_symbol
        , cast(null as double) as percent_complete
        , cast(null as double) as percent_pending_investigation
        , (select max(extracted_at) from api_data) as extracted_at
        , 'CDC SODA API' as data_source
        , 'not_reportable' as reporting_status
    from months
    cross join expected_states
    left join api_data
        on months.year = api_data.year
        and months.month = api_data.month
        and expected_states.state = api_data.state
    where api_data.state is null
),

combined as (
    select * from api_data
    union all
    select * from not_reportable
),

matched_pep as (
    select
        year
        , month
        , state
        , population
        , population_year
        , population_source
    from (
        select
            combined.year
            , combined.month
            , combined.state
            , pop.population
            , pop.year as population_year
            , pop.population_source
            , row_number() over (
                partition by combined.year, combined.month, combined.state
                order by
                    case
                        when pop.year is null then 2
                        when pop.year <= combined.year then 0
                        else 1
                    end
                    , case when pop.year <= combined.year then pop.year end desc
                    , pop.year asc
            ) as population_rank
        from combined
        left join stg_census_pep_state_population as pop
            on combined.state = pop.state
            and combined.geo_type <> 'city'
    )
    where population_rank = 1
),

matched_acs as (
    select
        year
        , month
        , state
        , population
        , population_year
    from (
        select
            combined.year
            , combined.month
            , combined.state
            , acs.population
            , acs.year as population_year
            , row_number() over (
                partition by combined.year, combined.month, combined.state
                order by
                    case
                        when acs.year is null then 1
                        when acs.year <= combined.year then 0
                        else 1
                    end
                    , acs.year desc
            ) as population_rank
        from combined
        left join stg_census_state_population as acs
            on combined.state = acs.state
            and combined.geo_type = 'city'
    )
    where population_rank = 1
),

matched_economic as (
    select
        year
        , month
        , state
        , median_household_income
        , unemployment_rate
        , demographics_year
    from (
        select
            combined.year
            , combined.month
            , combined.state
            , econ.median_household_income
            , econ.unemployment_rate
            , econ.year as demographics_year
            , row_number() over (
                partition by combined.year, combined.month, combined.state
                order by
                    case
                        when econ.year is null then 1
                        when econ.year <= combined.year then 0
                        else 1
                    end
                    , econ.year desc
            ) as economics_rank
        from combined
        left join stg_census_state_economic as econ
            on combined.state = econ.state
    )
    where economics_rank = 1
),

with_population as (
    select
        combined.*
        , case
            when combined.geo_type = 'city' then matched_acs.population
            else matched_pep.population
          end as population
        , case
            when combined.geo_type = 'city' then matched_acs.population_year
            else matched_pep.population_year
          end as population_year
        , case
            when combined.geo_type = 'city' and matched_acs.population is not null
                then 'ACS 5-year'
            when combined.geo_type <> 'city' and matched_pep.population is not null
                then matched_pep.population_source
          end as population_source
        , matched_economic.median_household_income
        , matched_economic.unemployment_rate
        , matched_economic.demographics_year
    from combined
    left join matched_pep
        on combined.year = matched_pep.year
        and combined.month = matched_pep.month
        and combined.state = matched_pep.state
    left join matched_acs
        on combined.year = matched_acs.year
        and combined.month = matched_acs.month
        and combined.state = matched_acs.state
    left join matched_economic
        on combined.year = matched_economic.year
        and combined.month = matched_economic.month
        and combined.state = matched_economic.state
),

final_format as (
    select
        year
        , month
        , state
        , geo_type
        , rolling_12_month_deaths
        , predicted_12_month_deaths
        , case
            when predicted_12_month_deaths is not null
                and (
                    month >= (select max_month from latest) - interval 6 month
                    or (percent_complete is not null and percent_complete < 100)
                    or lower(coalesce(footnote, '')) like '%underreport%'
                    or lower(coalesce(footnote, '')) like '%incomplete%'
                )
                then predicted_12_month_deaths
            else rolling_12_month_deaths
          end as headline_deaths
        , case
            when predicted_12_month_deaths is not null
                and (
                    month >= (select max_month from latest) - interval 6 month
                    or (percent_complete is not null and percent_complete < 100)
                    or lower(coalesce(footnote, '')) like '%underreport%'
                    or lower(coalesce(footnote, '')) like '%incomplete%'
                )
                then 'predicted'
            when rolling_12_month_deaths is not null or reporting_status = 'reported'
                then 'reported'
          end as headline_basis
        , is_suppressed
        , reporting_status
        , footnote
        , footnote_symbol
        , percent_complete
        , percent_pending_investigation
        , data_source
        , population
        , population_year
        , population_source
        , median_household_income
        , unemployment_rate
        , demographics_year
        , case
            when rolling_12_month_deaths is not null and population > 0
                then round(rolling_12_month_deaths * 100000.0 / population, 2)
          end as deaths_per_100k
        , case
            when predicted_12_month_deaths is not null and population > 0
                then round(predicted_12_month_deaths * 100000.0 / population, 2)
          end as predicted_deaths_per_100k
        , (
            population_year is not null
            and population_year <> year
          ) as population_is_carried_forward
        , extracted_at
    from with_population
)

select * from final_format
