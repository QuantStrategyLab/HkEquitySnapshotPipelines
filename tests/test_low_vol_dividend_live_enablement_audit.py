from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.live_enablement_evidence import build_live_enablement_evidence_template
from hk_equity_snapshot_pipelines.low_vol_dividend_live_enablement_audit import (
    AUDIT_VERSION,
    build_low_vol_dividend_live_enablement_audit,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_quality import build_and_write_snapshot


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SOURCE = ROOT / "examples" / "low_vol_dividend_quality" / "factor_snapshot.sample.csv"
SCRIPT = ROOT / "scripts" / "audit_low_vol_dividend_live_enablement.py"


def _write_pending_template(tmp_path: Path, platform: str) -> Path:
    path = tmp_path / f"{platform}_live_enablement_evidence.json"
    path.write_text(
        json.dumps(
            build_live_enablement_evidence_template("hk_low_vol_dividend_quality", platform=platform),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def test_live_enablement_audit_blocks_when_artifact_and_platform_evidence_are_missing():
    payload = build_low_vol_dividend_live_enablement_audit()

    assert payload["audit_version"] == AUDIT_VERSION
    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["status"] == "blocked"
    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert payload["production_deployment_allowed"] is False
    assert payload["gates"] == {
        "artifact_pack_validation": "missing",
        "longbridge_live_enablement_evidence": "missing",
        "ibkr_live_enablement_evidence": "missing",
    }
    assert "artifact_pack_validation_missing" in payload["blockers"]
    assert "longbridge_live_enablement_evidence_missing" in payload["blockers"]
    assert "ibkr_live_enablement_evidence_missing" in payload["blockers"]


def test_live_enablement_audit_accepts_valid_artifact_but_blocks_pending_platform_evidence(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    build_and_write_snapshot(factor_snapshot_path=SAMPLE_SOURCE, output_dir=artifact_dir)
    longbridge_evidence = _write_pending_template(tmp_path, "longbridge")
    ibkr_evidence = _write_pending_template(tmp_path, "ibkr")

    payload = build_low_vol_dividend_live_enablement_audit(
        artifact_dir=artifact_dir,
        longbridge_evidence_file=longbridge_evidence,
        ibkr_evidence_file=ibkr_evidence,
        validation_as_of="2026-06-03",
    )

    assert payload["artifact_pack_validation"]["status"] == "failed"
    assert payload["artifact_pack_validation"]["valid"] is False
    assert payload["artifact_pack_validation"]["min_production_snapshot_row_count"] == 20
    assert payload["artifact_pack_validation"]["snapshot_row_count"] == 6
    assert any("snapshot_row_count below production threshold" in error for error in payload["artifact_pack_validation"]["errors"])
    assert payload["gates"]["longbridge_live_enablement_evidence"] == "failed"
    assert payload["gates"]["ibkr_live_enablement_evidence"] == "failed"
    assert payload["live_enablement_allowed"] is False
    assert payload["platform_live_enablement_evidence"]["longbridge"]["errors_count"] > 0
    assert "production_snapshot_source_audit" in (
        payload["platform_live_enablement_evidence"]["longbridge"]["error_sections"]
    )
    assert any("Fix longbridge evidence sections" in action for action in payload["next_actions"])


def test_live_enablement_audit_cli_json_blocks_missing_evidence(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    build_and_write_snapshot(factor_snapshot_path=SAMPLE_SOURCE, output_dir=artifact_dir)
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--artifact-dir",
            str(artifact_dir),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert completed.returncode == 1
    assert payload["artifact_pack_validation"]["status"] == "failed"
    assert payload["gates"]["longbridge_live_enablement_evidence"] == "missing"
    assert payload["live_enablement_allowed"] is False
