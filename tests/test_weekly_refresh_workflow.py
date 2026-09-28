from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_weekly_refresh_survives_actions_pr_permission_block():
    text = (ROOT / ".github/workflows/weekly-data-refresh.yml").read_text()
    assert "WEEKLY_REFRESH_TOKEN" in text
    assert "not permitted to create or approve pull requests" in text
    assert "Allow GitHub Actions to create and approve pull requests" in text
    assert "git push origin main --force" not in text


def test_required_checks_run_on_weekly_refresh_branch():
    dbt = (ROOT / ".github/workflows/dbt-ci.yml").read_text()
    security = (ROOT / ".github/workflows/security-audit.yml").read_text()
    assert "automated/weekly-data-refresh" in dbt
    assert "automated/weekly-data-refresh" in security
