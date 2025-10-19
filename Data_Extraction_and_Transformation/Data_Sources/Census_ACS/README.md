# Census ACS Data Integration

This directory contains the US Census American Community Survey (ACS) data extraction for the fentanyl awareness pipeline.

## 📊 Data Overview

The American Community Survey (ACS) provides:
- **State-level population estimates** (2018-2022)
- **Economic indicators** (income, unemployment, labor force)
- **Demographic data** for mortality rate calculations

## 🔑 Quick Setup

### 1. Get Census API Key
Visit: https://api.census.gov/data/key_signup.html
- Fill out the form to get your free API key
- You'll receive an email with your API key

### 2. Add API Key to Environment
Create a `.env` file in the `Data_Extraction_and_Transformation` directory:

```bash
cd Data_Extraction_and_Transformation
echo "CENSUS_API_KEY=your_actual_api_key_here" > .env
```

### 3. Test Setup
```bash
cd data_sources/Census_ACS
python3 -c "from census_extractor import test_census_api; test_census_api()"
```

### 4. Extract Data
```bash
python3 census_extractor.py
```

### 5. Load into dbt
```bash
cd ../../
dbt seed
dbt run
```

## 📁 Files

- `census_extractor.py` - Main extraction script with all functionality
- `README.md` - This documentation

## 🔒 Security

Your API key is safe because:
- `.env` files are in `.gitignore` (won't be committed)
- Keys are loaded at runtime, not hardcoded
- Local files stay on your machine

## 🧪 Testing

Test the Census API connection:
```bash
python3 -c "from census_extractor import test_census_api; test_census_api()"
```

## 📊 Data Output

The extractor generates:
- `census_state_population.csv` - Population estimates by state/year
- `census_state_economic.csv` - Economic indicators by state

## 🔄 For Other Developers

When you make the repo public, other developers will:
1. Copy `.env.example` to `.env`
2. Get their own Census API key
3. Add it to their `.env` file
4. Run the extraction

## 📝 Troubleshooting

### "API key not found" error:
- Check that `.env` file exists in `Data_Extraction_and_Transformation/`
- Verify the key format: `CENSUS_API_KEY=your_key_here`

### "Module not found" error:
- Install dependencies: `pip install -r requirements.txt`

### Rate limiting:
- Free tier: 500 requests per day
- Built-in 0.2 second delay between requests