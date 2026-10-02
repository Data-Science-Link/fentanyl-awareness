# Estimated deaths in each month

The main chart and `deaths_by_month.csv` answer a simpler question than the CDC file they come from: how many people died in that month?

## What the official files are

The provisional CDC file is not a count of deaths in a single month. Each number is the total for the 12 months ending in that month. CDC publishes it that way because recent death certificates are still being completed. In this project that column is `headline_deaths`. For a recent month, or a month CDC flags as incomplete, `headline_deaths` uses CDC's predicted count. Otherwise it uses the reported count.

Call that 12-month total `H_t`. The change from one month to the next is:

`H_t - H_{t-1} = deaths in month t − deaths in month t−12`

It is not, by itself, the number of deaths in month t.

The final file, from CDC WONDER, is different. A monthly row there is the number of deaths in that month on final death certificates.

## The rule used here

For a national month:

1. If CDC WONDER has a final count for that month, use it. The spreadsheet says `Official final count`.
2. If it does not, estimate `deaths in month t = (H_t − H_{t−1}) + deaths in month t−12`. The spreadsheet says `Estimated from the change in the 12-month total`.
3. The raw change `H_t − H_{t−1}` is kept in `Change in the 12-month total` so the arithmetic can be checked.
4. If an estimate comes out below zero, it is kept in the file and explained in `Note`. The chart leaves a gap. A negative number is what happens when CDC revises a provisional total. It is not a count of deaths.

Final months are never replaced by the estimate.

## A worked example

Suppose three monthly death counts are known, 12 months apart is simplified to a one-month window here only to show the arithmetic. With a real 12-month total:

- Deaths in January 2024 were 100 (final).
- The 12-month total ending December 2024 was 1,000.
- The 12-month total ending January 2025 was 1,040.

The change is 1,040 − 1,000 = 40. That 40 equals January 2025 minus January 2024. January 2025 is estimated as 40 + 100 = 140.

## What the count includes

The category is ICD-10 code T40.4, synthetic opioids other than methadone, on a drug-poisoning death. Fentanyl is in this group. So are some other synthetic opioids, such as tramadol. Methadone is not in this group. These are not fentanyl-only deaths.

State charts on the site do not use this monthly estimate. Some states have months that CDC leaves blank, so a state-by-state reconstruction would invent too much. The state map uses the change in the 12-month total from the same month a year earlier.

## Sources

- Provisional totals: CDC Vital Statistics Rapid Release, SODA dataset `xkb8-kh2a`, [Provisional Drug Overdose Death Counts](https://www.cdc.gov/nchs/nvss/vsrr/drug-overdose-data.htm).
- Final monthly counts: CDC WONDER multiple-cause datasets D77 (1999–2017) and D157 (2018 through the latest final year).
- Population for the per-100,000 column: Census Population Estimates Program, July 1 resident population. If that year is not in the file yet, the nearest Census year is named in `Note`.
