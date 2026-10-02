-- One row per geography and month.
-- A finished month uses the final death certificate.
-- Months after the last final year keep CDC's preliminary 12-month total.
-- A single-month estimate is published only for the United States.
-- State months are not reconstructed, because CDC leaves some of them blank.
-- See docs/methods/monthly_deaths.md.

{{ config(
    materialized='table'
    , post_hook=[
        """
        COPY (
            SELECT
                year AS {{ adapter.quote('Year') }}
                , strftime(month, '%Y-%m') AS {{ adapter.quote('Month') }}
                , state AS {{ adapter.quote('State') }}
                , geo_type AS {{ adapter.quote('Geography') }}
                , deaths_in_month AS {{ adapter.quote('Deaths in the month') }}
                , confidence AS {{ adapter.quote('Confidence') }}
                , preliminary_12_month_total AS {{ adapter.quote('Preliminary 12-month total') }}
                , preliminary_basis AS {{ adapter.quote('Preliminary basis') }}
                , note AS {{ adapter.quote('Note') }}
                , source AS {{ adapter.quote('Source') }}
            FROM {{ this }}
            ORDER BY state, month
        )
        TO '../../Final_Datasets/deaths_by_state_month.csv'
        (HEADER, DELIMITER ',')
        """
    ]
) }}

with final as (
    select
        cast(month as date) as month
        , state
        , geo_type
        , incident_deaths
        , is_suppressed
    from {{ ref('fact_nvss_final_t40_4') }}
    where period_type = 'month'
      and month is not null
),

provisional as (
    select
        cast(month as date) as month
        , state
        , geo_type
        , headline_deaths
        , headline_basis
        , reporting_status
    from {{ ref('fact_fentanyl_deaths_over_time') }}
),

national as (
    select
        cast(month as date) as month
        , estimated_deaths
        , how_produced
        , is_negative_estimate
    from {{ ref('fact_deaths_by_month') }}
),

keys as (
    select month, state from final
    union
    select month, state from provisional
)

select
    year(keys.month) as year
    , keys.month
    , keys.state
    , coalesce(final.geo_type, provisional.geo_type) as geo_type
    , case
        when final.incident_deaths is not null then final.incident_deaths
        when keys.state = 'United States'
            and national.how_produced = 'Estimated from the change in the 12-month total'
            then national.estimated_deaths
      end as deaths_in_month
    , case
        when final.incident_deaths is not null then 'Final death certificate'
        when final.is_suppressed then 'Withheld by CDC'
        when keys.state = 'United States'
            and national.how_produced = 'Estimated from the change in the 12-month total'
            and national.is_negative_estimate
            then 'Preliminary estimate below zero'
        when keys.state = 'United States'
            and national.how_produced = 'Estimated from the change in the 12-month total'
            and national.estimated_deaths is not null
            then 'Preliminary estimate'
        else 'Not published as a single month'
      end as confidence
    , provisional.headline_deaths as preliminary_12_month_total
    , provisional.headline_basis as preliminary_basis
    , case
        when final.incident_deaths is not null and provisional.headline_deaths is not null
            then 'Final death certificate for this month. The preliminary column is CDC''s total for the 12 months ending this month. It is not a second count of the same deaths. The category is synthetic opioids other than methadone. It includes fentanyl and is not fentanyl alone.'
        when final.incident_deaths is not null
            then 'Final death certificate for this month. The category is synthetic opioids other than methadone. It includes fentanyl and is not fentanyl alone.'
        when final.is_suppressed
            then 'CDC withheld this monthly count. A blank is not a zero.'
        when keys.state = 'United States'
            and national.is_negative_estimate
            then 'The preliminary estimate is below zero because CDC revised a provisional total. It is not a count of deaths.'
        when keys.state = 'United States'
            and national.how_produced = 'Estimated from the change in the 12-month total'
            then 'CDC has not published a final count for this month. Deaths in the month are estimated from the change in the preliminary 12-month total plus the same month one year earlier. The preliminary column is the 12-month total, not the deaths in this month alone.'
        when provisional.reporting_status = 'not_reportable'
            then 'CDC does not publish this jurisdiction in the preliminary series. A blank is not a zero. Final months, when CDC has finished them, stay in this file.'
        when provisional.headline_deaths is not null
            then 'No final monthly count is available, and a single-month figure is not estimated for a state. The preliminary column is CDC''s total for the 12 months ending this month.'
        else 'CDC has not published a count for this month. A blank is not a zero.'
      end as note
    , case
        when final.incident_deaths is not null and provisional.headline_deaths is not null
            then 'CDC WONDER final death certificates; CDC VSRR preliminary 12-month total'
        when final.incident_deaths is not null or final.is_suppressed
            then 'CDC WONDER final death certificates'
        when keys.state = 'United States'
            and national.how_produced = 'Estimated from the change in the 12-month total'
            then 'CDC VSRR preliminary 12-month totals, plus an earlier month in this file'
        else 'CDC VSRR preliminary 12-month totals'
      end as source
from keys
left join final
    on keys.month = final.month
    and keys.state = final.state
left join provisional
    on keys.month = provisional.month
    and keys.state = provisional.state
left join national
    on keys.month = national.month
    and keys.state = 'United States'
