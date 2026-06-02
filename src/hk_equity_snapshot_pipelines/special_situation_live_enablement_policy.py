from __future__ import annotations

from typing import Any

from .contracts import (
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
    HK_INDEX_REBALANCE_EVENT_PROFILE,
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
)
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_special_situation_live_enablement_policy.v1"

SPECIAL_SITUATION_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
    HK_INDEX_REBALANCE_EVENT_PROFILE,
)

SPECIAL_SITUATION_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "southbound_flow_vs_price_momentum_same_universe",
    "ah_premium_overlay_vs_plain_value_quality_same_universe",
    "ah_premium_extreme_level_vs_hsi_trough_timing_ablation",
    "ah_smart_share_class_switch_vs_long_only_h_share_overlay",
    "index_rebalance_event_window_vs_baseline_liquidity_filter",
    "index_add_delete_vs_review_candidate_probability_same_universe",
    "announcement_close_vs_effective_close_execution_window_ablation",
    "market_on_close_vs_next_open_execution_window_ablation",
    "official_schedule_vs_press_release_event_source_reconciliation",
    "proforma_weighted_add_delete_vs_equal_weight_event_trade_ablation",
    "flow_valuation_event_overlay_vs_first_quality_yield_candidates",
    "signal_decay_window_and_rebalance_frequency_ablation",
    "southbound_top10_turnover_vs_ccass_holding_change_same_universe",
)

SPECIAL_SITUATION_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "stock_connect_holiday_quota_or_trading_suspension_window",
    "southbound_policy_event_and_crowding_reversal_window",
    "southbound_realtime_data_suppression_and_top10_only_window",
    "ccass_southbound_shareholding_reporting_lag_and_eligibility_mismatch_window",
    "a_h_close_time_fx_and_exchange_holiday_misalignment_window",
    "ah_premium_widening_and_h_share_liquidity_stress_window",
    "ah_premium_extreme_level_false_reversal_window",
    "a_share_shorting_access_settlement_and_capital_control_constraint_window",
    "index_review_announcement_to_effective_date_crowding_window",
    "index_rebalance_add_delete_slippage_and_capacity_sensitivity",
    "quarterly_review_result_announcement_after_market_close_window",
    "effective_date_market_on_close_auction_and_passive_flow_window",
    "hsi_fast_entry_suspension_and_buffer_rule_exception_window",
    "closing_auction_random_close_and_price_limit_execution_window",
    "review_schedule_change_and_delayed_press_release_window",
    "cas_random_close_price_limit_and_order_rejection_window",
    "passive_flow_closing_auction_liquidity_gap_window",
)

SPECIAL_SITUATION_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "hkex_stock_connect_turnover_and_holding_history",
    "stock_connect_eligibility_and_trading_calendar_history",
    "hkex_southbound_top10_turnover_and_market_turnover_history",
    "ccass_southbound_shareholding_percent_issued_history",
    "stock_connect_market_data_dissemination_change_history",
    "southbound_flow_raw_vs_vendor_reconciliation",
    "ah_pair_mapping_close_alignment_and_fx_history",
    "ah_premium_index_constituent_and_price_ratio_history",
    "ah_smart_share_class_switch_threshold_history",
    "a_share_access_shorting_settlement_and_fx_constraint_review",
    "official_index_review_announcement_and_effective_date_history",
    "hsi_quarterly_review_schedule_and_cutoff_history",
    "hsi_index_methodology_and_operation_guide_version_history",
    "hsi_review_schedule_file_version_and_effective_date_history",
    "hsi_next_review_notice_timestamp_and_scope_history",
    "hsi_review_result_press_release_history",
    "hsi_review_result_timestamp_constituent_weight_and_proforma_history",
    "hsi_constituent_added_deleted_effective_date_history",
    "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history",
    "hsi_fast_entry_suspension_and_buffer_rule_exception_history",
    "market_on_close_order_type_price_limit_and_random_close_policy",
    "hkex_cas_order_type_random_close_price_limit_and_rejection_history",
    "closing_auction_volume_spread_and_passive_flow_history",
    "closing_auction_imbalance_passive_flow_and_spread_history",
    "event_side_label_and_corporate_action_history",
    "order_preview_liquidity_and_crowding_evidence",
)

SPECIAL_SITUATION_SOURCE_URLS: tuple[str, ...] = (
    "https://www.hkex.com.hk/mutual-market/stock-connect/statistics?sc_lang=en",
    "https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Statistics/Historical-Daily?sc_lang=en",
    "https://www3.hkexnews.hk/sdw/search/mutualmarket.aspx?t=hk",
    "https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=en",
    "https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en",
    "https://www.hkex.com.hk/News/Market-Communications/2024/2404122news?sc_lang=en",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/ahpremium",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/chinaah",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/ahpremiume.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/index_flash/20240124T000000.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/blog/20210914T000000.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_operation_guide_e.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/products/is_update.xlsx",
    "https://www.hsi.com.hk/static/uploads/contents/en/news/indexChgNotice/20260102T163000.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260213T174500.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260522T174500.pdf",
    "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/CAS?sc_lang=en",
    "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
    "https://english.sse.com.cn/indices/indices/list/indexmethods/c/H50066_h50066hbooken_EN.pdf",
)


def build_special_situation_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(SPECIAL_SITUATION_SOURCE_URLS),
        "required_ablation_tests": list(SPECIAL_SITUATION_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(SPECIAL_SITUATION_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(SPECIAL_SITUATION_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(SPECIAL_SITUATION_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK flow, AH-premium, and index-event snapshot profiles must prove official-source provenance, "
            "calendar/close-time alignment, event-window labels, crowding/slippage stress, signal-decay ablation, "
            "Stock Connect top-turnover, CCASS shareholding, eligibility, data-dissemination, and vendor "
            "reconciliation controls, AH price-ratio formula, share-class-switch, FX, shorting/access/settlement "
            "constraints, HSI methodology/operation-guide versioning, review schedule/results, next-review notices, "
            "press-release timestamps, constituent weight/pro-forma records, fast-entry/suspension/buffer exceptions, "
            "CAS / market-on-close order type, random-close, price-limit and rejection controls, passive-flow auction "
            "liquidity evidence, plus dry-run order-preview provenance before dry-run removal."
        ),
    }


__all__ = [
    "SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "SPECIAL_SITUATION_REQUIRED_ABLATION_TESTS",
    "SPECIAL_SITUATION_REQUIRED_DATA_PROVENANCE",
    "SPECIAL_SITUATION_REQUIRED_STRESS_TESTS",
    "SPECIAL_SITUATION_SOURCE_URLS",
    "SPECIAL_SITUATION_STOCK_SELECTION_PROFILES",
    "build_special_situation_live_enablement_policy",
]
