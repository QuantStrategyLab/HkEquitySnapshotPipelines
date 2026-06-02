from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .live_enablement_evidence import build_live_enablement_evidence_template
from .live_enablement_policy import (
    MAX_ALLOWED_BACKTEST_DRAWDOWN,
    MAX_SINGLE_PERIOD_RETURN_CONTRIBUTION,
    MIN_REQUIRED_OOS_FOLD_COUNT,
    MIN_RETURN_TO_DRAWDOWN_RATIO,
    get_max_allowed_annualized_turnover,
    get_required_benchmark_symbol,
)


LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION = "hk_low_vol_dividend_walk_forward_backtest_draft.v1"
DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_walk_forward_backtest")
REQUIRED_SUMMARY_FIELDS = (
    "period_start",
    "period_end",
    "annual_return",
    "max_drawdown",
    "rolling_oos_fold_max_drawdown",
    "oos_fold_count",
    "max_single_period_return_contribution",
    "annualized_turnover",
    "benchmark_symbol",
    "benchmark_annual_return",
    "strategy_excess_return",
)
REQUIRED_BOOLEAN_CONTROLS = (
    "out_of_sample",
    "hk_fees_and_levies",
    "stamp_duty_or_exemption",
    "slippage",
    "lot_size_rounding",
    "suspension_handling",
    "survivorship_bias_controls",
    "lookahead_bias_controls",
    "benchmark_period_aligned",
    "rolling_oos_fold_drawdown_controls",
    "parameter_sensitivity_and_holdout_stability_controls",
    "regime_stress_and_liquidity_shock_controls",
    "fee_slippage_spread_stress_sensitivity_controls",
    "net_return_after_costs_controls",
    "data_vendor_reconciliation_and_missingness_controls",
    "corporate_action_delisting_and_stale_price_controls",
    "cash_leverage_short_borrow_and_margin_controls",
    "tail_loss_time_underwater_and_recovery_controls",
    "portfolio_correlation_and_aggregate_risk_budget_controls",
)


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("backtest summary must be a JSON object")
    return payload


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _drawdown_abs(value: Any) -> float | None:
    number = _number(value)
    return abs(number) if number is not None else None


def _ratio(annual_return: Any, max_drawdown: Any) -> float | None:
    annual = _number(annual_return)
    drawdown = _drawdown_abs(max_drawdown)
    if annual is None or drawdown in (None, 0.0):
        return None
    return annual / drawdown


def _validate_period(summary: dict[str, Any], errors: list[str]) -> None:
    start = str(summary.get("period_start", "")).strip()
    end = str(summary.get("period_end", "")).strip()
    if not start or not end:
        return
    try:
        start_date = dt.date.fromisoformat(start[:10])
        end_date = dt.date.fromisoformat(end[:10])
    except ValueError:
        errors.append("period_start and period_end must be ISO dates")
        return
    if end_date <= start_date:
        errors.append("period_end must be after period_start")


