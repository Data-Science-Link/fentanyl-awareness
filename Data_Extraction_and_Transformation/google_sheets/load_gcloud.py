#!/usr/bin/env python3
"""
Google Sheets Data Loader

This script connects to the DuckDB database, exports the final mart table
to CSV format, and uploads it to Google Sheets for Tableau Public consumption.
"""

import os
import pandas as pd
import duckdb
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import logging
from typing import Optional
import csv
import io

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheetsLoader:
    """Load data from DuckDB to Google Sheets."""
    
    def __init__(self, credentials_file: str, sheet_id: str):
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.conn = None
        self.gc = None
        
    def connect_to_duckdb(self, db_path: str = "fentanyl_awareness.duckdb") -> bool:
        """Connect to DuckDB database."""
        try:
            self.conn = duckdb.connect(db_path)
            logger.info(f"Connected to DuckDB database: {db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB: {e}")
            return False
    
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
            
            # Upload data in batches to avoid API limits
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                start_row = i + 1
                end_row = start_row + len(batch) - 1
                
                # Update the worksheet
                worksheet.update(f'A{start_row}:Z{end_row}', batch)
                logger.info(f"Uploaded batch {i//batch_size + 1}: rows {start_row}-{end_row}")
            
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
        """Close database connections."""
        if self.conn:
            self.conn.close()
            logger.info("Closed DuckDB connection")

def main():
    """Main function to run the data loading process."""
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
        # Connect to DuckDB
        if not loader.connect_to_duckdb():
            return 1
        
        # Authenticate with Google Sheets
        if not loader.authenticate_google_sheets():
            return 1
        
        # Load data
        logger.info("Starting data upload to Google Sheets...")
        success = loader.load_data()
        
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
