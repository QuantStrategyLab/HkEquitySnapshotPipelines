from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_evidence_assembler import (
    build_low_vol_dividend_live_enablement_evidence_assembly,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_operator_evidence import (
    DRAFT_VERSION,
    build_low_vol_dividend_operator_evidence_draft,
    write_low_vol_dividend_operator_evidence_draft,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_operator_evidence.py"
DATE = "2026-06-03"


def test_operator_evidence_draft_stays_pending_without_confirmations():
    payload = build_low_vol_dividend_operator_evidence_draft(
        platform="longbridge",
        evidence_generated_at=DATE,
    )

    assert payload["draft_version"] == DRAFT_VERSION
    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["platform"] == "longbridge"
    assert payload["operator_sections_can_pass"] is False
    assert payload["section_statuses"] == {
        "broker_permission_and_fee_verification": "pending",
        "paper_or_dry_run_rebalance_window": "pending",
        "runtime_rollout_plan": "pending",
        "risk_approval": "pending",
        "strategy_policy_evidence": "pending",
    }
    assert payload["broker_permission_and_fee_verification_draft"]["status"] == "pending"
    assert payload["risk_approval_draft"]["operator_approved"] is False
    assert payload["operator_section_errors_preview"]
    assert payload["live_enablement_allowed"] is False


def test_operator_evidence_draft_can_complete_operator_sections():
    payload = build_low_vol_dividend_operator_evidence_draft(
        platform="ibkr",
        evidence_generated_at=DATE,
        broker_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/broker-permissions.json",
        confirm_hk_market_data=True,
        confirm_sehk_trading_permission=True,
        confirm_hkd_cash_handling=True,
        confirm_fees_verified=True,
        confirm_stamp_duty_or_exemption_verified=True,
        rebalance_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/rebalance-window.json",
        rebalance_window_count=3,
        confirm_rebalance_or_event_window_covered=True,
        rollout_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/rollout-plan.json",
        initial_capital_fraction=0.10,
        per_symbol_capital_fraction=0.05,
        intraday_drawdown_tripwire=0.02,
        cumulative_drawdown_tripwire=0.04,
        observation_trading_days_before_scale_up=20,
        confirm_staged_rollout_plan=True,
        confirm_kill_switch=True,
        confirm_rollback_plan=True,
        confirm_post_deploy_monitoring=True,
        confirm_operator_notification=True,
        confirm_severe_weather_trading_runbook=True,
        confirm_vcm_cooling_off_handling=True,
        approval_reference="operator-approval://hk-low-vol-dividend-quality-snapshot/20260603",
        confirm_operator_approved=True,
        confirm_strategy_runtime_enablement_approved=True,
        confirm_dry_run_removal_approved=True,
        strategy_policy_evidence_uri="gs://qsl-evidence/hk-low-vol/policy/quality-yield-policy-evidence.json",
        confirm_all_strategy_policy_evidence=True,
    )

    assert payload["operator_sections_can_pass"] is True
    assert set(payload["section_statuses"].values()) == {"passed"}
    assert payload["operator_section_errors_preview"] == {}
    assert payload["broker_permission_and_fee_verification_draft"]["hk_market_data"] is True
    assert payload["paper_or_dry_run_rebalance_window_draft"]["window_count"] == 3
    assert payload["runtime_rollout_plan_draft"]["initial_capital_fraction"] == 0.10
    assert payload["risk_approval_section_status"] == "passed"
    assert payload["strategy_policy_evidence_draft"]["status"] == "passed"
    assert payload["live_enablement_allowed"] is False


def test_operator_evidence_respects_strategy_policy_controls_file(tmp_path):
    controls = {
        "low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe": True,
    }
    controls_path = tmp_path / "controls.json"
    controls_path.write_text(json.dumps(controls), encoding="utf-8")

    payload = build_low_vol_dividend_operator_evidence_draft(
        platform="longbridge",
        evidence_generated_at=DATE,
        strategy_policy_evidence_uri="gs://qsl-evidence/hk-low-vol/policy/partial.json",
        strategy_policy_controls_file=controls_path,
    )

    policy = payload["strategy_policy_evidence_draft"]
    assert policy["low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe"] is True
    assert policy["dividend_yield_only_vs_dividend_quality_controls"] is False
    assert policy["status"] == "pending"
    assert payload["section_statuses"]["strategy_policy_evidence"] == "pending"


def test_write_operator_evidence_draft_outputs_section_files(tmp_path):
    payload = write_low_vol_dividend_operator_evidence_draft(
        output_dir=tmp_path / "out",
        platform="longbridge",
        evidence_generated_at=DATE,
        broker_evidence_uri="gs://qsl-evidence/hk-low-vol/longbridge/broker-permissions.json",
        confirm_hk_market_data=True,
        confirm_sehk_trading_permission=True,
        confirm_hkd_cash_handling=True,
        confirm_fees_verified=True,
        confirm_stamp_duty_or_exemption_verified=True,
    )

    for key in (
        "broker_permission_and_fee_verification_path",
        "paper_or_dry_run_rebalance_window_path",
        "runtime_rollout_plan_path",
        "risk_approval_path",
        "strategy_policy_evidence_path",
        "summary_path",
    ):
        assert Path(payload[key]).exists()
    assert json.loads(Path(payload["summary_path"]).read_text(encoding="utf-8"))["platform"] == "longbridge"


def test_operator_output_can_feed_assembler(tmp_path):
    payload = write_low_vol_dividend_operator_evidence_draft(
        output_dir=tmp_path / "operator",
        platform="ibkr",
        evidence_generated_at=DATE,
        broker_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/broker-permissions.json",
        confirm_hk_market_data=True,
        confirm_sehk_trading_permission=True,
        confirm_hkd_cash_handling=True,
        confirm_fees_verified=True,
        confirm_stamp_duty_or_exemption_verified=True,
        rebalance_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/rebalance-window.json",
        rebalance_window_count=3,
        confirm_rebalance_or_event_window_covered=True,
        rollout_evidence_uri="gs://qsl-evidence/hk-low-vol/ibkr/rollout-plan.json",
        initial_capital_fraction=0.10,
        per_symbol_capital_fraction=0.05,
        intraday_drawdown_tripwire=0.02,
        cumulative_drawdown_tripwire=0.04,
        observation_trading_days_before_scale_up=20,
        confirm_staged_rollout_plan=True,
        confirm_kill_switch=True,
        confirm_rollback_plan=True,
        confirm_post_deploy_monitoring=True,
        confirm_operator_notification=True,
        confirm_severe_weather_trading_runbook=True,
        confirm_vcm_cooling_off_handling=True,
        approval_reference="operator-approval://hk-low-vol-dividend-quality-snapshot/20260603",
        confirm_operator_approved=True,
        confirm_strategy_runtime_enablement_approved=True,
        confirm_dry_run_removal_approved=True,
        strategy_policy_evidence_uri="gs://qsl-evidence/hk-low-vol/policy/quality-yield-policy-evidence.json",
        confirm_all_strategy_policy_evidence=True,
    )

    assembled = build_low_vol_dividend_live_enablement_evidence_assembly(
        platform="ibkr",
        validation_as_of=DATE,
        broker_permission_file=payload["broker_permission_and_fee_verification_path"],
        rebalance_window_file=payload["paper_or_dry_run_rebalance_window_path"],
        runtime_rollout_file=payload["runtime_rollout_plan_path"],
        risk_approval_file=payload["risk_approval_path"],
        strategy_policy_evidence_file=payload["strategy_policy_evidence_path"],
    )

    assert "broker_permission_and_fee_verification" in assembled["provided_sections"]
    assert assembled["evidence"]["broker_permission_and_fee_verification"]["status"] == "passed"
    assert assembled["evidence"]["runtime_rollout_plan"]["status"] == "passed"
    assert assembled["live_enablement_allowed"] is False
    assert "production_snapshot_source_audit" in assembled["missing_section_sources"]


def test_operator_evidence_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "longbridge",
            "--evidence-generated-at",
            DATE,
            "--broker-evidence-uri",
            "gs://qsl-evidence/hk-low-vol/longbridge/broker-permissions.json",
            "--confirm-hk-market-data",
            "--confirm-sehk-trading-permission",
            "--confirm-hkd-cash-handling",
            "--confirm-fees-verified",
            "--confirm-stamp-duty-or-exemption-verified",
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["platform"] == "longbridge"
    assert payload["section_statuses"]["broker_permission_and_fee_verification"] == "passed"
    assert payload["section_statuses"]["runtime_rollout_plan"] == "pending"
    assert payload["broker_permission_and_fee_verification_path"].endswith(
        "longbridge_broker_permission_and_fee_verification.draft.json"
    )
