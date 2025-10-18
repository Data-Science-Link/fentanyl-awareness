# Fentanyl Awareness Data Pipeline

An open-source, automated data pipeline that extracts CDC WONDER synthetic opioid mortality data, transforms it using modern analytics engineering practices, and publishes results to a continuously updating Tableau Public dashboard.

## 🎯 Project Overview

This project provides a fully automated, reproducible data pipeline that:

- **Extracts** synthetic opioid mortality data from CDC WONDER API (datasets D77, D157, D176)
- **Transforms** data using dbt with DuckDB for robust, testable analytics
- **Loads** processed data to Google Sheets for Tableau Public consumption
- **Automates** the entire pipeline with GitHub Actions on a monthly schedule

## 📂 Folder Organization

The project is organized into three main folders for different user needs:

### 🔧 Data-Extraction-and-Transformation
Contains all technical components for data engineers and developers who want to replicate or modify the pipeline. Includes Python scripts, dbt models, raw data sources, and configuration files.

### 📊 Final-Datasets  
Contains polished, ready-to-use CSV files for researchers, analysts, and anyone who just wants the data without technical setup. These files are cleaned, validated, and formatted for immediate analysis.

### 📈 Data-Visualization
Contains Tableau workbooks and links to interactive dashboards for data visualization and exploration. Perfect for creating presentations and sharing insights.

## 🏗️ Architecture

```
CDC WONDER API → Python Extraction → DuckDB → dbt Transformations → Google Sheets → Tableau Public
```

### Technology Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Data Engine** | DuckDB (via dbt-duckdb) | Embedded, zero-setup analytical database |
| **Transformations** | dbt | SQL-based data modeling with testing & documentation |
| **Extraction** | Python (requests) | CDC WONDER API integration |
| **Automation** | GitHub Actions | Monthly pipeline scheduling |
| **Visualization** | Google Sheets → Tableau Public | Free, auto-refreshing data connector |

## 📊 Data Sources

The pipeline extracts data from three CDC WONDER datasets:

- **D77**: Official mortality data (1999-2020) - Multiple Cause of Death
- **D157**: Official mortality data (2018-2023) - Multiple Cause of Death, Single Race  
- **D176**: Provisional mortality data (2023-current) - Provisional Mortality Statistics

All datasets focus on synthetic opioid deaths (ICD-10 code T40.4).

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- Google Cloud Service Account (for Sheets API)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/fentanyl-awareness.git
   cd fentanyl-awareness
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Sheets credentials and sheet ID
   ```

4. **Set up Google Sheets API**
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create a Service Account and download credentials JSON
   - Share your Google Sheet with the service account email
   - Place credentials file as `service_account.json`

5. **Run the pipeline**
   ```bash
   # Navigate to the technical folder
   cd Data-Extraction-and-Transformation
   
   # Extract data from CDC WONDER
   python extract_data.py
   
   # Transform data with dbt
   cd dbt
   dbt deps
   dbt seed
   dbt run
   dbt test
   
   # Load to Google Sheets
   cd ..
   python load_gcloud.py
   ```

## 📁 Project Structure

```
fentanyl-awareness/
├── Data-Extraction-and-Transformation/    # Technical pipeline components
│   ├── dbt/                              # dbt project for data transformations
│   ├── elt/                              # Extract, Load, Transform scripts
│   ├── cleaned_datasets/                 # Intermediate processed data
│   ├── extract_data.py                   # CDC WONDER data extraction
│   ├── load_gcloud.py                    # Google Sheets integration
│   ├── requirements.txt                  # Python dependencies
│   └── README.md                         # Technical documentation
├── Final-Datasets/                       # Ready-to-use CSV files
│   ├── synthetic_opioid_deaths_sample.csv
│   └── README.md                         # Dataset documentation
├── Data-Visualization/                   # Tableau workbooks and dashboards
│   ├── tableau_workbooks_placeholder.txt
│   └── README.md                         # Visualization documentation
└── README.md                             # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Google Sheets API Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# CDC WONDER API Configuration  
CDC_WONDER_BASE_URL=https://wonder.cdc.gov/controller/datarequest
CDC_WONDER_TIMEOUT=600

# Data Configuration
DATA_DIRECTORY=./data
SEEDS_DIRECTORY=./dbt/seeds
```

### GitHub Secrets

For automated runs, configure these repository secrets:

- `GOOGLE_SHEETS_CREDENTIALS_FILE`: Contents of your service account JSON
- `GOOGLE_SHEET_ID`: Your Google Sheet ID

## 📈 Data Models

### Staging Models

- `stg_d77_official_1999_2020`: Cleaned D77 data
- `stg_d157_official_2018_2023`: Cleaned D157 data  
- `stg_d176_provisional_2023_current`: Cleaned D176 data

### Mart Models

- `fct_synthetic_opioid_deaths`: Unified fact table combining all datasets

### Key Features

- **Data Quality Flags**: Identifies zero deaths, missing population data
- **Time Period Categorization**: Historical, Recent Official, Provisional
- **Rate Calculations**: Both crude and age-adjusted death rates
- **Population Size Categories**: Small, Medium, Large, Very Large counties
- **Deduplication**: Handles overlapping time periods between datasets

## 🤖 Automation

The pipeline runs automatically via GitHub Actions:

- **Schedule**: Monthly on the 1st day at midnight UTC
- **Manual Trigger**: Available via GitHub Actions UI
- **Failure Notifications**: Creates GitHub issues on pipeline failures
- **Artifact Storage**: Preserves logs and database files for 30 days

## 📊 Tableau Public Integration

1. **Connect Tableau Public** to your Google Sheet
2. **Enable Auto-Refresh** for daily data updates
3. **Publish Dashboard** with auto-sync enabled

The Google Sheet acts as a free, non-expiring data bridge that enables automated refreshes on Tableau Public.

## 🧪 Testing

Run data quality tests:

```bash
cd dbt
dbt test
```

Tests include:
- Not null constraints on key fields
- Data freshness checks
- Referential integrity between models

## 🔍 Monitoring

### Data Quality Metrics

The pipeline tracks:
- **Data Freshness**: When each dataset was last updated
- **Completeness**: Missing values and zero-population counties
- **Accuracy**: Calculated vs. provided death rates

### Logging

All scripts include comprehensive logging:
- Extraction progress and API response times
- Transformation row counts and data quality issues
- Upload status and batch processing details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CDC WONDER**: For providing comprehensive mortality data
- **dbt Labs**: For the excellent data transformation framework
- **DuckDB**: For the embedded analytical database
- **Google**: For free Sheets API access

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Check the [documentation](docs/)
- Review the [FAQ](docs/FAQ.md)

---

**Note**: This pipeline is designed for educational and awareness purposes. Always verify data accuracy and consult official sources for policy decisions.