from __future__ import annotations

import pytest

from hk_equity_snapshot_pipelines.contracts import (
    HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE,
    get_profile_contract,
    list_profile_contracts,
)


REJECTED_PROFILES = (
    "hk_ah_premium_relative_value",
    "hk_blue_chip_leader_rotation",
    "hk_central_soe_value_quality_select",
    "hk_composite_factor_quality_value_momentum",
    "hk_factor_mix_qvlm_risk_parity",
    "hk_free_cash_flow_quality",
    "hk_index_rebalance_event",
    "hk_liquid_momentum_quality",
    "hk_quality_growth_low_volatility",
    "hk_residual_momentum_quality",
    "hk_shareholder_yield_quality",
    "hk_southbound_flow_momentum",
)


def test_contract_surface_keeps_only_low_vol_dividend_quality():
    contracts = list_profile_contracts()

    assert [contract.profile for contract in contracts] == [HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE]
    contract = get_profile_contract("hk-low-vol-dividend-quality-snapshot")
    assert contract.profile == HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE
    assert contract.contract_version == "hk_low_vol_dividend_quality_snapshot.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_low_vol_dividend_quality_snapshot_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True


@pytest.mark.parametrize(
    "profile",
    [
        "hk_dividend_quality",
        "hk_low_vol_dividend",
        "hk_low_vol_dividend_snapshot",
    ],
)
def test_legacy_aliases_are_not_preserved(profile: str):
    with pytest.raises(ValueError, match="Unknown snapshot profile"):
        get_profile_contract(profile)


@pytest.mark.parametrize("profile", REJECTED_PROFILES)
def test_rejected_snapshot_profiles_are_not_active_contracts(profile: str):
    with pytest.raises(ValueError, match="Unknown snapshot profile"):
        get_profile_contract(profile)
