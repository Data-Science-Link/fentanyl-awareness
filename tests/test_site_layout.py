"""The public site is five story pages with a shared reading order and a source on each visual."""

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
PAGES = {
    "index.html": "home",
    "trend.html": "trend",
    "who.html": "who",
    "actions.html": "actions",
    "download.html": "download",
}
NAV = list(PAGES)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.current = []
        self.body = {}
        self.canvas_labels = []
        self.skip = False
        self.main = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "body":
            self.body = values
        if tag == "a":
            if "href" in values:
                self.hrefs.append(values["href"])
            if values.get("aria-current") == "page":
                self.current.append(values.get("href"))
            if values.get("href") == "#content" and "skip" in values.get("class", ""):
                self.skip = True
        if tag == "main" and values.get("id") == "content":
            self.main = True
        if tag == "canvas":
            self.canvas_labels.append(values.get("aria-label", ""))
        if tag == "div" and values.get("aria-current") == "page":
            self.current.append("path")


def read_page(name):
    parser = Page()
    parser.feed((SITE / name).read_text())
    return parser


def test_each_page_has_the_same_reading_order():
    for name, page_id in PAGES.items():
        page = read_page(name)
        assert page.body.get("data-page") == page_id
        assert page.skip
        assert page.main
        assert "status" in page.ids or name == "download.html"
        for href in NAV:
            assert href in page.hrefs
        assert page.current == [name] or (name == "index.html" and "index.html" in page.current)
        assert "design.html" not in page.hrefs


def test_visuals_name_a_source_and_charts_are_labeled():
    home = read_page("index.html")
    home_text = (SITE / "index.html").read_text()
    assert "monthly-chart" in home.ids
    assert "monthly-chart-data" in home.ids
    assert "deaths_by_month.csv" in home.hrefs
    assert "comparison-chart" not in home.ids
    assert "getting better or worse" in home_text
    assert "Fentanyl Awareness" in home_text
    assert "What fentanyl is" in home_text
    assert "Deaths by state" in home_text
    assert "Get the data" in home_text
    assert "Tap a month to see the count." in home_text
    for name in PAGES:
        page_text = (SITE / name).read_text()
        assert "Fentanyl Awareness" in page_text
        assert ">Fentanyl deaths<" not in page_text
    assert all(home.canvas_labels)

    trend = read_page("trend.html")
    assert {"state-map", "state-table", "state-answer", "map-readout"} <= trend.ids
    assert "monthly-chart" not in trend.ids
    assert "fact_fentanyl_deaths_over_time.csv" in trend.hrefs
    assert "Tap a state to see both 12-month totals." in (SITE / "trend.html").read_text()

    who = read_page("who.html")
    for element_id in ("people", "age-chart", "race-chart", "share-meter", "seizure-chart", "region-table"):
        assert element_id in who.ids
    assert "budget-chart" not in who.ids
    assert "region-chart" not in who.ids
    for href in ("faces_of_fentanyl.csv", "wonder_age.csv", "wonder_race.csv", "census_race_2024.csv", "wonder_drug_share.csv", "cbp_fentanyl_seizures.csv", "sources/supply_context.md"):
        assert href in who.hrefs
    assert "agency_budgets.csv" in (SITE / "download.html").read_text()
    assert all(who.canvas_labels)

    actions = read_page("actions.html")
    assert {"policy-chart", "action-table"} <= actions.ids
    assert "policy_actions.csv" in actions.hrefs

    news = read_page("news.html")
    assert "news-list" in news.ids
    assert "official_announcements.csv" in news.hrefs
    assert "actions.html" in news.hrefs


def test_download_keeps_the_plain_language_dictionary():
    text = (SITE / "download.html").read_text()
    for column in (
        "Estimated deaths",
        "How this number was produced",
        "Deaths per 100,000",
        "Change from the previous month",
        "Change from the same month a year earlier",
        "Change in the 12-month total",
        "Official actions that month",
    ):
        assert column in text
    for column in (
        "Deaths in the month",
        "Confidence",
        "Preliminary 12-month total",
        "month, state, and year",
    ):
        assert column in text
    assert "deaths_by_month.csv" in text
    assert "deaths_by_state_month.csv" in text
    assert "methods/monthly_deaths.md" in text
    assert "github.com/Data-Science-Link/fentanyl-awareness" in text
    assert "data-preview" in text
    assert "month, state, and year" in text


def test_layout_note_names_the_practice_and_the_five_pages():
    note = (ROOT / "docs/design/public-site-layout.md").read_text()
    page = (SITE / "design.html").read_text()
    for phrase in (
        "Our World in Data",
        "Office for National Statistics",
        "Marshall Project",
        "Periscopic",
        "Five pages",
        "deaths_by_month.csv",
    ):
        assert phrase in note
        assert phrase in page
    brief = (ROOT / "docs/Fentanyl_Project_Overview_and_Initial_Design.md").read_text()
    assert "design/public-site-layout.md" in brief


def test_motion_and_photos_stay_restrained():
    script = (SITE / "app.js").read_text()
    style = (SITE / "styles.css").read_text()
    assert "prefers-reduced-motion" in script
    assert "prefers-reduced-motion" in style
    assert "escapeHtml" in script
    assert "spanGaps: false" in script
    assert "below zero" in script
    assert "autoplay" not in script
    assert "Hide photos" in (SITE / "who.html").read_text()
    assert "menu-button" in style
    assert ":focus-visible" in style
    assert "showVizTip" in script
    assert "viz-tip" in style
    assert "Tap a month to see the count." in (SITE / "index.html").read_text()
    assert "Tap a month or a policy line to see the count." in (SITE / "actions.html").read_text()
    assert "Tap a state to see both 12-month totals." in (SITE / "trend.html").read_text()
    assert "Tap a bar to see the figure." in (SITE / "who.html").read_text()
    assert "map-readout" in (SITE / "trend.html").read_text()
    for name in PAGES:
        assert "design.html" not in (SITE / name).read_text()
        assert "How this site is laid out" not in (SITE / name).read_text()
