from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "monthly_snapshot_audit.yml"


def test_monthly_snapshot_audit_workflow_dispatches_codex_bridge():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "actions: write" in workflow
    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/create-github-app-token@v3" in workflow
    assert "write_monthly_snapshot_audit_issue.py" in workflow
    assert "monthly_snapshot_audit_issue.json" in workflow
    assert "QuantStrategyLab/CodexAuditBridge" in workflow
    assert "selfhosted_monthly_review.yml" in workflow
    assert "/actions/workflows/selfhosted_monthly_review.yml/dispatches" in workflow
    assert '"task": "monthly_snapshot_audit"' in workflow
    assert "CODEX_AUDIT_DISPATCH_TOKEN" in workflow
    assert "SELFHOSTED_CODEX_REVIEW_PROVIDER || 'auto'" in workflow
    assert "SELFHOSTED_CODEX_REVIEW_MODE || 'review_and_fix'" in workflow


def test_monthly_snapshot_audit_workflow_stays_source_safe():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "google-github-actions/auth" not in workflow
    assert "GCP_SERVICE_ACCOUNT_KEY" not in workflow
    assert "GCS_BUCKET" not in workflow
    assert "OPENAI_API_KEY" not in workflow
    assert "ANTHROPIC_API_KEY" not in workflow
    assert "gh issue create" not in workflow
    assert "gh workflow run" not in workflow
