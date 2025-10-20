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
- `data_sources/CDC_WONDER/` - CDC WONDER XML request files and documentation
- `data_sources/Census_ACS/` - US Census Bureau data extraction scripts
- `data_sources/Customs_and_Border_Control/` - Border control data (placeholder)
- `data_sources/Third_Source/` - Additional data sources (placeholder)

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

## 🏛️ Census Data Integration

### Overview
The pipeline now includes US Census Bureau data integration for enhanced demographic analysis:

- **Population Estimates Program (PEP)** - State-level population data
- **American Community Survey (ACS)** - Economic and demographic indicators
- **Automated extraction** - Python scripts for API data retrieval
- **dbt integration** - Staging models and mart models for analysis

### Setup Census Data

1. **Get Census API Key**:
   ```bash
   # Visit: https://api.census.gov/data/key_signup.html
   # Add to environment or .env file:
   export CENSUS_API_KEY='your_api_key_here'
   ```

2. **Run Census Setup**:
   ```bash
   cd data_sources/Census_ACS
   python3 setup_census.py
   ```

3. **Extract Census Data**:
   ```bash
   python3 census_extractor.py
   ```

4. **Load into dbt**:
   ```bash
   cd ../../
   dbt seed
   dbt run
   ```

### Available Census Models

- `stg_census_state_population` - Cleaned population estimates
- `stg_census_state_economic` - Economic indicators
- `fct_synthetic_opioid_deaths_with_population` - Combined mortality + population data

### Sample Queries with Population Data

```sql
-- Mortality rates per 100,000 population
SELECT 
    residence_state,
    year,
    SUM(deaths) as total_deaths,
    AVG(population) as avg_population,
    ROUND(SUM(deaths)::decimal / AVG(population) * 100000, 2) as death_rate_per_100k
FROM main.fct_synthetic_opioid_deaths_with_population
WHERE population IS NOT NULL
GROUP BY residence_state, year
ORDER BY death_rate_per_100k DESC
LIMIT 10;
```

## 🔧 Technical Details

This folder contains the complete data engineering pipeline that:
- Extracts data from CDC WONDER API (datasets D77, D157, D176)
- Integrates US Census Bureau demographic and economic data
- Transforms data using dbt with DuckDB
- Implements data quality tests and validation
- Automates the entire process with GitHub Actions

For detailed technical documentation, see the individual script files and dbt model documentation.
