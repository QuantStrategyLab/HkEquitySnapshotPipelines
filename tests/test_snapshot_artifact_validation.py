from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_quality import build_and_write_snapshot
from hk_equity_snapshot_pipelines.snapshot_artifact_validation import validate_snapshot_artifact_pack

ROOT = Path(__file__).resolve().parents[1]
FACTOR_SNAPSHOT = ROOT / "examples" / "low_vol_dividend_quality" / "factor_snapshot.sample.csv"


def test_validate_snapshot_artifact_pack_accepts_generated_release(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)

    result = validate_snapshot_artifact_pack("hk_low_vol_dividend_quality_snapshot", tmp_path)

    assert result["valid"] is True
    assert result["validation_status"] == "passed"
    assert result["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert result["snapshot_row_count"] > 0
    assert result["ranking_row_count"] > 0
    assert result["errors"] == []


def test_validate_snapshot_artifact_pack_rejects_manifest_sha_mismatch(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)
    manifest_path = tmp_path / "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["snapshot_sha256"] = "bad-sha"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_snapshot_artifact_pack("hk_low_vol_dividend_quality_snapshot", tmp_path)

    assert result["valid"] is False
    assert result["validation_status"] == "failed"
    assert any("manifest.snapshot_sha256 mismatch" in error for error in result["errors"])


def test_validate_snapshot_artifact_pack_cli_json(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_equity_snapshot_pipelines.snapshot_artifact_validation",
            "--profile",
            "hk_low_vol_dividend_quality_snapshot",
            "--artifact-dir",
            str(tmp_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["valid"] is True
    assert payload["contract_version"] == "hk_low_vol_dividend_quality_snapshot.factor_snapshot.v1"
