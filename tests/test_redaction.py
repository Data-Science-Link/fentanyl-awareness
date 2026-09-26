import os

import requests

from data_engineering.data_sources.census_acs.census_extractor import CensusExtractor


def test_sanitize_error_redacts_api_key():
    os.environ["CENSUS_API_KEY"] = "SUPER_SECRET_KEY"
    extractor = CensusExtractor()
    assert extractor.api_key == "SUPER_SECRET_KEY"

    error = requests.exceptions.HTTPError(
        "Failed to fetch from https://api.census.gov/data/2021/acs/acs5?get=NAME&for=state:*&key=SUPER_SECRET_KEY"
    )
    sanitized = extractor._sanitize_error(error)
    assert "SUPER_SECRET_KEY" not in sanitized
    assert "***REDACTED***" in sanitized
