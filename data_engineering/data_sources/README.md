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

## 2. Census ACS (`census_acs/`)

**Status**: Active

American Community Survey **5-year** estimates (not PEP point-in-time counts).

- Population: `B01001_001E`
- Income and labor force: `B19013_001E`, `B19301_001E`, `B23025_*`
- Requires `CENSUS_API_KEY` for reliable refreshes
- Unemployment stays null when labor force is missing

```bash
python3 census_acs/census_extractor.py
```

## 3. CDC WONDER

**Status**: Removed. Historical WONDER downloads are no longer in the pipeline. The published fact table is SODA-only from 2015 forward.

## 4. Customs and Border Protection

**Status**: Not implemented.

## Pipeline

```
CDC SODA API → soda_extractor.py → dbt seed → staging → fact CSV → GitHub Pages
Census ACS   → census_extractor.py ↗
```
