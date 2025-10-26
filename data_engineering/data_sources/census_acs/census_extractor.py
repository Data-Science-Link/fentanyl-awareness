#!/usr/bin/env python3
"""
Census ACS Data Extractor

This script extracts US Census American Community Survey (ACS) and Population Estimates Program (PEP) data
for integration with the fentanyl awareness data pipeline.

Key Features:
- State-level population estimates
- Age-adjusted population data
- Economic indicators
- Automated data validation and cleaning
"""

import os
import requests
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Census API Configuration
CENSUS_API_BASE_URL = "https://api.census.gov/data"

# API Rate Limits
RATE_LIMITS = {
    "requests_per_day": 500,
    "requests_per_minute": 10,
    "delay_between_requests": 0.2  # seconds
}

class CensusExtractor:
    """Extract data from US Census API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Census extractor with API key"""
        self.api_key = api_key or os.getenv('CENSUS_API_KEY')
        if not self.api_key:
            raise ValueError("Census API key required. Set CENSUS_API_KEY environment variable or pass api_key parameter")

        self.base_url = CENSUS_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Fentanyl-Awareness-Pipeline/1.0'
        })

    def get_state_population_estimates(self, years: List[int] = None) -> pd.DataFrame:
        """
        Extract state-level population estimates from ACS

        Args:
            years: List of years to extract (default: 2005-2023)

        Returns:
            DataFrame with state population data
        """
        if years is None:
            years = list(range(2005, 2024))  # 2005-2023 (ACS 5-year estimates)

        logger.info(f"Extracting state population estimates for years: {years}")

        all_data = []

        for year in years:
            try:
                # ACS 5-Year Estimates endpoint (more reliable than PEP)
                url = f"{self.base_url}/{year}/acs/acs5"

                params = {
                    'get': 'NAME,B01001_001E',  # B01001_001E is total population
                    'for': 'state:*',
                    'key': self.api_key
                }

                logger.info(f"Fetching data for year {year}...")
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Convert to DataFrame
                df = pd.DataFrame(data[1:], columns=data[0])
                df['year'] = year
                df['extracted_at'] = datetime.now()

                all_data.append(df)

                # Rate limiting
                time.sleep(RATE_LIMITS["delay_between_requests"])

            except Exception as e:
                logger.error(f"Error fetching data for year {year}: {e}")
                continue

        if not all_data:
            raise Exception("No data extracted successfully")

        # Combine all years
        combined_df = pd.concat(all_data, ignore_index=True)

        # Clean and standardize data
        combined_df = self._clean_population_data(combined_df)

        logger.info(f"Successfully extracted {len(combined_df)} records")
        return combined_df

    def get_state_economic_data(self, years: List[int] = None) -> pd.DataFrame:
        """
        Extract state-level economic data from ACS

        Args:
            years: List of years to extract (default: 2009-2023)

        Returns:
            DataFrame with state economic data
        """
        if years is None:
            years = list(range(2009, 2024))  # 2009-2023 (ACS 5-year estimates)

        logger.info(f"Extracting state economic data for years: {years}")

        all_data = []

        for year in years:
            try:
                # ACS 5-Year Estimates endpoint
                url = f"{self.base_url}/{year}/acs/acs5"

                params = {
                    'get': 'B19013_001E,B19301_001E,B23025_002E,B23025_003E,B23025_004E,B23025_005E,NAME',
                    'for': 'state:*',
                    'key': self.api_key
                }

                logger.info(f"Fetching economic data for year {year}...")
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Convert to DataFrame
                df = pd.DataFrame(data[1:], columns=data[0])
                df['year'] = year
                df['extracted_at'] = datetime.now()

                all_data.append(df)

                # Rate limiting
                time.sleep(RATE_LIMITS["delay_between_requests"])

            except Exception as e:
                logger.error(f"Error fetching economic data for year {year}: {e}")
                continue

        if not all_data:
            raise Exception("No economic data extracted successfully")

        # Combine all years
        combined_df = pd.concat(all_data, ignore_index=True)

        # Clean and standardize data
        combined_df = self._clean_economic_data(combined_df)

        logger.info(f"Successfully extracted {len(combined_df)} economic records")
        return combined_df

    def _clean_population_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize population data from ACS"""

        # Convert numeric columns
        df['B01001_001E'] = pd.to_numeric(df['B01001_001E'], errors='coerce')
        df['state'] = pd.to_numeric(df['state'], errors='coerce')

        # Rename columns for consistency
        df = df.rename(columns={
            'B01001_001E': 'population',
            'state': 'state_code',
            'NAME': 'state_name'
        })

        # Clean state names (remove extra text)
        df['state_name'] = df['state_name'].str.replace(',', '').str.strip()

        # Add data description
        df['date_description'] = 'ACS 5-Year Estimate'

        # Select final columns
        final_columns = [
            'year', 'state_code', 'state_name', 'population',
            'date_description', 'extracted_at'
        ]

        return df[final_columns].dropna()

    def _clean_economic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize economic data"""

        # Convert numeric columns
        numeric_columns = ['B19013_001E', 'B19301_001E', 'B23025_002E',
                          'B23025_003E', 'B23025_004E', 'B23025_005E']

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert state code to numeric
        df['state'] = pd.to_numeric(df['state'], errors='coerce')

        # Rename columns to meaningful names
        df = df.rename(columns={
            'B19013_001E': 'median_household_income',
            'B19301_001E': 'per_capita_income',
            'B23025_002E': 'labor_force_total',
            'B23025_003E': 'labor_force_civilian',
            'B23025_004E': 'employed',
            'B23025_005E': 'unemployed',
            'NAME': 'state_name'
        })

        # Calculate unemployment rate (handle division by zero and NaN)
        df['unemployment_rate'] = (df['unemployed'] / df['labor_force_civilian'] * 100).round(2)
        df['unemployment_rate'] = df['unemployment_rate'].fillna(0)

        # Use the state field directly (already converted to numeric above)
        df['state_code'] = df['state'].astype(int)

        # Select final columns
        final_columns = [
            'year', 'state_code', 'state_name', 'median_household_income',
            'per_capita_income', 'unemployment_rate', 'labor_force_total',
            'employed', 'unemployed', 'extracted_at'
        ]

        return df[final_columns].dropna()

