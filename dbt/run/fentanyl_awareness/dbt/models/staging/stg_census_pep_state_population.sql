
  
  create view "fentanyl_awareness"."main"."stg_census_pep_state_population__dbt_tmp" as (
    -- July 1 resident population from the Census Population Estimates Program.



with source_data as (
    select * from "fentanyl_awareness"."main"."census_pep_state_population"
),

cleaned_data as (
    select
        cast(year as integer) as year
        , trim(state_name) as state_name
        , cast(population as bigint) as population
        , trim(vintage) as vintage
        , trim(population_source) as population_source
        , try_cast(extracted_at as timestamp) as extracted_at
    from source_data
)

select * from cleaned_data
  );
