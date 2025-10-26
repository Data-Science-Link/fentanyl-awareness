# Final Datasets

This folder contains polished, ready-to-use CSV files with fentanyl-related mortality data. These datasets are cleaned, validated, and formatted for immediate analysis without requiring any technical setup.

## 📊 Available Dataset

### Fentanyl Deaths Over Time
- **File**: `fact_fentanyl_deaths_over_time.csv`
- **Description**: Comprehensive dataset combining all CDC WONDER sources (1999-current) with census demographics
- **Includes**: Death counts, population data, economic indicators, data source tracking
- **Time Period**: 1999-current
- **Update Frequency**: Weekly (every Monday at 12:00 PM UTC)

### Key Features
- **Clean Data**: All missing values handled, data types standardized
- **Geographic Coverage**: State-level aggregation from CDC WONDER
- **Time Series**: Historical trends from 1999 to present
- **Demographics**: Population, income, and unemployment data from US Census
- **Source Prioritization**: Handles overlapping time periods between official and provisional data

## 📈 Data Dictionary

| Column | Description | Type |
|--------|-------------|------|
| `year` | Year of data | Integer |
| `month` | Month (first day of month) | Date |
| `state` | State name | String |
| `deaths` | Number of synthetic opioid deaths | Integer |
| `data_source` | Source dataset (Official 1999-2020, Official 2018-2023, or Provisional 2018-current) | String |
| `population` | State population from US Census | Integer |
| `median_household_income` | Median household income (dollars) from US Census | Float |
| `unemployment_rate` | Unemployment rate (percentage) from US Census | Float |

## 🎯 Use Cases

These datasets are perfect for:
- **Research**: Academic studies on opioid mortality trends
- **Analysis**: Data science projects and statistical analysis
- **Visualization**: Creating charts, maps, and dashboards
- **Policy**: Supporting evidence-based policy decisions
- **Education**: Teaching data analysis and public health concepts

## 📥 How to Use

1. **Download** the CSV files directly
2. **Import** into your preferred analysis tool (Excel, R, Python, Tableau, etc.)
3. **Analyze** using the provided data dictionary
4. **Visualize** trends and patterns in the data

## 🔄 Data Updates

This dataset is automatically updated **every Monday at 12:00 PM UTC** through our GitHub Actions pipeline. The CSV in this folder is always the latest version, and GitHub maintains a complete history of all changes.

## 📞 Questions?

For questions about the data or requests for additional datasets, please open a GitHub issue or contact the project maintainers.
