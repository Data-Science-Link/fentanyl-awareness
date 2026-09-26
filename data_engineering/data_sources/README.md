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

## 5. Customs and Border Protection

**Status**: Not implemented.

## Pipeline

```
CDC SODA API → soda_extractor.py  → provisional fact CSV
NCHS MCD     → wonder_extractor.py → final incident fact CSV
Census PEP   → pep_extractor.py    → rate denominators
Census ACS   → census_extractor.py → income and unemployment
```
