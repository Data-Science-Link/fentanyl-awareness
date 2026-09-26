import pandas as pd

from data_engineering.data_sources.census_pep.pep_extractor import (
    prefer_newer_vintage,
    select_intercensal_totals,
    select_vintage_geographies,
    unpivot_population,
)


def test_unpivot_keeps_requested_years_only():
    frame = pd.DataFrame(
        {
            "NAME": ["Alabama", "United States"],
            "POPESTIMATE2024": [500, 1000],
            "POPESTIMATE2025": [510, 1010],
        }
    )
    melted = unpivot_population(frame, [2025], "2025")
    assert list(melted["year"]) == [2025, 2025]
    assert list(melted["population"]) == [510, 1010]
    assert set(melted["population_source"]) == {"Census PEP"}


def test_vintage_filter_keeps_nation_and_states():
    frame = pd.DataFrame(
        {
            "SUMLEV": ["010", "020", "040"],
            "NAME": ["United States", "Northeast", "Alabama"],
        }
    )
    kept = select_vintage_geographies(frame)
    assert list(kept["NAME"]) == ["United States", "Alabama"]


def test_intercensal_filter_keeps_the_total_row():
    frame = pd.DataFrame(
        {
            "NAME": ["Alabama", "Alabama"],
            "SEX": [0, 1],
            "ORIGIN": [0, 0],
            "RACE": [0, 0],
            "AGEGRP": [0, 0],
        }
    )
    kept = select_intercensal_totals(frame)
    assert len(kept) == 1


def test_newer_vintage_replaces_the_same_year():
    frame = pd.DataFrame(
        {
            "year": [2020, 2020],
            "state_name": ["Alabama", "Alabama"],
            "population": [1, 2],
            "vintage": ["2020", "2025"],
            "population_source": ["Census PEP", "Census PEP"],
        }
    )
    kept = prefer_newer_vintage(frame)
    assert len(kept) == 1
    assert int(kept.iloc[0]["population"]) == 2
