from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.first_snapshot_promotion_plan import (
    FIRST_SNAPSHOT_PROFILE_ORDER,
    FIRST_SNAPSHOT_PROMOTION_PLAN_VERSION,
    build_first_snapshot_promotion_plan,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "print_first_snapshot_promotion_plan.py"


def test_first_snapshot_promotion_plan_scopes_only_first_candidates():
    plan = build_first_snapshot_promotion_plan()

    assert plan["plan_version"] == FIRST_SNAPSHOT_PROMOTION_PLAN_VERSION
    assert plan["status"] == "first_snapshot_promotion_plan_not_live_enabled"
    assert plan["live_enablement_allowed_without_evidence"] is False
    assert plan["profiles_in_scope"] == list(FIRST_SNAPSHOT_PROFILE_ORDER)
    assert [profile["profile"] for profile in plan["profiles"]] == list(FIRST_SNAPSHOT_PROFILE_ORDER)
    assert "hk_residual_momentum_quality" in plan["excluded_from_scope"]
    assert "hk_index_rebalance_event" in plan["excluded_from_scope"]
    assert all(profile["runtime_enabled"] is False for profile in plan["profiles"])
    assert all(profile["promotion_bucket"] == "first_snapshot_candidate" for profile in plan["profiles"])
    assert {step["name"] for step in plan["promotion_steps"]} == {
        "sample_artifact_smoke",
        "production_source_audit",
        "walk_forward_backtest",
        "artifact_pack_validation",
        "platform_dry_run_evidence",
        "operator_approval_and_rollout_plan",
    }


def test_first_snapshot_promotion_plan_includes_actionable_commands_and_gates():
    plan = build_first_snapshot_promotion_plan(profile="hk_low_vol_dividend_quality", platforms=("longbridge",))
    profile = plan["profiles"][0]

    assert plan["profiles_in_scope"] == ["hk_low_vol_dividend_quality"]
    assert "scripts/build_low_vol_dividend_sample.py" in profile["sample_build_commands"]["sample_script"]
    assert profile["artifact_validation_command"] == (
        "hkeq-validate-snapshot-artifact-pack "
        "--profile hk_low_vol_dividend_quality --artifact-dir data/output/hk_low_vol_dividend_quality --json"
    )
    assert profile["readiness_commands"] == {
        "longbridge": (
            "python scripts/print_snapshot_readiness.py "
            "--profile hk_low_vol_dividend_quality --platform longbridge --json"
        )
    }
    assert "--print-template --profile hk_low_vol_dividend_quality --platform longbridge --json" in (
        profile["live_enablement_evidence_template_commands"]["longbridge"]
    )
    assert profile["platform_env_templates"]["longbridge"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_low_vol_dividend_quality_factor_snapshot_latest.csv"
    )
    assert profile["live_enablement_thresholds"]["max_allowed_backtest_drawdown"] == 0.30
    assert profile["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert plan["shared_gates"]["backtest_validation_policy"]["min_required_oos_fold_count"] == 3
    assert plan["shared_gates"]["quality_yield_live_enablement_policy"]["required"] is True


def test_first_snapshot_promotion_plan_cli_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--profile", "hk_free_cash_flow_quality", "--platform", "ibkr", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profiles_in_scope"] == ["hk_free_cash_flow_quality"]
    profile = payload["profiles"][0]
    assert profile["sample_build_commands"]["sample_script"] == (
        "PYTHONPATH=src python scripts/build_free_cash_flow_sample.py"
    )
    assert profile["platform_env_templates"]["ibkr"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_free_cash_flow_quality_factor_snapshot_latest.csv"
    )
