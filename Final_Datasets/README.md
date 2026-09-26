# Final Datasets

This folder holds the published extract of the Fentanyl Awareness Project. The numbers are people. Use them carefully.

## Available dataset

**File**: `fact_fentanyl_deaths_over_time.csv`

Provisional CDC 12-month ending counts for **synthetic opioids, excl. methadone (T40.4)**, joined to Census ACS 5-year demographics.

- **Time period**: 2015 through the latest month CDC has published
- **Source**: CDC VSRR SODA dataset `xkb8-kh2a` (not CDC WONDER)
- **Update**: Weekly via GitHub Actions. The portal CSV can be newer than `main` when branch protection blocks a direct bot commit

## Data dictionary

| Column | Description |
|--------|-------------|
| `year` | End year of the 12-month reporting window |
| `month` | First day of the month that ends the window |
| `state` | Geography name |
| `geo_type` | `nation`, `state`, `city`, or `territory` |
| `rolling_12_month_deaths` | Reported 12-month ending T40.4 deaths. **Null when CDC withheld the number** |
| `predicted_12_month_deaths` | CDC predicted (delay-adjusted) count when published |
| `is_suppressed` | True when the reported count is blank |
| `footnote` | CDC footnote text |
| `footnote_symbol` | CDC footnote symbol |
| `percent_complete` | CDC completeness of death reporting |
| `percent_pending_investigation` | CDC percent pending investigation |
| `data_source` | Always `CDC SODA API` |
| `population` | ACS 5-year total population for `population_year` |
| `population_year` | ACS 5-year end year used for population |
| `median_household_income` | ACS 5-year median household income for `demographics_year` |
| `unemployment_rate` | ACS 5-year unemployment rate for `demographics_year` |
| `demographics_year` | ACS 5-year end year used for income and unemployment |
| `deaths_per_100k` | `rolling_12_month_deaths` per 100,000 population |
| `predicted_deaths_per_100k` | Predicted count per 100,000 population |
| `population_is_carried_forward` | True when `population_year` is earlier than `year` |
| `extracted_at` | UTC timestamp of the CDC extract |

## How to use this file

- Filter `geo_type = state` before ranking states
- Do **not** sum `rolling_12_month_deaths` across months
- Do **not** treat blank death counts as zero
- Do not add New York City to New York, and do not add states to the United States row
- Louisiana is often absent from the T40.4 VSRR series
- T40.4 is broader than fentanyl alone

## Questions

Open a GitHub issue.
