from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_evidence_intake import (
    INTAKE_VERSION,
    build_low_vol_dividend_live_enablement_evidence_intake,
    write_low_vol_dividend_live_enablement_evidence_intake,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "intake_low_vol_dividend_live_enablement_evidence.py"


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_evidence_intake_preview_finds_sources_without_copying(tmp_path):
    source_dir = tmp_path / "source"
    evidence_dir = tmp_path / "evidence"
    _write(source_dir / "artifact_pack_validation.draft.json", {"validation_status": "passed"})
    _write(source_dir / "nested" / "longbridge_live_enablement_evidence.draft.json", {"platform": "longbridge"})

    payload = build_low_vol_dividend_live_enablement_evidence_intake(
        source_dirs=(source_dir,),
        evidence_dir=evidence_dir,
        output_dir=tmp_path / "out",
        platforms=("longbridge",),
        apply=False,
    )

    assert payload["intake_version"] == INTAKE_VERSION
    assert payload["would_copy_count"] == 2
    assert payload["copied_count"] == 0
    assert not (evidence_dir / "artifact_pack_validation.draft.json").exists()
    assert payload["gate_missing_files_count"] == 9
    assert payload["gate_live_enablement_allowed"] is False


def test_evidence_intake_apply_copies_matching_convention_files_and_runs_gate(tmp_path):
    source_dir = tmp_path / "source"
    evidence_dir = tmp_path / "evidence"
    _write(source_dir / "artifact_pack_validation.draft.json", {"validation_status": "passed"})
    _write(source_dir / "longbridge_live_enablement_evidence.draft.json", {"platform": "longbridge"})

    payload = write_low_vol_dividend_live_enablement_evidence_intake(
        source_dirs=(source_dir,),
        evidence_dir=evidence_dir,
        output_dir=tmp_path / "out",
        platforms=("longbridge",),
        apply=True,
    )

    assert payload["copied_count"] == 2
    assert payload["would_copy_count"] == 0
    assert (evidence_dir / "artifact_pack_validation.draft.json").exists()
    assert (evidence_dir / "longbridge_live_enablement_evidence.draft.json").exists()
    assert payload["gate_missing_files_count"] == 7
    assert Path(payload["summary_path"]).exists()


def test_evidence_intake_cli_json(tmp_path):
    source_dir = tmp_path / "source"
    evidence_dir = tmp_path / "evidence"
    _write(source_dir / "production_source_audit.draft.json", {"status": "passed"})

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-dir",
            str(source_dir),
            "--evidence-dir",
            str(evidence_dir),
            "--output-dir",
            str(tmp_path / "out"),
            "--platform",
            "ibkr",
            "--apply",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["copied_count"] == 1
    assert payload["platforms"] == ["ibkr"]
    assert Path(payload["summary_path"]).exists()
