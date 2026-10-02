# Data Sources

Official extracts used by the Fentanyl Awareness pipeline.

## 1. CDC SODA API (`cdc_api/`)

**Status**: Active primary source

CDC VSRR provisional drug overdose death counts via `https://data.cdc.gov/resource/xkb8-kh2a.json`.

- Indicator: Synthetic opioids, excl. methadone (T40.4)
- Period kept downstream: `12 month-ending`
- Extractor paginates, stamps `extracted_at`, and fails if unexpected states are missing
- Louisiana is a documented source gap when CDC withholds T40.4 for quality reasons

```bash
python3 cdc_api/soda_extractor.py
```

## 2. Census PEP (`census_pep/`)

**Status**: Active. This is the population denominator for death rates.

July 1 resident population from the public PEP vintage files. No API key.

- Vintage 2025 (or the newest file that exists) for 2020 through that vintage
- 2010–2019 from the 2020 estimates file
- 2000–2009 from the 2000–2010 intercensal file
- 1999 is not in those files. A 1999 rate would carry the 2000 population and set `population_is_carried_forward`

```bash
python3 census_pep/pep_extractor.py
```

## 3. Census ACS (`census_acs/`)

**Status**: Active for income and unemployment only.

American Community Survey **5-year** estimates.

- Income and labor force: `B19013_001E`, `B19301_001E`, `B23025_*`
- Requires `CENSUS_API_KEY`. The weekly job warns and keeps the last seed when the secret is missing
- A missing future ACS year ends the year loop instead of failing years that already returned data
- Unemployment stays null when labor force is missing

```bash
python3 census_acs/census_extractor.py
```

## 4. Final NVSS / CDC WONDER (`nvss_wonder/`)

**Status**: Active, as a second labeled series.

Final incident T40.4 drug-overdose deaths, 1999 through the latest final year on CDC WONDER. The XML API refuses state grouping, so the extractor posts the WONDER request form for datasets D77 (1999–2017) and D157 (2018–latest). Monthly and annual counts are both stored. Counts under 10 are suppressed. Nothing in this file is differenced from the VSRR rolling column. If WONDER is down and a seed already exists, the weekly job keeps that seed.

```bash
python3 nvss_wonder/wonder_extractor.py
```

Age, race, and the share of drug-poisoning deaths that also list T40.4 come from the same WONDER form, for the latest final year. The share numerator is the race-group total, because an age grouping can omit a few deaths. If that request fails and a seed already exists, the job keeps the seed. The race categories are the ones WONDER returned. The Census crosswalk is written in `docs/methods/who_is_affected.md`.

```bash
python3 nvss_wonder/wonder_demographics.py
```

## 5. Customs and Border Protection (`cbp/`)

**Status**: Active for fentanyl aggregates only.

The newest CSV linked from [Nationwide Drug Seizures](https://www.cbp.gov/document/stats/nationwide-drug-seizures). Rows with drug type Fentanyl are summed by fiscal year, CBP component, and region. Field offices, concealment, and seizure narratives are not published. If the page is down and a seed exists, the job keeps that seed.

```bash
python3 cbp/cbp_extractor.py
```

## 6. DEA Faces of Fentanyl (`faces/`)

**Status**: Active for the public exhibit listing.

[Faces of Fentanyl](https://fof.dea.gov/exhibit) is a memorial families submit to DEA. The extractor stores first name, state, age, the exhibit URL, and the DEA-hosted image URL. It does not download image files. A person who leaves the exhibit leaves the file on the next run. Song for Charlie is not scraped.

```bash
python3 faces/faces_extractor.py
```

## 7. Official announcements (`announcements/`)

**Status**: Active.

CDC’s media feed, plus a small set of DEA and CBP releases whose titles were checked against the agency page. Rows are kept only when the title or summary mentions fentanyl or synthetic opioids. If a feed is down, earlier rows from that publisher stay in the file.

```bash
python3 announcements/announcements_extractor.py
```

## Cited snapshots

`docs/sources/` holds files that do not have a stable feed: `policy_actions.csv`, `agency_budgets.csv`, `comparison_per_1000.csv`, `census_race_2024.csv`, and `supply_context.md`. A row without a primary-source URL does not belong in those tables. dbt loads `policy_actions` as a seed for the monthly file.

## Pipeline

```
CDC SODA API → soda_extractor.py       → provisional fact CSV
NCHS MCD     → wonder_extractor.py     → final incident fact CSV
NCHS MCD     → wonder_demographics.py  → age, race, and drug-poisoning share
Census PEP   → pep_extractor.py        → rate denominators
Census ACS   → census_extractor.py     → income and unemployment
CBP CSV      → cbp_extractor.py        → fentanyl pounds by year, component, region
DEA exhibit  → faces_extractor.py      → public memorial listing
Agency feeds → announcements_extractor.py → fentanyl releases
dbt          → fact_deaths_by_month       → deaths_by_month.csv
dbt          → fact_deaths_by_state_month → deaths_by_state_month.csv
CDC metadata → freshness.py               → data_freshness.csv
```
