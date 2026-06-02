from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_evidence_bundle import (
    LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_STATUS,
    LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_VERSION,
    build_low_vol_dividend_evidence_bundle,
    write_low_vol_dividend_evidence_bundle,
)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_low_vol_dividend_evidence_bundle.py"


def test_low_vol_dividend_evidence_bundle_defines_pending_non_live_templates():
    payload = build_low_vol_dividend_evidence_bundle()

    assert payload["bundle_version"] == LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_VERSION
    assert payload["status"] == LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_STATUS
    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert payload["production_deployment_allowed"] is False
    assert payload["platforms"] == ["longbridge", "ibkr"]
    assert payload["production_source_audit_template"]["status"] == "pending"
    assert payload["walk_forward_backtest_template"]["status"] == "pending"
    assert payload["walk_forward_backtest_template"]["out_of_sample"] is False
    assert payload["walk_forward_backtest_template"]["benchmark_symbol"]
    assert "forecast_dividend_yield_estimate_history" in payload["production_source_required_boolean_fields"]
    assert "dividend_yield_trap_controls" in payload["production_source_required_boolean_fields"]
    assert "annual_return" in payload["walk_forward_required_metric_fields"]
    assert "max_drawdown" in payload["walk_forward_required_metric_fields"]
    assert "hk_fees_and_levies" in payload["walk_forward_required_boolean_controls"]
    assert "survivorship_bias_controls" in payload["walk_forward_required_boolean_controls"]
    assert "low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe" in (
        payload["quality_yield_required_ablation_tests"]
    )
    assert "sample_artifacts_or_synthetic_data_used_as_evidence" in payload["stop_conditions"]


def test_low_vol_dividend_evidence_bundle_writes_templates(tmp_path):
    payload = write_low_vol_dividend_evidence_bundle(output_dir=tmp_path, platforms=("longbridge",))

    for key in (
        "bundle_path",
        "readme_path",
        "production_source_audit_template_path",
        "walk_forward_backtest_template_path",
        "strategy_policy_evidence_template_path",
    ):
        assert Path(payload[key]).exists()
    assert Path(payload["platform_live_enablement_template_paths"]["longbridge"]).exists()
    assert payload["platforms"] == ["longbridge"]

    source_template = json.loads(Path(payload["production_source_audit_template_path"]).read_text(encoding="utf-8"))
    backtest_template = json.loads(Path(payload["walk_forward_backtest_template_path"]).read_text(encoding="utf-8"))
    assert source_template["section_name"] == "production_snapshot_source_audit"
    assert source_template["template_status"] == "pending_operator_evidence"
    assert backtest_template["section_name"] == "walk_forward_backtest"
    assert backtest_template["max_drawdown"] is None


def test_low_vol_dividend_evidence_bundle_cli_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--json", "--platform", "ibkr"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["platforms"] == ["ibkr"]
    assert "ibkr" in payload["platform_live_enablement_templates"]
