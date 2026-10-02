#!/usr/bin/env python3
"""Aggregate CBP's public fentanyl seizure file.

The source is the newest Nationwide Drug Seizures CSV linked from
https://www.cbp.gov/document/stats/nationwide-drug-seizures.
Rows are already totals. This step keeps drug type Fentanyl and sums
pounds and event counts by fiscal year, CBP component, and region.
Field offices and other location detail are not published.
"""

from __future__ import annotations

import logging
import re
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PAGE_URL = "https://www.cbp.gov/document/stats/nationwide-drug-seizures"
CBP_HOME = "https://www.cbp.gov"
PUBLISHED_COLUMNS = [
    "fiscal_year",
    "component",
    "region",
    "pounds",
    "seizure_events",
    "source_url",
    "source_file",
    "extracted_at",
]


def newest_dataset_url(html: str) -> str:
    """First nationwide-drugs CSV on the page. CBP lists the newest file first."""
    for href in re.findall(r'href="([^"]+)"', html):
        if "nationwide-drugs" in href and href.lower().endswith(".csv"):
            if href.startswith("http"):
                return href
            return CBP_HOME + href
    raise RuntimeError("CBP page did not link a nationwide drug-seizure CSV")


def aggregate_fentanyl(frame: pd.DataFrame, source_url: str, source_file: str, extracted_at: str) -> pd.DataFrame:
    """Sum fentanyl pounds and events. Drop field-office detail."""
    required = {"FY", "Component", "Region", "Drug Type", "Count of Event", "Sum Qty (lbs)"}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"CBP file is missing columns: {sorted(missing)}")
    drugs = frame["Drug Type"].astype(str).str.strip().str.lower()
    kept = frame.loc[drugs == "fentanyl"].copy()
    if kept.empty:
        raise RuntimeError("CBP file had no Fentanyl rows")
    grouped = (
        kept.groupby(["FY", "Component", "Region"], dropna=False)[["Count of Event", "Sum Qty (lbs)"]]
        .sum()
        .reset_index()
    )
    grouped["pounds"] = grouped["Sum Qty (lbs)"].round(2)
    return pd.DataFrame(
        {
            "fiscal_year": grouped["FY"].astype(str),
            "component": grouped["Component"].astype(str),
            "region": grouped["Region"].astype(str),
            "pounds": grouped["pounds"],
            "seizure_events": grouped["Count of Event"].astype(int),
            "source_url": source_url,
            "source_file": source_file,
            "extracted_at": extracted_at,
        }
    )[PUBLISHED_COLUMNS]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def output_paths() -> list[Path]:
    root = repo_root()
    return [
        root / "docs" / "sources" / "cbp_fentanyl_seizures.csv",
        root / "Final_Datasets" / "cbp_fentanyl_seizures.csv",
    ]


def write_outputs(frame: pd.DataFrame) -> None:
    for path in output_paths():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        logger.info("Wrote %s (%s rows)", path, len(frame))


def fetch_and_aggregate(session) -> pd.DataFrame:
    page = session.get(PAGE_URL, timeout=60)
    if page.status_code >= 400:
        raise RuntimeError(f"CBP page returned HTTP {page.status_code}")
    csv_url = newest_dataset_url(page.text)
    logger.info("CBP file %s", csv_url)
    data = session.get(csv_url, timeout=120)
    if data.status_code >= 400:
        raise RuntimeError(f"CBP CSV returned HTTP {data.status_code}")
    frame = pd.read_csv(StringIO(data.text))
    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return aggregate_fentanyl(frame, PAGE_URL, csv_url, extracted_at)


def main(argv: list[str] | None = None) -> int:
    del argv
    existing = all(path.exists() and path.stat().st_size > 0 for path in output_paths())
    try:
        from curl_cffi import requests as curl_requests

        frame = fetch_and_aggregate(curl_requests.Session(impersonate="chrome"))
        write_outputs(frame)
        return 0
    except Exception as exc:
        if existing:
            logger.warning("CBP extract failed (%s). Keeping the existing file.", exc)
            return 0
        logger.error("CBP extract failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
