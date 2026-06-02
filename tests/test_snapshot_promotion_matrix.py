from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.contracts import list_profile_contracts
from hk_equity_snapshot_pipelines.snapshot_promotion_matrix import (
    BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION,
    BACKTEST_VALIDATION_POLICY_VERSION,
    FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION,
    FUTURE_RESEARCH_BACKLOG_VERSION,
    FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION,
    MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION,
    MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION,
    POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION,
    QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION,
    QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION,
    SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION,
    SNAPSHOT_PROMOTION_GATE,
    build_baseline_rotation_live_enablement_policy,
    build_future_research_backlog,
    build_future_research_live_enablement_policy,
    build_factor_mix_live_enablement_policy,
    build_momentum_live_enablement_comparison,
    build_momentum_live_enablement_policy,
    build_policy_value_live_enablement_policy,
    build_quality_growth_live_enablement_policy,
    build_quality_yield_live_enablement_policy,
    build_snapshot_promotion_matrix,
    build_snapshot_promotion_row,
    build_special_situation_live_enablement_policy,
    list_snapshot_promotion_candidates,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "print_snapshot_promotion_matrix.py"


def test_snapshot_promotion_matrix_covers_every_contract_profile():
    matrix = build_snapshot_promotion_matrix()
    contract_profiles = {contract.profile for contract in list_profile_contracts()}
    matrix_profiles = {row["profile"] for row in matrix["profiles"]}

    assert matrix_profiles == contract_profiles
    assert matrix["profile_count"] == len(contract_profiles)
    assert matrix["runtime_enabled_count"] == 0
    assert matrix["blocked_profile_count"] == matrix["profile_count"]
    assert matrix["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert "signature=" in matrix["evidence_uri_policy"]["rejected_query_markers"]
    assert matrix["artifact_provenance_policy"]["required"] is True
    assert matrix["backtest_validation_policy"]["policy_version"] == BACKTEST_VALIDATION_POLICY_VERSION
    assert matrix["backtest_validation_policy"]["live_enablement_allowed_without_policy_evidence"] is False
    assert matrix["backtest_validation_policy"]["max_allowed_drawdown"] == 0.30
    assert matrix["backtest_validation_policy"]["min_return_to_drawdown_ratio"] == 0.50
    assert matrix["backtest_validation_policy"]["min_required_oos_fold_count"] == 3
    assert matrix["backtest_validation_policy"]["max_single_period_return_contribution"] == 0.60
    assert "point_in_time_inputs_only" in matrix["backtest_validation_policy"]["required_controls"]
    assert "no_full_sample_parameter_selection" in matrix["backtest_validation_policy"]["required_controls"]
    assert "rolling_oos_fold_drawdown_controls" in matrix["backtest_validation_policy"]["required_controls"]
    assert "regime_stress_and_liquidity_shock_controls" in matrix["backtest_validation_policy"]["required_controls"]
    assert "max_drawdown_at_or_below_30_percent" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "adv_capacity_spread_board_lot_and_odd_lot_limits" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "each_oos_fold_max_drawdown_at_or_below_30_percent" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "cash_leverage_short_borrow_and_margin_constraints" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "fee_slippage_spread_sensitivity_stays_profitable" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "annual_return_to_max_drawdown_ratio_at_or_above_50_percent" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "minimum_three_independent_oos_folds" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "single_period_return_contribution_at_or_below_60_percent" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "cross_strategy_correlation_and_aggregate_drawdown_budget_limits" in (
        matrix["backtest_validation_policy"]["required_risk_constraints"]
    )
    assert "oos_fold_count" in matrix["backtest_validation_policy"]["required_metrics"]
    assert "max_single_period_return_contribution" in matrix["backtest_validation_policy"]["required_metrics"]
    assert "annual_return_to_max_drawdown_ratio" in matrix["backtest_validation_policy"]["required_metrics"]
    assert "data_vendor_reconciliation_and_missingness_controls" in (
        matrix["backtest_validation_policy"]["required_controls"]
    )
    assert "tail_loss_time_underwater_and_recovery_controls" in (
        matrix["backtest_validation_policy"]["required_controls"]
    )
    assert "using_future_financials_estimates_or_index_changes_before_effective_timestamp" in (
        matrix["backtest_validation_policy"]["reject_criteria"]
    )
    assert "rolling_or_oos_fold_drawdown_above_30_percent" in matrix["backtest_validation_policy"]["reject_criteria"]
    assert "fee_slippage_spread_stress_turns_excess_return_non_positive" in (
        matrix["backtest_validation_policy"]["reject_criteria"]
    )
    assert "annual_return_to_max_drawdown_ratio_below_50_percent" in (
        matrix["backtest_validation_policy"]["reject_criteria"]
    )
    assert "fewer_than_three_independent_oos_folds" in matrix["backtest_validation_policy"]["reject_criteria"]
    assert "single_period_return_contribution_above_60_percent" in (
        matrix["backtest_validation_policy"]["reject_criteria"]
    )
    assert "gross_return_only_backtest_without_net_cost_validation" in (
        matrix["backtest_validation_policy"]["reject_criteria"]
    )
    assert matrix["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert "artifact_publication_provenance" in matrix["generic_required_next_evidence"]
    assert "production_source_uri_and_quality_report_provenance" in matrix["generic_required_next_evidence"]
    assert "fresh_section_evidence_generated_at" in matrix["generic_required_next_evidence"]
    assert "execution_capacity_and_liquidity_limits" in matrix["generic_required_next_evidence"]
    assert "dry_run_order_preview_artifact_provenance" in matrix["generic_required_next_evidence"]
    assert "staged_rollout_tripwires_and_rollback" in matrix["generic_required_next_evidence"]
    assert "bilingual_notification_delivery_log" in matrix["generic_required_next_evidence"]
    assert "backtest_validation_policy_evidence" in matrix["generic_required_next_evidence"]
    assert "point_in_time_no_lookahead_and_no_overfit_controls" in matrix["generic_required_next_evidence"]
    assert "minimum_three_independent_oos_folds" in matrix["generic_required_next_evidence"]
    assert "single_period_return_contribution_below_60_percent" in matrix["generic_required_next_evidence"]
    assert "per_fold_drawdown_parameter_stability_and_regime_stress_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["execution_capacity_policy"]["max_single_order_adv_fraction"] == 0.025
    assert matrix["rollout_risk_policy"]["max_initial_capital_fraction"] == 0.25
    assert matrix["notification_audit_policy"]["schema_version"] == "hk_live_enablement_notification.v1"
    assert matrix["dry_run_order_preview_policy"]["required"] is True
    assert matrix["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "baseline_rotation_ablation_hsi_constituent_and_execution_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["quality_yield_live_enablement_policy"]["policy_version"] == (
        QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "dividend_yield_trap_and_payout_cut_window" in (
        matrix["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "abnormally_high_yield_price_crash_bottom_decile_window" in (
        matrix["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "high_dividend_screened_financial_soundness_and_high_volatility_exclusion_window" in (
        matrix["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "free_cash_flow_restatement_reporting_date_and_sector_normalization_window" in (
        matrix["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert "fcf_formula_cash_flow_statement_lineage_history" in (
        matrix["quality_yield_live_enablement_policy"]["required_data_provenance"]
    )
    assert "forecast_dividend_yield_estimate_history" in (
        matrix["quality_yield_live_enablement_policy"]["required_data_provenance"]
    )
    assert "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe" in (
        matrix["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert any(
        "methodology-sp-access-hk-fcf-50-index.pdf" in url
        for url in matrix["quality_yield_live_enablement_policy"]["source_reference_urls"]
    )
    assert any(
        "forecast-dividend-yield-strategy" in url
        for url in matrix["quality_yield_live_enablement_policy"]["source_reference_urls"]
    )
    assert matrix["momentum_live_enablement_comparison"]["comparison_version"] == (
        MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION
    )
    assert matrix["momentum_live_enablement_policy"]["policy_version"] == MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION
    assert "current_price_to_52_week_high_history" in matrix["momentum_live_enablement_policy"]["required_data_provenance"]
    assert matrix["quality_growth_live_enablement_policy"]["policy_version"] == (
        QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "quality_growth_ablation_growth_deceleration_and_low_vol_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["factor_mix_live_enablement_policy"]["policy_version"] == FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION
    assert "factor_mix_risk_parity_ablation_and_factor_volatility_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["policy_value_live_enablement_policy"]["policy_version"] == (
        POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "policy_value_government_ownership_and_concentration_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["special_situation_live_enablement_policy"]["policy_version"] == (
        SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "hkex_stock_connect_turnover_and_holding_history" in (
        matrix["special_situation_live_enablement_policy"]["required_data_provenance"]
    )
    assert "special_situation_signal_decay_crowding_and_calendar_alignment_controls" in (
        matrix["generic_required_next_evidence"]
    )
    assert matrix["future_research_backlog"]["backlog_version"] == FUTURE_RESEARCH_BACKLOG_VERSION
    assert matrix["future_research_backlog"]["status"] == "research_only_not_scaffolded"
    assert matrix["future_research_backlog"]["future_research_live_enablement_policy"]["policy_version"] == (
        FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert matrix["recommended_live_enablement_sequence"] == [
        row["profile"] for row in sorted(matrix["profiles"], key=lambda item: item["priority"])
    ]
    assert all(row["live_enablement_gate"] == SNAPSHOT_PROMOTION_GATE for row in matrix["profiles"])


def test_first_snapshot_candidates_prioritize_low_turnover_quality_styles():
    matrix = build_snapshot_promotion_matrix()

    assert matrix["first_snapshot_candidates"] == [
        "hk_low_vol_dividend_quality",
        "hk_shareholder_yield_quality",
        "hk_free_cash_flow_quality",
    ]


def test_blue_chip_baseline_row_carries_active_policy_and_hsi_execution_controls():
    row = build_snapshot_promotion_row("hk_blue_chip_snapshot")

    assert row["profile"] == "hk_blue_chip_leader_rotation"
    assert row["priority"] == 12
    assert row["promotion_bucket"] == "baseline_snapshot_candidate"
    assert row["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert row["backtest_validation_policy"]["policy_version"] == BACKTEST_VALIDATION_POLICY_VERSION
    assert "signal_timestamp_before_trade_timestamp" in row["backtest_validation_policy"]["required_controls"]
    assert "blue_chip_rotation_vs_hsi_tracker_same_universe" in (
        row["baseline_rotation_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "hsi_constituent_history" in row["production_data_dependencies"]
    assert "current_price_to_52_week_high_history" in row["production_data_dependencies"]
    assert "hsi_constituent_history" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "board_lot_vcm_and_trading_session_rule_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("IM_hsie.pdf" in url for url in row["research_evidence_urls"])
    assert any("Trading-Mechanism" in url for url in row["research_evidence_urls"])
    assert any("VCM" in url for url in row["research_evidence_urls"])
    assert any("HSI constituent" in evidence for evidence in row["profile_specific_next_evidence"])


def test_baseline_rotation_live_enablement_policy_requires_hsi_and_execution_provenance():
    policy = build_baseline_rotation_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION
    assert "blue_chip_rotation_vs_hsi_tracker_same_universe" in policy["required_ablation_tests"]
    assert "blue_chip_baseline_vs_liquid_momentum_quality_same_universe" in policy["required_ablation_tests"]
    assert "sector_neutral_vs_sector_unconstrained_leader_weights" in policy["required_ablation_tests"]
    assert "hsi_hstech_leadership_reversal_window" in policy["required_stress_tests"]
    assert "vcm_cas_and_market_session_execution_window" in policy["required_stress_tests"]
    assert "point_in_time_hsi_constituent_history" in policy["required_data_provenance"]
    assert "board_lot_vcm_and_trading_session_rule_history" in policy["required_data_provenance"]
    assert any("IM_hsie.pdf" in url for url in policy["source_reference_urls"])
    assert any("Trading-Mechanism" in url for url in policy["source_reference_urls"])
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"


def test_low_vol_dividend_row_carries_hshylv_source_audit_controls():
    row = build_snapshot_promotion_row("hk_low_vol_dividend_quality")

    assert row["priority"] == 1
    assert row["promotion_bucket"] == "first_snapshot_candidate"
    assert "southbound_eligibility_history" in row["production_data_dependencies"]
    assert "forecast_dividend_yield_estimate_history" in row["production_data_dependencies"]
    assert "three_year_cash_dividend_record" in row["production_data_dependencies"]
    assert "one_year_high_volatility_exclusion" in row["production_data_dependencies"]
    assert "high_dividend_financial_soundness_screen" in row["production_data_dependencies"]
    assert "sp_access_hk_low_vol_high_div_methodology" in row["production_data_dependencies"]
    assert "price_crash_bottom_decile_screen" in row["production_data_dependencies"]
    assert "three_year_cash_dividend_record_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_estimate_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_vs_trailing_yield_benchmark_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "price_crash_bottom_decile_screen_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "high_dividend_financial_soundness_screen_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sp_access_hk_low_vol_high_div_methodology_and_constituent_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("hshylve.pdf" in url for url in row["research_evidence_urls"])
    assert any("IM_hshylve.pdf" in url for url in row["research_evidence_urls"])
    assert any("hsschyse.pdf" in url for url in row["research_evidence_urls"])
    assert any("IM_hsschkye.pdf" in url for url in row["research_evidence_urls"])
    assert any("sp-access-hong-kong-low-volatility-high-dividend-index" in url for url in row["research_evidence_urls"])
    assert any("forecast-dividend-yield-strategy" in url for url in row["research_evidence_urls"])
    assert any(
        "sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index" in url
        for url in row["research_evidence_urls"]
    )
    assert any("S&P Access HK Low Volatility High Dividend" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("forecast dividend yield versus trailing dividend yield" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("price-crash screens" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("financial-soundness screens" in evidence for evidence in row["profile_specific_next_evidence"])


def test_shareholder_yield_row_carries_hkex_evidence_and_turnover_cap():
    row = build_snapshot_promotion_row("hk_capital_return_quality")

    assert row["profile"] == "hk_shareholder_yield_quality"
    assert row["priority"] == 2
    assert row["promotion_bucket"] == "first_snapshot_candidate"
    assert row["recommended_live_enablement_stage"] == "production_data_audit_and_walk_forward_first"
    assert "production snapshot source" in row["next_live_enablement_action"]
    assert row["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.0
    assert "hkex_buyback_disclosure_history" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "hkex_next_day_share_repurchase_return_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_estimate_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_vs_trailing_yield_benchmark_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "treasury_share_moratorium_blackout_and_connected_person_controls" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "post_buyback_new_issue_convertible_and_public_float_review" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("sharerepur" in url for url in row["production_source_audit_policy"]["source_reference_urls"])
    assert any("repurchase-securities-and-treasury-shares" in url for url in row["production_source_audit_policy"]["source_reference_urls"])
    assert any("240412news" in url for url in row["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "forecast-dividend-yield-strategy" in url
        for url in row["production_source_audit_policy"]["source_reference_urls"]
    )
    assert row["evidence_uri_policy"]["required"] is True
    assert "published_snapshot_uri" in row["artifact_provenance_policy"]["required_uri_fields"]
    assert "production_source_uri" in row["production_source_audit_policy"]["required_uri_fields"]
    assert row["evidence_freshness_policy"]["max_allowed_age_days_by_section"]["artifact_pack_validation"] == 14
    assert row["execution_capacity_policy"]["min_median_daily_turnover_hkd"] == 20_000_000
    assert row["rollout_risk_policy"]["required"] is True
    assert row["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert row["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert row["quality_yield_live_enablement_policy"]["policy_version"] == QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION
    assert "buyback_yield_raw_vs_share_count_reduction_adjusted" in (
        row["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe" in (
        row["quality_yield_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "treasury_share_moratorium_blackout_and_connected_person_window" in (
        row["quality_yield_live_enablement_policy"]["required_stress_tests"]
    )
    assert any("hkex.com.hk" in url for url in row["research_evidence_urls"])
    assert any("entiresection/498" in url for url in row["research_evidence_urls"])
    assert any("sp-access-hong-kong-dividend-free-cash-flow-index" in url for url in row["research_evidence_urls"])
    assert any("forecast-dividend-yield-strategy" in url for url in row["research_evidence_urls"])
    assert any("share-count" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("forecast dividend yield versus trailing dividend yield" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("next-day share-repurchase returns" in evidence for evidence in row["profile_specific_next_evidence"])
    assert any("post-buyback financing" in evidence for evidence in row["profile_specific_next_evidence"])


def test_quality_yield_live_enablement_policy_requires_ablation_stress_and_source_provenance():
    policy = build_quality_yield_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION
    assert "low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe" in policy["required_ablation_tests"]
    assert "sp_access_low_vol_high_div_vs_hshylv_same_universe" in policy["required_ablation_tests"]
    assert "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe" in policy["required_ablation_tests"]
    assert "dividend_yield_trap_and_payout_cut_window" in policy["required_stress_tests"]
    assert "abnormally_high_yield_price_crash_bottom_decile_window" in policy["required_stress_tests"]
    assert "high_dividend_screened_financial_soundness_and_high_volatility_exclusion_window" in (
        policy["required_stress_tests"]
    )
    assert "forecast_dividend_cut_and_estimate_revision_window" in policy["required_stress_tests"]
    assert "forecast_dividend_financials_active_exposure_concentration_window" in policy["required_stress_tests"]
    assert "forecast_dividend_yield_estimate_history" in policy["required_data_provenance"]
    assert "forecast_dividend_yield_vs_trailing_yield_benchmark_history" in policy["required_data_provenance"]
    assert "dividend_forecast_vendor_methodology_and_estimate_revision_history" in policy["required_data_provenance"]
    assert "three_year_cash_dividend_record_and_payout_ratio_history" in policy["required_data_provenance"]
    assert "price_crash_bottom_decile_screen_history" in policy["required_data_provenance"]
    assert "one_year_high_volatility_exclusion_history" in policy["required_data_provenance"]
    assert "high_dividend_financial_soundness_screen_history" in policy["required_data_provenance"]
    assert "sp_access_hk_low_vol_high_div_methodology_and_constituent_history" in (
        policy["required_data_provenance"]
    )
    assert "hsi_vs_sp_low_vol_high_div_rebalance_and_capping_history" in policy["required_data_provenance"]
    assert "hkex_buyback_disclosure_and_share_count_history" in policy["required_data_provenance"]
    assert "hkex_next_day_share_repurchase_return_history" in policy["required_data_provenance"]
    assert "treasury_share_moratorium_blackout_and_connected_person_controls" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("forecast-dividend-yield-strategy" in url for url in policy["source_reference_urls"])
    assert any("hshylve.pdf" in url for url in policy["source_reference_urls"])
    assert any("IM_hshylve.pdf" in url for url in policy["source_reference_urls"])
    assert any("hsschyse.pdf" in url for url in policy["source_reference_urls"])
    assert any("IM_hsschkye.pdf" in url for url in policy["source_reference_urls"])
    assert any("navigating-dividend-yield" in url for url in policy["source_reference_urls"])
    assert any("sp-access-hong-kong-low-volatility-high-dividend-index" in url for url in policy["source_reference_urls"])
    assert any("sp-low-volatility-high-dividend-indices-methodology" in url for url in policy["source_reference_urls"])
    assert any(
        "sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index" in url
        for url in policy["source_reference_urls"]
    )
    assert any("sharerepur" in url for url in policy["source_reference_urls"])
    assert any("repurchase-securities-and-treasury-shares" in url for url in policy["source_reference_urls"])


def test_momentum_rows_carry_current_hsi_momentum_methodology_and_later_stage():
    row = build_snapshot_promotion_row("hk_residual_momentum_quality")

    assert row["priority"] == 7
    assert row["promotion_bucket"] == "momentum_snapshot_candidate"
    assert row["recommended_live_enablement_stage"] == "momentum_research_after_quality_candidates"
    assert "Compare residual, liquid, and composite momentum variants" in row["next_live_enablement_action"]
    assert row["momentum_live_enablement_comparison"]["momentum_priority"] == 1
    assert row["momentum_live_enablement_comparison"]["momentum_role"] == (
        "closest_to_us_momentum_factor_stock_selection"
    )
    assert "residual_mom_12_1" in row["momentum_live_enablement_comparison"]["signal_inputs"]
    assert row["momentum_live_enablement_comparison"]["momentum_live_enablement_policy"]["required"] is True
    assert "quality_screen_on_vs_quality_screen_off" in (
        row["momentum_live_enablement_comparison"]["momentum_live_enablement_policy"]["required_ablation_tests"]
    )
    assert any(
        "same survivorship-safe universe" in item
        for item in row["momentum_live_enablement_comparison"]["pre_live_comparison_evidence"]
    )
    assert "residual_model_reproducible" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "momentum_6m_12m_one_month_skip_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "risk_adjusted_momentum_volatility_normalization_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "momentum_turnover_buffer_and_capacity_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("IM_hssbisme.pdf" in url for url in row["production_source_audit_policy"]["source_reference_urls"])
    assert any("msci.com/indexes/index/711028" in url for url in row["production_source_audit_policy"]["source_reference_urls"])
    assert any("MSCI_Momentum_Indexes_Methodology" in url for url in row["research_evidence_urls"])
    assert any("IM_hssbisme.pdf" in url for url in row["research_evidence_urls"])
    assert any("6/12-month one-month-skip" in item for item in row["profile_specific_next_evidence"])


def test_momentum_live_enablement_policy_requires_ablation_stress_and_order_preview_provenance():
    policy = build_momentum_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION
    assert "residual_vs_liquid_vs_composite_same_universe" in policy["required_ablation_tests"]
    assert "msci_6_12_month_vs_hsi_52_week_high_descriptor_same_universe" in policy["required_ablation_tests"]
    assert "one_month_reversal_skip_vs_no_skip_momentum_signal" in policy["required_ablation_tests"]
    assert "hsi_hstech_sharp_reversal_window" in policy["required_stress_tests"]
    assert "momentum_turnover_spike_and_rebalance_buffer_window" in policy["required_stress_tests"]
    assert "point_in_time_industry_classification" in policy["required_data_provenance"]
    assert "risk_adjusted_momentum_volatility_normalization_history" in policy["required_data_provenance"]
    assert "msci_hk_and_hk_listed_southbound_momentum_benchmark_history" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("hsscsme.pdf" in url for url in policy["source_reference_urls"])
    assert any("momentum-indexes" in url for url in policy["source_reference_urls"])
    assert any("711028" in url for url in policy["source_reference_urls"])


def test_momentum_live_enablement_comparison_prioritizes_residual_before_raw_and_composite():
    comparison = build_momentum_live_enablement_comparison()

    assert comparison["comparison_version"] == MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION
    assert comparison["momentum_live_enablement_policy"]["policy_version"] == MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION
    assert comparison["recommended_first_momentum_candidate"] == "hk_residual_momentum_quality"
    assert comparison["must_compare_before_live_enablement"] is True
    assert [row["profile"] for row in comparison["profiles"]] == [
        "hk_residual_momentum_quality",
        "hk_liquid_momentum_quality",
        "hk_composite_factor_quality_value_momentum",
    ]
    assert comparison["profiles"][0]["momentum_role"] == "closest_to_us_momentum_factor_stock_selection"
    assert "residual_mom_12_1" in comparison["profiles"][0]["signal_inputs"]
    assert "mom_12_1" in comparison["profiles"][1]["signal_inputs"]
    assert "momentum_score" in comparison["profiles"][2]["signal_inputs"]
    assert any("hsi.com.hk/solutions/factor-indexes" in url for url in comparison["external_evidence_urls"])
    assert any("msci.com/indexes/group/momentum-indexes" in url for url in comparison["external_evidence_urls"])
    assert any("one-month-skip" in item for item in comparison["profiles"][0]["pre_live_comparison_evidence"])
    assert any("factor ablation" in item for item in comparison["common_pre_live_requirements"])
    assert any("dry-run order-preview artifact provenance" in item for item in comparison["common_pre_live_requirements"])


def test_special_situation_live_enablement_policy_requires_signal_decay_calendar_and_crowding_controls():
    policy = build_special_situation_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION
    assert "signal_decay_window_and_rebalance_frequency_ablation" in policy["required_ablation_tests"]
    assert "southbound_top10_turnover_vs_ccass_holding_change_same_universe" in policy["required_ablation_tests"]
    assert "ah_premium_extreme_level_vs_hsi_trough_timing_ablation" in policy["required_ablation_tests"]
    assert "ah_smart_share_class_switch_vs_long_only_h_share_overlay" in policy["required_ablation_tests"]
    assert "index_add_delete_vs_review_candidate_probability_same_universe" in policy["required_ablation_tests"]
    assert "announcement_close_vs_effective_close_execution_window_ablation" in policy["required_ablation_tests"]
    assert "market_on_close_vs_next_open_execution_window_ablation" in policy["required_ablation_tests"]
    assert "official_schedule_vs_press_release_event_source_reconciliation" in policy["required_ablation_tests"]
    assert "proforma_weighted_add_delete_vs_equal_weight_event_trade_ablation" in policy["required_ablation_tests"]
    assert "a_h_close_time_fx_and_exchange_holiday_misalignment_window" in policy["required_stress_tests"]
    assert "ah_premium_extreme_level_false_reversal_window" in policy["required_stress_tests"]
    assert "a_share_shorting_access_settlement_and_capital_control_constraint_window" in (
        policy["required_stress_tests"]
    )
    assert "southbound_realtime_data_suppression_and_top10_only_window" in policy["required_stress_tests"]
    assert "ccass_southbound_shareholding_reporting_lag_and_eligibility_mismatch_window" in (
        policy["required_stress_tests"]
    )
    assert "effective_date_market_on_close_auction_and_passive_flow_window" in policy["required_stress_tests"]
    assert "hsi_fast_entry_suspension_and_buffer_rule_exception_window" in policy["required_stress_tests"]
    assert "closing_auction_random_close_and_price_limit_execution_window" in policy["required_stress_tests"]
    assert "review_schedule_change_and_delayed_press_release_window" in policy["required_stress_tests"]
    assert "cas_random_close_price_limit_and_order_rejection_window" in policy["required_stress_tests"]
    assert "passive_flow_closing_auction_liquidity_gap_window" in policy["required_stress_tests"]
    assert "official_index_review_announcement_and_effective_date_history" in policy["required_data_provenance"]
    assert "hsi_quarterly_review_schedule_and_cutoff_history" in policy["required_data_provenance"]
    assert "hsi_index_methodology_and_operation_guide_version_history" in policy["required_data_provenance"]
    assert "hsi_review_schedule_file_version_and_effective_date_history" in policy["required_data_provenance"]
    assert "hsi_next_review_notice_timestamp_and_scope_history" in policy["required_data_provenance"]
    assert "hsi_review_result_press_release_history" in policy["required_data_provenance"]
    assert "hsi_review_result_timestamp_constituent_weight_and_proforma_history" in policy["required_data_provenance"]
    assert "hsi_constituent_added_deleted_effective_date_history" in policy["required_data_provenance"]
    assert "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history" in policy["required_data_provenance"]
    assert "hsi_fast_entry_suspension_and_buffer_rule_exception_history" in policy["required_data_provenance"]
    assert "market_on_close_order_type_price_limit_and_random_close_policy" in policy["required_data_provenance"]
    assert "hkex_cas_order_type_random_close_price_limit_and_rejection_history" in policy["required_data_provenance"]
    assert "closing_auction_volume_spread_and_passive_flow_history" in policy["required_data_provenance"]
    assert "closing_auction_imbalance_passive_flow_and_spread_history" in policy["required_data_provenance"]
    assert "ccass_southbound_shareholding_percent_issued_history" in policy["required_data_provenance"]
    assert "southbound_flow_raw_vs_vendor_reconciliation" in policy["required_data_provenance"]
    assert "ah_premium_index_constituent_and_price_ratio_history" in policy["required_data_provenance"]
    assert "ah_smart_share_class_switch_threshold_history" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("Stock-Connect/Statistics/Historical-Daily" in url for url in policy["source_reference_urls"])
    assert any("mutualmarket.aspx?t=hk" in url for url in policy["source_reference_urls"])
    assert any("2404122news" in url for url in policy["source_reference_urls"])
    assert any("ahpremiume.pdf" in url for url in policy["source_reference_urls"])
    assert any("20240124T000000.pdf" in url for url in policy["source_reference_urls"])
    assert any("20210914T000000.pdf" in url for url in policy["source_reference_urls"])
    assert any("H50066_h50066hbooken_EN.pdf" in url for url in policy["source_reference_urls"])
    assert any("index_methodology_guide_e.pdf" in url for url in policy["source_reference_urls"])
    assert any("index_operation_guide_e.pdf" in url for url in policy["source_reference_urls"])
    assert any("is_update.xlsx" in url for url in policy["source_reference_urls"])
    assert any("20260102T163000.pdf" in url for url in policy["source_reference_urls"])
    assert any("20260213T174500.pdf" in url for url in policy["source_reference_urls"])
    assert any("20260522T174500.pdf" in url for url in policy["source_reference_urls"])
    assert any("Trading/CAS" in url for url in policy["source_reference_urls"])


def test_special_situation_rows_carry_profile_specific_policy_and_controls():
    southbound = build_snapshot_promotion_row("hk_southbound_momentum")
    ah_premium = build_snapshot_promotion_row("hk_ah_premium")
    index_event = build_snapshot_promotion_row("hk_index_event")

    assert southbound["special_situation_live_enablement_policy"]["policy_version"] == (
        SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "southbound_flow_vs_price_momentum_same_universe" in (
        southbound["special_situation_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "stock_connect_holding_history" in southbound["production_source_audit_policy"]["required_boolean_fields"]
    assert "ccass_southbound_shareholding_percent_issued_history" in (
        southbound["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "southbound_flow_raw_vs_vendor_reconciliation" in (
        southbound["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("mutualmarket.aspx?t=hk" in url for url in southbound["research_evidence_urls"])
    assert any("abstract_id=5128472" in url for url in southbound["research_evidence_urls"])
    assert any("top-10 turnover" in item for item in southbound["profile_specific_next_evidence"])
    assert any("flow signal-decay" in item for item in southbound["profile_specific_next_evidence"])
    assert ah_premium["special_situation_live_enablement_policy"]["policy_version"] == (
        SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "ah_close_time_alignment_policy" in ah_premium["production_source_audit_policy"]["required_boolean_fields"]
    assert "ah_price_ratio_formula_and_market_cap_weight_history" in (
        ah_premium["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "a_share_access_shorting_settlement_and_fx_constraint_review" in (
        ah_premium["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("20240124T000000.pdf" in url for url in ah_premium["research_evidence_urls"])
    assert any("20210914T000000.pdf" in url for url in ah_premium["research_evidence_urls"])
    assert any("H50066_h50066hbooken_EN.pdf" in url for url in ah_premium["research_evidence_urls"])
    assert any("AH price ratio" in item for item in ah_premium["profile_specific_next_evidence"])
    assert any("share-class switch" in item for item in ah_premium["profile_specific_next_evidence"])
    assert any("FX source" in item for item in ah_premium["profile_specific_next_evidence"])
    assert index_event["special_situation_live_enablement_policy"]["policy_version"] == (
        SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "event_crowding_slippage_controls" in index_event["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_quarterly_review_schedule_and_cutoff_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_review_result_press_release_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_review_result_timestamp_constituent_weight_and_proforma_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_fast_entry_suspension_and_buffer_rule_exception_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "market_on_close_order_type_price_limit_and_random_close_policy" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hkex_cas_order_type_random_close_price_limit_and_rejection_history" in (
        index_event["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("is_update.xlsx" in url for url in index_event["research_evidence_urls"])
    assert any("20260522T174500.pdf" in url for url in index_event["research_evidence_urls"])
    assert any("Trading/CAS" in url for url in index_event["research_evidence_urls"])
    assert any("pro-forma" in item for item in index_event["profile_specific_next_evidence"])
    assert any("market-on-close versus next-open" in item for item in index_event["profile_specific_next_evidence"])
    assert any("announcement-to-effective-date" in item for item in index_event["profile_specific_next_evidence"])
    assert any("fast-entry" in item for item in index_event["profile_specific_next_evidence"])
    assert any("Closing Auction Session" in item for item in index_event["profile_specific_next_evidence"])


def test_future_research_backlog_keeps_non_scaffolded_candidates_out_of_live_enablement():
    backlog = build_future_research_backlog()

    assert backlog["backlog_version"] == FUTURE_RESEARCH_BACKLOG_VERSION
    assert backlog["live_enablement_gate"] == "requires_new_snapshot_contract_and_production_evidence"
    assert backlog["future_research_live_enablement_policy"]["live_enablement_allowed"] is False
    assert "new_snapshot_profile_name_and_contract_version" in (
        backlog["future_research_live_enablement_policy"]["required_pre_scaffold_gates"]
    )
    assert backlog["candidate_count"] == 34
    assert backlog["candidates"][0]["profile_hint"] == "hk_earnings_revision_quality_overlay"
    assert backlog["candidates"][0]["scaffold_status"] == "research_only_not_scaffolded"
    assert any("earnings-revision-overlay" in url for url in backlog["candidates"][0]["source_reference_urls"])
    assert any("point_in_time_consensus_eps_estimate_history" in item for item in backlog["candidates"][0]["required_new_data"])
    assert backlog["candidates"][1]["profile_hint"] == "hk_low_size_quality_liquidity_premium"
    assert backlog["candidates"][1]["suggested_contract_type"] == "factor_snapshot"
    assert any("IM_hssbisse.pdf" in url for url in backlog["candidates"][1]["source_reference_urls"])
    assert any("free_float_market_cap" in item for item in backlog["candidates"][1]["required_new_data"])
    assert backlog["candidates"][2]["profile_hint"] == "hk_stock_connect_inclusion_event_flow"
    assert backlog["candidates"][2]["suggested_contract_type"] == "event_calendar_snapshot"
    assert any("eligible-stocks" in url.lower() for url in backlog["candidates"][2]["source_reference_urls"])
    assert any("stock_connect_eligible_security" in item for item in backlog["candidates"][2]["required_new_data"])
    assert backlog["candidates"][3]["profile_hint"] == "hk_short_selling_pressure_risk_overlay"
    assert backlog["candidates"][3]["suggested_contract_type"] == "factor_snapshot_overlay"
    assert any("Short-Selling-Turnover" in url for url in backlog["candidates"][3]["source_reference_urls"])
    assert any("short_ratio" in item for item in backlog["candidates"][3]["required_new_data"])
    assert backlog["candidates"][4]["profile_hint"] == "hk_director_dealing_disclosure_quality_overlay"
    assert backlog["candidates"][4]["suggested_contract_type"] == "factor_snapshot_overlay"
    assert any("Disclosure-of-Interests" in url for url in backlog["candidates"][4]["source_reference_urls"])
    assert any("disclosure_of_interests" in item for item in backlog["candidates"][4]["required_new_data"])
    assert any("director" in item for item in backlog["candidates"][4]["required_new_data"])
    assert backlog["candidates"][5]["profile_hint"] == "hk_dually_traded_liquid_reversal_overlay"
    assert backlog["candidates"][5]["suggested_contract_type"] == "factor_snapshot_overlay"
    assert any("pacfin" in url or "applec" in url for url in backlog["candidates"][5]["source_reference_urls"])
    assert any("dually_traded" in item for item in backlog["candidates"][5]["required_new_data"])
    assert any("vcm_cas_fee_slippage" in item for item in backlog["candidates"][5]["required_new_data"])
    assert backlog["candidates"][6]["profile_hint"] == "hk_earnings_announcement_drift_overlay"
    assert backlog["candidates"][6]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("hkexnews" in url.lower() or "4070" in url for url in backlog["candidates"][6]["source_reference_urls"])
    assert any("earnings_surprise" in item for item in backlog["candidates"][6]["required_new_data"])
    assert any("announcement_publication_timestamp" in item for item in backlog["candidates"][6]["required_new_data"])
    assert backlog["candidates"][7]["profile_hint"] == "hk_lottery_stock_risk_exclusion_overlay"
    assert backlog["candidates"][7]["suggested_contract_type"] == "factor_snapshot_overlay"
    assert any("Gambling_Hong_Kong" in url for url in backlog["candidates"][7]["source_reference_urls"])
    assert any("lottery_feature" in item for item in backlog["candidates"][7]["required_new_data"])
    assert any("max1_max5" in item for item in backlog["candidates"][7]["required_new_data"])
    assert backlog["candidates"][8]["profile_hint"] == "hk_equity_financing_dilution_risk_overlay"
    assert backlog["candidates"][8]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("13000929" in url for url in backlog["candidates"][8]["source_reference_urls"])
    assert any("180504news" in url for url in backlog["candidates"][8]["source_reference_urls"])
    assert any("placement" in item for item in backlog["candidates"][8]["required_new_data"])
    assert any("2018_rule_change" in item for item in backlog["candidates"][8]["required_new_data"])
    assert backlog["candidates"][9]["profile_hint"] == "hk_connected_transaction_governance_risk_overlay"
    assert backlog["candidates"][9]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("1008780" in url for url in backlog["candidates"][9]["source_reference_urls"])
    assert any("connected_transaction" in item for item in backlog["candidates"][9]["required_new_data"])
    assert any("independent_shareholder_approval" in item for item in backlog["candidates"][9]["required_new_data"])
    assert backlog["candidates"][10]["profile_hint"] == "hk_takeover_privatization_event_spread_overlay"
    assert backlog["candidates"][10]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("Takeovers-and-mergers" in url for url in backlog["candidates"][10]["source_reference_urls"])
    assert any("2926" in url for url in backlog["candidates"][10]["source_reference_urls"])
    assert any("offer_period" in item for item in backlog["candidates"][10]["required_new_data"])
    assert any("rule_3_7" in item for item in backlog["candidates"][10]["required_new_data"])
    assert backlog["candidates"][11]["profile_hint"] == "hk_distribution_ex_date_entitlement_overlay"
    assert backlog["candidates"][11]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("f_div.pdf" in url for url in backlog["candidates"][11]["source_reference_urls"])
    assert any("jfinan" in url for url in backlog["candidates"][11]["source_reference_urls"])
    assert any("ex_date_record_date" in item for item in backlog["candidates"][11]["required_new_data"])
    assert any("bonus_issue_split" in item for item in backlog["candidates"][11]["required_new_data"])
    assert backlog["candidates"][12]["profile_hint"] == "hk_ipo_lockup_overhang_event_overlay"
    assert backlog["candidates"][12]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("chapter_4.pdf" in url for url in backlog["candidates"][12]["source_reference_urls"])
    assert any("2647696" in url for url in backlog["candidates"][12]["source_reference_urls"])
    assert any("cornerstone" in item for item in backlog["candidates"][12]["required_new_data"])
    assert any("lockup_expiry" in item for item in backlog["candidates"][12]["required_new_data"])
    assert backlog["candidates"][13]["profile_hint"] == "hk_audit_opinion_suspension_risk_overlay"
    assert backlog["candidates"][13]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("190524news" in url for url in backlog["candidates"][13]["source_reference_urls"])
    assert any("1350a" in url for url in backlog["candidates"][13]["source_reference_urls"])
    assert any("0165410184900181" in url for url in backlog["candidates"][13]["source_reference_urls"])
    assert any("audit_opinion" in item for item in backlog["candidates"][13]["required_new_data"])
    assert any("resumption_guidance" in item for item in backlog["candidates"][13]["required_new_data"])
    assert backlog["candidates"][14]["profile_hint"] == "hk_share_repurchase_execution_signal_overlay"
    assert backlog["candidates"][14]["suggested_contract_type"] == "event_calendar_snapshot_overlay"
    assert any("sharerepur" in url for url in backlog["candidates"][14]["source_reference_urls"])
    assert any("newsletter_202506" in url for url in backlog["candidates"][14]["source_reference_urls"])
    assert any("097265270500400301" in url for url in backlog["candidates"][14]["source_reference_urls"])
    assert any("repurchase" in item for item in backlog["candidates"][14]["required_new_data"])
    assert any("treasury_share" in item for item in backlog["candidates"][14]["required_new_data"])
    assert backlog["candidates"][15]["profile_hint"] == "hk_liquid_pairs_cointegration_stat_arb_overlay"
    assert backlog["candidates"][15]["suggested_contract_type"] == "pair_snapshot_overlay"
    assert any("2022-02" in url for url in backlog["candidates"][15]["source_reference_urls"])
    assert any("261387" in url for url in backlog["candidates"][15]["source_reference_urls"])
    assert any("S1059056017300254" in url for url in backlog["candidates"][15]["source_reference_urls"])
    assert any("cointegration" in item for item in backlog["candidates"][15]["required_new_data"])
    assert any("borrow_fee" in item for item in backlog["candidates"][15]["required_new_data"])
    assert any("tick_rule" in item for item in backlog["candidates"][15]["required_new_data"])
    assert backlog["candidates"][16]["profile_hint"] == "hk_macro_liquidity_inflation_rate_sensitivity_overlay"
    assert backlog["candidates"][16]["suggested_contract_type"] == "macro_snapshot_overlay"
    assert any("sciedu.ca" in url for url in backlog["candidates"][16]["source_reference_urls"])
    assert any("hkma.gov.hk" in url for url in backlog["candidates"][16]["source_reference_urls"])
    assert any("hkab.org.hk" in url for url in backlog["candidates"][16]["source_reference_urls"])
    assert any("censtatd.gov.hk" in url for url in backlog["candidates"][16]["source_reference_urls"])
    assert any("base_rate_hibor" in item for item in backlog["candidates"][16]["required_new_data"])
    assert any("release_timestamp_lag" in item for item in backlog["candidates"][16]["required_new_data"])
    assert any("sector_industry_rate_beta" in item for item in backlog["candidates"][16]["required_new_data"])
    assert backlog["candidates"][17]["profile_hint"] == "hk_turn_of_month_lunar_new_year_calendar_overlay"
    assert backlog["candidates"][17]["suggested_contract_type"] == "calendar_snapshot_overlay"
    assert any("apfiec" in url for url in backlog["candidates"][17]["source_reference_urls"])
    assert any("Trading-hours-and-Severe-Weather" in url for url in backlog["candidates"][17]["source_reference_urls"])
    assert any("lunar_new_year" in item for item in backlog["candidates"][17]["required_new_data"])
    assert any("short_selling_turnover" in item for item in backlog["candidates"][17]["required_new_data"])
    assert backlog["candidates"][18]["profile_hint"] == "hk_etf_premium_discount_tracking_quality_overlay"
    assert backlog["candidates"][18]["suggested_contract_type"] == "etf_product_snapshot_overlay"
    assert any("2303600" in url for url in backlog["candidates"][18]["source_reference_urls"])
    assert any("ETF-Handbook" in url for url in backlog["candidates"][18]["source_reference_urls"])
    assert any("nav_inav_premium_discount" in item for item in backlog["candidates"][18]["required_new_data"])
    assert any("complex_product" in item for item in backlog["candidates"][18]["required_new_data"])
    assert backlog["candidates"][19]["profile_hint"] == "hk_asset_growth_net_issuance_quality_overlay"
    assert backlog["candidates"][19]["suggested_contract_type"] == "accounting_factor_snapshot_overlay"
    assert any("3043649" in url for url in backlog["candidates"][19]["source_reference_urls"])
    assert any("188473" in url for url in backlog["candidates"][19]["source_reference_urls"])
    assert any("total_asset_growth" in item for item in backlog["candidates"][19]["required_new_data"])
    assert any("net_share_issuance" in item for item in backlog["candidates"][19]["required_new_data"])
    assert backlog["candidates"][20]["profile_hint"] == "hk_accrual_quality_earnings_persistence_overlay"
    assert backlog["candidates"][20]["suggested_contract_type"] == "accounting_factor_snapshot_overlay"
    assert any("2057/3638" in url for url in backlog["candidates"][20]["source_reference_urls"])
    assert any("S1042443114000808" in url for url in backlog["candidates"][20]["source_reference_urls"])
    assert any("operating_accruals" in item for item in backlog["candidates"][20]["required_new_data"])
    assert any("earnings_persistence" in item for item in backlog["candidates"][20]["required_new_data"])
    assert backlog["candidates"][21]["profile_hint"] == "hk_fscore_gross_profitability_quality_overlay"
    assert backlog["candidates"][21]["suggested_contract_type"] == "accounting_factor_snapshot_overlay"
    assert any("10397/81583" in url for url in backlog["candidates"][21]["source_reference_urls"])
    assert any("s41260-020-00157-2" in url for url in backlog["candidates"][21]["source_reference_urls"])
    assert any("S0927538X16300804" in url for url in backlog["candidates"][21]["source_reference_urls"])
    assert any("piotroski_fscore" in item for item in backlog["candidates"][21]["required_new_data"])
    assert any("gross_profitability" in item for item in backlog["candidates"][21]["required_new_data"])
    assert backlog["candidates"][22]["profile_hint"] == "hk_shareholding_concentration_free_float_risk_overlay"
    assert backlog["candidates"][22]["suggested_contract_type"] == "ownership_liquidity_risk_snapshot_overlay"
    assert any("High-shareholding-concentration" in url for url in backlog["candidates"][22]["source_reference_urls"])
    assert any("searchsdw" in url for url in backlog["candidates"][22]["source_reference_urls"])
    assert any("sfc_high_shareholding" in item for item in backlog["candidates"][22]["required_new_data"])
    assert any("ccass_participant_concentration" in item for item in backlog["candidates"][22]["required_new_data"])
    assert backlog["candidates"][23]["profile_hint"] == "hk_amihud_liquidity_risk_capacity_overlay"
    assert backlog["candidates"][23]["suggested_contract_type"] == "liquidity_risk_snapshot_overlay"
    assert any("jbfina/v35y2011i9p2217-2230" in url for url in backlog["candidates"][23]["source_reference_urls"])
    assert any("S0378426612002014" in url for url in backlog["candidates"][23]["source_reference_urls"])
    assert any("Securities-Market" in url for url in backlog["candidates"][23]["source_reference_urls"])
    assert any("amihud_illiquidity" in item for item in backlog["candidates"][23]["required_new_data"])
    assert any("liquidity_beta" in item for item in backlog["candidates"][23]["required_new_data"])
    assert backlog["candidates"][24]["profile_hint"] == "hk_analyst_dispersion_coverage_risk_overlay"
    assert backlog["candidates"][24]["suggested_contract_type"] == "analyst_consensus_risk_snapshot_overlay"
    assert any("S1544612322007462" in url for url in backlog["candidates"][24]["source_reference_urls"])
    assert any("10722/238965" in url for url in backlog["candidates"][24]["source_reference_urls"])
    assert any("1949417" in url for url in backlog["candidates"][24]["source_reference_urls"])
    assert any("forecast_dispersion" in item for item in backlog["candidates"][24]["required_new_data"])
    assert any("coverage_drop" in item for item in backlog["candidates"][24]["required_new_data"])
    assert backlog["candidates"][25]["profile_hint"] == "hk_financial_distress_deleveraging_risk_overlay"
    assert backlog["candidates"][25]["suggested_contract_type"] == "financial_distress_risk_snapshot_overlay"
    assert any("corporate-sector-vulnerabilities" in url for url in backlog["candidates"][25]["source_reference_urls"])
    assert any("2071-1050/7/2/1186" in url for url in backlog["candidates"][25]["source_reference_urls"])
    assert any("18479790231165603" in url for url in backlog["candidates"][25]["source_reference_urls"])
    assert any("zscore" in item for item in backlog["candidates"][25]["required_new_data"])
    assert any("debt_maturity" in item for item in backlog["candidates"][25]["required_new_data"])
    assert backlog["candidates"][26]["profile_hint"] == "hk_downside_beta_tail_risk_volatility_overlay"
    assert backlog["candidates"][26]["suggested_contract_type"] == "downside_risk_volatility_snapshot_overlay"
    assert any("extreme-downside-risk" in url for url in backlog["candidates"][26]["source_reference_urls"])
    assert any("S154461231730346X" in url for url in backlog["candidates"][26]["source_reference_urls"])
    assert any("S0927538X13000425" in url for url in backlog["candidates"][26]["source_reference_urls"])
    assert any("downside_beta" in item for item in backlog["candidates"][26]["required_new_data"])
    assert any("tail_loss" in item for item in backlog["candidates"][26]["required_new_data"])
    assert backlog["candidates"][27]["profile_hint"] == "hk_structured_product_warrant_cbbc_flow_risk_overlay"
    assert backlog["candidates"][27]["suggested_contract_type"] == "structured_product_flow_risk_snapshot_overlay"
    assert any("Structured-Products/Overview" in url for url in backlog["candidates"][27]["source_reference_urls"])
    assert any("products/securities/dw" in url.lower() for url in backlog["candidates"][27]["source_reference_urls"])
    assert any("v35y2015i11p1042-1066" in url for url in backlog["candidates"][27]["source_reference_urls"])
    assert any("warrant_cbbc" in item for item in backlog["candidates"][27]["required_new_data"])
    assert any("mandatory_call_event" in item for item in backlog["candidates"][27]["required_new_data"])
    assert backlog["candidates"][28]["profile_hint"] == (
        "hk_index_derivatives_futures_options_sentiment_basis_overlay"
    )
    assert backlog["candidates"][28]["suggested_contract_type"] == (
        "index_derivatives_sentiment_basis_snapshot_overlay"
    )
    assert any("Futures-and-Options-Prices" in url for url in backlog["candidates"][28]["source_reference_urls"])
    assert any("20231010T000000.pdf" in url for url in backlog["candidates"][28]["source_reference_urls"])
    assert any("S0378426699001272" in url for url in backlog["candidates"][28]["source_reference_urls"])
    assert any("put_call" in item for item in backlog["candidates"][28]["required_new_data"])
    assert any("expiry_roll" in item for item in backlog["candidates"][28]["required_new_data"])
    assert backlog["candidates"][29]["profile_hint"] == "hk_vcm_cas_microstructure_shock_risk_overlay"
    assert backlog["candidates"][29]["suggested_contract_type"] == "microstructure_shock_risk_snapshot_overlay"
    assert any("Trading/VCM" in url for url in backlog["candidates"][29]["source_reference_urls"])
    assert any("150703news" in url for url in backlog["candidates"][29]["source_reference_urls"])
    assert any("4209595" in url for url in backlog["candidates"][29]["source_reference_urls"])
    assert any("vcm_security" in item for item in backlog["candidates"][29]["required_new_data"])
    assert any("auction_session" in item for item in backlog["candidates"][29]["required_new_data"])
    assert backlog["candidates"][30]["profile_hint"] == "hk_reit_dividend_spread_rate_sensitivity_overlay"
    assert backlog["candidates"][30]["suggested_contract_type"] == "reit_rate_income_snapshot_overlay"
    assert any("Real-Estate-Investment-Trusts" in url for url in backlog["candidates"][30]["source_reference_urls"])
    assert any("Code-on-Real-Estate-Investment-Trusts" in url for url in backlog["candidates"][30]["source_reference_urls"])
    assert any("reite.pdf" in url for url in backlog["candidates"][30]["source_reference_urls"])
    assert any("reit_universe" in item for item in backlog["candidates"][30]["required_new_data"])
    assert any("yield_spread" in item for item in backlog["candidates"][30]["required_new_data"])
    assert backlog["candidates"][31]["profile_hint"] == "hk_regulatory_enforcement_disciplinary_risk_overlay"
    assert backlog["candidates"][31]["suggested_contract_type"] == "regulatory_event_risk_snapshot_overlay"
    assert any("Disciplinary-Sanctions" in url for url in backlog["candidates"][31]["source_reference_urls"])
    assert any("Regulatory-functions/Enforcement" in url for url in backlog["candidates"][31]["source_reference_urls"])
    assert any("1869454" in url for url in backlog["candidates"][31]["source_reference_urls"])
    assert any("disciplinary_sanction" in item for item in backlog["candidates"][31]["required_new_data"])
    assert any("market_misconduct" in item for item in backlog["candidates"][31]["required_new_data"])
    assert backlog["candidates"][32]["profile_hint"] == (
        "hk_margin_financing_collateral_forced_selling_risk_overlay"
    )
    assert backlog["candidates"][32]["suggested_contract_type"] == "margin_collateral_risk_snapshot_overlay"
    assert any("Securities-Margin-Finance-SMF" in url for url in backlog["candidates"][32]["source_reference_urls"])
    assert any("refNo=17EC67" in url for url in backlog["candidates"][32]["source_reference_urls"])
    assert any("S1057521921001721" in url for url in backlog["candidates"][32]["source_reference_urls"])
    assert any("marginable_security" in item for item in backlog["candidates"][32]["required_new_data"])
    assert any("forced_selling" in item for item in backlog["candidates"][32]["required_new_data"])
    assert backlog["candidates"][33]["profile_hint"] == "hk_liquid_largecap_weekly_reversal_cost_aware_overlay"
    assert backlog["candidates"][33]["suggested_contract_type"] == "cost_aware_reversal_snapshot_overlay"
    assert any("applec" in url for url in backlog["candidates"][33]["source_reference_urls"])
    assert any("S1044028399000162" in url for url in backlog["candidates"][33]["source_reference_urls"])
    assert any("Transaction" in url for url in backlog["candidates"][33]["source_reference_urls"])
    assert any("weekly_extreme_return" in item for item in backlog["candidates"][33]["required_new_data"])
    assert any("bid_ask_bounce" in item for item in backlog["candidates"][33]["required_new_data"])


def test_future_research_live_enablement_policy_blocks_backlog_until_new_contract_and_evidence():
    policy = build_future_research_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION
    assert policy["status"] == "pre_scaffold_gate_only"
    assert policy["live_enablement_allowed"] is False
    assert policy["candidate_order"] == [
        "hk_earnings_revision_quality_overlay",
        "hk_low_size_quality_liquidity_premium",
        "hk_stock_connect_inclusion_event_flow",
        "hk_short_selling_pressure_risk_overlay",
        "hk_director_dealing_disclosure_quality_overlay",
        "hk_dually_traded_liquid_reversal_overlay",
        "hk_earnings_announcement_drift_overlay",
        "hk_lottery_stock_risk_exclusion_overlay",
        "hk_equity_financing_dilution_risk_overlay",
        "hk_connected_transaction_governance_risk_overlay",
        "hk_takeover_privatization_event_spread_overlay",
        "hk_distribution_ex_date_entitlement_overlay",
        "hk_ipo_lockup_overhang_event_overlay",
        "hk_audit_opinion_suspension_risk_overlay",
        "hk_share_repurchase_execution_signal_overlay",
        "hk_liquid_pairs_cointegration_stat_arb_overlay",
        "hk_macro_liquidity_inflation_rate_sensitivity_overlay",
        "hk_turn_of_month_lunar_new_year_calendar_overlay",
        "hk_etf_premium_discount_tracking_quality_overlay",
        "hk_asset_growth_net_issuance_quality_overlay",
        "hk_accrual_quality_earnings_persistence_overlay",
        "hk_fscore_gross_profitability_quality_overlay",
        "hk_shareholding_concentration_free_float_risk_overlay",
        "hk_amihud_liquidity_risk_capacity_overlay",
        "hk_analyst_dispersion_coverage_risk_overlay",
        "hk_financial_distress_deleveraging_risk_overlay",
        "hk_downside_beta_tail_risk_volatility_overlay",
        "hk_structured_product_warrant_cbbc_flow_risk_overlay",
        "hk_index_derivatives_futures_options_sentiment_basis_overlay",
        "hk_vcm_cas_microstructure_shock_risk_overlay",
        "hk_reit_dividend_spread_rate_sensitivity_overlay",
        "hk_regulatory_enforcement_disciplinary_risk_overlay",
        "hk_margin_financing_collateral_forced_selling_risk_overlay",
        "hk_liquid_largecap_weekly_reversal_cost_aware_overlay",
    ]
    assert "same_universe_ablation_vs_existing_quality_yield_momentum_and_special_situation_profiles" in (
        policy["required_pre_scaffold_gates"]
    )
    assert "mutating_existing_contract_in_place" in policy["required_reject_criteria"]
    assert "benchmark_and_candidate_index_methodology_versions" in policy["required_data_provenance"]
    assert "point_in_time_consensus_estimate_and_revision_history" in policy["required_data_provenance"]
    assert "point_in_time_free_float_market_cap_and_size_factor_history" in policy["required_data_provenance"]
    assert "liquidity_spread_lot_size_suspension_and_capacity_history" in policy["required_data_provenance"]
    assert "point_in_time_stock_connect_eligibility_change_history" in policy["required_data_provenance"]
    assert "southbound_turnover_ccass_holding_and_flow_confirmation_history" in policy["required_data_provenance"]
    assert "daily_short_selling_turnover_short_interest_and_short_ratio_history" in (
        policy["required_data_provenance"]
    )
    assert "covered_short_sale_tick_rule_and_shorting_eligibility_history" in policy["required_data_provenance"]
    assert "point_in_time_disclosure_of_interests_notice_history" in policy["required_data_provenance"]
    assert "director_chief_executive_and_substantial_shareholder_dealing_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_dually_traded_security_mapping_history" in policy["required_data_provenance"]
    assert "weekly_reversal_signal_cost_spread_and_capacity_history" in policy["required_data_provenance"]
    assert "point_in_time_hkex_results_announcement_profit_warning_and_alert_history" in (
        policy["required_data_provenance"]
    )
    assert "earnings_surprise_sign_magnitude_and_post_announcement_window_history" in (
        policy["required_data_provenance"]
    )
    assert "announcement_publication_timestamp_suspension_and_trading_resumption_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_lottery_feature_ivol_iskew_max_price_history" in policy["required_data_provenance"]
    assert "market_regime_volatility_drawdown_and_lottery_premium_condition_history" in (
        policy["required_data_provenance"]
    )
    assert "lottery_overlay_liquidity_short_sale_suspension_and_capacity_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_equity_financing_rights_open_offer_placement_and_convertible_history" in (
        policy["required_data_provenance"]
    )
    assert "issue_size_discount_dilution_proceeds_underwriter_and_shareholder_approval_history" in (
        policy["required_data_provenance"]
    )
    assert "post_equity_financing_return_liquidity_suspension_and_rule_change_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_connected_transaction_announcement_circular_and_shareholder_approval_history" in (
        policy["required_data_provenance"]
    )
    assert "connected_person_relationship_transaction_type_pricing_policy_and_independent_advice_history" in (
        policy["required_data_provenance"]
    )
    assert "post_connected_transaction_return_tunneling_propping_disclosure_quality_and_governance_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_takeover_possible_offer_firm_intention_privatisation_and_offer_period_history" in (
        policy["required_data_provenance"]
    )
    assert "offer_price_spread_conditions_acceptance_level_compulsory_acquisition_and_withdrawal_history" in (
        policy["required_data_provenance"]
    )
    assert "takeover_event_liquidity_trading_halt_disclosure_dealing_and_completion_risk_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_dividend_and_entitlement_ex_date_record_date_book_closure_and_payment_history" in (
        policy["required_data_provenance"]
    )
    assert "cash_special_scrip_stock_distribution_bonus_issue_split_and_adjustment_factor_history" in (
        policy["required_data_provenance"]
    )
    assert "ex_entitlement_price_adjustment_settlement_extreme_weather_liquidity_and_cost_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_ipo_listing_prospectus_cornerstone_pre_ipo_investor_and_lockup_expiry_history" in (
        policy["required_data_provenance"]
    )
    assert "cornerstone_allocation_lockup_size_free_float_clawback_double_dipping_and_stabilization_history" in (
        policy["required_data_provenance"]
    )
    assert "post_ipo_return_lockup_expiry_overhang_liquidity_block_trade_and_short_sale_eligibility_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_audit_opinion_disclaimer_adverse_qualified_going_concern_and_results_history" in (
        policy["required_data_provenance"]
    )
    assert "audit_issue_resolution_remedial_period_suspension_resumption_guidance_and_delisting_history" in (
        policy["required_data_provenance"]
    )
    assert "post_audit_opinion_return_liquidity_resumption_restructuring_and_capacity_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_share_repurchase_next_day_return_program_mandate_and_execution_history" in (
        policy["required_data_provenance"]
    )
    assert "treasury_share_retention_cancellation_resale_blackout_moratorium_and_connected_person_history" in (
        policy["required_data_provenance"]
    )
    assert "post_buyback_share_count_reduction_dilution_financing_and_undervaluation_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_pairs_universe_industry_beta_borrow_shortable_dual_listing_and_corporate_action_history" in (
        policy["required_data_provenance"]
    )
    assert "cointegration_distance_correlation_spread_half_life_hurst_breakdown_and_rebalance_window_history" in (
        policy["required_data_provenance"]
    )
    assert "pair_leg_quote_spread_lot_size_borrow_fee_tick_rule_vcm_cas_and_capacity_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hk_cpi_inflation_base_rate_hibor_and_liquidity_condition_history" in (
        policy["required_data_provenance"]
    )
    assert "macro_release_timestamp_lag_revision_currency_peg_and_rate_regime_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hkex_trading_calendar_turn_of_month_and_lunar_new_year_window_history" in (
        policy["required_data_provenance"]
    )
    assert "calendar_overlay_short_selling_turnover_liquidity_spread_and_capacity_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hk_listed_etf_nav_inav_premium_discount_and_tracking_difference_history" in (
        policy["required_data_provenance"]
    )
    assert "etf_replication_synthetic_leveraged_inverse_complex_product_and_stock_connect_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_total_asset_growth_net_operating_asset_growth_and_capex_history" in (
        policy["required_data_provenance"]
    )
    assert "net_share_issuance_equity_financing_buyback_share_count_and_dilution_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_operating_accruals_working_capital_accruals_cash_flow_and_earnings_history" in (
        policy["required_data_provenance"]
    )
    assert "earnings_persistence_cash_conversion_receivables_inventory_payables_and_depreciation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_piotroski_fscore_component_and_gross_profitability_history" in (
        policy["required_data_provenance"]
    )
    assert "fscore_profitability_leverage_liquidity_share_issuance_margin_turnover_and_reporting_lag_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_sfc_high_shareholding_concentration_announcement_history" in (
        policy["required_data_provenance"]
    )
    assert "ccass_participant_concentration_free_float_public_float_and_liquidity_history" in (
        policy["required_data_provenance"]
    )
    assert "shareholding_concentration_ramp_dump_red_flag_price_volume_and_halt_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_amihud_illiquidity_turnover_spread_depth_and_zero_volume_history" in (
        policy["required_data_provenance"]
    )
    assert "market_wide_liquidity_shock_liquidity_beta_and_liquidity_regime_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_analyst_forecast_dispersion_coverage_recommendation_and_target_price_history" in (
        policy["required_data_provenance"]
    )
    assert "analyst_forecast_accuracy_bias_revision_staleness_policy_uncertainty_and_coverage_drop_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_earnings_revision_momentum_quality_value_liquidity_and_short_interest_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_financial_distress_zscore_distance_to_default_interest_coverage_and_debt_maturity_history" in (
        policy["required_data_provenance"]
    )
    assert "profitability_liquidity_leverage_cash_flow_debt_service_and_property_exposure_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_quality_value_yield_momentum_liquidity_audit_opinion_and_suspension_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_downside_beta_semivariance_realized_volatility_and_tail_risk_history" in (
        policy["required_data_provenance"]
    )
    assert "var_cvar_drawdown_contribution_volatility_regime_and_stress_beta_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_quality_value_yield_momentum_liquidity_lottery_and_distress_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_derivative_warrant_cbbc_listing_issuance_expiry_underlying_and_turnover_history" in (
        policy["required_data_provenance"]
    )
    assert "cbbc_call_price_mce_distance_bull_bear_outstanding_notional_and_strike_maturity_history" in (
        policy["required_data_provenance"]
    )
    assert "structured_product_liquidity_provider_spread_hedging_stress_and_underlying_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hsi_hstech_hscei_futures_options_price_volume_open_interest_basis_and_put_call_history" in (
        policy["required_data_provenance"]
    )
    assert "options_implied_volatility_skew_term_structure_futures_basis_calendar_spread_and_expiry_roll_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_index_etf_largecap_momentum_volatility_structured_product_and_macro_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_vcm_security_eligibility_trigger_cooling_off_price_band_and_cas_price_limit_history" in (
        policy["required_data_provenance"]
    )
    assert "auction_session_pos_cas_reference_price_order_imbalance_close_auction_and_volatility_interruption_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hk_reit_universe_distribution_nav_gav_leverage_and_property_sector_history" in (
        policy["required_data_provenance"]
    )
    assert "reit_dividend_yield_hibor_base_rate_bond_yield_spread_and_rental_growth_expectation_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_reit_vs_property_dividend_quality_macro_rate_and_etf_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_hkex_disciplinary_sanction_enforcement_bulletin_and_remedial_action_history" in (
        policy["required_data_provenance"]
    )
    assert "sfc_enforcement_mmt_restriction_notice_false_disclosure_and_market_misconduct_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_governance_audit_opinion_connected_transaction_concentration_and_liquidity_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_marginable_security_broker_haircut_ltv_and_collateral_concentration_history" in (
        policy["required_data_provenance"]
    )
    assert "sfc_smf_guideline_broker_margin_loan_top_collateral_concentration_and_elc_stress_history" in (
        policy["required_data_provenance"]
    )
    assert "share_pledge_disclosure_margin_call_forced_selling_price_gap_and_liquidity_history" in (
        policy["required_data_provenance"]
    )
    assert "point_in_time_weekly_extreme_return_reversal_continuance_liquidity_and_volume_history" in (
        policy["required_data_provenance"]
    )
    assert "largecap_liquid_universe_spread_fee_slippage_vcm_cas_and_bid_ask_bounce_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_momentum_dual_listing_liquidity_volatility_lottery_and_event_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "same_universe_liquidity_volatility_derivatives_structured_product_momentum_event_and_execution_ablation_history" in (
        policy["required_data_provenance"]
    )
    assert "sector_rate_beta_inflation_beta_property_financial_and_dividend_yield_sensitivity_history" in (
        policy["required_data_provenance"]
    )
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("IM_hsscsqe.pdf" in url for url in policy["source_reference_urls"])
    assert any("factor-indexes" in url for url in policy["source_reference_urls"])
    assert any("earnings-revision-overlay" in url for url in policy["source_reference_urls"])
    assert any("IM_hssbisse.pdf" in url for url in policy["source_reference_urls"])
    assert any("eligible-stocks" in url.lower() for url in policy["source_reference_urls"])
    assert any("Short-Selling-Turnover" in url for url in policy["source_reference_urls"])
    assert any("Disclosure-of-Interests" in url for url in policy["source_reference_urls"])
    assert any("applec" in url or "pacfin" in url for url in policy["source_reference_urls"])
    assert any("hkexnews" in url.lower() or "4070" in url for url in policy["source_reference_urls"])
    assert any("Gambling_Hong_Kong" in url for url in policy["source_reference_urls"])
    assert any("13000929" in url for url in policy["source_reference_urls"])
    assert any("180504news" in url for url in policy["source_reference_urls"])
    assert any("1008780" in url for url in policy["source_reference_urls"])
    assert any("1214" in url for url in policy["source_reference_urls"])
    assert any("Takeovers-and-mergers" in url for url in policy["source_reference_urls"])
    assert any("S089083898371022X" in url for url in policy["source_reference_urls"])
    assert any("f_div.pdf" in url for url in policy["source_reference_urls"])
    assert any("jfinan" in url for url in policy["source_reference_urls"])
    assert any("chapter_4.pdf" in url for url in policy["source_reference_urls"])
    assert any("2647696" in url for url in policy["source_reference_urls"])
    assert any("190524news" in url for url in policy["source_reference_urls"])
    assert any("rulebook/1350a" in url for url in policy["source_reference_urls"])
    assert any("0165410184900181" in url for url in policy["source_reference_urls"])
    assert any("sharerepur" in url for url in policy["source_reference_urls"])
    assert any("newsletter_202506" in url for url in policy["source_reference_urls"])
    assert any("097265270500400301" in url for url in policy["source_reference_urls"])
    assert any("2022-02" in url for url in policy["source_reference_urls"])
    assert any("261387" in url for url in policy["source_reference_urls"])
    assert any("S1059056017300254" in url for url in policy["source_reference_urls"])
    assert any("afr/article/view/16166" in url for url in policy["source_reference_urls"])
    assert any("daily-figures-interbank-liquidity" in url for url in policy["source_reference_urls"])
    assert any("rates/hibor" in url for url in policy["source_reference_urls"])
    assert any("scode270" in url for url in policy["source_reference_urls"])
    assert any("apfiec" in url for url in policy["source_reference_urls"])
    assert any("S1057521903000073" in url for url in policy["source_reference_urls"])
    assert any("Trading-hours-and-Severe-Weather" in url for url in policy["source_reference_urls"])
    assert any("2303600" in url for url in policy["source_reference_urls"])
    assert any("ETF-Handbook" in url for url in policy["source_reference_urls"])
    assert any("20110814" in url for url in policy["source_reference_urls"])
    assert any("3043649" in url for url in policy["source_reference_urls"])
    assert any("188473" in url for url in policy["source_reference_urls"])
    assert any("S0304405X11000894" in url for url in policy["source_reference_urls"])
    assert any("2057/3638" in url for url in policy["source_reference_urls"])
    assert any("S1042443114000808" in url for url in policy["source_reference_urls"])
    assert any("dac5ab3e" in url for url in policy["source_reference_urls"])
    assert any("10397/81583" in url for url in policy["source_reference_urls"])
    assert any("s41260-020-00157-2" in url for url in policy["source_reference_urls"])
    assert any("S0927538X16300804" in url for url in policy["source_reference_urls"])
    assert any("indexes/index/721604" in url for url in policy["source_reference_urls"])
    assert any("High-shareholding-concentration" in url for url in policy["source_reference_urls"])
    assert any("refNo=21EC26" in url for url in policy["source_reference_urls"])
    assert any("searchsdw" in url for url in policy["source_reference_urls"])
    assert any("10722/33347" in url for url in policy["source_reference_urls"])
    assert any("jbfina/v35y2011i9p2217-2230" in url for url in policy["source_reference_urls"])
    assert any("S0378426612002014" in url for url in policy["source_reference_urls"])
    assert any("Securities-Market" in url for url in policy["source_reference_urls"])
    assert any("S1544612322007462" in url for url in policy["source_reference_urls"])
    assert any("10722/238965" in url for url in policy["source_reference_urls"])
    assert any("1949417" in url for url in policy["source_reference_urls"])
    assert any("corporate-sector-vulnerabilities" in url for url in policy["source_reference_urls"])
    assert any("2071-1050/7/2/1186" in url for url in policy["source_reference_urls"])
    assert any("18479790231165603" in url for url in policy["source_reference_urls"])
    assert any("extreme-downside-risk" in url for url in policy["source_reference_urls"])
    assert any("S154461231730346X" in url for url in policy["source_reference_urls"])
    assert any("risk-return-relationships-in-the-hong-kong-stock-market" in url for url in policy["source_reference_urls"])
    assert any("Structured-Products/Overview" in url for url in policy["source_reference_urls"])
    assert any("Trading-Information-and-Historical-Data" in url for url in policy["source_reference_urls"])
    assert any("products/securities/cbbc" in url.lower() for url in policy["source_reference_urls"])
    assert any("S0378426600001382" in url for url in policy["source_reference_urls"])
    assert any("v35y2015i11p1042-1066" in url for url in policy["source_reference_urls"])
    assert any("Futures-and-Options-Prices" in url for url in policy["source_reference_urls"])
    assert any("HKEX_HSI_FO_EN.pdf" in url for url in policy["source_reference_urls"])
    assert any("mispricing-of-index-futures-contracts" in url for url in policy["source_reference_urls"])
    assert any("S0378426600001667" in url for url in policy["source_reference_urls"])
    assert any("jfutmk/v24y2004i9p887-907" in url for url in policy["source_reference_urls"])
    assert any("Trading/VCM" in url for url in policy["source_reference_urls"])
    assert any("VCM-Enhancements-Initiative" in url for url in policy["source_reference_urls"])
    assert any("160818news" in url for url in policy["source_reference_urls"])
    assert any("4209595" in url for url in policy["source_reference_urls"])
    assert any("10722/85627" in url for url in policy["source_reference_urls"])
    assert any("Real-Estate-Investment-Trusts" in url for url in policy["source_reference_urls"])
    assert any("Code-on-Real-Estate-Investment-Trusts" in url for url in policy["source_reference_urls"])
    assert any("IM_reite.pdf" in url for url in policy["source_reference_urls"])
    assert any("S1463578X21000190" in url for url in policy["source_reference_urls"])
    assert any("Disciplinary-and-Enforcement/Overview" in url for url in policy["source_reference_urls"])
    assert any("Disciplinary-Sanctions" in url for url in policy["source_reference_urls"])
    assert any("Regulatory-functions/Enforcement" in url for url in policy["source_reference_urls"])
    assert any("refNo=21PR27" in url for url in policy["source_reference_urls"])
    assert any("1869454" in url for url in policy["source_reference_urls"])
    assert any("Securities-Margin-Finance-SMF" in url for url in policy["source_reference_urls"])
    assert any("Guidelines-for-Securities-Margin-Financing-Activities" in url for url in policy["source_reference_urls"])
    assert any("refNo=17EC67" in url for url in policy["source_reference_urls"])
    assert any("Review-of-Securities-Margin-Financing-Activities" in url for url in policy["source_reference_urls"])
    assert any("S1057521921001721" in url for url in policy["source_reference_urls"])
    assert any("applec/v46y2014i12p1335-1349" in url for url in policy["source_reference_urls"])
    assert any("does-the-hong-kong-stock-market-overreact" in url for url in policy["source_reference_urls"])
    assert any("S1044028399000162" in url for url in policy["source_reference_urls"])
    assert any("f9bc272223de4c26b1fb161ccaf76cfa" in url for url in policy["source_reference_urls"])



def test_policy_value_central_soe_row_carries_active_policy_and_external_evidence():
    row = build_snapshot_promotion_row("hk_policy_value_quality")

    assert row["profile"] == "hk_central_soe_value_quality_select"
    assert row["priority"] == 6
    assert row["promotion_bucket"] == "policy_value_quality_candidate"
    assert row["recommended_live_enablement_stage"] == (
        "policy_value_quality_after_factor_mix_and_quality_yield_ablation"
    )
    assert row["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.0
    assert row["policy_value_live_enablement_policy"]["policy_version"] == (
        POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION
    )
    assert "central_soe_flag_methodology_version_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sasac_central_soe_parent_list_effective_date_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_central_soe_value_quality_factor_index_constituent_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_40pct_factor_screening_and_buffer_rule_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "central_soe_largest_shareholder_source_list_effective_date_drift_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hkex_southbound_eligible_security_point_in_time_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "policy_event_and_governance_risk_controls" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("IM_hssccsme.pdf" in url for url in row["research_evidence_urls"])
    assert any("hsscsoee.pdf" in url for url in row["research_evidence_urls"])
    assert any("hssccsve.pdf" in url for url in row["research_evidence_urls"])
    assert any("hssccsqe.pdf" in url for url in row["research_evidence_urls"])
    assert any("eligible-stocks" in url for url in row["research_evidence_urls"])
    assert any("sasac.gov.cn" in url for url in row["research_evidence_urls"])
    assert any("en.sasac.gov.cn" in url for url in row["research_evidence_urls"])
    assert any("mof.gov.cn" in url for url in row["research_evidence_urls"])
    assert any("central-SOE" in item for item in row["profile_specific_next_evidence"])
    assert any("SASAC/MOF" in item for item in row["profile_specific_next_evidence"])
    assert any("missing-measure averaging" in item for item in row["profile_specific_next_evidence"])
    assert any("source-list effective-date drift" in item for item in row["profile_specific_next_evidence"])


def test_policy_value_live_enablement_policy_requires_ablation_stress_and_provenance():
    policy = build_policy_value_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION
    assert "central_soe_value_quality_vs_broad_value_quality_same_universe" in policy["required_ablation_tests"]
    assert "central_soe_value_quality_vs_hsi_value_and_quality_factor_indexes_same_universe" in (
        policy["required_ablation_tests"]
    )
    assert "hsi_40pct_factor_screening_vs_unbuffered_top_rank_selection" in policy["required_ablation_tests"]
    assert "hsi_factor_cap_weighting_vs_uncapped_policy_value_portfolio" in policy["required_ablation_tests"]
    assert "southbound_eligible_vs_all_hk_central_soe_universe" in policy["required_ablation_tests"]
    assert "soe_sector_concentration_financials_energy_telecom_window" in policy["required_stress_tests"]
    assert "sasac_mof_reclassification_and_parent_restructuring_window" in policy["required_stress_tests"]
    assert "hsi_factor_screening_cap_and_rebalance_turnover_spike_window" in policy["required_stress_tests"]
    assert "government_shareholder_classification_history" in policy["required_data_provenance"]
    assert "mof_central_financial_soe_list_effective_date_history" in policy["required_data_provenance"]
    assert "hsi_factor_score_zscore_industry_standardization_history" in policy["required_data_provenance"]
    assert "hsi_40pct_factor_screening_and_buffer_rule_history" in policy["required_data_provenance"]
    assert "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("IM_hssccsme.pdf" in url for url in policy["source_reference_urls"])
    assert any("eligible-stocks" in url for url in policy["source_reference_urls"])
    assert any("mof.gov.cn" in url for url in policy["source_reference_urls"])


def test_factor_mix_qvlm_row_carries_active_policy_and_external_evidence():
    row = build_snapshot_promotion_row("hk_qvlm_risk_parity")

    assert row["profile"] == "hk_factor_mix_qvlm_risk_parity"
    assert row["priority"] == 5
    assert row["promotion_bucket"] == "factor_mix_snapshot_candidate"
    assert row["recommended_live_enablement_stage"] == "factor_mix_risk_parity_after_single_factor_ablation"
    assert row["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.20
    assert row["factor_mix_live_enablement_policy"]["policy_version"] == FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION
    assert "qvlm_risk_parity_vs_equal_weight_factor_mix_same_universe" in (
        row["factor_mix_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "risk_parity_weighting_history" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_qvlm_component_index_and_methodology_version_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qvlm_quality_value_low_vol_momentum_component_index_return_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_risk_parity_weight_formula_and_factor_vol_estimation_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "factor_covariance_correlation_and_rebalance_window_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "qvlm_12pct_cap_and_component_overlap_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "factor_mix_leave_one_out_ablation" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert any("hssbmfrpe.pdf" in url for url in row["research_evidence_urls"])
    assert any("IM_hssbmfrpe.pdf" in url for url in row["research_evidence_urls"])
    assert any("all-indexes/hssbmfew" in url for url in row["research_evidence_urls"])
    assert any("msci.com/indexes/index/705097" in url for url in row["research_evidence_urls"])
    assert any("MSCI_Factor_Mix_Indexes_Methodology" in url for url in row["research_evidence_urls"])
    assert any("Quality_Mix" in url or "quality-mix" in url for url in row["research_evidence_urls"])
    assert any("risk-parity versus equal-weight" in item for item in row["profile_specific_next_evidence"])
    assert any("12% capping lineage" in item for item in row["profile_specific_next_evidence"])
    assert any("component-index returns" in item for item in row["profile_specific_next_evidence"])
    assert any("capped-methodology history" in item for item in row["profile_specific_next_evidence"])
    assert any("covariance/correlation" in item for item in row["profile_specific_next_evidence"])


def test_factor_mix_live_enablement_policy_requires_ablation_stress_and_provenance():
    policy = build_factor_mix_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION
    assert "qvlm_risk_parity_vs_equal_weight_factor_mix_same_universe" in policy["required_ablation_tests"]
    assert "hsi_qvlm_risk_parity_vs_hsi_equal_weight_factor_mix_same_universe" in (
        policy["required_ablation_tests"]
    )
    assert "msci_equal_weight_qvl_vs_hsi_qvlm_with_momentum_sleeve" in policy["required_ablation_tests"]
    assert "msci_hk_factor_mix_equal_weight_qvl_vs_hsi_risk_parity_qvlm_without_momentum" in (
        policy["required_ablation_tests"]
    )
    assert "component_index_overlap_adjusted_vs_naive_factor_sleeve_blend" in policy["required_ablation_tests"]
    assert "factor_crowding_and_low_volatility_reversal_window" in policy["required_stress_tests"]
    assert "factor_correlation_breakdown_and_covariance_instability_window" in policy["required_stress_tests"]
    assert "qvlm_12pct_cap_sector_and_single_name_concentration_window" in policy["required_stress_tests"]
    assert "component_index_overlap_and_capping_turnover_spike_window" in policy["required_stress_tests"]
    assert "factor_volatility_and_risk_parity_weight_history" in policy["required_data_provenance"]
    assert "hsi_qvlm_component_index_and_methodology_version_history" in policy["required_data_provenance"]
    assert "hsi_qvlm_quality_value_low_vol_momentum_component_index_return_history" in (
        policy["required_data_provenance"]
    )
    assert "msci_hk_factor_mix_a_series_equal_weight_qvl_history" in policy["required_data_provenance"]
    assert "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history" in (
        policy["required_data_provenance"]
    )
    assert "factor_covariance_correlation_and_rebalance_window_history" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("hssbmfrpe.pdf" in url for url in policy["source_reference_urls"])
    assert any("IM_hssbmfrpe.pdf" in url for url in policy["source_reference_urls"])
    assert any("factor-mix-a-series-indexes" in url for url in policy["source_reference_urls"])


def test_quality_growth_low_volatility_row_carries_active_policy_and_external_evidence():
    row = build_snapshot_promotion_row("hk_qglv")

    assert row["profile"] == "hk_quality_growth_low_volatility"
    assert row["priority"] == 4
    assert row["promotion_bucket"] == "quality_growth_snapshot_candidate"
    assert row["recommended_live_enablement_stage"] == "quality_growth_low_vol_after_first_quality_candidates"
    assert row["quality_growth_live_enablement_policy"]["policy_version"] == QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION
    assert "quality_growth_vs_quality_only_vs_growth_only_vs_low_vol_only" in (
        row["quality_growth_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "hsi_qglv_four_component_score_vs_raw_quality_growth_inputs" in (
        row["quality_growth_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "revenue_earnings_roa_growth_history" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "quality_growth_low_vol_factor_ablation" in row["production_source_audit_policy"]["required_boolean_fields"]
    assert "msci_quality_roe_earnings_stability_and_leverage_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_winsorized_zscore_and_component_weight_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "minimum_volatility_optimizer_constraint_history" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "cash_conversion_accruals_and_quality_trap_controls" in (
        row["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("hsqglve.pdf" in url for url in row["research_evidence_urls"])
    assert any("msci.com/indexes/index/721604" in url for url in row["research_evidence_urls"])
    assert any("60ebccab" in url for url in row["research_evidence_urls"])
    assert any("quality-indexes" in url for url in row["research_evidence_urls"])
    assert any("minimum-volatility-indexes" in url for url in row["research_evidence_urls"])
    assert any("IM_hssbisve.pdf" in url for url in row["research_evidence_urls"])
    assert any("Growth in ROA adjusted by P/B" in item for item in row["profile_specific_next_evidence"])
    assert any("MSCI quality variables" in item for item in row["profile_specific_next_evidence"])
    assert any("minimum-volatility optimizer" in item for item in row["profile_specific_next_evidence"])
    assert any("growth deceleration" in item for item in row["profile_specific_next_evidence"])


def test_quality_growth_live_enablement_policy_requires_ablation_stress_and_provenance():
    policy = build_quality_growth_live_enablement_policy()

    assert policy["required"] is True
    assert policy["policy_version"] == QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION
    assert "quality_growth_low_vol_vs_low_vol_dividend_same_universe" in policy["required_ablation_tests"]
    assert "msci_quality_roe_earnings_stability_leverage_vs_hsi_qglv_same_universe" in (
        policy["required_ablation_tests"]
    )
    assert "hsi_qglv_four_component_score_vs_raw_quality_growth_inputs" in policy["required_ablation_tests"]
    assert "min_vol_optimizer_vs_simple_low_vol_beta_drawdown_filter" in policy["required_ablation_tests"]
    assert "hsi_low_vol_quality_screen_vs_simple_12m_volatility_filter" in policy["required_ablation_tests"]
    assert "growth_deceleration_and_earnings_revision_window" in policy["required_stress_tests"]
    assert "qglv_component_missingness_restatement_and_negative_equity_window" in policy["required_stress_tests"]
    assert "quality_trap_high_roe_low_cash_conversion_window" in policy["required_stress_tests"]
    assert "real_estate_financials_concentration_and_leverage_window" in policy["required_stress_tests"]
    assert "point_in_time_revenue_earnings_roa_growth_history" in policy["required_data_provenance"]
    assert "msci_quality_roe_earnings_stability_and_leverage_history" in policy["required_data_provenance"]
    assert "hsi_qglv_winsorized_zscore_and_component_weight_history" in policy["required_data_provenance"]
    assert "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history" in policy["required_data_provenance"]
    assert "minimum_volatility_optimizer_constraint_history" in policy["required_data_provenance"]
    assert policy["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert any("IM_hsqglve.pdf" in url for url in policy["source_reference_urls"])
    assert any("quality-indexes" in url for url in policy["source_reference_urls"])
    assert any("minimum-volatility-indexes" in url for url in policy["source_reference_urls"])


def test_free_cash_flow_row_carries_current_hsi_and_sp_evidence():
    row = build_snapshot_promotion_row("hk_free_cash_flow_quality")

    assert row["profile"] == "hk_free_cash_flow_quality"
    assert row["priority"] == 3
    assert row["promotion_bucket"] == "first_snapshot_candidate"
    assert any("hsscfcfe.pdf" in url for url in row["research_evidence_urls"])
    assert any("IM_hsscfcfe.pdf" in url for url in row["research_evidence_urls"])
    assert any("methodology-sp-access-hk-fcf-50-index.pdf" in url for url in row["research_evidence_urls"])
    assert any("sp-access-hong-kong-dividend-free-cash-flow-index" in url for url in row["research_evidence_urls"])
    assert "fcf_formula_cash_flow_statement_lineage_history" in row["production_data_dependencies"]
    assert "enterprise_value_market_cap_debt_cash_fx_history" in row["production_data_dependencies"]
    assert "financial_real_estate_and_negative_fcf_exception_policy" in row["production_data_dependencies"]
    assert any("FCF formula lineage" in evidence for evidence in row["profile_specific_next_evidence"])


def test_list_snapshot_promotion_candidates_is_priority_sorted():
    candidates = list_snapshot_promotion_candidates()

    assert [candidate.priority for candidate in candidates] == sorted(candidate.priority for candidate in candidates)
    assert candidates[0].profile == "hk_low_vol_dividend_quality"


def test_print_snapshot_promotion_matrix_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["live_enablement_gate"] == SNAPSHOT_PROMOTION_GATE
    assert payload["runtime_enabled_count"] == 0
    assert payload["recommended_live_enablement_sequence"][:3] == [
        "hk_low_vol_dividend_quality",
        "hk_shareholder_yield_quality",
        "hk_free_cash_flow_quality",
    ]
    assert any(row["profile"] == "hk_shareholder_yield_quality" for row in payload["profiles"])
