#!/usr/bin/env python3
"""Record how current the layered death series is.

Finished death certificates stop at the latest final year. CDC's provisional
12-month file continues after that. This check asks the CDC API whether a
newer provisional month exists than the seed just extracted. The Monday
publish runs the extractor first, then this script. If CDC has posted a month
the seed does not have, the job fails instead of publishing a stale file.
"""

from __future__ import annotations

import csv
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATASET_ID = "xkb8-kh2a"
INDICATOR = "Synthetic opioids, excl. methadone (T40.4)"
MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}
COLUMNS = [
    "checked_at",
    "cdc_dataset_id",
    "cdc_dataset_updated_at",
    "latest_provisional_month",
    "latest_final_year",
    "provisional_extract_at",
    "update_schedule",
    "note",
]
NOTE = (
    "Finished death certificates are layered with CDC's preliminary 12-month totals. "
    "The preliminary series is as new as CDC has published it. Drug-overdose certificates "
    "usually lag the calendar by about four months. This check runs with the Monday publish. "
    "A new month is added when CDC has posted one."
)
SCHEDULE = "Every Monday, and when the pipeline changes on main"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def provisional_seed_path() -> Path:
    return repo_root() / "data_engineering" / "data_build_tool" / "dbt" / "seeds" / "cdc_api_provisional_overdose_counts.csv"


def final_seed_path() -> Path:
    return repo_root() / "data_engineering" / "data_build_tool" / "dbt" / "seeds" / "nvss_final_t40_4_deaths.csv"


def output_path() -> Path:
    return repo_root() / "Final_Datasets" / "data_freshness.csv"


def month_stamp(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def latest_provisional_month(rows: list[dict]) -> str:
    """Latest US T40.4 month in a SODA extract. Month names are CDC's labels."""
    best: tuple[int, int] | None = None
    for row in rows:
        state = str(row.get("state") or "").strip()
        # A query already limited to the United States may omit the state column.
        if state and state != "US":
            continue
        indicator = (row.get("indicator") or "").strip()
        if indicator and indicator != INDICATOR:
            continue
        year = int(str(row["year"]).strip())
        month_name = str(row["month"]).strip()
        if month_name not in MONTHS:
            raise ValueError(f"Unexpected CDC month label: {month_name}")
        key = (year, MONTHS[month_name])
        if best is None or key > best:
            best = key
    if best is None:
        raise ValueError("Provisional extract has no United States T40.4 month")
    return month_stamp(*best)


def latest_extract_timestamp(rows: list[dict]) -> str:
    stamps = sorted({(row.get("extracted_at") or "").strip() for row in rows if (row.get("extracted_at") or "").strip()})
    return stamps[-1] if stamps else ""


def latest_final_year(rows: list[dict]) -> str:
    years = []
    for row in rows:
        if (row.get("state") or "").strip() != "United States":
            continue
        if (row.get("period_type") or "").strip() != "month":
            continue
        if not (row.get("incident_deaths") or "").strip():
            continue
        years.append(int(str(row["year"]).strip()))
    if not years:
        raise ValueError("Final extract has no United States monthly deaths")
    return str(max(years))


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def fetch_api_month(session: requests.Session) -> tuple[str, str]:
    """Return the newest US T40.4 month and the dataset's rows-updated timestamp."""
    response = session.get(
        f"https://data.cdc.gov/resource/{DATASET_ID}.json",
        params={
            "indicator": INDICATOR,
            "state": "US",
            "$select": "year,month",
            "$limit": 5000,
        },
        timeout=60,
    )
    response.raise_for_status()
    latest = latest_provisional_month(response.json())
    meta = session.get(f"https://data.cdc.gov/api/views/{DATASET_ID}.json", timeout=60)
    meta.raise_for_status()
    updated_at = ""
    raw = meta.json().get("rowsUpdatedAt")
    if raw:
        updated_at = datetime.fromtimestamp(int(raw), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return latest, updated_at


def build_row(
    provisional_rows: list[dict],
    final_rows: list[dict],
    api_month: str,
    dataset_updated_at: str,
    checked_at: str,
) -> dict:
    seed_month = latest_provisional_month(provisional_rows)
    if api_month and api_month > seed_month:
        raise RuntimeError(
            f"CDC has published {api_month}, but the extract only reaches {seed_month}. "
            "Re-run soda_extractor.py before publishing."
        )
    return {
        "checked_at": checked_at,
        "cdc_dataset_id": DATASET_ID,
        "cdc_dataset_updated_at": dataset_updated_at,
        "latest_provisional_month": seed_month,
        "latest_final_year": latest_final_year(final_rows),
        "provisional_extract_at": latest_extract_timestamp(provisional_rows),
        "update_schedule": SCHEDULE,
        "note": NOTE,
    }


def write_row(row: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerow(row)


def main() -> int:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    provisional_rows = read_csv(provisional_seed_path())
    final_rows = read_csv(final_seed_path())
    api_month = ""
    dataset_updated_at = ""
    try:
        api_month, dataset_updated_at = fetch_api_month(requests.Session())
        logger.info("CDC API latest provisional month is %s", api_month)
    except Exception as exc:
        logger.warning("CDC freshness lookup failed (%s). The extract's own latest month is recorded.", exc)
    try:
        row = build_row(provisional_rows, final_rows, api_month, dataset_updated_at, checked_at)
    except Exception as exc:
        logger.error("%s", exc)
        return 1
    write_row(row, output_path())
    logger.info(
        "Provisional series through %s. Final certificates through %s.",
        row["latest_provisional_month"],
        row["latest_final_year"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
