from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines import publish
from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_snapshot_pipelines.low_vol_dividend_quality import build_and_write_snapshot

PROFILE = "hk_low_vol_dividend_quality_snapshot"
PREFIX = "gs://test-only/hk_low_vol_dividend_quality_snapshot_staging"
SAMPLE = Path(__file__).resolve().parents[1] / "examples/low_vol_dividend_quality/factor_snapshot.sample.csv"


def _pack(tmp_path: Path, *, age_days: int = 0) -> dict[str, Path]:
    # Synthetic test data exercises transfer boundaries, not source attestation.
    snapshot = pd.read_csv(SAMPLE)
    as_of = datetime.now(timezone.utc).date() - timedelta(days=age_days)
    snapshot["as_of"] = as_of.isoformat()
    snapshot["snapshot_date"] = as_of.isoformat()
    source = tmp_path / "synthetic-input.csv"
    snapshot.to_csv(source, index=False)
    build_and_write_snapshot(factor_snapshot_path=source, output_dir=tmp_path)
    return get_profile_contract(PROFILE).artifact_paths(tmp_path)


def _execute(tmp_path: Path) -> int:
    return publish.main([
        "--profile", PROFILE, "--artifact-dir", str(tmp_path),
        "--gcs-prefix", PREFIX, "--execute",
    ])


@pytest.mark.parametrize("invalid_case", [
    "stale", "future", "digest", "date_rewrite", "missing_last_file",
    "research_summary", "research_snapshot",
])
def test_execute_rejects_invalid_pack_before_any_gcs_write(tmp_path, monkeypatch, invalid_case):
    paths = _pack(tmp_path, age_days=45 if invalid_case in {"stale", "date_rewrite"} else 0)
    if invalid_case in {"future", "digest", "date_rewrite"}:
        manifest = json.loads(paths["manifest"].read_text())
        if invalid_case == "digest":
            paths["snapshot"].write_text(paths["snapshot"].read_text() + "\n")
        else:
            offset = 1 if invalid_case == "future" else 0
            manifest["snapshot_as_of"] = (
                datetime.now(timezone.utc).date() + timedelta(days=offset)
            ).isoformat()
        paths["manifest"].write_text(json.dumps(manifest))
    elif invalid_case == "missing_last_file":
        paths["release_summary"].unlink()
    elif invalid_case == "research_summary":
        (tmp_path / publish.SOURCE_INPUT_SUMMARY_FILENAME).write_text(json.dumps({
            "source_name": "public_yfinance_staging", "allow_research_defaults": True,
            "artifact_evidence_role": "research_smoke_input",
        }))
    elif invalid_case == "research_snapshot":
        snapshot = pd.read_csv(paths["snapshot"])
        snapshot["source_quality"] = "public_yfinance_generated_with_research_defaults"
        source = tmp_path / "research-input.csv"
        snapshot.to_csv(source, index=False)
        build_and_write_snapshot(factor_snapshot_path=source, output_dir=tmp_path)
    transfers = []
    monkeypatch.setattr(publish.subprocess, "run", lambda command, **_: transfers.append(command))

    assert _execute(tmp_path) == 1
    assert transfers == []


def test_execute_accepts_fresh_pack_at_existing_40_day_boundary(tmp_path, monkeypatch):
    _pack(tmp_path, age_days=40)
    transfers = []
    monkeypatch.setattr(publish.subprocess, "run", lambda command, **_: transfers.append(command))

    assert _execute(tmp_path) == 0
    assert len(transfers) == 4
    assert all(command[:3] == ["gcloud", "storage", "cp"] for command in transfers)


def test_dry_run_still_allows_research_packaging_without_writes(tmp_path, monkeypatch):
    _pack(tmp_path, age_days=45)
    monkeypatch.setattr(publish.subprocess, "run", lambda *_args, **_kwargs: pytest.fail("dry run wrote to GCS"))

    assert publish.main([
        "--profile", PROFILE, "--artifact-dir", str(tmp_path), "--gcs-prefix", PREFIX,
    ]) == 0


def test_preflight_report_validates_local_bytes_without_remote_reads_or_writes(tmp_path, monkeypatch):
    paths = _pack(tmp_path, age_days=45)
    report_path = tmp_path / "publish_preflight.json"
    monkeypatch.setattr(publish.subprocess, "run", lambda *_args, **_kwargs: pytest.fail("preflight contacted GCS"))

    assert publish.main([
        "--profile", PROFILE, "--artifact-dir", str(tmp_path), "--gcs-prefix", PREFIX,
        "--preflight-report", str(report_path),
    ]) == 1
    report = json.loads(report_path.read_text())
    assert report["status"] == "failed"
    assert report["published_snapshot_health"]["age_days"] == 45
    assert report["artifact_pack_validation"]["snapshot_sha256"]
    assert report["snapshot_source"] == str(paths["snapshot"])
    assert "does not attest source lineage" in report["boundary"]


@pytest.mark.parametrize("execute,defaults,prefix,success", [
    ("false", "false", "", True),
    ("false", "true", "", True),
    ("true", "false", PREFIX, True),
    ("true", "true", PREFIX, False),
    ("true", "false", "", False),
    ("true", "false", "/tmp/local-output", False),
])
def test_workflow_publish_mode_rejects_research_or_missing_cloud_target(execute, defaults, prefix, success):
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/publish-hk-snapshot-artifacts.yml").read_text()
    step = re.search(r"      - name: Validate publish mode\n        run: \|\n(.*?)(?=\n      - name:)", workflow, re.S)
    assert step is not None
    script = "\n".join(line[10:] for line in step.group(1).splitlines())
    result = subprocess.run([
        "bash", "-c", script,
    ], env={**os.environ, "EXECUTE_PUBLISH": execute, "ALLOW_RESEARCH_DEFAULTS": defaults, "GCS_PREFIX": prefix},
        capture_output=True, text=True, check=False)

    assert (result.returncode == 0) is success
