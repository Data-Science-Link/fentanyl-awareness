from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_weekly_job_publishes_pages_without_a_pull_request():
    text = (ROOT / ".github/workflows/weekly-data-refresh.yml").read_text()
    assert "peaceiris/actions-gh-pages" in text
    assert "keep_files: false" in text
    assert "gh pr create" not in text
    assert "WEEKLY_REFRESH_TOKEN" not in text
    assert "automated/weekly-data-refresh" not in text
    assert "git push origin main" not in text


def test_dbt_ci_does_not_publish_the_portal():
    dbt = (ROOT / ".github/workflows/dbt-ci.yml").read_text()
    security = (ROOT / ".github/workflows/security-audit.yml").read_text()
    assert "peaceiris/actions-gh-pages" not in dbt
    assert "automated/weekly-data-refresh" not in dbt
    assert "automated/weekly-data-refresh" not in security


def test_website_html_deploy_keeps_published_csvs():
    text = (ROOT / ".github/workflows/deploy-portal-html.yml").read_text()
    assert "website/**" in text
    assert "keep_files: true" in text
    assert "peaceiris/actions-gh-pages" in text
