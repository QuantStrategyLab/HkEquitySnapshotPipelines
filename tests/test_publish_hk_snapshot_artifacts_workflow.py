from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/publish-hk-snapshot-artifacts.yml")


def test_publish_workflow_supports_public_yfinance_staging_source():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "public_yfinance_staging" in workflow
    assert "python -m pip install -e '.[public-data]'" in workflow
    assert "scripts/build_low_vol_dividend_public_factor_snapshot.py" in workflow
    assert "factor_snapshot.public_yfinance_staging.csv" in workflow
    assert "generated CSVs are runtime artifact inputs after validation when allow_research_defaults=false" in workflow


def test_publish_workflow_keeps_longbridge_staging_source_available():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "longbridge_openapi_staging" in workflow
    assert "python -m pip install -e '.[longbridge]'" in workflow
    assert "scripts/build_low_vol_dividend_longbridge_factor_snapshot.py" in workflow
