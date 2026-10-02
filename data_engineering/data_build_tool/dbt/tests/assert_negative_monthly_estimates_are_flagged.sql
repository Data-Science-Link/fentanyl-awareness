select month
from {{ ref('fact_deaths_by_month') }}
where estimated_deaths < 0
  and is_negative_estimate = false
