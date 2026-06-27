-- Staging model for Census Population Estimates Program (PEP) data
-- This model cleans and standardizes state-level population data from US Census



with source_data as (
    select * from "fentanyl_awareness"."main"."census_state_population"
),

cleaned_data as (
    select
        -- Clean and standardize columns
        year
        , state_code
        , trim(state_name) as state_name
        , population
        , trim(date_description) as date_description
        , extracted_at

        -- Add derived fields
        , case
            when population > 0
                then true
            else false
          end as has_population_data

        -- Add data quality flags
        , case
            when population is null
                then 'missing'
            when population = 0
                then 'zero'
            when population < 1000000
                then 'low_population'
            else 'normal'
          end as population_quality_flag

    from source_data
)

select * from cleaned_data