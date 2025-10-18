# CDC_WONDER Data Source

This folder contains CDC WONDER (Wide-ranging Online Data for Epidemiologic Research) data files and documentation.

## 📊 Current Datasets

### Request Files (.xml)
- `Official_1999-2020_Synthetic_Opioid_Deaths-req.xml` - Historical mortality data (D77)
- `Official_2018-2023_Synthetic_Opioid_Deaths-req.xml` - Recent official mortality data (D157)
- `Provisional_Mortality_Statistics_2018_through_Last_Week_1760806798363-req.xml` - Provisional mortality data (D176)

### Extraction Script
- `cdc_wonder_extractor.py` - Automated data extraction script that processes XML request files and saves results as CSV files

### Documentation
- `Screenshot_2025-10-12_at_5.42.48_PM.png` - CDC WONDER interface screenshot
- `Screenshot_2025-10-12_at_5.42.54_PM.png` - Data request configuration
- `Screenshot_2025-10-12_at_5.43.00_PM.png` - Query results preview

## 🔗 Data Source Information

- **Source**: CDC WONDER API
- **Datasets**: D77, D157, D176
- **Focus**: Synthetic opioid deaths (ICD-10 code T40.4)
- **Time Period**: 1999-present
- **Geographic Coverage**: National, state, and county level
- **Update Frequency**: Monthly for provisional data

## 📈 Data Characteristics

- **Official Data**: Complete, validated mortality records
- **Provisional Data**: Preliminary data with potential revisions
- **Demographics**: Age, gender, race/ethnicity breakdowns
- **Rates**: Both crude and age-adjusted death rates
- **Population Data**: Census population estimates

## 🚀 Usage

### Automated Extraction
Run the extraction script to process all XML request files:
```bash
python cdc_wonder_extractor.py
```

This will create CSV files in the `../../dbt/seeds/` directory:
- `d176_provisional_2018_current.csv`
- `d77_official_1999_2020.csv` 
- `d157_official_2018_2023.csv`

### Manual Usage
These XML request files can also be used to:
1. Replicate data extractions from CDC WONDER
2. Modify queries for different time periods or demographics
3. Document the exact parameters used in data collection
4. Troubleshoot data extraction issues

## 🔄 Future Updates

This folder will be updated monthly as new provisional data becomes available through the automated pipeline.
