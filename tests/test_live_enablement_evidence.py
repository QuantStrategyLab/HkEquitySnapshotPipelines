from __future__ import annotations

import json
import subprocess
import sys

from hk_equity_snapshot_pipelines.live_enablement_evidence import (
    build_live_enablement_evidence_template,
    validate_live_enablement_evidence,
)
from hk_equity_snapshot_pipelines.momentum_live_enablement_policy import (
    MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION,
    build_momentum_live_enablement_policy,
)
from hk_equity_snapshot_pipelines.quality_yield_live_enablement_policy import (
    QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION,
    build_quality_yield_live_enablement_policy,
)


def _complete_quality_yield_strategy_policy_evidence(**overrides):
    policy = build_quality_yield_live_enablement_policy()
    required_bool_fields = (
        *policy["required_ablation_tests"],
        *policy["required_stress_tests"],
        *policy["required_data_provenance"],
    )
    payload = {
        "status": "passed",
        "policy_version": QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION,
        **{field: True for field in required_bool_fields},
        "evidence_generated_at": "2026-05-10",
        "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/strategy-policy.json",
    }
    payload.update(overrides)
    return payload


def _complete_momentum_strategy_policy_evidence(**overrides):
    policy = build_momentum_live_enablement_policy()
    required_bool_fields = (
        *policy["required_ablation_tests"],
        *policy["required_stress_tests"],
        *policy["required_data_provenance"],
    )
    payload = {
        "status": "passed",
        "policy_version": MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION,
        **{field: True for field in required_bool_fields},
        "evidence_generated_at": "2026-05-10",
        "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-liquid-momentum-quality/strategy-policy.json",
    }
    payload.update(overrides)
    return payload


def _minimal_momentum_evidence(**overrides):
    payload = {
        "evidence_type": "hk_snapshot_live_enablement",
        "profile": "hk_liquid_momentum_quality",
        "platform": "longbridge",
        "validation_as_of": "2026-06-02",
        "production_snapshot_source_audit": {},
        "artifact_pack_validation": {},
        "walk_forward_backtest": {},
        "platform_dry_run_order_preview": {},
        "broker_permission_and_fee_verification": {},
        "paper_or_dry_run_rebalance_window": {},
        "runtime_rollout_plan": {},
        "risk_approval": {},
    }
    payload.update(overrides)
    return payload


def _minimal_policy_profile_evidence(profile: str, **overrides):
    payload = {
        "evidence_type": "hk_snapshot_live_enablement",
        "profile": profile,
        "platform": "longbridge",
        "validation_as_of": "2026-06-02",
        "production_snapshot_source_audit": {},
        "artifact_pack_validation": {},
        "walk_forward_backtest": {},
        "platform_dry_run_order_preview": {},
        "broker_permission_and_fee_verification": {},
        "paper_or_dry_run_rebalance_window": {},
        "runtime_rollout_plan": {},
        "risk_approval": {},
    }
    payload.update(overrides)
    return payload


