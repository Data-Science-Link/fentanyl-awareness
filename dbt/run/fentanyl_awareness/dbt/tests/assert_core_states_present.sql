
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Every US state and DC must appear at least once, except documented CDC gaps.
with expected(state) as (
    values
        ('Alabama'), ('Alaska'), ('Arizona'), ('Arkansas'), ('California'),
        ('Colorado'), ('Connecticut'), ('Delaware'), ('District of Columbia'),
        ('Florida'), ('Georgia'), ('Hawaii'), ('Idaho'), ('Illinois'),
        ('Indiana'), ('Iowa'), ('Kansas'), ('Kentucky'), ('Louisiana'),
        ('Maine'), ('Maryland'), ('Massachusetts'), ('Michigan'), ('Minnesota'),
        ('Mississippi'), ('Missouri'), ('Montana'), ('Nebraska'), ('Nevada'),
        ('New Hampshire'), ('New Jersey'), ('New Mexico'), ('New York'),
        ('North Carolina'), ('North Dakota'), ('Ohio'), ('Oklahoma'),
        ('Oregon'), ('Pennsylvania'), ('Rhode Island'), ('South Carolina'),
        ('South Dakota'), ('Tennessee'), ('Texas'), ('Utah'), ('Vermont'),
        ('Virginia'), ('Washington'), ('West Virginia'), ('Wisconsin'),
        ('Wyoming')
),
excluded(state) as (
    values
        ('Louisiana')
),
actual as (
    select distinct state
    from "fentanyl_awareness"."main"."fact_fentanyl_deaths_over_time"
    where geo_type = 'state'
)

select expected.state as missing_state
from expected
left join excluded
    on expected.state = excluded.state
left join actual
    on expected.state = actual.state
where excluded.state is null
  and actual.state is null
  
  
      
    ) dbt_internal_test