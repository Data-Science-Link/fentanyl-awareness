-- Final NVSS incident deaths involving synthetic opioids other than methadone.
-- These rows are not 12-month ending VSRR counts.



with source_data as (
    select * from "fentanyl_awareness"."main"."nvss_final_t40_4_deaths"
),

cleaned_data as (
    select
        cast(year as integer) as year
        , try_cast(nullif(trim(cast(month as varchar)), '') as date) as month
        , trim(state) as state
        , trim(geo_type) as geo_type
        , trim(period_type) as period_type
        , try_cast(incident_deaths as integer) as incident_deaths
        , case
            when lower(cast(is_suppressed as varchar)) in ('true', 't', '1') then true
            else false
          end as is_suppressed
        , trim(data_source) as data_source
        , trim(source_dataset) as source_dataset
        , try_cast(extracted_at as timestamp) as extracted_at
    from source_data
)

select * from cleaned_data