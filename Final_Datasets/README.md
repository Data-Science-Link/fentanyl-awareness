# Final Datasets

This folder contains polished, ready-to-use CSV files with fentanyl-related mortality data. These datasets are cleaned, validated, and formatted for immediate analysis.

**Note on Tone**: This project is dedicated to the memory of those lost to the fentanyl crisis. We believe that transparency and access to granular data are essential steps toward understanding and eventually overcoming this tragedy. Every data point here represents a life lost too soon.

## 📊 Available Dataset

### Fentanyl Deaths Over Time
- **File**: `fact_fentanyl_deaths_over_time.csv`
- **Description**: Comprehensive dataset combining all CDC sources (1999-current) with census demographics.
- **Includes**: Death counts, population data, economic indicators, data source tracking.
- **Time Period**: 1999-current
- **Update Frequency**: Weekly (every Monday at 12:00 PM UTC)

### Key Features
- **Clean Data**: All missing values handled, data types standardized.
- **Geographic Coverage**: State-level aggregation.
- **Time Series**: Historical trends from 1999 to present.
- **Demographics**: Population, income, and unemployment data from US Census.

## 📈 Data Dictionary

| Column | Description | Type |
|--------|-------------|------|
| `year` | Year of data (e.g., 2023) | Integer |
| `month` | Month represented as the first day of the month (e.g., 2023-01-01) | Date |
| `state` | State name | String |
| `deaths` | Number of synthetic opioid deaths (ICD-10 code T40.4). Note: Provisional API data may be reported as 12-month rolling totals depending on the source availability. | Integer |
| `data_source` | Source dataset (e.g., "CDC SODA API") | String |
| `population` | State population from US Census Bureau | Integer |
| `median_household_income` | Median household income in dollars from US Census Bureau | Float |
| `unemployment_rate` | Unemployment rate percentage from US Census Bureau | Float |

## 📥 How to Use

1. **Download** the CSV files directly.
2. **Import** into your preferred analysis tool (Excel, R, Python, Tableau, etc.).
3. **Analyze** using the provided data dictionary.

## 🔄 Data Updates

This dataset is automatically updated **every Monday at 12:00 PM UTC** through our GitHub Actions pipeline.
