from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.first_snapshot_backtest_evidence import (
    FIRST_SNAPSHOT_BACKTEST_DRAFT_VERSION,
    analyze_first_snapshot_backtest_summary,
    build_first_snapshot_backtest_evidence_draft,
    write_first_snapshot_backtest_evidence_draft,
)
from hk_equity_snapshot_pipelines.first_snapshot_evidence_bundle import (
    FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS,
    FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION,
    build_first_snapshot_evidence_bundle,
    write_first_snapshot_evidence_bundles,
)
from hk_equity_snapshot_pipelines.first_snapshot_evidence_profiles import get_first_snapshot_evidence_profile
from hk_equity_snapshot_pipelines.first_snapshot_live_enablement_package import (
    FIRST_SNAPSHOT_PACKAGE_STATUS,
    FIRST_SNAPSHOT_PACKAGE_VERSION,
    build_first_snapshot_live_enablement_package,
    write_first_snapshot_live_enablement_packages,
)
from hk_equity_snapshot_pipelines.first_snapshot_production_source_audit import (
    FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION,
    analyze_first_snapshot_production_source,
    build_first_snapshot_production_source_audit_draft,
    write_first_snapshot_production_source_audit_draft,
)
from hk_equity_snapshot_pipelines.first_snapshot_promotion_plan import FIRST_SNAPSHOT_PROFILE_ORDER
from hk_equity_snapshot_pipelines.live_enablement_policy import get_required_benchmark_symbol

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SCRIPT = ROOT / "scripts" / "build_first_snapshot_live_enablement_packages.py"
BUNDLE_SCRIPT = ROOT / "scripts" / "build_first_snapshot_evidence_bundles.py"
SOURCE_AUDIT_SCRIPT = ROOT / "scripts" / "draft_first_snapshot_production_source_audit.py"
BACKTEST_SCRIPT = ROOT / "scripts" / "draft_first_snapshot_backtest_evidence.py"
PROFILE = "hk_low_vol_dividend_quality_snapshot"


def _summary(profile: str = PROFILE, **overrides):
    payload = {
        "status": "passed",
        "out_of_sample": True,
        "period_start": "2018-01-01",
        "period_end": "2026-01-01",
        "annual_return": 0.12,
        "max_drawdown": -0.18,
        "rolling_oos_fold_max_drawdown": -0.22,
        "oos_fold_count": 4,
        "max_single_period_return_contribution": 0.42,
        "annualized_turnover": 0.60,
        "hk_fees_and_levies": True,
        "stamp_duty_or_exemption": True,
        "slippage": True,
        "lot_size_rounding": True,
        "suspension_handling": True,
        "survivorship_bias_controls": True,
        "lookahead_bias_controls": True,
        "benchmark_period_aligned": True,
        "rolling_oos_fold_drawdown_controls": True,
        "parameter_sensitivity_and_holdout_stability_controls": True,
        "regime_stress_and_liquidity_shock_controls": True,
        "fee_slippage_spread_stress_sensitivity_controls": True,
        "net_return_after_costs_controls": True,
        "data_vendor_reconciliation_and_missingness_controls": True,
        "corporate_action_delisting_and_stale_price_controls": True,
        "cash_leverage_short_borrow_and_margin_controls": True,
        "tail_loss_time_underwater_and_recovery_controls": True,
        "portfolio_correlation_and_aggregate_risk_budget_controls": True,
        "benchmark_symbol": get_required_benchmark_symbol(profile),
        "benchmark_annual_return": 0.06,
        "strategy_excess_return": 0.06,
    }
    payload.update(overrides)
    return payload


def test_first_snapshot_live_enablement_package_supports_retained_profile():
    payload = build_first_snapshot_live_enablement_package(PROFILE, platforms=("longbridge",))

    assert payload["package_version"] == FIRST_SNAPSHOT_PACKAGE_VERSION
    assert payload["profile"] == PROFILE
    assert payload["status"] == FIRST_SNAPSHOT_PACKAGE_STATUS
    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert payload["production_deployment_allowed"] is False
    assert payload["candidate_rank"] == 1
    assert payload["promotion_bucket"] == "first_snapshot_candidate"
    assert payload["platforms"] == ["longbridge"]
    assert payload["platform_env_templates"]["longbridge"]["LONGBRIDGE_DRY_RUN_ONLY"] == "true"
    assert any(item["section"] == "longbridge_live_enablement_evidence" for item in payload["required_evidence_files"])
    assert "any_oos_fold_drawdown_above_30_percent" in payload["stop_conditions"]


