#!/usr/bin/env python3
"""
CDC SODA API Data Extraction Script

This script pulls provisional drug overdose death counts from the CDC's Socrata Open Data API (SODA).
Specifically, it extracts data for "Synthetic opioids, excl. methadone (T40.4)".
The data is saved as a CSV file in the dbt seeds directory.
"""

import os
import requests
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CDCSodaExtractor:
    """Extract data from CDC SODA API."""

    def __init__(self, dataset_id: str = "xkb8-kh2a"):
        self.base_url = f"https://data.cdc.gov/resource/{dataset_id}.json"
        self.indicator = "Synthetic opioids, excl. methadone (T40.4)"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch data from the CDC API."""
        logger.info(f"Fetching data from {self.base_url} for indicator: {self.indicator}")

        # SODA API parameters
        # We want all states and all time periods for this indicator
        params = {
            "indicator": self.indicator,
            "$limit": 50000  # Ensure we get all records
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} records.")
            return df

        except Exception as e:
            logger.error(f"Error fetching data from CDC API: {e}")
            raise

    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save the DataFrame to a CSV file."""
        logger.info(f"Saving data to {output_path}")
        output_dir = os.path.dirname(output_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)
        logger.info("Data saved successfully.")

def main():
    # Set up paths
    script_dir = Path(__file__).parent
    output_path = script_dir.parent.parent / "data_build_tool" / "dbt" / "seeds" / "cdc_api_provisional_overdose_counts.csv"

    extractor = CDCSodaExtractor()
    try:
        df = extractor.fetch_data()
        extractor.save_to_csv(df, str(output_path))
        return 0
    except Exception:
        return 1

if __name__ == "__main__":
    exit(main())
