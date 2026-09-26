# Fentanyl Awareness Data Pipeline

The fentanyl crisis in the United States is a profound tragedy. This project republishes one official CDC series so it is easier to see whether synthetic-opioid deaths are rising or falling, and how states compare per capita.

**A note on the data**: Every count is a life lost too soon. The files here are for awareness and research. Confirm figures with CDC before using them for policy.

## What this project provides

- A cleaned CSV of **provisional CDC 12-month ending T40.4 counts** (2015–current)
- An [interactive portal](https://data-science-link.github.io/fentanyl-awareness/) with methodology, charts, and a downloadable table
- Weekly extracts via GitHub Actions
- dbt tests and lineage docs

## What the numbers are

| Topic | Fact |
|--------|------|
| Source | CDC VSRR SODA dataset `xkb8-kh2a` |
| Indicator | Synthetic opioids, excl. methadone (**T40.4**). Includes fentanyl and other synthetics such as tramadol |
| Metric | **12-month ending** provisional counts. Do not sum monthly rows |
| Geography | States, DC, New York City, Puerto Rico, and a United States total. Filter on `geo_type` |
| Known gap | Louisiana is often missing from T40.4 VSRR when CDC quality thresholds are not met |
| Blank deaths | CDC withheld the number. That is not a zero |
| Demographics | Census ACS 5-year population and economics; last available year is carried forward when needed |

The published file is [`Final_Datasets/fact_fentanyl_deaths_over_time.csv`](Final_Datasets/fact_fentanyl_deaths_over_time.csv). See [`Final_Datasets/README.md`](Final_Datasets/README.md) for the data dictionary.

## Quick access

- **Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **CSV**: [`Final_Datasets/fact_fentanyl_deaths_over_time.csv`](Final_Datasets/fact_fentanyl_deaths_over_time.csv)
- **Pipeline docs**: [`data_engineering/`](data_engineering/README.md)

## How it works

1. `soda_extractor.py` pulls T40.4 rows from the CDC SODA API
2. `census_extractor.py` pulls ACS 5-year population and economic estimates when a Census API key is present
3. dbt + DuckDB stages the seeds, joins the latest ACS year on or before each death year, and writes the fact CSV
4. GitHub Actions deploys the portal every Monday. If `main` is protected, the refreshed seeds are opened as a pull request instead of a direct push

## Reliability

- dbt tests cover keys, geography coverage, and suppression handling
- Python unit tests run in CI
- Security scanning runs on pushes and pull requests
- Git history is the audit trail for each published extract

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

- CDC National Center for Health Statistics (VSRR)
- U.S. Census Bureau (ACS)
- GitHub (hosting and automation)
