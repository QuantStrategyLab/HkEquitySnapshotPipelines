from __future__ import annotations

from pathlib import Path
import re


WORKFLOW_PATH = Path(".github/workflows/hk-snapshot-artifact-health.yml")
FULL_SHA_ACTION = re.compile(r"uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+v\d+)?$")


def test_hk_snapshot_artifact_health_workflow_is_read_only_and_scheduled():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "id-token: write" in workflow
    assert "google-github-actions/auth@" in workflow
    assert "published_snapshot_health" in workflow
    assert "gcloud storage cp" not in workflow
    assert "publish-hk-snapshot-artifacts" not in workflow
    assert "no source generation, publication, deployment, or order submission" in workflow
    assert "Keep the profile parked" in workflow


def test_hk_snapshot_artifact_health_workflow_pins_remote_actions():
    action_lines = [
        line.strip()
        for line in WORKFLOW_PATH.read_text(encoding="utf-8").splitlines()
        if "uses:" in line
    ]

    assert action_lines
    assert all(FULL_SHA_ACTION.fullmatch(line) for line in action_lines)
