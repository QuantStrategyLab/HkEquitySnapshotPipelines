from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

from .artifact_provenance_policy import build_artifact_provenance_policy
from .backtest_validation_policy import BACKTEST_VALIDATION_POLICY_VERSION, build_backtest_validation_policy
from .baseline_rotation_live_enablement_policy import (
    BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION,
    BASELINE_ROTATION_PROFILES,
    build_baseline_rotation_live_enablement_policy,
)
from .contracts import (
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
    HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
    HK_INDEX_REBALANCE_EVENT_PROFILE,
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
    SOURCE_PROJECT,
    SnapshotProfileContract,
    get_profile_contract,
    list_profile_contracts,
)
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy
from .evidence_freshness_policy import build_evidence_freshness_policy
from .evidence_uri_policy import build_evidence_uri_policy
from .factor_mix_live_enablement_policy import (
    FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION,
    FACTOR_MIX_STOCK_SELECTION_PROFILES,
    build_factor_mix_live_enablement_policy,
)
from .future_research_live_enablement_policy import (
    ECONPAPERS_DIRECTOR_DEALING_SHARE_REPURCHASE_HK_URL,
    ECONPAPERS_STOCK_CONNECT_INCLUSION_EXCLUSION_URL,
    FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION,
    HK_DIRECTOR_DEALING_DISCLOSURE_QUALITY_OVERLAY_PROFILE_HINT,
    HK_DUALLY_TRADED_LIQUID_REVERSAL_OVERLAY_PROFILE_HINT,
    HK_EARNINGS_ANNOUNCEMENT_DRIFT_OVERLAY_PROFILE_HINT,
    HK_EARNINGS_REVISION_QUALITY_OVERLAY_PROFILE_HINT,
    HK_EQUITY_FINANCING_DILUTION_RISK_OVERLAY_PROFILE_HINT,
    HK_LOTTERY_STOCK_RISK_EXCLUSION_OVERLAY_PROFILE_HINT,
    HK_LOW_SIZE_QUALITY_LIQUIDITY_PREMIUM_PROFILE_HINT,
    HK_MOMENTUM_PROFITABILITY_RESEARCH_URL,
    HK_SHORT_SELLING_PRESSURE_RISK_OVERLAY_PROFILE_HINT,
    HK_STOCK_CONNECT_INCLUSION_EVENT_FLOW_PROFILE_HINT,
    HKBU_HSI_FUTURES_INTRADAY_REVERSAL_URL,
    HKEX_CAPITAL_RAISINGS_RULE_CHANGE_2018_URL,
    HKEX_DESIGNATED_SHORT_SELLING_SECURITIES_URL,
    HKEX_DISCLOSURE_OF_INTERESTS_SEARCH_URL,
    HKEX_LISTED_COMPANY_INFORMATION_DISSEMINATION_FAQ_URL,
    HKEX_LISTED_ISSUER_EQUITY_SECURITIES_DISCLOSURE_URL,
    HKEX_MAIN_BOARD_ISSUER_FORMS_URL,
    HKEX_PROFIT_WARNING_ALERT_FAQ_URL,
    HKEX_REGULATED_SHORT_SELLING_URL,
    HKEX_REVERSAL_EXECUTION_TRADING_MECHANISM_URL,
    HKEX_REVERSAL_EXECUTION_TRANSACTION_FEES_URL,
    HKEX_SHORT_SELLING_DAILY_FILE_DATA_PRODUCT_URL,
    HKEX_SHORT_SELLING_TURNOVER_TODAY_URL,
    HKEX_STOCK_CONNECT_EXPANSION_2023_URL,
    HKEX_STOCK_CONNECT_FAQ_URL,
    HKEXNEWS_ADVANCED_SEARCH_URL,
    HSI_LOW_SIZE_INDEX_METHODOLOGY_URL,
    HSI_SMART_BETA_PRESS_RELEASE_URL,
    HSI_SMART_BETA_RESEARCH_PAPER_URL,
    IDEAS_HK_STOCK_RETURN_REVERSAL_CONTINUANCE_URL,
    POLYU_HK_EARNINGS_ANNOUNCEMENT_DRIFT_THESIS_URL,
    POLYU_HK_GAMBLING_STOCK_MARKET_PDF_URL,
    POLYU_HK_RIGHTS_ISSUE_REACTION_THESIS_URL,
    SCIENCEDIRECT_HK_DIRECTOR_DEALING_SHARE_REPURCHASE_URL,
    SCIENCEDIRECT_HK_DUALLY_TRADED_CONTRARIAN_URL,
    SCIENCEDIRECT_HK_GAMBLING_STOCK_MARKET_URL,
    SCIENCEDIRECT_HK_RIGHTS_OFFERS_DIFFERENT_URL,
    SCIENCEDIRECT_HK_SEO_INSIDER_TRADING_URL,
    SCIENCEDIRECT_HK_SHORT_SALE_BAN_PEAD_URL,
    SCIENCEDIRECT_HK_VOLATILITY_EFFECT_URL,
    SCIENCEDIRECT_SHORT_SALES_PRICE_ADJUSTMENT_HK_URL,
    SFC_DISCLOSURE_OF_INTERESTS_DI_NOTICES_URL,
    SFC_DISCLOSURE_OF_INTERESTS_PART_XV_URL,
    SP_DO_EARNINGS_REVISIONS_MATTER_ASIA_URL,
    SP_EARNINGS_REVISION_OVERLAY_ASIA_URL,
    SPRINGER_HK_PROFIT_WARNING_MARKET_REACTION_URL,
    SSRN_SHORT_INTEREST_RETURN_PREDICTABILITY_URL,
    TANDF_HK_SHORT_TERM_OVERREACTION_URL,
    build_future_research_live_enablement_policy,
)
from .live_enablement_policy import (
    build_execution_capacity_policy,
    build_live_enablement_thresholds,
    build_production_source_audit_policy,
)
from .momentum_live_enablement_policy import (
    MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION,
    MOMENTUM_LIVE_ENABLEMENT_SOURCE_URLS,
    MOMENTUM_STOCK_SELECTION_PROFILES,
    build_momentum_live_enablement_policy,
)
from .notification_audit_policy import SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE, build_notification_audit_policy
from .policy_value_live_enablement_policy import (
    POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION,
    POLICY_VALUE_STOCK_SELECTION_PROFILES,
    build_policy_value_live_enablement_policy,
)
from .quality_yield_live_enablement_policy import (
    QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION,
    QUALITY_YIELD_STOCK_SELECTION_PROFILES,
    build_quality_yield_live_enablement_policy,
)
from .quality_growth_live_enablement_policy import (
    QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION,
    QUALITY_GROWTH_STOCK_SELECTION_PROFILES,
    build_quality_growth_live_enablement_policy,
)
from .rollout_risk_policy import build_rollout_risk_policy
from .snapshot_readiness import SNAPSHOT_STATUS
from .special_situation_live_enablement_policy import (
    SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION,
    SPECIAL_SITUATION_STOCK_SELECTION_PROFILES,
    build_special_situation_live_enablement_policy,
)

SNAPSHOT_PROMOTION_GATE = "blocked_until_production_evidence"
SNAPSHOT_RUNTIME_ENABLED = False

GENERIC_REQUIRED_NEXT_EVIDENCE: tuple[str, ...] = (
    "production_snapshot_source_audit",
    "production_source_uri_and_quality_report_provenance",
    "artifact_publication_provenance",
    "fresh_section_evidence_generated_at",
    "execution_capacity_and_liquidity_limits",
    "dry_run_order_preview_artifact_provenance",
    "staged_rollout_tripwires_and_rollback",
    "survivorship_safe_walk_forward_backtest_min_three_oos_years",
    "backtest_validation_policy_evidence",
    "point_in_time_no_lookahead_and_no_overfit_controls",
    "positive_annual_return_and_positive_excess_return_vs_profile_benchmark",
    "hk_fee_stamp_duty_or_exemption_slippage_and_lot_size_model",
    "paper_or_dry_run_rebalance_windows",
    "platform_order_preview_notifications_and_operator_approval",
    "bilingual_notification_delivery_log",
    "baseline_rotation_ablation_hsi_constituent_and_execution_controls",
    "quality_yield_ablation_and_yield_trap_controls_for_first_snapshot_candidates",
    "quality_growth_ablation_growth_deceleration_and_low_vol_controls",
    "factor_mix_risk_parity_ablation_and_factor_volatility_controls",
    "policy_value_government_ownership_and_concentration_controls",
    "special_situation_signal_decay_crowding_and_calendar_alignment_controls",
)

