# Workflow Templates

This folder contains GitHub Actions workflow templates and documentation for automated data processing and deployment.

**Note**: These are template files for reference. The actual GitHub Actions workflows are located in `.github/workflows/` at the project root.

## 📁 Files

| File | Purpose |
|------|---------|
| `weekly-data-pipeline.yml` | Template for automated weekly data extraction and Google Sheets export |

## 🔄 How GitHub Actions Actually Works

### **Active Workflows**
- **Location**: `.github/workflows/` (project root)
- **Control**: GitHub automatically detects and runs workflows from this location
- **Current**: `weekly-data-pipeline.yml` (updated for new folder structure)

### **This Folder**
- **Purpose**: Documentation and template storage
- **Impact**: **ZERO** - GitHub ignores this folder completely
- **Value**: Reference copies and documentation

## 🔄 Workflows

### Weekly Data Pipeline

**Trigger**: Every Monday at 6 AM UTC + Manual trigger

**Steps**:
1. **Checkout** repository
2. **Setup** Python environment
3. **Install** dependencies (dbt, Python packages)
4. **Extract** data from CDC WONDER
5. **Extract** data from Census ACS
6. **Process** data through dbt models
7. **Test** data quality
8. **Export** to Google Sheets
9. **Upload** artifacts
10. **Cleanup** credentials

## 🔧 Configuration

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `GOOGLE_SHEET_ID` | Google Sheet ID for data export |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account credentials JSON |

### Setup Instructions

1. **Enable GitHub Actions** in repository settings
2. **Add secrets** in Settings > Secrets and variables > Actions
3. **Copy workflow** to `.github/workflows/` directory
4. **Test** with manual trigger

## 📊 Monitoring

- **Success notifications** via GitHub
- **Failure alerts** with detailed logs
- **Artifact downloads** for data files
- **Manual triggers** for immediate updates

## 🛠️ Customization

### Schedule Changes
Edit the cron expression in `weekly-data-pipeline.yml`:
```yaml
schedule:
  - cron: '0 6 * * 1'  # Monday 6 AM UTC
```

### Additional Data Sources
Add new extraction steps:
```yaml
- name: Run New Data Source
  run: |
    cd Data_Extraction_and_Transformation/data_sources/New_Source
    python extractor.py
```

### Environment Variables
Add environment variables for different configurations:
```yaml
env:
  NEW_VARIABLE: ${{ secrets.NEW_SECRET }}
```

## 🔍 Troubleshooting

### Common Issues

1. **Workflow not triggering**
   - Check cron schedule syntax
   - Verify GitHub Actions are enabled
   - Check repository permissions

2. **Data extraction fails**
   - Review API rate limits
   - Check data source availability
   - Verify credentials

3. **Google Sheets upload fails**
   - Validate service account permissions
   - Check sheet sharing settings
   - Review API quotas

### Debug Steps

1. **Check workflow logs** in Actions tab
2. **Test locally** with same commands
3. **Validate secrets** are properly set
4. **Review error messages** for specific issues

## 📈 Performance

- **Runtime**: ~10-15 minutes
- **Resource usage**: Standard GitHub runner
- **Storage**: Temporary files cleaned up
- **Bandwidth**: Minimal data transfer

## 🔒 Security

- **Secrets management** via GitHub
- **Credential cleanup** after each run
- **Minimal permissions** for service accounts
- **No sensitive data** in logs
