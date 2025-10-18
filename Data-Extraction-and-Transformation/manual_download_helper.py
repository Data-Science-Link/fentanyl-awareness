#!/usr/bin/env python3
"""
Manual CDC WONDER Data Download Helper

This script provides instructions and tools for manually downloading
CDC WONDER data when the API is unavailable.
"""

import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_manual_download_instructions():
    """Print instructions for manually downloading CDC WONDER data."""
    
    print("""
🔧 MANUAL CDC WONDER DATA DOWNLOAD INSTRUCTIONS
==============================================

Since the CDC WONDER API is currently experiencing issues (502 Bad Gateway),
here's how to manually download the data:

1. 🌐 VISIT CDC WONDER WEBSITE
   Go to: https://wonder.cdc.gov/

2. 📊 SELECT DATABASE
   Choose "Multiple Cause of Death" for datasets D77 and D157
   Choose "Provisional Mortality Statistics" for dataset D176

3. 🔍 CONFIGURE QUERY
   For each dataset, use these settings:
   
   D77 (1999-2020):
   - Years: 1999-2020
   - Cause of Death: Drug-induced causes (D)
   - Multiple Cause: T40.4 (Other synthetic narcotics)
   - Geography: All States, All Counties
   - Export Format: Tab-delimited text
   
   D157 (2018-2023):
   - Years: 2018-2023
   - Cause of Death: Drug-induced causes (D)
   - Multiple Cause: T40.4 (Other synthetic narcotics)
   - Geography: All States, All Counties
   - Export Format: Tab-delimited text
   
   D176 (2023-current):
   - Years: 2023-current
   - Cause of Death: Drug-induced causes (D)
   - Multiple Cause: T40.4 (Other synthetic narcotics)
   - Geography: All States, All Counties
   - Export Format: Tab-delimited text

4. 💾 DOWNLOAD DATA
   - Click "Send" to submit the query
   - Download the resulting TSV file
   - Save with these exact names:
     * d77_official_1999_2020.tsv
     * d157_official_2018_2023.tsv
     * d176_provisional_2023_current.tsv

5. 📁 PLACE FILES
   Put the downloaded files in: ./dbt/seeds/

6. ▶️ RUN PIPELINE
   After placing the files, run:
   cd dbt && dbt seed && dbt run

📞 ALTERNATIVE: Contact CDC WONDER Support
If the website is also down, contact:
- Email: wonder@cdc.gov
- Phone: (800) 232-4636
- Hours: Monday-Friday, 8:00 AM - 8:00 PM EST

🔄 RETRY API LATER
The API issues might be temporary. Try running the extraction script again later:
python3 extract_data.py
""")

def create_seeds_directory():
    """Create the seeds directory if it doesn't exist."""
    seeds_dir = Path("dbt/seeds")
    seeds_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created/verified seeds directory: {seeds_dir}")
    return seeds_dir

def check_for_existing_data():
    """Check if data files already exist in the seeds directory."""
    seeds_dir = Path("dbt/seeds")
    
    if not seeds_dir.exists():
        logger.info("Seeds directory doesn't exist yet")
        return False
    
    expected_files = [
        "d77_official_1999_2020.tsv",
        "d157_official_2018_2023.tsv", 
        "d176_provisional_2023_current.tsv"
    ]
    
    existing_files = []
    for file in expected_files:
        file_path = seeds_dir / file
        if file_path.exists():
            existing_files.append(file)
            logger.info(f"✅ Found existing data file: {file}")
        else:
            logger.info(f"❌ Missing data file: {file}")
    
    return len(existing_files) == len(expected_files)

def main():
    """Main function."""
    logger.info("🔍 Checking CDC WONDER data availability...")
    
    # Create seeds directory
    create_seeds_directory()
    
    # Check for existing data
    has_data = check_for_existing_data()
    
    if has_data:
        logger.info("✅ All data files found! You can proceed with dbt transformations.")
        logger.info("Run: cd dbt && dbt seed && dbt run")
    else:
        logger.info("❌ Data files missing. Follow the manual download instructions below.")
        print_manual_download_instructions()

if __name__ == "__main__":
    main()

