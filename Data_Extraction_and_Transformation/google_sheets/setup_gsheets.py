#!/usr/bin/env python3
"""
Google Sheets Setup Script

This script helps set up Google Sheets integration for the fentanyl awareness project.
It guides you through creating a Google Cloud project, enabling APIs, and creating
service account credentials.
"""

import os
import json
from pathlib import Path

def print_setup_instructions():
    """Print step-by-step setup instructions."""
    print("=" * 60)
    print("GOOGLE SHEETS SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    
    print("1. CREATE GOOGLE CLOUD PROJECT:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Create a new project or select existing one")
    print("   - Note your Project ID")
    print()
    
    print("2. ENABLE REQUIRED APIs:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Enable 'Google Sheets API'")
    print("   - Enable 'Google Drive API'")
    print()
    
    print("3. CREATE SERVICE ACCOUNT:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'Service Account'")
    print("   - Name: 'fentanyl-data-loader'")
    print("   - Description: 'Service account for automated data loading'")
    print("   - Click 'Create and Continue'")
    print("   - Skip role assignment for now")
    print("   - Click 'Done'")
    print()
    
    print("4. CREATE SERVICE ACCOUNT KEY:")
    print("   - Find your service account in the list")
    print("   - Click on it, then go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key'")
    print("   - Choose 'JSON' format")
    print("   - Download the JSON file")
    print("   - Rename it to 'service_account.json'")
    print("   - Place it in Data_Extraction_and_Transformation/ folder")
    print()
    
    print("5. CREATE GOOGLE SHEET:")
    print("   - Go to https://sheets.google.com/")
    print("   - Create a new spreadsheet")
    print("   - Name it 'Fentanyl Awareness Data'")
    print("   - Copy the Sheet ID from the URL")
    print("   - Share the sheet with your service account email")
    print("   - Give 'Editor' permissions")
    print()
    
    print("6. SET UP GITHUB SECRETS:")
    print("   - Go to your GitHub repository")
    print("   - Settings > Secrets and variables > Actions")
    print("   - Add these secrets:")
    print("     - GOOGLE_SHEET_ID: Your Google Sheet ID")
    print("     - GOOGLE_SERVICE_ACCOUNT_JSON: Contents of service_account.json")
    print()
    
    print("7. TEST LOCALLY:")
    print("   - Set environment variables:")
    print("     export GOOGLE_SHEET_ID='your_sheet_id'")
    print("   - Run: python load_gcloud.py")
    print()

def create_env_template():
    """Create environment template file."""
    template_content = """# Google Sheets Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json

# Data Configuration
CSV_FILE_PATH=../Final_Datasets/fact_fentanyl_deaths_over_time.csv
WORKSHEET_NAME=Fentanyl Deaths Over Time

# Database Configuration
DUCKDB_PATH=fentanyl_awareness.duckdb
"""
    
    env_file = Path(".env")
    env_file.write_text(template_content)
    print(f"Created environment template: {env_file}")
    print("Edit this file with your actual values.")

def validate_setup():
    """Validate the current setup."""
    print("\n" + "=" * 40)
    print("VALIDATING SETUP")
    print("=" * 40)
    
    # Check for service account file
    sa_file = Path("Data_Extraction_and_Transformation/service_account.json")
    if sa_file.exists():
        print("✅ Service account file found")
        try:
            with open(sa_file) as f:
                sa_data = json.load(f)
            print(f"✅ Service account email: {sa_data.get('client_email', 'Not found')}")
        except json.JSONDecodeError:
            print("❌ Service account file is not valid JSON")
    else:
        print("❌ Service account file not found")
    
    # Check for environment variables
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    if sheet_id:
        print(f"✅ GOOGLE_SHEET_ID environment variable set")
    else:
        print("❌ GOOGLE_SHEET_ID environment variable not set")
    
    # Check for CSV file
    csv_file = Path("../../final_datasets/fact_fentanyl_deaths_over_time.csv")
    if csv_file.exists():
        print("✅ Data CSV file found")
    else:
        print("❌ Data CSV file not found - run dbt first")

def main():
    """Main function."""
    print("Fentanyl Awareness - Google Sheets Setup")
    print("This script will help you set up automated Google Sheets export.")
    print()
    
    while True:
        print("\nChoose an option:")
        print("1. Show setup instructions")
        print("2. Create environment template")
        print("3. Validate current setup")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print_setup_instructions()
        elif choice == '2':
            create_env_template()
        elif choice == '3':
            validate_setup()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
