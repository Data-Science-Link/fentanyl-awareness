# Data Sources

This directory contains all data sources for the fentanyl awareness pipeline, including extraction scripts, documentation, and configuration files.

## 📊 Available Data Sources

### 1. CDC WONDER (`cdc_wonder/`)
**Status**: ✅ Active - Fully implemented and operational

**Overview**: CDC WONDER (Wide-ranging Online Data for Epidemiologic Research) provides comprehensive mortality data for synthetic opioid deaths.

**Datasets**:
- **D77**: Official mortality data (1999-2020) - Multiple Cause of Death
- **D157**: Official mortality data (2018-2023) - Multiple Cause of Death, Single Race
- **D176**: Provisional mortality data (2018-current) - Provisional Mortality Statistics

**Key Features**:
- **Focus**: Synthetic opioid deaths (ICD-10 code T40.4)
- **Time Period**: 1999-present
- **Geographic Coverage**: National, state, and county level
- **Update Frequency**: Monthly for provisional data
- **Data Types**: Death counts, rates, demographics, population estimates

**Files**:
- `cdc_wonder_extractor.py` - Automated data extraction script
- `Multiple Cause of Death, 1999-2020_1760923374111-req.xml` - Historical data request
- `Multiple Cause of Death, 2018-2023, Single Race_1760923356309-req.xml` - Recent official data request
- `Official_2018-2023_Synthetic_Opioid_Deaths-req.xml` - Official data request (Alternative)
- Screenshots documenting the CDC WONDER interface and configuration

**Usage**:
```bash
cd cdc_wonder
python cdc_wonder_extractor.py
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

### 3. Customs and Border Control (`customs_and_border_control/`)
**Status**: 🚧 Planned - Placeholder for future implementation

**Overview**: U.S. Customs and Border Protection (CBP) data related to fentanyl seizures and interdictions.

**Planned Datasets**:
- **Seizure Data**: Fentanyl seizure quantities by port of entry
- **Border Statistics**: Port traffic volumes, inspection statistics
- **Enforcement Data**: Resource allocation, detection methods
- **Geographic Data**: Border regions, port locations

**Integration Goals**:
- Correlate seizure trends with overdose patterns
- Analyze effectiveness of border enforcement
- Identify geographic hotspots for supply and demand
- Support policy analysis and resource allocation

## 🔧 Data Integration

### Current Pipeline
```
CDC WONDER → Python Extraction → DuckDB → dbt Transformations → Google Sheets
Census ACS → Python Extraction → DuckDB → dbt Transformations → Google Sheets
```

### Future Pipeline
```
CDC WONDER → Python Extraction → DuckDB → dbt Transformations → Google Sheets
Census ACS → Python Extraction → DuckDB → dbt Transformations → Google Sheets
CBP Data   → Python Extraction → DuckDB → dbt Transformations → Google Sheets
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

2. **Configure Census API** (if using ACS data):
   ```bash
   echo "CENSUS_API_KEY=your_key_here" > .env
   ```

3. **Extract data**:
   ```bash
   # CDC WONDER data
   cd data_sources/cdc_wonder
   python cdc_wonder_extractor.py

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

## 📈 Data Quality

### CDC WONDER
- **Official Data**: Complete, validated mortality records
- **Provisional Data**: Preliminary data with potential revisions
- **Demographics**: Age, gender, race/ethnicity breakdowns
- **Rates**: Both crude and age-adjusted death rates

### Census ACS
- **Population Data**: Census population estimates
- **Economic Data**: Median income, unemployment rates
- **Geographic Coverage**: State-level data
- **Update Frequency**: Annual updates

## 🔒 Security & Privacy

- **API Keys**: Stored in `.env` files (not committed to git)
- **Data Sources**: All sources are publicly available
- **No PII**: No personally identifiable information collected
- **Compliance**: Follows data source terms of service

## 📝 Troubleshooting

### CDC WONDER Issues
- **XML Request Files**: Can be used to replicate extractions manually
- **API Timeouts**: Built-in retry logic and timeout handling
- **Data Validation**: Automated checks for data completeness

### Census ACS Issues
- **API Key**: Verify `.env` file exists with correct format
- **Rate Limiting**: Free tier allows 500 requests per day
- **Dependencies**: Ensure all Python packages are installed

### General Issues
- **Network Connectivity**: Required for API calls
- **File Permissions**: Ensure write access to output directories
- **Python Environment**: Use virtual environment for dependencies

## 🔄 Future Development

### Planned Enhancements
1. **CBP Data Integration**: Border control and seizure data
2. **Third Source Addition**: Healthcare, law enforcement, or economic data
3. **Real-time Updates**: Automated daily/weekly data refreshes
4. **Data Validation**: Enhanced quality checks and monitoring
5. **API Improvements**: Better error handling and retry logic

### Contributing
When adding new data sources:
1. Create new subdirectory in `data_sources/`
2. Include extraction script and documentation
3. Update this README with source information
4. Add integration to dbt models
5. Test with existing pipeline

## 📞 Support

For questions about data sources:
- **CDC WONDER**: Check CDC WONDER documentation and API
- **Census ACS**: Review Census API documentation
- **General**: Open GitHub issue with specific data source questions
- **Pipeline Issues**: Check dbt logs and error messages
