from data_engineering.data_sources.census_acs.census_extractor import CensusExtractor
import os
import requests

os.environ['CENSUS_API_KEY'] = 'SUPER_SECRET_KEY'
extractor = CensusExtractor()
assert extractor.api_key == 'SUPER_SECRET_KEY'
try:
    raise requests.exceptions.HTTPError("Failed to fetch from https://api.census.gov/data/2021/acs/acs5?get=NAME&for=state:*&key=SUPER_SECRET_KEY")
except Exception as e:
    sanitized = extractor._sanitize_error(e)
    assert 'SUPER_SECRET_KEY' not in sanitized
    assert '***REDACTED***' in sanitized
    print("Sanitized error:", sanitized)
    print("Test passed.")
