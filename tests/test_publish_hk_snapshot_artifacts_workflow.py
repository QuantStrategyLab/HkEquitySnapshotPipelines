from pathlib import Path
import re


WORKFLOW_PATH = Path(".github/workflows/publish-hk-snapshot-artifacts.yml")
FULL_SHA_ACTION = re.compile(r"uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+v\d+)?$")


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


def test_publish_workflow_scopes_github_broker_secrets_to_generation_step():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    job_env = workflow[workflow.index("    env:\n") : workflow.index("    steps:\n")]
    generation_step = workflow[
        workflow.index("      - name: Resolve or generate factor snapshot CSV") :
        workflow.index("      - name: Build and validate HK snapshot artifacts")
    ]

    assert "secrets." not in job_env
    assert "LONG_BRIDGE_APP_KEY_FROM_GITHUB_SECRET" in generation_step
    assert "LONG_BRIDGE_APP_SECRET_FROM_GITHUB_SECRET" in generation_step
    assert "LONG_BRIDGE_ACCESS_TOKEN_FROM_GITHUB_SECRET" in generation_step
    assert "inputs.input_source_mode == 'longbridge_openapi_staging'" in generation_step
    assert "inputs.longbridge_credentials_mode == 'github_secrets'" in generation_step


def test_publish_workflow_remote_actions_are_pinned_to_full_commit_shas():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    action_lines = [line.strip() for line in workflow.splitlines() if "uses:" in line]

    assert action_lines
    assert all(FULL_SHA_ACTION.fullmatch(line) for line in action_lines)
