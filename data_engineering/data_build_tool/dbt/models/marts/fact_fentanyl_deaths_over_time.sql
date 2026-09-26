-- Fact table for provisional T40.4 (synthetic opioid) 12-month ending counts.
-- Census ACS 5-year attributes are joined to the latest year that is on or
-- before the death-year label so 2024+ rows can still compute rates.

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

with stg_census_state_population as (
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
    from {{ ref('stg_cdc_api_provisional_overdose_counts') }}
),

matched_population as (
    select
        api_data.year
        , api_data.month
        , api_data.state
        , pop.population
        , pop.year as population_year
    from api_data
    left join stg_census_state_population as pop
        on api_data.state = pop.state
        and pop.year = (
            select max(older.year)
            from stg_census_state_population as older
            where older.state = api_data.state
              and older.year <= api_data.year
        )
),

matched_economic as (
    select
        api_data.year
        , api_data.month
        , api_data.state
        , econ.median_household_income
        , econ.unemployment_rate
        , econ.year as demographics_year
    from api_data
    left join stg_census_state_economic as econ
        on api_data.state = econ.state
        and econ.year = (
            select max(older.year)
            from stg_census_state_economic as older
            where older.state = api_data.state
              and older.year <= api_data.year
        )
),

final_format as (
    select
        api_data.year
        , api_data.month
        , api_data.state
        , api_data.geo_type
        , api_data.rolling_12_month_deaths
        , api_data.predicted_12_month_deaths
        , api_data.is_suppressed
        , api_data.footnote
        , api_data.footnote_symbol
        , api_data.percent_complete
        , api_data.percent_pending_investigation
        , api_data.data_source
        , matched_population.population
        , matched_population.population_year
        , matched_economic.median_household_income
        , matched_economic.unemployment_rate
        , matched_economic.demographics_year
        , case
            when api_data.rolling_12_month_deaths is not null
                and matched_population.population > 0
                then round(
                    api_data.rolling_12_month_deaths * 100000.0
                    / matched_population.population
                    , 2
                )
          end as deaths_per_100k
        , case
            when api_data.predicted_12_month_deaths is not null
                and matched_population.population > 0
                then round(
                    api_data.predicted_12_month_deaths * 100000.0
                    / matched_population.population
                    , 2
                )
          end as predicted_deaths_per_100k
        , (matched_population.population_year is not null
            and matched_population.population_year < api_data.year) as population_is_carried_forward
        , api_data.extracted_at
    from api_data
    left join matched_population
        on api_data.year = matched_population.year
        and api_data.month = matched_population.month
        and api_data.state = matched_population.state
    left join matched_economic
        on api_data.year = matched_economic.year
        and api_data.month = matched_economic.month
        and api_data.state = matched_economic.state
)

select * from final_format
