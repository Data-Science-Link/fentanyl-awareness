#!/usr/bin/env python3
"""
Google Sheets Data Loader

This script reads CSV files and uploads them to Google Sheets for Tableau Public consumption.
"""

import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import logging
from typing import Optional
import csv
import io
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheetsLoader:
    """Load data from CSV files to Google Sheets."""
    
    def __init__(self, credentials_file: str, sheet_id: str):
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.gc = None
        
    def authenticate_google_sheets(self) -> bool:
        """Authenticate with Google Sheets API."""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            
            # Authorize and create client
            self.gc = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            return False
    
    def export_data_to_csv(self, csv_file_path: str = "../../final_datasets/fact_fentanyl_deaths_over_time.csv") -> Optional[str]:
        """Export data from CSV file to string."""
        try:
            csv_path = Path(csv_file_path)
            if not csv_path.exists():
                logger.error(f"CSV file not found: {csv_file_path}")
                return None
            
            # Read the CSV file
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_data = file.read()
            
            # Count rows for logging
            row_count = csv_data.count('\n')
            logger.info(f"Exported {row_count} rows from {csv_file_path}")
            return csv_data
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return None
    
    def upload_to_google_sheets(self, csv_data: str, worksheet_name: str = "Synthetic Opioid Deaths") -> bool:
        """Upload CSV data to Google Sheets."""
        try:
            if not self.gc:
                logger.error("Not authenticated with Google Sheets")
                return False
            
            # Open the spreadsheet
            spreadsheet = self.gc.open_by_key(self.sheet_id)
            
            # Try to get existing worksheet, create if doesn't exist
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                logger.info(f"Found existing worksheet: {worksheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
                logger.info(f"Created new worksheet: {worksheet_name}")
            
            # Clear existing data
            worksheet.clear()
            
            # Parse CSV and upload data
            csv_reader = csv.reader(io.StringIO(csv_data))
            rows = list(csv_reader)
            
            # Resize worksheet to accommodate all data
            num_rows = len(rows)
            num_cols = len(rows[0]) if rows else 0
            worksheet.resize(num_rows, num_cols)
            logger.info(f"Resized worksheet to {num_rows} rows × {num_cols} columns")
            
            # Upload data in batches to avoid API limits
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                start_row = i + 1
                end_row = start_row + len(batch) - 1
                
                # Calculate the actual range based on data size
                num_cols = len(batch[0]) if batch else 0
                col_end = chr(ord('A') + num_cols - 1) if num_cols > 0 else 'A'
                
                # Update the worksheet with proper range
                range_name = f'A{start_row}:{col_end}{end_row}'
                worksheet.update(range_name, batch)
                logger.info(f"Uploaded batch {i//batch_size + 1}: rows {start_row}-{end_row}, columns A-{col_end}")
            
            logger.info(f"Successfully uploaded {len(rows)} rows to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to Google Sheets: {e}")
            return False
    
    def load_data(self, csv_file_path: str = "../../final_datasets/fact_fentanyl_deaths_over_time.csv", 
                  worksheet_name: str = "Fentanyl Deaths Over Time") -> bool:
        """Complete data loading process."""
        try:
            # Export data from CSV file
            csv_data = self.export_data_to_csv(csv_file_path)
            if not csv_data:
                return False
            
            # Upload to Google Sheets
            success = self.upload_to_google_sheets(csv_data, worksheet_name)
            return success
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return False
    
    def close_connections(self):
        """Close any open connections."""
        # No database connections to close
        logger.info("No connections to close")

def print_available_exports():
    """Print available export configurations."""
    print("📊 Available Export Configurations:")
    print("=" * 50)
    
    exports = [
        {
            "name": "CDC Mortality Data",
            "worksheet": "CDC Mortality",
            "description": "CDC WONDER mortality data (1999-present)",
            "csv_file": "../../final_datasets/fact_fentanyl_deaths_over_time.csv"
        },
        {
            "name": "Census Population Data", 
            "worksheet": "Census Population",
            "description": "US Census population estimates",
            "csv_file": "../../final_datasets/census_population.csv"
        },
        {
            "name": "Combined Analysis",
            "worksheet": "Combined Analysis", 
            "description": "Combined CDC and Census data",
            "csv_file": "../../final_datasets/combined_analysis.csv"
        }
    ]
    
    for i, export in enumerate(exports, 1):
        print(f"{i}. {export['name']}")
        print(f"   Worksheet: {export['worksheet']}")
        print(f"   Description: {export['description']}")
        print(f"   File: {export['csv_file']}")
        print()

def export_multiple_datasets(loader):
    """Export multiple datasets to different worksheets."""
    logger.info("Starting multi-dataset export to Google Sheets...")
    
    # Define export configurations
    exports = [
        {
            "worksheet": "CDC Mortality",
            "csv_file": "../../final_datasets/fact_fentanyl_deaths_over_time.csv",
            "description": "CDC WONDER mortality data"
        },
        {
            "worksheet": "Census Population", 
            "csv_file": "../../final_datasets/census_state_population.csv",
            "description": "US Census population estimates"
        },
        {
            "worksheet": "Census Economic",
            "csv_file": "../../final_datasets/census_state_economic.csv", 
            "description": "US Census economic indicators"
        }
    ]
    
    success_count = 0
    total_exports = len(exports)
    
    for i, export in enumerate(exports, 1):
        logger.info(f"Exporting {i}/{total_exports}: {export['description']}")
        
        # Check if CSV file exists
        if not os.path.exists(export['csv_file']):
            logger.warning(f"CSV file not found: {export['csv_file']} - skipping")
            continue
            
        # Export to worksheet
        success = loader.load_data(export['csv_file'], export['worksheet'])
        if success:
            success_count += 1
            logger.info(f"✅ Successfully exported to worksheet: {export['worksheet']}")
        else:
            logger.error(f"❌ Failed to export to worksheet: {export['worksheet']}")
    
    logger.info(f"Multi-export completed: {success_count}/{total_exports} successful")
    return success_count == total_exports

def main():
    """Main function to run the data loading process."""
    parser = argparse.ArgumentParser(description='Upload data to Google Sheets')
    parser.add_argument('--worksheet', '-w', 
                       default='Fentanyl Deaths Over Time',
                       help='Name of the worksheet/tab (default: "Fentanyl Deaths Over Time")')
    parser.add_argument('--csv-file', '-f',
                       default='../../final_datasets/fact_fentanyl_deaths_over_time.csv',
                       help='Path to CSV file to upload')
    parser.add_argument('--multi-export', '-m',
                       action='store_true',
                       help='Export multiple datasets to different worksheets')
    parser.add_argument('--list-exports',
                       action='store_true',
                       help='List available export configurations')
    
    args = parser.parse_args()
    
    # Load configuration from environment variables
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'service_account.json')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    if not sheet_id:
        logger.error("GOOGLE_SHEET_ID environment variable is required")
        return 1
    
    if not os.path.exists(credentials_file):
        logger.error(f"Google Sheets credentials file not found: {credentials_file}")
        return 1
    
    # Create loader
    loader = GoogleSheetsLoader(credentials_file, sheet_id)
    
    try:
        # Authenticate with Google Sheets
        if not loader.authenticate_google_sheets():
            return 1
        
        if args.list_exports:
            print_available_exports()
            return 0
        
        if args.multi_export:
            success = export_multiple_datasets(loader)
        else:
            # Single export
            logger.info(f"Starting data upload to Google Sheets worksheet: {args.worksheet}")
            success = loader.load_data(args.csv_file, args.worksheet)
        
        if success:
            logger.info("Data upload completed successfully!")
            return 0
        else:
            logger.error("Data upload failed")
            return 1
            
    finally:
        loader.close_connections()

if __name__ == "__main__":
    exit(main())
