from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_backtest_evidence import (
    LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION,
    analyze_low_vol_dividend_backtest_summary,
    build_low_vol_dividend_backtest_evidence_draft,
    write_low_vol_dividend_backtest_evidence_draft,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_backtest_evidence.py"


def _summary(**overrides):
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
        "benchmark_symbol": "02800",
        "benchmark_annual_return": 0.06,
        "strategy_excess_return": 0.06,
    }
    payload.update(overrides)
    return payload


def test_analyze_low_vol_dividend_backtest_summary_accepts_complete_summary():
    result = analyze_low_vol_dividend_backtest_summary(_summary())

    assert result["draft_version"] == LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION
    assert result["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert result["local_backtest_summary_status"] == "passed_with_warnings"
    assert result["missing_fields"] == []
    assert result["missing_boolean_controls"] == []
    assert round(result["computed_annual_return_to_max_drawdown_ratio"], 2) == 0.67
    assert result["errors"] == []
    assert any("annual_return_to_max_drawdown_ratio missing" in warning for warning in result["warnings"])


def test_analyze_low_vol_dividend_backtest_summary_rejects_bad_gates():
    result = analyze_low_vol_dividend_backtest_summary(
        _summary(
            max_drawdown=-0.35,
            oos_fold_count=2,
            annualized_turnover=1.20,
            strategy_excess_return=0.0,
            lookahead_bias_controls=False,
        )
    )

    assert result["local_backtest_summary_status"] == "failed"
    assert "lookahead_bias_controls" in result["missing_boolean_controls"]
    assert "max_drawdown exceeds 30%" in result["errors"]
    assert "oos_fold_count must be >= 3" in result["errors"]
    assert "annualized_turnover exceeds profile threshold" in result["errors"]
    assert "strategy_excess_return must be positive" in result["errors"]


def test_build_low_vol_dividend_backtest_evidence_draft_stays_pending():
    payload = build_low_vol_dividend_backtest_evidence_draft(
        summary=_summary(),
        evidence_uri="gs://qsl-hk-evidence/low-vol-dividend/backtest.json",
        evidence_generated_at="2026-06-03",
    )
    draft = payload["walk_forward_backtest_draft"]

    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert draft["status"] == "pending"
    assert draft["annual_return"] == 0.12
    assert draft["max_drawdown"] == -0.18
    assert round(draft["annual_return_to_max_drawdown_ratio"], 2) == 0.67
    assert draft["evidence_uri"] == "gs://qsl-hk-evidence/low-vol-dividend/backtest.json"
    assert draft["local_backtest_summary_validation"]["local_backtest_summary_status"] == "passed_with_warnings"


def test_write_low_vol_dividend_backtest_evidence_draft_outputs_files(tmp_path):
    payload = write_low_vol_dividend_backtest_evidence_draft(
        summary=_summary(annual_return_to_max_drawdown_ratio=0.67),
        output_dir=tmp_path,
        evidence_generated_at="2026-06-03",
    )

    draft_path = Path(payload["draft_path"])
    summary_path = Path(payload["summary_path"])
    assert draft_path.exists()
    assert summary_path.exists()
    assert json.loads(draft_path.read_text(encoding="utf-8"))["status"] == "pending"
    assert json.loads(summary_path.read_text(encoding="utf-8"))["local_backtest_summary_status"] == "passed"


def test_low_vol_dividend_backtest_evidence_cli_json(tmp_path):
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(_summary()), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--summary",
            str(summary_path),
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

    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["walk_forward_backtest_draft"]["status"] == "pending"
    assert payload["walk_forward_backtest_draft"]["benchmark_symbol"] == "02800"
    assert Path(payload["draft_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert Path(payload["draft_path"]).name == "walk_forward_backtest.draft.json"
