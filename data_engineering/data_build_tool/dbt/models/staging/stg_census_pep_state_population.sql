-- July 1 resident population from the Census Population Estimates Program.

{{ config(
    materialized='view',
    order_by=['year', 'state_name']
) }}

with source_data as (
    select * from {{ source('census_raw', 'census_pep_state_population') }}
),

cleaned_data as (
    select
        cast(year as integer) as year
        , trim(state_name) as state_name
        , cast(population as bigint) as population
        , trim(vintage) as vintage
        , trim(population_source) as population_source
        , try_cast(extracted_at as timestamp) as extracted_at
    from source_data
)

select * from cleaned_data
