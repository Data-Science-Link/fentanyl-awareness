# Deaths per 1,000 people per year

The "Why this matters" chart compares five events with one formula:

`deaths per 1,000 people per year = deaths / years / population × 1,000`

The numbers in [comparison_per_1000.csv](../sources/comparison_per_1000.csv) are the inputs. The rate column is that formula rounded to 4 decimal places. Nothing on the chart is rounded to a slogan.

These events are not the same kind of death. War rows are U.S. military deaths. COVID-19 rows are death certificates that mention COVID-19. The 2024 row is drug-poisoning deaths that also list a synthetic opioid other than methadone. That group includes fentanyl and is not fentanyl alone. The chart puts them side by side only as deaths per 1,000 people per year, for the dates in the file.

## Windows

- World War I uses the two calendar years in the CRS table label, 1917-1918. Population is the average of the July 1 estimates that include Armed Forces overseas.
- World War II uses December 1, 1941 through December 31, 1946, from CRS footnote j. Years are the inclusive number of days divided by 365.25.
- Vietnam uses November 1, 1955 through May 15, 1975, from CRS footnote n. The per-year figure is low because those deaths are spread across that full window, not across a single peak year.
- COVID-19 uses calendar years 2020, 2021, and 2022. Each year is the sum of NCHS weekly U.S. rows whose week-ending date falls in that year, from dataset `r8kw-7aab` as of October 1, 2026.
- Synthetic opioids uses the final 2024 U.S. annual count in this project (47,735) and the July 1, 2024 Census population.

Population for 1940-1979 in the historical Census file is resident population plus Armed Forces overseas. Population for 2020-2024 is the July 1 resident population from the Census Population Estimates Program vintage already used for death rates in this project.

## Sources

- Congressional Research Service, *American War and Military Operations Casualties: Lists and Statistics*, RL32492, updated July 29, 2020. https://www.congress.gov/crs-product/RL32492
- The CRS table cites the Defense Casualty Analysis System: https://dcas.dmdc.osd.mil/dcas/pages/report_principal_wars.xhtml
- Census Bureau, Historical National Population Estimates, July 1, 1900 to July 1, 1999. http://www2.census.gov/programs-surveys/popest/tables/1900-1980/national/totals/popclockest.txt
- National Center for Health Statistics, Provisional COVID-19 Death Counts by Week Ending Date and State. https://data.cdc.gov/resource/r8kw-7aab.json
- CDC WONDER multiple-cause dataset D157, and Census PEP July 1, 2024, as extracted by this project.