EVIDENCE_URI_POLICY: dict[str, Any] = build_evidence_uri_policy()
EVIDENCE_FRESHNESS_POLICY: dict[str, Any] = build_evidence_freshness_policy()
HSI_MOMENTUM_METHODOLOGY_URL = "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf"
HSI_SMART_BETA_MOMENTUM_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbism"
HSI_MOMENTUM_RESEARCH_PAPER_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf"
)
HSI_SCHK_SOES_MOMENTUM_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscsme.pdf"
)
HSI_FACTOR_INDEXES_URL = "https://www.hsi.com.hk/solutions/factor-indexes/"
MSCI_MOMENTUM_INDEXES_URL = "https://www.msci.com/indexes/group/momentum-indexes"
MSCI_HK_MOMENTUM_INDEX_URL = "https://www.msci.com/indexes/index/711028"
MSCI_MOMENTUM_METHODOLOGY_URL = (
    "https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf"
)
MSCI_HK_LISTED_SOUTHBOUND_MOMENTUM_FACTSHEET_URL = (
    "https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c"
)
HSI_QUALITY_GROWTH_LOW_VOL_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsqglve.pdf"
)
HSI_QUALITY_GROWTH_LOW_VOL_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsqglve.pdf"
)
HSI_LOW_VOLATILITY_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisve.pdf"
)
HSI_SCHK_HIGH_DIV_LOW_VOL_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/hshylv"
HSI_SCHK_HIGH_DIV_LOW_VOL_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshylve.pdf"
)
HSI_SCHK_HIGH_DIV_LOW_VOL_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hshylve.pdf"
)
HSI_SCHK_HIGH_DIV_SCREENED_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/hsschys"
HSI_SCHK_HIGH_DIV_SCREENED_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsschyse.pdf"
)
HSI_SCHK_HIGH_DIV_SCREENED_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsschkye.pdf"
)
HSI_HIGH_DIVIDEND_RESEARCH_PAPER_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20231214T000000.pdf"
)
MSCI_HK_QUALITY_INDEX_URL = "https://www.msci.com/indexes/index/721604"
MSCI_QUALITY_INDEXES_URL = "https://www.msci.com/indexes/group/quality-indexes"
MSCI_HK_LISTED_SOUTHBOUND_QUALITY_FACTSHEET_URL = (
    "https://www.msci.com/documents/10199/60ebccab-109f-6a16-8451-557498ea39fb"
)
MSCI_MINIMUM_VOLATILITY_INDEXES_URL = "https://www.msci.com/indexes/group/minimum-volatility-indexes/"
MSCI_HK_LISTED_SOUTHBOUND_MIN_VOL_FACTSHEET_URL = (
    "https://www.msci.com/documents/10199/1396fa66-b4bd-40f3-8dfb-0109895d94ac"
)
HSI_RISK_PARITY_FACTOR_MIX_QVLM_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssbmfrpe.pdf"
)
HSI_RISK_PARITY_FACTOR_MIX_QVLM_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbmfrpe.pdf"
)
HSI_EQUAL_WEIGHT_FACTOR_MIX_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/hssbmfew"
HSI_SCHK_CENTRAL_SOES_FACTOR_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssccsme.pdf"
)
HSI_SCHK_CENTRAL_SOES_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsoee.pdf"
)
HSI_SCHK_CENTRAL_SOES_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscsoee.pdf"
)
HSI_SCHK_CENTRAL_SOES_VALUE_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssccsve.pdf"
)
HSI_SCHK_CENTRAL_SOES_QUALITY_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssccsqe.pdf"
)
SASAC_CENTRAL_SOE_DIRECTORY_URL = "https://www.sasac.gov.cn/n2588045/n27271785/n27271792/index.html"
MOF_CENTRAL_FINANCIAL_SOE_DIRECTORY_RULES_URL = "https://www.mof.gov.cn/zcsjtsgb/gfxwj/202007/t20200713_3583827.htm"
MSCI_HK_FACTOR_MIX_A_SERIES_URL = "https://www.msci.com/indexes/index/705097"
MSCI_FACTOR_MIX_A_SERIES_INDEXES_URL = "https://www.msci.com/indexes/factor-indexes/factor-mix-a-series-indexes"
MSCI_HK_FACTOR_MIX_A_SERIES_FACTSHEET_URL = (
    "https://www.msci.com/documents/10199/e56a62f4-3ff6-40a7-a8e6-54a6de8e6763"
)
MSCI_FACTOR_MIX_A_SERIES_METHODOLOGY_URL = (
    "https://www.msci.com/eqb/methodology/meth_docs/MSCI_Factor_Mix_Indexes_Methodology_Apr16.pdf"
)
MSCI_QUALITY_MIX_INDEXES_PAPER_URL = "https://www.msci.com/research-and-insights/paper/the-msci-quality-mix-indexes"
HKEX_ETF_CONNECT_FACTSHEET_URL = (
    "https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Exchange-Traded-Products/"
    "Launch/Inclusion-of-ETFs-in-Stock-Connect_Investor.pdf"
)
HKEX_STOCK_CONNECT_STATISTICS_URL = "https://www.hkex.com.hk/mutual-market/stock-connect/statistics?sc_lang=en"
HKEX_STOCK_CONNECT_HISTORICAL_DAILY_URL = (
    "https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Statistics/Historical-Daily?sc_lang=en"
)
HKEX_SOUTHBOUND_CCASS_SHAREHOLDING_URL = "https://www3.hkexnews.hk/sdw/search/mutualmarket.aspx?t=hk"
HKEX_STOCK_CONNECT_ELIGIBLE_SECURITIES_URL = (
    "https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=en"
)
HKEX_STOCK_CONNECT_DATA_DISSEMINATION_URL = (
    "https://www.hkex.com.hk/News/Market-Communications/2024/2404122news?sc_lang=en"
)
SOUTHBOUND_FLOW_RETURN_PREDICTABILITY_SSRN_URL = "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5128472"
HSI_AH_PREMIUM_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/ahpremium"
HSI_CHINA_AH_INDEX_SERIES_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/chinaah"
HSI_AH_PREMIUM_FACTSHEET_URL = "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/ahpremiume.pdf"
HSI_AH_PREMIUM_INDEX_FLASH_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/index_flash/20240124T000000.pdf"
)
HSI_AH_SMART_INDEX_BLOG_URL = "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/blog/20210914T000000.pdf"
SSE_SH_HK_AH_PREMIUM_METHODOLOGY_URL = (
    "https://english.sse.com.cn/indices/indices/list/indexmethods/c/H50066_h50066hbooken_EN.pdf"
)
AH_PREMIUM_SIAMESE_TWIN_SCIENCEDIRECT_URL = (
    "https://www.sciencedirect.com/science/article/abs/pii/S0927539825000210"
)
HSI_INDEX_METHODOLOGY_GUIDE_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf"
)
HSI_INDEX_OPERATION_GUIDE_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_operation_guide_e.pdf"
)
HSI_INDEX_REBALANCE_SCHEDULE_URL = "https://www.hsi.com.hk/static/uploads/contents/en/products/is_update.xlsx"
HSI_INDEX_NEXT_REVIEW_NOTICE_20260102_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/news/indexChgNotice/20260102T163000.pdf"
)
HSI_INDEX_REVIEW_RESULT_20260213_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260213T174500.pdf"
)
HSI_INDEX_REVIEW_RESULT_20260522_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20260522T174500.pdf"
)
HKEX_CLOSING_AUCTION_SESSION_FAQ_URL = (
    "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/CAS?sc_lang=en"
)
HKEX_TRADING_MECHANISM_URL = (
    "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en"
)
HKEX_REPURCHASE_TREASURY_SHARES_RULEBOOK_URL = (
    "https://en-rules.hkex.com.hk/rulebook/9-repurchase-securities-and-treasury-shares"
)
HKEX_SHARE_REPURCHASE_RULE_SECTION_URL = "https://en-rules.hkex.com.hk/entiresection/498"
HKEX_TREASURY_SHARES_CONCLUSIONS_URL = (
    "https://www.hkex.com.hk/News/Regulatory-Announcements/2024/240412news?sc_lang=en"
)
HKEX_SHARE_REPURCHASE_ELEARNING_URL = (
    "https://www.hkex.com.hk/Listing/Education-Centre/Listed-Issuers/"
    "Share-Repurchase-and-Treasury-Shares?sc_lang=en"
)
HSI_SCHK_FREE_CASH_FLOW_INDEX_URL = "https://www.hsi.com.hk/eng/indexes/all-indexes/hsscfcf"
HSI_SCHK_FREE_CASH_FLOW_FACTSHEET_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscfcfe.pdf"
)
HSI_SCHK_FREE_CASH_FLOW_METHODOLOGY_URL = (
    "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscfcfe.pdf"
)
SP_ACCESS_HK_FCF_50_INDEX_URL = (
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/"
    "sp-access-hong-kong-free-cash-flow-50-index/"
)
SP_ACCESS_HK_FCF_50_METHODOLOGY_URL = (
    "https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-access-hk-fcf-50-index.pdf"
)
SP_ACCESS_HK_LOW_VOL_HIGH_DIV_URL = (
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/"
    "sp-access-hong-kong-low-volatility-high-dividend-index/"
)
SP_LOW_VOL_HIGH_DIV_METHODOLOGY_URL = (
    "https://www.spglobal.com/spdji/en/methodology/article/sp-low-volatility-high-dividend-indices-methodology/"
)
SP_ETF_CONNECT_HK_US_LOW_VOL_HIGH_DIV_URL = (
    "https://www.spglobal.com/spdji/en/indices/dividends-factors/"
    "sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index/"
)
MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION = "hk_snapshot_momentum_live_enablement_comparison.v1"
FUTURE_RESEARCH_BACKLOG_VERSION = "hk_snapshot_future_research_backlog.v1"

LIVE_ENABLEMENT_STAGE_BY_BUCKET: dict[str, str] = {
    "first_snapshot_candidate": "production_data_audit_and_walk_forward_first",
    "quality_growth_snapshot_candidate": "quality_growth_low_vol_after_first_quality_candidates",
    "factor_mix_snapshot_candidate": "factor_mix_risk_parity_after_single_factor_ablation",
    "policy_value_quality_candidate": "policy_value_quality_after_factor_mix_and_quality_yield_ablation",
    "momentum_snapshot_candidate": "momentum_research_after_quality_candidates",
    "broad_multifactor_candidate": "factor_data_audit_before_promotion",
    "flow_overlay_candidate": "production_flow_collector_before_promotion",
    "valuation_overlay_candidate": "valuation_data_alignment_before_promotion",
    "baseline_snapshot_candidate": "platform_contract_baseline_not_first_live_candidate",
    "event_research_candidate": "event_study_before_promotion",
}

NEXT_LIVE_ENABLEMENT_ACTION_BY_BUCKET: dict[str, str] = {
    "first_snapshot_candidate": "Audit production snapshot source, then run survivorship-safe walk-forward backtests.",
    "quality_growth_snapshot_candidate": "Ablate quality, growth, and low-volatility factors after first quality/yield candidates.",
    "factor_mix_snapshot_candidate": (
        "Compare risk-parity QVLM against equal-weight factor mix and composite QVM before promotion."
    ),
    "policy_value_quality_candidate": (
        "Audit government ownership and compare central-SOE value-quality against broad value/quality candidates."
    ),
    "momentum_snapshot_candidate": "Compare residual, liquid, and composite momentum variants after first quality-style candidates.",
    "broad_multifactor_candidate": "Audit quality/value/momentum/low-vol factor history and run factor ablation.",
    "flow_overlay_candidate": "Build and validate a production Stock Connect flow collector before promotion-grade backtests.",
    "valuation_overlay_candidate": "Audit AH pair mapping, FX, close-time alignment, and eligibility history before backtests.",
    "baseline_snapshot_candidate": "Use for artifact contract plumbing; do not treat as the first preferred live candidate.",
    "event_research_candidate": "Run an event study with announcement/effective timestamps before any dry-run promotion.",
}