def test_census_api():
    """Test Census API connection and data extraction"""
    try:
        extractor = CensusExtractor()
        print("🧪 Testing Census data extraction...")

        # Test with a small dataset
        df = extractor.get_state_population_estimates(years=[2021])
        print(f"✅ Successfully extracted {len(df)} records")
        print("🎉 Census API test successful!")
        return True

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def main():
    """Main function to extract Census data"""

    try:
        # Initialize extractor
        extractor = CensusExtractor()

        # Extract population data
        logger.info("Starting Census data extraction...")
        population_df = extractor.get_state_population_estimates()

        # Extract economic data
        economic_df = extractor.get_state_economic_data()

        # Save to CSV files (overwrite if they exist)
        output_dir = "../../dbt/seeds"
        os.makedirs(output_dir, exist_ok=True)

        population_file = f"{output_dir}/census_state_population.csv"
        economic_file = f"{output_dir}/census_state_economic.csv"

        # Remove existing files if they exist to ensure clean overwrite
        for file_path in [population_file, economic_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed existing file: {file_path}")

        population_df.to_csv(population_file, index=False)
        economic_df.to_csv(economic_file, index=False)

        logger.info(f"Population data saved to: {population_file}")
        logger.info(f"Economic data saved to: {economic_file}")

        # Print summary
        print(f"\n📊 Census Data Extraction Summary:")
        print(f"Population records: {len(population_df)}")
        print(f"Economic records: {len(economic_df)}")
        print(f"Years covered: {population_df['year'].min()}-{population_df['year'].max()}")
        print(f"States covered: {population_df['state_name'].nunique()}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
