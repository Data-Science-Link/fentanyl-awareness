# Audit of the public figures

Checked on October 2, 2026, against the sources named on the page. Each item is either confirmed or changed. The front page keeps ordinary words. The code for the death category stays in the method notes.

## Monthly deaths

Finished months are the official count. The 12 months of 2024 in `deaths_by_month.csv` add up to 47,735, the same number as the 2024 annual row in the final death file. No finished month is replaced by an estimate. The first estimated month is January 2025.

Later months follow the rule in [monthly_deaths.md](monthly_deaths.md): the change in the 12-month total, plus the count from 12 months earlier. That identity holds for every estimated month in the file.

**Changed: October 2025.** CDC's file has two totals. The reported total is the count received so far. The predicted total is CDC's adjustment for death certificates that are still coming in. September 2025 uses the reported total, 40,022. October 2025 is inside the latest six months, so the headline is the predicted total, 39,722. The old estimate subtracted those two different kinds of totals. That counted CDC's reporting adjustment as if it were deaths in October.

| Step | Old figure | Figure used now |
|------|------------|-----------------|
| October 2025 total | predicted 39,722 | predicted 39,722 |
| September 2025 total | reported 40,022 | predicted 40,247 |
| Change | −300 | −525 |
| October 2024 finished count | 3,130 | 3,130 |
| October 2025 estimate | 2,830 | 2,605 |

The reported-only change would be 39,519 − 40,022 = −503, and the estimate would be 2,627. The chart uses the predicted series on both sides, which is the same kind of total the headline already uses for October. Months after October were already predicted on both sides, so their estimates did not change. November's change from the previous month changed because October's estimate changed.

**Revisions.** No month in this file estimates below zero. If one does, the spreadsheet keeps the number and explains it, and the chart leaves a gap. That gap is a revision, not a month with no deaths. The sentence is next to the chart.

**Residence and place of death.** Finished counts are deaths of residents of the 50 states and DC. CDC's provisional file counts deaths by where they occurred, and it can include people who were not residents. A recent estimate can sit a little above or below the count CDC prints when the certificates are finished. The decline on the chart is much larger than that gap. The method note says so. The page says a recent month can move when CDC revises a provisional total.

**Population.** The chart is a count, not a rate. In the spreadsheet, deaths per 100,000 use a July 1 Census population. The note on a row names the Census year when it is not the death year. In this file, 1999 uses July 1 2000, the first year in the Census file, and 2026 uses July 1 2025. The download section says that.

## The drug category

Confirmed. The opening paragraph says the death records include fentanyl and other synthetic opioids, do not include methadone, and are not a fentanyl-only count. That matches CDC's category. The code stays in the method note, not on the front page.

## State map

Confirmed as a percent change in the 12-month total, not deaths in that month. Gray means CDC did not publish a count. Gray is not zero.

In the latest month, April 2026, Florida, Nevada, Oregon, and Virginia are blank. Florida's footnote says the count is withheld for data quality. Louisiana is gray in every month because CDC does not include it in this series. Nebraska, North Dakota, and Pennsylvania are gray in this comparison because the same month a year earlier was blank. A blank is not treated as zero.

**Changed: the two months now use the same kind of CDC total.** The latest month is predicted. The same month a year earlier was reported. Differencing those two counted part of CDC's reporting adjustment as a change in deaths. The map now uses the predicted total for both months when the latest month is predicted. No state flips from up to down. California, New Jersey, North Carolina, and Rhode Island move by a point or more. North Carolina goes from about 23 percent down to about 27 percent down. Rhode Island, on the list of largest decreases, goes from 43 percent to 44 percent. The other names on that list do not change at the rounded percent.

**Changed: New York.** CDC publishes New York City separately from the rest of New York. In the latest 12-month total the city is 1,226 and the rest of the state is 981. The map does not add the city into the state. The sentence next to the map says so. Adding them would contradict the project's rule that New York City stays separate.

## Age, race, and the share of drug-poisoning deaths

