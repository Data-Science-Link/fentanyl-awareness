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
3. The change stays inside one CDC series. When month t uses the predicted total, month t−1 uses its predicted total too, even if the headline for month t−1 was the reported total. Subtracting a predicted total from a reported total counts CDC's reporting adjustment as if it were deaths in one month. The raw change is kept in `Change in the 12-month total` so the arithmetic can be checked.
4. If an estimate comes out below zero, it is kept in the file and explained in `Note`. The chart leaves a gap. A negative number is what happens when CDC revises a provisional total. It is not a count of deaths.

Final months are never replaced by the estimate.

## A worked example

Suppose three monthly death counts are known, 12 months apart is simplified to a one-month window here only to show the arithmetic. With a real 12-month total:

- Deaths in January 2024 were 100 (final).
- The 12-month total ending December 2024 was 1,000.
- The 12-month total ending January 2025 was 1,040.

The change is 1,040 − 1,000 = 40. That 40 equals January 2025 minus January 2024. January 2025 is estimated as 40 + 100 = 140.

## Predicted and reported totals

In the extract checked on October 2, 2026, September 2025 still uses the reported total (40,022; the predicted total that month is 40,247). October 2025 is inside the latest six months, so its headline is the predicted total, 39,722. The reported total for October is 39,519.

The change used for October 2025 is 39,722 − 40,247 = −525. October 2024's finished count is 3,130, so October 2025 is estimated as 2,605. The mixed subtraction, 39,722 − 40,022 = −300, would have produced 2,830. That 2,830 figure is not used.

Finished counts are deaths of residents of the 50 states and DC. CDC's provisional file counts deaths by where they occurred, and it can include people who were not residents. A recent estimate can therefore sit a little above or below the count CDC prints when the certificates are finished. The chart's decline is much larger than that gap. No month in the current file estimates below zero. If one does, the chart leaves a gap and the spreadsheet explains it.

## What the count includes

The category is ICD-10 code T40.4, synthetic opioids other than methadone, on a drug-poisoning death. Fentanyl is in this group. So are some other synthetic opioids, such as tramadol. Methadone is not in this group. These are not fentanyl-only deaths.

State charts on the site do not use this monthly estimate. Some states have months that CDC leaves blank, so a state-by-state reconstruction would invent too much. The state map is the percent change in the 12-month total from the same month a year earlier. Both months use the same kind of CDC total. New York on the map does not include New York City, because CDC publishes the city separately.

## Sources

- Provisional totals: CDC Vital Statistics Rapid Release, SODA dataset `xkb8-kh2a`, [Provisional Drug Overdose Death Counts](https://www.cdc.gov/nchs/nvss/vsrr/drug-overdose-data.htm).
- Final monthly counts: CDC WONDER multiple-cause datasets D77 (1999–2017) and D157 (2018 through the latest final year).
- Population for the per-100,000 column: Census Population Estimates Program, July 1 resident population. If that year is not in the file yet, the note names the Census year that was used. In this extract, 1999 uses July 1 2000, the first year in the file, and 2026 uses July 1 2025.
