# Google Sheets Integration

This directory contains scripts and configuration for automatically exporting fentanyl awareness data to Google Sheets for easy access and visualization.

## 🚀 Quick Start

### 1. Run Setup Script
```bash
cd data_extraction_and_transformation/google_sheets
python setup_gsheets.py
```

### 2. Follow the Interactive Setup
The setup script will guide you through:
- Creating Google Cloud project
- Enabling APIs
- Creating service account
- Setting up credentials
- Configuring GitHub secrets

### 3. Test Locally
```bash
cd data_extraction_and_transformation/google_sheets
export GOOGLE_SHEET_ID="your_sheet_id_here"
python test_gsheets.py  # Test everything
python load_gcloud.py   # Upload data
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `load_gcloud.py` | Main script for uploading data to Google Sheets |
| `setup_gsheets.py` | Interactive setup and validation script |
| `config.env.example` | Environment variables template |
| `requirements.txt` | Python dependencies |

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `google_sheets` folder with:
```bash
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
CSV_FILE_PATH=../../final_datasets/fact_fentanyl_deaths_over_time.csv
WORKSHEET_NAME=Fentanyl Deaths Over Time
```

### Google Sheets Setup
1. **Create Google Cloud Project**
2. **Enable APIs**: Google Sheets API, Google Drive API
3. **Create Service Account** with JSON key
4. **Create Google Sheet** and share with service account
5. **Set GitHub Secrets** for automated runs

## 🤖 GitHub Actions Integration

The workflow (`.github/workflows/weekly-data-pipeline.yml`) automatically:
- Runs every Monday at 6 AM UTC
- Extracts data from CDC WONDER and Census
- Processes data through dbt
- Exports to Google Sheets
- Can be triggered manually

### Required GitHub Secrets
- `GOOGLE_SHEET_ID`: Your Google Sheet ID
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Full JSON content of service account file

## 📊 Data Structure

The exported data includes:
- **Year/Month**: Time period
- **State**: Geographic location
- **Deaths**: Number of fentanyl-related deaths
- **Data Source**: CDC WONDER source (Official/Provisional)
- **Population**: State population data
- **Economic Data**: Median income, unemployment rate

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify service account JSON file
   - Check Google Cloud project APIs are enabled
   - Ensure service account has access to the sheet

2. **Sheet Not Found**
   - Verify GOOGLE_SHEET_ID is correct
   - Check sheet is shared with service account email
   - Ensure sheet exists and is accessible

3. **Data Upload Fails**
   - Check CSV file exists and has data
   - Verify worksheet name doesn't conflict
   - Check API quotas and limits

### Debug Mode
Run with verbose logging:
```bash
cd data_extraction_and_transformation/google_sheets
python load_gcloud.py --verbose
```

## 🔄 Manual Data Refresh

To manually refresh data:
1. Run dbt models: `cd data_extraction_and_transformation/data_engineering && dbt run`
2. Export to sheets: `cd data_extraction_and_transformation/google_sheets && python load_gcloud.py`

## 📈 Monitoring

The GitHub Action provides:
- Success/failure notifications
- Data artifacts for download
- Logs for troubleshooting
- Weekly schedule with manual trigger option

## 🛡️ Security

- Service account credentials are stored as GitHub secrets
- Credentials are cleaned up after each run
- Minimal permissions (only Sheets and Drive APIs)
- No sensitive data in logs

## 📞 Support

For issues with Google Sheets integration:
1. Check the troubleshooting section
2. Review GitHub Action logs
3. Validate setup with `python setup_gsheets.py`
4. Open a GitHub issue with error details
