from __future__ import annotations

from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_snapshot_pipelines.low_vol_dividend_quality_strategy import (
    REQUIRE_SNAPSHOT_MANIFEST as LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST,
)
from hk_equity_snapshot_pipelines.low_vol_dividend_quality_strategy import (
    SNAPSHOT_CONTRACT_VERSION as LOW_VOL_SNAPSHOT_CONTRACT_VERSION,
)


def test_low_vol_dividend_contract_matches_local_strategy_contract():
    contract = get_profile_contract("hk_low_vol_dividend_quality_snapshot")

    assert contract.profile == "hk_low_vol_dividend_quality_snapshot"
    assert contract.contract_version == LOW_VOL_SNAPSHOT_CONTRACT_VERSION
    assert contract.manifest_required_by_runtime is LOW_VOL_REQUIRE_SNAPSHOT_MANIFEST is True
