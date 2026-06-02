from __future__ import annotations

MAX_ALLOWED_BACKTEST_DRAWDOWN = 0.30
MIN_RETURN_TO_DRAWDOWN_RATIO = 0.50
DEFAULT_MAX_ALLOWED_ANNUALIZED_TURNOVER = 1.50
DEFAULT_MIN_REQUIRED_REBALANCE_WINDOWS = 3
DEFAULT_MIN_ADV_WINDOW_TRADING_DAYS = 20
DEFAULT_MIN_MEDIAN_DAILY_TURNOVER_HKD = 20_000_000
DEFAULT_MAX_SINGLE_ORDER_ADV_FRACTION = 0.025
DEFAULT_MAX_REBALANCE_ADV_FRACTION = 0.10
MIN_REQUIRED_WALK_FORWARD_YEARS = 3.0

MAX_ALLOWED_ANNUALIZED_TURNOVER_BY_PROFILE: dict[str, float] = {
    "hk_ah_premium_relative_value": 1.20,
    "hk_blue_chip_leader_rotation": 1.50,
    "hk_central_soe_value_quality_select": 1.00,
    "hk_composite_factor_quality_value_momentum": 1.20,
    "hk_factor_mix_qvlm_risk_parity": 1.20,
    "hk_free_cash_flow_quality": 1.00,
    "hk_index_rebalance_event": 2.00,
    "hk_liquid_momentum_quality": 1.50,
    "hk_low_vol_dividend_quality": 1.00,
    "hk_quality_growth_low_volatility": 1.00,
    "hk_residual_momentum_quality": 1.20,
    "hk_shareholder_yield_quality": 1.00,
    "hk_southbound_flow_momentum": 1.50,
}

MIN_REQUIRED_REBALANCE_WINDOWS_BY_PROFILE: dict[str, int] = {
    "hk_index_rebalance_event": 1,
}

MIN_MEDIAN_DAILY_TURNOVER_HKD_BY_PROFILE: dict[str, int] = {
    "hk_ah_premium_relative_value": 50_000_000,
    "hk_blue_chip_leader_rotation": 50_000_000,
    "hk_central_soe_value_quality_select": 50_000_000,
    "hk_composite_factor_quality_value_momentum": 50_000_000,
    "hk_factor_mix_qvlm_risk_parity": 50_000_000,
    "hk_index_rebalance_event": 100_000_000,
    "hk_liquid_momentum_quality": 50_000_000,
    "hk_residual_momentum_quality": 50_000_000,
    "hk_southbound_flow_momentum": 50_000_000,
}

REQUIRED_BENCHMARK_SYMBOL_BY_PROFILE: dict[str, str] = {
    "hk_ah_premium_relative_value": "02800",
    "hk_blue_chip_leader_rotation": "02800",
    "hk_central_soe_value_quality_select": "02800",
    "hk_composite_factor_quality_value_momentum": "02800",
    "hk_factor_mix_qvlm_risk_parity": "02800",
    "hk_free_cash_flow_quality": "02800",
    "hk_index_rebalance_event": "02800",
    "hk_liquid_momentum_quality": "02800",
    "hk_low_vol_dividend_quality": "02800",
    "hk_quality_growth_low_volatility": "02800",
    "hk_residual_momentum_quality": "02800",
    "hk_shareholder_yield_quality": "02800",
    "hk_southbound_flow_momentum": "02800",
}

REQUIRED_BACKTEST_COST_MODEL_FIELDS: tuple[str, ...] = (
    "hk_fees_and_levies",
    "stamp_duty_or_exemption",
    "slippage",
    "lot_size_rounding",
    "suspension_handling",
)

REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS: tuple[str, ...] = (
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

REQUIRED_EXECUTION_CAPACITY_FIELDS: tuple[str, ...] = (
    "liquidity_cap_verified",
    "board_lot_rounding_verified",
    "odd_lot_avoidance_verified",
    "market_session_routing_verified",
    "vcm_price_band_controls_verified",
)

COMMON_PRODUCTION_SOURCE_AUDIT_FIELDS: tuple[str, ...] = (
    "point_in_time_asof",
    "adjusted_prices",
    "corporate_actions",
    "suspensions",
    "stale_price_checks",
    "missing_field_checks",
    "symbol_mapping",
    "survivorship_safe_universe",
)

PRODUCTION_SOURCE_AUDIT_REQUIRED_FIELDS: tuple[str, ...] = (
    "source_name",
    "source_coverage_start",
    "source_coverage_end",
)

PRODUCTION_SOURCE_AUDIT_URI_FIELDS: tuple[str, ...] = (
    "production_source_uri",
    "source_quality_report_uri",
    "point_in_time_data_dictionary_uri",
)

REQUIRED_PRODUCTION_SOURCE_AUDIT_FIELDS_BY_PROFILE: dict[str, tuple[str, ...]] = {
    "hk_ah_premium_relative_value": (
        "ah_pair_mapping",
        "a_h_close_alignment",
        "ah_close_time_alignment_policy",
        "fx_history",
        "fx_rate_source_provenance",
        "stock_connect_eligibility_history",
        "share_class_corporate_action_adjustments",
        "h_share_liquidity_and_short_sale_constraint_review",
        "ah_premium_index_constituent_history",
        "ah_price_ratio_formula_and_market_cap_weight_history",
        "ah_smart_share_class_switch_threshold_history",
        "a_share_access_shorting_settlement_and_fx_constraint_review",
        "ah_premium_extreme_level_and_false_reversal_controls",
    ),
    "hk_blue_chip_leader_rotation": (
        "hsi_constituent_history",
        "hsi_methodology_and_review_history",
        "universe_and_sector_history",
        "benchmark_relative_momentum_history",
        "current_price_to_52_week_high_history",
        "liquidity_history",
        "board_lot_vcm_and_trading_session_rule_history",
        "rebalance_buffer_turnover_and_capacity_history",
        "corporate_action_suspension_and_stale_price_history",
    ),
    "hk_central_soe_value_quality_select": (
        "government_shareholder_classification_history",
        "largest_shareholder_and_ownership_pct_history",
        "central_soe_flag_methodology_version_history",
        "sasac_central_soe_parent_list_effective_date_history",
        "mof_central_financial_soe_list_effective_date_history",
        "largest_shareholder_look_through_chain_and_source_uri_history",
        "state_ownership_threshold_policy",
        "hsi_central_soe_value_quality_factor_index_constituent_history",
        "hsi_factor_score_zscore_industry_standardization_history",
        "hsi_factor_score_missing_measure_average_policy_history",
        "hsi_40pct_factor_screening_and_buffer_rule_history",
        "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history",
        "quality_value_low_vol_momentum_factor_history",
        "sector_neutralization_policy",
        "policy_event_and_governance_risk_controls",
        "public_float_parent_support_connected_transaction_and_dividend_policy_history",
        "central_soe_largest_shareholder_source_list_effective_date_drift_history",
        "southbound_eligibility_history",
        "hkex_southbound_eligible_security_point_in_time_history",
        "liquidity_suspension_and_corporate_action_history",
    ),
    "hk_composite_factor_quality_value_momentum": (
        "quality_factor_history",
        "value_factor_history",
        "momentum_trend_history",
        "momentum_6m_12m_one_month_skip_history",
        "risk_adjusted_momentum_volatility_normalization_history",
        "low_volatility_beta_history",
        "quality_value_momentum_low_vol_factor_formula_lineage",
        "factor_score_winsorization_neutralization_history",
        "momentum_sleeve_ablation_history",
        "factor_turnover_buffer_and_capacity_history",
        "southbound_eligibility_history",
    ),
    "hk_factor_mix_qvlm_risk_parity": (
        "quality_value_momentum_low_vol_factor_history",
        "factor_volatility_history",
        "risk_parity_weighting_history",
        "hsi_qvlm_component_index_and_methodology_version_history",
        "hsi_qvlm_parent_large_mid_cap_investable_universe_history",
        "hsi_qvlm_quality_value_low_vol_momentum_component_index_return_history",
        "hsi_risk_parity_weight_formula_and_factor_vol_estimation_history",
        "hsi_equal_weight_factor_mix_benchmark_history",
        "msci_hk_factor_mix_a_series_equal_weight_qvl_history",
        "msci_hk_factor_mix_component_index_equal_weight_and_capped_methodology_history",
        "factor_covariance_correlation_and_rebalance_window_history",
        "factor_score_formula_lineage_and_winsorization_history",
        "qvlm_12pct_cap_and_component_overlap_history",
        "component_index_overlap_sector_cap_and_single_name_cap_history",
        "factor_leg_turnover_capacity_and_crowding_history",
        "factor_mix_leave_one_out_ablation",
        "sector_neutralization_policy",
        "southbound_eligibility_history",
        "valuation_fundamental_reporting_date_history",
    ),
    "hk_free_cash_flow_quality": (
        "free_cash_flow_history",
        "enterprise_value_history",
        "reporting_date_availability",
        "negative_fcf_policy",
        "sector_normalization",
        "fcf_reporting_date_point_in_time",
        "restatement_stale_fundamental_controls",
        "financial_real_estate_sector_policy",
        "fcf_formula_cash_flow_statement_lineage_history",
        "enterprise_value_market_cap_debt_cash_fx_history",
        "financial_real_estate_and_negative_fcf_exception_policy",
        "fcf_sector_normalization_and_concentration_history",
        "fundamental_restatement_and_reporting_date_asof_history",
    ),
    "hk_index_rebalance_event": (
        "official_index_review_history",
        "official_index_schedule_source_uri",
        "official_review_result_source_uri",
        "hsi_quarterly_review_schedule_and_cutoff_history",
        "hsi_index_methodology_and_operation_guide_version_history",
        "hsi_review_schedule_file_version_and_effective_date_history",
        "hsi_next_review_notice_timestamp_and_scope_history",
        "hsi_review_result_press_release_history",
        "hsi_review_result_timestamp_constituent_weight_and_proforma_history",
        "hsi_constituent_added_deleted_effective_date_history",
        "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history",
        "hsi_fast_entry_suspension_and_buffer_rule_exception_history",
        "announcement_and_effective_timestamps",
        "announcement_to_effective_date_window_policy",
        "event_side_labels",
        "liquidity_slippage_estimates",
        "event_crowding_slippage_controls",
        "market_on_close_order_type_price_limit_and_random_close_policy",
        "hkex_cas_order_type_random_close_price_limit_and_rejection_history",
        "closing_auction_volume_spread_and_passive_flow_history",
        "closing_auction_imbalance_passive_flow_and_spread_history",
        "event_window_market_on_close_execution_policy",
    ),
    "hk_liquid_momentum_quality": (
        "benchmark_relative_momentum_history",
        "momentum_6m_12m_one_month_skip_history",
        "hsi_smart_beta_momentum_descriptor_history",
        "msci_hk_momentum_benchmark_comparison_history",
        "risk_adjusted_momentum_volatility_normalization_history",
        "momentum_reversal_skip_and_crash_controls",
        "momentum_turnover_buffer_and_capacity_history",
        "liquidity_history",
        "market_cap_history",
        "high_watermark_history",
    ),
    "hk_low_vol_dividend_quality": (
        "fundamentals_point_in_time",
        "southbound_trading_eligibility_history",
        "dividend_history",
        "forecast_dividend_yield_estimate_history",
        "forecast_dividend_yield_vs_trailing_yield_benchmark_history",
        "three_year_cash_dividend_record_history",
        "earnings_and_payout_fields",
        "payout_ratio_bounds_history",
        "large_mid_cap_market_value_shortlist_history",
        "one_year_high_volatility_exclusion_history",
        "high_dividend_financial_soundness_screen_history",
        "sp_access_hk_low_vol_high_div_methodology_and_constituent_history",
        "hsi_vs_sp_low_vol_high_div_rebalance_and_capping_history",
        "volatility_beta_history",
        "sector_classification_history",
        "dividend_yield_trap_controls",
        "price_crash_bottom_decile_screen_history",
        "payout_coverage_and_earnings_positive_history",
        "low_volatility_beta_drawdown_stress",
        "sector_concentration_caps",
    ),
    "hk_quality_growth_low_volatility": (
        "revenue_earnings_roa_growth_history",
        "roe_accruals_cash_flow_debt_history",
        "msci_quality_roe_earnings_stability_and_leverage_history",
        "msci_quality_descriptor_return_on_equity_earnings_variability_leverage_history",
        "hsi_quality_growth_low_vol_score_formula_lineage",
        "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history",
        "hsi_qglv_winsorized_zscore_and_component_weight_history",
        "hsi_qglv_negative_equity_financials_and_missing_factor_policy_history",
        "reporting_date_point_in_time",
        "valuation_normalization_history",
        "growth_signal_reporting_date_and_restatement_asof_history",
        "cash_conversion_accruals_and_quality_trap_controls",
        "negative_equity_and_financials_policy",
        "volatility_beta_drawdown_history",
        "minimum_volatility_optimizer_constraint_history",
        "low_volatility_factor_beta_residual_volatility_history",
        "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history",
        "sector_classification_history",
        "sector_weight_cap_and_concentration_history",
        "southbound_eligibility_history",
        "sector_neutralization_policy",
        "quality_growth_low_vol_factor_ablation",
    ),
    "hk_residual_momentum_quality": (
        "industry_classification_point_in_time",
        "residual_model_reproducible",
        "residual_momentum_model_fit_window_history",
        "industry_relative_momentum_history",
        "benchmark_relative_returns",
        "momentum_6m_12m_one_month_skip_history",
        "hsi_smart_beta_momentum_descriptor_history",
        "msci_hk_momentum_benchmark_comparison_history",
        "risk_adjusted_momentum_volatility_normalization_history",
        "industry_sector_neutralization_history",
        "momentum_reversal_skip_and_crash_controls",
        "momentum_turnover_buffer_and_capacity_history",
        "beta_volatility_history",
    ),
    "hk_shareholder_yield_quality": (
        "dividend_history",
        "forecast_dividend_yield_estimate_history",
        "forecast_dividend_yield_vs_trailing_yield_benchmark_history",
        "hkex_buyback_disclosure_history",
        "hkex_next_day_share_repurchase_return_history",
        "share_count_history",
        "treasury_share_history",
        "treasury_share_retention_cancellation_and_resale_history",
        "free_cash_flow_roe_debt_history",
        "dilution_controls",
        "buyback_share_count_reconciliation",
        "treasury_share_resale_controls",
        "treasury_share_moratorium_blackout_and_connected_person_controls",
        "share_buyback_mandate_and_program_waiver_history",
        "post_buyback_new_issue_convertible_and_public_float_review",
        "dividend_fcf_coverage_controls",
        "hkex_disclosure_latency_audit",
    ),
    "hk_southbound_flow_momentum": (
        "stock_connect_daily_turnover",
        "southbound_holding_history",
        "stock_connect_holding_history",
        "connect_eligibility_history",
        "connect_trading_calendar_alignment",
        "holiday_aware_flow_calendar",
        "missing_flow_day_policy",
        "southbound_policy_event_stress_controls",
        "hkex_southbound_top10_turnover_and_market_turnover_history",
        "ccass_southbound_shareholding_percent_issued_history",
        "stock_connect_market_data_dissemination_change_history",
        "eligible_stock_list_point_in_time_history",
        "southbound_flow_raw_vs_vendor_reconciliation",
    ),
}

COMMON_PRODUCTION_SOURCE_REFERENCE_URLS: tuple[str, ...] = (
    "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities?sc_lang=en",
    "https://www.hkexnews.hk/",
)

EXECUTION_CAPACITY_REFERENCE_URLS: tuple[str, ...] = (
    "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
    "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/Securities-Market-Operations?sc_lang=en",
    "https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en",
)

PRODUCTION_SOURCE_REFERENCE_URLS_BY_PROFILE: dict[str, tuple[str, ...]] = {
    "hk_ah_premium_relative_value": (
        "https://www.hsi.com.hk/eng/indexes/all-indexes/ahpremium",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/chinaah",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/ahpremiume.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/index_flash/20240124T000000.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/blog/20210914T000000.pdf",
        "https://english.sse.com.cn/indices/indices/list/indexmethods/c/H50066_h50066hbooken_EN.pdf",
        "https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Statistics/Historical-Daily?sc_lang=en",
    ),
    "hk_blue_chip_leader_rotation": (
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hsi",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsie.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf",
        "https://www.hkex.com.hk/Market-Data/Statistics/Securities-Market?sc_lang=en",
        "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
        "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/VCM?sc_lang=en",
    ),
    "hk_central_soe_value_quality_select": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssccsme.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsoee.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscsoee.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssccsve.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssccsqe.pdf",
        "https://www.hsi.com.hk/solutions/factor-indexes/",
        "https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=en",
        "https://www.sasac.gov.cn/n2588045/n27271785/n27271792/index.html",
        "https://en.sasac.gov.cn/directorynames.html",
        "https://www.mof.gov.cn/zcsjtsgb/gfxwj/202007/t20200713_3583827.htm",
    ),
    "hk_composite_factor_quality_value_momentum": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbism",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf",
        "https://www.hsi.com.hk/solutions/factor-indexes/",
        "https://www.msci.com/indexes/group/momentum-indexes",
        "https://www.msci.com/indexes/index/711028",
        "https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf",
        "https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c",
    ),
    "hk_factor_mix_qvlm_risk_parity": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssbmfrpe.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbmfrpe.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbmfew",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf",
        "https://www.hsi.com.hk/solutions/factor-indexes/",
        "https://www.msci.com/indexes/factor-indexes/factor-mix-a-series-indexes",
        "https://www.msci.com/indexes/index/705097",
        "https://www.msci.com/documents/10199/e56a62f4-3ff6-40a7-a8e6-54a6de8e6763",
        "https://www.msci.com/eqb/methodology/meth_docs/MSCI_Factor_Mix_Indexes_Methodology_Apr16.pdf",
        "https://www.msci.com/research-and-insights/paper/the-msci-quality-mix-indexes",
    ),
    "hk_free_cash_flow_quality": (
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hsscfcf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscfcfe.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscfcfe.pdf",
        "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-free-cash-flow-50-index/",
        "https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-access-hk-fcf-50-index.pdf",
        "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/",
    ),
    "hk_index_rebalance_event": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_operation_guide_e.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/products/is_update.xlsx",
        "https://www.hsi.com.hk/static/uploads/contents/en/news/indexChgNotice/20260102T163000.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260213T174500.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260522T174500.pdf",
        "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/CAS?sc_lang=en",
        "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
    ),
    "hk_liquid_momentum_quality": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbism",
        "https://www.msci.com/indexes/group/momentum-indexes",
        "https://www.msci.com/indexes/index/711028",
        "https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf",
        "https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c",
    ),
    "hk_low_vol_dividend_quality": (
        "https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hslvie.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshdyie.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hshylv",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshylve.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hshylve.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hsschys",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsschyse.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsschkye.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20231214T000000.pdf",
        "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-low-volatility-high-dividend-index/",
        "https://www.spglobal.com/spdji/en/methodology/article/sp-low-volatility-high-dividend-indices-methodology/",
        "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index/",
    ),
    "hk_quality_growth_low_volatility": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsqglve.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsqglve.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisve.pdf",
        "https://www.hsi.com.hk/solutions/factor-indexes/",
        "https://www.msci.com/indexes/group/quality-indexes",
        "https://www.msci.com/indexes/index/721604",
        "https://www.msci.com/documents/10199/60ebccab-109f-6a16-8451-557498ea39fb",
        "https://www.msci.com/indexes/group/minimum-volatility-indexes/",
        "https://www.msci.com/documents/10199/1396fa66-b4bd-40f3-8dfb-0109895d94ac",
    ),
    "hk_residual_momentum_quality": (
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf",
        "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf",
        "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbism",
        "https://www.msci.com/indexes/group/momentum-indexes",
        "https://www.msci.com/indexes/index/711028",
        "https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf",
        "https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c",
    ),
    "hk_shareholder_yield_quality": (
        "https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar",
        "https://www3.hkexnews.hk/reports/sharerepur/sbn.asp",
        "https://www.hkex.com.hk/-/media/HKEX-Market/Listing/Rules-and-Guidance/Other-Resources/Listed-Issuers/LIR-Newsletter/newsletter_202506.pdf",
        "https://en-rules.hkex.com.hk/rulebook/9-repurchase-securities-and-treasury-shares",
        "https://en-rules.hkex.com.hk/entiresection/498",
        "https://www.hkex.com.hk/News/Regulatory-Announcements/2024/240412news?sc_lang=en",
        "https://www.hkex.com.hk/Listing/Education-Centre/Listed-Issuers/Share-Repurchase-and-Treasury-Shares?sc_lang=en",
        "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/",
    ),
    "hk_southbound_flow_momentum": (
        "https://www.hkex.com.hk/mutual-market/stock-connect/statistics?sc_lang=en",
        "https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Statistics/Historical-Daily?sc_lang=en",
        "https://www3.hkexnews.hk/sdw/search/mutualmarket.aspx?t=hk",
        "https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=en",
        "https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en",
        "https://www.hkex.com.hk/News/Market-Communications/2024/2404122news?sc_lang=en",
    ),
}


