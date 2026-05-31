from __future__ import annotations

from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_strategies.catalog import get_strategy_definition
from hk_equity_strategies.runtime_adapters import get_platform_runtime_adapter


def test_snapshot_contract_matches_strategy_runtime_adapter():
    contract = get_profile_contract("hk_blue_chip_leader_rotation")
    definition = get_strategy_definition(contract.profile)
    adapter = get_platform_runtime_adapter(contract.profile, platform_id="ibkr")

    assert definition.domain == "hk_equity"
    assert definition.required_inputs == frozenset({"feature_snapshot"})
    assert adapter.snapshot_contract_version == contract.contract_version
    assert adapter.require_snapshot_manifest is True
    assert contract.manifest_required_by_runtime is True