**Age. Changed.** The chart is final 2024 death certificates. The note used to call every bar a ten-year group. The youngest groups are under 1, 1–4, and 5–14. The groups add up to 47,732. The full year, and the race table, are 47,735. The chart does not fill in those three deaths. The sentence is next to the chart.

**Race. Confirmed.** Both sides are race alone for 2024. Hispanic origin is not separated. The six death groups add up to 47,735. The six Census rows are the July 1, 2024 race-alone rows, plus Two or More Races, from Census table NC-EST2024-SR11H:

| Group | Population |
|-------|------------|
| White | 254,281,598 |
| Black or African American | 46,608,846 |
| American Indian and Alaska Native | 4,743,298 |
| Asian | 22,825,008 |
| Native Hawaiian and Other Pacific Islander | 939,712 |
| Two or More Races | 10,712,526 |
| Total | 340,110,988 |

Those are not the "not Hispanic" rows. A not-Hispanic population would not match a death file that does not separate Hispanic origin. The July 1, 2024 total in this table, 340,110,988, is not the Census PEP total used for death rates, 340,003,797. The race chart uses the race table. The monthly rates use PEP. The note next to the chart already says the bars are shares, not a claim about why they differ.

**Share. Changed.** The sentence used 47,732, the age-group sum, of 79,384 drug-poisoning deaths. The rest of the site uses the full-year total, 47,735. The share file now uses 47,735. Divided by 79,384, both round to 60.1 percent, so the percent does not change. The sentence still says one death can list more than one drug, so the share is not a slice of a pie.

## Deaths per 1,000 people per year

The inputs in `comparison_per_1000.csv` match the sources. The rate column is deaths ÷ years ÷ population × 1,000, rounded to 4 decimal places.

| Bar | Deaths | Years | Population | Rate |
|-----|--------|-------|------------|------|
| World War I | 116,516 | 2 | 103,982,000 | 0.5603 |
| World War II | 405,399 | 5.084189 | 138,262,596 | 0.5767 |
| Vietnam | 58,220 | 19.537303 | 192,997,874 | 0.0154 |
| COVID-19, 2020–2022 | 1,095,240 | 3 | 332,558,191 | 1.0978 |
| Synthetic opioids, 2024 | 47,735 | 1 | 340,003,797 | 0.1404 |

Deaths: Congressional Research Service RL32492, Table 1. World War I and World War II are total U.S. military deaths, battle deaths plus other deaths. Vietnam is total in-theater deaths, 58,220. COVID-19 is the sum of NCHS weekly United States rows in dataset `r8kw-7aab` whose week-ending date falls in 2020, 2021, or 2022, data as of October 1, 2026: 367,923, 471,027, and 256,290. The 2024 bar is the final annual count in this project.

Years: World War I is the two calendar years in the table label. World War II is December 1, 1941 through December 31, 1946, from footnote j, which is 1,857 days, or 5.084189 years. Vietnam is November 1, 1955 through May 15, 1975, from footnote n, which is 7,136 days, or 19.537303 years. The table label says 1964–1973. The deaths themselves cover the longer footnote window.

Population: World War I is the average of the July 1, 1917 and July 1, 1918 estimates that include Armed Forces overseas, 103,414,000 and 104,550,000. World War II is the average of July 1, 1942 through July 1, 1946, which is 138,262,596.4, rounded to 138,262,596. Vietnam is the average of July 1, 1956 through July 1, 1974, which is 192,997,873.7, rounded to 192,997,874. Those years include Armed Forces overseas. COVID-19 is the average of this project's July 1, 2020, 2021, and 2022 Census PEP populations, 332,558,191. The 2024 bar uses the July 1, 2024 PEP population, 340,003,797.

**Changed: the sentence next to the chart.** The numbers were already right, and the method note already said the Vietnam window is long. A reader of the chart alone would see a very short Vietnam bar and treat it as a peak year of fighting, and would treat war deaths as the same kind of count as a death certificate. The note now says war bars are service members, including deaths from disease and other causes that were not battle deaths, and that the Vietnam bar is short because the deaths are spread from 1955 to 1975.

## Budget lines

Confirmed, and the sentence next to the chart is more specific. The three amounts match the cited documents. They are not pieces of one fentanyl budget.

