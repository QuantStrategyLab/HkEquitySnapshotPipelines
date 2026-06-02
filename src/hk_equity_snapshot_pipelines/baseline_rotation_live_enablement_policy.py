from __future__ import annotations

from typing import Any

from .contracts import HK_BLUE_CHIP_LEADER_ROTATION_PROFILE
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_baseline_rotation_live_enablement_policy.v1"

BASELINE_ROTATION_PROFILES: tuple[str, ...] = (
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
)

BASELINE_ROTATION_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "blue_chip_rotation_vs_hsi_tracker_same_universe",
    "blue_chip_baseline_vs_liquid_momentum_quality_same_universe",
    "relative_momentum_vs_absolute_momentum_vs_52_week_high",
    "hsi_only_vs_hsi_hscei_hstech_liquid_universe",
    "sector_neutral_vs_sector_unconstrained_leader_weights",
    "rebalance_buffer_vs_naive_monthly_rotation",
    "quality_liquidity_filter_on_vs_filter_off",
)

BASELINE_ROTATION_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "hsi_hstech_leadership_reversal_window",
    "china_macro_policy_rate_cycle_and_hkd_liquidity_window",
    "crowded_blue_chip_liquidity_slippage_window",
    "suspension_stale_price_and_corporate_action_window",
    "sector_concentration_financials_technology_property_window",
    "rebalance_turnover_spike_and_lot_size_window",
    "vcm_cas_and_market_session_execution_window",
)

BASELINE_ROTATION_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "point_in_time_hsi_constituent_history",
    "hsi_methodology_and_review_history",
    "point_in_time_adjusted_price_history",
    "benchmark_relative_momentum_history",
    "current_price_to_52_week_high_history",
    "liquidity_adv_market_cap_and_board_lot_history",
    "sector_classification_history",
    "corporate_action_suspension_and_stale_price_history",
    "rebalance_buffer_turnover_and_capacity_history",
    "board_lot_vcm_and_trading_session_rule_history",
)

BASELINE_ROTATION_SOURCE_URLS: tuple[str, ...] = (
    "https://www.hsi.com.hk/eng/indexes/all-indexes/hsi",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsie.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf",
    "https://www.hkex.com.hk/Market-Data/Statistics/Securities-Market?sc_lang=en",
    "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
    "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/VCM?sc_lang=en",
)


def build_baseline_rotation_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(BASELINE_ROTATION_SOURCE_URLS),
        "required_ablation_tests": list(BASELINE_ROTATION_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(BASELINE_ROTATION_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(BASELINE_ROTATION_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(BASELINE_ROTATION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK blue-chip baseline rotation snapshots must prove HSI constituent and adjusted-price provenance, "
            "benchmark-relative momentum versus simple tracker and momentum alternatives, sector / liquidity / "
            "rebalance-buffer ablations, HK board-lot / VCM / trading-session execution controls, and dry-run "
            "order-preview provenance before dry-run removal."
        ),
    }


__all__ = [
    "BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "BASELINE_ROTATION_PROFILES",
    "BASELINE_ROTATION_REQUIRED_ABLATION_TESTS",
    "BASELINE_ROTATION_REQUIRED_DATA_PROVENANCE",
    "BASELINE_ROTATION_REQUIRED_STRESS_TESTS",
    "BASELINE_ROTATION_SOURCE_URLS",
    "build_baseline_rotation_live_enablement_policy",
]
