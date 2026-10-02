"""The freshness check layers a final year with the newest provisional month."""

from data_engineering.data_sources.cdc_api.freshness import (
    build_row,
    latest_final_year,
    latest_provisional_month,
)


PROVISIONAL = [
    {"state": "US", "year": "2024", "month": "December", "indicator": "Synthetic opioids, excl. methadone (T40.4)", "extracted_at": "2026-09-26T00:00:00Z"},
    {"state": "US", "year": "2026", "month": "April", "indicator": "Synthetic opioids, excl. methadone (T40.4)", "extracted_at": "2026-09-26T00:00:00Z"},
    {"state": "CA", "year": "2026", "month": "May", "indicator": "Synthetic opioids, excl. methadone (T40.4)", "extracted_at": "2026-09-26T00:00:00Z"},
]

FINAL = [
    {"state": "United States", "year": "2024", "period_type": "month", "incident_deaths": "3307"},
    {"state": "United States", "year": "2023", "period_type": "year", "incident_deaths": "70000"},
    {"state": "Alabama", "year": "2024", "period_type": "month", "incident_deaths": "10"},
]


def test_latest_provisional_month_uses_the_national_series():
    assert latest_provisional_month(PROVISIONAL) == "2026-04"


def test_latest_provisional_month_accepts_a_query_that_already_filtered_to_the_nation():
    rows = [{"year": "2026", "month": "April", "indicator": "Synthetic opioids, excl. methadone (T40.4)"}]
    assert latest_provisional_month(rows) == "2026-04"


def test_latest_final_year_uses_national_monthly_counts():
    assert latest_final_year(FINAL) == "2024"


def test_build_row_records_the_layer_and_rejects_a_stale_extract():
    row = build_row(PROVISIONAL, FINAL, "2026-04", "2026-09-16T14:03:29Z", "2026-10-02T00:00:00Z")
    assert row["latest_provisional_month"] == "2026-04"
    assert row["latest_final_year"] == "2024"
    assert row["cdc_dataset_id"] == "xkb8-kh2a"
    assert "Monday" in row["update_schedule"]

    try:
        build_row(PROVISIONAL, FINAL, "2026-05", "", "2026-10-02T00:00:00Z")
    except RuntimeError as exc:
        assert "2026-05" in str(exc)
    else:
        raise AssertionError("A newer CDC month should fail the freshness check")
