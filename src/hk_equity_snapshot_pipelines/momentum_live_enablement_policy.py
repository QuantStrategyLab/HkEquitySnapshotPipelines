from __future__ import annotations

from typing import Any

from .contracts import (
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
)
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_momentum_live_enablement_policy.v1"

MOMENTUM_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
)

MOMENTUM_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "residual_vs_liquid_vs_composite_same_universe",
    "momentum_sleeve_vs_quality_value_low_volatility_sleeves",
    "current_price_to_52_week_high_vs_12_1_price_momentum",
    "msci_6_12_month_vs_hsi_52_week_high_descriptor_same_universe",
    "one_month_reversal_skip_vs_no_skip_momentum_signal",
    "risk_adjusted_vs_raw_price_momentum_same_universe",
    "industry_neutral_vs_sector_unconstrained_weights",
    "quality_screen_on_vs_quality_screen_off",
)

MOMENTUM_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "hsi_hstech_sharp_reversal_window",
    "high_beta_rebound_and_momentum_crash_window",
    "suspension_and_stale_price_window",
    "southbound_connect_holiday_or_policy_event_window",
    "fee_slippage_and_lot_size_rounding_sensitivity",
    "momentum_turnover_spike_and_rebalance_buffer_window",
    "sector_concentration_financials_real_estate_crowding_window",
    "southbound_momentum_universe_capacity_window",
)

MOMENTUM_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "point_in_time_adjusted_price_history",
    "point_in_time_industry_classification",
    "quality_screen_inputs_roe_de_eps_variability",
    "current_price_to_52_week_high_history",
    "momentum_6m_12m_one_month_skip_history",
    "risk_adjusted_momentum_volatility_normalization_history",
    "momentum_score_winsorization_and_rank_history",
    "hsi_smart_beta_momentum_descriptor_history",
    "msci_hk_and_hk_listed_southbound_momentum_benchmark_history",
    "rebalance_buffer_turnover_and_capacity_history",
    "liquidity_adv_and_suspension_history",
)

MOMENTUM_LIVE_ENABLEMENT_SOURCE_URLS: tuple[str, ...] = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbism",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscsme.pdf",
    "https://www.hsi.com.hk/solutions/factor-indexes/",
    "https://www.msci.com/indexes/group/momentum-indexes",
    "https://www.msci.com/indexes/index/711028",
    "https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf",
    "https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c",
    "https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en",
)


def build_momentum_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(MOMENTUM_LIVE_ENABLEMENT_SOURCE_URLS),
        "required_ablation_tests": list(MOMENTUM_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(MOMENTUM_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(MOMENTUM_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(MOMENTUM_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK momentum snapshot profiles must prove that momentum adds robust out-of-sample excess return "
            "after factor ablation, MSCI/HSI descriptor reconciliation, one-month reversal-skip and risk-adjusted "
            "momentum checks, stress windows, HK costs, turnover caps, and order-preview provenance."
        ),
    }
