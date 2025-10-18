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

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the extraction pipeline**:
   ```bash
   python extract_data.py
   ```

4. **Transform data with dbt**:
   ```bash
   cd dbt
   dbt deps
   dbt seed
   dbt run
   dbt test
   ```

5. **Load to Google Sheets**:
   ```bash
   cd ..
   python load_gcloud.py
   ```

## 🔧 Technical Details

This folder contains the complete data engineering pipeline that:
- Extracts data from CDC WONDER API (datasets D77, D157, D176)
- Transforms data using dbt with DuckDB
- Implements data quality tests and validation
- Automates the entire process with GitHub Actions

For detailed technical documentation, see the individual script files and dbt model documentation.
