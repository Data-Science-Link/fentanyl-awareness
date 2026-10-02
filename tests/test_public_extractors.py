import pandas as pd

from data_engineering.data_sources.announcements.announcements_extractor import (
    combine,
    mentions_fentanyl,
    parse_rss,
)
from data_engineering.data_sources.cbp.cbp_extractor import aggregate_fentanyl, newest_dataset_url
from data_engineering.data_sources.faces.faces_extractor import public_records
from data_engineering.data_sources.nvss_wonder.wonder_demographics import (
    choose_group,
    group_options,
    parse_grouped_export,
)


def test_cbp_keeps_fentanyl_and_rolls_up_field_offices():
    html = '''
    <a href="/sites/default/files/2026-09/nationwide-drugs-fy23-fy26-aug.csv">August</a>
    <a href="/sites/default/files/2026-08/nationwide-drugs-fy23-fy26-jul.csv">July</a>
    '''
    assert newest_dataset_url(html).endswith("nationwide-drugs-fy23-fy26-aug.csv")
    frame = pd.DataFrame(
        [
            {
                "FY": "2024",
                "Component": "Office of Field Operations",
                "Region": "Southwest Border",
                "Land Filter": "Land Only",
                "Area of Responsibility": "SAN DIEGO FIELD OFFICE",
                "Drug Type": "Fentanyl",
                "Count of Event": 2,
                "Sum Qty (lbs)": 10.5,
            },
            {
                "FY": "2024",
                "Component": "Office of Field Operations",
                "Region": "Southwest Border",
                "Land Filter": "Land Only",
                "Area of Responsibility": "TUCSON FIELD OFFICE",
                "Drug Type": "Fentanyl",
                "Count of Event": 1,
                "Sum Qty (lbs)": 1.25,
            },
            {
                "FY": "2024",
                "Component": "Office of Field Operations",
                "Region": "Southwest Border",
                "Land Filter": "Land Only",
                "Area of Responsibility": "SAN DIEGO FIELD OFFICE",
                "Drug Type": "Cocaine",
                "Count of Event": 9,
                "Sum Qty (lbs)": 100,
            },
        ]
    )
    out = aggregate_fentanyl(frame, "https://www.cbp.gov/document/stats/nationwide-drug-seizures", "file.csv", "2026-10-01")
    assert list(out.columns) == [
        "fiscal_year",
        "component",
        "region",
        "pounds",
        "seizure_events",
        "source_url",
        "source_file",
        "extracted_at",
    ]
    assert len(out) == 1
    assert out.iloc[0]["pounds"] == 11.75
    assert out.iloc[0]["seizure_events"] == 3
    assert "SAN DIEGO" not in out.to_csv(index=False)


def test_faces_listing_skips_blank_photos_and_builds_dea_image_url():
    frame = public_records(
        [
            {"id": "2", "name": "Ada", "age": "30", "state": "Ohio", "age_desc": None, "image": "2024-01/a.jpg"},
            {"id": "1", "name": " ", "age": "4", "state": "Texas", "image": "2024-01/b.jpg"},
            {"id": "3", "name": "DATA NEEDED", "age": "1", "state": "", "image": "2024-01/c.jpg"},
            {"id": "4", "name": "Bo", "age": "0", "state": "", "image": ""},
        ],
        "2026-10-01",
    )
    assert list(frame["first_name"]) == ["Ada"]
    assert frame.iloc[0]["image_url"] == "https://fof.dea.gov/sites/default/files/2024-01/a.jpg"
    assert frame.iloc[0]["exhibit_url"] == "https://fof.dea.gov/exhibit"


def test_announcements_keep_fentanyl_items_and_prior_publishers():
    assert mentions_fentanyl("CDC update", "synthetic opioid deaths")
    assert not mentions_fentanyl("Flu season", "influenza")
    rss = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Fentanyl deaths decline</title>
        <link>https://www.cdc.gov/example</link>
        <pubDate>Wed, 01 Oct 2025 12:00:00 GMT</pubDate>
        <description>provisional</description>
      </item>
      <item>
        <title>Flu update</title>
        <link>https://www.cdc.gov/flu</link>
        <pubDate>Wed, 01 Oct 2025 12:00:00 GMT</pubDate>
        <description>influenza</description>
      </item>
    </channel></rss>
    """
    fetched = parse_rss(rss, "Centers for Disease Control and Prevention", "2026-10-01")
    assert len(fetched) == 1
    previous = pd.DataFrame(
        [
            {
                "published": "2024-01-01",
                "title": "Older DEA note",
                "publisher": "Drug Enforcement Administration",
                "url": "https://www.dea.gov/example",
                "extracted_at": "2024-01-01",
            }
        ]
    )
    combined = combine(fetched, previous, "2026-10-01")
    publishers = set(combined["publisher"])
    assert "Drug Enforcement Administration" in publishers
    assert "Centers for Disease Control and Prevention" in publishers
    assert combined["url"].tolist().count("https://www.cdc.gov/example") == 1


def test_wonder_group_choice_and_export():
    html = """
    <select name="B_1">
      <option value="D157.V1-level1">Year</option>
      <option value="D157.V5">Ten-Year Age Groups</option>
      <option value="D157.V8">Hispanic Origin and Race</option>
    </select>
    """
    options = group_options(html)
    assert choose_group(options, "age") == "D157.V5"
    assert choose_group(options, "race") == "D157.V8"
    text = '''"Notes","Ten-Year Age Groups","Ten-Year Age Groups Code",Deaths,Population,Crude Rate
,"25-34 years","25-34",100,1,1
"Total",,,100,1,1
"---"
'''
    frame = parse_grouped_export(text, 2024, "2026-10-01")
    assert frame.iloc[0]["group"] == "25-34 years"
    assert int(frame.iloc[0]["deaths"]) == 100
