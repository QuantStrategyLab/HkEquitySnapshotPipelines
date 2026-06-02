from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.snapshot_readiness import build_snapshot_readiness, build_snapshot_readiness_matrix

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "print_snapshot_readiness.py"


def test_snapshot_readiness_blocks_scaffold_live_enablement():
    plan = build_snapshot_readiness("hk_liquid_momentum", platform_id="longbridge")

    assert plan["profile"] == "hk_liquid_momentum_quality"
    assert plan["runtime_enabled"] is False
    assert plan["status"] == "architecture_scaffold_not_live_enabled"
    assert plan["promotion_scope"] == "research_only_scaffold"
    assert plan["live_enablement_work_queue"] is False
    assert plan["requires_full_backtest_now"] is False
    assert plan["evidence_tooling_scope"] == "research_only_no_live_enablement_package"
    assert plan["manifest_required_by_runtime"] is True
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_liquid_momentum_quality_feature_snapshot_latest.csv"
    )
    assert plan["artifact_validation"]["required"] is True
    assert "hkeq-validate-snapshot-artifact-pack" in plan["artifact_validation"]["command"]
    assert plan["live_enablement_evidence_validation"]["required"] is True
    assert "hkeq-validate-live-enable-evidence" in plan["live_enablement_evidence_validation"]["command"]
    assert "--print-template" in plan["live_enablement_evidence_validation"]["template_command"]
    assert any("three independent OOS folds" in item for item in plan["live_enablement_requirements"])
    assert plan["live_enablement_thresholds"] == {
        "max_allowed_backtest_drawdown": 0.30,
        "min_return_to_drawdown_ratio": 0.50,
        "min_required_oos_fold_count": 3,
        "max_single_period_return_contribution": 0.60,
        "max_allowed_annualized_turnover": 1.50,
        "min_required_rebalance_windows": 3,
        "min_required_walk_forward_years": 3.0,
    }
    assert plan["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert "signature=" in plan["evidence_uri_policy"]["rejected_query_markers"]
    assert plan["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert plan["evidence_freshness_policy"]["max_allowed_age_days_by_section"]["walk_forward_backtest"] == 90
    assert "published_manifest_uri" in plan["artifact_provenance_policy"]["required_uri_fields"]
    assert plan["execution_capacity_policy"]["min_median_daily_turnover_hkd"] == 50_000_000
    assert plan["execution_capacity_policy"]["max_rebalance_adv_fraction"] == 0.10
    assert plan["rollout_risk_policy"]["max_cumulative_drawdown_tripwire"] == 0.05
    assert plan["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert "notification_delivery_log_uri" in plan["notification_audit_policy"]["required_uri_fields"]
    assert plan["dry_run_order_preview_policy"]["policy_version"] == "hk_dry_run_order_preview_provenance.v1"
    assert "raw_order_preview_uri" in plan["dry_run_order_preview_policy"]["required_uri_fields"]
    assert plan["momentum_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_momentum_live_enablement_policy.v1"
    )
    assert "residual_vs_liquid_vs_composite_same_universe" in (
        plan["momentum_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "hsi_hstech_sharp_reversal_window" in plan["momentum_live_enablement_policy"]["required_stress_tests"]
    assert "risk_adjusted_momentum_volatility_normalization_history" in (
        plan["momentum_live_enablement_policy"]["required_data_provenance"]
    )
    assert "high_watermark_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "momentum_6m_12m_one_month_skip_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "risk_adjusted_momentum_volatility_normalization_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "momentum_reversal_skip_and_crash_controls" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "survivorship_safe_universe" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "source_coverage_start" in plan["production_source_audit_policy"]["required_fields"]
    assert "source_quality_report_uri" in plan["production_source_audit_policy"]["required_uri_fields"]
    assert any("IM_hssbisme.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("711028" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("Sample artifacts" in reason for reason in plan["blocking_reasons"])
    assert any("research-only scaffold" in reason for reason in plan["blocking_reasons"])
    assert any("runtime_enabled" in requirement for requirement in plan["live_enablement_requirements"])
    assert any("one-month-skip" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("walk-forward" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_blue_chip_baseline_requires_policy_evidence():
    plan = build_snapshot_readiness("hk_blue_chip_snapshot", platform_id="longbridge")

    assert plan["profile"] == "hk_blue_chip_leader_rotation"
    assert plan["runtime_enabled"] is False
    assert plan["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_baseline_rotation_live_enablement_policy.v1"
    )
    assert "blue_chip_rotation_vs_hsi_tracker_same_universe" in (
        plan["baseline_rotation_live_enablement_policy"]["required_ablation_tests"]
    )
    assert "point_in_time_hsi_constituent_history" in (
        plan["baseline_rotation_live_enablement_policy"]["required_data_provenance"]
    )
    assert "hsi_constituent_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "board_lot_vcm_and_trading_session_rule_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("IM_hsie.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("Trading-Mechanism" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("strategy_policy_evidence" in requirement for requirement in plan["live_enablement_requirements"])


def test_snapshot_readiness_ibkr_env_uses_contract_artifacts():
    plan = build_snapshot_readiness("hk_dividend_quality", platform_id="ibkr")

    assert plan["profile"] == "hk_low_vol_dividend_quality"
    assert plan["promotion_scope"] == "first_snapshot_live_enablement_candidate"
    assert plan["live_enablement_work_queue"] is True
    assert plan["requires_full_backtest_now"] is True
    assert plan["evidence_tooling_scope"] == "active_first_snapshot_shared_evidence_tools"
    assert plan["platform_env_template"]["IBKR_MARKET"] == "HK"
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_low_vol_dividend_quality_factor_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["manifest"] == (
        "hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.0
    assert "dividend_yield_trap_controls" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "forecast_dividend_yield_estimate_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_vs_trailing_yield_benchmark_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "three_year_cash_dividend_record_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "price_crash_bottom_decile_screen_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "high_dividend_financial_soundness_screen_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sp_access_hk_low_vol_high_div_methodology_and_constituent_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("IM_hshylve.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "forecast-dividend-yield-strategy" in url
        for url in plan["production_source_audit_policy"]["source_reference_urls"]
    )
    assert any("IM_hsschkye.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "sp-low-volatility-high-dividend-indices-methodology" in url
        for url in plan["production_source_audit_policy"]["source_reference_urls"]
    )
    assert any("three-year cash-dividend" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("forecast dividend yield versus trailing dividend yield" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("price-crash screens" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("financial-soundness screens" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert plan["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )


def test_snapshot_readiness_supports_southbound_flow_alias():
    plan = build_snapshot_readiness("hk_southbound_momentum", platform_id="longbridge")

    assert plan["profile"] == "hk_southbound_flow_momentum"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_southbound_flow_momentum_flow_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["ranking"] == "hk_southbound_flow_momentum_ranking_latest.csv"
    assert plan["special_situation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert "stock_connect_holding_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "connect_trading_calendar_alignment" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "ccass_southbound_shareholding_percent_issued_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "eligible_stock_list_point_in_time_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "southbound_flow_raw_vs_vendor_reconciliation" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("mutualmarket.aspx?t=hk" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("2404122news" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("top-10 turnover" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_ah_premium_alias():
    plan = build_snapshot_readiness("hk_ah_premium", platform_id="ibkr")

    assert plan["profile"] == "hk_ah_premium_relative_value"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_ah_premium_relative_value_valuation_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["manifest"] == (
        "hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json"
    )
    assert plan["special_situation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert "ah_close_time_alignment_policy" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "fx_rate_source_provenance" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "ah_price_ratio_formula_and_market_cap_weight_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "ah_premium_extreme_level_and_false_reversal_controls" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("20240124T000000.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("20210914T000000.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("H50066_h50066hbooken_EN.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("AH pair mapping" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("price-ratio formula" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("share-class switch" in requirement for requirement in plan["profile_live_enablement_requirements"])



def test_snapshot_readiness_supports_central_soe_value_quality_alias():
    plan = build_snapshot_readiness("hk_policy_value_quality", platform_id="longbridge")

    assert plan["profile"] == "hk_central_soe_value_quality_select"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_central_soe_value_quality_select_factor_snapshot_latest.csv"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert "central_soe_flag_methodology_version_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sasac_central_soe_parent_list_effective_date_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_factor_score_zscore_industry_standardization_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_factor_score_missing_measure_average_policy_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_40pct_factor_screening_and_buffer_rule_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "central_soe_largest_shareholder_source_list_effective_date_drift_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("SASAC/MOF" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("missing-measure averaging" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("5% factor-index / 10% base-index capping" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("source-list effective-date drift" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("Southbound eligibility removal" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert "policy_event_and_governance_risk_controls" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert plan["policy_value_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_policy_value_live_enablement_policy.v1"
    )
    assert any("IM_hssccsme.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("central-SOE value-quality ranks" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_composite_factor_alias():
    plan = build_snapshot_readiness("hk_qvm_factor", platform_id="longbridge")

    assert plan["profile"] == "hk_composite_factor_quality_value_momentum"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["manifest"] == (
        "hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.20
    assert "momentum_sleeve_ablation_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "risk_adjusted_momentum_volatility_normalization_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("711028" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("one-month-skip" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("composite-factor ranks" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_free_cash_flow_alias():
    plan = build_snapshot_readiness("hk_free_cash_flow", platform_id="ibkr")

    assert plan["profile"] == "hk_free_cash_flow_quality"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_free_cash_flow_quality_factor_snapshot_latest.csv"
    )
    assert plan["artifact_filenames"]["manifest"] == (
        "hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert "free_cash_flow_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "fcf_formula_cash_flow_statement_lineage_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "enterprise_value_market_cap_debt_cash_fx_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "fundamental_restatement_and_reporting_date_asof_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("hsscfcfe.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("IM_hsscfcfe.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "methodology-sp-access-hk-fcf-50-index.pdf" in url
        for url in plan["production_source_audit_policy"]["source_reference_urls"]
    )
    assert any("free-cash-flow" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("formula lineage" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_residual_momentum_alias():
    plan = build_snapshot_readiness("hk_industry_neutral_momentum", platform_id="longbridge")

    assert plan["profile"] == "hk_residual_momentum_quality"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_residual_momentum_quality_factor_snapshot_latest.csv"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.20
    assert "momentum_6m_12m_one_month_skip_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "residual_momentum_model_fit_window_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "momentum_turnover_buffer_and_capacity_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("MSCI_Momentum_Indexes_Methodology" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("industry-neutral momentum" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("MSCI-style 6/12-month" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert plan["momentum_live_enablement_policy"]["required_profile_order"][0] == "hk_residual_momentum_quality"
    assert any("momentum-indexes" in url for url in plan["momentum_live_enablement_policy"]["source_reference_urls"])


def test_snapshot_readiness_supports_quality_growth_low_volatility_alias():
    plan = build_snapshot_readiness("hk_qglv", platform_id="longbridge")

    assert plan["profile"] == "hk_quality_growth_low_volatility"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_quality_growth_low_volatility_factor_snapshot_latest.csv"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert "revenue_earnings_roa_growth_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "quality_growth_low_vol_factor_ablation" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "msci_quality_roe_earnings_stability_and_leverage_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qglv_winsorized_zscore_and_component_weight_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "minimum_volatility_optimizer_constraint_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "sector_weight_cap_and_concentration_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("quality-indexes" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("60ebccab" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("minimum-volatility-indexes" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert plan["quality_growth_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_growth_live_enablement_policy.v1"
    )
    assert "hsi_qglv_four_component_score_vs_raw_quality_growth_inputs" in (
        plan["quality_growth_live_enablement_policy"]["required_ablation_tests"]
    )
    assert any("MSCI quality variables" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("Growth in ROA adjusted by P/B" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("minimum-volatility optimizer" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("winsorized z-scores" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("quality-growth low-vol ranks" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_factor_mix_qvlm_alias():
    plan = build_snapshot_readiness("hk_qvlm_risk_parity", platform_id="ibkr")

    assert plan["profile"] == "hk_factor_mix_qvlm_risk_parity"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.20
    assert "risk_parity_weighting_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_qvlm_component_index_and_methodology_version_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qvlm_parent_large_mid_cap_investable_universe_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_qvlm_quality_value_low_vol_momentum_component_index_return_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_equal_weight_factor_mix_benchmark_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "msci_hk_factor_mix_a_series_equal_weight_qvl_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "qvlm_12pct_cap_and_component_overlap_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "component_index_overlap_sector_cap_and_single_name_cap_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "factor_mix_leave_one_out_ablation" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert any("IM_hssbmfrpe.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("factor-mix-a-series-indexes" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert plan["factor_mix_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_factor_mix_live_enablement_policy.v1"
    )
    assert "msci_hk_factor_mix_equal_weight_qvl_vs_hsi_risk_parity_qvlm_without_momentum" in (
        plan["factor_mix_live_enablement_policy"]["required_ablation_tests"]
    )
    assert any("12% capping lineage" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("component-index return history" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("capped-methodology history" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("factor covariance/correlation" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("risk-parity factor weights" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_shareholder_yield_alias():
    plan = build_snapshot_readiness("hk_capital_return_quality", platform_id="ibkr")

    assert plan["profile"] == "hk_shareholder_yield_quality"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["IBKR_FEATURE_SNAPSHOT_PATH"] == (
        "hk_shareholder_yield_quality_factor_snapshot_latest.csv"
    )
    assert plan["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert "hkex_buyback_disclosure_history" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "hkex_next_day_share_repurchase_return_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_estimate_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "forecast_dividend_yield_vs_trailing_yield_benchmark_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "treasury_share_retention_cancellation_and_resale_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("sharerepur" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any(
        "forecast-dividend-yield-strategy" in url
        for url in plan["production_source_audit_policy"]["source_reference_urls"]
    )
    assert any("repurchase-securities-and-treasury-shares" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("forecast dividend yield versus trailing dividend yield" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("shareholder-yield ranks" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("treasury-share retention" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("post-buyback financing" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_supports_index_event_alias():
    plan = build_snapshot_readiness("hk_index_event", platform_id="longbridge")

    assert plan["profile"] == "hk_index_rebalance_event"
    assert plan["runtime_enabled"] is False
    assert plan["platform_env_template"]["LONGBRIDGE_FEATURE_SNAPSHOT_PATH"] == (
        "hk_index_rebalance_event_event_calendar_snapshot_latest.csv"
    )
    assert plan["special_situation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert "official_review_result_source_uri" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "event_crowding_slippage_controls" in plan["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_quarterly_review_schedule_and_cutoff_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_index_methodology_and_operation_guide_version_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_review_schedule_file_version_and_effective_date_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_next_review_notice_timestamp_and_scope_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_review_result_press_release_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_review_result_timestamp_constituent_weight_and_proforma_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "market_on_close_order_type_price_limit_and_random_close_policy" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "hkex_cas_order_type_random_close_price_limit_and_rejection_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert "closing_auction_imbalance_passive_flow_and_spread_history" in (
        plan["production_source_audit_policy"]["required_boolean_fields"]
    )
    assert any("is_update.xlsx" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("20260522T174500.pdf" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("Trading/CAS" in url for url in plan["production_source_audit_policy"]["source_reference_urls"])
    assert any("review calendars" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("pro-forma" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("two-stage price-limit" in requirement for requirement in plan["profile_live_enablement_requirements"])
    assert any("Closing Auction Session" in requirement for requirement in plan["profile_live_enablement_requirements"])


def test_snapshot_readiness_matrix_blocks_every_scaffold_profile():
    matrix = build_snapshot_readiness_matrix(platform_id="ibkr")

    assert matrix["platform"] == "ibkr"
    assert matrix["live_enable_gate"] == "blocked_until_production_evidence"
    assert matrix["runtime_enabled_count"] == 0
    assert matrix["blocked_profile_count"] == matrix["profile_count"]
    assert "production_snapshot_source_audit" in matrix["required_evidence_categories"]
    assert "production_source_uri_and_quality_report_provenance" in matrix["required_evidence_categories"]
    assert "artifact_pack_validation" in matrix["required_evidence_categories"]
    assert "live_enablement_evidence_validation" in matrix["required_evidence_categories"]
    assert "turnover_and_cost_model_limits" in matrix["required_evidence_categories"]
    assert "production_source_profile_specific_fields" in matrix["required_evidence_categories"]
    assert "baseline_rotation_ablation_hsi_constituent_and_execution_controls" in (
        matrix["required_evidence_categories"]
    )
    assert "quality_yield_ablation_and_yield_trap_controls" in matrix["required_evidence_categories"]
    assert "quality_growth_ablation_growth_deceleration_and_low_vol_controls" in matrix["required_evidence_categories"]
    assert "factor_mix_risk_parity_ablation_and_factor_volatility_controls" in matrix["required_evidence_categories"]
    assert "momentum_factor_ablation_descriptor_reconciliation_and_crash_controls" in (
        matrix["required_evidence_categories"]
    )
    assert "policy_value_government_ownership_and_concentration_controls" in matrix["required_evidence_categories"]
    assert "special_situation_signal_decay_crowding_and_calendar_alignment_controls" in (
        matrix["required_evidence_categories"]
    )
    assert "artifact_publication_provenance" in matrix["required_evidence_categories"]
    assert "fresh_section_evidence_generated_at" in matrix["required_evidence_categories"]
    assert "execution_capacity_and_liquidity_limits" in matrix["required_evidence_categories"]
    assert "dry_run_order_preview_artifact_provenance" in matrix["required_evidence_categories"]
    assert "staged_rollout_tripwires_and_rollback" in matrix["required_evidence_categories"]
    assert "bilingual_notification_delivery_log" in matrix["required_evidence_categories"]
    assert matrix["evidence_uri_policy"]["required"] is True
    assert matrix["artifact_provenance_policy"]["sha256_hex_length"] == 64
    assert matrix["evidence_freshness_policy"]["required"] is True
    assert matrix["execution_capacity_policy"]["required"] is True
    assert matrix["rollout_risk_policy"]["required"] is True
    assert matrix["notification_audit_policy"]["schema_version"] == "hk_live_enablement_notification.v1"
    assert matrix["dry_run_order_preview_policy"]["required"] is True
    assert matrix["baseline_rotation_live_enablement_policy"]["required"] is True
    assert matrix["quality_yield_live_enablement_policy"]["required"] is True
    assert matrix["quality_growth_live_enablement_policy"]["required"] is True
    assert matrix["factor_mix_live_enablement_policy"]["required"] is True
    assert matrix["momentum_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_momentum_live_enablement_policy.v1"
    )
    assert matrix["policy_value_live_enablement_policy"]["required"] is True
    assert matrix["special_situation_live_enablement_policy"]["required"] is True
    assert {
        "hk_low_vol_dividend_quality",
        "hk_liquid_momentum_quality",
        "hk_southbound_flow_momentum",
        "hk_ah_premium_relative_value",
        "hk_central_soe_value_quality_select",
        "hk_composite_factor_quality_value_momentum",
        "hk_free_cash_flow_quality",
        "hk_factor_mix_qvlm_risk_parity",
        "hk_index_rebalance_event",
        "hk_quality_growth_low_volatility",
        "hk_blue_chip_leader_rotation",
    }.issubset(set(matrix["blocked_profiles"]))


def test_print_snapshot_readiness_json():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--profile",
            "hk_blue_chip_leader_rotation",
            "--platform",
            "ibkr",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_blue_chip_leader_rotation"
    assert payload["platform"] == "ibkr"
    assert payload["runtime_enabled"] is False
    assert payload["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert payload["artifact_provenance_policy"]["required"] is True
    assert payload["evidence_freshness_policy"]["required_field"] == "evidence_generated_at"
    assert payload["execution_capacity_policy"]["max_single_order_adv_fraction"] == 0.025
    assert payload["rollout_risk_policy"]["required"] is True
    assert payload["notification_audit_policy"]["required"] is True
    assert payload["dry_run_order_preview_policy"]["required"] is True
    assert payload["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_baseline_rotation_live_enablement_policy.v1"
    )
    assert "benchmark_relative_momentum_history" in payload["production_source_audit_policy"]["required_boolean_fields"]
    assert "hsi_constituent_history" in payload["production_source_audit_policy"]["required_boolean_fields"]


def test_print_snapshot_readiness_all_json():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--all",
            "--platform",
            "longbridge",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["platform"] == "longbridge"
    assert payload["runtime_enabled_count"] == 0
    assert payload["blocked_profile_count"] == payload["profile_count"]
    assert payload["evidence_uri_policy"]["required"] is True
    assert payload["artifact_provenance_policy"]["required"] is True
    assert payload["evidence_freshness_policy"]["required"] is True
    assert payload["execution_capacity_policy"]["required"] is True
    assert payload["rollout_risk_policy"]["required"] is True
    assert payload["notification_audit_policy"]["expected_event_type"] == "hk_snapshot_live_enablement_dry_run"
    assert payload["dry_run_order_preview_policy"]["required"] is True
    assert payload["baseline_rotation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_baseline_rotation_live_enablement_policy.v1"
    )
    assert payload["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )
    assert payload["momentum_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_momentum_live_enablement_policy.v1"
    )
    assert payload["special_situation_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_special_situation_live_enablement_policy.v1"
    )
    assert any(profile["profile"] == "hk_index_rebalance_event" for profile in payload["profiles"])
