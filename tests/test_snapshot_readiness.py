from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from hk_equity_snapshot_pipelines.snapshot_readiness import build_snapshot_readiness, build_snapshot_readiness_matrix

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "print_snapshot_readiness.py"


REJECTED_PROFILES = (
    "hk_liquid_momentum",
    "hk_blue_chip_snapshot",
    "hk_southbound_momentum",
    "hk_ah_premium",
    "hk_policy_value_quality",
    "hk_free_cash_flow",
    "hk_qglv",
    "hk_factor_mix_qvlm",
    "hk_shareholder_yield_quality",
    "hk_index_event",
)


def test_snapshot_readiness_keeps_only_low_vol_dividend_quality():
    plan = build_snapshot_readiness("hk_low_vol_dividend_quality_snapshot", platform_id="ibkr")

    assert plan["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert plan["promotion_scope"] == "first_snapshot_live_enablement_candidate"
    assert plan["live_enablement_work_queue"] is True
    assert plan["requires_full_backtest_now"] is True
    assert plan["evidence_tooling_scope"] == "active_first_snapshot_shared_evidence_tools"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["IBKR_MARKET"] == "HK"
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["manifest"] == (
        "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_backtest_drawdown"] == 0.30
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.0
    assert "dividend_yield_trap_controls" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "forecast_dividend_yield_estimate_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert plan["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )
    assert any("Sample artifacts" in reason for reason in plan["blocking_reasons"])


@pytest.mark.parametrize("profile", REJECTED_PROFILES)
def test_snapshot_readiness_rejects_removed_profiles(profile: str):
    with pytest.raises(ValueError, match="Unknown snapshot profile"):
        build_snapshot_readiness(profile, platform_id="longbridge")


def test_snapshot_readiness_matrix_only_lists_retained_profile():
    matrix = build_snapshot_readiness_matrix(platform_id="longbridge")

    assert matrix["profile_count"] == 1
    assert matrix["first_snapshot_candidate_count"] == 1
    assert matrix["research_only_scaffold_count"] == 0
    assert [profile["profile"] for profile in matrix["profiles"]] == ["hk_low_vol_dividend_quality_snapshot"]
    assert matrix["recommended_live_enablement_sequence"] == ["hk_low_vol_dividend_quality_snapshot"]
    assert matrix["research_only_scaffold_sequence"] == []


def test_snapshot_readiness_cli_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--profile", "hk_low_vol_dividend_quality_snapshot", "--platform", "longbridge", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv"
    )
