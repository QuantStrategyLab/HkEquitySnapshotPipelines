from __future__ import annotations

from typing import Any

from .contracts import HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_policy_value_live_enablement_policy.v1"

POLICY_VALUE_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
)

POLICY_VALUE_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "central_soe_value_quality_vs_broad_value_quality_same_universe",
    "central_soe_only_vs_all_soe_value_quality_same_universe",
    "central_soe_value_quality_vs_hsi_value_and_quality_factor_indexes_same_universe",
    "central_soe_ownership_source_sasac_vs_mof_financial_list_ablation",
    "hsi_40pct_factor_screening_vs_unbuffered_top_rank_selection",
    "hsi_factor_cap_weighting_vs_uncapped_policy_value_portfolio",
    "southbound_eligible_vs_all_hk_central_soe_universe",
    "value_quality_vs_value_only_vs_quality_only",
    "state_ownership_threshold_sensitivity",
    "dividend_policy_value_quality_with_vs_without_payout_controls",
    "sector_neutral_vs_sector_unconstrained_policy_value",
)

POLICY_VALUE_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "policy_event_and_state_ownership_reform_window",
    "sasac_mof_reclassification_and_parent_restructuring_window",
    "central_soe_parent_list_merger_split_and_effective_date_drift_window",
    "hsi_factor_screening_cap_and_rebalance_turnover_spike_window",
    "soe_sector_concentration_financials_energy_telecom_window",
    "china_macro_credit_property_and_rate_cycle_window",
    "southbound_eligibility_removal_suspension_and_calendar_gap_window",
    "public_float_connected_transaction_parent_support_and_sanction_window",
    "governance_connected_transaction_and_dividend_cut_window",
    "fee_slippage_lot_size_suspension_and_capacity_sensitivity",
)

POLICY_VALUE_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "government_shareholder_classification_history",
    "largest_shareholder_and_ownership_pct_history",
    "central_soe_flag_and_methodology_version_history",
    "sasac_central_soe_parent_list_effective_date_history",
    "mof_central_financial_soe_list_effective_date_history",
    "largest_shareholder_look_through_chain_and_source_uri_history",
    "hsi_central_soe_value_quality_factor_index_constituent_history",
    "hsi_factor_score_zscore_industry_standardization_history",
    "hsi_factor_score_missing_measure_average_policy_history",
    "hsi_40pct_factor_screening_and_buffer_rule_history",
    "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history",
    "value_quality_low_vol_momentum_factor_history",
    "hkex_southbound_eligible_security_point_in_time_history",
    "southbound_eligibility_liquidity_and_suspension_history",
    "central_soe_largest_shareholder_source_list_effective_date_drift_history",
    "public_float_parent_support_connected_transaction_and_dividend_policy_history",
    "policy_event_sector_concentration_and_governance_risk_history",
)

POLICY_VALUE_SOURCE_URLS: tuple[str, ...] = (
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
)


def build_policy_value_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(POLICY_VALUE_SOURCE_URLS),
        "required_ablation_tests": list(POLICY_VALUE_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(POLICY_VALUE_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(POLICY_VALUE_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(POLICY_VALUE_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK policy/value snapshots must prove point-in-time central-SOE largest-shareholder classification, "
            "SASAC/MOF central-SOE source lineage, ownership thresholds, HSI value/quality factor-index reconciliation, "
            "HSI factor-score missing-measure handling, 40% screening, 5%/10% capping lineage, HKEX Southbound "
            "eligibility history, sector concentration controls, same-universe ablations, policy-event, source-list "
            "effective-date drift, cap-turnover, and parent-support stress windows, HK costs, capacity, artifact "
            "provenance, and dry-run order previews before dry-run removal."
        ),
    }


__all__ = [
    "POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION",
    "POLICY_VALUE_REQUIRED_ABLATION_TESTS",
    "POLICY_VALUE_REQUIRED_DATA_PROVENANCE",
    "POLICY_VALUE_REQUIRED_STRESS_TESTS",
    "POLICY_VALUE_SOURCE_URLS",
    "POLICY_VALUE_STOCK_SELECTION_PROFILES",
    "build_policy_value_live_enablement_policy",
]