def get_max_allowed_annualized_turnover(profile: str) -> float:
    return MAX_ALLOWED_ANNUALIZED_TURNOVER_BY_PROFILE.get(
        str(profile or "").strip(),
        DEFAULT_MAX_ALLOWED_ANNUALIZED_TURNOVER,
    )


def get_min_required_rebalance_windows(profile: str) -> int:
    return MIN_REQUIRED_REBALANCE_WINDOWS_BY_PROFILE.get(
        str(profile or "").strip(),
        DEFAULT_MIN_REQUIRED_REBALANCE_WINDOWS,
    )


def get_min_median_daily_turnover_hkd(profile: str) -> int:
    return MIN_MEDIAN_DAILY_TURNOVER_HKD_BY_PROFILE.get(
        str(profile or "").strip(),
        DEFAULT_MIN_MEDIAN_DAILY_TURNOVER_HKD,
    )


def get_required_benchmark_symbol(profile: str) -> str:
    return REQUIRED_BENCHMARK_SYMBOL_BY_PROFILE.get(str(profile or "").strip(), "02800")


def get_required_production_source_audit_fields(profile: str) -> tuple[str, ...]:
    normalized = str(profile or "").strip()
    return (
        *COMMON_PRODUCTION_SOURCE_AUDIT_FIELDS,
        *REQUIRED_PRODUCTION_SOURCE_AUDIT_FIELDS_BY_PROFILE.get(normalized, ()),
    )


