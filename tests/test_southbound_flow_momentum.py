from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_snapshot_pipelines.southbound_flow_momentum import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]
FLOW_SNAPSHOT = ROOT / "examples" / "southbound_flow_momentum" / "flow_snapshot.sample.csv"


def test_southbound_flow_sample_snapshot_has_required_rows():
    snapshot = pd.read_csv(FLOW_SNAPSHOT)

    assert set(snapshot["symbol"].astype(str).str.zfill(5)) >= {"02800", "00700", "00941"}
    assert snapshot["southbound_net_buy_hkd_20d"].notna().all()
    assert snapshot["flow_persistence_score"].notna().all()


def test_build_and_write_southbound_flow_outputs_artifact_contract(tmp_path):
    result = build_and_write_snapshot(
        flow_snapshot_path=FLOW_SNAPSHOT,
        output_dir=tmp_path,
    )
    contract = get_profile_contract("hk_southbound_flow_momentum")
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
    assert summary["diagnostics"]["snapshot_contract_version"] == contract.contract_version
    assert len(result.ranking) >= 1