MOMENTUM_COMPARISON_BY_PROFILE: dict[str, dict[str, object]] = {
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE: {
        "momentum_priority": 1,
        "momentum_role": "closest_to_us_momentum_factor_stock_selection",
        "recommended_stage": "first_momentum_factor_candidate_after_quality_styles",
        "why": (
            "Closest to a US-style long-only momentum factor because it isolates residual / industry-relative "
            "momentum and adds beta, volatility, drawdown, suspension, and Southbound eligibility controls."
        ),
        "signal_inputs": (
            "mom_12_1",
            "residual_mom_12_1",
            "industry_relative_mom_6m",
            "rel_mom_6m_vs_benchmark",
            "high_252_gap",
            "sma200_gap",
            "realized_vol_126",
            "beta_252",
            "maxdd_252",
        ),
        "pre_live_comparison_evidence": (
            "Compare residual momentum versus liquid price momentum and composite QVM on the same survivorship-safe universe.",
            "Reconcile 12-1 residual momentum with MSCI-style 6/12-month one-month-skip risk-adjusted momentum and HSI close-to-high descriptors.",
            "Show positive out-of-sample excess return versus 02800 after HK fees, stamp duty or exemption, slippage, and lot-size rounding.",
            "Prove annualized turnover stays <= 120% with hold buffers, sector caps, and realistic suspension handling.",
        ),
    },
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE: {
        "momentum_priority": 2,
        "momentum_role": "simpler_liquid_price_momentum_candidate",
        "recommended_stage": "fallback_if_residual_factor_history_is_not_ready",
        "why": (
            "Simpler to source from adjusted price history and liquidity fields; useful when residual-model inputs "
            "are not yet production-grade, but raw price momentum needs stricter turnover and crash-risk controls."
        ),
        "signal_inputs": (
            "mom_3m",
            "mom_6m",
            "mom_12_1",
            "rel_mom_6m_vs_benchmark",
            "high_252_gap",
            "sma200_gap",
            "vol_63",
            "maxdd_126",
            "adv20_hkd",
        ),
        "pre_live_comparison_evidence": (
            "Use the same cost model and benchmark window as residual momentum.",
            "Compare 52-week-high proximity, 12-1 price momentum, and MSCI-style 6/12-month risk-adjusted momentum on one universe.",
            "Show hold buffers and liquidity filters keep realized turnover compatible with HK single-name costs.",
            "Stress test sharp HSI/HSTECH reversals because raw momentum can crowd into high-beta rebounds.",
        ),
    },
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE: {
        "momentum_priority": 3,
        "momentum_role": "diversified_multifactor_with_momentum_sleeve",
        "recommended_stage": "after_single_factor_momentum_ablation",
        "why": (
            "Better diversification across quality/value/momentum/low-volatility, but it should not be treated as "
            "pure momentum live evidence until factor ablations prove the momentum sleeve adds robust excess return."
        ),
        "signal_inputs": (
            "quality_score",
            "value_score",
            "momentum_score",
            "low_volatility_score",
            "southbound_eligible",
            "sector",
        ),
        "pre_live_comparison_evidence": (
            "Run factor ablation against residual momentum, liquid momentum, quality-only, and value-only sleeves.",
            "Prove the momentum sleeve is not just a proxy for MSCI/HSI sector weights, liquidity, or low-volatility exposure.",
            "Prove the composite does not merely inherit low-volatility or yield exposure from the first quality candidates.",
            "Validate annualized turnover stays <= 120% and sector concentration stays within the profile cap.",
        ),
    },
}

