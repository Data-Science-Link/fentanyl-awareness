-- Staging model for D176 Provisional 2018-Current data
-- This model cleans and standardizes the raw CDC WONDER data

{{ config(materialized='table') }}

with source_data as (
    select * from {{ source('cdc_wonder_raw', 'd176_provisional_2018_current') }}
),

cleaned_data as (
    select
        -- Clean and standardize columns
        notes,
        trim("Year") as year,
        "Year Code" as year_code,
        trim("Month") as month,
        trim("Month Code") as month_code,
        trim("Residence State") as residence_state,
        "Residence State Code" as residence_state_code,
        trim("Multiple Cause of death") as multiple_cause_of_death,
        trim("Multiple Cause of death Code") as multiple_cause_of_death_code,
        
        -- Deaths is already an integer, just handle nulls
        case 
            when "Deaths" is null then 0
            else "Deaths"
        end as deaths,
        
        -- Handle population column (often "Not Applicable")
        case 
            when "Population" = 'Not Applicable' or "Population" = '' or "Population" is null then null
            else cast("Population" as integer)
        end as population,
        
        -- Handle crude rate column (often "Not Applicable")
        case 
            when "Crude Rate" = 'Not Applicable' or "Crude Rate" = '' or "Crude Rate" is null then null
            else cast("Crude Rate" as decimal(10,2))
        end as crude_rate
        
    from source_data
)

select * from cleaned_data
