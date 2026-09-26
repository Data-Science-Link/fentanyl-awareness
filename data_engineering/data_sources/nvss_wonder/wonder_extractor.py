#!/usr/bin/env python3
"""
Final NVSS T40.4 incident deaths, 1999 through the latest final year.

CDC WONDER's XML data-request API refuses state, month-by-state, and other
subnational tabulations ("only national data are available" for vital
statistics). The public-use multiple-cause files blank residence state for
the same reason. State and month counts are therefore requested from the
WONDER request form, which is the interface CDC documents for those
tabulations:

- D77 Multiple Cause of Death, 1999-2020, used for 1999-2017
- D157 Multiple Cause of Death, 2018-latest single-race final

A death is counted when the underlying cause is drug poisoning
(ICD-10 X40-X44, X60-X64, X85, Y10-Y14) and a multiple-cause code is T40.4.
Counts are not differenced from the VSRR 12-month column. Annual totals come
from the year query, not from summing months. Cells of 1-9 deaths stay null
with is_suppressed set. Overlap years 2018-2020 use D157 only.

The United States row is the WONDER national total (50 states and DC).
Puerto Rico is not in these WONDER residence lists.
"""

from __future__ import annotations

import argparse
import csv
import io
import logging
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WONDER_HOME = "https://wonder.cdc.gov"
DATASETS = (
    {
        "page": "https://wonder.cdc.gov/mcd-icd10.html",
        "dataset_id": "D77",
        "min_year": 1999,
        "max_year": 2017,
    },
    {
        "page": "https://wonder.cdc.gov/mcd-icd10-expanded.html",
        "dataset_id": "D157",
        "min_year": 2018,
        "max_year": 2100,
    },
)
DRUG_POISONING_UCD = (
    "X40", "X41", "X42", "X43", "X44",
    "X60", "X61", "X62", "X63", "X64",
    "X85",
    "Y10", "Y11", "Y12", "Y13", "Y14",
)
SUPPRESS_BELOW = 10
DATA_SOURCE = "NVSS final"
REQUEST_GAP_SECONDS = 15
# Published NCHS multiple-cause total for 2024 drug-poisoning deaths with T40.4.
EXPECTED_2024_US_DEATHS = 47735


def source_dataset_for_year(year: int) -> str:
    """WONDER final-file id that covers this death year."""
    return "D77" if year <= 2017 else "D157"


def geo_type_for(state: str) -> str:
    if state == "United States":
        return "nation"
    if state == "Puerto Rico":
        return "territory"
    return "state"


