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
HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE = "hk_low_vol_dividend_quality"
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
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE: SnapshotProfileContract(
        profile=HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
        display_name="HK A/H Premium Relative Value",
        contract_version="hk_ah_premium_relative_value.valuation_snapshot.v1",
        snapshot_filename="hk_ah_premium_relative_value_valuation_snapshot_latest.csv",
        manifest_filename="hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_ah_premium_relative_value_ranking_latest.csv",
        legacy_aliases=("hk_ah_premium", "hk_ah_relative_value"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_ah_premium_relative_value"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE: SnapshotProfileContract(
        profile=HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
        display_name="HK Blue Chip Leader Rotation",
        contract_version="hk_blue_chip_leader_rotation.feature_snapshot.v1",
        snapshot_filename="hk_blue_chip_leader_rotation_feature_snapshot_latest.csv",
        manifest_filename="hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_blue_chip_leader_rotation_ranking_latest.csv",
        legacy_aliases=("hk_blue_chip_snapshot", "hk_leader_rotation"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_blue_chip_leader_rotation"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE: SnapshotProfileContract(
        profile=HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
        display_name="HK Central SOE Value Quality Select",
        contract_version="hk_central_soe_value_quality_select.factor_snapshot.v1",
        snapshot_filename="hk_central_soe_value_quality_select_factor_snapshot_latest.csv",
        manifest_filename="hk_central_soe_value_quality_select_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_central_soe_value_quality_select_ranking_latest.csv",
        legacy_aliases=("hk_central_soe_value_quality", "hk_policy_value_quality"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_central_soe_value_quality_select"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE: SnapshotProfileContract(
        profile=HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
        display_name="HK Composite Factor Quality Value Momentum",
        contract_version="hk_composite_factor_quality_value_momentum.factor_snapshot.v1",
        snapshot_filename="hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv",
        manifest_filename="hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_composite_factor_quality_value_momentum_ranking_latest.csv",
        legacy_aliases=("hk_composite_factor", "hk_qvm_factor"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_composite_factor_quality_value_momentum"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_FREE_CASH_FLOW_QUALITY_PROFILE: SnapshotProfileContract(
        profile=HK_FREE_CASH_FLOW_QUALITY_PROFILE,
        display_name="HK Free Cash Flow Quality",
        contract_version="hk_free_cash_flow_quality.factor_snapshot.v1",
        snapshot_filename="hk_free_cash_flow_quality_factor_snapshot_latest.csv",
        manifest_filename="hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_free_cash_flow_quality_ranking_latest.csv",
        legacy_aliases=("hk_fcf_quality", "hk_free_cash_flow"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_free_cash_flow_quality"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE: SnapshotProfileContract(
        profile=HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
        display_name="HK Factor Mix QVLM Risk Parity",
        contract_version="hk_factor_mix_qvlm_risk_parity.factor_snapshot.v1",
        snapshot_filename="hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv",
        manifest_filename="hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_factor_mix_qvlm_risk_parity_ranking_latest.csv",
        legacy_aliases=("hk_qvlm_risk_parity", "hk_factor_mix_qvlm"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_factor_mix_qvlm_risk_parity"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_INDEX_REBALANCE_EVENT_PROFILE: SnapshotProfileContract(
        profile=HK_INDEX_REBALANCE_EVENT_PROFILE,
        display_name="HK Index Rebalance Event",
        contract_version="hk_index_rebalance_event.event_calendar_snapshot.v1",
        snapshot_filename="hk_index_rebalance_event_event_calendar_snapshot_latest.csv",
        manifest_filename="hk_index_rebalance_event_event_calendar_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_index_rebalance_event_ranking_latest.csv",
        legacy_aliases=("hk_index_event", "hk_rebalance_event"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_index_rebalance_event"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE: SnapshotProfileContract(
        profile=HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
        display_name="HK Low-Volatility Dividend Quality",
        contract_version="hk_low_vol_dividend_quality.factor_snapshot.v1",
        snapshot_filename="hk_low_vol_dividend_quality_factor_snapshot_latest.csv",
        manifest_filename="hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_low_vol_dividend_quality_ranking_latest.csv",
        legacy_aliases=("hk_low_vol_dividend", "hk_dividend_quality"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_low_vol_dividend_quality"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE: SnapshotProfileContract(
        profile=HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
        display_name="HK Liquid Momentum Quality",
        contract_version="hk_liquid_momentum_quality.feature_snapshot.v1",
        snapshot_filename="hk_liquid_momentum_quality_feature_snapshot_latest.csv",
        manifest_filename="hk_liquid_momentum_quality_feature_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_liquid_momentum_quality_ranking_latest.csv",
        legacy_aliases=("hk_momentum_quality", "hk_liquid_momentum"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_liquid_momentum_quality"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE: SnapshotProfileContract(
        profile=HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
        display_name="HK Quality Growth Low Volatility",
        contract_version="hk_quality_growth_low_volatility.factor_snapshot.v1",
        snapshot_filename="hk_quality_growth_low_volatility_factor_snapshot_latest.csv",
        manifest_filename="hk_quality_growth_low_volatility_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_quality_growth_low_volatility_ranking_latest.csv",
        legacy_aliases=("hk_quality_growth_low_vol", "hk_qglv"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_quality_growth_low_volatility"
        ),
        manifest_required_by_runtime=True,
    ),

    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE: SnapshotProfileContract(
        profile=HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
        display_name="HK Residual Momentum Quality",
        contract_version="hk_residual_momentum_quality.factor_snapshot.v1",
        snapshot_filename="hk_residual_momentum_quality_factor_snapshot_latest.csv",
        manifest_filename="hk_residual_momentum_quality_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_residual_momentum_quality_ranking_latest.csv",
        legacy_aliases=("hk_residual_momentum", "hk_industry_neutral_momentum"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_residual_momentum_quality"
        ),
        manifest_required_by_runtime=True,
    ),

    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE: SnapshotProfileContract(
        profile=HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
        display_name="HK Shareholder Yield Quality",
        contract_version="hk_shareholder_yield_quality.factor_snapshot.v1",
        snapshot_filename="hk_shareholder_yield_quality_factor_snapshot_latest.csv",
        manifest_filename="hk_shareholder_yield_quality_factor_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_shareholder_yield_quality_ranking_latest.csv",
        legacy_aliases=("hk_shareholder_yield", "hk_capital_return_quality"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_shareholder_yield_quality"
        ),
        manifest_required_by_runtime=True,
    ),
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE: SnapshotProfileContract(
        profile=HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
        display_name="HK Southbound Flow Momentum",
        contract_version="hk_southbound_flow_momentum.flow_snapshot.v1",
        snapshot_filename="hk_southbound_flow_momentum_flow_snapshot_latest.csv",
        manifest_filename="hk_southbound_flow_momentum_flow_snapshot_latest.csv.manifest.json",
        ranking_filename="hk_southbound_flow_momentum_ranking_latest.csv",
        legacy_aliases=("hk_southbound_momentum", "hk_flow_momentum"),
        neutral_gcs_prefix_hint=(
            "gs://qsl-runtime-logs-interactivebrokersquant/strategy-artifacts/hk_equity/"
            "hk_southbound_flow_momentum"
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
