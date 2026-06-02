from __future__ import annotations

from typing import Any

from .contracts import (
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
)
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy

QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION = "hk_snapshot_quality_yield_live_enablement_policy.v1"

QUALITY_YIELD_STOCK_SELECTION_PROFILES: tuple[str, ...] = (
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
)

QUALITY_YIELD_REQUIRED_ABLATION_TESTS: tuple[str, ...] = (
    "low_vol_dividend_vs_shareholder_yield_vs_fcf_same_universe",
    "sp_access_low_vol_high_div_vs_hshylv_same_universe",
    "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe",
    "dividend_yield_only_vs_dividend_quality_controls",
    "buyback_yield_raw_vs_share_count_reduction_adjusted",
    "fcf_yield_raw_vs_sector_normalized_fcf_quality",
    "quality_yield_sleeve_vs_momentum_value_low_volatility_sleeves",
)

QUALITY_YIELD_REQUIRED_STRESS_TESTS: tuple[str, ...] = (
    "dividend_yield_trap_and_payout_cut_window",
    "abnormally_high_yield_price_crash_bottom_decile_window",
    "high_dividend_screened_financial_soundness_and_high_volatility_exclusion_window",
    "forecast_dividend_cut_and_estimate_revision_window",
    "forecast_dividend_financials_active_exposure_concentration_window",
    "property_financials_and_utilities_sector_concentration_window",
    "rate_cycle_and_hkd_liquidity_stress_window",
    "treasury_share_resale_dilution_and_convertible_issue_window",
    "treasury_share_moratorium_blackout_and_connected_person_window",
    "automatic_share_buyback_program_and_post_buyback_financing_window",
    "free_cash_flow_restatement_reporting_date_and_sector_normalization_window",
    "negative_fcf_ev_financial_real_estate_exception_window",
    "reporting_date_restatement_and_stale_fundamental_window",
    "fee_slippage_lot_size_and_suspension_sensitivity",
)

QUALITY_YIELD_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = (
    "point_in_time_dividend_history",
    "forecast_dividend_yield_estimate_history",
    "forecast_dividend_yield_vs_trailing_yield_benchmark_history",
    "dividend_forecast_vendor_methodology_and_estimate_revision_history",
    "point_in_time_earnings_payout_and_fcf_history",
    "southbound_high_dividend_low_vol_universe_history",
    "three_year_cash_dividend_record_and_payout_ratio_history",
    "price_crash_bottom_decile_screen_history",
    "large_mid_cap_market_value_shortlist_history",
    "one_year_high_volatility_exclusion_history",
    "high_dividend_financial_soundness_screen_history",
    "sp_access_hk_low_vol_high_div_methodology_and_constituent_history",
    "hsi_vs_sp_low_vol_high_div_rebalance_and_capping_history",
    "hkex_buyback_disclosure_and_share_count_history",
    "treasury_share_resale_and_dilution_history",
    "hkex_next_day_share_repurchase_return_history",
    "treasury_share_retention_cancellation_and_resale_history",
    "share_buyback_mandate_and_program_waiver_history",
    "post_buyback_new_issue_convertible_and_public_float_review",
    "treasury_share_moratorium_blackout_and_connected_person_controls",
    "fcf_formula_cash_flow_statement_lineage_history",
    "enterprise_value_market_cap_debt_cash_fx_history",
    "financial_real_estate_and_negative_fcf_exception_policy",
    "fcf_sector_normalization_and_concentration_history",
    "fundamental_restatement_and_reporting_date_asof_history",
    "sector_classification_and_southbound_eligibility_history",
    "volatility_beta_drawdown_and_liquidity_history",
)

QUALITY_YIELD_SOURCE_URLS: tuple[str, ...] = (
    "https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar",
    "https://www.spglobal.com/spdji/en/education/article/navigating-dividend-yield-in-the-hong-kong-market-the-sp-access-hong-kong-low-volatility-high-dividend-index",
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-low-volatility-high-dividend-index/",
    "https://www.spglobal.com/spdji/en/methodology/article/sp-low-volatility-high-dividend-indices-methodology/",
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index/",
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/hshylv",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshylve.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hshylve.pdf",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/hsschys",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsschyse.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsschkye.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20231214T000000.pdf",
    "https://www.hsi.com.hk/eng/indexes/all-indexes/hsscfcf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscfcfe.pdf",
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscfcfe.pdf",
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-free-cash-flow-50-index/",
    "https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-access-hk-fcf-50-index.pdf",
    "https://www.hkex.com.hk/-/media/HKEX-Market/Listing/Rules-and-Guidance/Other-Resources/Listed-Issuers/LIR-Newsletter/newsletter_202506.pdf",
    "https://www3.hkexnews.hk/reports/sharerepur/sbn.asp",
    "https://en-rules.hkex.com.hk/rulebook/9-repurchase-securities-and-treasury-shares",
    "https://en-rules.hkex.com.hk/entiresection/498",
    "https://www.hkex.com.hk/News/Regulatory-Announcements/2024/240412news?sc_lang=en",
    "https://www.hkex.com.hk/Listing/Education-Centre/Listed-Issuers/Share-Repurchase-and-Treasury-Shares?sc_lang=en",
)


def build_quality_yield_live_enablement_policy() -> dict[str, Any]:
    return {
        "required": True,
        "policy_version": QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION,
        "source_reference_urls": list(QUALITY_YIELD_SOURCE_URLS),
        "required_ablation_tests": list(QUALITY_YIELD_REQUIRED_ABLATION_TESTS),
        "required_stress_tests": list(QUALITY_YIELD_REQUIRED_STRESS_TESTS),
        "required_data_provenance": list(QUALITY_YIELD_REQUIRED_DATA_PROVENANCE),
        "required_profile_order": list(QUALITY_YIELD_STOCK_SELECTION_PROFILES),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": (
            "HK quality/yield snapshot profiles must prove dividend, buyback, and free-cash-flow signals are "
            "point-in-time, not yield traps, reconciled to Southbound, three-year cash-dividend, payout-ratio, "
            "forecast-dividend-yield estimate history, trailing-yield benchmarks, price-crash, high-volatility "
            "exclusion, financial-soundness, share-count, and treasury-share "
            "changes; reconciled against HSI HSHYLV/HSSCHYS and S&P Access HK Low Volatility High Dividend "
            "methodology / constituent evidence; checked against HKEX repurchase disclosures, treasury-share resale restrictions, "
            "moratorium/blackout controls, and post-buyback financing risk; sector-stress tested; and validated "
            "against HSI/S&P FCF formula, EV, reporting-date, restatement, and sector-exception evidence; "
            "with HK costs, turnover caps, and order-preview provenance before dry-run removal."
        ),
    }


__all__ = [
    "QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION",
    "QUALITY_YIELD_REQUIRED_ABLATION_TESTS",
    "QUALITY_YIELD_REQUIRED_DATA_PROVENANCE",
    "QUALITY_YIELD_REQUIRED_STRESS_TESTS",
    "QUALITY_YIELD_SOURCE_URLS",
    "QUALITY_YIELD_STOCK_SELECTION_PROFILES",
    "build_quality_yield_live_enablement_policy",
]
