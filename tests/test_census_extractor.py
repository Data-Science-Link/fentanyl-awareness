import pandas as pd

from data_engineering.data_sources.census_acs.census_extractor import CensusExtractor


def test_clean_economic_data_keeps_null_income():
    extractor = CensusExtractor()
    data = {
        "B19013_001E": ["1000", "2000", "invalid"],
        "B19301_001E": ["3000", "4000", "5000"],
        "B23025_002E": ["100", "200", "300"],
        "B23025_003E": ["90", "180", "270"],
        "B23025_004E": ["80", "160", "240"],
        "B23025_005E": ["10", "20", "30"],
        "state": ["01", "02", "03"],
        "NAME": ["State 1", "State 2", "State 3"],
        "year": [2021, 2021, 2021],
        "extracted_at": ["2023-01-01", "2023-01-01", "2023-01-01"],
    }
    cleaned_df = extractor._clean_economic_data(pd.DataFrame(data))

    assert len(cleaned_df) == 3
    assert list(cleaned_df["state_code"]) == [1, 2, 3]
    assert list(cleaned_df["median_household_income"].head(2)) == [1000.0, 2000.0]
    assert pd.isna(cleaned_df.loc[cleaned_df["state_code"] == 3, "median_household_income"]).all()


def test_unemployment_rate_stays_null_when_labor_force_missing():
    extractor = CensusExtractor()
    data = {
        "B19013_001E": ["1000"],
        "B19301_001E": ["3000"],
        "B23025_002E": ["100"],
        "B23025_003E": [None],
        "B23025_004E": ["80"],
        "B23025_005E": ["10"],
        "state": ["01"],
        "NAME": ["State 1"],
        "year": [2021],
        "extracted_at": ["2023-01-01"],
    }
    cleaned_df = extractor._clean_economic_data(pd.DataFrame(data))

    assert len(cleaned_df) == 1
    assert pd.isna(cleaned_df.iloc[0]["unemployment_rate"])
