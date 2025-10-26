#!/usr/bin/env python3
"""
Test Script for Google Sheets Integration

This script tests the Google Sheets integration without actually uploading data.
It validates configuration, connectivity, and data format.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from load_gcloud import GoogleSheetsLoader

# Load environment variables from .env file
load_dotenv()

def test_configuration():
    """Test if all required configuration is present."""
    print("🔍 Testing Configuration...")

    # Check for service account file
    sa_file = Path("service_account.json")
    if not sa_file.exists():
        print("❌ service_account.json not found")
        return False

    try:
        with open(sa_file) as f:
            sa_data = json.load(f)
        print(f"✅ Service account: {sa_data.get('client_email', 'Unknown')}")
    except json.JSONDecodeError:
        print("❌ service_account.json is not valid JSON")
        return False

    # Check for Google Sheet ID
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID environment variable not set")
        return False
    print(f"✅ Google Sheet ID: {sheet_id[:10]}...")

    # Check for CSV file
    csv_file = Path("../../final_datasets/fact_fentanyl_deaths_over_time.csv")
    if not csv_file.exists():
        print("❌ Data CSV file not found")
        return False
    print(f"✅ Data file: {csv_file}")

    return True

def test_google_sheets_connection():
    """Test connection to Google Sheets."""
    print("\n🔗 Testing Google Sheets Connection...")

    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    loader = GoogleSheetsLoader("service_account.json", sheet_id)

    try:
        if loader.authenticate_google_sheets():
            print("✅ Successfully authenticated with Google Sheets")

            # Try to open the spreadsheet
            spreadsheet = loader.gc.open_by_key(sheet_id)
            print(f"✅ Successfully opened spreadsheet: {spreadsheet.title}")
            return True
        else:
            print("❌ Failed to authenticate with Google Sheets")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_data_export():
    """Test data export functionality."""
    print("\n📊 Testing Data Export...")

    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    loader = GoogleSheetsLoader("service_account.json", sheet_id)

    try:
        csv_data = loader.export_data_to_csv()
        if csv_data:
            lines = csv_data.count('\n')
            print(f"✅ Successfully exported {lines} rows of data")
            return True
        else:
            print("❌ Failed to export data")
            return False
    except Exception as e:
        print(f"❌ Data export test failed: {e}")
        return False

def test_dry_run():
    """Test the complete process without uploading."""
    print("\n🧪 Testing Complete Process (Dry Run)...")

    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    loader = GoogleSheetsLoader("service_account.json", sheet_id)

    try:
        # Test authentication
        if not loader.authenticate_google_sheets():
            print("❌ Authentication failed")
            return False

        # Test data export
        csv_data = loader.export_data_to_csv()
        if not csv_data:
            print("❌ Data export failed")
            return False

        print("✅ All components working correctly")
        print("✅ Ready for production upload")
        return True

    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Google Sheets Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Configuration", test_configuration),
        ("Google Sheets Connection", test_google_sheets_connection),
        ("Data Export", test_data_export),
        ("Dry Run", test_dry_run)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your Google Sheets integration is ready.")
        print("\nTo upload data, run:")
        print("python load_gcloud.py")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
