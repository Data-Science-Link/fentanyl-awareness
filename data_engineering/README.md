# data_engineering

This folder contains all the technical components for extracting, processing, and transforming fentanyl-related mortality data from CDC WONDER.

## 📁 Contents

### Automation & Integration
- `google_sheets/` - Google Sheets export automation
  - `load_gcloud.py` - Main Google Sheets integration script
  - `test_gsheets.py` - Test suite
  - `README.md` - Complete documentation

### Data Engineering
- `data_build_tool/` - Complete dbt project for data transformations
  - `dbt/` - dbt project files
    - `models/staging/` - Data cleaning and staging models
    - `models/marts/` - Final analytical models
    - `seeds/` - Raw data files
    - `tests/` - Data quality tests
    - `macros/` - Reusable SQL macros
  - `dbt_project.yml` - dbt configuration
  - `packages.yml` - dbt package dependencies
  - `fentanyl_awareness.duckdb` - DuckDB database
  - `logs/` - dbt execution logs
  - `target/` - dbt compiled artifacts

### Raw Data Sources
- `data_sources/cdc_wonder/` - CDC WONDER XML request files and documentation
- `data_sources/census_acs/` - US Census Bureau data extraction scripts
- `data_sources/customs_and_border_control/` - Border control data (placeholder)

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
   # Edit .env with your configuration (at project root)
   ```

4. **Transform data with dbt**:
   ```bash
   cd data_build_tool
   dbt deps --profiles-dir ~/.dbt
   dbt seed --profiles-dir ~/.dbt
   dbt run --profiles-dir ~/.dbt
   dbt test --profiles-dir ~/.dbt
   ```

5. **Generate documentation**:
   ```bash
   dbt docs generate --profiles-dir ~/.dbt
   dbt docs serve --profiles-dir ~/.dbt
   ```

6. **Load to Google Sheets** (optional):
   ```bash
   cd google_sheets
   python load_gcloud.py
   ```

## 🔍 Querying Your Data

### Using DuckDB CLI

Once you've run the pipeline, you can query your data directly using DuckDB CLI:

```bash
# Connect to your database
duckdb data_build_tool/fentanyl_awareness.duckdb

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
conn = duckdb.connect('data_build_tool/fentanyl_awareness.duckdb')
result = conn.execute('SELECT COUNT(*) FROM main.d176_provisional_2018_current').fetchdf()
print(result)
conn.close()
"
```

## 📊 Data Sources

This pipeline uses data from:

1. **CDC WONDER** - Mortality data (seeds in `dbt/seeds/`)
2. **US Census** - Population and economic data (seeds in `dbt/seeds/`)

The seed files are automatically loaded when you run `dbt seed`.

### Available dbt Models

**Staging Models**:
- `stg_cdc_wonder_fentanyl_deaths_final_1999_2020` - Historical CDC data
- `stg_cdc_wonder_fentanyl_deaths_final_2018_2023` - Recent CDC data
- `stg_cdc_wonder_fentanyl_deaths_provisional_2018_current` - Provisional data
- `stg_census_state_population` - Population estimates
- `stg_census_state_economic` - Economic indicators

**Mart Models**:
- `fact_fentanyl_deaths_over_time` - Final fact table with all data sources

### Sample Queries

```sql
-- View final dataset
SELECT * FROM main.fact_fentanyl_deaths_over_time LIMIT 10;

-- Deaths by state in 2023
SELECT 
    state,
    SUM(deaths) as total_deaths
FROM main.fact_fentanyl_deaths_over_time
WHERE year = 2023
GROUP BY state
ORDER BY total_deaths DESC;

-- Monthly trends
SELECT 
    year,
    SUM(deaths) as total_deaths
FROM main.fact_fentanyl_deaths_over_time
GROUP BY year
ORDER BY year;
```

## 🤖 GitHub Actions Automation

This pipeline is fully automated with three GitHub workflows:

- **dbt CI/CD**: Runs tests on every push/PR, deploys docs to GitHub Pages
- **Security Audit**: Scans code and dependencies for vulnerabilities  
- **Weekly Data Refresh**: Automated pipeline runs every Monday

All workflows can be manually triggered from the Actions tab.

## 🔧 Technical Details

This folder contains the complete data engineering pipeline that:
- **Loads** data from CSV seed files (CDC WONDER and Census data)
- Transforms data using dbt with DuckDB
- Implements data quality tests and validation
- Automates the entire process with GitHub Actions
- Generates final CSV and documentation

For detailed technical documentation, see the individual dbt model files.
