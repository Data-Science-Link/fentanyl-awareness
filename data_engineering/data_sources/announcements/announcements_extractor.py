#!/usr/bin/env python3
"""Official announcements that mention fentanyl.

The list is built from agency feeds and pages, not from a choice of news
outlets. Each row keeps the title, date, publisher, and URL. If a feed is
down, rows already saved for that publisher stay in the file.
"""

from __future__ import annotations

import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

COLUMNS = ["published", "title", "publisher", "url", "extracted_at"]
FEEDS = (
    {
        "publisher": "Centers for Disease Control and Prevention",
        "url": "https://tools.cdc.gov/api/v2/resources/media/132608.rss",
        "kind": "rss",
    },
)
# Releases already checked against the page they link to. They stay in the
# file when a feed does not carry them.
BASELINE = (
    {
        "published": "2025-05-15",
        "title": "DEA releases the 2025 National Drug Threat Assessment",
        "publisher": "Drug Enforcement Administration",
        "url": "https://www.dea.gov/press-releases/2025/05/15/dea-releases-2025-national-drug-threat-assessment",
    },
    {
        "published": "2023-04-12",
        "title": "Fentanyl combined with xylazine designated an emerging threat",
        "publisher": "White House Office of National Drug Control Policy",
        "url": "https://www.whitehouse.gov/ondcp/briefing-room/2023/04/12/biden-harris-administration-designates-fentanyl-combined-with-xylazine-as-an-emerging-threat-to-the-united-states/",
    },
    {
        "published": "2023-03-13",
        "title": "Operation Blue Lotus launch reported by ICE",
        "publisher": "Immigration and Customs Enforcement",
        "url": "https://www.ice.gov/news/releases/operation-blue-lotus-stops-more-900-pounds-fentanyl-entering-us-first-week",
    },
    {
        "published": "2023-05-31",
        "title": "CBP statement on fentanyl seized during Operation Blue Lotus",
        "publisher": "U.S. Customs and Border Protection",
        "url": "https://www.cbp.gov/newsroom/national-media-release/statement-acting-commissioner-troy-miller-cbp-s-successful-fentanyl",
    },
)


def mentions_fentanyl(title: str, summary: str = "") -> bool:
    text = f"{title} {summary}".lower()
    return "fentanyl" in text or "synthetic opioid" in text


def _text(node, name: str) -> str:
    child = node.find(name)
    return (child.text or "").strip() if child is not None and child.text else ""


def parse_rss(xml_text: str, publisher: str, extracted_at: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.findall(".//item"):
        title = _text(item, "title")
        summary = _text(item, "description")
        if not mentions_fentanyl(title, summary):
            continue
        url = _text(item, "link")
        raw_date = _text(item, "pubDate")
        published = ""
        if raw_date:
            try:
                published = parsedate_to_datetime(raw_date).date().isoformat()
            except (TypeError, ValueError, IndexError):
                published = raw_date[:10]
        if not title or not url:
            continue
        rows.append(
            {
                "published": published,
                "title": re.sub(r"\s+", " ", title),
                "publisher": publisher,
                "url": url,
                "extracted_at": extracted_at,
            }
        )
    return rows


def parse_html_links(html: str, publisher: str, extracted_at: str, host: str) -> list[dict]:
    """Pull linked titles that mention fentanyl. Dates are left blank when the page has none."""
    rows = []
    for href, raw_title in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.I | re.S):
        title = re.sub(r"<[^>]+>", " ", raw_title)
        title = re.sub(r"\s+", " ", title).strip()
        if not mentions_fentanyl(title):
            continue
        url = href if href.startswith("http") else host.rstrip("/") + "/" + href.lstrip("/")
        rows.append(
            {
                "published": "",
                "title": title,
                "publisher": publisher,
                "url": url,
                "extracted_at": extracted_at,
            }
        )
    return rows


def combine(fetched: list[dict], previous: pd.DataFrame | None, extracted_at: str) -> pd.DataFrame:
    """Union of baseline, new rows, and prior rows from publishers that returned nothing."""
    rows = [dict(item, extracted_at=extracted_at) for item in BASELINE]
    rows.extend(fetched)
    fetched_publishers = {item["publisher"] for item in fetched}
    if previous is not None and not previous.empty:
        for record in previous.to_dict(orient="records"):
            if record.get("publisher") not in fetched_publishers:
                rows.append(record)
    frame = pd.DataFrame(rows, columns=COLUMNS)
    frame["url"] = frame["url"].astype(str).str.strip()
    frame = frame[frame["url"] != ""]
    frame = frame.drop_duplicates(subset=["url"], keep="first")
    frame = frame.sort_values(["published", "title"], ascending=[False, True], kind="mergesort")
    return frame.reset_index(drop=True)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def output_paths() -> list[Path]:
    root = repo_root()
    return [
        root / "docs" / "sources" / "official_announcements.csv",
        root / "Final_Datasets" / "official_announcements.csv",
    ]


def write_outputs(frame: pd.DataFrame) -> None:
    for path in output_paths():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        logger.info("Wrote %s (%s rows)", path, len(frame))


def load_previous() -> pd.DataFrame | None:
    path = output_paths()[0]
    if not path.exists() or path.stat().st_size == 0:
        return None
    return pd.read_csv(path, dtype=str).fillna("")


def fetch_all(session, extracted_at: str) -> list[dict]:
    rows = []
    for feed in FEEDS:
        try:
            response = session.get(feed["url"], timeout=60)
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code}")
            rows.extend(parse_rss(response.text, feed["publisher"], extracted_at))
            logger.info("%s: %s fentanyl items in this response", feed["publisher"], len(rows))
        except Exception as exc:
            logger.warning("%s feed failed (%s). Prior rows for that publisher are kept.", feed["publisher"], exc)
    return rows


def main(argv: list[str] | None = None) -> int:
    del argv
    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    previous = load_previous()
    try:
        from curl_cffi import requests as curl_requests

        fetched = fetch_all(curl_requests.Session(impersonate="chrome"), extracted_at)
    except Exception as exc:
        logger.warning("Announcement fetch failed (%s).", exc)
        fetched = []
    frame = combine(fetched, previous, extracted_at)
    if frame.empty:
        logger.error("No official announcements to publish")
        return 1
    write_outputs(frame)
    return 0


if __name__ == "__main__":
    sys.exit(main())
