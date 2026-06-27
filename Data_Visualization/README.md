# Data Visualization

**Status**: Placeholder for future Python-based dashboards

This folder will contain interactive visualizations for exploring fentanyl mortality data. We are transitioning away from Tableau and Google Sheets to a more open-source approach using Python-generated visualizations.

## 🔗 Available Resources

### Data Portal
- **Interactive Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **Interactive Explorer**: Browse and filter data online without any setup.
- **dbt Docs**: Technical documentation and data lineage.

### Data Access
- **CSV File**: Available at `Final_Datasets/fact_fentanyl_deaths_over_time.csv`
- **GitHub**: https://github.com/Data-Science-Link/fentanyl-awareness
- **Raw Data**: See `data_engineering/` folder for source data

## 📊 Current Visualization Options

You can use the CSV file to create visualizations in:
- **Data Portal**: Use our built-in explorer at the link above.
- **Python/R**: Use provided datasets with Plotly, Matplotlib, or ggplot2.
- **Excel**: Open the CSV directly for local charts.

## 🔄 Data Updates

The CSV and interactive portal are automatically updated every Monday at 12:00 PM UTC via GitHub Actions.

## 📥 Quick Start

1. **Browse** the data on our [Interactive Portal](https://data-science-link.github.io/fentanyl-awareness/)
2. **Download** `fact_fentanyl_deaths_over_time.csv` for local analysis
3. **Explore** trends over time by state
4. **Analyze** correlations between deaths and economic indicators

## 💡 Future Plans

- Python-based interactive dashboards (Streamlit/Plotly)
- Automated static chart generation for the project page
- Integrated map visualizations for geographic trends
