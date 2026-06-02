from __future__ import annotations

from hk_equity_snapshot_pipelines.contracts import (
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
    get_profile_contract,
    list_profile_contracts,
)


def test_contract_exposes_ah_premium_relative_value_artifact_names():
    contract = get_profile_contract("hk-ah-premium")

    assert contract.profile == HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE
    assert contract.contract_version == "hk_ah_premium_relative_value.valuation_snapshot.v1"
    assert contract.snapshot_filename == "hk_ah_premium_relative_value_valuation_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_ah_premium_relative_value_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_hk_blue_chip_artifact_names():
    contract = get_profile_contract("hk-blue-chip-snapshot")

    assert contract.profile == HK_BLUE_CHIP_LEADER_ROTATION_PROFILE
    assert contract.contract_version == "hk_blue_chip_leader_rotation.feature_snapshot.v1"
    assert contract.snapshot_filename == "hk_blue_chip_leader_rotation_feature_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_central_soe_value_quality_artifact_names():
    contract = get_profile_contract("hk-policy-value-quality")

    assert contract.profile == HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE
    assert contract.contract_version == "hk_central_soe_value_quality_select.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_central_soe_value_quality_select_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_central_soe_value_quality_select_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_central_soe_value_quality_select_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_composite_factor_artifact_names():
    contract = get_profile_contract("hk-qvm-factor")

    assert contract.profile == HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE
    assert contract.contract_version == "hk_composite_factor_quality_value_momentum.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv"
    assert contract.manifest_filename == (
        "hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json"
    )
    assert contract.ranking_filename == "hk_composite_factor_quality_value_momentum_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_free_cash_flow_quality_artifact_names():
    contract = get_profile_contract("hk-fcf-quality")

    assert contract.profile == HK_FREE_CASH_FLOW_QUALITY_PROFILE
    assert contract.contract_version == "hk_free_cash_flow_quality.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_free_cash_flow_quality_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_free_cash_flow_quality_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_factor_mix_qvlm_risk_parity_artifact_names():
    contract = get_profile_contract("hk-factor-mix-qvlm")

    assert contract.profile == HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE
    assert contract.contract_version == "hk_factor_mix_qvlm_risk_parity.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_factor_mix_qvlm_risk_parity_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_index_rebalance_event_artifact_names():
    contract = get_profile_contract("hk-index-event")

    assert contract.profile == HK_INDEX_REBALANCE_EVENT_PROFILE
    assert contract.contract_version == "hk_index_rebalance_event.event_calendar_snapshot.v1"
    assert contract.snapshot_filename == "hk_index_rebalance_event_event_calendar_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_index_rebalance_event_event_calendar_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_index_rebalance_event_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_low_vol_dividend_quality_artifact_names():
    contract = get_profile_contract("hk-dividend-quality")

    assert contract.profile == HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE
    assert contract.contract_version == "hk_low_vol_dividend_quality.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_low_vol_dividend_quality_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_low_vol_dividend_quality_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_liquid_momentum_quality_artifact_names():
    contract = get_profile_contract("hk-momentum-quality")

    assert contract.profile == HK_LIQUID_MOMENTUM_QUALITY_PROFILE
    assert contract.contract_version == "hk_liquid_momentum_quality.feature_snapshot.v1"
    assert contract.snapshot_filename == "hk_liquid_momentum_quality_feature_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_liquid_momentum_quality_feature_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_liquid_momentum_quality_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_quality_growth_low_volatility_artifact_names():
    contract = get_profile_contract("hk-qglv")

    assert contract.profile == HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE
    assert contract.contract_version == "hk_quality_growth_low_volatility.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_quality_growth_low_volatility_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_quality_growth_low_volatility_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_quality_growth_low_volatility_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_residual_momentum_quality_artifact_names():
    contract = get_profile_contract("hk-residual-momentum")

    assert contract.profile == HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE
    assert contract.contract_version == "hk_residual_momentum_quality.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_residual_momentum_quality_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_residual_momentum_quality_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_residual_momentum_quality_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_shareholder_yield_quality_artifact_names():
    contract = get_profile_contract("hk-capital-return-quality")

    assert contract.profile == HK_SHAREHOLDER_YIELD_QUALITY_PROFILE
    assert contract.contract_version == "hk_shareholder_yield_quality.factor_snapshot.v1"
    assert contract.snapshot_filename == "hk_shareholder_yield_quality_factor_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_shareholder_yield_quality_factor_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_shareholder_yield_quality_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()


def test_contract_exposes_southbound_flow_momentum_artifact_names():
    contract = get_profile_contract("hk-flow-momentum")

    assert contract.profile == HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE
    assert contract.contract_version == "hk_southbound_flow_momentum.flow_snapshot.v1"
    assert contract.snapshot_filename == "hk_southbound_flow_momentum_flow_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_southbound_flow_momentum_flow_snapshot_latest.csv.manifest.json"
    assert contract.ranking_filename == "hk_southbound_flow_momentum_ranking_latest.csv"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()
