#!/usr/bin/env python3
"""Age, race, and drug-poisoning share from CDC WONDER.

These are national final-year tabulations for the same T40.4 definition
used by the rest of the pipeline. The drug-poisoning total has no T40.4
filter, so the share is "drug-poisoning deaths that also list T40.4."
Drug categories overlap, so that share is not a slice of a pie.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

import pandas as pd

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from data_engineering.data_sources.nvss_wonder.wonder_extractor import (  # noqa: E402
    DATASETS,
    DRUG_POISONING_UCD,
    _death_cell,
    _export_csv,
    _pairs,
    _replace,
    _response_error,
    make_session,
    open_request_form,
    read_year_options,
    time,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REQUEST_GAP_SECONDS = 15
D157 = DATASETS[1]


class _OptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.options: dict[str, list[tuple[str, str]]] = {}
        self._select: str | None = None
        self._value: str | None = None
        self._label: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "select":
            self._select = attr.get("name")
            if self._select:
                self.options.setdefault(self._select, [])
        elif tag == "option" and self._select:
            self._value = attr.get("value", "")
            self._label = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self._select and self._value is not None:
            label = " ".join("".join(self._label).split())
            self.options[self._select].append((self._value, label))
            self._value = None
            self._label = []
        elif tag == "select":
            self._select = None

    def handle_data(self, data: str) -> None:
        if self._value is not None:
            self._label.append(data)


def group_options(html: str) -> list[tuple[str, str]]:
    parser = _OptionParser()
    parser.feed(html)
    return parser.options.get("B_1", [])


def choose_group(options: list[tuple[str, str]], kind: str) -> str:
    """Pick a WONDER group-by value from the option label."""
    labels = [(value, label.lower()) for value, label in options if value and value != "*None*"]
    if kind == "age":
        patterns = ("ten-year age", "age group", "age groups")
    elif kind == "race":
        patterns = ("hispanic origin and race", "race and hispanic", "single race 6")
    else:
        raise ValueError(kind)
    for pattern in patterns:
        for value, label in labels:
            if pattern in label:
                return value
    available = ", ".join(label for _value, label in options[:12])
    raise RuntimeError(f"WONDER form has no {kind} group. Options start: {available}")


def _prepare(fields, prefix: str, group_code: str, years: list[int], multiple_cause: str | None, title: str):
    updated = [field[:] for field in fields]
    groups = [group_code, "*None*", "*None*", "*None*", "*None*"]
    for index, value in enumerate(groups, start=1):
        updated = _replace(updated, f"B_{index}", [value])
    updated = _replace(updated, f"F_{prefix}.V1", [str(year) for year in years])
    updated = _replace(updated, "O_V2_fmode", ["fadv"])
    updated = _replace(updated, "O_V13_fmode", ["fadv"])
    updated = _replace(updated, f"V_{prefix}.V2", ["\n".join(DRUG_POISONING_UCD)])
    updated = _replace(updated, f"V_{prefix}.V13", [multiple_cause or ""])
    updated = _replace(updated, "O_title", [title])
    updated = [field for field in updated if field[0] != "O_show_totals"]
    updated = [field for field in updated if not field[0].startswith("action-")]
    updated.append(["action-Send", "Send"])
    return updated


def run_grouped(session, action, fields, prefix, group_code, years, multiple_cause, title) -> str:
    payload = _prepare(fields, prefix, group_code, years, multiple_cause, title)
    response = session.post(action, data=_pairs(payload), timeout=300)
    error = _response_error(response.text, response.status_code)
    if error:
        raise RuntimeError(f"WONDER {title} failed ({error})")
    return _export_csv(session, action, response.text)


def parse_grouped_export(text: str, year: int, extracted_at: str) -> pd.DataFrame:
    """Read a one-way WONDER export into group, deaths, suppressed."""
    body = []
    for line in text.splitlines():
        if line.strip().strip('"') == "---":
            break
        body.append(line)
    frame = pd.read_csv(StringIO("\n".join(body)), dtype=str)
    group_column = None
    for column in frame.columns:
        if column not in {"Notes", "Deaths", "Population", "Crude Rate", "Year", "Year Code"} and "Code" not in column:
            group_column = column
            break
    if group_column is None or "Deaths" not in frame.columns:
        raise RuntimeError(f"WONDER export columns were {list(frame.columns)}")
    rows = []
    for record in frame.to_dict(orient="records"):
        notes = str(record.get("Notes") or "").strip().lower()
        if notes == "total":
            continue
        label = str(record.get(group_column) or "").strip()
        if not label or label.lower() == "nan":
            continue
        parsed = _death_cell(str(record.get("Deaths") or ""))
        if parsed is None:
            continue
        deaths, suppressed = parsed
        rows.append(
            {
                "year": year,
                "group": label,
                "deaths": deaths,
                "is_suppressed": suppressed,
                "extracted_at": extracted_at,
            }
        )
    if not rows:
        raise RuntimeError("WONDER export had no grouped death rows")
    return pd.DataFrame(rows)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _write(frame: pd.DataFrame, filename: str) -> None:
    root = repo_root()
    for folder in (root / "docs" / "sources", root / "Final_Datasets"):
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename
        frame.to_csv(path, index=False)
        logger.info("Wrote %s (%s rows)", path, len(frame))


def extract(session, sleep=time.sleep) -> dict[str, pd.DataFrame]:
    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    action, fields, html = open_request_form(session, D157["page"])
    prefix = "D157"
    years = [year for year in read_year_options(html, prefix) if D157["min_year"] <= year <= D157["max_year"]]
    if not years:
        raise RuntimeError("D157 did not list a final year")
    year = max(years)
    options = group_options(html)
    logger.info("D157 latest year %s", year)
    age_code = choose_group(options, "age")
    race_code = choose_group(options, "race")
    age_csv = run_grouped(session, action, fields, prefix, age_code, [year], "T40.4", "t40.4 age")
    sleep(REQUEST_GAP_SECONDS)
    race_csv = run_grouped(session, action, fields, prefix, race_code, [year], "T40.4", "t40.4 race")
    sleep(REQUEST_GAP_SECONDS)
    # No multiple-cause drug code: all drug-poisoning deaths, for the share.
    total_csv = run_grouped(session, action, fields, prefix, f"{prefix}.V1-level1", [year], None, "drug poisoning")
    age = parse_grouped_export(age_csv, year, extracted_at)
    race = parse_grouped_export(race_csv, year, extracted_at)
    total = parse_grouped_export(total_csv, year, extracted_at)
    t40 = int(age["deaths"].fillna(0).sum()) if not age["is_suppressed"].all() else None
    # Prefer the unsuppressed T40.4 total from the age table only if every age is present.
    # The national T40.4 total is the sum of age rows when none are suppressed.
    drug_total = None
    if not total.empty and not bool(total.iloc[0]["is_suppressed"]):
        drug_total = int(total.iloc[0]["deaths"])
    if t40 is None or bool(age["is_suppressed"].any()):
        t40_deaths = None
    else:
        t40_deaths = int(age["deaths"].sum())
    share = pd.DataFrame(
        [
            {
                "year": year,
                "t40_4_deaths": t40_deaths,
                "drug_poisoning_deaths": drug_total,
                "share_of_drug_poisoning_deaths": (
                    round(t40_deaths / drug_total, 4) if t40_deaths and drug_total else None
                ),
                "note": (
                    "Share of drug-poisoning deaths that also list a synthetic opioid "
                    "other than methadone. One death can list more than one drug, so "
                    "this is not a slice of a pie."
                ),
                "extracted_at": extracted_at,
            }
        ]
    )
    return {"age": age, "race": race, "share": share}


def main(argv: list[str] | None = None) -> int:
    del argv
    root = repo_root()
    existing = (root / "docs" / "sources" / "wonder_age.csv").exists()
    try:
        tables = extract(make_session())
        _write(tables["age"], "wonder_age.csv")
        _write(tables["race"], "wonder_race.csv")
        _write(tables["share"], "wonder_drug_share.csv")
        return 0
    except Exception as exc:
        if existing:
            logger.warning("WONDER demographic extract failed (%s). Keeping the existing files.", exc)
            return 0
        logger.error("WONDER demographic extract failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
