from data_engineering.data_sources.nvss_wonder.wonder_extractor import (
    parse_wonder_export,
    parse_wonder_form,
    read_year_options,
    run_tabulation,
    source_dataset_for_year,
)


ABOUT_HTML = """
<form id="wonderform" action="/controller/datarequest/D77">
  <input type="hidden" name="stage" value="about">
  <input type="submit" name="action-I Agree" value="I Agree">
</form>
"""

REQUEST_HTML = """
<form id="wonderform" action="/controller/datarequest/D77">
  <input type="hidden" name="stage" value="request">
  <select name="B_1"><option value="D77.V10-level1" selected>Region</option></select>
  <select name="B_2"><option value="*None*" selected>*None*</option></select>
  <select name="B_3"><option value="*None*" selected>*None*</option></select>
  <select name="B_4"><option value="*None*" selected>*None*</option></select>
  <select name="B_5"><option value="*None*" selected>*None*</option></select>
  <select name="F_D77.V1" multiple>
    <option value="*All*" selected>*All*</option>
    <option value="2016">2016</option>
    <option value="2017">2017</option>
  </select>
  <input type="hidden" name="O_V2_fmode" value="freg">
  <input type="hidden" name="O_V13_fmode" value="fadv">
  <textarea name="V_D77.V2"></textarea>
  <textarea name="V_D77.V13"></textarea>
  <textarea name="V_D77.V13_AND"></textarea>
  <input type="checkbox" name="O_show_totals" value="true" checked>
  <input type="text" name="O_title" value="">
  <input type="submit" name="action-Send" value="Send">
</form>
"""

RESULTS_HTML = """
<form id="wonderform" action="/controller/datarequest/D77">
  <input type="hidden" name="stage" value="results">
  <input type="hidden" name="saved_id" value="abc">
  <select name="O_export-format">
    <option value="xls" selected>xls</option>
    <option value="csv">csv</option>
  </select>
  <input type="submit" name="action-Export" value="Download">
</form>
"""

EXPORT_CSV = """\
"Notes","State","State Code","Year","Year Code",Deaths,Population,Crude Rate
,"Alabama","01","2017","2017",12,1,1.0
"Total","Alabama","01",,,12,1,1.0
,"Wyoming","56","2017","2017",Suppressed,Not Applicable,Not Applicable
,"Delaware","10","2017","2017",4,1,1.0
"Total",,,,,100,1,1.0
"---"
"Dataset: Multiple Cause of Death, 1999-2020"
"""

MONTH_CSV = """\
"Notes","Month","Month Code",Deaths,Population,Crude Rate
,"Jan., 2017","2017/01",730,Not Applicable,Not Applicable
,"Feb., 2017","2017/02",Suppressed,Not Applicable,Not Applicable
"---"
"Dataset: Multiple Cause of Death, 1999-2020"
"""


class _Response:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


class _Session:
    def __init__(self):
        self.posts = []

    def post(self, url, data=None, timeout=None):
        self.posts.append((url, list(data)))
        if any(name == "action-Send" for name, _value in data):
            return _Response(RESULTS_HTML)
        return _Response(EXPORT_CSV)


def test_source_dataset_splits_at_2018():
    assert source_dataset_for_year(2017) == "D77"
    assert source_dataset_for_year(2018) == "D157"


def test_form_parser_reads_the_request_form_and_year_list():
    action, fields = parse_wonder_form(REQUEST_HTML)
    assert action.endswith("/D77")
    assert ("B_1", "D77.V10-level1") in [(name, value) for name, value in fields]
    assert read_year_options(REQUEST_HTML, "D77") == [2016, 2017]
    about_action, about_fields = parse_wonder_form(ABOUT_HTML)
    assert about_action.endswith("/D77")
    assert about_fields == [["stage", "about"]]


def test_tabulation_requests_state_and_t40_4_not_county():
    session = _Session()
    _action, fields = parse_wonder_form(REQUEST_HTML)
    text = run_tabulation(
        session,
        "https://wonder.cdc.gov/controller/datarequest/D77",
        fields,
        "D77",
        "state-year",
        [2017],
    )
    assert "Alabama" in text
    sent = dict_pairs(session.posts[0][1])
    assert sent["B_1"] == ["D77.V9-level1"]
    assert sent["B_2"] == ["D77.V1-level1"]
    assert sent["V_D77.V13"] == ["T40.4"]
    assert "X40" in sent["V_D77.V2"][0] and "Y14" in sent["V_D77.V2"][0]
    assert sent["F_D77.V1"] == ["2017"]
    assert sent["O_V2_fmode"] == ["fadv"]
    assert "O_show_totals" not in sent
    assert not any("V9-level2" in value for values in sent.values() for value in values)
    exported = dict_pairs(session.posts[1][1])
    assert exported["O_export-format"] == ["csv"]
    assert exported["action-Export"] == ["Download"]


def test_export_parser_suppresses_small_cells_and_keeps_months_separate():
    annual = parse_wonder_export(EXPORT_CSV, "D77", "2026-09-26T00:00:00Z")
    alabama = annual[annual["state"] == "Alabama"].iloc[0]
    wyoming = annual[annual["state"] == "Wyoming"].iloc[0]
    delaware = annual[annual["state"] == "Delaware"].iloc[0]
    assert int(alabama["incident_deaths"]) == 12
    assert alabama["is_suppressed"] == False  # noqa: E712
    assert alabama["period_type"] == "year"
    assert alabama["month"] == ""
    assert alabama["source_dataset"] == "D77"
    assert pd_isna(wyoming["incident_deaths"]) and wyoming["is_suppressed"] == True  # noqa: E712
    assert pd_isna(delaware["incident_deaths"]) and delaware["is_suppressed"] == True  # noqa: E712
    assert "United States" not in set(annual["state"])

    monthly = parse_wonder_export(MONTH_CSV, "D157", "2026-09-26T00:00:00Z")
    january = monthly[monthly["month"] == "2017-01-01"].iloc[0]
    february = monthly[monthly["month"] == "2017-02-01"].iloc[0]
    assert january["state"] == "United States"
    assert january["geo_type"] == "nation"
    assert int(january["incident_deaths"]) == 730
    assert january["period_type"] == "month"
    assert january["source_dataset"] == "D157"
    assert pd_isna(february["incident_deaths"]) and february["is_suppressed"] == True  # noqa: E712
    assert int(january["incident_deaths"]) != 12


def dict_pairs(pairs):
    grouped = {}
    for name, value in pairs:
        grouped.setdefault(name, []).append(value)
    return grouped


def pd_isna(value):
    return value is None or (isinstance(value, float) and value != value)
