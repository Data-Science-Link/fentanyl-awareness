# Age, race, and the share of overdose deaths

## Age

The age chart is the 2024 final count of U.S. drug-poisoning deaths that also list ICD-10 T40.4, by ten-year age group, from CDC WONDER dataset D157. T40.4 is synthetic opioids other than methadone. It includes fentanyl and is not fentanyl alone.

The age groups in `wonder_age.csv` sum to 47,732. The annual United States total in the final death file for 2024 is 47,735. The three-death difference is left as WONDER published it. The chart does not adjust it.

## Race

The race chart uses the same 2024 WONDER request, grouped by race. Those six groups sum to 47,735. Hispanic origin is not a separate group in this extract. Hispanic and non-Hispanic people are inside the race recorded on the death certificate.

The population bars use Census table NC-EST2024-SR11H, July 1, 2024, race alone, plus Two or More Races. Those six Census rows also sum to the table total, 340,110,988. They are not the "not Hispanic" rows. A not-Hispanic population would not match a death file that does not separate Hispanic origin.

The labels differ by one word. Census says "American Indian and Alaska Native" and "Native Hawaiian and Other Pacific Islander." The death file says "or." The crosswalk is `census_race_2024.csv`.

The chart shows each group's share of deaths and share of the population. It does not say why the shares differ.

The July 1, 2024 total in the race table is 340,110,988. The population used for death rates elsewhere in this project is the Census PEP vintage total, 340,003,797. They are different Census products. The race chart uses the race table. The monthly rates use PEP.

## Share of drug-poisoning deaths

`wonder_drug_share.csv` is drug-poisoning deaths in 2024 (underlying cause X40–X44, X60–X64, X85, Y10–Y14) and, beside that, the count of those deaths that also list T40.4. One death can list more than one drug. The share is not a slice of a pie, and the other drugs are not shown as the remainder.

Source for the death tabulations: CDC WONDER, https://wonder.cdc.gov/mcd-icd10-expanded.html

Source for the population: https://www2.census.gov/programs-surveys/popest/tables/2020-2024/national/asrh/nc-est2024-sr11h.xlsx