def _evidence(**overrides):
    payload = {
        "evidence_type": "hk_snapshot_live_enablement",
        "profile": "hk_low_vol_dividend_quality",
        "platform": "longbridge",
        "validation_as_of": "2026-06-02",
        "production_snapshot_source_audit": {
            "status": "passed",
            "source_name": "audited-prod-factor-store",
            "source_coverage_start": "2018-01-01",
            "source_coverage_end": "2026-05-29",
            "production_source_uri": (
                "gs://qsl-hk-prod-sources/factors/hk-low-vol-dividend-quality/20260601/source.parquet"
            ),
            "source_quality_report_uri": (
                "gs://qsl-hk-prod-sources/factors/hk-low-vol-dividend-quality/20260601/source-quality.json"
            ),
            "point_in_time_data_dictionary_uri": (
                "gs://qsl-hk-prod-sources/factors/hk-low-vol-dividend-quality/20260601/data-dictionary.json"
            ),
            "point_in_time_asof": True,
            "adjusted_prices": True,
            "corporate_actions": True,
            "suspensions": True,
            "stale_price_checks": True,
            "missing_field_checks": True,
            "symbol_mapping": True,
            "survivorship_safe_universe": True,
            "fundamentals_point_in_time": True,
            "southbound_trading_eligibility_history": True,
            "dividend_history": True,
            "forecast_dividend_yield_estimate_history": True,
            "forecast_dividend_yield_vs_trailing_yield_benchmark_history": True,
            "three_year_cash_dividend_record_history": True,
            "earnings_and_payout_fields": True,
            "payout_ratio_bounds_history": True,
            "large_mid_cap_market_value_shortlist_history": True,
            "one_year_high_volatility_exclusion_history": True,
            "high_dividend_financial_soundness_screen_history": True,
            "sp_access_hk_low_vol_high_div_methodology_and_constituent_history": True,
            "hsi_vs_sp_low_vol_high_div_rebalance_and_capping_history": True,
            "volatility_beta_history": True,
            "sector_classification_history": True,
            "dividend_yield_trap_controls": True,
            "price_crash_bottom_decile_screen_history": True,
            "payout_coverage_and_earnings_positive_history": True,
            "low_volatility_beta_drawdown_stress": True,
            "sector_concentration_caps": True,
            "evidence_generated_at": "2026-05-20",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/source-audit.json",
        },
        "artifact_pack_validation": {
            "valid": True,
            "validation_status": "passed",
            "profile": "hk_low_vol_dividend_quality",
            "artifact_release_id": "hk-low-vol-dividend-quality-20260601T160000Z",
            "contract_version": "hk_low_vol_dividend_quality.factor_snapshot.v1",
            "snapshot_sha256": "a" * 64,
            "row_count": 12,
            "published_snapshot_uri": "gs://qsl-hk-artifacts/snapshot/hk-low-vol-dividend-quality/20260601/hk_low_vol_dividend_quality_factor_snapshot_latest.csv",
            "published_manifest_uri": "gs://qsl-hk-artifacts/snapshot/hk-low-vol-dividend-quality/20260601/hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json",
            "published_ranking_uri": "gs://qsl-hk-artifacts/snapshot/hk-low-vol-dividend-quality/20260601/hk_low_vol_dividend_quality_ranking_latest.csv",
            "published_release_summary_uri": "gs://qsl-hk-artifacts/snapshot/hk-low-vol-dividend-quality/20260601/release_status_summary.json",
            "immutable_release_id": True,
            "published_artifacts_not_sample": True,
            "manifest_snapshot_sha256_verified": True,
            "manifest_row_count_verified": True,
            "release_summary_ready": True,
            "evidence_generated_at": "2026-05-25",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/artifact-pack.json",
        },
        "walk_forward_backtest": {
            "status": "passed",
            "out_of_sample": True,
            "period_start": "2018-01-01",
            "period_end": "2026-01-01",
            "annual_return": 0.12,
            "max_drawdown": -0.18,
            "rolling_oos_fold_max_drawdown": -0.22,
            "annual_return_to_max_drawdown_ratio": 0.67,
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
            "evidence_generated_at": "2026-04-15",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/backtest.json",
        },
        "platform_dry_run_order_preview": {
            "status": "passed",
            "orders_previewed": 8,
            "fractional_share_errors": 0,
            "lot_size_errors": 0,
            "notification_sent": True,
            "notification_schema_version": "hk_live_enablement_notification.v1",
            "notification_event_type": "hk_snapshot_live_enablement_dry_run",
            "notification_correlation_id": "hk-snapshot-low-vol-dividend-20260602-dryrun-001",
            "notification_locale_en": True,
            "notification_locale_zh_hans": True,
            "notification_contains_profile": True,
            "notification_contains_platform": True,
            "notification_contains_validation_status": True,
            "notification_contains_order_preview_summary": True,
            "notification_redacts_sensitive_fields": True,
            "notification_delivery_log_uri": (
                "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/notifications/"
                "20260602-dryrun.json"
            ),
            "dry_run_session_id": "hk-snapshot-low-vol-dividend-longbridge-20260602-dryrun-001",
            "raw_order_preview_uri": (
                "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/order-preview/"
                "raw-order-preview.json"
            ),
            "raw_order_preview_sha256": "b" * 64,
            "quote_snapshot_uri": (
                "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/order-preview/quote-snapshot.json"
            ),
            "quote_snapshot_sha256": "c" * 64,
            "fee_breakdown_uri": (
                "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/order-preview/fee-breakdown.json"
            ),
            "fee_breakdown_sha256": "d" * 64,
            "order_preview_artifact_not_sample": True,
            "order_preview_redacts_sensitive_fields": True,
            "quote_snapshot_covers_all_symbols": True,
            "fee_breakdown_reconciled_to_broker_preview": True,
            "order_preview_reconciled_to_strategy_decision": True,
            "adv_window_trading_days": 60,
            "median_daily_turnover_hkd": 250_000_000,
            "max_single_order_adv_fraction": 0.01,
            "rebalance_adv_fraction": 0.04,
            "liquidity_cap_verified": True,
            "board_lot_rounding_verified": True,
            "odd_lot_avoidance_verified": True,
            "market_session_routing_verified": True,
            "vcm_price_band_controls_verified": True,
            "evidence_generated_at": "2026-05-28",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/order-preview.json",
        },
        "broker_permission_and_fee_verification": {
            "status": "passed",
            "hk_market_data": True,
            "sehk_trading_permission": True,
            "hkd_cash_handling": True,
            "fees_verified": True,
            "stamp_duty_or_exemption_verified": True,
            "evidence_generated_at": "2026-05-20",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/broker-fees.json",
        },
        "paper_or_dry_run_rebalance_window": {
            "status": "passed",
            "window_count": 3,
            "rebalance_or_event_window_covered": True,
            "evidence_generated_at": "2026-05-20",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/rebalance-windows.json",
        },
        "runtime_rollout_plan": {
            "status": "passed",
            "staged_rollout_plan_ready": True,
            "initial_capital_fraction": 0.10,
            "per_symbol_capital_fraction": 0.08,
            "intraday_drawdown_tripwire": 0.02,
            "cumulative_drawdown_tripwire": 0.04,
            "observation_trading_days_before_scale_up": 20,
            "kill_switch_ready": True,
            "rollback_plan_ready": True,
            "post_deploy_monitoring_ready": True,
            "operator_notification_ready": True,
            "severe_weather_trading_runbook_ready": True,
            "vcm_cooling_off_handling_ready": True,
            "evidence_generated_at": "2026-05-20",
            "evidence_uri": "gs://qsl-hk-evidence/snapshot/hk-low-vol-dividend-quality/rollout-plan.json",
        },
        "risk_approval": {
            "operator_approved": True,
            "strategy_runtime_enablement_approved": True,
            "dry_run_removal_approved": True,
            "approval_reference": "ops-review-2026-06-hk-low-vol-dividend-quality",
        },
        "strategy_policy_evidence": _complete_quality_yield_strategy_policy_evidence(),
    }
    payload.update(overrides)
    return payload


