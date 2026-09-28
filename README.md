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

The published file is [`Final_Datasets/fact_fentanyl_deaths_over_time.csv`](Final_Datasets/fact_fentanyl_deaths_over_time.csv). See [`Final_Datasets/README.md`](Final_Datasets/README.md) for the data dictionary.

## Quick access

- **Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **CSV**: [`Final_Datasets/fact_fentanyl_deaths_over_time.csv`](Final_Datasets/fact_fentanyl_deaths_over_time.csv)
- **Pipeline docs**: [`data_engineering/`](data_engineering/README.md)

## How it works

1. `soda_extractor.py` pulls T40.4 rows from the CDC SODA API and fails if a state that was in the previous extract disappears
2. `wonder_extractor.py` requests final T40.4 incident deaths from the CDC WONDER request form. The XML API does not return state tabulations, so the job uses the form that does
3. `pep_extractor.py` loads Census PEP July 1 population. `census_extractor.py` loads ACS income and unemployment when `CENSUS_API_KEY` is present
4. dbt writes two fact CSVs. Final incident deaths are never copied into `rolling_12_month_deaths`
5. GitHub Actions deploys the portal every Monday and force-pushes `automated/weekly-data-refresh`. It opens that pull request when Actions is allowed to, then requests auto-merge. The job does not push `main` directly.

### Unattended merge

`main` requires a pull request, a review, and the checks `dbt-test` and `security-audit`. This token cannot edit those rules. An admin needs to:

1. Settings → Actions → General → enable **Allow GitHub Actions to create and approve pull requests**. Without this, the weekly job extracts, tests, and deploys Pages, then fails at `gh pr create`.
2. Optionally add repository secret `WEEKLY_REFRESH_TOKEN` (a PAT with `repo` scope). Use this when the Actions checkbox must stay off. A PAT-created PR also starts other workflows; `GITHUB_TOKEN` PRs do not. `dbt-test` and `security-audit` still run on pushes to `automated/weekly-data-refresh`.
3. Allow auto-merge on the repository (`allow_auto_merge`).
4. Remove the pull-request review rule from ruleset `18204346` (Main Branch Protections). Leave deletion, non-fast-forward, and the required status checks, with no bypass actors.
5. Add a second ruleset, "Main pull request reviews", with the same review settings (one approval, code owners, dismiss stale reviews, extra approval for unattributed changes, merge commits only) and a bypass for GitHub Actions (integration id `15368`, bypass mode `pull_request`).

Without (1) or (2), the weekly job still publishes Pages and updates the data branch. Open a PR from `automated/weekly-data-refresh` (the compare URL is in the Actions log). After (3)–(5), auto-merge waits for the checks and does not wait for a person.

## Reliability

- dbt tests cover keys, geography coverage, and suppression handling
- Python unit tests run in CI
- Security scanning runs on pushes and pull requests
- Git history is the audit trail for each published extract

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

- CDC National Center for Health Statistics (VSRR and WONDER multiple-cause datasets D77 and D157)
- U.S. Census Bureau (Population Estimates Program and ACS)
- GitHub (hosting and automation)
