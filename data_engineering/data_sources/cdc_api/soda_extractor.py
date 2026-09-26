#!/usr/bin/env python3
"""
CDC SODA API Data Extraction Script

Pulls provisional drug overdose death counts from the CDC Socrata Open Data API.
The extract is limited to "Synthetic opioids, excl. methadone (T40.4)" — the ICD-10
class that includes fentanyl and other synthetic opioids other than methadone.

The data is saved as a CSV seed for dbt. Empty data_value cells are preserved so
downstream models can treat CDC suppression as missing, not zero.
"""

from datetime import datetime, timezone
from pathlib import Path
import logging
import sys

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CDC_DATASET_ID = "xkb8-kh2a"
CDC_INDICATOR = "Synthetic opioids, excl. methadone (T40.4)"
PAGE_SIZE = 10000
MIN_EXPECTED_ROWS = 1000
CORE_STATE_NAMES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
}
# Jurisdictions CDC often omits from T40.4 VSRR when quality thresholds are not met.
KNOWN_SOURCE_GAPS = {"Louisiana"}


class CDCSodaExtractor:
    """Extract T40.4 provisional counts from the CDC SODA API."""

    def __init__(self, dataset_id: str = CDC_DATASET_ID):
        self.dataset_id = dataset_id
        self.base_url = f"https://data.cdc.gov/resource/{dataset_id}.json"
        self.indicator = CDC_INDICATOR

    def fetch_data(self) -> pd.DataFrame:
        """Fetch every page of T40.4 records from the CDC API."""
        logger.info("Fetching data from %s for indicator: %s", self.base_url, self.indicator)

        frames = []
        offset = 0

        while True:
            params = {
                "indicator": self.indicator,
                "$limit": PAGE_SIZE,
                "$offset": offset,
                "$order": "year,month,state",
            }
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            page = response.json()
            if not page:
                break
            frames.append(pd.DataFrame(page))
            logger.info("Fetched %s rows (offset %s)", len(page), offset)
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

        if not frames:
            raise ValueError("CDC SODA API returned no T40.4 records")

        df = pd.concat(frames, ignore_index=True)
        df["extracted_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        df["dataset_id"] = self.dataset_id
        logger.info("Successfully fetched %s records.", len(df))
        return df

    def validate(self, df: pd.DataFrame) -> None:
        """Fail fast on empty or truncated extracts; warn on known geography gaps."""
        if len(df) < MIN_EXPECTED_ROWS:
            raise ValueError(
                f"CDC extract has only {len(df)} rows; expected at least {MIN_EXPECTED_ROWS}"
            )

        indicators = set(df.get("indicator", pd.Series(dtype=str)).dropna().unique())
        if indicators and indicators != {self.indicator}:
            raise ValueError(f"Unexpected indicator values in extract: {indicators}")

        names = set(df.get("state_name", pd.Series(dtype=str)).dropna().unique())
        missing = sorted((CORE_STATE_NAMES - names) - KNOWN_SOURCE_GAPS)
        known_missing = sorted(KNOWN_SOURCE_GAPS - names)
        unexpected_extra = sorted(names - CORE_STATE_NAMES - {"United States", "New York City", "Puerto Rico"})

        if missing:
            raise ValueError(
                "CDC extract is missing unexpected jurisdictions: " + ", ".join(missing)
            )
        if known_missing:
            logger.warning(
                "CDC extract is missing documented source gap(s): %s",
                ", ".join(known_missing),
            )
        if unexpected_extra:
            logger.info("CDC extract includes additional geographies: %s", ", ".join(unexpected_extra))

    def save_to_csv(self, df: pd.DataFrame, output_path: Path) -> None:
        """Save the DataFrame to a CSV file."""
        logger.info("Saving data to %s", output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Data saved successfully.")


def main() -> int:
    script_path = Path(__file__).resolve()
    output_dir = script_path.parent.parent.parent / "data_build_tool" / "dbt" / "seeds"
    output_path = output_dir / "cdc_api_provisional_overdose_counts.csv"

    extractor = CDCSodaExtractor()
    try:
        df = extractor.fetch_data()
        extractor.validate(df)
        extractor.save_to_csv(df, output_path)
        return 0
    except Exception as exc:
        logger.error("Error fetching data from CDC API: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
