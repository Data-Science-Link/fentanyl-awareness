
  
  create view "fentanyl_awareness"."main"."stg_cdc_api_provisional_overdose_counts__dbt_tmp" as (
    -- Staging model for CDC VSRR provisional T40.4 counts.
-- Empty CDC data_value cells stay null (suppressed / not shown), never zero.



with source_data as (
    select * from "fentanyl_awareness"."main"."cdc_api_provisional_overdose_counts"
),

cleaned_data as (
    select
        cast(year as integer) as year
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
        , case
            when trim(state_name) = 'United States' then 'nation'
            when trim(state_name) = 'New York City' then 'city'
            when trim(state_name) = 'Puerto Rico' then 'territory'
            else 'state'
          end as geo_type
        , trim(indicator) as multiple_cause_of_death
        , 'T40.4' as multiple_cause_of_death_code
        , try_cast(data_value as integer) as rolling_12_month_deaths
        , try_cast(predicted_value as integer) as predicted_12_month_deaths
        , case
            when data_value is null or trim(cast(data_value as varchar)) = ''
                then true
            else false
          end as is_suppressed
        , nullif(trim(footnote), '') as footnote
        , nullif(trim(footnote_symbol), '') as footnote_symbol
        , try_cast(percent_complete as double) as percent_complete
        , try_cast(percent_pending_investigation as double) as percent_pending_investigation
        , try_cast(extracted_at as timestamp) as extracted_at
    from source_data
    where period = '12 month-ending'
)

select * from cleaned_data
  );
