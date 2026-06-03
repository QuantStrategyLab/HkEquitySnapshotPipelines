from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SOURCE_PROJECT = "HkEquitySnapshotPipelines"
HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE = "hk_ah_premium_relative_value"
HK_BLUE_CHIP_LEADER_ROTATION_PROFILE = "hk_blue_chip_leader_rotation"
HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE = "hk_central_soe_value_quality_select"
HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE = "hk_composite_factor_quality_value_momentum"
HK_FREE_CASH_FLOW_QUALITY_PROFILE = "hk_free_cash_flow_quality"
HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE = "hk_factor_mix_qvlm_risk_parity"
HK_INDEX_REBALANCE_EVENT_PROFILE = "hk_index_rebalance_event"
HK_LIQUID_MOMENTUM_QUALITY_PROFILE = "hk_liquid_momentum_quality"
HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE = "hk_low_vol_dividend_quality_snapshot"
HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE = "hk_quality_growth_low_volatility"
HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE = "hk_residual_momentum_quality"
HK_SHAREHOLDER_YIELD_QUALITY_PROFILE = "hk_shareholder_yield_quality"
HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE = "hk_southbound_flow_momentum"


@dataclass(frozen=True)
class SnapshotProfileContract:
    profile: str
    display_name: str
    contract_version: str
    snapshot_filename: str
    manifest_filename: str
    ranking_filename: str
    release_summary_filename: str = "release_status_summary.json"
    legacy_aliases: tuple[str, ...] = ()
    neutral_gcs_prefix_hint: str | None = None
    manifest_required_by_runtime: bool = True

    def artifact_paths(self, output_dir: str | Path) -> dict[str, Path]:
        root = Path(output_dir)
        return {
            "snapshot": root / self.snapshot_filename,
            "manifest": root / self.manifest_filename,
            "ranking": root / self.ranking_filename,
            "release_summary": root / self.release_summary_filename,
        }


_PROFILE_CONTRACTS = {
    HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE: SnapshotProfileContract(
        profile=HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE,
        display_name="HK Low-Vol Dividend Quality Snapshot",
        contract_version="hk_low_vol_dividend_quality_snapshot.factor_snapshot.v1",
        snapshot_filename="hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv",
        manifest_filename="hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_low_vol_dividend_quality_snapshot_ranking_latest.csv",
        legacy_aliases=(),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_low_vol_dividend_quality_snapshot"
        ),
        manifest_required_by_runtime=True,
    ),
}

_ALIAS_TO_PROFILE = {
    alias: contract.profile
    for contract in _PROFILE_CONTRACTS.values()
    for alias in (contract.profile, *contract.legacy_aliases)
}


def get_profile_contract(profile: str) -> SnapshotProfileContract:
    normalized = str(profile or "").strip().lower().replace("-", "_")
    canonical = _ALIAS_TO_PROFILE.get(normalized)
    if canonical is None:
        known = ", ".join(sorted(_PROFILE_CONTRACTS))
        raise ValueError(f"Unknown snapshot profile {profile!r}; known profiles: {known}")
    return _PROFILE_CONTRACTS[canonical]


def list_profile_contracts() -> tuple[SnapshotProfileContract, ...]:
    return tuple(_PROFILE_CONTRACTS.values())
