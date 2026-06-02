from __future__ import annotations

from typing import Any

from .contracts import HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_quality_growth_live_enablement_policy.v1"

QUALITY_GROWTH_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
)

QUALITY_GROWTH_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "quality_growth_low_vol_vs_low_vol_dividend_same_universe",
    "quality_growth_vs_quality_only_vs_growth_only_vs_low_vol_only",
    "msci_quality_roe_earnings_stability_leverage_vs_hsi_qglv_same_universe",
    "hsi_qglv_four_component_score_vs_raw_quality_growth_inputs",
    "min_vol_optimizer_vs_simple_low_vol_beta_drawdown_filter",
    "hsi_low_vol_quality_screen_vs_simple_12m_volatility_filter",
    "valuation_normalized_growth_vs_unadjusted_growth_signal",
    "southbound_eligible_universe_vs_broad_hk_universe",
    "sector_neutral_vs_sector_unconstrained_weights",
    "qglv_candidate_vs_first_quality_yield_and_momentum_candidates",
)

QUALITY_GROWTH_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "growth_deceleration_and_earnings_revision_window",
    "rate_cycle_hkd_liquidity_and_high_valuation_window",
    "qglv_high_pb_growth_reversal_and_valuation_normalization_window",
    "platform_regulation_and_technology_drawdown_window",
    "financials_property_and_insurance_factor_normalization_window",
    "qglv_component_missingness_restatement_and_negative_equity_window",
    "real_estate_financials_concentration_and_leverage_window",
    "minimum_volatility_optimizer_sector_exposure_drift_window",
    "quality_trap_high_roe_low_cash_conversion_window",
    "low_volatility_crowding_reversal_window",
    "fee_slippage_lot_size_suspension_and_southbound_holiday_sensitivity",
)

QUALITY_GROWTH_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "point_in_time_revenue_earnings_roa_growth_history",
    "point_in_time_roe_accruals_cash_flow_and_debt_history",
    "msci_quality_roe_earnings_stability_and_leverage_history",
    "msci_quality_descriptor_return_on_equity_earnings_variability_leverage_history",
    "hsi_quality_growth_low_vol_score_formula_lineage",
    "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history",
    "hsi_qglv_winsorized_zscore_and_component_weight_history",
    "hsi_qglv_negative_equity_financials_and_missing_factor_policy_history",
    "valuation_normalization_and_negative_equity_policy",
    "growth_signal_reporting_date_and_restatement_asof_history",
    "cash_conversion_accruals_and_quality_trap_controls",
    "volatility_beta_drawdown_and_liquidity_history",
    "minimum_volatility_optimizer_constraint_history",
    "low_volatility_factor_beta_residual_volatility_history",
    "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history",
    "sector_classification_and_southbound_eligibility_history",
    "sector_weight_cap_and_concentration_history",
    "candidate_index_methodology_version_history",
)

QUALITY_GROWTH_SOURCE_URLS: tuple[str, ...] = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsqglve.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsqglve.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisve.pdf",
    "https://www.hsi.com.hk/solutions/factor-indexes/",
    "https://www.msci.com/indexes/group/quality-indexes",
    "https://www.msci.com/indexes/index/721604",
    "https://www.msci.com/documents/10199/60ebccab-109f-6a16-8451-557498ea39fb",
    "https://www.msci.com/indexes/group/minimum-volatility-indexes/",
    "https://www.msci.com/documents/10199/1396fa66-b4bd-40f3-8dfb-0109895d94ac",
)


def build_quality_growth_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(QUALITY_GROWTH_SOURCE_URLS),
        "required_ablation_tests": list(QUALITY_GROWTH_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(QUALITY_GROWTH_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(QUALITY_GROWTH_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(QUALITY_GROWTH_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK quality-growth low-volatility snapshots must prove point-in-time growth, quality, valuation, "
            "and risk inputs; reconcile HSI QGLV four-component scoring, HSI low-volatility quality screening, "
            "MSCI quality descriptors, and minimum-volatility descriptors; ablate quality, growth, low-volatility, "
            "sector, and Southbound-universe effects; stress growth deceleration, valuation, regulation, "
            "real-estate/financial concentration, low-vol crowding, factor missingness, and HK execution costs before "
            "dry-run removal."
        ),
    }


__all__ = [
    "QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION",
    "QUALITY_GROWTH_REQUIRED_ABLATION_TESTS",
    "QUALITY_GROWTH_REQUIRED_DATA_PROVENANCE",
    "QUALITY_GROWTH_REQUIRED_STRESS_TESTS",
    "QUALITY_GROWTH_SOURCE_URLS",
    "QUALITY_GROWTH_STOCK_SELECTION_PROFILES",
    "build_quality_growth_live_enablement_policy",
]
