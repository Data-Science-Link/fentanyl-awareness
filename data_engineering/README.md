# Data Engineering

Technical infrastructure for the Fentanyl Awareness Project. The pipeline extracts CDC VSRR T40.4 counts and Census ACS 5-year estimates, then publishes one fact table.

## Contents

- `data_sources/cdc_api/soda_extractor.py` — CDC SODA extract
- `data_sources/census_acs/census_extractor.py` — Census ACS extract
- `data_build_tool/` — dbt project (DuckDB)
  - `dbt/models/staging/` — cleaning
  - `dbt/models/marts/` — published fact table
  - `dbt/seeds/` — versioned extracts
  - `dbt/tests/` — extra data-quality tests

CDC WONDER and Google Sheets are not part of this pipeline.

## Setup

Python 3.10+ is required.

```bash
pip install -r requirements.txt
cp ../.env.example ../.env   # add CENSUS_API_KEY to refresh ACS seeds
```

Create a DuckDB profile at `~/.dbt/profiles.yml`:

```yaml
fentanyl_awareness:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: 'fentanyl_awareness.duckdb'
      threads: 4
      schema: 'main'
```

```bash
python data_sources/cdc_api/soda_extractor.py
python data_sources/census_acs/census_extractor.py   # optional without a key
cd data_build_tool
dbt deps --profiles-dir ~/.dbt
dbt seed --profiles-dir ~/.dbt
dbt run --profiles-dir ~/.dbt
dbt test --profiles-dir ~/.dbt
```

The fact model writes `../Final_Datasets/fact_fentanyl_deaths_over_time.csv`.

## Models

- `stg_cdc_api_provisional_overdose_counts` — T40.4 12-month ending rows; suppressed counts stay null
- `stg_census_state_population` — ACS 5-year population
- `stg_census_state_economic` — ACS 5-year income and unemployment
- `fact_fentanyl_deaths_over_time` — published table with `geo_type`, rates, and CDC footnotes

## Query notes

```sql
-- Latest national 12-month ending count
SELECT month, rolling_12_month_deaths
FROM main.fact_fentanyl_deaths_over_time
WHERE geo_type = 'nation'
ORDER BY month DESC
LIMIT 1;

-- Latest state rates (do not include nation / NYC / PR)
SELECT state, deaths_per_100k, rolling_12_month_deaths
FROM main.fact_fentanyl_deaths_over_time
WHERE geo_type = 'state'
  AND month = (SELECT max(month) FROM main.fact_fentanyl_deaths_over_time)
  AND is_suppressed = false
ORDER BY deaths_per_100k DESC;
```

Do not `SUM(rolling_12_month_deaths)` across months. That metric is already a 12-month window.

## Automation

- **dbt CI**: seeds, models, dbt tests, Python tests, Pages deploy from `main`
- **Weekly refresh**: re-extract CDC (and Census when `CENSUS_API_KEY` is set), rebuild, deploy Pages, force-push `automated/weekly-data-refresh`. Opening the PR needs Settings → Actions → "Allow GitHub Actions to create and approve pull requests" or secret `WEEKLY_REFRESH_TOKEN`
- **Security audit**: Bandit and pip-audit

## Tests

```bash
cd data_build_tool && dbt test --profiles-dir ~/.dbt
cd ../.. && python -m pytest tests
```

dbt tests include uniqueness, accepted `geo_type` values, core-state coverage (Louisiana is a documented source gap), a national row in the latest month, and suppressed deaths remaining null.
