from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_portal_publishes_from_the_action_without_a_pull_request():
    text = (ROOT / ".github/workflows/weekly-data-refresh.yml").read_text()
    assert "actions/deploy-pages" in text
    assert "actions/upload-pages-artifact" in text
    assert "peaceiris/actions-gh-pages" not in text
    assert "gh pr create" not in text
    assert "branches: [main]" in text
    assert "git push origin main" not in text
    assert not (ROOT / ".github/workflows/deploy-portal-html.yml").exists()


def test_pages_artifact_includes_the_plain_csv_memorials_and_site_assets():
    text = (ROOT / ".github/workflows/weekly-data-refresh.yml").read_text()
    assert "cp -r website/. docs/" in text
    assert "Final_Datasets/deaths_by_month.csv" in text
    assert "Final_Datasets/deaths_by_state_month.csv" in text
    assert "Final_Datasets/data_freshness.csv" in text
    assert "data_engineering/data_sources/cdc_api/freshness.py" in text
    assert "Final_Datasets/faces_of_fentanyl.csv" in text
    assert "data_engineering/data_sources/cbp/cbp_extractor.py" in text
    assert "data_engineering/data_sources/faces/faces_extractor.py" in text
    assert "data_engineering/data_sources/announcements/announcements_extractor.py" in text
    assert "data_engineering/data_sources/nvss_wonder/wonder_demographics.py" in text
    assert "rm -rf docs" not in text


def test_dbt_ci_does_not_publish_the_portal():
    dbt = (ROOT / ".github/workflows/dbt-ci.yml").read_text()
    security = (ROOT / ".github/workflows/security-audit.yml").read_text()
    assert "peaceiris/actions-gh-pages" not in dbt
    assert "actions/deploy-pages" not in dbt
    assert "automated/weekly-data-refresh" not in dbt
    assert "automated/weekly-data-refresh" not in security