def get_production_source_reference_urls(profile: str) -> tuple[str, ...]:
    normalized = str(profile or "").strip()
    return tuple(
        dict.fromkeys(
            (
                *COMMON_PRODUCTION_SOURCE_REFERENCE_URLS,
                *PRODUCTION_SOURCE_REFERENCE_URLS_BY_PROFILE.get(normalized, ()),
            )
        )
    )


def build_production_source_audit_policy(profile: str) -> dict[str, object]:
    return {
        "required": True,
        "required_fields": list(PRODUCTION_SOURCE_AUDIT_REQUIRED_FIELDS),
        "required_uri_fields": list(PRODUCTION_SOURCE_AUDIT_URI_FIELDS),
        "required_boolean_fields": list(get_required_production_source_audit_fields(profile)),
        "source_reference_urls": list(get_production_source_reference_urls(profile)),
        "description": "Production snapshot source audits must prove point-in-time, survivorship-safe data coverage, stable source provenance, and data-quality reporting before live enablement.",
    }


def build_execution_capacity_policy(profile: str) -> dict[str, object]:
    return {
        "required": True,
        "min_adv_window_trading_days": DEFAULT_MIN_ADV_WINDOW_TRADING_DAYS,
        "min_median_daily_turnover_hkd": get_min_median_daily_turnover_hkd(profile),
        "max_single_order_adv_fraction": DEFAULT_MAX_SINGLE_ORDER_ADV_FRACTION,
        "max_rebalance_adv_fraction": DEFAULT_MAX_REBALANCE_ADV_FRACTION,
        "required_boolean_fields": list(REQUIRED_EXECUTION_CAPACITY_FIELDS),
        "source_reference_urls": list(EXECUTION_CAPACITY_REFERENCE_URLS),
        "description": "Platform dry-run evidence must prove HK board-lot routing, odd-lot avoidance, VCM/price-band controls, and conservative ADV capacity before live enablement.",
    }


