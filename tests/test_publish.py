from __future__ import annotations

import json
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_quality import build_and_write_snapshot
from hk_equity_snapshot_pipelines.publish import (
    SOURCE_INPUT_SUMMARY_FILENAME,
    VALIDATION_REPORT_FILENAME,
    build_publish_plan,
    publish_artifacts,
)
from hk_equity_snapshot_pipelines.snapshot_artifact_validation import validate_snapshot_artifact_pack

ROOT = Path(__file__).resolve().parents[1]
FACTOR_SNAPSHOT = ROOT / "examples" / "low_vol_dividend_quality" / "factor_snapshot.sample.csv"


def test_build_publish_plan_includes_contract_artifacts(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)

    plan = build_publish_plan(
        profile="hk_low_vol_dividend_quality_snapshot",
        artifact_dir=tmp_path,
        gcs_prefix="gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging/",
    )

    destinations = [item.destination for item in plan]
    assert len(plan) == 4
    assert destinations == [
        "gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging/hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv",
        "gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging/hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json",
        "gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging/hk_low_vol_dividend_quality_snapshot_ranking_latest.csv",
        "gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging/release_status_summary.json",
    ]


def test_build_publish_plan_includes_validation_report_when_present(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)
    validation = validate_snapshot_artifact_pack("hk_low_vol_dividend_quality_snapshot", tmp_path)
    (tmp_path / VALIDATION_REPORT_FILENAME).write_text(json.dumps(validation), encoding="utf-8")

    plan = build_publish_plan(
        profile="hk_low_vol_dividend_quality_snapshot",
        artifact_dir=tmp_path,
        gcs_prefix="gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging",
    )

    assert len(plan) == 5
    assert plan[-1].destination.endswith(f"/{VALIDATION_REPORT_FILENAME}")


def test_build_publish_plan_includes_source_input_summary_when_present(tmp_path):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)
    (tmp_path / SOURCE_INPUT_SUMMARY_FILENAME).write_text('{"source_name": "longbridge_openapi_staging"}', encoding="utf-8")

    plan = build_publish_plan(
        profile="hk_low_vol_dividend_quality_snapshot",
        artifact_dir=tmp_path,
        gcs_prefix="gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging",
    )

    assert len(plan) == 5
    assert plan[-1].destination.endswith(f"/{SOURCE_INPUT_SUMMARY_FILENAME}")


def test_publish_artifacts_dry_run_prints_commands(tmp_path, capsys):
    build_and_write_snapshot(factor_snapshot_path=FACTOR_SNAPSHOT, output_dir=tmp_path)
    plan = build_publish_plan(
        profile="hk_low_vol_dividend_quality_snapshot",
        artifact_dir=tmp_path,
        gcs_prefix="gs://bucket/hk_equity/hk_low_vol_dividend_quality_snapshot_staging",
    )

    publish_artifacts(plan, dry_run=True)

    output = capsys.readouterr().out
    assert "DRY-RUN gcloud storage cp" in output
    assert "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv" in output
