-- The newest month must include a United States (nation) row.
select 1 as missing_national_row
where not exists (
    select 1
    from {{ ref('fact_fentanyl_deaths_over_time') }}
    where geo_type = 'nation'
      and month = (
          select max(month)
          from {{ ref('fact_fentanyl_deaths_over_time') }}
      )
)
