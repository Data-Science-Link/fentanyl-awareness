from datetime import date

from data_engineering.transforms.monthly_deaths import (
    ESTIMATED,
    OFFICIAL,
    estimate_monthly_deaths,
)


def _month(index):
    """Month 0 is January 2020."""
    return date(2020 + index // 12, index % 12 + 1, 1)


def _rolling(deaths):
    """12-month ending totals starting at month index 11."""
    rows = []
    for index in range(11, len(deaths)):
        rows.append(
            {
                "month": _month(index),
                "headline_deaths": sum(deaths[index - 11 : index + 1]),
            }
        )
    return rows


def test_lag_identity_recovers_monthly_deaths_after_the_final_year():
    deaths = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 15, 25, 35, 45]
    final = [{"month": _month(index), "deaths": deaths[index]} for index in range(12)]
    series = estimate_monthly_deaths(final, _rolling(deaths))
    by_month = {row["month"]: row for row in series}

    for index, count in enumerate(deaths):
        row = by_month[_month(index)]
        assert row["estimated_deaths"] == count
        if index < 12:
            assert row["how_produced"] == OFFICIAL
            assert row["is_negative_estimate"] is False
        else:
            assert row["how_produced"] == ESTIMATED
            assert row["change_in_12_month_total"] == deaths[index] - deaths[index - 12]


def test_final_count_is_not_replaced_by_the_lag_estimate():
    final = [{"month": _month(11), "deaths": 100}, {"month": _month(12), "deaths": 4}]
    headline = [
        {"month": _month(11), "headline_deaths": 1000},
        {"month": _month(12), "headline_deaths": 5000},
    ]
    series = estimate_monthly_deaths(final, headline)
    row = next(item for item in series if item["month"] == _month(12))
    assert row["estimated_deaths"] == 4
    assert row["how_produced"] == OFFICIAL


def test_negative_estimate_is_kept_and_flagged():
    final = [{"month": _month(0), "deaths": 5}]
    headline = [
        {"month": _month(11), "headline_deaths": 100},
        {"month": _month(12), "headline_deaths": 90},
    ]
    series = estimate_monthly_deaths(final, headline)
    row = next(item for item in series if item["month"] == _month(12))
    assert row["estimated_deaths"] == -5
    assert row["is_negative_estimate"] is True
    assert row["how_produced"] == ESTIMATED


def test_predicted_month_is_not_differenced_from_a_reported_month():
    final = [{"month": _month(0), "deaths": 100}]
    headline = [
        {
            "month": _month(11),
            "headline_deaths": 1000,
            "headline_basis": "reported",
            "reported_deaths": 1000,
            "predicted_deaths": 1010,
        },
        {
            "month": _month(12),
            "headline_deaths": 1005,
            "headline_basis": "predicted",
            "reported_deaths": 980,
            "predicted_deaths": 1005,
        },
    ]
    series = estimate_monthly_deaths(final, headline)
    row = next(item for item in series if item["month"] == _month(12))
    assert row["change_in_12_month_total"] == -5
    assert row["estimated_deaths"] == 95
    assert row["how_produced"] == ESTIMATED


def test_published_monthly_file_keeps_each_change_inside_one_series():
    from pathlib import Path

    import pandas as pd

    root = Path(__file__).resolve().parents[1]
    monthly_path = root / "Final_Datasets" / "deaths_by_month.csv"
    provisional_path = root / "Final_Datasets" / "fact_fentanyl_deaths_over_time.csv"
    final_path = root / "Final_Datasets" / "fact_nvss_final_t40_4.csv"
    monthly = pd.read_csv(monthly_path)
    provisional = pd.read_csv(provisional_path)
    final = pd.read_csv(final_path)
    nation = provisional[provisional["geo_type"] == "nation"]
    headlines = []
    for record in nation.to_dict(orient="records"):
        if pd.isna(record["headline_deaths"]):
            continue
        headlines.append(
            {
                "month": record["month"],
                "headline_deaths": int(record["headline_deaths"]),
                "headline_basis": record["headline_basis"],
                "reported_deaths": None if pd.isna(record["rolling_12_month_deaths"]) else int(record["rolling_12_month_deaths"]),
                "predicted_deaths": None if pd.isna(record["predicted_12_month_deaths"]) else int(record["predicted_12_month_deaths"]),
            }
        )
    finals = []
    national_months = final[(final["geo_type"] == "nation") & (final["period_type"] == "month")]
    for record in national_months.to_dict(orient="records"):
        suppressed = str(record["is_suppressed"]).strip().lower() == "true"
        if pd.isna(record["incident_deaths"]) or suppressed:
            continue
        finals.append({"month": record["month"], "deaths": int(record["incident_deaths"])})
    expected = {row["month"].strftime("%Y-%m"): row for row in estimate_monthly_deaths(finals, headlines)}
    for record in monthly.to_dict(orient="records"):
        month = record["Month"]
        if month not in expected:
            continue
        assert int(record["Estimated deaths"]) == expected[month]["estimated_deaths"]
        change = record["Change in the 12-month total"]
        if pd.isna(change):
            assert expected[month]["change_in_12_month_total"] is None
        else:
            assert int(change) == expected[month]["change_in_12_month_total"]


def test_lag_is_ignored_when_a_headline_month_is_missing():
    final = [{"month": _month(0), "deaths": 8}]
    headline = [
        {"month": _month(10), "headline_deaths": 50},
        {"month": _month(12), "headline_deaths": 80},
    ]
    series = estimate_monthly_deaths(final, headline)
    assert all(row["month"] != _month(12) for row in series)