| Line | Amount | Source |
|------|--------|--------|
| DEA, fiscal 2025, requested and anticipated funding | $3,770,000,000 | Testimony of Administrator Anne Milgram, May 7, 2024. The testimony says this is the whole request, including fee accounts and reimbursable funds. The salaries-and-expenses request in the same testimony is $2.687 billion. |
| SAMHSA State Opioid Response grants, fiscal 2024 subtotal | $1,575,000,000 | SAMHSA FY 2024 operating plan, subtotal 1,575.000 million. Opioids broadly, not fentanyl alone. |
| CDC Opioid Overdose Prevention and Surveillance, fiscal 2024 | $505,579,000 | CDC FY 2024 operating plan, $505,579 thousand. |

The tall bar is the whole DEA request. The shorter bars are 2024 opioid lines. The note says not to add them or read the heights as a ranking of fentanyl spending.

## Customs and Border Protection seizures

Confirmed against the September 2026 file `nationwide-drugs-fy23-fy26-aug.csv`, the newest file linked from CBP's Nationwide Drug Seizures page. Every fiscal year, component, and region total matches that file. The pounds are:

| Fiscal year | Pounds |
|-------------|--------|
| 2023 | 27,022.86 |
| 2024 | 21,889.21 |
| 2025 | 12,027.28 |
| 2026, year so far | 10,368.75 |

**Changed: the sentences next to the charts.** The year chart already labels the last year as the year so far. The note now says that in ordinary words, and says a seizure total is not a measure of how much got through. The region chart adds every year in the file, including the unfinished year. That was not said on the page. The Southwest border is still where almost all of the pounds were counted. The chart does not show that total as a share of drugs that got through.

## Official actions

A line on the death chart is the date in the source. It is not evidence the action caused a change. The page says that next to the chart and again above the table.

| Date | What was checked |
|------|------------------|
| October 26, 2017 | The ASPR page for the nationwide public health emergency is dated October 26, 2017. |
| February 6, 2018 | The Federal Register issue linked from the table is the February 6, 2018 issue. |
| October 24, 2018 | Public Law 115-271 is noted as October 24, 2018. |
| March 13, 2023 | The ICE release is dated March 22, 2023, and the text says Operation Blue Lotus launched on March 13, 2023. The chart uses the launch date. |
| April 12, 2023 | The designation date is April 12, 2023. The whitehouse.gov page now returns "not found." The link is the same release on the archived White House site, which loads. |
| July 16, 2025 | Public Law 119-26, the Halt All Lethal Trafficking of Fentanyl Act, is noted as July 16, 2025. |

## Official announcements

The list is agency releases that mention fentanyl, not a ranking of news outlets.

**Changed: three links that did not open the release.** The two CDC items pointed at a CDC media tool that now redirects to a "page not found" address. They now point at CDC's archive copies of those releases, which load: the March 29, 2018 press release and the October 27, 2017 media statement. The xylazine item uses the same archived White House page as the action table. The weekly extract follows a CDC media link and, if the newsroom page is gone, stores the archive address instead.

## Memorial cards

Confirmed. The cards are people whose families sent a photo to DEA's Faces of Fentanyl exhibit. The file has 7,039 names with a photo. The page does not copy the image files. It links to the image on DEA's site. The note now says the number of cards is the number of photos families sent, not the number of deaths.

## DEA kilograms and Customs and Border Protection pounds

Confirmed as separate series. The 2025 National Drug Threat Assessment says U.S. law enforcement seized 14,069 kilograms of fentanyl at the southwest border in 2024, the majority at the Arizona-Mexico border, citing the National Seizure System, figure NIIPG-021-25, as of March 25, 2025. That sentence is in the source note. It is not drawn on the seizure chart. The page says the kilogram figure is a different system and is not added to the Customs and Border Protection pounds. CBP's own fiscal 2024 total in this file is 21,889.21 pounds. The two should not be converted and added.

The two quotations on the page match the assessment: the letter from the Acting Administrator on the Sinaloa Cartel and the Jalisco New Generation Cartel, and the fentanyl section on the southwest border as the main entry point.
