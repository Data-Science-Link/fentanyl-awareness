# dbt transformations

dbt + DuckDB turn versioned CSV seeds into the published fact table.

## Run

```bash
dbt deps --profiles-dir ~/.dbt
dbt seed --profiles-dir ~/.dbt
dbt run --profiles-dir ~/.dbt
dbt test --profiles-dir ~/.dbt
dbt docs generate --profiles-dir ~/.dbt
```

`fact_fentanyl_deaths_over_time` copies itself to `../../Final_Datasets/fact_fentanyl_deaths_over_time.csv`.

## Models

- Staging: CDC T40.4 12-month ending rows; Census ACS population and economics
- Mart: one fact table with `geo_type`, suppression flags, predicted counts, and deaths per 100,000

## Tests

Schema tests plus:

- `assert_suppressed_deaths_are_null`
- `assert_latest_month_has_national_row`
- `assert_core_states_present` (Louisiana excluded as a documented CDC gap)

## Flow

```
CDC / Census seeds → staging views → fact view → Final_Datasets CSV
```
