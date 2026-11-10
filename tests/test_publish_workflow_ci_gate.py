"""Workflow config tests for publish CI gating."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_WORKFLOW = ROOT / ".github/workflows/publish-hk-snapshot-artifacts.yml"
SHARED_CI_CHECK = r"uses: QuantStrategyLab/\.github/actions/verify-main-ci@[0-9a-f]{40}"


def test_publish_hk_snapshot_artifacts_requires_main_ci_before_live_publish() -> None:
    workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

    assert "actions: read" in workflow
    assert "Verify main CI succeeded before publish" in workflow
    assert re.search(SHARED_CI_CHECK, workflow)
    assert "inputs.execute_publish == true" in workflow