FUTURE_RESEARCH_BACKLOG: tuple[dict[str, object], ...] = (
    {
        "profile_hint": HK_EARNINGS_REVISION_QUALITY_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "earnings_revision_quality_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot_overlay",
        "research_thesis": (
            "Use point-in-time analyst EPS forecast revisions as an overlay on existing HK quality, "
            "value, low-volatility, and dividend/FCF sleeves instead of a standalone high-turnover signal."
        ),
        "required_new_data": (
            "point_in_time_consensus_eps_estimate_history",
            "analyst_revision_breadth_and_magnitude_history",
            "analyst_coverage_count_and_staleness_history",
            "forecast_vendor_methodology_and_survivorship_controls",
            "earnings_announcement_calendar_and_reporting_date_history",
        ),
        "live_enablement_blockers": (
            "Create a new snapshot profile and contract version before adding any artifact fields.",
            "Ablate earnings-revision overlay versus existing quality/yield, momentum, QGLV, QVLM, and central-SOE sleeves.",
            "Prove turnover remains compatible with HK single-name costs, lot-size rounding, and suspension handling.",
            "Stress stale coverage, estimate clustering, negative-revision whipsaws, sector concentration, and policy-event windows.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            SP_EARNINGS_REVISION_OVERLAY_ASIA_URL,
            SP_DO_EARNINGS_REVISIONS_MATTER_ASIA_URL,
            HK_MOMENTUM_PROFITABILITY_RESEARCH_URL,
        ),
    },
    {
        "profile_hint": HK_LOW_SIZE_QUALITY_LIQUIDITY_PREMIUM_PROFILE_HINT,
        "candidate_bucket": "low_size_quality_liquidity_premium_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot",
        "research_thesis": (
            "Test whether HK low-size exposure still adds robust excess return after Hang Seng-style quality "
            "screening, industry controls, liquidity filters, and capacity limits."
        ),
        "required_new_data": (
            "point_in_time_free_float_market_cap_history",
            "hsics_industry_classification_history",
            "roe_de_eps_variability_quality_screen_history",
            "adv_spread_board_lot_suspension_and_free_float_capacity_history",
            "stock_connect_or_southbound_eligibility_history",
        ),
        "live_enablement_blockers": (
            "Create a new snapshot profile and contract version before adding any artifact fields.",
            "Ablate low-size exposure versus existing value, quality, low-volatility, momentum, and QVLM sleeves.",
            "Prove the signal is not an illiquidity proxy by enforcing ADV, spread, board-lot, suspension, and free-float capacity limits.",
            "Stress small-cap crash, liquidity freeze, sector crowding, index exclusion, Southbound eligibility removal, and corporate-action windows.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK single-name cost limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            HSI_LOW_SIZE_INDEX_METHODOLOGY_URL,
            HSI_SMART_BETA_PRESS_RELEASE_URL,
            HSI_SMART_BETA_RESEARCH_PAPER_URL,
        ),
    },
    {
        "profile_hint": HK_STOCK_CONNECT_INCLUSION_EVENT_FLOW_PROFILE_HINT,
        "candidate_bucket": "stock_connect_inclusion_event_flow_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "event_calendar_snapshot",
        "research_thesis": (
            "Test Stock Connect Southbound eligibility inclusions, exclusions, and sell-only transitions as an "
            "event signal, with post-event Southbound turnover or CCASS holding confirmation."
        ),
        "required_new_data": (
            "point_in_time_stock_connect_eligible_security_change_history",
            "announcement_date_effective_date_review_calendar_and_sell_only_status_history",
            "southbound_daily_turnover_top10_turnover_and_ccass_holding_history",
            "pre_event_post_event_liquidity_spread_suspension_and_short_sale_eligibility_history",
            "raw_hkex_sse_szse_change_list_and_vendor_reconciliation_history",
        ),
        "live_enablement_blockers": (
            "Create a new event-calendar snapshot profile and contract version before adding any artifact fields.",
            "Separate inclusion, exclusion, sell-only, secondary-to-primary, dual-primary, ETF, and review-cycle event labels.",
            "Ablate Stock Connect event flow versus existing Southbound-flow, index-rebalance, AH-premium, and liquid-momentum profiles.",
            "Stress signal decay, crowding, passive-flow reversal, eligibility reversal, holiday/settlement gaps, suspension, and slippage windows.",
            "Require walk-forward event-study evidence with max drawdown <= 30%, positive benchmark excess return, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            HKEX_STOCK_CONNECT_ELIGIBLE_SECURITIES_URL,
            HKEX_STOCK_CONNECT_EXPANSION_2023_URL,
            HKEX_STOCK_CONNECT_FAQ_URL,
            ECONPAPERS_STOCK_CONNECT_INCLUSION_EXCLUSION_URL,
        ),
    },
    {
        "profile_hint": HK_SHORT_SELLING_PRESSURE_RISK_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "short_selling_pressure_risk_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot_overlay",
        "research_thesis": (
            "Use HKEX daily short-selling turnover, designated-shortable status, and short-interest ratio "
            "evidence as a risk overlay for crowded longs, short-squeeze risk, or negative-information exposure."
        ),
        "required_new_data": (
            "point_in_time_designated_short_selling_security_history",
            "daily_short_selling_turnover_short_ratio_and_short_interest_history",
            "shortable_status_add_delete_effective_date_and_tick_rule_history",
            "options_or_derivatives_hedging_and_borrow_availability_proxy_history",
            "price_reversal_squeeze_liquidity_spread_and_suspension_history",
        ),
        "live_enablement_blockers": (
            "Create a new overlay snapshot profile and contract version before adding any artifact fields.",
            "Use as a risk overlay or exclusion test first; do not convert it into a short-selling execution strategy.",
            "Ablate short-selling pressure versus existing momentum, Southbound-flow, AH-premium, and quality/yield profiles.",
            "Stress short-squeeze rebounds, borrow/shorting eligibility changes, tick-rule effects, option-hedging flows, liquidity freezes, and crowding windows.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK single-name cost limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            HKEX_REGULATED_SHORT_SELLING_URL,
            HKEX_SHORT_SELLING_TURNOVER_TODAY_URL,
            HKEX_DESIGNATED_SHORT_SELLING_SECURITIES_URL,
            HKEX_SHORT_SELLING_DAILY_FILE_DATA_PRODUCT_URL,
            SSRN_SHORT_INTEREST_RETURN_PREDICTABILITY_URL,
            SCIENCEDIRECT_SHORT_SALES_PRICE_ADJUSTMENT_HK_URL,
        ),
    },
    {
        "profile_hint": HK_DIRECTOR_DEALING_DISCLOSURE_QUALITY_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "director_dealing_disclosure_quality_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot_overlay",
        "research_thesis": (
            "Use disclosed director, chief-executive, and substantial-shareholder dealings as a legal "
            "alignment / undervaluation overlay after excluding routine, lagged, or compliance-driven filings."
        ),
        "required_new_data": (
            "point_in_time_disclosure_of_interests_notice_history",
            "director_chief_executive_and_substantial_shareholder_dealing_history",
            "buy_sell_exercise_transfer_and_derivative_position_change_history",
            "filing_lag_correction_cancellation_and_blackout_context_history",
            "share_repurchase_director_dealing_overlap_history",
        ),
        "live_enablement_blockers": (
            "Create a new overlay snapshot profile and contract version before adding any artifact fields.",
            "Use only disclosed DI notices and director-dealing records; do not imply or trade on illegal insider information.",
            "Ablate director-dealing disclosure overlay versus shareholder-yield, buyback, quality/yield, value, and momentum profiles.",
            "Stress routine option exercises, connected-person transfers, filing lags, correction/cancellation notices, blackout/moratorium windows, low liquidity, and crowding.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK single-name cost limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            SFC_DISCLOSURE_OF_INTERESTS_PART_XV_URL,
            SFC_DISCLOSURE_OF_INTERESTS_DI_NOTICES_URL,
            HKEX_DISCLOSURE_OF_INTERESTS_SEARCH_URL,
            ECONPAPERS_DIRECTOR_DEALING_SHARE_REPURCHASE_HK_URL,
            SCIENCEDIRECT_HK_DIRECTOR_DEALING_SHARE_REPURCHASE_URL,
        ),
    },
    {
        "profile_hint": HK_DUALLY_TRADED_LIQUID_REVERSAL_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "dually_traded_liquid_reversal_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot_overlay",
        "research_thesis": (
            "Test whether short-horizon reversal can be harvested only in liquid, dually traded or cross-listed "
            "HK names where foreign-listing alignment, volume, and execution cost evidence reduce false reversals."
        ),
        "required_new_data": (
            "point_in_time_dually_traded_security_mapping_history",
            "hk_foreign_close_fx_volume_and_listing_status_alignment_history",
            "weekly_reversal_signal_rank_volume_and_extreme_move_history",
            "bid_ask_spread_board_lot_vcm_cas_fee_slippage_and_suspension_history",
            "same_universe_momentum_value_quality_and_ah_premium_ablation_history",
        ),
        "live_enablement_blockers": (
            "Create a new overlay snapshot profile and contract version before adding any artifact fields.",
            "Treat as execution-aware reversal overlay only; do not promote a high-turnover intraday strategy without order-book evidence.",
            "Ablate dually traded liquid reversal versus existing momentum, AH-premium, index-event, and quality/yield profiles on the same universe.",
            "Stress transaction costs, opening/closing auction liquidity, VCM/CAS price controls, bid-ask bounce, stale quotes, suspensions, cross-market close/FX alignment, and crowding decay.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK cost/capacity limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            SCIENCEDIRECT_HK_DUALLY_TRADED_CONTRARIAN_URL,
            IDEAS_HK_STOCK_RETURN_REVERSAL_CONTINUANCE_URL,
            TANDF_HK_SHORT_TERM_OVERREACTION_URL,
            HKBU_HSI_FUTURES_INTRADAY_REVERSAL_URL,
            HKEX_REVERSAL_EXECUTION_TRADING_MECHANISM_URL,
            HKEX_REVERSAL_EXECUTION_TRANSACTION_FEES_URL,
        ),
    },
    {
        "profile_hint": HK_EARNINGS_ANNOUNCEMENT_DRIFT_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "earnings_announcement_drift_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "event_calendar_snapshot_overlay",
        "research_thesis": (
            "Test HK post-earnings-announcement drift and profit-warning / alert reactions as an event overlay, "
            "using only public HKEXnews announcements after publication timestamps and trading resumption are known."
        ),
        "required_new_data": (
            "point_in_time_hkex_results_announcement_profit_warning_and_alert_history",
            "announcement_publication_timestamp_board_meeting_date_and_trading_resumption_history",
            "earnings_surprise_sign_magnitude_and_post_announcement_window_history",
            "profit_warning_alert_language_classification_and_inside_information_flag_history",
            "liquidity_short_sale_eligibility_suspension_spread_fee_and_slippage_history",
        ),
        "live_enablement_blockers": (
            "Create a new event-calendar overlay snapshot profile and contract version before adding any artifact fields.",
            "Use only public HKEXnews announcements after publication; never infer unpublished earnings or profit-warning content.",
            "Ablate PEAD / profit-warning drift versus earnings-revision overlay, momentum, short-selling pressure, and quality/yield profiles on the same universe.",
            "Stress stale or late announcements, trading halts/suspensions, after-hours publication windows, bilingual headline parsing, profit-warning false positives, short-sale constraints, liquidity freezes, and crowded post-announcement trades.",
            "Require walk-forward event-study evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK event-trading cost limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            POLYU_HK_EARNINGS_ANNOUNCEMENT_DRIFT_THESIS_URL,
            HKEX_LISTED_ISSUER_EQUITY_SECURITIES_DISCLOSURE_URL,
            HKEX_LISTED_COMPANY_INFORMATION_DISSEMINATION_FAQ_URL,
            HKEX_PROFIT_WARNING_ALERT_FAQ_URL,
            HKEXNEWS_ADVANCED_SEARCH_URL,
            SCIENCEDIRECT_HK_SHORT_SALE_BAN_PEAD_URL,
            SPRINGER_HK_PROFIT_WARNING_MARKET_REACTION_URL,
        ),
    },
    {
        "profile_hint": HK_LOTTERY_STOCK_RISK_EXCLUSION_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "lottery_stock_risk_exclusion_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "factor_snapshot_overlay",
        "research_thesis": (
            "Test HK lottery-like stock features as a risk exclusion / underweight overlay for existing "
            "single-name snapshots, using IVOL, ISKEW, low price, and MAX-return features to avoid overpaid "
            "speculative tails rather than to create a direct short-selling strategy."
        ),
        "required_new_data": (
            "point_in_time_lottery_feature_ivol_iskew_max_price_history",
            "monthly_max1_max5_daily_return_and_idiosyncratic_skewness_history",
            "market_regime_volatility_drawdown_and_lottery_premium_condition_history",
            "price_turnover_market_cap_free_float_liquidity_and_suspension_history",
            "same_universe_quality_momentum_low_size_low_vol_and_short_pressure_ablation_history",
            "short_sale_eligibility_spread_fee_slippage_vcm_cas_and_capacity_history",
        ),
        "live_enablement_blockers": (
            "Create a new overlay snapshot profile and contract version before adding any artifact fields.",
            "Use as an exclusion or underweight overlay first; do not promote a short-lottery strategy without borrow, short-sale eligibility, and locate evidence.",
            "Ablate lottery-risk exclusion versus low-vol dividend, quality growth, residual momentum, low-size, short-selling pressure, and composite QVLM profiles on the same universe.",
            "Stress persistent lottery features, down-market and high-volatility regimes, low-price illiquidity, one-day MAX outliers, stale quotes, suspensions, corporate actions, and retail-crowding windows.",
            "Require walk-forward evidence with max drawdown <= 30%, positive benchmark excess return, turnover within HK cost/capacity limits, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            POLYU_HK_GAMBLING_STOCK_MARKET_PDF_URL,
            SCIENCEDIRECT_HK_GAMBLING_STOCK_MARKET_URL,
            SCIENCEDIRECT_HK_VOLATILITY_EFFECT_URL,
            HKEX_REVERSAL_EXECUTION_TRADING_MECHANISM_URL,
            HKEX_REVERSAL_EXECUTION_TRANSACTION_FEES_URL,
        ),
    },
    {
        "profile_hint": HK_EQUITY_FINANCING_DILUTION_RISK_OVERLAY_PROFILE_HINT,
        "candidate_bucket": "equity_financing_dilution_risk_overlay_candidate",
        "scaffold_status": "research_only_not_scaffolded",
        "suggested_contract_type": "event_calendar_snapshot_overlay",
        "research_thesis": (
            "Test HK rights issues, open offers, placings, convertible issues, and other equity financing "
            "announcements as a dilution / adverse-selection risk overlay for existing single-name snapshots, "
            "distinguishing value-destroying rights offers from growth-oriented placements."
        ),
        "required_new_data": (
            "point_in_time_hkexnews_rights_issue_open_offer_placement_and_convertible_announcement_history",
            "announcement_publication_timestamp_trading_halt_resumption_and_completion_history",
            "issue_size_discount_dilution_use_of_proceeds_underwriter_and_shareholder_commitment_history",
            "general_mandate_specific_mandate_minority_approval_and_2018_rule_change_history",
            "same_universe_quality_value_momentum_shareholder_yield_and_director_dealing_ablation_history",
            "post_announcement_and_long_run_return_liquidity_spread_slippage_suspension_and_capacity_history",
        ),
        "live_enablement_blockers": (
            "Create a new event-calendar overlay snapshot profile and contract version before adding any artifact fields.",
            "Use as a dilution and adverse-selection risk overlay first; do not blindly short every financing announcement because private placements can differ from rights offers.",
            "Parse announcement type, issue scale, price discount, use of proceeds, underwriting, shareholder pre-commitment, minority approval, mandate type, completion, and cancellation before ranking risk.",
            "Ablate equity-financing dilution risk versus shareholder-yield, director-dealing, value-quality, momentum, low-size, and short-selling-pressure overlays on the same universe.",
            "Stress deep-discount rights issues, highly dilutive open offers, specific-mandate placings, convertible/warrant issuance, treasury-share sales, 2018 rule-change regimes, trading halts, suspensions, liquidity freezes, and completion failures.",
            "Require walk-forward event-study evidence with max drawdown <= 30%, positive benchmark excess return, HK event-trading cost/capacity controls, dry-run order previews, bilingual notifications, rollout controls, and operator approval.",
        ),
        "source_reference_urls": (
            POLYU_HK_RIGHTS_ISSUE_REACTION_THESIS_URL,
            SCIENCEDIRECT_HK_RIGHTS_OFFERS_DIFFERENT_URL,
            SCIENCEDIRECT_HK_SEO_INSIDER_TRADING_URL,
            HKEX_CAPITAL_RAISINGS_RULE_CHANGE_2018_URL,
            HKEX_MAIN_BOARD_ISSUER_FORMS_URL,
            HKEX_LISTED_ISSUER_EQUITY_SECURITIES_DISCLOSURE_URL,
        ),
    },
)


@dataclass(frozen=True)
class SnapshotPromotionCandidate:
    profile: str
    priority: int
    promotion_bucket: str
    snapshot_type: str
    style_family: str
    research_thesis: str
    production_data_dependencies: tuple[str, ...]
    research_evidence_urls: tuple[str, ...]
    profile_specific_next_evidence: tuple[str, ...]


