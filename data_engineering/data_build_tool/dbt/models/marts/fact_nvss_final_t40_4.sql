-- Final NVSS incident deaths for T40.4 drug overdoses.
-- Kept separate from the VSRR rolling series. Do not add these rows to
-- rolling_12_month_deaths.

{{ config(
    materialized='view'
    , order_by=['year', 'state', 'period_type']
    , post_hook=[
        """
        COPY (SELECT * FROM {{ this }} ORDER BY period_type, year, month, state)
        TO '../../Final_Datasets/fact_nvss_final_t40_4.csv'
        (HEADER, DELIMITER ',')
        """
    ]
) }}

select
    year
    , month
    , state
    , geo_type
    , period_type
    , incident_deaths
    , is_suppressed
    , data_source
    , source_dataset
    , extracted_at
from {{ ref('stg_nvss_final_t40_4') }}