class _WonderFormParser(HTMLParser):
    """Collect the WONDER request form as repeated name/value pairs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.action: str | None = None
        self.fields: list[list[str]] = []
        self._in_form = False
        self._select: str | None = None
        self._options: list[tuple[str, bool]] = []
        self._option_value: str | None = None
        self._option_selected = False
        self._textarea_name: str | None = None
        self._textarea: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "form" and attr.get("id") == "wonderform":
            self._in_form = True
            self.action = attr.get("action") or self.action
            return
        if not self._in_form:
            return
        if tag == "input":
            name = attr.get("name")
            if not name:
                return
            input_type = attr.get("type", "text").lower()
            if input_type in {"submit", "button", "image", "reset"}:
                return
            if input_type in {"checkbox", "radio"}:
                if "checked" in attr:
                    self.fields.append([name, attr.get("value", "on")])
                return
            self.fields.append([name, attr.get("value", "")])
        elif tag == "select":
            self._select = attr.get("name")
            self._options = []
        elif tag == "option" and self._select:
            self._option_value = attr.get("value", "")
            self._option_selected = "selected" in attr
        elif tag == "textarea":
            self._textarea_name = attr.get("name")
            self._textarea = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self._in_form:
            self._in_form = False
        elif tag == "option" and self._select is not None and self._option_value is not None:
            self._options.append((self._option_value, self._option_selected))
            self._option_value = None
        elif tag == "select" and self._select:
            selected = [value for value, is_selected in self._options if is_selected]
            if not selected and self._options:
                selected = [self._options[0][0]]
            for value in selected:
                self.fields.append([self._select, value])
            self._select = None
            self._options = []
        elif tag == "textarea" and self._textarea_name:
            self.fields.append([self._textarea_name, "".join(self._textarea)])
            self._textarea_name = None
            self._textarea = []

    def handle_data(self, data: str) -> None:
        if self._textarea_name is not None:
            self._textarea.append(data)


def parse_wonder_form(html: str) -> tuple[str | None, list[list[str]]]:
    parser = _WonderFormParser()
    parser.feed(html)
    return parser.action, parser.fields


def _replace(fields: list[list[str]], name: str, values: list[str]) -> list[list[str]]:
    kept = [field for field in fields if field[0] != name]
    kept.extend([name, value] for value in values)
    return kept


def _dataset_prefix(fields: list[list[str]]) -> str:
    for name, _value in fields:
        match = re.fullmatch(r"F_(D\d+)\.V1", name)
        if match:
            return match.group(1)
    raise RuntimeError("WONDER form did not include a year field")


class _YearOptionParser(HTMLParser):
    def __init__(self, field_name: str) -> None:
        super().__init__(convert_charrefs=True)
        self.field_name = field_name
        self.years: list[int] = []
        self._capture = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "select" and attr.get("name") == self.field_name:
            self._capture = True
        elif tag == "option" and self._capture and attr.get("value", "").isdigit():
            self.years.append(int(attr["value"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "select" and self._capture:
            self._capture = False


def read_year_options(html: str, prefix: str) -> list[int]:
    parser = _YearOptionParser(f"F_{prefix}.V1")
    parser.feed(html)
    return parser.years


def _group_by(prefix: str, kind: str) -> list[str]:
    if kind == "us-year":
        groups = [f"{prefix}.V1-level1"]
    elif kind == "us-month":
        groups = [f"{prefix}.V1-level2"]
    elif kind == "state-year":
        groups = [f"{prefix}.V9-level1", f"{prefix}.V1-level1"]
    elif kind == "state-month":
        groups = [f"{prefix}.V9-level1", f"{prefix}.V1-level2"]
    else:
        raise ValueError(kind)
    groups.extend(["*None*"] * (5 - len(groups)))
    return groups


def _prepare_query(
    fields: list[list[str]],
    prefix: str,
    kind: str,
    years: list[int],
    title: str,
) -> list[list[str]]:
    updated = [field[:] for field in fields]
    for index, value in enumerate(_group_by(prefix, kind), start=1):
        updated = _replace(updated, f"B_{index}", [value])
    updated = _replace(updated, f"F_{prefix}.V1", [str(year) for year in years])
    updated = _replace(updated, f"O_V2_fmode", ["fadv"])
    updated = _replace(updated, f"O_V13_fmode", ["fadv"])
    updated = _replace(updated, f"V_{prefix}.V2", ["\n".join(DRUG_POISONING_UCD)])
    updated = _replace(updated, f"V_{prefix}.V13", ["T40.4"])
    updated = _replace(updated, "O_title", [title])
    updated = [field for field in updated if field[0] != "O_show_totals"]
    updated = [field for field in updated if not field[0].startswith("action-")]
    updated.append(["action-Send", "Send"])
    return updated


def _pairs(fields: list[list[str]]) -> list[tuple[str, str]]:
    return [(name, value) for name, value in fields]


def _absolute(action: str | None) -> str:
    if not action:
        raise RuntimeError("WONDER form has no action")
    return urljoin(WONDER_HOME, action)


def _response_error(text: str, status: int) -> str | None:
    if status >= 400 or "error processing your request" in text.lower():
        return f"HTTP {status}"
    return None


def open_request_form(session, page_url: str) -> tuple[str, list[list[str]], str]:
    """Accept the data-use terms and return the request-form action, fields, and HTML."""
    landing = session.get(page_url, timeout=90)
    if landing.status_code >= 400:
        raise RuntimeError(f"WONDER page {page_url} returned HTTP {landing.status_code}")
    action, fields = parse_wonder_form(landing.text)
    if any(name == "B_1" for name, _value in fields):
        return _absolute(action), fields, landing.text
    fields = [field for field in fields if not field[0].startswith("action-")]
    fields.append(["action-I Agree", "I Agree"])
    agreed = session.post(_absolute(action), data=_pairs(fields), timeout=90)
    error = _response_error(agreed.text, agreed.status_code)
    if error:
        raise RuntimeError(f"WONDER data-use agreement failed ({error})")
    action, fields = parse_wonder_form(agreed.text)
    if not any(name == "B_1" for name, _value in fields):
        raise RuntimeError("WONDER did not open the request form")
    return _absolute(action), fields, agreed.text


def _export_csv(session, action: str, results_html: str) -> str:
    export_action, fields = parse_wonder_form(results_html)
    if not fields:
        raise RuntimeError("WONDER results page had no form to export")
    fields = _replace(fields, "O_export-format", ["csv"])
    fields = [field for field in fields if not field[0].startswith("action-")]
    fields.append(["action-Export", "Download"])
    exported = session.post(_absolute(export_action or action), data=_pairs(fields), timeout=180)
    error = _response_error(exported.text, exported.status_code)
    if error or "Notes" not in exported.text.splitlines()[0]:
        raise RuntimeError(f"WONDER export was not a results table ({error or 'unexpected body'})")
    return exported.text


def run_tabulation(session, action: str, fields: list[list[str]], prefix: str, kind: str, years: list[int]) -> str:
    payload = _prepare_query(fields, prefix, kind, years, f"t40.4 {prefix} {kind}")
    if any("V9-level2" in value for _name, value in payload):
        raise RuntimeError("County grouping is not part of this extract")
    response = session.post(action, data=_pairs(payload), timeout=300)
    error = _response_error(response.text, response.status_code)
    if error:
        raise RuntimeError(f"WONDER {prefix} {kind} failed ({error})")
    return _export_csv(session, action, response.text)


def _death_cell(raw: str) -> tuple[int | None, bool] | None:
    text = (raw or "").strip().replace(",", "")
    if text.lower() == "suppressed":
        return None, True
    if not text.isdigit():
        return None
    count = int(text)
    if 0 < count < SUPPRESS_BELOW:
        return None, True
    return count, False


def parse_wonder_export(text: str, source_dataset: str, extracted_at: str) -> pd.DataFrame:
    """Turn a WONDER CSV export into annual or monthly incident-death rows."""
    body = []
    for line in text.splitlines():
        if line.strip().strip('"') == "---":
            break
        body.append(line)
    reader = csv.DictReader(io.StringIO("\n".join(body)))
    rows = []
    for record in reader:
        notes = (record.get("Notes") or "").strip().lower()
        if notes == "total":
            continue
        parsed = _death_cell(record.get("Deaths") or "")
        if parsed is None:
            continue
        deaths, suppressed = parsed
        state = (record.get("State") or "").strip() or "United States"
        month_code = (record.get("Month Code") or "").strip()
        if month_code:
            year_text, month_text = month_code.split("/", 1)
            year = int(year_text)
            month = f"{int(year_text):04d}-{int(month_text):02d}-01"
            period_type = "month"
        else:
            year_text = (record.get("Year Code") or record.get("Year") or "").strip()
            if not year_text.isdigit():
                continue
            year = int(year_text)
            month = ""
            period_type = "year"
        rows.append(
            {
                "year": year,
                "month": month,
                "state": state,
                "geo_type": geo_type_for(state),
                "period_type": period_type,
                "incident_deaths": deaths,
                "is_suppressed": suppressed,
                "data_source": DATA_SOURCE,
                "source_dataset": source_dataset,
                "extracted_at": extracted_at,
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values(
        ["period_type", "year", "month", "state"], kind="mergesort"
    ).reset_index(drop=True)


def _check_known_totals(frame: pd.DataFrame) -> None:
    us_2024 = frame[
        (frame["year"] == 2024)
        & (frame["state"] == "United States")
        & (frame["period_type"] == "year")
        & (frame["source_dataset"] == "D157")
    ]
    if us_2024.empty:
        return
    deaths = int(us_2024.iloc[0]["incident_deaths"])
    if deaths != EXPECTED_2024_US_DEATHS:
        raise RuntimeError(
            f"2024 United States T40.4 deaths were {deaths}, expected {EXPECTED_2024_US_DEATHS}"
        )


def extract(session, sleep=time.sleep) -> tuple[pd.DataFrame, list[str]]:
    """Query D77 and D157. Monthly failures are returned and do not drop annual rows."""
    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    frames: list[pd.DataFrame] = []
    monthly_failures: list[str] = []
    for spec in DATASETS:
        action, fields, html = open_request_form(session, spec["page"])
        prefix = _dataset_prefix(fields)
        if prefix != spec["dataset_id"]:
            raise RuntimeError(f"{spec['page']} opened {prefix}, expected {spec['dataset_id']}")
        available = [
            year for year in read_year_options(html, prefix)
            if spec["min_year"] <= year <= spec["max_year"]
        ]
        if not available:
            raise RuntimeError(f"{prefix} has no years in {spec['min_year']}-{spec['max_year']}")
        logger.info("%s years %s-%s", prefix, available[0], available[-1])
        for kind in ("us-year", "us-month", "state-year", "state-month"):
            try:
                csv_text = run_tabulation(session, action, fields, prefix, kind, available)
                frame = parse_wonder_export(csv_text, prefix, extracted_at)
                if frame.empty:
                    raise RuntimeError("export had no death rows")
                frames.append(frame)
                logger.info("%s %s: %s rows", prefix, kind, len(frame))
            except Exception as exc:
                if "month" not in kind:
                    raise
                logger.warning("%s %s failed (%s). Annual rows are unchanged.", prefix, kind, exc)
                monthly_failures.append(f"{prefix} {kind}: {exc}")
            sleep(REQUEST_GAP_SECONDS)
    if not frames:
        raise RuntimeError("WONDER returned no final T40.4 tables")
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(
        ["period_type", "year", "month", "state"], kind="mergesort"
    ).reset_index(drop=True)
    _check_known_totals(combined)
    return combined, monthly_failures


def default_output_path() -> Path:
    script_path = Path(__file__).resolve()
    return (
        script_path.parent.parent.parent
        / "data_build_tool"
        / "dbt"
        / "seeds"
        / "nvss_final_t40_4_deaths.csv"
    )


def make_session():
    """HTTP session that can complete the WONDER form handshake."""
    from curl_cffi import requests as curl_requests

    return curl_requests.Session(impersonate="chrome")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract final NVSS T40.4 deaths from CDC WONDER")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    output_path = args.output or default_output_path()
    existing = output_path.exists() and output_path.stat().st_size > 0
    try:
        frame, monthly_failures = extract(make_session())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output_path, index=False)
        logger.info("Wrote %s (%s rows)", output_path, len(frame))
        for failure in monthly_failures:
            logger.warning("Monthly WONDER query failed: %s", failure)
        return 0
    except Exception as exc:
        if existing:
            logger.warning(
                "Final NVSS extract failed (%s). Keeping the existing seed at %s.",
                exc,
                output_path,
            )
            return 0
        logger.error("Final NVSS extract failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
