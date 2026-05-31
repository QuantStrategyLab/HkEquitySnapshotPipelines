from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.blue_chip_leader_rotation import (
    build_and_write_snapshot,
    build_feature_snapshot,
)
from hk_equity_snapshot_pipelines.contracts import get_profile_contract

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "examples" / "blue_chip" / "prices.sample.csv"
UNIVERSE = ROOT / "examples" / "blue_chip" / "universe.sample.csv"


def test_build_feature_snapshot_from_sample_inputs():
    snapshot = build_feature_snapshot(pd.read_csv(PRICES), pd.read_csv(UNIVERSE))

    assert set(snapshot["symbol"]) >= {"02800", "00700", "03690"}
    assert snapshot["as_of"].nunique() == 1
    assert snapshot["close_hkd"].notna().all()
    assert snapshot["adv20_hkd"].gt(0).all()
    assert snapshot.loc[snapshot["symbol"] == "00700", "sector"].iloc[0] == "Technology"


def test_build_and_write_snapshot_outputs_artifact_contract(tmp_path):
    result = build_and_write_snapshot(
        prices_path=PRICES,
        universe_path=UNIVERSE,
        output_dir=tmp_path,
    )
    contract = get_profile_contract("hk_blue_chip_leader_rotation")
    paths = contract.artifact_paths(tmp_path)

    for path in paths.values():
        assert path.exists(), path
    manifest = json.loads(paths["manifest"].read_text())
    assert manifest["strategy_profile"] == contract.profile
    assert manifest["contract_version"] == contract.contract_version
    assert manifest["row_count"] == len(result.snapshot)
    assert manifest["snapshot_sha256"]

    summary = json.loads(paths["release_summary"].read_text())
    assert summary["release_status"] == "ready"
    assert summary["strategy_profile"] == contract.profile
    assert summary["diagnostics"]["selected_count"] >= 1
    assert len(result.ranking) >= 1