_CANDIDATES: dict[str, SnapshotPromotionCandidate] = {
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
        priority=1,
        promotion_bucket="first_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="defensive_yield_quality",
        research_thesis="Low-volatility plus sustainable dividend quality is a natural HK low-turnover style.",
        production_data_dependencies=(
            "dividend_history",
            "forecast_dividend_yield_estimate_history",
            "forecast_dividend_yield_vs_trailing_yield_benchmark_history",
            "southbound_eligibility_history",
            "three_year_cash_dividend_record",
            "earnings_positive_flags",
            "payout_ratio",
            "large_mid_cap_market_value_shortlist",
            "one_year_high_volatility_exclusion",
            "high_dividend_financial_soundness_screen",
            "sp_access_hk_low_vol_high_div_methodology",
            "hsi_vs_sp_low_vol_high_div_constituent_and_capping_history",
            "price_crash_bottom_decile_screen",
            "realized_volatility_beta_drawdown",
            "corporate_actions_and_suspensions",
        ),
        research_evidence_urls=(
            "https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar",
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hslvie.pdf",
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshdyie.pdf",
            HSI_SCHK_HIGH_DIV_LOW_VOL_INDEX_URL,
            HSI_SCHK_HIGH_DIV_LOW_VOL_FACTSHEET_URL,
            HSI_SCHK_HIGH_DIV_LOW_VOL_METHODOLOGY_URL,
            HSI_SCHK_HIGH_DIV_SCREENED_INDEX_URL,
            HSI_SCHK_HIGH_DIV_SCREENED_FACTSHEET_URL,
            HSI_SCHK_HIGH_DIV_SCREENED_METHODOLOGY_URL,
            HSI_HIGH_DIVIDEND_RESEARCH_PAPER_URL,
            SP_ACCESS_HK_LOW_VOL_HIGH_DIV_URL,
            SP_LOW_VOL_HIGH_DIV_METHODOLOGY_URL,
            SP_ETF_CONNECT_HK_US_LOW_VOL_HIGH_DIV_URL,
            "https://www.indexologyblog.com/2017/10/19/does-low-volatility-enhance-dividend-investing-in-the-hong-kong-market/",
            "https://www.spglobal.com/spdji/en/education/article/navigating-dividend-yield-in-the-hong-kong-market-the-sp-access-hong-kong-low-volatility-high-dividend-index",
        ),
        profile_specific_next_evidence=(
            "Run low-vol dividend versus shareholder-yield versus FCF ablation on the same survivorship-safe universe.",
            "Ablate forecast dividend yield versus trailing dividend yield and require point-in-time estimate history before accepting forward yield as a live signal.",
            "Reconcile HSI HSHYLV/HSSCHYS style signals against S&P Access HK Low Volatility High Dividend methodology and constituent history.",
            "Audit Southbound eligibility, three-year cash-dividend records, payout-ratio bounds, and price-crash screens.",
            "Audit large/mid-cap shortlist, one-year high-volatility exclusion, and financial-soundness screens.",
            "Validate dividend cash treatment against broker reporting.",
            "Run yield-trap and sector-cap stress tests across financials, utilities, property, and telecom.",
        ),
    ),
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
        priority=2,
        promotion_bucket="first_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="shareholder_yield_quality",
        research_thesis="Actual buybacks are increasingly observable in HK; combine buyback yield with dividends, FCF quality, and dilution controls.",
        production_data_dependencies=(
            "hkex_share_repurchase_reports",
            "hkex_next_day_share_repurchase_returns",
            "dividend_history",
            "forecast_dividend_yield_estimate_history",
            "forecast_dividend_yield_vs_trailing_yield_benchmark_history",
            "share_count_and_treasury_share_history",
            "treasury_share_retention_cancellation_and_resale_history",
            "share_buyback_mandate_and_program_waiver_history",
            "free_cash_flow_and_roe",
            "debt_and_dilution_controls",
            "post_buyback_new_issue_convertible_and_public_float_review",
        ),
        research_evidence_urls=(
            "https://www.hkex.com.hk/-/media/HKEX-Market/Listing/Rules-and-Guidance/Other-Resources/Listed-Issuers/LIR-Newsletter/newsletter_202506.pdf",
            "https://www3.hkexnews.hk/reports/sharerepur/sbn.asp",
            HKEX_REPURCHASE_TREASURY_SHARES_RULEBOOK_URL,
            HKEX_SHARE_REPURCHASE_RULE_SECTION_URL,
            HKEX_TREASURY_SHARES_CONCLUSIONS_URL,
            HKEX_SHARE_REPURCHASE_ELEARNING_URL,
            "https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar",
            "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/",
        ),
        profile_specific_next_evidence=(
            "Run low-vol dividend versus shareholder-yield versus FCF ablation on the same survivorship-safe universe.",
            "Ablate forecast dividend yield versus trailing dividend yield and reject stale estimate revisions or sector-concentrated forward-yield exposure.",
            "Reconcile buyback yield against actual share-count reduction, treasury-share resale, and dilution.",
            "Audit HKEX next-day share-repurchase returns, treasury-share retention/cancellation, and CCASS/resale treatment.",
            "Stress treasury-share moratorium, results blackout, connected-person restrictions, and post-buyback financing windows.",
            "Audit HKEX disclosure ingestion latency and symbol mapping before any live enablement.",
        ),
    ),
    HK_FREE_CASH_FLOW_QUALITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_FREE_CASH_FLOW_QUALITY_PROFILE,
        priority=3,
        promotion_bucket="first_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="free_cash_flow_quality_value",
        research_thesis="High free-cash-flow yield with profitability and risk controls is supported by HK/Southbound index products.",
        production_data_dependencies=(
            "free_cash_flow_history",
            "enterprise_value_history",
            "fcf_formula_cash_flow_statement_lineage_history",
            "enterprise_value_market_cap_debt_cash_fx_history",
            "roe_and_revenue_growth",
            "reporting_date_availability",
            "fundamental_restatement_and_reporting_date_asof_history",
            "fcf_sector_normalization_and_concentration_history",
            "negative_fcf_and_financial_sector_exceptions",
            "financial_real_estate_and_negative_fcf_exception_policy",
        ),
        research_evidence_urls=(
            HSI_SCHK_FREE_CASH_FLOW_INDEX_URL,
            HSI_SCHK_FREE_CASH_FLOW_FACTSHEET_URL,
            HSI_SCHK_FREE_CASH_FLOW_METHODOLOGY_URL,
            SP_ACCESS_HK_FCF_50_INDEX_URL,
            SP_ACCESS_HK_FCF_50_METHODOLOGY_URL,
            "https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/",
        ),
        profile_specific_next_evidence=(
            "Run low-vol dividend versus shareholder-yield versus FCF ablation on the same survivorship-safe universe.",
            "Audit FCF formula lineage from cash-flow statement fields and EV inputs from market cap, debt, cash, and FX history.",
            "Audit restatements and stale-fundamental handling using point-in-time reporting dates and as-of snapshots.",
            "Validate sector normalization and concentration caps so energy or telecom FCF does not dominate unintentionally.",
            "Document negative-FCF and financial/real-estate sector exception policy before any platform selection.",
        ),
    ),
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
        priority=4,
        promotion_bucket="quality_growth_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="quality_growth_low_volatility",
        research_thesis=(
            "Quality growth with low-volatility controls is a natural HK defensive growth style supported by "
            "Hang Seng and MSCI quality / minimum-volatility index evidence."
        ),
        production_data_dependencies=(
            "point_in_time_revenue_earnings_roa_growth_history",
            "roe_accruals_cash_flow_debt_history",
            "msci_quality_roe_earnings_stability_and_leverage_history",
            "msci_quality_descriptor_return_on_equity_earnings_variability_leverage_history",
            "hsi_quality_growth_low_vol_score_formula_lineage",
            "hsi_qglv_roe_accruals_cash_flow_to_debt_growth_in_roa_pb_component_history",
            "hsi_qglv_winsorized_zscore_and_component_weight_history",
            "hsi_qglv_negative_equity_financials_and_missing_factor_policy_history",
            "valuation_normalization_and_negative_equity_policy",
            "growth_signal_reporting_date_and_restatement_asof_history",
            "cash_conversion_accruals_and_quality_trap_controls",
            "volatility_beta_drawdown_history",
            "minimum_volatility_optimizer_constraint_history",
            "low_volatility_factor_beta_residual_volatility_history",
            "hsi_low_vol_quality_screen_roe_de_epsvar_and_12mvol_history",
            "sector_weight_cap_and_concentration_history",
            "sector_and_southbound_eligibility_history",
        ),
        research_evidence_urls=(
            HSI_QUALITY_GROWTH_LOW_VOL_FACTSHEET_URL,
            HSI_QUALITY_GROWTH_LOW_VOL_METHODOLOGY_URL,
            HSI_LOW_VOLATILITY_METHODOLOGY_URL,
            HSI_FACTOR_INDEXES_URL,
            MSCI_QUALITY_INDEXES_URL,
            MSCI_HK_QUALITY_INDEX_URL,
            MSCI_HK_LISTED_SOUTHBOUND_QUALITY_FACTSHEET_URL,
            MSCI_MINIMUM_VOLATILITY_INDEXES_URL,
            MSCI_HK_LISTED_SOUTHBOUND_MIN_VOL_FACTSHEET_URL,
        ),
        profile_specific_next_evidence=(
            "Run quality-growth versus quality-only, growth-only, and low-vol-only ablation on the same universe.",
            "Trace HSI QGLV components: ROE, accruals ratio, cash-flow-to-debt, and Growth in ROA adjusted by P/B, including winsorized z-scores and component averaging.",
            "Reconcile HSI QGLV score lineage with MSCI quality variables: ROE, stable earnings growth, and low leverage.",
            "Validate HSI low-volatility quality screening and minimum-volatility optimizer constraints against a simple low-vol / beta / drawdown filter.",
            "Audit reporting-date availability, missing-factor handling, negative-equity / financials-sector normalization, and valuation normalization before backtests.",
            "Stress test growth deceleration, valuation compression, regulation, real-estate/financial concentration, and low-volatility crowding windows.",
        ),
    ),
    HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
        priority=5,
        promotion_bucket="factor_mix_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="quality_value_low_vol_momentum_risk_parity",
        research_thesis=(
            "Risk-parity QVLM can diversify quality, value, low-volatility, and momentum factor sleeves while "
            "reducing concentration in any single crowded HK style."
        ),
        production_data_dependencies=(
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
            "sector_and_southbound_eligibility_history",
            "valuation_and_fundamental_reporting_date_history",
            "liquidity_suspension_and_corporate_action_history",
        ),
        research_evidence_urls=(
            HSI_RISK_PARITY_FACTOR_MIX_QVLM_FACTSHEET_URL,
            HSI_RISK_PARITY_FACTOR_MIX_QVLM_METHODOLOGY_URL,
            HSI_EQUAL_WEIGHT_FACTOR_MIX_INDEX_URL,
            HSI_FACTOR_INDEXES_URL,
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf",
            MSCI_FACTOR_MIX_A_SERIES_INDEXES_URL,
            MSCI_HK_FACTOR_MIX_A_SERIES_URL,
            MSCI_HK_FACTOR_MIX_A_SERIES_FACTSHEET_URL,
            MSCI_FACTOR_MIX_A_SERIES_METHODOLOGY_URL,
            MSCI_QUALITY_MIX_INDEXES_PAPER_URL,
        ),
        profile_specific_next_evidence=(
            "Run QVLM risk-parity versus equal-weight factor mix and composite QVM ablation on the same universe.",
            "Reconcile HSI QVLM parent universe, Quality/Value/Low Volatility/Momentum component-index returns, risk-parity weight, and 12% capping lineage against MSCI equal-weight Q/V/L factor-mix controls.",
            "Audit MSCI HK Factor Mix A-Series component-index equal weighting and capped-methodology history before accepting it as the external Q/V/L benchmark.",
            "Audit factor covariance/correlation history, component overlap, cap-induced turnover, and rebalance-window sensitivity before accepting risk-parity weights.",
            "Audit factor-volatility history and weighting-window sensitivity before any dry-run promotion.",
            "Stress factor crowding, factor-correlation breakdowns, momentum crashes, value traps, low-volatility reversals, and sector/single-name concentration.",
        ),
    ),
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE: SnapshotPromotionCandidate(
        profile=HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
        priority=6,
        promotion_bucket="policy_value_quality_candidate",
        snapshot_type="factor_snapshot",
        style_family="central_soe_value_quality_select",
        research_thesis=(
            "Southbound-eligible central-SOE factor indexes support a HK-specific policy/value sleeve, but it "
            "must prove ownership classification, concentration, and policy-event controls before promotion."
        ),
        production_data_dependencies=(
            "government_shareholder_classification_history",
            "largest_shareholder_and_ownership_pct_history",
            "central_soe_flag_methodology_version_history",
            "sasac_central_soe_parent_list_effective_date_history",
            "mof_central_financial_soe_list_effective_date_history",
            "largest_shareholder_look_through_chain_and_source_uri_history",
            "hsi_central_soe_value_quality_factor_index_constituent_history",
            "hsi_factor_score_zscore_industry_standardization_history",
            "hsi_factor_score_missing_measure_average_policy_history",
            "hsi_40pct_factor_screening_and_buffer_rule_history",
            "hsi_factor_index_5pct_cap_and_base_index_10pct_cap_history",
            "quality_value_low_vol_momentum_factor_history",
            "hkex_southbound_eligible_security_point_in_time_history",
            "southbound_eligibility_liquidity_and_suspension_history",
            "central_soe_largest_shareholder_source_list_effective_date_drift_history",
            "public_float_parent_support_connected_transaction_and_dividend_policy_history",
            "policy_event_sector_concentration_and_governance_risk_history",
        ),
        research_evidence_urls=(
            HSI_SCHK_CENTRAL_SOES_FACTOR_METHODOLOGY_URL,
            HSI_SCHK_CENTRAL_SOES_METHODOLOGY_URL,
            HSI_SCHK_CENTRAL_SOES_FACTSHEET_URL,
            HSI_SCHK_CENTRAL_SOES_VALUE_FACTSHEET_URL,
            HSI_SCHK_CENTRAL_SOES_QUALITY_FACTSHEET_URL,
            HSI_FACTOR_INDEXES_URL,
            HKEX_STOCK_CONNECT_ELIGIBLE_SECURITIES_URL,
            SASAC_CENTRAL_SOE_DIRECTORY_URL,
            "https://en.sasac.gov.cn/directorynames.html",
            MOF_CENTRAL_FINANCIAL_SOE_DIRECTORY_RULES_URL,
        ),
        profile_specific_next_evidence=(
            "Audit point-in-time central-SOE largest-shareholder classification, look-through ownership chain, and SASAC/MOF list effective dates.",
            "Reconcile HSI Central SOEs value/quality factor-index constituents, Z-score standardisation, missing-measure averaging, 40% factor screening, buffer rules, and 5%/10% capping lineage.",
            "Audit SASAC/MOF source-list effective-date drift for central-SOE parent mergers, splits, and reclassifications before accepting largest-shareholder flags.",
            "Run central-SOE value-quality versus broad value-quality, HSI value/quality factor indexes, and existing quality/yield profiles on one universe.",
            "Stress SASAC/MOF reclassifications, parent restructurings, factor-screen/cap turnover spikes, sector concentration, Southbound eligibility removals, connected transactions, public-float pressure, sanctions, and dividend cuts.",
        ),
    ),
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
        priority=7,
        promotion_bucket="momentum_snapshot_candidate",
        snapshot_type="factor_snapshot",
        style_family="residual_industry_neutral_momentum",
        research_thesis="HK momentum exists, but a residual / industry-neutral implementation is safer than high-turnover raw price momentum.",
        production_data_dependencies=(
            "adjusted_price_history",
            "point_in_time_industry_classification",
            "market_and_industry_residual_model",
            "momentum_6m_12m_one_month_skip_history",
            "risk_adjusted_momentum_volatility_normalization_history",
            "hsi_close_to_high_momentum_descriptor_history",
            "beta_and_volatility_estimates",
            "momentum_turnover_buffer_and_capacity_history",
            "suspension_and_stale_price_handling",
        ),
        research_evidence_urls=(
            HSI_MOMENTUM_METHODOLOGY_URL,
            HSI_SMART_BETA_MOMENTUM_INDEX_URL,
            HSI_MOMENTUM_RESEARCH_PAPER_URL,
            MSCI_MOMENTUM_INDEXES_URL,
            MSCI_HK_MOMENTUM_INDEX_URL,
            MSCI_MOMENTUM_METHODOLOGY_URL,
            MSCI_HK_LISTED_SOUTHBOUND_MOMENTUM_FACTSHEET_URL,
            "https://www.hsi.com.hk/static/uploads/contents/zh_hk/dl_centre/methodologies/IM_hssbismc.pdf",
        ),
        profile_specific_next_evidence=(
            "Prove residual momentum is reproducible from raw adjusted history without look-ahead bias.",
            "Reconcile residual 12-1 momentum with MSCI-style 6/12-month one-month-skip risk-adjusted momentum and HSI close-to-high descriptors.",
            "Audit volatility normalization, winsorization, industry neutralization, and sector/capacity concentration before platform selection.",
            "Validate annualized turnover below the profile cap after HK stamp duty and slippage.",
        ),
    ),
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE: SnapshotPromotionCandidate(
        profile=HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
        priority=8,
        promotion_bucket="momentum_snapshot_candidate",
        snapshot_type="feature_snapshot",
        style_family="liquid_price_momentum_quality",
        research_thesis="Liquid price momentum with 52-week-high proximity and trend/risk filters is a simpler HK momentum scaffold.",
        production_data_dependencies=(
            "adjusted_price_history",
            "benchmark_relative_momentum",
            "momentum_6m_12m_one_month_skip_history",
            "risk_adjusted_momentum_volatility_normalization_history",
            "hsi_close_to_high_momentum_descriptor_history",
            "liquidity_and_market_cap_history",
            "momentum_turnover_buffer_and_capacity_history",
            "corporate_actions_and_suspensions",
            "stale_price_detection",
        ),
        research_evidence_urls=(
            HSI_MOMENTUM_METHODOLOGY_URL,
            HSI_SMART_BETA_MOMENTUM_INDEX_URL,
            HSI_MOMENTUM_RESEARCH_PAPER_URL,
            MSCI_MOMENTUM_INDEXES_URL,
            MSCI_HK_MOMENTUM_INDEX_URL,
            MSCI_MOMENTUM_METHODOLOGY_URL,
            MSCI_HK_LISTED_SOUTHBOUND_MOMENTUM_FACTSHEET_URL,
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf",
        ),
        profile_specific_next_evidence=(
            "Compare raw price momentum against residual momentum and composite factor variants.",
            "Compare 52-week-high proximity, 12-1 price momentum, and MSCI-style 6/12-month one-month-skip risk-adjusted momentum.",
            "Confirm hold buffers keep turnover compatible with HK single-name costs.",
        ),
    ),
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE: SnapshotPromotionCandidate(
        profile=HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
        priority=9,
        promotion_bucket="broad_multifactor_candidate",
        snapshot_type="factor_snapshot",
        style_family="quality_value_momentum_low_volatility",
        research_thesis="A broader multi-factor model can diversify HK single-name signal risk but needs the widest data audit.",
        production_data_dependencies=(
            "quality_factor_history",
            "value_factor_history",
            "momentum_and_trend_history",
            "momentum_6m_12m_one_month_skip_history",
            "risk_adjusted_momentum_volatility_normalization_history",
            "low_volatility_beta_drawdown_history",
            "factor_score_winsorization_and_neutralization_history",
            "factor_turnover_buffer_and_capacity_history",
            "southbound_eligibility_history",
        ),
        research_evidence_urls=(
            HSI_MOMENTUM_METHODOLOGY_URL,
            HSI_SMART_BETA_MOMENTUM_INDEX_URL,
            HSI_MOMENTUM_RESEARCH_PAPER_URL,
            MSCI_MOMENTUM_INDEXES_URL,
            MSCI_HK_MOMENTUM_INDEX_URL,
            MSCI_MOMENTUM_METHODOLOGY_URL,
            MSCI_HK_LISTED_SOUTHBOUND_MOMENTUM_FACTSHEET_URL,
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf",
            "https://www.hsi.com.hk/solutions/factor-indexes/",
        ),
        profile_specific_next_evidence=(
            "Run factor ablation so live promotion is not driven by one overfit sleeve.",
            "Show the momentum sleeve adds excess return beyond quality/value/low-volatility after MSCI/HSI descriptor reconciliation.",
            "Validate profile annualized turnover below 120% with sector caps and hold buffers.",
        ),
    ),
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE: SnapshotPromotionCandidate(
        profile=HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
        priority=10,
        promotion_bucket="flow_overlay_candidate",
        snapshot_type="flow_snapshot",
        style_family="southbound_flow_momentum",
        research_thesis="Southbound flows are large enough to matter but should be a smoothed snapshot overlay, not a daily trading trigger.",
        production_data_dependencies=(
            "stock_connect_daily_turnover",
            "southbound_holding_history",
            "hkex_southbound_top10_turnover_and_market_turnover_history",
            "ccass_southbound_shareholding_percent_issued_history",
            "holiday_aware_flow_windows",
            "connect_eligibility_history",
            "stock_connect_market_data_dissemination_change_history",
            "missing_flow_day_handling",
            "southbound_flow_raw_vs_vendor_reconciliation",
        ),
        research_evidence_urls=(
            HKEX_STOCK_CONNECT_STATISTICS_URL,
            HKEX_STOCK_CONNECT_HISTORICAL_DAILY_URL,
            HKEX_SOUTHBOUND_CCASS_SHAREHOLDING_URL,
            HKEX_STOCK_CONNECT_ELIGIBLE_SECURITIES_URL,
            "https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en",
            HKEX_STOCK_CONNECT_DATA_DISSEMINATION_URL,
            HKEX_ETF_CONNECT_FACTSHEET_URL,
            SOUTHBOUND_FLOW_RETURN_PREDICTABILITY_SSRN_URL,
        ),
        profile_specific_next_evidence=(
            "Build a production Stock Connect collector before any backtest is considered promotion-grade.",
            "Reconcile HKEX historical daily market turnover and top-10 turnover against CCASS Southbound shareholding changes.",
            "Validate point-in-time Stock Connect eligibility and flag names that appear in CCASS shareholding but are not eligible securities.",
            "Stress test policy-event, data-dissemination-change, real-time-turnover-suppression, top-10-only, and holiday windows where flow data can be noisy.",
            "Run flow signal-decay and holiday/calendar stress tests against the price-momentum baseline.",
        ),
    ),
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE: SnapshotPromotionCandidate(
        profile=HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
        priority=11,
        promotion_bucket="valuation_overlay_candidate",
        snapshot_type="valuation_snapshot",
        style_family="ah_premium_relative_value",
        research_thesis="A/H premium is HK-specific; safest first use is a long-only H-share valuation overlay.",
        production_data_dependencies=(
            "ah_pair_mapping",
            "a_share_and_h_share_close_alignment",
            "cnyhkd_fx_history",
            "northbound_and_southbound_eligibility_history",
            "share_class_and_corporate_action_adjustments",
            "ah_premium_index_constituent_and_price_ratio_history",
            "ah_smart_share_class_switch_threshold_history",
            "a_share_access_shorting_settlement_and_fx_constraint_review",
            "ah_premium_extreme_level_and_false_reversal_controls",
        ),
        research_evidence_urls=(
            HSI_AH_PREMIUM_INDEX_URL,
            HSI_CHINA_AH_INDEX_SERIES_URL,
            HSI_AH_PREMIUM_FACTSHEET_URL,
            HSI_AH_PREMIUM_INDEX_FLASH_URL,
            HSI_AH_SMART_INDEX_BLOG_URL,
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_operation_guide_e.pdf",
            SSE_SH_HK_AH_PREMIUM_METHODOLOGY_URL,
            AH_PREMIUM_SIAMESE_TWIN_SCIENCEDIRECT_URL,
        ),
        profile_specific_next_evidence=(
            "Keep implementation long-only unless A-share access, shorting, settlement, and FX constraints are approved.",
            "Audit close-time mismatch and exchange-holiday alignment before computing premium percentiles.",
            "Recompute AH price ratio from A-share price, H-share price, FX, and freefloat-adjusted market-cap inputs.",
            "Validate AH Smart-style share-class switch thresholds against the long-only H-share overlay before platform selection.",
            "Stress extreme-premium false-reversal windows because HSI evidence treats 15-year AH-premium highs as possible trough signals, not guaranteed convergence.",
            "Audit FX source, AH close alignment, premium-widening stress, and A-share access / shorting / settlement constraints before live use.",
        ),
    ),
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE: SnapshotPromotionCandidate(
        profile=HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
        priority=12,
        promotion_bucket="baseline_snapshot_candidate",
        snapshot_type="feature_snapshot",
        style_family="blue_chip_leader_rotation",
        research_thesis="Baseline liquid blue-chip rotation is useful for platform wiring and feature contract validation.",
        production_data_dependencies=(
            "adjusted_price_history",
            "hsi_constituent_history",
            "hsi_methodology_and_review_history",
            "universe_and_sector_history",
            "benchmark_relative_momentum",
            "current_price_to_52_week_high_history",
            "liquidity_history",
            "board_lot_vcm_and_trading_session_rule_history",
            "corporate_actions_and_suspensions",
        ),
        research_evidence_urls=(
            "https://www.hsi.com.hk/eng/indexes/all-indexes/hsi",
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsie.pdf",
            "https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf",
            "https://www.hkex.com.hk/Services/Rules-and-Forms-and-Fees/Fees/Securities-%28Hong-Kong%29/Trading/Transaction?sc_lang=en",
            "https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en",
            "https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/VCM?sc_lang=en",
        ),
        profile_specific_next_evidence=(
            "Use this as contract plumbing baseline, not as the first preferred single-name live strategy.",
            "Replace sample price/universe files with audited production adjusted history.",
            "Prove HSI constituent, review, sector, liquidity, board-lot, VCM, and trading-session provenance before platform dry-run removal.",
            "Ablate benchmark-relative momentum against HSI tracker, liquid-momentum quality, 52-week-high, sector-neutral, and rebalance-buffer alternatives.",
        ),
    ),
    HK_INDEX_REBALANCE_EVENT_PROFILE: SnapshotPromotionCandidate(
        profile=HK_INDEX_REBALANCE_EVENT_PROFILE,
        priority=13,
        promotion_bucket="event_research_candidate",
        snapshot_type="event_calendar_snapshot",
        style_family="index_rebalance_event",
        research_thesis="Official index reviews create repeatable event windows but have small samples and crowding/slippage risk.",
        production_data_dependencies=(
            "official_index_review_history",
            "hsi_quarterly_review_schedule_and_cutoff_history",
            "hsi_index_methodology_and_operation_guide_version_history",
            "hsi_review_schedule_file_version_and_effective_date_history",
            "hsi_next_review_notice_timestamp_and_scope_history",
            "hsi_review_result_press_release_history",
            "hsi_review_result_timestamp_constituent_weight_and_proforma_history",
            "hsi_constituent_added_deleted_effective_date_history",
            "announcement_and_effective_timestamps",
            "event_side_labels",
            "hsi_regular_fast_entry_deletion_buffer_and_suspension_rule_history",
            "hsi_fast_entry_suspension_and_buffer_rule_exception_history",
            "market_on_close_order_type_price_limit_and_random_close_policy",
            "hkex_cas_order_type_random_close_price_limit_and_rejection_history",
            "closing_auction_volume_spread_and_passive_flow_history",
            "closing_auction_imbalance_passive_flow_and_spread_history",
            "liquidity_and_slippage_estimates",
            "crowding_and_capacity_controls",
        ),
        research_evidence_urls=(
            HSI_INDEX_METHODOLOGY_GUIDE_URL,
            HSI_INDEX_OPERATION_GUIDE_URL,
            HSI_INDEX_REBALANCE_SCHEDULE_URL,
            HSI_INDEX_NEXT_REVIEW_NOTICE_20260102_URL,
            HSI_INDEX_REVIEW_RESULT_20260213_URL,
            HSI_INDEX_REVIEW_RESULT_20260522_URL,
            HKEX_CLOSING_AUCTION_SESSION_FAQ_URL,
            HKEX_TRADING_MECHANISM_URL,
        ),
        profile_specific_next_evidence=(
            "Treat as event study first; one event window is the minimum dry-run gate but not enough for capital scale-up.",
            "Validate post-announcement order timing and effective-date slippage before promotion.",
            "Validate announcement-to-effective-date crowding and slippage with official review history.",
            "Ingest the HSI regular rebalancing schedule, next-review notices, and review-result press releases as immutable event-source records.",
            "Split pre-announcement candidate probability, confirmed adds/removes, and effective-date execution windows to avoid look-ahead bias.",
            "Reconcile official schedule files against press-release timestamps, constituent weights, and pro-forma records before treating an event as tradable.",
            "Ablate market-on-close versus next-open execution and pro-forma-weighted add/delete trades versus equal-weight event trades.",
            "Stress fast-entry, suspension, buffer-rule, and ad-hoc index-change exceptions before treating the event sample as repeatable.",
            "Validate market-on-close / Closing Auction Session order type, random-close, two-stage price-limit, order rejection, passive-flow imbalance, and auction-liquidity controls.",
        ),
    ),
}


