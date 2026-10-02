# Data Engineering

Technical infrastructure for the Fentanyl Awareness Project. The pipeline extracts CDC VSRR T40.4 counts, final WONDER deaths, Census population, CBP fentanyl seizure totals, the DEA memorial listing, and agency announcements. dbt publishes the provisional fact, the final fact, and a monthly death series.

## Contents

- `data_sources/cdc_api/soda_extractor.py` — CDC SODA extract
- `data_sources/nvss_wonder/wonder_extractor.py` — final T40.4 deaths
- `data_sources/nvss_wonder/wonder_demographics.py` — age, race, and drug-poisoning share
- `data_sources/census_pep/pep_extractor.py` — Census PEP population
- `data_sources/census_acs/census_extractor.py` — Census ACS income and unemployment
- `data_sources/cbp/cbp_extractor.py` — CBP fentanyl aggregates
- `data_sources/faces/faces_extractor.py` — DEA Faces of Fentanyl listing
- `data_sources/announcements/announcements_extractor.py` — agency releases
- `transforms/monthly_deaths.py` — the lag-difference formula, with Python tests
- `data_build_tool/` — dbt project (DuckDB)
  - `dbt/models/staging/` — cleaning
  - `dbt/models/marts/` — published facts, including `fact_deaths_by_month`
  - `dbt/seeds/` — versioned extracts. `docs/sources/` is also a seed path so `policy_actions` can join the monthly series
  - `dbt/tests/` — extra data-quality tests

Google Sheets are not part of this pipeline.

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

The fact models write `../Final_Datasets/fact_fentanyl_deaths_over_time.csv`, `../Final_Datasets/fact_nvss_final_t40_4.csv`, and `../Final_Datasets/deaths_by_month.csv`.

## Models

- `stg_cdc_api_provisional_overdose_counts` — T40.4 12-month ending rows; suppressed counts stay null
- `stg_census_state_population` — ACS 5-year population
- `stg_census_state_economic` — ACS 5-year income and unemployment
- `fact_fentanyl_deaths_over_time` — published table with `geo_type`, rates, and CDC footnotes
- `fact_nvss_final_t40_4` — final incident deaths
- `fact_deaths_by_month` — one national row per month. Final months stay official. Later months are estimated from the change in the 12-month total. The model writes `Final_Datasets/deaths_by_month.csv`

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

- **dbt CI**: seeds, models, dbt tests, and Python tests. Does not deploy Pages
- **Publish portal**: re-extract CDC, CBP, the DEA listing, and announcements (and Census ACS when `CENSUS_API_KEY` is set), rebuild, and deploy Pages. Runs Monday, on demand, and when website or pipeline changes merge to `main`. No pull request. A failed extract keeps the last seed when one exists
- **Security audit**: Bandit and pip-audit

## Tests

```bash
cd data_build_tool && dbt test --profiles-dir ~/.dbt
cd ../.. && python -m pytest tests
```

dbt tests include uniqueness, accepted `geo_type` values, core-state coverage (Louisiana is a documented source gap), a national row in the latest month, and suppressed deaths remaining null.
