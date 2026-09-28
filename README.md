# Fentanyl Awareness Data Pipeline

The fentanyl crisis in the United States is a profound tragedy. This project republishes official CDC series so it is easier to see whether synthetic-opioid deaths are rising or falling, and how states compare per capita.

**A note on the data**: Every count is a life lost too soon. The files here are for awareness and research. Confirm figures with CDC before using them for policy.

## What this project provides

- A cleaned CSV of **provisional CDC 12-month ending T40.4 counts** (2015–current)
- A separate CSV of **final NVSS incident deaths** for the same ICD-10 code (1999 through the latest final year)
- An [interactive portal](https://data-science-link.github.io/fentanyl-awareness/) with methodology, charts, and a downloadable table
- Weekly extracts via GitHub Actions
- dbt tests and lineage docs

## What the numbers are

| Topic | Fact |
|--------|------|
| Provisional source | CDC VSRR SODA dataset `xkb8-kh2a` |
| Final source | CDC WONDER multiple-cause request form, labeled `NVSS final` (`D77` for 1999–2017, `D157` for 2018–latest final year) |
| Indicator | Synthetic opioids, excl. methadone (**T40.4**). Includes fentanyl and other synthetics such as tramadol |
| Provisional metric | **12-month ending** counts. Do not sum monthly rows. Recent months use CDC predicted counts in `headline_deaths` |
| Final metric | Incident deaths in a calendar year or month. Not derived from the rolling column |
| Geography | States, DC, New York City, Puerto Rico, and a United States total. Filter on `geo_type` |
| Known gap | Louisiana is not in T40.4 VSRR. The provisional file has an explicit `not_reportable` row. Final NVSS counts for Louisiana are in the final file |
| Blank deaths | CDC withheld the number. That is not a zero |
| Rates | Census PEP July 1 population. `population_year` is shown when a different year is carried forward |
| Income and unemployment | Census ACS 5-year estimates. Those refresh only when `CENSUS_API_KEY` is set |

The published files are on the [portal](https://data-science-link.github.io/fentanyl-awareness/): [provisional CSV](https://data-science-link.github.io/fentanyl-awareness/fact_fentanyl_deaths_over_time.csv) and [final CSV](https://data-science-link.github.io/fentanyl-awareness/fact_nvss_final_t40_4.csv). See [`Final_Datasets/README.md`](Final_Datasets/README.md) for the data dictionary. Copies under `Final_Datasets/` are for local dbt and can lag the portal.

## Quick access

- **Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **Provisional CSV**: https://data-science-link.github.io/fentanyl-awareness/fact_fentanyl_deaths_over_time.csv
- **Final CSV**: https://data-science-link.github.io/fentanyl-awareness/fact_nvss_final_t40_4.csv
- **Pipeline docs**: [`data_engineering/`](data_engineering/README.md)

## How it works

1. `soda_extractor.py` pulls T40.4 rows from the CDC SODA API and fails if a state that was in the previous extract disappears
2. `wonder_extractor.py` requests final T40.4 incident deaths from the CDC WONDER request form. The XML API does not return state tabulations, so the job uses the form that does
3. `pep_extractor.py` loads Census PEP July 1 population. `census_extractor.py` loads ACS income and unemployment when `CENSUS_API_KEY` is present
4. dbt writes two fact CSVs. Final incident deaths are never copied into `rolling_12_month_deaths`
5. The publish job extracts, tests, and deploys GitHub Pages. It runs every Monday, on **Run workflow**, and when website or pipeline changes merge to `main`. HTML and data in that run are one snapshot. It does not open a pull request.

### Publishing

The portal is whatever the last successful **Publish portal** run deployed. `main` holds code, models, tests, and a local seed snapshot.

| Event | What goes live |
|--------|----------------|
| Monday schedule, **Run workflow**, or a merge to `main` that touches `website/`, `data_engineering/`, or `Final_Datasets/` | Fresh extracts, fact CSVs, dbt docs, and `website/index.html` from that commit |
| Merge of README or test-only changes | Nothing on the portal |

Pages source must be **GitHub Actions** (Settings → Pages → Build and deployment → Source). This token cannot flip that. Until it is set, `actions/deploy-pages` will fail and the last `gh-pages` copy stays live.

`main` still requires a reviewed pull request for code. Publishing does not.

## Reliability

- dbt tests cover keys, geography coverage, and suppression handling
- Python unit tests run in CI
- Security scanning runs on pushes and pull requests
- GitHub Actions Pages deployments are the audit trail for each published extract

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

- CDC National Center for Health Statistics (VSRR and WONDER multiple-cause datasets D77 and D157)
- U.S. Census Bureau (Population Estimates Program and ACS)
- GitHub (hosting and automation)
