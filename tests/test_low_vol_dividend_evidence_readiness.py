from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_evidence_readiness import (
    READINESS_VERSION,
    build_low_vol_dividend_live_enablement_readiness_report,
    write_low_vol_dividend_live_enablement_readiness_report,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "print_low_vol_dividend_live_enablement_readiness.py"


def test_readiness_report_lists_missing_convention_files(tmp_path):
    payload = build_low_vol_dividend_live_enablement_readiness_report(
        evidence_dir=tmp_path / "evidence",
        output_dir=tmp_path / "out",
        gate_output_dir=tmp_path / "gate",
    )

    assert payload["readiness_version"] == READINESS_VERSION
    assert payload["status"] == "blocked"
    assert payload["live_enablement_allowed"] is False
    assert payload["ready_to_request_live_enable"] is False
    assert payload["missing_required_files_count"] == 15
    assert payload["provided_required_files_count"] == 0
    missing = [item for item in payload["required_files"] if item["status"] == "missing"]
    assert len(missing) == 15
    assert any(item["section"] == "artifact_pack_validation" for item in missing)
    assert {item["platform"] for item in payload["platform_readiness"]} == {"ibkr", "longbridge"}
    assert all(item["live_enablement_allowed"] is False for item in payload["platform_readiness"])


def test_readiness_report_counts_present_files_without_treating_them_as_passed(tmp_path):
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "artifact_pack_validation.draft.json").write_text(
        json.dumps({"validation_status": "pending"}),
        encoding="utf-8",
    )

    payload = build_low_vol_dividend_live_enablement_readiness_report(
        evidence_dir=evidence_dir,
        output_dir=tmp_path / "out",
        gate_output_dir=tmp_path / "gate",
        platforms=("longbridge",),
    )

    assert payload["provided_required_files_count"] == 1
    assert payload["missing_required_files_count"] == 8
    artifact = next(item for item in payload["required_files"] if item["section"] == "artifact_pack_validation")
    assert artifact["status"] == "present"
    assert payload["live_enablement_allowed"] is False
    assert payload["platform_readiness"][0]["validation_status"] == "failed"


def test_write_readiness_report_outputs_json(tmp_path):
    payload = write_low_vol_dividend_live_enablement_readiness_report(
        evidence_dir=tmp_path / "evidence",
        output_dir=tmp_path / "out",
        gate_output_dir=tmp_path / "gate",
    )

    report_path = Path(payload["report_path"])
    assert report_path.exists()
    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written["readiness_version"] == READINESS_VERSION
    assert written["status"] == "blocked"


def test_readiness_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--output-dir",
            str(tmp_path / "out"),
            "--gate-output-dir",
            str(tmp_path / "gate"),
            "--platform",
            "ibkr",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["platforms"] == ["ibkr"]
    assert payload["missing_required_files_count"] == 9
    assert payload["ready_to_request_live_enable"] is False
    assert Path(payload["report_path"]).exists()
