"""Public policy actions are sourced and cover the themes a reader would look for."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    ROOT / "docs" / "sources" / "policy_actions.csv",
    ROOT / "Final_Datasets" / "policy_actions.csv",
)
THEMES = {
    "Border",
    "Immigration enforcement",
    "Supply chain",
    "Pressure on China",
    "Public health",
    "Law",
}


def rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_policy_files_match_and_name_a_source():
    first, second = (rows(path) for path in PATHS)
    assert first == second
    assert len(first) >= 10
    for row in first:
        assert row["theme"] in THEMES
        assert row["source_url"].startswith("https://")
        assert row["action_date"]
        assert row["summary"]


def test_policy_themes_include_border_enforcement_supply_and_china():
    present = {row["theme"] for row in rows(PATHS[0])}
    assert {"Border", "Immigration enforcement", "Supply chain", "Pressure on China"} <= present
