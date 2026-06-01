from __future__ import annotations

from hk_equity_snapshot_pipelines.blue_chip_strategy import REQUIRE_SNAPSHOT_MANIFEST, SNAPSHOT_CONTRACT_VERSION
from hk_equity_snapshot_pipelines.contracts import get_profile_contract


def test_snapshot_contract_matches_local_snapshot_strategy_contract():
    contract = get_profile_contract("hk_blue_chip_leader_rotation")

    assert contract.profile == "hk_blue_chip_leader_rotation"
    assert contract.contract_version == SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is REQUIRE_SNAPSHOT_MANIFEST is True