def test_validate_live_enablement_evidence_accepts_complete_pack():
    result = validate_live_enablement_evidence(_evidence())

    assert result["validation_status"] == "passed"
    assert result["live_enablement_allowed"] is True
    assert "dividend_history" in result["production_source_audit_policy"]["required_boolean_fields"]
    assert "three_year_cash_dividend_record_history" in (
        result["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "dividend_yield_trap_controls" in result["production_source_audit_policy"]["required_boolean_fields"]
    assert "price_crash_bottom_decile_screen_history" in (
        result["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "one_year_high_volatility_exclusion_history" in (
        result["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "high_dividend_financial_soundness_screen_history" in (
        result["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "source_coverage_start" in result["production_source_audit_policy"]["required_fields"]
    assert "production_source_uri" in result["production_source_audit_policy"]["required_uri_fields"]
    assert any("hslvie.pdf" in url for url in result["production_source_audit_policy"]["source_reference_urls"])
    assert any("hshylve.pdf" in url for url in result["production_source_audit_policy"]["source_reference_urls"])
    assert any("hsschyse.pdf" in url for url in result["production_source_audit_policy"]["source_reference_urls"])
    assert result["artifact_provenance_policy"]["sha256_hex_length"] == 64
    assert result["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert "token=" in result["evidence_uri_policy"]["rejected_query_markers"]
    assert result["validation_as_of"] == "2026-06-02"
    assert result["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert result["evidence_freshness_policy"]["max_allowed_age_days_by_section"]["platform_dry_run_order_preview"] == 14
    assert result["execution_capacity_policy"]["max_single_order_adv_fraction"] == 0.025
    assert result["execution_capacity_policy"]["min_median_daily_turnover_hkd"] == 20_000_000
    assert result["rollout_risk_policy"]["max_initial_capital_fraction"] == 0.25
    assert result["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert "notification_locale_zh_hans" in result["notification_audit_policy"]["required_boolean_fields"]
    assert result["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert result["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )
    assert "dividend_yield_trap_and_payout_cut_window" in (
        result["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "abnormally_high_yield_price_crash_bottom_decile_window" in (
        result["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "high_dividend_screened_financial_soundness_and_high_volatility_exclusion_window" in (
        result["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe" in (
        result["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "sp_access_low_vol_high_div_vs_hshylv_same_universe" in (
        result["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe" in (
        result["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "sp_access_hk_low_vol_high_div_methodology_and_constituent_history" in (
        result["quality_yield_live_enablement_policy"]["required_data_provenance"]
    )
    assert "forecast_dividend_yield_estimate_history" in (
        result["quality_yield_live_enablement_policy"]["required_data_provenance"]
    )
    assert _evidence()["strategy_policy_evidence"]["policy_version"] == (
        result["quality_yield_live_enablement_policy"]["policy_version"]
    )
    assert _evidence()["strategy_policy_evidence"]["low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe"] is True
    assert "raw_order_preview_uri" in result["dry_run_order_preview_policy"]["required_uri_fields"]
    assert "raw_order_preview_sha256" in result["dry_run_order_preview_policy"]["required_sha256_fields"]
    assert "fee_breakdown_reconciled_to_broker_preview" in (
        result["dry_run_order_preview_policy"]["required_boolean_fields"]
    )
    assert result["errors"] == []


def test_build_live_enablement_evidence_template_is_fillable_but_not_preapproved():
    template = build_live_enablement_evidence_template("hk_dividend_quality", platform="longbridge")

    assert template["evidence_type"] == "hk_snapshot_live_enablement"
    assert template["template_status"] == "pending_operator_evidence"
    assert template["profile"] == "hk_low_vol_dividend_quality"
    assert template["platform"] == "longbridge"
    assert template["max_allowed_annualized_turnover"] == 1.0
    assert template["validation_as_of"] == "<YYYY-MM-DD>"
    assert "dividend_history" in template["production_source_audit_policy"]["required_boolean_fields"]
    assert "forecast_dividend_yield_estimate_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "three_year_cash_dividend_record_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "high_dividend_financial_soundness_screen_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sector_concentration_caps" in template["production_source_audit_policy"]["required_boolean_fields"]
    assert "source_coverage_end" in template["production_source_audit_policy"]["required_fields"]
    assert "source_quality_report_uri" in template["production_source_audit_policy"]["required_uri_fields"]
    assert any("sp-access-hong-kong-low-volatility-high-dividend-index" in url for url in template["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "forecast-dividend-yield-strategy" in url
        for url in template["production_source_audit_policy"]["source_reference_urls"]
    )
    assert any("sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index" in url for url in template["production_source_audit_policy"]["source_reference_urls"])
    assert any("IM_hshylve.pdf" in url for url in template["production_source_audit_policy"]["source_reference_urls"])
    assert any("IM_hsschkye.pdf" in url for url in template["production_source_audit_policy"]["source_reference_urls"])
    assert "published_manifest_uri" in template["artifact_provenance_policy"]["required_uri_fields"]
    assert template["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert template["execution_capacity_policy"]["required"] is True
    assert template["execution_capacity_policy"]["min_median_daily_turnover_hkd"] == 20_000_000
    assert template["rollout_risk_policy"]["min_observation_trading_days_before_scale_up"] == 20
    assert template["notification_audit_policy"]["schema_version"] == "hk_live_enablement_notification.v1"
    assert template["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert template["dry_run_order_preview_policy"]["required"] is True
    assert template["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert template["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe"] is False
    assert template["strategy_policy_evidence"]["sp_access_low_vol_high_div_vs_hshylv_same_universe"] is False
    assert template["strategy_policy_evidence"]["forecast_dividend_yield_vs_trailing_dividend_yield_same_universe"] is False
    assert template["strategy_policy_evidence"]["dividend_yield_trap_and_payout_cut_window"] is False
    assert template["strategy_policy_evidence"]["forecast_dividend_cut_and_estimate_revision_window"] is False
    assert (
        template["strategy_policy_evidence"]["sp_access_hk_low_vol_high_div_methodology_and_constituent_history"]
        is False
    )
    assert template["strategy_policy_evidence"]["hkex_buyback_disclosure_and_share_count_history"] is False
    assert template["strategy_policy_evidence"]["forecast_dividend_yield_estimate_history"] is False
    assert template["strategy_policy_evidence"]["evidence_generated_at"] == ""
    assert template["strategy_policy_evidence"]["evidence_uri"] == ""
    assert template["production_snapshot_source_audit"]["dividend_history"] is False
    assert template["production_snapshot_source_audit"]["forecast_dividend_yield_estimate_history"] is False
    assert template["production_snapshot_source_audit"]["three_year_cash_dividend_record_history"] is False
    assert template["production_snapshot_source_audit"]["one_year_high_volatility_exclusion_history"] is False
    assert template["production_snapshot_source_audit"]["high_dividend_financial_soundness_screen_history"] is False
    assert template["production_snapshot_source_audit"]["dividend_yield_trap_controls"] is False
    assert template["production_snapshot_source_audit"]["price_crash_bottom_decile_screen_history"] is False
    assert template["production_snapshot_source_audit"]["source_coverage_start"] == ""
    assert template["production_snapshot_source_audit"]["production_source_uri"] == ""
    assert template["production_snapshot_source_audit"]["survivorship_safe_universe"] is False
    assert template["production_snapshot_source_audit"]["evidence_generated_at"] == ""
    assert template["walk_forward_backtest"]["max_drawdown"] is None
    assert template["walk_forward_backtest"]["rolling_oos_fold_max_drawdown"] is None
    assert template["walk_forward_backtest"]["annual_return_to_max_drawdown_ratio"] is None
    assert template["walk_forward_backtest"]["annualized_turnover"] is None
    assert template["walk_forward_backtest"]["hk_fees_and_levies"] is False
    assert template["walk_forward_backtest"]["fee_slippage_spread_stress_sensitivity_controls"] is False
    assert template["walk_forward_backtest"]["data_vendor_reconciliation_and_missingness_controls"] is False
    assert template["walk_forward_backtest"]["tail_loss_time_underwater_and_recovery_controls"] is False
    assert template["walk_forward_backtest"]["portfolio_correlation_and_aggregate_risk_budget_controls"] is False
    assert template["walk_forward_backtest"]["benchmark_symbol"] == "02800"
    assert template["walk_forward_backtest"]["strategy_excess_return"] is None
    assert template["artifact_pack_validation"]["contract_version"] == "hk_low_vol_dividend_quality.factor_snapshot.v1"
    assert template["artifact_pack_validation"]["published_artifacts_not_sample"] is False
    assert template["artifact_pack_validation"]["snapshot_sha256"] == ""
    assert template["evidence_uri_policy"]["required"] is True
    assert template["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert template["paper_or_dry_run_rebalance_window"]["min_required_window_count"] == 3
    assert template["platform_dry_run_order_preview"]["liquidity_cap_verified"] is False
    assert template["platform_dry_run_order_preview"]["median_daily_turnover_hkd"] is None
    assert template["platform_dry_run_order_preview"]["notification_locale_zh_hans"] is False
    assert template["platform_dry_run_order_preview"]["notification_delivery_log_uri"] == ""
    assert template["platform_dry_run_order_preview"]["dry_run_session_id"] == ""
    assert template["platform_dry_run_order_preview"]["raw_order_preview_uri"] == ""
    assert template["platform_dry_run_order_preview"]["raw_order_preview_sha256"] == ""
    assert template["platform_dry_run_order_preview"]["quote_snapshot_uri"] == ""
    assert template["platform_dry_run_order_preview"]["fee_breakdown_uri"] == ""
    assert template["platform_dry_run_order_preview"]["order_preview_artifact_not_sample"] is False
    assert template["platform_dry_run_order_preview"]["fee_breakdown_reconciled_to_broker_preview"] is False
    assert template["runtime_rollout_plan"]["staged_rollout_plan_ready"] is False
    assert template["runtime_rollout_plan"]["initial_capital_fraction"] is None
    assert template["risk_approval"]["operator_approved"] is False
    assert "hkeq-validate-snapshot-artifact-pack" in template["artifact_pack_validation"]["validator_command"]


def test_build_live_enablement_evidence_template_for_special_situation_policy():
    template = build_live_enablement_evidence_template("hk_southbound_momentum", platform="ibkr")

    assert template["profile"] == "hk_southbound_flow_momentum"
    assert template["platform"] == "ibkr"
    assert template["special_situation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert "stock_connect_daily_turnover" in template["production_source_audit_policy"]["required_boolean_fields"]
    assert "stock_connect_holding_history" in template["production_source_audit_policy"]["required_boolean_fields"]
    assert "connect_trading_calendar_alignment" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "signal_decay_window_and_rebalance_frequency_ablation" in (
        template["special_situation_live_enablement_policy"]["required_ablation_tests"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["southbound_flow_vs_price_momentum_same_universe"] is False
    assert template["strategy_policy_evidence"]["stock_connect_holiday_quota_or_trading_suspension_window"] is False
    assert template["strategy_policy_evidence"]["hkex_stock_connect_turnover_and_holding_history"] is False
    assert template["strategy_policy_evidence"]["market_on_close_vs_next_open_execution_window_ablation"] is False
    assert template["strategy_policy_evidence"]["official_schedule_vs_press_release_event_source_reconciliation"] is False
    assert template["strategy_policy_evidence"]["cas_random_close_price_limit_and_order_rejection_window"] is False
    assert template["strategy_policy_evidence"]["hsi_review_schedule_file_version_and_effective_date_history"] is False
    assert (
        template["strategy_policy_evidence"][
            "hsi_review_result_timestamp_constituent_weight_and_proforma_history"
        ]
        is False
    )
    assert (
        template["strategy_policy_evidence"][
            "hkex_cas_order_type_random_close_price_limit_and_rejection_history"
        ]
        is False
    )
    assert template["production_snapshot_source_audit"]["stock_connect_daily_turnover"] is False
    assert template["production_snapshot_source_audit"]["southbound_policy_event_stress_controls"] is False
    assert template["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"


def test_build_live_enablement_evidence_template_for_baseline_rotation_policy():
    template = build_live_enablement_evidence_template("hk_leader_rotation", platform="longbridge")

    assert template["profile"] == "hk_blue_chip_leader_rotation"
    assert template["platform"] == "longbridge"
    assert template["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_baseline_rotation_live_enablement_policy.v1"
    )
    assert "hsi_constituent_history" in template["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_methodology_and_review_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "board_lot_vcm_and_trading_session_rule_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "blue_chip_rotation_vs_hsi_tracker_same_universe" in (
        template["baseline_rotation_live_enablement_policy"]["required_ablation_tests"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_baseline_rotation_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["blue_chip_rotation_vs_hsi_tracker_same_universe"] is False
    assert template["strategy_policy_evidence"]["hsi_hstech_leadership_reversal_window"] is False
    assert template["strategy_policy_evidence"]["point_in_time_hsi_constituent_history"] is False
    assert template["production_snapshot_source_audit"]["hsi_constituent_history"] is False
    assert template["production_snapshot_source_audit"]["board_lot_vcm_and_trading_session_rule_history"] is False


def test_build_live_enablement_evidence_template_for_quality_growth_policy():
    template = build_live_enablement_evidence_template("hk_qglv", platform="longbridge")

    assert template["profile"] == "hk_quality_growth_low_volatility"
    assert template["platform"] == "longbridge"
    assert template["max_allowed_annualized_turnover"] == 1.0
    assert template["quality_growth_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_growth_live_enablement_policy.v1"
    )
    assert "revenue_earnings_roa_growth_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_negative_equity_financials_and_missing_factor_policy_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "quality_growth_low_vol_factor_ablation" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "quality_growth_vs_quality_only_vs_growth_only_vs_low_vol_only" in (
        template["quality_growth_live_enablement_policy"]["required_ablation_tests"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_quality_growth_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["quality_growth_vs_quality_only_vs_growth_only_vs_low_vol_only"] is False
    assert template["strategy_policy_evidence"]["hsi_qglv_four_component_score_vs_raw_quality_growth_inputs"] is False
    assert template["strategy_policy_evidence"]["growth_deceleration_and_earnings_revision_window"] is False
    assert template["strategy_policy_evidence"]["qglv_component_missingness_restatement_and_negative_equity_window"] is False
    assert template["strategy_policy_evidence"]["point_in_time_revenue_earnings_roa_growth_history"] is False
    assert (
        template["strategy_policy_evidence"][
            "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history"
        ]
        is False
    )
    assert template["production_snapshot_source_audit"]["revenue_earnings_roa_growth_history"] is False
    assert template["production_snapshot_source_audit"]["sector_neutralization_policy"] is False


def test_build_live_enablement_evidence_template_for_factor_mix_policy():
    template = build_live_enablement_evidence_template("hk_qvlm_risk_parity", platform="longbridge")

    assert template["profile"] == "hk_factor_mix_qvlm_risk_parity"
    assert template["platform"] == "longbridge"
    assert template["max_allowed_annualized_turnover"] == 1.20
    assert template["factor_mix_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_factor_mix_live_enablement_policy.v1"
    )
    assert "risk_parity_weighting_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qvlm_quality_value_low_vol_momentum_component_index_return_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "factor_mix_leave_one_out_ablation" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "qvlm_risk_parity_vs_equal_weight_factor_mix_same_universe" in (
        template["factor_mix_live_enablement_policy"]["required_ablation_tests"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_factor_mix_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["qvlm_risk_parity_vs_equal_weight_factor_mix_same_universe"] is False
    assert (
        template["strategy_policy_evidence"][
            "msci_hk_factor_mix_equal_weight_qvl_vs_hsi_risk_parity_qvlm_without_momentum"
        ]
        is False
    )
    assert template["strategy_policy_evidence"]["factor_crowding_and_low_volatility_reversal_window"] is False
    assert template["strategy_policy_evidence"]["component_index_overlap_and_capping_turnover_spike_window"] is False
    assert template["strategy_policy_evidence"]["factor_volatility_and_risk_parity_weight_history"] is False
    assert (
        template["strategy_policy_evidence"][
            "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history"
        ]
        is False
    )
    assert template["production_snapshot_source_audit"]["risk_parity_weighting_history"] is False
    assert template["production_snapshot_source_audit"]["factor_mix_leave_one_out_ablation"] is False


def test_build_live_enablement_evidence_template_for_momentum_policy():
    template = build_live_enablement_evidence_template("hk_industry_neutral_momentum", platform="longbridge")

    assert template["profile"] == "hk_residual_momentum_quality"
    assert template["platform"] == "longbridge"
    assert template["max_allowed_annualized_turnover"] == 1.20
    assert template["momentum_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_momentum_live_enablement_policy.v1"
    )
    assert "residual_vs_liquid_vs_composite_same_universe" in (
        template["momentum_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "msci_6_12_month_vs_hsi_52_week_high_descriptor_same_universe" in (
        template["momentum_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "hsi_hstech_sharp_reversal_window" in (
        template["momentum_live_enablement_policy"]["required_stress_tests"]
    )
    assert "risk_adjusted_momentum_volatility_normalization_history" in (
        template["momentum_live_enablement_policy"]["required_data_provenance"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == "hk_snapshot_momentum_live_enablement_policy.v1"
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["residual_vs_liquid_vs_composite_same_universe"] is False
    assert template["strategy_policy_evidence"]["hsi_hstech_sharp_reversal_window"] is False
    assert template["strategy_policy_evidence"]["risk_adjusted_momentum_volatility_normalization_history"] is False
    assert template["strategy_policy_evidence"]["evidence_uri"] == ""
    assert "momentum_6m_12m_one_month_skip_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert template["production_snapshot_source_audit"]["residual_model_reproducible"] is False
    assert template["production_snapshot_source_audit"]["momentum_turnover_buffer_and_capacity_history"] is False


def test_validate_live_enablement_evidence_result_includes_momentum_policy_for_momentum_profile():
    result = validate_live_enablement_evidence(
        {
            "evidence_type": "hk_snapshot_live_enablement",
            "profile": "hk_liquid_momentum_quality",
            "platform": "longbridge",
            "validation_as_of": "2026-06-02",
        }
    )

    assert result["profile"] == "hk_liquid_momentum_quality"
    assert result["live_enablement_allowed"] is False
    assert result["momentum_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_momentum_live_enablement_policy.v1"
    )
    assert result["momentum_live_enablement_policy"]["required_profile_order"] == [
        "hk_residual_momentum_quality",
        "hk_liquid_momentum_quality",
        "hk_composite_factor_quality_value_momentum",
    ]
    assert any("missing required evidence section" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_momentum_strategy_policy_section():
    result = validate_live_enablement_evidence(_minimal_momentum_evidence())

    assert result["live_enablement_allowed"] is False
    assert any(
        "missing required evidence section for momentum profile: strategy_policy_evidence" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_requires_momentum_ablation_and_stress_evidence():
    result = validate_live_enablement_evidence(
        _minimal_momentum_evidence(
            strategy_policy_evidence=_complete_momentum_strategy_policy_evidence(
                residual_vs_liquid_vs_composite_same_universe=False,
                hsi_hstech_sharp_reversal_window=False,
            )
        )
    )

    assert result["live_enablement_allowed"] is False
    assert any(
        "strategy_policy_evidence.residual_vs_liquid_vs_composite_same_universe must be true" in error
        for error in result["errors"]
    )
    assert any(
        "strategy_policy_evidence.hsi_hstech_sharp_reversal_window must be true" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_rejects_stale_momentum_policy_evidence():
    result = validate_live_enablement_evidence(
        _minimal_momentum_evidence(
            strategy_policy_evidence=_complete_momentum_strategy_policy_evidence(
                evidence_generated_at="2026-01-01"
            )
        )
    )

    assert result["live_enablement_allowed"] is False
    assert any("strategy_policy_evidence.evidence_generated_at is stale" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_quality_yield_strategy_policy_section():
    payload = _evidence()
    payload.pop("strategy_policy_evidence")

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "missing required evidence section for quality/yield profile: strategy_policy_evidence" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_requires_quality_yield_ablation_and_stress_evidence():
    payload = _evidence(
        strategy_policy_evidence=_complete_quality_yield_strategy_policy_evidence(
            low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe=False,
            dividend_yield_trap_and_payout_cut_window=False,
        )
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "strategy_policy_evidence.low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe must be true" in error
        for error in result["errors"]
    )
    assert any(
        "strategy_policy_evidence.dividend_yield_trap_and_payout_cut_window must be true" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_rejects_stale_quality_yield_policy_evidence():
    payload = _evidence(
        strategy_policy_evidence=_complete_quality_yield_strategy_policy_evidence(
            evidence_generated_at="2026-01-01"
        )
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("strategy_policy_evidence.evidence_generated_at is stale" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_strategy_policy_for_remaining_policy_families():
    profile_labels = {
        "hk_blue_chip_leader_rotation": "baseline-rotation",
        "hk_quality_growth_low_volatility": "quality-growth",
        "hk_factor_mix_qvlm_risk_parity": "factor-mix",
        "hk_central_soe_value_quality_select": "policy-value",
        "hk_southbound_flow_momentum": "special-situation",
    }

    for profile, label in profile_labels.items():
        result = validate_live_enablement_evidence(_minimal_policy_profile_evidence(profile))

        assert result["live_enablement_allowed"] is False
        assert any(
            f"missing required evidence section for {label} profile: strategy_policy_evidence" in error
            for error in result["errors"]
        )



def test_build_live_enablement_evidence_template_for_policy_value_policy():
    template = build_live_enablement_evidence_template("hk_policy_value_quality", platform="ibkr")

    assert template["profile"] == "hk_central_soe_value_quality_select"
    assert template["platform"] == "ibkr"
    assert template["max_allowed_annualized_turnover"] == 1.0
    assert template["policy_value_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_policy_value_live_enablement_policy.v1"
    )
    assert "central_soe_flag_methodology_version_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sasac_central_soe_parent_list_effective_date_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_40pct_factor_screening_and_buffer_rule_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "central_soe_largest_shareholder_source_list_effective_date_drift_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hkex_southbound_eligible_security_point_in_time_history" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "policy_event_and_governance_risk_controls" in (
        template["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "central_soe_value_quality_vs_broad_value_quality_same_universe" in (
        template["policy_value_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "central_soe_value_quality_vs_hsi_value_and_quality_factor_indexes_same_universe" in (
        template["policy_value_live_enablement_policy"]["required_ablation_tests"]
    )
    assert template["strategy_policy_evidence"]["policy_version"] == (
        "hk_snapshot_policy_value_live_enablement_policy.v1"
    )
    assert template["strategy_policy_evidence"]["status"] == "pending"
    assert template["strategy_policy_evidence"]["central_soe_value_quality_vs_broad_value_quality_same_universe"] is False
    assert template["strategy_policy_evidence"]["hsi_40pct_factor_screening_vs_unbuffered_top_rank_selection"] is False
    assert template["strategy_policy_evidence"]["policy_event_and_state_ownership_reform_window"] is False
    assert template["strategy_policy_evidence"]["hsi_factor_screening_cap_and_rebalance_turnover_spike_window"] is False
    assert template["strategy_policy_evidence"]["government_shareholder_classification_history"] is False
    assert template["strategy_policy_evidence"]["hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history"] is False
    assert template["production_snapshot_source_audit"]["central_soe_flag_methodology_version_history"] is False
    assert template["production_snapshot_source_audit"]["sasac_central_soe_parent_list_effective_date_history"] is False
    assert template["production_snapshot_source_audit"]["policy_event_and_governance_risk_controls"] is False


def test_validate_live_enablement_evidence_rejects_drawdown_above_30_percent():
    payload = _evidence(walk_forward_backtest={**_evidence()["walk_forward_backtest"], "max_drawdown": -0.35})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("max_drawdown exceeds" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_oos_fold_drawdown_above_30_percent():
    payload = _evidence(
        walk_forward_backtest={**_evidence()["walk_forward_backtest"], "rolling_oos_fold_max_drawdown": -0.35}
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("rolling_oos_fold_max_drawdown exceeds" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_low_return_to_drawdown_ratio():
    payload = _evidence(
        walk_forward_backtest={**_evidence()["walk_forward_backtest"], "annual_return_to_max_drawdown_ratio": 0.49}
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("annual_return_to_max_drawdown_ratio must be" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_low_computed_return_to_drawdown_ratio():
    payload = _evidence(
        walk_forward_backtest={
            **_evidence()["walk_forward_backtest"],
            "annual_return": 0.04,
            "max_drawdown": -0.20,
            "annual_return_to_max_drawdown_ratio": 2.00,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("computed_annual_return_to_max_drawdown_ratio must be" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_excess_turnover():
    payload = _evidence(walk_forward_backtest={**_evidence()["walk_forward_backtest"], "annualized_turnover": 1.25})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert result["max_allowed_annualized_turnover"] == 1.0
    assert any("annualized_turnover exceeds" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_hk_cost_model_flags():
    payload = _evidence(walk_forward_backtest={**_evidence()["walk_forward_backtest"], "slippage": False})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("walk_forward_backtest.slippage" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_positive_benchmark_excess_return():
    payload = _evidence(walk_forward_backtest={**_evidence()["walk_forward_backtest"], "strategy_excess_return": 0.0})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("strategy_excess_return must be positive" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_profile_benchmark_symbol():
    payload = _evidence(walk_forward_backtest={**_evidence()["walk_forward_backtest"], "benchmark_symbol": "03110"})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("benchmark_symbol must be '02800'" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_minimum_oos_years():
    payload = _evidence(
        walk_forward_backtest={
            **_evidence()["walk_forward_backtest"],
            "period_start": "2024-01-01",
            "period_end": "2026-01-01",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("period must cover at least" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_minimum_rebalance_windows():
    payload = _evidence(paper_or_dry_run_rebalance_window={**_evidence()["paper_or_dry_run_rebalance_window"], "window_count": 1})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("paper_or_dry_run_rebalance_window.window_count must be >= 3" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_bias_control_flags():
    payload = _evidence(
        walk_forward_backtest={**_evidence()["walk_forward_backtest"], "lookahead_bias_controls": False}
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("walk_forward_backtest.lookahead_bias_controls" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_section_evidence_uri():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "evidence_uri": "",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("production_snapshot_source_audit.evidence_uri is required" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_section_evidence_generated_at():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "evidence_generated_at": "",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.evidence_generated_at is required" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_bad_artifact_snapshot_sha256():
    payload = _evidence(artifact_pack_validation={**_evidence()["artifact_pack_validation"], "snapshot_sha256": "abc"})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("artifact_pack_validation.snapshot_sha256 must be a 64-character hex sha256" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_mutable_artifact_release_id():
    payload = _evidence(artifact_pack_validation={**_evidence()["artifact_pack_validation"], "artifact_release_id": "latest"})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("artifact_pack_validation.artifact_release_id must be immutable" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_unstable_published_artifact_uri():
    payload = _evidence(
        artifact_pack_validation={
            **_evidence()["artifact_pack_validation"],
            "published_manifest_uri": "hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("artifact_pack_validation.published_manifest_uri must be a stable URI" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_stale_evidence_generated_at():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "evidence_generated_at": "2026-04-01",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.evidence_generated_at is stale" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_future_evidence_generated_at():
    payload = _evidence(
        broker_permission_and_fee_verification={
            **_evidence()["broker_permission_and_fee_verification"],
            "evidence_generated_at": "2026-06-10",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("broker_permission_and_fee_verification.evidence_generated_at must not be after" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_rollout_cap_above_policy():
    payload = _evidence(runtime_rollout_plan={**_evidence()["runtime_rollout_plan"], "initial_capital_fraction": 0.50})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("runtime_rollout_plan.initial_capital_fraction exceeds" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_rollout_runbooks():
    payload = _evidence(
        runtime_rollout_plan={
            **_evidence()["runtime_rollout_plan"],
            "severe_weather_trading_runbook_ready": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("runtime_rollout_plan.severe_weather_trading_runbook_ready must be true" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_order_above_adv_cap():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "max_single_order_adv_fraction": 0.04,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.max_single_order_adv_fraction exceeds" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_minimum_dry_run_liquidity():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "median_daily_turnover_hkd": 10_000_000,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.median_daily_turnover_hkd must be >= 20000000" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_execution_capacity_flags():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "odd_lot_avoidance_verified": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.odd_lot_avoidance_verified must be true" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_missing_profile_specific_source_audit():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "dividend_history": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("production_snapshot_source_audit.dividend_history must be true" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_quality_yield_trap_controls():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "dividend_yield_trap_controls": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "production_snapshot_source_audit.dividend_yield_trap_controls must be true" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_requires_production_source_provenance_uri():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "production_source_uri": "",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("production_snapshot_source_audit.production_source_uri is required" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_reversed_production_source_coverage():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "source_coverage_start": "2026-01-01",
            "source_coverage_end": "2025-12-31",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("source_coverage_end must not be before source_coverage_start" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_unstable_production_source_quality_report_uri():
    payload = _evidence(
        production_snapshot_source_audit={
            **_evidence()["production_snapshot_source_audit"],
            "source_quality_report_uri": "source-quality.json",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "production_snapshot_source_audit.source_quality_report_uri must be a stable URI" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_rejects_unstable_evidence_uri():
    payload = _evidence(
        artifact_pack_validation={
            **_evidence()["artifact_pack_validation"],
            "evidence_uri": "artifact-pack-passed",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("artifact_pack_validation.evidence_uri must be a stable URI" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_secret_bearing_evidence_uri():
    payload = _evidence(
        broker_permission_and_fee_verification={
            **_evidence()["broker_permission_and_fee_verification"],
            "evidence_uri": "https://evidence.example/hk/broker-fees.json?signature=secret",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("must not contain secret-like query parameters" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_notification_event_type():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "notification_event_type": "hk_runtime_live_enablement_dry_run",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("notification_event_type must be 'hk_snapshot_live_enablement_dry_run'" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_bilingual_notification():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "notification_locale_zh_hans": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("notification_locale_zh_hans must be true" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_unstable_notification_delivery_log_uri():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "notification_delivery_log_uri": "notifications/20260602-dryrun.json",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("notification_delivery_log_uri must be a stable URI" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_dry_run_session_id():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "dry_run_session_id": "",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.dry_run_session_id is required" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_order_preview_sha256():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "raw_order_preview_sha256": "not-a-sha",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "platform_dry_run_order_preview.raw_order_preview_sha256 must be a 64-character hex sha256" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_rejects_unstable_quote_snapshot_uri():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "quote_snapshot_uri": "order-preview/quote-snapshot.json",
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("platform_dry_run_order_preview.quote_snapshot_uri must be a stable URI" in error for error in result["errors"])


def test_validate_live_enablement_evidence_requires_broker_fee_reconciliation():
    payload = _evidence(
        platform_dry_run_order_preview={
            **_evidence()["platform_dry_run_order_preview"],
            "fee_breakdown_reconciled_to_broker_preview": False,
        }
    )

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any(
        "platform_dry_run_order_preview.fee_breakdown_reconciled_to_broker_preview must be true" in error
        for error in result["errors"]
    )


def test_validate_live_enablement_evidence_rejects_missing_operator_approval():
    payload = _evidence(risk_approval={**_evidence()["risk_approval"], "operator_approved": False})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("risk_approval.operator_approved" in error for error in result["errors"])


def test_validate_live_enablement_evidence_rejects_missing_approval_reference():
    payload = _evidence(risk_approval={**_evidence()["risk_approval"], "approval_reference": ""})

    result = validate_live_enablement_evidence(payload)

    assert result["live_enablement_allowed"] is False
    assert any("risk_approval.approval_reference is required" in error for error in result["errors"])


def test_validate_live_enablement_evidence_cli_json(tmp_path):
    evidence_file = tmp_path / "evidence.json"
    evidence_file.write_text(json.dumps(_evidence()), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_equity_snapshot_pipelines.live_enablement_evidence",
            "--evidence-file",
            str(evidence_file),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["live_enablement_allowed"] is True
    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert "dividend_history" in payload["production_source_audit_policy"]["required_boolean_fields"]
    assert payload["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert payload["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert payload["execution_capacity_policy"]["required"] is True
    assert payload["rollout_risk_policy"]["required"] is True
    assert payload["notification_audit_policy"]["required"] is True
    assert payload["dry_run_order_preview_policy"]["required"] is True
    assert payload["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )


def test_print_live_enablement_evidence_template_cli():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_equity_snapshot_pipelines.live_enablement_evidence",
            "--print-template",
            "--profile",
            "hk_low_vol_dividend_quality",
            "--platform",
            "ibkr",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality"
    assert payload["platform"] == "ibkr"
    assert payload["template_status"] == "pending_operator_evidence"
    assert payload["evidence_uri_policy"]["required"] is True
    assert payload["evidence_freshness_policy"]["required"] is True
    assert payload["execution_capacity_policy"]["max_rebalance_adv_fraction"] == 0.10
    assert payload["rollout_risk_policy"]["required"] is True
    assert payload["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert payload["dry_run_order_preview_policy"]["required"] is True
    assert payload["quality_yield_live_enablement_policy"]["required"] is True
    assert payload["platform_dry_run_order_preview"]["raw_order_preview_uri"] == ""
