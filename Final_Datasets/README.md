# Final Datasets

This folder holds snapshot extracts for local dbt. The live published files are on the [portal](https://data-science-link.github.io/fentanyl-awareness/). The numbers are people. Use them carefully.

## Provisional series

**File**: `fact_fentanyl_deaths_over_time.csv`

Provisional CDC 12-month ending counts for **synthetic opioids, excl. methadone (T40.4)**.

- **Time period**: 2015 through the latest month CDC has published
- **Source**: CDC VSRR SODA dataset `xkb8-kh2a`
- **Rates**: Census PEP July 1 population. Income and unemployment remain ACS 5-year estimates

| Column | Description |
|--------|-------------|
| `year` | End year of the 12-month reporting window |
| `month` | First day of the month that ends the window |
| `state` | Geography name |
| `geo_type` | `nation`, `state`, `city`, or `territory` |
| `rolling_12_month_deaths` | Reported 12-month ending deaths. Null when CDC withheld the number |
| `predicted_12_month_deaths` | CDC predicted count when published |
| `headline_deaths` | Predicted count for the latest six months, or when CDC flags underreporting, incomplete data, or completeness below 100. Otherwise the reported count |
| `headline_basis` | `predicted` or `reported` |
| `is_suppressed` | True when the reported count is blank |
| `reporting_status` | `reported`, `suppressed`, or `not_reportable` |
| `population` | Census PEP July 1 population for `population_year` |
| `population_year` | Year of that population estimate |
| `population_source` | `Census PEP` when a denominator is present |
| `population_is_carried_forward` | True when `population_year` is not `year` |
| `deaths_per_100k` | Reported count per 100,000 |
| `predicted_deaths_per_100k` | Predicted count per 100,000 |
| `data_source` | `CDC SODA API` |
| `extracted_at` | UTC timestamp of the CDC extract |

`not_reportable` rows, including Louisiana, have null death counts. They are not zeros and they are not all-drug overdose deaths.

## Final series

**File**: `fact_nvss_final_t40_4.csv`

Incident deaths from CDC WONDER final multiple-cause datasets. A death is counted when the underlying cause is drug poisoning (X40–X44, X60–X64, X85, Y10–Y14) and multiple-cause code T40.4 is present.

- **Time period**: 1999 through the latest final year WONDER returns (2024 as of this extract)
- **source_dataset**: `D77` for 1999–2017 and `D157` for 2018 through the latest final year. The XML API does not return state tables, so these counts come from the WONDER request form
- The United States row is the national total for the 50 states and DC. Puerto Rico is not in these residence lists
- Counts of 1–9 are withheld. WONDER leaves those cells out of the export, so they are absent here rather than stored as zero. A cell WONDER labels suppressed is stored with a null count and `is_suppressed` true
- Annual totals come from the year query, not from adding months
- This file has no `rolling_12_month_deaths` column

| Column | Description |
|--------|-------------|
| `year` | Calendar year |
| `month` | First of the month, or blank for an annual row |
| `period_type` | `year` or `month` |
| `incident_deaths` | Deaths in that period. Null when suppressed |
| `data_source` | `NVSS final` |
| `source_dataset` | `D77` or `D157` |

## How to use these files

- Do not add the final incident counts into the provisional rolling column
- Do not sum `rolling_12_month_deaths` across months
- Do not treat a blank death count as zero
- Filter `geo_type = state` before ranking states
- Do not add New York City to New York, and do not add states to the United States row
- For a finished year, use the final file. The provisional file remains a 12-month ending series even in years that were later finalized

## Questions

Open a GitHub issue.
