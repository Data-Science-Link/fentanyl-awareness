
  
  create view "fentanyl_awareness"."main"."stg_census_state_economic__dbt_tmp" as (
    -- Staging model for Census Economic Data (ACS)
-- This model cleans and standardizes state-level economic data from US Census



with source_data as (
    select * from "fentanyl_awareness"."main"."census_state_economic"
),

cleaned_data as (
    select
        -- Clean and standardize columns
        year
        , state_code
        , trim(state_name) as state_name
        , median_household_income
        , per_capita_income
        , unemployment_rate
        , labor_force_total
        , employed
        , unemployed
        , extracted_at
        
        -- Add derived fields
        , case 
            when median_household_income > 0 
                then true
            else false
          end as has_income_data
        
        , case 
            when unemployment_rate is not null 
                then true
            else false
          end as has_employment_data
        
        -- Add data quality flags
        , case 
            when median_household_income is null 
                then 'missing'
            when median_household_income < 20000 
                then 'low_income'
            when median_household_income > 150000 
                then 'high_income'
            else 'normal'
          end as income_quality_flag
        
        , case 
            when unemployment_rate is null 
                then 'missing'
            when unemployment_rate < 2.0 
                then 'very_low'
            when unemployment_rate > 10.0 
                then 'very_high'
            else 'normal'
          end as unemployment_quality_flag
        
    from source_data
)

select * from cleaned_data
  );
