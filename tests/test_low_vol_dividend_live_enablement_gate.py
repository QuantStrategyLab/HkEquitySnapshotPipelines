from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_live_enablement_gate import (
    GATE_RUNNER_VERSION,
    build_low_vol_dividend_live_enablement_gate_run,
    write_low_vol_dividend_live_enablement_gate_run,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_operator_evidence import write_low_vol_dividend_operator_evidence_draft

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_low_vol_dividend_live_enablement_gate.py"
DATE = "2026-06-03"


def _write_operator_pack(evidence_dir: Path, *, platform: str) -> None:
    write_low_vol_dividend_operator_evidence_draft(
        output_dir=evidence_dir,
        platform=platform,
        evidence_generated_at=DATE,
        broker_evidence_uri=f"gs://qsl-evidence/hk-low-vol/{platform}/broker-permissions.json",
        confirm_hk_market_data=True,
        confirm_sehk_trading_permission=True,
        confirm_hkd_cash_handling=True,
        confirm_fees_verified=True,
        confirm_stamp_duty_or_exemption_verified=True,
        rebalance_evidence_uri=f"gs://qsl-evidence/hk-low-vol/{platform}/rebalance-window.json",
        rebalance_window_count=3,
        confirm_rebalance_or_event_window_covered=True,
        rollout_evidence_uri=f"gs://qsl-evidence/hk-low-vol/{platform}/rollout-plan.json",
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
        approval_reference="operator-approval://hk-low-vol-dividend-quality/20260603",
        confirm_operator_approved=True,
        confirm_strategy_runtime_enablement_approved=True,
        confirm_dry_run_removal_approved=True,
        strategy_policy_evidence_uri="gs://qsl-evidence/hk-low-vol/policy/quality-yield-policy-evidence.json",
        confirm_all_strategy_policy_evidence=True,
    )


def test_gate_run_reports_all_missing_convention_files_when_evidence_dir_empty(tmp_path):
    payload = build_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=tmp_path / "evidence",
        output_dir=tmp_path / "out",
        validation_as_of=DATE,
    )

    assert payload["gate_runner_version"] == GATE_RUNNER_VERSION
    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["status"] == "blocked"
    assert payload["live_enablement_allowed"] is False
    assert len(payload["missing_files"]) == 15
    assert payload["assemblies"]["longbridge"]["provided_sections"] == []
    assert payload["audit"]["gates"]["longbridge_live_enablement_evidence"] == "failed"
    assert payload["audit"]["gates"]["ibkr_live_enablement_evidence"] == "failed"


def test_gate_run_consumes_operator_convention_files_and_keeps_remaining_gaps(tmp_path):
    evidence_dir = tmp_path / "evidence"
    _write_operator_pack(evidence_dir, platform="longbridge")
    _write_operator_pack(evidence_dir, platform="ibkr")

    payload = build_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=evidence_dir,
        output_dir=tmp_path / "out",
        validation_as_of=DATE,
    )

    longbridge_sections = set(payload["assemblies"]["longbridge"]["provided_sections"])
    assert {
        "broker_permission_and_fee_verification",
        "paper_or_dry_run_rebalance_window",
        "runtime_rollout_plan",
        "risk_approval",
        "strategy_policy_evidence",
    }.issubset(longbridge_sections)
    assert payload["assemblies"]["longbridge"]["missing_section_sources"] == [
        "production_snapshot_source_audit",
        "artifact_pack_validation",
        "walk_forward_backtest",
        "platform_dry_run_order_preview",
    ]
    missing_paths = {Path(item["path"]).name for item in payload["missing_files"]}
    assert "production_source_audit.draft.json" in missing_paths
    assert "longbridge_broker_permission_and_fee_verification.draft.json" not in missing_paths
    assert payload["live_enablement_allowed"] is False


def test_write_gate_run_outputs_summary_audit_and_assembled_files(tmp_path):
    payload = write_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=tmp_path / "evidence",
        output_dir=tmp_path / "out",
        validation_as_of=DATE,
    )

    assert Path(payload["audit_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert (tmp_path / "out" / "assembled" / "longbridge_live_enablement_evidence.json").exists()
    assert (tmp_path / "out" / "assembled" / "ibkr_live_enablement_evidence.json").exists()
    summary = json.loads(Path(payload["summary_path"]).read_text(encoding="utf-8"))
    assert "audit" not in summary
    assert summary["status"] == "blocked"


def test_gate_cli_defaults_to_zero_for_blocked_drafts(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--output-dir",
            str(tmp_path / "out"),
            "--validation-as-of",
            DATE,
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "blocked"
    assert payload["live_enablement_allowed"] is False
    assert payload["audit_path"].endswith("final_live_enablement_audit.json")


def test_gate_cli_can_fail_on_blocked(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--output-dir",
            str(tmp_path / "out"),
            "--validation-as-of",
            DATE,
            "--fail-on-blocked",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert json.loads(completed.stdout)["live_enablement_allowed"] is False
