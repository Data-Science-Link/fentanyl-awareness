# Final_Datasets

This folder contains polished, ready-to-use CSV files with fentanyl-related mortality data. These datasets are cleaned, validated, and formatted for immediate analysis without requiring any technical setup.

## 📊 Available Datasets

### Synthetic Opioid Deaths - Complete Dataset
- **File**: `synthetic_opioid_deaths_complete.csv`
- **Description**: Comprehensive dataset combining all CDC WONDER sources (1999-current)
- **Includes**: Death counts, rates, population data, geographic information
- **Time Period**: 1999-2024 (varies by data source)

### Key Features
- **Clean Data**: All missing values handled, data types standardized
- **Geographic Coverage**: National, state, and county-level data
- **Time Series**: Historical trends from 1999 to present
- **Rate Calculations**: Both crude and age-adjusted death rates
- **Population Categories**: County size classifications for analysis

## 📈 Data Dictionary

| Column | Description | Type |
|--------|-------------|------|
| `year` | Year of data | Integer |
| `state` | State name | String |
| `county` | County name | String |
| `deaths` | Number of synthetic opioid deaths | Integer |
| `population` | Population count | Integer |
| `crude_rate` | Deaths per 100,000 population | Float |
| `age_adjusted_rate` | Age-adjusted death rate | Float |
| `time_period` | Data source period (Historical/Recent/Provisional) | String |
| `county_size` | Population size category | String |

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

These datasets are updated monthly through our automated pipeline. Check the file timestamps for the most recent data.

## 📞 Questions?

For questions about the data or requests for additional datasets, please open a GitHub issue or contact the project maintainers.
