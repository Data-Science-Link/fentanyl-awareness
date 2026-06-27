
  
  create view "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts__dbt_tmp" as (
    -- Staging model for CDC API Provisional Overdose Counts
-- This model cleans and standardizes the data from the CDC SODA API



with source_data as (
    select * from "fentanyl_awareness"."main"."cdc_api_provisional_overdose_counts"
),

cleaned_data as (
    select
        -- Ensure year is an integer
        cast(year as integer) as year

        -- Convert month name and year to a proper date
        -- The API provides "January", "February", etc. and a "year"
        -- We'll assume the first day of the month
        , case
            when month = 'January' then strptime(year || '-01-01', '%Y-%m-%d')::date
            when month = 'February' then strptime(year || '-02-01', '%Y-%m-%d')::date
            when month = 'March' then strptime(year || '-03-01', '%Y-%m-%d')::date
            when month = 'April' then strptime(year || '-04-01', '%Y-%m-%d')::date
            when month = 'May' then strptime(year || '-05-01', '%Y-%m-%d')::date
            when month = 'June' then strptime(year || '-06-01', '%Y-%m-%d')::date
            when month = 'July' then strptime(year || '-07-01', '%Y-%m-%d')::date
            when month = 'August' then strptime(year || '-08-01', '%Y-%m-%d')::date
            when month = 'September' then strptime(year || '-09-01', '%Y-%m-%d')::date
            when month = 'October' then strptime(year || '-10-01', '%Y-%m-%d')::date
            when month = 'November' then strptime(year || '-11-01', '%Y-%m-%d')::date
            when month = 'December' then strptime(year || '-12-01', '%Y-%m-%d')::date
          end as month

        , trim(state_name) as state
        , trim(indicator) as multiple_cause_of_death
        , 'T40.4' as multiple_cause_of_death_code

        -- Handle nulls in data_value
        -- This represents the 12-month rolling total of deaths ending in the given month
        , coalesce(cast(data_value as integer), 0) as rolling_12_month_deaths

    from source_data
    -- The API includes "12 month-ending" and "Monthly" periods sometimes.
    -- Looking at the data, '12 month-ending' is the common one for these counts.
    where period = '12 month-ending'
)

select * from cleaned_data
  );
