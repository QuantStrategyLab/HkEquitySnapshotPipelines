from __future__ import annotations

from hk_equity_snapshot_pipelines.blue_chip_strategy import REQUIRE_SNAPSHOT_MANIFEST, SNAPSHOT_CONTRACT_VERSION
from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_snapshot_pipelines.ah_premium_relative_value_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as AH_PREMIUM_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.ah_premium_relative_value_strategy import (
    SNAPSHOT_CONTRACT_VERSION as AH_PREMIUM_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.central_soe_value_quality_select_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as CENTRAL_SOE_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.central_soe_value_quality_select_strategy import (
    SNAPSHOT_CONTRACT_VERSION as CENTRAL_SOE_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.composite_factor_quality_value_momentum_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as COMPOSITE_FACTOR_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.composite_factor_quality_value_momentum_strategy import (
    SNAPSHOT_CONTRACT_VERSION as COMPOSITE_FACTOR_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.free_cash_flow_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as FREE_CASH_FLOW_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.free_cash_flow_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as FREE_CASH_FLOW_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.factor_mix_qvlm_risk_parity_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as FACTOR_MIX_QVLM_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.factor_mix_qvlm_risk_parity_strategy import (
    SNAPSHOT_CONTRACT_VERSION as FACTOR_MIX_QVLM_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.index_rebalance_event_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as INDEX_REBALANCE_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.index_rebalance_event_strategy import (
    SNAPSHOT_CONTRACT_VERSION as INDEX_REBALANCE_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.liquid_momentum_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as LIQUID_MOMENTUM_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.liquid_momentum_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as LIQUID_MOMENTUM_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as LOW_VOL_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.quality_growth_low_volatility_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as QUALITY_GROWTH_LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.quality_growth_low_volatility_strategy import (
    SNAPSHOT_CONTRACT_VERSION as QUALITY_GROWTH_LOW_VOL_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.residual_momentum_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as RESIDUAL_MOMENTUM_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.residual_momentum_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as RESIDUAL_MOMENTUM_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.shareholder_yield_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as SHAREHOLDER_YIELD_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.shareholder_yield_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as SHAREHOLDER_YIELD_SNAPSHOT_CONTRACT_VERSION,
)
from hk_equity_snapshot_pipelines.southbound_flow_momentum_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as SOUTHBOUND_FLOW_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.southbound_flow_momentum_strategy import (
    SNAPSHOT_CONTRACT_VERSION as SOUTHBOUND_FLOW_SNAPSHOT_CONTRACT_VERSION,
)


def test_snapshot_contract_matches_local_snapshot_strategy_contract():
    contract = get_profile_contract("hk_blue_chip_leader_rotation")

    assert contract.profile == "hk_blue_chip_leader_rotation"
    assert contract.contract_version == SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is REQUIRE_SNAPSHOT_MANIFEST is True


def test_ah_premium_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_ah_premium_relative_value")

    assert contract.profile == "hk_ah_premium_relative_value"
    assert contract.contract_version == AH_PREMIUM_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is AH_PREMIUM_REQUIRE_SNAPSHOT_MANIFEST is True


def test_central_soe_value_quality_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_central_soe_value_quality_select")

    assert contract.profile == "hk_central_soe_value_quality_select"
    assert contract.contract_version == CENTRAL_SOE_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is CENTRAL_SOE_REQUIRE_SNAPSHOT_MANIFEST is True


def test_composite_factor_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_composite_factor_quality_value_momentum")

    assert contract.profile == "hk_composite_factor_quality_value_momentum"
    assert contract.contract_version == COMPOSITE_FACTOR_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is COMPOSITE_FACTOR_REQUIRE_SNAPSHOT_MANIFEST is True


def test_free_cash_flow_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_free_cash_flow_quality")

    assert contract.profile == "hk_free_cash_flow_quality"
    assert contract.contract_version == FREE_CASH_FLOW_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is FREE_CASH_FLOW_REQUIRE_SNAPSHOT_MANIFEST is True


def test_factor_mix_qvlm_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_factor_mix_qvlm_risk_parity")

    assert contract.profile == "hk_factor_mix_qvlm_risk_parity"
    assert contract.contract_version == FACTOR_MIX_QVLM_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is FACTOR_MIX_QVLM_REQUIRE_SNAPSHOT_MANIFEST is True


def test_index_rebalance_event_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_index_rebalance_event")

    assert contract.profile == "hk_index_rebalance_event"
    assert contract.contract_version == INDEX_REBALANCE_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is INDEX_REBALANCE_REQUIRE_SNAPSHOT_MANIFEST is True


def test_low_vol_dividend_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_low_vol_dividend_quality")

    assert contract.profile == "hk_low_vol_dividend_quality"
    assert contract.contract_version == LOW_VOL_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST is True


def test_liquid_momentum_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_liquid_momentum_quality")

    assert contract.profile == "hk_liquid_momentum_quality"
    assert contract.contract_version == LIQUID_MOMENTUM_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is LIQUID_MOMENTUM_REQUIRE_SNAPSHOT_MANIFEST is True


def test_quality_growth_low_volatility_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_quality_growth_low_volatility")

    assert contract.profile == "hk_quality_growth_low_volatility"
    assert contract.contract_version == QUALITY_GROWTH_LOW_VOL_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is QUALITY_GROWTH_LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST is True


def test_residual_momentum_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_residual_momentum_quality")

    assert contract.profile == "hk_residual_momentum_quality"
    assert contract.contract_version == RESIDUAL_MOMENTUM_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is RESIDUAL_MOMENTUM_REQUIRE_SNAPSHOT_MANIFEST is True


def test_shareholder_yield_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_shareholder_yield_quality")

    assert contract.profile == "hk_shareholder_yield_quality"
    assert contract.contract_version == SHAREHOLDER_YIELD_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is SHAREHOLDER_YIELD_REQUIRE_SNAPSHOT_MANIFEST is True


def test_southbound_flow_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_southbound_flow_momentum")

    assert contract.profile == "hk_southbound_flow_momentum"
    assert contract.contract_version == SOUTHBOUND_FLOW_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is SOUTHBOUND_FLOW_REQUIRE_SNAPSHOT_MANIFEST is True
