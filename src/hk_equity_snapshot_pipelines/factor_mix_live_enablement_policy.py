from __future__ import annotations

from typing import Any

from .contracts import HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_factor_mix_live_enablement_policy.v1"

FACTOR_MIX_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
)

FACTOR_MIX_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "qvlm_risk_parity_vs_equal_weight_factor_mix_same_universe",
    "qvlm_factor_mix_vs_composite_qvm_same_universe",
    "hsi_qvlm_risk_parity_vs_hsi_equal_weight_factor_mix_same_universe",
    "msci_equal_weight_qvl_vs_hsi_qvlm_with_momentum_sleeve",
    "msci_hk_factor_mix_equal_weight_qvl_vs_hsi_risk_parity_qvlm_without_momentum",
    "inverse_volatility_vs_equal_risk_contribution_weighting",
    "factor_covariance_window_sensitivity_ablation",
    "component_index_overlap_adjusted_vs_naive_factor_sleeve_blend",
    "quality_value_momentum_low_vol_sleeve_leave_one_out_ablation",
    "risk_parity_factor_vol_window_sensitivity",
    "sector_neutral_vs_sector_unconstrained_factor_mix",
)

FACTOR_MIX_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "factor_crowding_and_low_volatility_reversal_window",
    "momentum_crash_and_value_trap_rotation_window",
    "single_factor_underperformance_rotation_and_rebalance_drag_window",
    "factor_correlation_breakdown_and_covariance_instability_window",
    "qvlm_12pct_cap_sector_and_single_name_concentration_window",
    "component_index_overlap_and_capping_turnover_spike_window",
    "msci_factor_mix_low_vol_quality_value_underperformance_window",
    "rate_cycle_hkd_liquidity_and_sector_concentration_window",
    "southbound_policy_event_and_connect_holiday_window",
    "fee_slippage_lot_size_suspension_and_capacity_sensitivity",
)

FACTOR_MIX_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "point_in_time_quality_value_momentum_low_vol_factor_history",
    "factor_volatility_and_risk_parity_weight_history",
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
    "sector_classification_and_southbound_eligibility_history",
    "valuation_and_fundamental_reporting_date_history",
    "liquidity_suspension_and_corporate_action_history",
)

FACTOR_MIX_SOURCE_URLS: tuple[str, ...] = (
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
)


def build_factor_mix_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(FACTOR_MIX_SOURCE_URLS),
        "required_ablation_tests": list(FACTOR_MIX_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(FACTOR_MIX_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(FACTOR_MIX_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(FACTOR_MIX_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK factor-mix snapshots must prove point-in-time Q/V/L/M factor history, factor-volatility "
            "risk-parity weighting, HSI parent-universe and component-index lineage, HSI risk-parity versus "
            "equal-weight factor-mix comparison, MSCI equal-weight Q/V/L component and capped-methodology controls, "
            "component-overlap/capping effects, factor covariance stability, same-universe ablations versus "
            "equal-weight and existing composite QVM, sector/Southbound controls, HK costs, capacity, artifact "
            "provenance, and dry-run order previews before dry-run removal."
        ),
    }


__all__ = [
    "FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION",
    "FACTOR_MIX_REQUIRED_ABLATION_TESTS",
    "FACTOR_MIX_REQUIRED_DATA_PROVENANCE",
    "FACTOR_MIX_REQUIRED_STRESS_TESTS",
    "FACTOR_MIX_SOURCE_URLS",
    "FACTOR_MIX_STOCK_SELECTION_PROFILES",
    "build_factor_mix_live_enablement_policy",
]
