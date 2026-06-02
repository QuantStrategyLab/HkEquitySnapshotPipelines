from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import (
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
    get_profile_contract,
)
from .first_snapshot_promotion_plan import FIRST_SNAPSHOT_PROFILE_ORDER, SUPPORTED_FIRST_SNAPSHOT_EVIDENCE_PROFILE_ORDER
from .free_cash_flow_quality_strategy import (
    OPTIONAL_FACTOR_COLUMNS as FCF_OPTIONAL_FACTOR_COLUMNS,
)
from .free_cash_flow_quality_strategy import (
    REQUIRED_FACTOR_COLUMNS as FCF_REQUIRED_FACTOR_COLUMNS,
)
from .free_cash_flow_quality_strategy import (
    normalize_symbol as normalize_fcf_symbol,
)
from .low_vol_dividend_quality_strategy import (
    OPTIONAL_FACTOR_COLUMNS as LOW_VOL_OPTIONAL_FACTOR_COLUMNS,
)
from .low_vol_dividend_quality_strategy import (
    REQUIRED_FACTOR_COLUMNS as LOW_VOL_REQUIRED_FACTOR_COLUMNS,
)
from .low_vol_dividend_quality_strategy import (
    normalize_symbol as normalize_low_vol_symbol,
)
from .shareholder_yield_quality_strategy import (
    OPTIONAL_FACTOR_COLUMNS as SHAREHOLDER_OPTIONAL_FACTOR_COLUMNS,
)
from .shareholder_yield_quality_strategy import (
    REQUIRED_FACTOR_COLUMNS as SHAREHOLDER_REQUIRED_FACTOR_COLUMNS,
)
from .shareholder_yield_quality_strategy import (
    normalize_symbol as normalize_shareholder_symbol,
)


FIRST_SNAPSHOT_EVIDENCE_PROFILE_VERSION = "hk_first_snapshot_evidence_profiles.v1"

_NON_NUMERIC_SOURCE_COLUMNS = frozenset(
    {
        "as_of",
        "corporate_action_flag",
        "earnings_positive",
        "eligible",
        "snapshot_date",
        "sector",
        "southbound_eligible",
        "symbol",
    }
)


@dataclass(frozen=True)
class FirstSnapshotEvidenceProfile:
    profile: str
    sample_factor_snapshot_path: Path
    required_factor_columns: frozenset[str]
    optional_factor_columns: frozenset[str]
    required_operational_columns: frozenset[str]
    normalize_symbol: Callable[[Any], str]
    production_source_focus: tuple[str, ...]
    quality_yield_focus: tuple[str, ...]

    @property
    def required_production_columns(self) -> tuple[str, ...]:
        return tuple(sorted(self.required_factor_columns | self.required_operational_columns))

    @property
    def numeric_source_columns(self) -> tuple[str, ...]:
        return tuple(sorted((self.required_factor_columns | self.optional_factor_columns) - _NON_NUMERIC_SOURCE_COLUMNS))

    @property
    def slug(self) -> str:
        return self.profile.removeprefix("hk_")

    @property
    def display_name(self) -> str:
        return get_profile_contract(self.profile).display_name


