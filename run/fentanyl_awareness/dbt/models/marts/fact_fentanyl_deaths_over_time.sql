
  
  create view "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time__dbt_tmp" as (
    -- Fact table for CDC Fentanyl Deaths
-- This model now uses the CDC SODA API as the single source of truth for fentanyl deaths



with stg_census_state_population as (
    select
        year
        , state_name as state
        , population
    from "fentanyl_awareness"."main"."stg_census_state_population"
),

stg_census_state_economic as (
    select
        year
        , state_name as state
        , median_household_income
        , unemployment_rate
    from "fentanyl_awareness"."main"."stg_census_state_economic"
),

api_data as (
    select
        year
        , month
        , state
        , rolling_12_month_deaths
        , 'CDC SODA API' as data_source
    from "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts"
),

-- Final format with census data
final_format as (
    select
        api_data.year
        , api_data.month
        , api_data.state
        , api_data.rolling_12_month_deaths
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
  );