def _artifact_filenames(contract: SnapshotProfileContract) -> dict[str, str]:
    return {
        "snapshot": contract.snapshot_filename,
        "manifest": contract.manifest_filename,
        "ranking": contract.ranking_filename,
        "release_summary": contract.release_summary_filename,
    }


def get_snapshot_promotion_candidate(profile: str) -> SnapshotPromotionCandidate:
    contract = get_profile_contract(profile)
    return _CANDIDATES[contract.profile]


def list_snapshot_promotion_candidates() -> tuple[SnapshotPromotionCandidate, ...]:
    contracts = {contract.profile for contract in list_profile_contracts()}
    missing = contracts - set(_CANDIDATES)
    extra = set(_CANDIDATES) - contracts
    if missing or extra:
        raise RuntimeError(
            "Snapshot promotion matrix must match profile contracts; "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )
    return tuple(sorted(_CANDIDATES.values(), key=lambda item: (item.priority, item.profile)))


def _build_momentum_comparison_row(profile: str) -> dict[str, Any]:
    contract = get_profile_contract(profile)
    info = MOMENTUM_COMPARISON_BY_PROFILE[contract.profile]
    return {
        "profile": contract.profile,
        "display_name": contract.display_name,
        "momentum_priority": int(info["momentum_priority"]),
        "momentum_role": str(info["momentum_role"]),
        "recommended_stage": str(info["recommended_stage"]),
        "why": str(info["why"]),
        "signal_inputs": list(info["signal_inputs"]),
        "pre_live_comparison_evidence": list(info["pre_live_comparison_evidence"]),
        "live_enablement_thresholds": build_live_enablement_thresholds(contract.profile),
        "production_source_audit_policy": build_production_source_audit_policy(contract.profile),
        "execution_capacity_policy": build_execution_capacity_policy(contract.profile),
        "momentum_live_enablement_policy": build_momentum_live_enablement_policy(),
    }