def build_live_enablement_thresholds(profile: str) -> dict[str, float | int]:
    return {
        "max_allowed_backtest_drawdown": MAX_ALLOWED_BACKTEST_DRAWDOWN,
        "min_return_to_drawdown_ratio": MIN_RETURN_TO_DRAWDOWN_RATIO,
        "max_allowed_annualized_turnover": get_max_allowed_annualized_turnover(profile),
        "min_required_walk_forward_years": MIN_REQUIRED_WALK_FORWARD_YEARS,
        "min_required_rebalance_windows": get_min_required_rebalance_windows(profile),
    }


__all__ = [
    "DEFAULT_MAX_ALLOWED_ANNUALIZED_TURNOVER",
    "DEFAULT_MAX_REBALANCE_ADV_FRACTION",
    "DEFAULT_MAX_SINGLE_ORDER_ADV_FRACTION",
    "DEFAULT_MIN_ADV_WINDOW_TRADING_DAYS",
    "DEFAULT_MIN_MEDIAN_DAILY_TURNOVER_HKD",
    "DEFAULT_MIN_REQUIRED_REBALANCE_WINDOWS",
    "EXECUTION_CAPACITY_REFERENCE_URLS",
    "MAX_ALLOWED_ANNUALIZED_TURNOVER_BY_PROFILE",
    "MAX_ALLOWED_BACKTEST_DRAWDOWN",
    "MIN_RETURN_TO_DRAWDOWN_RATIO",
    "MIN_MEDIAN_DAILY_TURNOVER_HKD_BY_PROFILE",
    "MIN_REQUIRED_REBALANCE_WINDOWS_BY_PROFILE",
    "MIN_REQUIRED_WALK_FORWARD_YEARS",
    "COMMON_PRODUCTION_SOURCE_AUDIT_FIELDS",
    "COMMON_PRODUCTION_SOURCE_REFERENCE_URLS",
    "PRODUCTION_SOURCE_REFERENCE_URLS_BY_PROFILE",
    "REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS",
    "REQUIRED_BACKTEST_COST_MODEL_FIELDS",
    "REQUIRED_BENCHMARK_SYMBOL_BY_PROFILE",
    "REQUIRED_EXECUTION_CAPACITY_FIELDS",
    "REQUIRED_PRODUCTION_SOURCE_AUDIT_FIELDS_BY_PROFILE",
    "build_execution_capacity_policy",
    "build_production_source_audit_policy",
    "build_live_enablement_thresholds",
    "get_min_median_daily_turnover_hkd",
    "get_max_allowed_annualized_turnover",
    "get_min_required_rebalance_windows",
    "get_production_source_reference_urls",
    "get_required_production_source_audit_fields",
    "get_required_benchmark_symbol",
]
