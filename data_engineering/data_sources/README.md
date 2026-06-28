# Data Sources

This directory identifies the primary sources of information used to track the fentanyl crisis. Accuracy is paramount because we are documenting a human tragedy; we rely on official sources like the CDC and US Census Bureau to ensure the information we provide is as reliable as possible.

## 📊 Available Data Sources

### 1. CDC SODA API (`cdc_api/`)
**Status**: ✅ Active - Primary Data Source

**Overview**: The CDC SODA (Socrata Open Data API) provides modern REST API access to provisional drug overdose death counts. This is our primary source for fentanyl death data.

**Datasets**:
- **VSRR**: Vital Statistics Rapid Release Provisional Drug Overdose Death Counts

**Key Features**:
- **Focus**: Synthetic opioids, excl. methadone (T40.4)
- **Granularity**: National and State-level
- **Metric**: 12 month-ending rolling death counts
- **Programmatic Access**: Uses REST API (SODA) for automated workflows
- **Update Frequency**: Regular provisional updates

**Files**:
- `soda_extractor.py` - Automated extraction script using the SODA API

**Usage**:
```bash
cd cdc_api
python3 soda_extractor.py
```

### 2. Census ACS (`census_acs/`)
**Status**: ✅ Active - Fully implemented and operational

**Overview**: US Census American Community Survey (ACS) provides demographic and economic data for mortality rate calculations.

**Data Types**:
- **Population Estimates**: State-level population data (2018-2022)
- **Economic Indicators**: Income, unemployment, labor force statistics
- **Demographics**: Data for mortality rate calculations

**Setup Requirements**:
1. **Get Census API Key**: Visit https://api.census.gov/data/key_signup.html
2. **Add to Environment**: Create `.env` file at project root with `CENSUS_API_KEY=your_key_here`
3. **Test Connection**: `python3 -c "from census_extractor import test_census_api; test_census_api()"`

**Files**:
- `census_extractor.py` - Main extraction script with all functionality

**Usage**:
```bash
cd census_acs
python3 census_extractor.py
```

**Output**:
- `census_state_population.csv` - Population estimates by state/year
- `census_state_economic.csv` - Economic indicators by state

### 3. CDC WONDER (`cdc_wonder/`)
**Status**: ⚠️ Deprecated - Kept for reference only

**Overview**: CDC WONDER manual downloads were previously used but have been replaced by the programmatic CDC SODA API.

**Note**: The automated extractor `cdc_wonder_extractor.py` is available but no longer used in the main pipeline.

### 4. Customs and Border Control (`customs_and_border_control/`)
**Status**: 🚧 Planned - Placeholder for future implementation

**Overview**: U.S. Customs and Border Protection (CBP) data related to fentanyl seizures and interdictions.

## 🔧 Data Integration

### Current Pipeline
```
CDC SODA API → Python Extraction → DuckDB → dbt Transformations → Google Sheets
Census ACS  → Python Extraction → DuckDB → dbt Transformations → Google Sheets
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Census API key (for ACS data)
- Internet connection for API calls

### Quick Start
1. **Set up environment**:
   ```bash
   cd data_engineering
   pip install -r requirements.txt
   ```

2. **Configure Census API**:
   ```bash
   echo "CENSUS_API_KEY=your_key_here" > .env
   ```

3. **Extract data**:
   ```bash
   # CDC SODA API data
   cd data_sources/cdc_api
   python3 soda_extractor.py

   # Census ACS data
   cd ../census_acs
   python census_extractor.py
   ```

4. **Process with dbt**:
   ```bash
   cd ../../data_build_tool
   dbt seed
   dbt run
   dbt test
   ```
