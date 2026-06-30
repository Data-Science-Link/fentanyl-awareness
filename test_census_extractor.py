import pandas as pd
from data_engineering.data_sources.census_acs.census_extractor import CensusExtractor

def test_clean_economic_data():
    extractor = CensusExtractor()
    data = {
        'B19013_001E': ['1000', '2000', 'invalid'],
        'B19301_001E': ['3000', '4000', '5000'],
        'B23025_002E': ['100', '200', '300'],
        'B23025_003E': ['90', '180', '270'],
        'B23025_004E': ['80', '160', '240'],
        'B23025_005E': ['10', '20', '30'],
        'state': ['01', '02', '03'],
        'NAME': ['State 1', 'State 2', 'State 3'],
        'year': [2021, 2021, 2021],
        'extracted_at': ['2023-01-01', '2023-01-01', '2023-01-01']
    }
    df = pd.DataFrame(data)

    # Run the cleaning function
    cleaned_df = extractor._clean_economic_data(df)

    # Assertions
    assert len(cleaned_df) == 2  # The row with 'invalid' should be dropped due to dropna()
    assert list(cleaned_df['state_code']) == [1, 2]
    assert list(cleaned_df['median_household_income']) == [1000.0, 2000.0]

    print("Test passed successfully!")

if __name__ == "__main__":
    test_clean_economic_data()
