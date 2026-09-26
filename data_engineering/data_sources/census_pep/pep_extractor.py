#!/usr/bin/env python3
"""
Census Population Estimates Program (PEP) state populations.

Rates use these July 1 resident populations. The PEP JSON API has no vintage
after 2021, so this reads the public vintage CSV files. ACS 5-year estimates
stay in the census extractor and are used for income and unemployment, and
for New York City, which PEP does not publish.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

VINTAGE_URL = (
    "https://www2.census.gov/programs-surveys/popest/datasets/"
    "2020-{vintage}/state/totals/NST-EST{vintage}-ALLDATA.csv"
)
ESTIMATES_2010_URL = (
    "https://www2.census.gov/programs-surveys/popest/datasets/"
    "2010-2020/state/totals/nst-est2020-alldata.csv"
)
INTERCENSAL_2000_URL = (
    "https://www2.census.gov/programs-surveys/popest/datasets/"
    "2000-2010/intercensal/state/st-est00int-alldata.csv"
)


def unpivot_population(frame: pd.DataFrame, years: list[int], vintage: str) -> pd.DataFrame:
    """Melt POPESTIMATE{year} columns into one row per geography and year."""
    rows = []
    for year in years:
        column = f"POPESTIMATE{year}"
        if column not in frame.columns:
            continue
        for _, record in frame.iterrows():
            population = pd.to_numeric(record[column], errors="coerce")
            if pd.isna(population):
                continue
            rows.append(
                {
                    "year": year,
                    "state_name": str(record["NAME"]).strip(),
                    "population": int(population),
                    "vintage": vintage,
                    "population_source": "Census PEP",
                }
            )
    return pd.DataFrame(rows)


def select_vintage_geographies(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep the nation (SUMLEV 010) and states, DC, and Puerto Rico (040)."""
    if "SUMLEV" not in frame.columns:
        return frame
    levels = frame["SUMLEV"].astype(str).str.zfill(3)
    return frame[levels.isin(["010", "040"])].copy()


def select_intercensal_totals(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep the all-age, all-sex, all-race total in the 2000-2010 intercensal file."""
    mask = (
        (frame["SEX"] == 0)
        & (frame["ORIGIN"] == 0)
        & (frame["RACE"] == 0)
        & (frame["AGEGRP"] == 0)
    )
    return frame.loc[mask].copy()


def prefer_newer_vintage(frame: pd.DataFrame) -> pd.DataFrame:
    """If two vintages share a year and state, keep the later vintage label."""
    ordered = frame.sort_values(["vintage"])
    return (
        ordered.drop_duplicates(["year", "state_name"], keep="last")
        .sort_values(["year", "state_name"])
        .reset_index(drop=True)
    )


def _read_csv(session: requests.Session, url: str) -> pd.DataFrame:
    logger.info("Downloading %s", url)
    response = session.get(url, timeout=120)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))


def latest_vintage_url(session: requests.Session, start_year: int) -> tuple[int, str]:
    for vintage in range(start_year, 2020, -1):
        url = VINTAGE_URL.format(vintage=vintage)
        response = session.head(url, timeout=30, allow_redirects=True)
        if response.status_code == 200:
            return vintage, url
    raise RuntimeError("No Census PEP vintage file was found for 2021 or later")


def default_output_path() -> Path:
    script_path = Path(__file__).resolve()
    return (
        script_path.parent.parent.parent
        / "data_build_tool"
        / "dbt"
        / "seeds"
        / "census_pep_state_population.csv"
    )


def build_population_frame(session: requests.Session, now_year: int | None = None) -> pd.DataFrame:
    now_year = now_year or datetime.now(timezone.utc).year
    vintage, vintage_url = latest_vintage_url(session, now_year)
    current = select_vintage_geographies(_read_csv(session, vintage_url))
    estimates_2010 = select_vintage_geographies(_read_csv(session, ESTIMATES_2010_URL))
    intercensal = select_intercensal_totals(_read_csv(session, INTERCENSAL_2000_URL))

    pieces = [
        unpivot_population(intercensal, list(range(2000, 2010)), "intercensal-2000-2010"),
        unpivot_population(estimates_2010, list(range(2010, 2020)), "2020"),
        unpivot_population(current, list(range(2020, vintage + 1)), str(vintage)),
    ]
    frame = prefer_newer_vintage(pd.concat(pieces, ignore_index=True))
    frame["extracted_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if frame.empty:
        raise RuntimeError("Census PEP files produced no population rows")
    logger.info(
        "PEP population rows: %s (%s-%s, vintage %s)",
        len(frame),
        frame["year"].min(),
        frame["year"].max(),
        vintage,
    )
    return frame


def main() -> int:
    session = requests.Session()
    session.headers["User-Agent"] = "Fentanyl-Awareness-Pipeline/1.0"
    try:
        frame = build_population_frame(session)
        output_path = default_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output_path, index=False)
        logger.info("Wrote %s", output_path)
        return 0
    except Exception as exc:
        logger.error("Census PEP extract failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
