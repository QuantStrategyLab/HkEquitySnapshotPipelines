from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.live_enablement_evidence import build_live_enablement_evidence_template
from hk_equity_snapshot_pipelines.low_vol_dividend_evidence_assembler import (
    ASSEMBLY_VERSION,
    build_low_vol_dividend_live_enablement_evidence_assembly,
    write_low_vol_dividend_live_enablement_evidence_assembly,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "assemble_low_vol_dividend_live_enablement_evidence.py"
PROFILE = "hk_low_vol_dividend_quality_snapshot"
DATE = "2026-06-03"
HEX = "a" * 64


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _set_bool_fields(section: dict) -> None:
    for key, value in list(section.items()):
        if isinstance(value, bool):
            section[key] = True


def _passing_evidence(platform: str = "longbridge") -> dict:
    evidence = build_live_enablement_evidence_template(PROFILE, platform=platform)
    evidence["validation_as_of"] = DATE

    source = evidence["production_snapshot_source_audit"]
    _set_bool_fields(source)
    source.update(
        {
            "status": "passed",
            "source_name": "operator-pit-factor-snapshot",
            "source_coverage_start": "2018-01-01",
            "source_coverage_end": "2026-01-01",
            "production_source_uri": "gs://qsl-evidence/hk-low-vol/source/factors.csv",
            "source_quality_report_uri": "gs://qsl-evidence/hk-low-vol/source/source-quality.json",
            "point_in_time_data_dictionary_uri": "gs://qsl-evidence/hk-low-vol/source/pit-data-dictionary.json",
            "evidence_generated_at": DATE,
            "evidence_uri": "gs://qsl-evidence/hk-low-vol/source/source-audit.json",
        }
    )

    artifact = evidence["artifact_pack_validation"]
    _set_bool_fields(artifact)
    artifact.update(
        {
            "valid": True,
            "validation_status": "passed",
            "artifact_dir": "gs://qsl-evidence/hk-low-vol/artifacts/hk-low-vol-dividend-quality-snapshot-20260603-001",
            "artifact_release_id": "hk-low-vol-dividend-quality-snapshot-20260603-001",
            "snapshot_sha256": HEX,
            "row_count": 50,
            "published_snapshot_uri": "gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv",
            "published_manifest_uri": "gs://qsl-evidence/hk-low-vol/artifacts/snapshot.csv.manifest.json",
            "published_ranking_uri": "gs://qsl-evidence/hk-low-vol/artifacts/ranking.csv",
            "published_release_summary_uri": "gs://qsl-evidence/hk-low-vol/artifacts/release-summary.json",
            "evidence_generated_at": DATE,
            "evidence_uri": "gs://qsl-evidence/hk-low-vol/artifacts/artifact-validation.json",
        }
    )

    backtest = evidence["walk_forward_backtest"]
    _set_bool_fields(backtest)
    backtest.update(
        {
            "status": "passed",
            "period_start": "2018-01-01",
            "period_end": "2026-01-01",
            "annual_return": 0.12,
            "max_drawdown": -0.18,
            "rolling_oos_fold_max_drawdown": -0.22,
            "oos_fold_count": 4,
            "max_single_period_return_contribution": 0.42,
            "annual_return_to_max_drawdown_ratio": 0.67,
            "annualized_turnover": 0.60,
            "benchmark_symbol": "02800",
            "benchmark_annual_return": 0.06,
            "strategy_excess_return": 0.06,
            "evidence_generated_at": DATE,
            "evidence_uri": "gs://qsl-evidence/hk-low-vol/backtests/walk-forward.json",
        }
    )

    dry_run = evidence["platform_dry_run_order_preview"]
    _set_bool_fields(dry_run)
    dry_run.update(
        {
            "status": "passed",
            "orders_previewed": 2,
            "fractional_share_errors": 0,
            "lot_size_errors": 0,
            "notification_correlation_id": f"{platform}-run-001",
            "notification_delivery_log_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/notification-log.json",
            "dry_run_session_id": f"{platform}-run-001",
            "raw_order_preview_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/runtime-report.json",
            "raw_order_preview_sha256": HEX,
            "quote_snapshot_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/quotes.json",
            "quote_snapshot_sha256": HEX,
            "fee_breakdown_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/fees.json",
            "fee_breakdown_sha256": HEX,
            "adv_window_trading_days": 20,
            "median_daily_turnover_hkd": 50_000_000,
            "max_single_order_adv_fraction": 0.01,
            "rebalance_adv_fraction": 0.05,
            "evidence_generated_at": DATE,
            "evidence_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/platform-dry-run.json",
        }
    )

    broker = evidence["broker_permission_and_fee_verification"]
    _set_bool_fields(broker)
    broker.update(
        {
            "status": "passed",
            "evidence_generated_at": DATE,
            "evidence_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/broker-permissions.json",
        }
    )

    rebalance = evidence["paper_or_dry_run_rebalance_window"]
    _set_bool_fields(rebalance)
    rebalance.update(
        {
            "status": "passed",
            "window_count": 3,
            "evidence_generated_at": DATE,
            "evidence_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/rebalance-window.json",
        }
    )

    rollout = evidence["runtime_rollout_plan"]
    _set_bool_fields(rollout)
    rollout.update(
        {
            "status": "passed",
            "initial_capital_fraction": 0.10,
            "per_symbol_capital_fraction": 0.05,
            "intraday_drawdown_tripwire": 0.02,
            "cumulative_drawdown_tripwire": 0.04,
            "observation_trading_days_before_scale_up": 20,
            "evidence_generated_at": DATE,
            "evidence_uri": f"gs://qsl-evidence/hk-low-vol/{platform}/rollout-plan.json",
        }
    )

    evidence["risk_approval"].update(
        {
            "operator_approved": True,
            "strategy_runtime_enablement_approved": True,
            "dry_run_removal_approved": True,
            "approval_reference": "operator-approval://hk-low-vol-dividend-quality-snapshot/20260603",
        }
    )

    policy = evidence["strategy_policy_evidence"]
    _set_bool_fields(policy)
    policy.update(
        {
            "status": "passed",
            "evidence_generated_at": DATE,
            "evidence_uri": "gs://qsl-evidence/hk-low-vol/policy/quality-yield-policy-evidence.json",
        }
    )
    return evidence


def test_assembler_uses_template_and_remains_blocked_without_section_files():
    payload = build_low_vol_dividend_live_enablement_evidence_assembly(
        platform="longbridge",
        validation_as_of=DATE,
    )

    assert payload["assembly_version"] == ASSEMBLY_VERSION
    assert payload["profile"] == PROFILE
    assert payload["platform"] == "longbridge"
    assert payload["provided_sections"] == []
    assert "artifact_pack_validation" in payload["missing_section_sources"]
    assert payload["validation_status"] == "failed"
    assert payload["live_enablement_allowed"] is False
    assert payload["validation_errors_count"] > 0


def test_assembler_extracts_wrapped_and_direct_sections_into_passing_pack(tmp_path):
    evidence = _passing_evidence("ibkr")
    source_file = _write(tmp_path / "source.wrapper.json", {"production_source_audit_draft": evidence["production_snapshot_source_audit"]})
    artifact_file = _write(tmp_path / "artifact.direct.json", evidence["artifact_pack_validation"])
    backtest_file = _write(tmp_path / "backtest.wrapper.json", {"walk_forward_backtest_draft": evidence["walk_forward_backtest"]})
    platform_file = _write(tmp_path / "platform.full-evidence.json", {"evidence": evidence})
    broker_file = _write(tmp_path / "broker.json", {"broker_permission_and_fee_verification": evidence["broker_permission_and_fee_verification"]})
    rebalance_file = _write(tmp_path / "rebalance.json", evidence["paper_or_dry_run_rebalance_window"])
    rollout_file = _write(tmp_path / "rollout.json", {"runtime_rollout_plan_draft": evidence["runtime_rollout_plan"]})
    risk_file = _write(tmp_path / "risk.json", evidence["risk_approval"])
    policy_file = _write(tmp_path / "policy.json", {"strategy_policy_evidence_draft": evidence["strategy_policy_evidence"]})

    payload = build_low_vol_dividend_live_enablement_evidence_assembly(
        platform="ibkr",
        validation_as_of=DATE,
        production_source_audit_file=source_file,
        artifact_pack_validation_file=artifact_file,
        walk_forward_backtest_file=backtest_file,
        platform_dry_run_file=platform_file,
        broker_permission_file=broker_file,
        rebalance_window_file=rebalance_file,
        runtime_rollout_file=rollout_file,
        risk_approval_file=risk_file,
        strategy_policy_evidence_file=policy_file,
    )

    assert payload["provided_sections"] == sorted(payload["section_sources"])
    assert payload["missing_section_sources"] == []
    assert payload["validation_status"] == "passed"
    assert payload["live_enablement_allowed"] is True
    assert payload["evidence"]["template_status"] == "assembled_live_enablement_allowed"
    assert payload["validation_errors_preview"] == []


def test_write_assembly_outputs_evidence_validation_and_summary(tmp_path):
    output = write_low_vol_dividend_live_enablement_evidence_assembly(
        output_dir=tmp_path / "out",
        platform="longbridge",
        validation_as_of=DATE,
    )

    evidence_path = Path(output["evidence_path"])
    validation_path = Path(output["validation_path"])
    summary_path = Path(output["summary_path"])
    assert evidence_path.exists()
    assert validation_path.exists()
    assert summary_path.exists()
    assert json.loads(evidence_path.read_text(encoding="utf-8"))["platform"] == "longbridge"
    assert json.loads(validation_path.read_text(encoding="utf-8"))["live_enablement_allowed"] is False
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "evidence" not in summary
    assert "validation" not in summary


def test_assembly_cli_defaults_to_zero_for_blocked_drafts(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "longbridge",
            "--validation-as-of",
            DATE,
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
    assert payload["live_enablement_allowed"] is False
    assert payload["evidence_path"].endswith("longbridge_live_enablement_evidence.json")


def test_assembly_cli_can_fail_on_blocked_when_requested(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "ibkr",
            "--validation-as-of",
            DATE,
            "--output-dir",
            str(tmp_path / "out"),
            "--fail-on-blocked",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert json.loads(completed.stdout)["live_enablement_allowed"] is False