FIRST_SNAPSHOT_EVIDENCE_PROFILES: dict[str, FirstSnapshotEvidenceProfile] = {
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE: FirstSnapshotEvidenceProfile(
        profile=HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
        sample_factor_snapshot_path=Path("examples/low_vol_dividend_quality/factor_snapshot.sample.csv"),
        required_factor_columns=LOW_VOL_REQUIRED_FACTOR_COLUMNS,
        optional_factor_columns=LOW_VOL_OPTIONAL_FACTOR_COLUMNS,
        required_operational_columns=frozenset(
            {
                "as_of",
                "snapshot_date",
                "eligible",
                "lot_size",
                "corporate_action_flag",
            }
        ),
        normalize_symbol=normalize_low_vol_symbol,
        production_source_focus=(
            "point_in_time_dividend_history",
            "forecast_dividend_yield_estimate_history",
            "three_year_cash_dividend_record_and_payout_ratio_history",
            "sp_access_hk_low_vol_high_div_methodology_and_constituent_history",
        ),
        quality_yield_focus=(
            "forecast_dividend_yield_vs_trailing_dividend_yield_same_universe",
            "dividend_yield_only_vs_dividend_quality_controls",
            "dividend_yield_trap_and_payout_cut_window",
        ),
    ),
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE: FirstSnapshotEvidenceProfile(
        profile=HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
        sample_factor_snapshot_path=Path("examples/shareholder_yield_quality/factor_snapshot.sample.csv"),
        required_factor_columns=SHAREHOLDER_REQUIRED_FACTOR_COLUMNS,
        optional_factor_columns=SHAREHOLDER_OPTIONAL_FACTOR_COLUMNS,
        required_operational_columns=frozenset(
            {
                "as_of",
                "eligible",
                "southbound_eligible",
                "lot_size",
                "corporate_action_flag",
            }
        ),
        normalize_symbol=normalize_shareholder_symbol,
        production_source_focus=(
            "hkex_buyback_disclosure_and_share_count_history",
            "hkex_next_day_share_repurchase_return_history",
            "treasury_share_retention_cancellation_and_resale_history",
            "share_buyback_mandate_and_program_waiver_history",
        ),
        quality_yield_focus=(
            "buyback_yield_raw_vs_share_count_reduction_adjusted",
            "treasury_share_resale_dilution_and_convertible_issue_window",
            "post_buyback_new_issue_convertible_and_public_float_review",
        ),
    ),
    HK_FREE_CASH_FLOW_QUALITY_PROFILE: FirstSnapshotEvidenceProfile(
        profile=HK_FREE_CASH_FLOW_QUALITY_PROFILE,
        sample_factor_snapshot_path=Path("examples/free_cash_flow_quality/factor_snapshot.sample.csv"),
        required_factor_columns=FCF_REQUIRED_FACTOR_COLUMNS,
        optional_factor_columns=FCF_OPTIONAL_FACTOR_COLUMNS,
        required_operational_columns=frozenset(
            {
                "as_of",
                "snapshot_date",
                "eligible",
                "southbound_eligible",
                "lot_size",
                "corporate_action_flag",
            }
        ),
        normalize_symbol=normalize_fcf_symbol,
        production_source_focus=(
            "fcf_formula_cash_flow_statement_lineage_history",
            "enterprise_value_market_cap_debt_cash_fx_history",
            "financial_real_estate_and_negative_fcf_exception_policy",
            "fundamental_restatement_and_reporting_date_asof_history",
        ),
        quality_yield_focus=(
            "fcf_yield_raw_vs_sector_normalized_fcf_quality",
            "free_cash_flow_restatement_reporting_date_and_sector_normalization_window",
            "negative_fcf_ev_financial_real_estate_exception_window",
        ),
    ),
}


def normalize_first_snapshot_profile(profile: str) -> str:
    normalized = str(profile or "").strip().lower().replace("-", "_")
    if normalized not in FIRST_SNAPSHOT_EVIDENCE_PROFILES:
        known = ", ".join(SUPPORTED_FIRST_SNAPSHOT_EVIDENCE_PROFILE_ORDER)
        raise ValueError(f"Unsupported first snapshot evidence profile {profile!r}; known profiles: {known}")
    return normalized


def get_first_snapshot_evidence_profile(profile: str) -> FirstSnapshotEvidenceProfile:
    return FIRST_SNAPSHOT_EVIDENCE_PROFILES[normalize_first_snapshot_profile(profile)]


def iter_first_snapshot_evidence_profiles(
    profiles: tuple[str, ...] | None = None,
) -> tuple[FirstSnapshotEvidenceProfile, ...]:
    selected = profiles or FIRST_SNAPSHOT_PROFILE_ORDER
    return tuple(get_first_snapshot_evidence_profile(profile) for profile in selected)


__all__ = [
    "FIRST_SNAPSHOT_EVIDENCE_PROFILE_VERSION",
    "FIRST_SNAPSHOT_EVIDENCE_PROFILES",
    "FirstSnapshotEvidenceProfile",
    "get_first_snapshot_evidence_profile",
    "iter_first_snapshot_evidence_profiles",
    "normalize_first_snapshot_profile",
]