def test_first_snapshot_live_enablement_package_writes_index_and_profile_outputs(tmp_path):
    payload = write_first_snapshot_live_enablement_packages(output_dir=tmp_path, platforms=("ibkr",))

    assert payload["profiles_in_scope"] == list(FIRST_SNAPSHOT_PROFILE_ORDER) == [PROFILE]
    assert Path(payload["index_path"]).exists()
    paths = payload["package_paths"][PROFILE]
    assert Path(paths["json_path"]).exists()
    assert Path(paths["markdown_path"]).exists()
    assert json.loads(Path(paths["json_path"]).read_text(encoding="utf-8"))["platforms"] == ["ibkr"]


def test_first_snapshot_live_enablement_package_cli_json():
    completed = subprocess.run(
        [sys.executable, str(PACKAGE_SCRIPT), "--json", "--profile", PROFILE, "--platform", "ibkr"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profiles_in_scope"] == [PROFILE]
    assert payload["packages"][0]["platform_env_templates"]["ibkr"]["IBKR_DRY_RUN_ONLY"] == "true"


def test_first_snapshot_evidence_bundle_supports_retained_profile():
    payload = build_first_snapshot_evidence_bundle(PROFILE, platforms=("longbridge",))
    evidence_profile = get_first_snapshot_evidence_profile(PROFILE)

    assert payload["bundle_version"] == FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION
    assert payload["status"] == FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS
    assert payload["profile"] == PROFILE
    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert payload["production_source_required_columns"] == list(evidence_profile.required_production_columns)
    assert payload["production_source_focus"] == list(evidence_profile.production_source_focus)
    assert "quality_yield_sleeve_vs_momentum_value_low_volatility_sleeves" in payload[
        "quality_yield_required_ablation_tests"
    ]
    assert "longbridge" in payload["platform_live_enablement_templates"]


def test_first_snapshot_evidence_bundle_writes_retained_profile(tmp_path):
    payload = write_first_snapshot_evidence_bundles(output_dir=tmp_path, platforms=("longbridge",))

    assert Path(payload["index_path"]).exists()
    paths = payload["bundle_paths"][PROFILE]
    assert Path(paths["bundle_path"]).exists()
    assert Path(paths["production_source_audit_template_path"]).exists()
    assert Path(paths["walk_forward_backtest_template_path"]).exists()
    assert paths["platform_live_enablement_template_paths"].keys() == {"longbridge"}


def test_first_snapshot_evidence_bundle_cli_json():
    completed = subprocess.run([sys.executable, str(BUNDLE_SCRIPT), "--json", "--profile", PROFILE], check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)

    assert payload["profiles_in_scope"] == [PROFILE]
    assert payload["bundles"][0]["profile"] == PROFILE


def test_first_snapshot_production_source_audit_accepts_sample_but_warns_sample_path():
    evidence_profile = get_first_snapshot_evidence_profile(PROFILE)
    result = analyze_first_snapshot_production_source(PROFILE, ROOT / evidence_profile.sample_factor_snapshot_path)

    assert result["audit_draft_version"] == FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION
    assert result["profile"] == PROFILE
    assert result["local_schema_status"] == "passed_with_warnings"
    assert result["row_count"] > 0
    assert result["missing_columns"] == []
    assert result["errors"] == []
    assert any("sample" in warning for warning in result["warnings"])


def test_first_snapshot_production_source_audit_reports_missing_profile_columns(tmp_path):
    bad_path = tmp_path / "bad.csv"
    pd.DataFrame({"symbol": ["00941"], "as_of": ["2026-05-29"]}).to_csv(bad_path, index=False)

    result = analyze_first_snapshot_production_source(PROFILE, bad_path)
    required_columns = set(get_first_snapshot_evidence_profile(PROFILE).required_production_columns)

    assert result["local_schema_status"] == "failed"
    assert set(result["missing_columns"]) == required_columns - {"symbol", "as_of"}
    assert any("missing required production source columns" in error for error in result["errors"])


def test_first_snapshot_production_source_audit_draft_stays_pending():
    evidence_profile = get_first_snapshot_evidence_profile(PROFILE)
    payload = build_first_snapshot_production_source_audit_draft(
        profile=PROFILE,
        factor_snapshot_path=ROOT / evidence_profile.sample_factor_snapshot_path,
        source_name="operator-prod-source",
        evidence_generated_at="2026-06-03",
    )
    draft = payload["production_source_audit_draft"]

    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert draft["status"] == "pending"
    assert draft["local_schema_validation"]["local_schema_status"] == "passed_with_warnings"
    assert draft["profile_specific_source_focus"] == list(evidence_profile.production_source_focus)


def test_first_snapshot_production_source_audit_writes_files(tmp_path):
    evidence_profile = get_first_snapshot_evidence_profile(PROFILE)
    payload = write_first_snapshot_production_source_audit_draft(
        profile=PROFILE,
        factor_snapshot_path=ROOT / evidence_profile.sample_factor_snapshot_path,
        source_name="operator-prod-source",
        output_dir=tmp_path,
        evidence_generated_at="2026-06-03",
    )

    assert Path(payload["draft_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert json.loads(Path(payload["draft_path"]).read_text(encoding="utf-8"))["status"] == "pending"
    assert json.loads(Path(payload["summary_path"]).read_text(encoding="utf-8"))["profile"] == PROFILE


def test_first_snapshot_production_source_audit_cli_json():
    sample_path = ROOT / get_first_snapshot_evidence_profile(PROFILE).sample_factor_snapshot_path
    completed = subprocess.run(
        [
            sys.executable,
            str(SOURCE_AUDIT_SCRIPT),
            "--profile",
            PROFILE,
            "--factor-snapshot",
            str(sample_path),
            "--source-name",
            "operator-prod-source",
            "--evidence-generated-at",
            "2026-06-03",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == PROFILE
    assert payload["production_source_audit_draft"]["status"] == "pending"
    assert payload["local_schema_validation"]["missing_columns"] == []


def test_first_snapshot_backtest_summary_accepts_complete_summary():
    result = analyze_first_snapshot_backtest_summary(PROFILE, _summary())

    assert result["draft_version"] == FIRST_SNAPSHOT_BACKTEST_DRAFT_VERSION
    assert result["profile"] == PROFILE
    assert result["local_backtest_summary_status"] == "passed_with_warnings"
    assert result["missing_fields"] == []
    assert result["missing_boolean_controls"] == []
    assert round(result["computed_annual_return_to_max_drawdown_ratio"], 2) == 0.67
    assert result["errors"] == []


def test_first_snapshot_backtest_summary_rejects_bad_gates():
    result = analyze_first_snapshot_backtest_summary(
        PROFILE,
        _summary(
            max_drawdown=-0.35,
            oos_fold_count=2,
            annualized_turnover=1.20,
            strategy_excess_return=0.0,
            lookahead_bias_controls=False,
        ),
    )

    assert result["local_backtest_summary_status"] == "failed"
    assert "lookahead_bias_controls" in result["missing_boolean_controls"]
    assert "max_drawdown exceeds 30%" in result["errors"]
    assert "oos_fold_count must be >= 3" in result["errors"]
    assert "annualized_turnover exceeds profile threshold" in result["errors"]
    assert "strategy_excess_return must be positive" in result["errors"]


def test_first_snapshot_backtest_evidence_draft_stays_pending():
    payload = build_first_snapshot_backtest_evidence_draft(
        profile=PROFILE,
        summary=_summary(),
        evidence_uri=f"gs://qsl-hk-evidence/{PROFILE}/backtest.json",
        evidence_generated_at="2026-06-03",
    )
    draft = payload["walk_forward_backtest_draft"]

    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert draft["status"] == "pending"
    assert draft["annual_return"] == 0.12
    assert draft["max_drawdown"] == -0.18
    assert round(draft["annual_return_to_max_drawdown_ratio"], 2) == 0.67
    assert draft["benchmark_symbol"] == get_required_benchmark_symbol(PROFILE)
    assert draft["local_backtest_summary_validation"]["local_backtest_summary_status"] == "passed_with_warnings"


def test_first_snapshot_backtest_evidence_writes_files(tmp_path):
    payload = write_first_snapshot_backtest_evidence_draft(
        profile=PROFILE,
        summary=_summary(annual_return_to_max_drawdown_ratio=0.67),
        output_dir=tmp_path,
        evidence_generated_at="2026-06-03",
    )

    assert Path(payload["draft_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert json.loads(Path(payload["draft_path"]).read_text(encoding="utf-8"))["status"] == "pending"
    assert json.loads(Path(payload["summary_path"]).read_text(encoding="utf-8"))["local_backtest_summary_status"] == "passed"


def test_first_snapshot_backtest_evidence_cli_json(tmp_path):
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(_summary()), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(BACKTEST_SCRIPT),
            "--profile",
            PROFILE,
            "--summary",
            str(summary_path),
            "--evidence-generated-at",
            "2026-06-03",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == PROFILE
    assert payload["walk_forward_backtest_draft"]["status"] == "pending"
    assert payload["walk_forward_backtest_draft"]["benchmark_symbol"] == get_required_benchmark_symbol(PROFILE)


def test_first_snapshot_evidence_tools_reject_removed_profile():
    with pytest.raises(ValueError, match="Unsupported first snapshot evidence profile"):
        get_first_snapshot_evidence_profile("hk_free_cash_flow_quality")
