-- Staging model for CDC WONDER Fentanyl Deaths Final 1999-2020 data
-- This model cleans and standardizes the raw CDC WONDER data



with source_data as (
    select * from "fentanyl_awareness"."main"."multiple_cause_of_death_1999_2020_manual_download"
),

cleaned_data as (
    select
        -- Clean and standardize columns
        "Year Code" as year
        , strptime(trim("Month Code"), '%Y/%m')::date as month
        , trim("State") as state
        , trim("Multiple Cause of death") as multiple_cause_of_death
        , trim("Multiple Cause of death Code") as multiple_cause_of_death_code
        
        -- Deaths is already an integer, just handle nulls
        , case 
            when "Deaths" is null 
                then 0
            else "Deaths"
          end as deaths

        -- These columns are available in the raw data, but not needed for our analysis
        -- , notes -- Always null
        -- , trim("Year") as year -- String with (provisional and partial sometimes attached) (not needed as we will be prioritizing non-provisional data from other datasets in downstream datasets)
        -- , trim("Month") as month --Sting representation of the month (Jan., 2018, etc.)
        -- , "Residence State Code" as residence_state_code -- The integer state code is not needed for our analysis
        -- , population -- Almost always "Not Applicable". CDC Wonder attempts to anonymize the data when it is too granular (state, month, etc.)
        -- , crude_rate -- Almost always "Not Applicable". CDC Wonder attempts to anonymize the data when it is too granular (state, month, etc.)

        
    from source_data
)

select * from cleaned_data