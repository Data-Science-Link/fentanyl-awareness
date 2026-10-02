# Data Visualization

Charts now live on the project portal, not in this folder.

- **Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **Main chart**: estimated deaths in each month, with official-action dates as vertical lines
- **State map**: percent change in the 12-month total versus the same month a year earlier. Unpublished states stay gray
- **Download**: `Final_Datasets/deaths_by_month.csv`

The monthly chart uses the national series only. The map uses `geo_type = state`. Suppressed CDC counts are omitted rather than plotted as zero. A negative monthly estimate is left as a gap.
