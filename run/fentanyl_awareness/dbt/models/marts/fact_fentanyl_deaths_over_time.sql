
  
  create view "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time__dbt_tmp" as (
    -- Fact table for CDC WONDER Fentanyl Deaths
-- This model unions all CDC WONDER data sources and prioritizes older, more reliable data



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

wonder_data_union as (
    -- Union all CDC WONDER data sources (union all since no duplicates expected)
    select
        year
        , month
        , state
        , deaths
        , 'Official 1999-2020' as data_source
        , 1 as priority
    from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_final_1999_2020"

    union all

    select
        year
        , month
        , state
        , deaths
        , 'Official 2018-2023' as data_source
        , 2 as priority
    from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_final_2018_2023"

    union all

    select
        year
        , month
        , state
        , deaths
        , 'Provisional 2018-current' as data_source
        , 3 as priority
    from "fentanyl_awareness"."main"."stg_cdc_wonder_fentanyl_deaths_provisional_2018_current"
),

-- Remove duplicates based on primary keys (year, month, state)
-- Prioritize older data sources (lower priority number = higher priority)
deduplicated_data as (
    select
        year
        , month
        , state
        , deaths
        , data_source
        , priority
        , row_number() over (
            partition by year, month, state
            order by priority asc
        ) as row_num
    from wonder_data_union
),

-- Final format with coalesced deaths, prioritized data source, and census data
final_format as (
    select
        deduplicated_data.year
        , deduplicated_data.month
        , deduplicated_data.state
        , coalesce(deduplicated_data.deaths, 0) as deaths
        , deduplicated_data.data_source
        , stg_census_state_population.population
        , stg_census_state_economic.median_household_income
        , stg_census_state_economic.unemployment_rate
    from deduplicated_data
    left join stg_census_state_population
        on deduplicated_data.year = stg_census_state_population.year
        and deduplicated_data.state = stg_census_state_population.state
    left join stg_census_state_economic
        on deduplicated_data.year = stg_census_state_economic.year
        and deduplicated_data.state = stg_census_state_economic.state
    where deduplicated_data.row_num = 1  -- Keep only the highest priority record for each key
)

select * from final_format
  );
