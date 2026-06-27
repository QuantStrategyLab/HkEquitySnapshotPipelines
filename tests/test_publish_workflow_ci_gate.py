"""Workflow config tests for publish CI gating."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_WORKFLOW = ROOT / ".github/workflows/publish-hk-snapshot-artifacts.yml"
VERIFY_SCRIPT = ROOT / ".github/scripts/verify_main_ci_success.sh"


def test_publish_hk_snapshot_artifacts_requires_main_ci_before_live_publish() -> None:
    workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

    assert "actions: read" in workflow
    assert "Verify main CI succeeded before publish" in workflow
    assert "bash .github/scripts/verify_main_ci_success.sh" in workflow
    assert "inputs.execute_publish == true" in workflow


def test_verify_main_ci_success_script_checks_latest_main_run() -> None:
    script = VERIFY_SCRIPT.read_text(encoding="utf-8")

    assert 'workflow="${CI_WORKFLOW:-ci.yml}"' in script
    assert 'branch="${VERIFY_BRANCH:-main}"' in script
    assert "gh run list" in script
    assert 'conclusion}" != "success"' in script
