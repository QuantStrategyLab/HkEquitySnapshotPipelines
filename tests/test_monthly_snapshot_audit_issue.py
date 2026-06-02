from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from hk_equity_snapshot_pipelines.monthly_snapshot_audit_issue import (
    MONTHLY_SNAPSHOT_AUDIT_TASK,
    build_monthly_snapshot_audit_issue,
    normalize_as_of_month,
    write_monthly_snapshot_audit_issue,
)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_monthly_snapshot_audit_issue.py"


def test_build_monthly_snapshot_audit_issue_scopes_codex_review():
    payload = build_monthly_snapshot_audit_issue(as_of_month="2026-06", source_ref="main")
    body = payload["issue_body"]

    assert payload["issue_title"] == "HK Snapshot Monthly Audit: 2026-06"
    assert payload["codex_task"] == MONTHLY_SNAPSHOT_AUDIT_TASK
    assert "QuantStrategyLab/HkEquitySnapshotPipelines" in body
    assert "CodexAuditBridge" in body
    assert "monthly_snapshot_audit" in body
    assert "hk_low_vol_dividend_quality" in body
    assert "hk_shareholder_yield_quality" in body
    assert "hk_free_cash_flow_quality" in body
    assert "max drawdown <= 30%" in body
    assert "at least 3 independent OOS folds" in body
    assert "LongBridge and IBKR" in body
    assert "bilingual notification evidence" in body
    assert "research-only / deprioritized" in body
    assert "no publish, no deployment, no broker orders" not in body.lower()
    assert "deploy Cloud Run, or place broker orders" in body
    assert "hkeq-validate-live-enable-evidence" in body


def test_write_monthly_snapshot_audit_issue_outputs_bundle(tmp_path):
    payload = write_monthly_snapshot_audit_issue(output_dir=tmp_path, as_of_month="2026-06", source_ref="feature/hk")

    body_path = Path(payload["issue_body_path"])
    summary_path = Path(payload["job_summary_path"])
    metadata_path = Path(payload["metadata_path"])

    assert body_path.exists()
    assert summary_path.exists()
    assert metadata_path.exists()
    assert "HK Snapshot Monthly Audit: 2026-06" in body_path.read_text(encoding="utf-8")
    assert "no publish, no deployment, no broker orders" in summary_path.read_text(encoding="utf-8")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["artifact_name"] == "hk-snapshot-monthly-audit-2026-06"
    assert metadata["source_ref"] == "feature/hk"
    assert metadata["profiles_in_scope"] == ["hk_low_vol_dividend_quality"]
    assert "hk_shareholder_yield_quality" in metadata["excluded_from_scope"]
    assert "hk_free_cash_flow_quality" in metadata["excluded_from_scope"]
    assert "issue_body" not in metadata


def test_monthly_snapshot_audit_issue_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--as-of-month",
            "2026-06",
            "--output-dir",
            str(tmp_path),
            "--source-ref",
            "main",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["issue_title"] == "HK Snapshot Monthly Audit: 2026-06"
    assert Path(payload["issue_body_path"]).exists()
    assert Path(payload["metadata_path"]).exists()


def test_normalize_as_of_month_rejects_invalid_values():
    assert normalize_as_of_month("2026-06") == "2026-06"
    with pytest.raises(ValueError, match="YYYY-MM"):
        normalize_as_of_month("2026-06-01")
    with pytest.raises(ValueError, match="invalid month"):
        normalize_as_of_month("2026-13")
