from __future__ import annotations

from hk_equity_snapshot_pipelines.contracts import (
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
    get_profile_contract,
    list_profile_contracts,
)


def test_contract_exposes_hk_blue_chip_artifact_names():
    contract = get_profile_contract("hk-blue-chip-snapshot")

    assert contract.profile == HK_BLUE_CHIP_LEADER_ROTATION_PROFILE
    assert contract.contract_version == "hk_blue_chip_leader_rotation.feature_snapshot.v1"
    assert contract.snapshot_filename == "hk_blue_chip_leader_rotation_feature_snapshot_latest.csv"
    assert contract.manifest_filename == "hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json"
    assert contract.manifest_required_by_runtime is True
    assert contract in list_profile_contracts()
