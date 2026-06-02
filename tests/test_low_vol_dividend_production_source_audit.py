from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.low_vol_dividend_production_source_audit import (
    LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION,
    PRODUCTION_REQUIRED_COLUMNS,
    analyze_low_vol_dividend_production_source,
    build_low_vol_dividend_production_source_audit_draft,
    write_low_vol_dividend_production_source_audit_draft,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SOURCE = ROOT / "examples" / "low_vol_dividend_quality" / "factor_snapshot.sample.csv"
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_production_source_audit.py"


def test_analyze_low_vol_dividend_production_source_accepts_schema_but_warns_sample_path():
    result = analyze_low_vol_dividend_production_source(SAMPLE_SOURCE)

    assert result["audit_draft_version"] == LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION
    assert result["profile"] == "hk_low_vol_dividend_quality"
    assert result["local_schema_status"] == "passed_with_warnings"
    assert result["row_count"] == 6
    assert result["symbol_count"] == 6
    assert result["source_coverage_start"] == "2026-05-29"
    assert result["source_coverage_end"] == "2026-05-29"
    assert result["missing_columns"] == []
    assert result["errors"] == []
    assert any("sample" in warning for warning in result["warnings"])


def test_analyze_low_vol_dividend_production_source_reports_missing_required_columns(tmp_path):
    bad_path = tmp_path / "bad.csv"
    pd.DataFrame({"symbol": ["00941"], "as_of": ["2026-05-29"]}).to_csv(bad_path, index=False)

    result = analyze_low_vol_dividend_production_source(bad_path)

    assert result["local_schema_status"] == "failed"
    assert set(result["missing_columns"]) == set(PRODUCTION_REQUIRED_COLUMNS) - {"symbol", "as_of"}
    assert any("missing required production source columns" in error for error in result["errors"])


def test_build_low_vol_dividend_production_source_audit_draft_stays_pending():
    payload = build_low_vol_dividend_production_source_audit_draft(
        factor_snapshot_path=SAMPLE_SOURCE,
        source_name="operator-prod-source",
        production_source_uri="gs://qsl-hk-prod-source/low-vol-dividend/source.csv",
        source_quality_report_uri="gs://qsl-hk-prod-source/low-vol-dividend/quality.json",
        point_in_time_data_dictionary_uri="gs://qsl-hk-prod-source/low-vol-dividend/dictionary.json",
        evidence_uri="gs://qsl-hk-evidence/low-vol-dividend/source-audit.json",
        evidence_generated_at="2026-06-03",
    )
    draft = payload["production_source_audit_draft"]

    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert draft["status"] == "pending"
    assert draft["source_name"] == "operator-prod-source"
    assert draft["source_coverage_start"] == "2026-05-29"
    assert draft["source_coverage_end"] == "2026-05-29"
    assert draft["point_in_time_asof"] is False
    assert draft["forecast_dividend_yield_estimate_history"] is False
    assert draft["local_schema_validation"]["local_schema_status"] == "passed_with_warnings"


def test_write_low_vol_dividend_production_source_audit_draft_outputs_files(tmp_path):
    payload = write_low_vol_dividend_production_source_audit_draft(
        factor_snapshot_path=SAMPLE_SOURCE,
        source_name="operator-prod-source",
        output_dir=tmp_path,
        evidence_generated_at="2026-06-03",
    )

    draft_path = Path(payload["draft_path"])
    summary_path = Path(payload["summary_path"])
    assert draft_path.exists()
    assert summary_path.exists()
    assert json.loads(draft_path.read_text(encoding="utf-8"))["status"] == "pending"
    assert json.loads(summary_path.read_text(encoding="utf-8"))["row_count"] == 6


def test_low_vol_dividend_production_source_audit_cli_json_writes_files(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--factor-snapshot",
            str(SAMPLE_SOURCE),
            "--source-name",
            "operator-prod-source",
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
    assert payload["production_source_audit_draft"]["status"] == "pending"
    assert payload["local_schema_validation"]["row_count"] == 6
    assert Path(payload["draft_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert Path(payload["draft_path"]).name == "production_source_audit.draft.json"
