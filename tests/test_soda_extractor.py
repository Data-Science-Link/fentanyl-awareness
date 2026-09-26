from pathlib import Path

import pandas as pd
import pytest

from data_engineering.data_sources.cdc_api.soda_extractor import (
    CDCSodaExtractor,
    CORE_STATE_NAMES,
)


def test_save_to_csv(tmp_path: Path):
    extractor = CDCSodaExtractor()
    df = pd.DataFrame(
        {
            "state_name": ["Ohio"],
            "year": ["2023"],
            "indicator": [extractor.indicator],
            "data_value": [100],
        }
    )
    output = tmp_path / "cdc.csv"
    extractor.save_to_csv(df, output)

    loaded = pd.read_csv(output)
    assert len(loaded) == 1
    assert loaded.iloc[0]["state_name"] == "Ohio"


def test_validate_rejects_truncated_extract():
    extractor = CDCSodaExtractor()
    df = pd.DataFrame(
        {
            "state_name": ["Ohio"],
            "indicator": [extractor.indicator],
        }
    )
    with pytest.raises(ValueError, match="only 1 rows"):
        extractor.validate(df)


def test_validate_rejects_missing_unexpected_state():
    extractor = CDCSodaExtractor()
    names = (
        extractor_core_states_without_ohio()
    )
    df = pd.DataFrame(
        {
            "state_name": list(names) * 25,
            "indicator": [extractor.indicator] * (len(names) * 25),
        }
    )
    with pytest.raises(ValueError, match="Ohio"):
        extractor.validate(df)


def test_validate_fails_when_a_previously_present_state_disappears():
    extractor = CDCSodaExtractor()
    names = sorted(CORE_STATE_NAMES - {"Louisiana"})
    df = pd.DataFrame(
        {
            "state_name": names * 25,
            "indicator": [extractor.indicator] * (len(names) * 25),
        }
    )
    with pytest.raises(ValueError, match="Louisiana"):
        extractor.validate(df, previous_states={"Louisiana", "Ohio"})


def test_validate_allows_documented_louisiana_gap():
    extractor = CDCSodaExtractor()
    names = sorted(
        (
            {
                "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
                "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
                "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
                "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
                "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
                "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
                "United States",
            }
        )
    )
    df = pd.DataFrame(
        {
            "state_name": names * 25,
            "indicator": [extractor.indicator] * (len(names) * 25),
        }
    )
    extractor.validate(df)


def extractor_core_states_without_ohio():
    from data_engineering.data_sources.cdc_api.soda_extractor import CORE_STATE_NAMES

    return CORE_STATE_NAMES - {"Ohio", "Louisiana"}
