-- Staging model for D77 Official 1999-2020 data
-- This model cleans and standardizes the raw CDC WONDER data

{{ config(materialized='view') }}

with source_data as (
    select * from {{ source('cdc_wonder_raw', 'd77_official_1999_2020') }}
),

cleaned_data as (
    select
        -- Standardize year format
        cast(year as integer) as year,
        
        -- Clean state names
        trim(upper(state)) as state,
        
        -- Clean county names (remove extra spaces, handle nulls)
        case 
            when county is null or county = '' then 'Unknown'
            else trim(county)
        end as county,
        
        -- Convert deaths to integer, handle missing values
        case 
            when deaths = '' or deaths is null then 0
            else cast(deaths as integer)
        end as deaths,
        
        -- Convert population to integer, handle missing values
        case 
            when population = '' or population is null then 0
            else cast(population as integer)
        end as population,
        
        -- Convert rates to decimal, handle missing values
        case 
            when crude_rate = '' or crude_rate is null then 0.0
            else cast(crude_rate as decimal(10,2))
        end as crude_rate,
        
        case 
            when age_adjusted_rate = '' or age_adjusted_rate is null then 0.0
            else cast(age_adjusted_rate as decimal(10,2))
        end as age_adjusted_rate,
        
        -- Add data source identifier
        'D77' as dataset_code,
        'Official 1999-2020' as dataset_description
        
    from source_data
),

final as (
    select
        *,
        -- Calculate additional metrics
        case 
            when population > 0 then round((deaths::decimal / population) * 100000, 2)
            else 0.0
        end as calculated_crude_rate,
        
        -- Add data quality flags
        case 
            when deaths = 0 and population > 0 then true
            else false
        end as has_zero_deaths,
        
        case 
            when population = 0 then true
            else false
        end as has_zero_population
        
    from cleaned_data
)

select * from final
