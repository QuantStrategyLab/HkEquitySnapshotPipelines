from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_artifact_evidence import (
    DRAFT_VERSION,
    build_low_vol_dividend_artifact_evidence_draft,
    write_low_vol_dividend_artifact_evidence_draft,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_quality import build_and_write_snapshot


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SOURCE = ROOT / "examples" / "low_vol_dividend_quality" / "factor_snapshot.sample.csv"
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_artifact_evidence.py"


def _artifact_dir(tmp_path: Path) -> Path:
    path = tmp_path / "artifacts"
    build_and_write_snapshot(factor_snapshot_path=SAMPLE_SOURCE, output_dir=path)
    return path


def test_artifact_evidence_draft_validates_local_artifact_but_stays_pending_without_publication_proof(tmp_path):
    payload = build_low_vol_dividend_artifact_evidence_draft(
        artifact_dir=_artifact_dir(tmp_path),
        evidence_generated_at="2026-06-03",
    )
    draft = payload["artifact_pack_validation_draft"]

    assert payload["draft_version"] == DRAFT_VERSION
    assert payload["local_artifact_valid"] is True
    assert payload["artifact_section_status"] == "pending"
    assert payload["artifact_section_can_pass"] is False
    assert draft["validation_status"] == "passed"
    assert draft["valid"] is False
    assert draft["snapshot_sha256"]
    assert draft["row_count"] == 6
    assert draft["published_artifacts_not_sample"] is False
    assert "artifact_pack_validation.valid must be true" in payload["artifact_section_errors_preview"]


def test_artifact_evidence_draft_can_complete_artifact_section_with_immutable_publication_proof(tmp_path):
    payload = build_low_vol_dividend_artifact_evidence_draft(
        artifact_dir=_artifact_dir(tmp_path),
        artifact_release_id="hk-low-vol-dividend-quality-20260603-001",
        published_snapshot_uri="gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv",
        published_manifest_uri="gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv.manifest.json",
        published_ranking_uri="gs://qsl-evidence/hk-low-vol/artifacts/ranking.csv",
        published_release_summary_uri="gs://qsl-evidence/hk-low-vol/artifacts/release-summary.json",
        evidence_uri="gs://qsl-evidence/hk-low-vol/artifacts/artifact-validation.json",
        evidence_generated_at="2026-06-03",
        confirm_immutable_release=True,
        confirm_published_artifacts_not_sample=True,
        confirm_manifest_provenance=True,
        confirm_release_summary_ready=True,
    )
    draft = payload["artifact_pack_validation_draft"]

    assert payload["artifact_section_status"] == "passed"
    assert payload["artifact_section_can_pass"] is True
    assert draft["valid"] is True
    assert draft["immutable_release_id"] is True
    assert draft["manifest_snapshot_sha256_verified"] is True
    assert draft["manifest_row_count_verified"] is True
    assert draft["release_summary_ready"] is True
    assert payload["artifact_section_errors_preview"] == []
    assert payload["live_enablement_allowed"] is False


def test_artifact_evidence_draft_rejects_mutable_release_alias(tmp_path):
    payload = build_low_vol_dividend_artifact_evidence_draft(
        artifact_dir=_artifact_dir(tmp_path),
        artifact_release_id="latest",
        published_snapshot_uri="gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv",
        published_manifest_uri="gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv.manifest.json",
        published_ranking_uri="gs://qsl-evidence/hk-low-vol/artifacts/ranking.csv",
        published_release_summary_uri="gs://qsl-evidence/hk-low-vol/artifacts/release-summary.json",
        evidence_uri="gs://qsl-evidence/hk-low-vol/artifacts/artifact-validation.json",
        evidence_generated_at="2026-06-03",
        confirm_immutable_release=True,
        confirm_published_artifacts_not_sample=True,
        confirm_manifest_provenance=True,
        confirm_release_summary_ready=True,
    )

    assert payload["artifact_section_status"] == "pending"
    assert payload["artifact_section_can_pass"] is False
    assert "artifact_pack_validation.valid must be true" in payload["artifact_section_errors_preview"]


def test_write_artifact_evidence_draft_outputs_files(tmp_path):
    payload = write_low_vol_dividend_artifact_evidence_draft(
        output_dir=tmp_path / "out",
        artifact_dir=_artifact_dir(tmp_path),
        evidence_generated_at="2026-06-03",
    )

    draft_path = Path(payload["draft_path"])
    summary_path = Path(payload["summary_path"])
    assert draft_path.exists()
    assert summary_path.exists()
    assert json.loads(draft_path.read_text(encoding="utf-8"))["profile"] == "hk_low_vol_dividend_quality"
    assert "artifact_pack_validation_draft" not in json.loads(summary_path.read_text(encoding="utf-8"))


def test_artifact_evidence_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--artifact-dir",
            str(_artifact_dir(tmp_path)),
            "--evidence-generated-at",
            "2026-06-03",
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["local_artifact_valid"] is True
    assert payload["artifact_section_status"] == "pending"
    assert payload["draft_path"].endswith("artifact_pack_validation.draft.json")
