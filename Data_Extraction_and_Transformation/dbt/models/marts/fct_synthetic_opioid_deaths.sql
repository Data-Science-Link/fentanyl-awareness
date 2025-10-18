-- Final mart model combining all CDC WONDER synthetic opioid mortality datasets
-- This model creates a unified view of synthetic opioid deaths across all time periods

{{ config(materialized='table') }}

with d77_data as (
    select * from {{ ref('stg_d77_official_1999_2020') }}
),

d157_data as (
    select * from {{ ref('stg_d157_official_2018_2023') }}
),

d176_data as (
    select * from {{ ref('stg_d176_provisional_2023_current') }}
),

-- Combine all datasets using UNION ALL
combined_data as (
    select * from d77_data
    union all
    select * from d157_data
    union all
    select * from d176_data
),

-- Add additional analytical fields
enriched_data as (
    select
        *,
        
        -- Add time period categorization
        case 
            when year between 1999 and 2020 then 'Historical (1999-2020)'
            when year between 2018 and 2023 then 'Recent Official (2018-2023)'
            when year >= 2023 then 'Provisional (2023+)'
            else 'Unknown Period'
        end as time_period_category,
        
        -- Add decade grouping
        case 
            when year between 1999 and 1999 then '1990s'
            when year between 2000 and 2009 then '2000s'
            when year between 2010 and 2019 then '2010s'
            when year between 2020 and 2029 then '2020s'
            else 'Other'
        end as decade,
        
        -- Add data quality score
        case 
            when deaths > 0 and population > 0 and crude_rate > 0 then 'High Quality'
            when deaths > 0 and population > 0 then 'Medium Quality'
            when deaths = 0 and population > 0 then 'Zero Deaths'
            when population = 0 then 'No Population Data'
            else 'Low Quality'
        end as data_quality_score,
        
        -- Add population size categories
        case 
            when population = 0 then 'No Data'
            when population < 10000 then 'Small (<10K)'
            when population < 100000 then 'Medium (10K-100K)'
            when population < 1000000 then 'Large (100K-1M)'
            else 'Very Large (1M+)'
        end as population_size_category,
        
        -- Add death rate categories
        case 
            when crude_rate = 0 then 'No Deaths'
            when crude_rate < 5 then 'Low (<5)'
            when crude_rate < 10 then 'Moderate (5-10)'
            when crude_rate < 20 then 'High (10-20)'
            else 'Very High (20+)'
        end as death_rate_category,
        
        -- Add current timestamp for data freshness tracking
        current_timestamp as data_loaded_at
        
    from combined_data
),

-- Final output with deduplication and sorting
final as (
    select
        year,
        state,
        county,
        deaths,
        population,
        crude_rate,
        age_adjusted_rate,
        calculated_crude_rate,
        dataset_code,
        dataset_description,
        time_period_category,
        decade,
        data_quality_score,
        population_size_category,
        death_rate_category,
        has_zero_deaths,
        has_zero_population,
        data_loaded_at
        
    from enriched_data
    
    -- Remove duplicates based on year, state, county, and dataset
    qualify row_number() over (
        partition by year, state, county, dataset_code 
        order by data_loaded_at desc
    ) = 1
    
    order by year desc, state, county
)

select * from final
