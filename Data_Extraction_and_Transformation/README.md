# Data_Extraction_and_Transformation

This folder contains all the technical components for extracting, processing, and transforming fentanyl-related mortality data from CDC WONDER.

## 📁 Contents

### Python Scripts
- `extract_data.py` - CDC WONDER API data extraction
- `load_gcloud.py` - Google Sheets integration for data loading
- `manual_download_helper.py` - Helper script for manual data downloads
- `test_pipeline.py` - Pipeline testing and validation

### Data Engineering
- `dbt/` - Complete dbt project for data transformations
  - `models/staging/` - Data cleaning and staging models
  - `models/marts/` - Final analytical models
  - `seeds/` - Raw data files
  - `tests/` - Data quality tests
  - `macros/` - Reusable SQL macros
- `dbt_project.yml` - dbt configuration
- `requirements.txt` - Python dependencies
- `setup.py` - Package setup configuration

### Raw Data Sources
- `elt/extract/source_wonder/` - CDC WONDER XML request files and documentation
- `elt/transform/` - Data transformation scripts
- `elt/load/` - Data loading utilities

### Processed Data
- `cleaned_datasets/` - Intermediate cleaned data files

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git
- DuckDB CLI (optional, for direct database queries)

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install DuckDB CLI (optional)**:
   ```bash
   # On macOS with Homebrew
   brew install duckdb
   
   # On Ubuntu/Debian
   sudo apt-get install duckdb
   
   # On Windows with Chocolatey
   choco install duckdb
   
   # Or download from: https://duckdb.org/docs/installation/
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the extraction pipeline**:
   ```bash
   python extract_data.py
   ```

5. **Transform data with dbt**:
   ```bash
   cd dbt
   dbt deps
   dbt seed
   dbt run
   dbt test
   ```

6. **Load to Google Sheets**:
   ```bash
   cd ..
   python load_gcloud.py
   ```

## 🔍 Querying Your Data

### Using DuckDB CLI

Once you've run the pipeline, you can query your data directly using DuckDB CLI:

```bash
# Connect to your database
duckdb fentanyl_awareness.duckdb

# List available tables
.tables

# Explore raw data
SELECT * FROM main.d176_provisional_2018_current LIMIT 5;

# Query cleaned staging data (after dbt run)
SELECT * FROM main.stg_cdc_wonder_fentanyl_deaths_provisional_2018_current LIMIT 5;

# Top states by deaths
SELECT residence_state, SUM(deaths) as total_deaths 
FROM main.stg_cdc_wonder_fentanyl_deaths_provisional_2018_current 
GROUP BY residence_state 
ORDER BY total_deaths DESC 
LIMIT 10;

# Export results to CSV
.output results.csv
SELECT * FROM main.stg_cdc_wonder_fentanyl_deaths_provisional_2018_current;
.output stdout
```

### Using Python Scripts

We've included query tools for programmatic access:

```bash
# Interactive query tool
python3 query_tool.py

# Or run individual queries
python3 -c "
import duckdb
conn = duckdb.connect('fentanyl_awareness.duckdb')
result = conn.execute('SELECT COUNT(*) FROM main.d176_provisional_2018_current').fetchdf()
print(result)
conn.close()
"
```

## 🔧 Technical Details

This folder contains the complete data engineering pipeline that:
- Extracts data from CDC WONDER API (datasets D77, D157, D176)
- Transforms data using dbt with DuckDB
- Implements data quality tests and validation
- Automates the entire process with GitHub Actions

For detailed technical documentation, see the individual script files and dbt model documentation.
