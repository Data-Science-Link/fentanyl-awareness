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


def test_dbt_ci_does_not_publish_the_portal():
    dbt = (ROOT / ".github/workflows/dbt-ci.yml").read_text()
    security = (ROOT / ".github/workflows/security-audit.yml").read_text()
    assert "peaceiris/actions-gh-pages" not in dbt
    assert "actions/deploy-pages" not in dbt
    assert "automated/weekly-data-refresh" not in dbt
    assert "automated/weekly-data-refresh" not in security