def build_momentum_live_enablement_comparison() -> dict[str, Any]:
    rows = [
        _build_momentum_comparison_row(profile)
        for profile in sorted(
            MOMENTUM_STOCK_SELECTION_PROFILES,
            key=lambda item: int(MOMENTUM_COMPARISON_BY_PROFILE[item]["momentum_priority"]),
        )
    ]
    return {
        "comparison_version": MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION,
        "recommended_first_momentum_candidate": HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
        "live_enablement_gate": SNAPSHOT_PROMOTION_GATE,
        "status": SNAPSHOT_STATUS,
        "must_compare_before_live_enablement": True,
        "momentum_live_enablement_policy": build_momentum_live_enablement_policy(),
        "external_evidence_urls": list(MOMENTUM_LIVE_ENABLEMENT_SOURCE_URLS),
        "common_pre_live_requirements": [
            "Use one survivorship-safe HK universe and the same benchmark/cost/slippage model across residual, liquid, and composite momentum.",
            "Keep every momentum profile blocked until production adjusted-history, factor-history, suspension, corporate-action, and liquidity evidence passes.",
            "Require factor ablation across residual, liquid, and composite momentum plus quality/value/low-volatility sleeves before treating momentum as a live edge.",
            "Require reversal, high-beta rebound, suspension/stale-price, Southbound holiday/policy-event, and fee/slippage/lot-size stress windows.",
            "Require walk-forward evidence with positive annual return, positive excess return versus the profile benchmark, max drawdown <= 30%, and turnover within the profile cap.",
            "Require snapshot artifact provenance, evidence freshness, execution capacity, dry-run order-preview artifact provenance, bilingual notification audit logs, rollout tripwires, and operator approval before dry-run removal.",
        ],
        "profiles": rows,
    }


