-- Fact table for CDC Fentanyl Deaths
-- This model now uses the CDC SODA API as the single source of truth for fentanyl deaths

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
        , deaths
        , 'CDC SODA API' as data_source
    from {{ ref('stg_cdc_api_provisional_overdose_counts') }}
),

-- Final format with census data
final_format as (
    select
        api_data.year
        , api_data.month
        , api_data.state
        , api_data.deaths
        , api_data.data_source
        , stg_census_state_population.population
        , stg_census_state_economic.median_household_income
        , stg_census_state_economic.unemployment_rate
    from api_data
    left join stg_census_state_population
        on api_data.year = stg_census_state_population.year
        and api_data.state = stg_census_state_population.state
    left join stg_census_state_economic
        on api_data.year = stg_census_state_economic.year
        and api_data.state = stg_census_state_economic.state
)

select * from final_format
