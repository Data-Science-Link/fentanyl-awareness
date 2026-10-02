# Data Visualization

The public site is six pages. The order is the project brief. The layout note is [How this site is laid out](../docs/design/public-site-layout.md).

- **What this is**: deaths per 1,000 people per year, same formula for every event
- **Rising or falling**: estimated deaths in each month. Official months are a solid line. Estimated months are dashed. A negative estimate is a gap
- **Who is affected**: the DEA memorial listing, age, race compared with Census, the share of drug-poisoning deaths, CBP pounds, and budget lines as printed
- **Official actions**: the monthly series with action dates, plus the count that month and twelve months later
- **Announcements**: agency releases that mention fentanyl
- **Download**: `deaths_by_month.csv` and the column dictionary

The state map is the percent change in the 12-month total versus the same month a year earlier. It uses `geo_type = state`. Unpublished states stay gray. Suppressed CDC counts are omitted rather than plotted as zero.

Portal: https://data-science-link.github.io/fentanyl-awareness/
