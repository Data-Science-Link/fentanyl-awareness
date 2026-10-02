"""Estimated deaths in a single month from final counts and 12-month totals.

CDC's provisional file is a 12-month ending total. The change from one month
to the next equals deaths in the new month minus deaths in the month that
fell out of the window:

    H_t - H_{t-1} = deaths_t - deaths_{t-12}

When a final death-certificate count exists, that count is used. After the
last final month, deaths in month t are estimated as:

    deaths_t = (H_t - H_{t-1}) + deaths_{t-12}

H is the provisional headline count (CDC's predicted count when CDC already
flags the month as incomplete, or when the month is inside the latest six
months). The change from one month to the next stays inside one CDC series.
A predicted total is not subtracted from a reported total. That gap is a
reporting adjustment, not deaths in a single month.
"""

from __future__ import annotations

from datetime import date

OFFICIAL = "Official final count"
ESTIMATED = "Estimated from the change in the 12-month total"


def month_start(value) -> date:
    """First day of the month for a date or an ISO date string."""
    if isinstance(value, date):
        return value.replace(day=1)
    text = str(value)[:10]
    year, month, _day = text.split("-")
    return date(int(year), int(month), 1)


def add_months(value: date, count: int) -> date:
    """Move a first-of-month date by a whole number of months."""
    start = month_start(value)
    index = start.month - 1 + count
    return date(start.year + index // 12, index % 12 + 1, 1)


def _series_value(row, basis):
    """Value to difference. Predicted months use predicted on both sides."""
    if basis == "predicted" and row.get("predicted_deaths") is not None:
        return int(row["predicted_deaths"])
    if basis == "reported" and row.get("reported_deaths") is not None:
        return int(row["reported_deaths"])
    return int(row["headline_deaths"])


def estimate_monthly_deaths(final_months, headline_months):
    """Build one national monthly series.

    final_months: mappings with month and deaths (official incident counts).
    headline_months: mappings with month and headline_deaths. Optional
    headline_basis, reported_deaths, and predicted_deaths keep the monthly
    change inside one CDC series. A lag is used only when the previous
    headline row is the previous calendar month.

    Final months are never replaced by an estimate. A negative estimate is
    kept and marked; it is a revision artifact, not a death count.
    """
    final = {}
    for row in final_months:
        if row.get("deaths") is None:
            continue
        final[month_start(row["month"])] = int(row["deaths"])

    headline = []
    for row in headline_months:
        if row.get("headline_deaths") is None:
            continue
        headline.append(row)
    headline.sort(key=lambda row: month_start(row["month"]))

    lag = {}
    for index, row in enumerate(headline):
        if index == 0:
            continue
        month = month_start(row["month"])
        previous = headline[index - 1]
        if month_start(previous["month"]) == add_months(month, -1):
            basis = row.get("headline_basis")
            lag[month] = _series_value(row, basis) - _series_value(previous, basis)

    series = {
        month: {
            "month": month,
            "estimated_deaths": deaths,
            "how_produced": OFFICIAL,
            "change_in_12_month_total": lag.get(month),
            "is_negative_estimate": False,
        }
        for month, deaths in final.items()
    }

    # Each new month needs the count from 12 months earlier, which may itself
    # be an estimate once the series moves more than a year past final data.
    pending = True
    while pending:
        pending = False
        for month, change in lag.items():
            if month in series:
                continue
            anchor = series.get(add_months(month, -12))
            if anchor is None:
                continue
            estimated = change + anchor["estimated_deaths"]
            series[month] = {
                "month": month,
                "estimated_deaths": estimated,
                "how_produced": ESTIMATED,
                "change_in_12_month_total": change,
                "is_negative_estimate": estimated < 0,
            }
            pending = True

    return [series[month] for month in sorted(series)]
