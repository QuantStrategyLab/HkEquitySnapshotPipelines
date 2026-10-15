from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "monthly_snapshot_audit.yml"


def test_monthly_snapshot_audit_workflow_keeps_issue_creation_without_bridge_dispatch():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "actions: write" not in workflow
    assert "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6" in workflow
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6" in workflow
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7" in workflow
    assert "write_monthly_snapshot_audit_issue.py" in workflow
    assert "monthly_snapshot_audit_issue.json" in workflow
    assert "Reused issue" in workflow
    assert "existing_issues = request_json" in workflow
    for retired in (
        "AIAuditBridge",
        "CODEX_AUDIT_",
        "codex_audit.yml",
        "create-github-app-token",
        "Trigger Monthly Snapshot Review Automation",
        "--codex-audit-repository",
    ):
        assert retired not in workflow


def test_monthly_snapshot_audit_workflow_stays_source_safe():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "google-github-actions/auth" not in workflow
    assert "GCP_SERVICE_ACCOUNT_KEY" not in workflow
    assert "GCS_BUCKET" not in workflow
    assert "OPENAI_API_KEY" not in workflow
    assert "ANTHROPIC_API_KEY" not in workflow
    assert "gh issue create" not in workflow
    assert "gh workflow run" not in workflow
