# Google Sheets Integration

This directory contains scripts and configuration for automatically exporting fentanyl awareness data to Google Sheets for easy access and visualization.

## 🚀 Quick Start

### 1. Google Cloud Setup
1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Note your Project ID

2. **Enable Required APIs**
   - Go to "APIs & Services" → "Library"
   - Enable "Google Sheets API"
   - Enable "Google Drive API"

3. **Create Service Account**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: `fentanyl-data-loader`
   - Description: `Service account for automated data loading`
   - Click "Create and Continue" → "Done"

4. **Create Service Account Key**
   - Find your service account in the list
   - Click on it → "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Download and rename to `service_account.json`
   - Place in `data_engineering/google_sheets/` folder

### 2. Google Sheet Setup
1. **Create Google Sheet**
   - Go to [Google Sheets](https://sheets.google.com/)
   - Create new spreadsheet
   - Name it "Fentanyl Awareness Data"
   - Copy Sheet ID from URL

2. **Share with Service Account**
   - Click "Share" button
   - Add service account email: `fentanyl-data-loader@your-project-id.iam.gserviceaccount.com`
   - Give "Editor" permissions

### 3. Environment Configuration
Create `.env` file at project root (copy from `.env.example`):
```bash
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
CSV_FILE_PATH=Final_Datasets/fact_fentanyl_deaths_over_time.csv
```

### 4. Test Setup
```bash
cd data_engineering/google_sheets
python test_gsheets.py  # Test everything
python load_gcloud.py   # Upload data
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `load_gcloud.py` | Main script for uploading data to Google Sheets |
| `test_gsheets.py` | Test script to validate setup and connectivity |
| `service_account.json` | Google Cloud service account credentials (not committed) |
| `README.md` | This documentation |

## 🔧 Configuration

### Environment Variables
Ensure your `.env` file at the project root contains:
```bash
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
CSV_FILE_PATH=Final_Datasets/fact_fentanyl_deaths_over_time.csv
WORKSHEET_NAME=Fentanyl Deaths Over Time
```

### Google Sheets Setup Summary
1. **Create Google Cloud Project** and enable **Google Sheets** and **Google Drive** APIs.
2. **Create Service Account** with a JSON key, rename to `service_account.json` and place it in this directory.
3. **Create Google Sheet** and share it with the service account email as "Editor".
4. **Set GitHub Secrets** (`GOOGLE_SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`) for automated runs.

## 🤖 GitHub Actions Integration

The workflow (`.github/workflows/weekly-data-refresh.yml`) automatically:
- Runs every Monday at 12:00 PM UTC
- Processes data through dbt transformations
- Generates final CSV and updates documentation
- Exports to Google Sheets (only if CSV has changed)
- Can be triggered manually via workflow_dispatch

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
cd data_engineering/google_sheets
python load_gcloud.py
```

## 🔄 Manual Data Refresh

To manually refresh data:
1. Run dbt models: `cd data_engineering/data_build_tool && dbt run`
2. Export to sheets: `cd data_engineering/google_sheets && python load_gcloud.py`

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
3. Validate setup with `python test_gsheets.py`
4. Open a GitHub issue with error details