def build_future_research_backlog() -> dict[str, Any]:
    return {
        "backlog_version": FUTURE_RESEARCH_BACKLOG_VERSION,
        "status": "research_only_not_scaffolded",
        "live_enablement_gate": "requires_new_snapshot_contract_and_production_evidence",
        "candidate_count": len(FUTURE_RESEARCH_BACKLOG),
        "future_research_live_enablement_policy": build_future_research_live_enablement_policy(),
        "candidates": [
            {
                "profile_hint": str(item["profile_hint"]),
                "candidate_bucket": str(item["candidate_bucket"]),
                "scaffold_status": str(item["scaffold_status"]),
                "suggested_contract_type": str(item["suggested_contract_type"]),
                "research_thesis": str(item["research_thesis"]),
                "required_new_data": list(item["required_new_data"]),
                "live_enablement_blockers": list(item["live_enablement_blockers"]),
                "source_reference_urls": list(item["source_reference_urls"]),
            }
            for item in FUTURE_RESEARCH_BACKLOG
        ],
    }


def build_snapshot_promotion_row(profile: str) -> dict[str, Any]:
    contract = get_profile_contract(profile)
    candidate = get_snapshot_promotion_candidate(contract.profile)
    row = {
        "profile": contract.profile,
        "display_name": contract.display_name,
        "source_project": SOURCE_PROJECT,
        "priority": candidate.priority,
        "promotion_bucket": candidate.promotion_bucket,
        "recommended_live_enablement_stage": LIVE_ENABLEMENT_STAGE_BY_BUCKET[candidate.promotion_bucket],
        "next_live_enablement_action": NEXT_LIVE_ENABLEMENT_ACTION_BY_BUCKET[candidate.promotion_bucket],
        "snapshot_type": candidate.snapshot_type,
        "style_family": candidate.style_family,
        "status": SNAPSHOT_STATUS,
        "runtime_enabled": SNAPSHOT_RUNTIME_ENABLED,
        "live_enablement_gate": SNAPSHOT_PROMOTION_GATE,
        "contract_version": contract.contract_version,
        "artifact_filenames": _artifact_filenames(contract),
        "manifest_required_by_runtime": contract.manifest_required_by_runtime,
        "live_enablement_thresholds": build_live_enablement_thresholds(contract.profile),
        "production_source_audit_policy": build_production_source_audit_policy(contract.profile),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "backtest_validation_policy": build_backtest_validation_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(contract.profile),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "research_thesis": candidate.research_thesis,
        "production_data_dependencies": list(candidate.production_data_dependencies),
        "research_evidence_urls": list(candidate.research_evidence_urls),
        "evidence_uri_policy": EVIDENCE_URI_POLICY,
        "evidence_freshness_policy": EVIDENCE_FRESHNESS_POLICY,
        "required_next_evidence": list(GENERIC_REQUIRED_NEXT_EVIDENCE),
        "profile_specific_next_evidence": list(candidate.profile_specific_next_evidence),
    }
    if contract.profile in MOMENTUM_COMPARISON_BY_PROFILE:
        row["momentum_live_enablement_comparison"] = _build_momentum_comparison_row(contract.profile)
    if contract.profile in BASELINE_ROTATION_PROFILES:
        row["baseline_rotation_live_enablement_policy"] = build_baseline_rotation_live_enablement_policy()
    if contract.profile in QUALITY_YIELD_STOCK_SELECTION_PROFILES:
        row["quality_yield_live_enablement_policy"] = build_quality_yield_live_enablement_policy()
    if contract.profile in QUALITY_GROWTH_STOCK_SELECTION_PROFILES:
        row["quality_growth_live_enablement_policy"] = build_quality_growth_live_enablement_policy()
    if contract.profile in FACTOR_MIX_STOCK_SELECTION_PROFILES:
        row["factor_mix_live_enablement_policy"] = build_factor_mix_live_enablement_policy()
    if contract.profile in POLICY_VALUE_STOCK_SELECTION_PROFILES:
        row["policy_value_live_enablement_policy"] = build_policy_value_live_enablement_policy()
    if contract.profile in SPECIAL_SITUATION_STOCK_SELECTION_PROFILES:
        row["special_situation_live_enablement_policy"] = build_special_situation_live_enablement_policy()
    return row


def build_snapshot_promotion_matrix() -> dict[str, Any]:
    rows = [build_snapshot_promotion_row(candidate.profile) for candidate in list_snapshot_promotion_candidates()]
    first_snapshot_candidates = [
        row["profile"] for row in rows if row["promotion_bucket"] == "first_snapshot_candidate"
    ]
    return {
        "source_project": SOURCE_PROJECT,
        "status": SNAPSHOT_STATUS,
        "live_enablement_gate": SNAPSHOT_PROMOTION_GATE,
        "runtime_enabled_count": sum(1 for row in rows if row["runtime_enabled"]),
        "blocked_profile_count": sum(1 for row in rows if not row["runtime_enabled"]),
        "profile_count": len(rows),
        "first_snapshot_candidates": first_snapshot_candidates,
        "recommended_live_enablement_sequence": [row["profile"] for row in rows],
        "generic_required_next_evidence": list(GENERIC_REQUIRED_NEXT_EVIDENCE),
        "evidence_uri_policy": EVIDENCE_URI_POLICY,
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "backtest_validation_policy": build_backtest_validation_policy(),
        "evidence_freshness_policy": EVIDENCE_FRESHNESS_POLICY,
        "execution_capacity_policy": build_execution_capacity_policy(""),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "baseline_rotation_live_enablement_policy": build_baseline_rotation_live_enablement_policy(),
        "quality_yield_live_enablement_policy": build_quality_yield_live_enablement_policy(),
        "quality_growth_live_enablement_policy": build_quality_growth_live_enablement_policy(),
        "factor_mix_live_enablement_policy": build_factor_mix_live_enablement_policy(),
        "policy_value_live_enablement_policy": build_policy_value_live_enablement_policy(),
        "momentum_live_enablement_policy": build_momentum_live_enablement_policy(),
        "special_situation_live_enablement_policy": build_special_situation_live_enablement_policy(),
        "momentum_live_enablement_comparison": build_momentum_live_enablement_comparison(),
        "future_research_backlog": build_future_research_backlog(),
        "profiles": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print HK snapshot promotion/live-enable matrix.")
    parser.add_argument("--profile", help="Print one profile row instead of the full matrix")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args(argv)

    payload = build_snapshot_promotion_row(args.profile) if args.profile else build_snapshot_promotion_matrix()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.profile:
        print(f"profile={payload['profile']}")
        print(f"priority={payload['priority']}")
        print(f"promotion_bucket={payload['promotion_bucket']}")
        print(f"recommended_live_enablement_stage={payload['recommended_live_enablement_stage']}")
        print(f"next_live_enablement_action={payload['next_live_enablement_action']}")
        print(f"live_enablement_gate={payload['live_enablement_gate']}")
        return 0
    print(f"source_project={payload['source_project']}")
    print(f"status={payload['status']}")
    print(f"live_enablement_gate={payload['live_enablement_gate']}")
    print(f"profile_count={payload['profile_count']}")
    print("first_snapshot_candidates=" + ",".join(payload["first_snapshot_candidates"]))
    print("recommended_live_enablement_sequence=" + ",".join(payload["recommended_live_enablement_sequence"]))
    for row in payload["profiles"]:
        print(f"- {row['priority']}: {row['profile']} ({row['recommended_live_enablement_stage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "BACKTEST_VALIDATION_POLICY_VERSION",
    "BASELINE_ROTATION_PROFILES",
    "EVIDENCE_URI_POLICY",
    "FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION",
    "FACTOR_MIX_STOCK_SELECTION_PROFILES",
    "FUTURE_RESEARCH_BACKLOG_VERSION",
    "FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION",
    "GENERIC_REQUIRED_NEXT_EVIDENCE",
    "HSI_MOMENTUM_METHODOLOGY_URL",
    "HSI_QUALITY_GROWTH_LOW_VOL_FACTSHEET_URL",
    "HSI_QUALITY_GROWTH_LOW_VOL_METHODOLOGY_URL",
    "HSI_SCHK_HIGH_DIV_LOW_VOL_FACTSHEET_URL",
    "HSI_SCHK_HIGH_DIV_LOW_VOL_INDEX_URL",
    "HSI_SCHK_HIGH_DIV_LOW_VOL_METHODOLOGY_URL",
    "HSI_HIGH_DIVIDEND_RESEARCH_PAPER_URL",
    "HSI_SCHK_HIGH_DIV_SCREENED_FACTSHEET_URL",
    "HSI_SCHK_HIGH_DIV_SCREENED_INDEX_URL",
    "HSI_SCHK_HIGH_DIV_SCREENED_METHODOLOGY_URL",
    "HKEX_REPURCHASE_TREASURY_SHARES_RULEBOOK_URL",
    "HKEX_SHARE_REPURCHASE_ELEARNING_URL",
    "HKEX_SHARE_REPURCHASE_RULE_SECTION_URL",
    "HKEX_TREASURY_SHARES_CONCLUSIONS_URL",
    "LIVE_ENABLEMENT_STAGE_BY_BUCKET",
    "MOMENTUM_LIVE_ENABLEMENT_COMPARISON_VERSION",
    "MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION",
    "MOMENTUM_STOCK_SELECTION_PROFILES",
    "POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION",
    "POLICY_VALUE_STOCK_SELECTION_PROFILES",
    "NEXT_LIVE_ENABLEMENT_ACTION_BY_BUCKET",
    "QUALITY_YIELD_LIVE_ENABLEMENT_POLICY_VERSION",
    "QUALITY_YIELD_STOCK_SELECTION_PROFILES",
    "QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION",
    "QUALITY_GROWTH_STOCK_SELECTION_PROFILES",
    "SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "SPECIAL_SITUATION_STOCK_SELECTION_PROFILES",
    "SNAPSHOT_PROMOTION_GATE",
    "SnapshotPromotionCandidate",
    "build_baseline_rotation_live_enablement_policy",
    "build_future_research_backlog",
    "build_future_research_live_enablement_policy",
    "build_factor_mix_live_enablement_policy",
    "build_momentum_live_enablement_comparison",
    "build_momentum_live_enablement_policy",
    "build_policy_value_live_enablement_policy",
    "build_quality_yield_live_enablement_policy",
    "build_quality_growth_live_enablement_policy",
    "build_special_situation_live_enablement_policy",
    "build_snapshot_promotion_matrix",
    "build_snapshot_promotion_row",
    "get_snapshot_promotion_candidate",
    "list_snapshot_promotion_candidates",
    "main",
]