def analyze_low_vol_dividend_backtest_summary(summary: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    missing_fields = [field for field in REQUIRED_SUMMARY_FIELDS if field not in summary]
    missing_boolean_controls = [field for field in REQUIRED_BOOLEAN_CONTROLS if summary.get(field) is not True]
    if missing_fields:
        errors.append("missing required walk-forward fields: " + ", ".join(missing_fields))
    if missing_boolean_controls:
        errors.append("missing or false walk-forward boolean controls: " + ", ".join(missing_boolean_controls))
    _validate_period(summary, errors)

    annual_return = _number(summary.get("annual_return"))
    if annual_return is not None and annual_return <= 0:
        errors.append("annual_return must be positive")
    max_drawdown = _drawdown_abs(summary.get("max_drawdown"))
    if max_drawdown is not None and max_drawdown > MAX_ALLOWED_BACKTEST_DRAWDOWN:
        errors.append("max_drawdown exceeds 30%")
    rolling_drawdown = _drawdown_abs(summary.get("rolling_oos_fold_max_drawdown"))
    if rolling_drawdown is not None and rolling_drawdown > MAX_ALLOWED_BACKTEST_DRAWDOWN:
        errors.append("rolling_oos_fold_max_drawdown exceeds 30%")
    oos_fold_count = _number(summary.get("oos_fold_count"))
    if oos_fold_count is not None and oos_fold_count < MIN_REQUIRED_OOS_FOLD_COUNT:
        errors.append(f"oos_fold_count must be >= {MIN_REQUIRED_OOS_FOLD_COUNT}")
    max_period_contribution = _number(summary.get("max_single_period_return_contribution"))
    if max_period_contribution is not None and max_period_contribution > MAX_SINGLE_PERIOD_RETURN_CONTRIBUTION:
        errors.append("max_single_period_return_contribution exceeds 60%")
    turnover = _number(summary.get("annualized_turnover"))
    max_turnover = get_max_allowed_annualized_turnover(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    if turnover is not None and turnover > max_turnover:
        errors.append("annualized_turnover exceeds profile threshold")
    benchmark_symbol = str(summary.get("benchmark_symbol", "")).strip()
    required_benchmark = get_required_benchmark_symbol(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    if benchmark_symbol and benchmark_symbol != required_benchmark:
        errors.append(f"benchmark_symbol must be {required_benchmark!r}")
    strategy_excess_return = _number(summary.get("strategy_excess_return"))
    if strategy_excess_return is not None and strategy_excess_return <= 0:
        errors.append("strategy_excess_return must be positive")

    computed_ratio = _ratio(summary.get("annual_return"), summary.get("max_drawdown"))
    declared_ratio = _number(summary.get("annual_return_to_max_drawdown_ratio"))
    if computed_ratio is not None and computed_ratio < MIN_RETURN_TO_DRAWDOWN_RATIO:
        errors.append("computed annual_return_to_max_drawdown_ratio is below 0.50")
    if declared_ratio is None and computed_ratio is not None:
        warnings.append("annual_return_to_max_drawdown_ratio missing; draft will use computed ratio")
    elif declared_ratio is not None and declared_ratio < MIN_RETURN_TO_DRAWDOWN_RATIO:
        errors.append("annual_return_to_max_drawdown_ratio is below 0.50")

    return {
        "draft_version": LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION,
        "profile": HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
        "local_backtest_summary_status": "failed" if errors else "passed_with_warnings" if warnings else "passed",
        "missing_fields": missing_fields,
        "missing_boolean_controls": missing_boolean_controls,
        "computed_annual_return_to_max_drawdown_ratio": computed_ratio,
        "errors": errors,
        "warnings": warnings,
    }


def build_low_vol_dividend_backtest_evidence_draft(
    *,
    summary: dict[str, Any],
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    analysis = analyze_low_vol_dividend_backtest_summary(summary)
    template = build_live_enablement_evidence_template(contract.profile, platform="longbridge")
    draft = dict(template["walk_forward_backtest"])
    computed_ratio = analysis["computed_annual_return_to_max_drawdown_ratio"]
    draft.update({field: summary.get(field, draft.get(field)) for field in REQUIRED_SUMMARY_FIELDS})
    draft.update({field: summary.get(field, draft.get(field)) for field in REQUIRED_BOOLEAN_CONTROLS})
    draft["annual_return_to_max_drawdown_ratio"] = summary.get("annual_return_to_max_drawdown_ratio", computed_ratio)
    draft["status"] = "pending"
    draft["evidence_generated_at"] = evidence_generated_at or dt.date.today().isoformat()
    draft["evidence_uri"] = evidence_uri
    draft["local_backtest_summary_validation"] = analysis
    draft["operator_note"] = (
        "This is a draft only. Keep status=pending until the full walk-forward report, "
        "fold metrics, parameter sensitivity, cost model, and PIT/no-lookahead evidence are attached."
    )
    return {
        "draft_version": LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "walk_forward_backtest_draft": draft,
        "local_backtest_summary_validation": analysis,
    }


def write_low_vol_dividend_backtest_evidence_draft(
    *,
    summary: dict[str, Any],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_low_vol_dividend_backtest_evidence_draft(
        summary=summary,
        evidence_uri=evidence_uri,
        evidence_generated_at=evidence_generated_at,
    )
    draft_path = output_dir / "walk_forward_backtest.draft.json"
    summary_path = output_dir / "walk_forward_backtest_summary_validation.json"
    draft_path.write_text(
        json.dumps(payload["walk_forward_backtest_draft"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(payload["local_backtest_summary_validation"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        **payload,
        "draft_path": str(draft_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft HK low-vol dividend walk-forward backtest evidence.")
    parser.add_argument("--summary", required=True, help="Operator-supplied walk-forward summary JSON")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for draft files")
    parser.add_argument("--evidence-uri", default="", help="Immutable backtest evidence URI")
    parser.add_argument("--evidence-generated-at", help="Evidence generation date in YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Print payload without writing files")
    args = parser.parse_args(argv)
    summary = _load_json(args.summary)
    if args.json:
        payload = build_low_vol_dividend_backtest_evidence_draft(
            summary=summary,
            evidence_uri=args.evidence_uri,
            evidence_generated_at=args.evidence_generated_at,
        )
    else:
        payload = write_low_vol_dividend_backtest_evidence_draft(
            summary=summary,
            output_dir=Path(args.output_dir),
            evidence_uri=args.evidence_uri,
            evidence_generated_at=args.evidence_generated_at,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "LOW_VOL_DIVIDEND_BACKTEST_DRAFT_VERSION",
    "REQUIRED_BOOLEAN_CONTROLS",
    "REQUIRED_SUMMARY_FIELDS",
    "analyze_low_vol_dividend_backtest_summary",
    "build_low_vol_dividend_backtest_evidence_draft",
    "main",
    "write_low_vol_dividend_backtest_evidence_draft",
]
