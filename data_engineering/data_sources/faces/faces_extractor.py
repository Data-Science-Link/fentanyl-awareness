#!/usr/bin/env python3
"""Read the public DEA Faces of Fentanyl exhibit listing.

Families submit a photo, first name, state, and age to DEA and acknowledge
DEA's privacy policy before the photo is shown. DEA also takes removal
requests. This extractor keeps those public fields and the DEA-hosted image
address. It does not download image files. A person who leaves the exhibit
leaves this file on the next run.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EXHIBIT_URL = "https://fof.dea.gov/exhibit"
LISTING_URL = "https://fof.dea.gov/sites/default/files/timeline-min.json"
IMAGE_ROOT = "https://fof.dea.gov/sites/default/files/"
COLUMNS = [
    "dea_id",
    "first_name",
    "age",
    "age_description",
    "state",
    "image_url",
    "exhibit_url",
    "extracted_at",
]


def image_url(path: str) -> str:
    text = (path or "").strip()
    if not text:
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return IMAGE_ROOT + quote(text.lstrip("/"), safe="/")


def public_records(payload, extracted_at: str) -> pd.DataFrame:
    """Keep listings that have a first name and a photo path."""
    rows = []
    for item in payload:
        name = str(item.get("name") or "").strip()
        photo = image_url(str(item.get("image") or ""))
        if not name or name.upper() == "DATA NEEDED" or not photo:
            continue
        age = str(item.get("age") or "").strip()
        age_description = str(item.get("age_desc") or "").strip()
        if age == "0" and not age_description:
            age_description = "Under 1"
        rows.append(
            {
                "dea_id": str(item.get("id") or "").strip(),
                "first_name": name,
                "age": age,
                "age_description": age_description,
                "state": str(item.get("state") or "").strip(),
                "image_url": photo,
                "exhibit_url": EXHIBIT_URL,
                "extracted_at": extracted_at,
            }
        )
    frame = pd.DataFrame(rows, columns=COLUMNS)
    if frame.empty:
        raise RuntimeError("Faces of Fentanyl listing had no public photos")
    return frame.sort_values(["dea_id", "first_name"], kind="mergesort").reset_index(drop=True)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def output_paths() -> list[Path]:
    root = repo_root()
    return [
        root / "docs" / "sources" / "faces_of_fentanyl.csv",
        root / "Final_Datasets" / "faces_of_fentanyl.csv",
    ]


def write_outputs(frame: pd.DataFrame) -> None:
    for path in output_paths():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        logger.info("Wrote %s (%s rows)", path, len(frame))


def main(argv: list[str] | None = None) -> int:
    del argv
    existing = all(path.exists() and path.stat().st_size > 0 for path in output_paths())
    try:
        from curl_cffi import requests as curl_requests

        response = curl_requests.Session(impersonate="chrome").get(LISTING_URL, timeout=90)
        if response.status_code >= 400:
            raise RuntimeError(f"Exhibit listing returned HTTP {response.status_code}")
        extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frame = public_records(response.json(), extracted_at)
        write_outputs(frame)
        return 0
    except Exception as exc:
        if existing:
            logger.warning("Faces of Fentanyl extract failed (%s). Keeping the existing file.", exc)
            return 0
        logger.error("Faces of Fentanyl extract failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
