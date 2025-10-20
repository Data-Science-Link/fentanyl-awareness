-- Fact table for CDC WONDER Fentanyl Deaths
-- This model unions all CDC WONDER data sources and prioritizes older, more reliable data

{{ config(
    materialized='table',
    order_by=['year', 'month', 'state']
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

wonder_data_union as (
    -- Union all CDC WONDER data sources (union all since no duplicates expected)
    select
        year
        , month
        , state
        , deaths
        , 'Official 1999-2020' as data_source
        , 1 as priority
    from {{ ref('stg_cdc_wonder_fentanyl_deaths_final_1999_2020') }}
    
    union all
    
    select
        year
        , month
        , state
        , deaths
        , 'Official 2018-2023' as data_source
        , 2 as priority
    from {{ ref('stg_cdc_wonder_fentanyl_deaths_final_2018_2023') }}
    
    union all
    
    select
        year
        , month
        , state
        , deaths
        , 'Provisional 2018-current' as data_source
        , 3 as priority
    from {{ ref('stg_cdc_wonder_fentanyl_deaths_provisional_2018_current') }}
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
        w.year
        , w.month
        , w.state
        , coalesce(w.deaths, 0) as deaths
        , w.data_source
        , p.population
        , e.median_household_income
        , e.unemployment_rate
    from deduplicated_data w
    left join census_population p
        on w.year = p.year
        and w.state = p.state
    left join census_economic e
        on w.year = e.year
        and w.state = e.state
    where w.row_num = 1  -- Keep only the highest priority record for each key
)

select * from final_format
