from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.contracts import get_profile_contract
from hk_equity_snapshot_pipelines.index_rebalance_event import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]
EVENT_SNAPSHOT = ROOT / "examples" / "index_rebalance_event" / "event_snapshot.sample.csv"


def test_index_rebalance_event_sample_snapshot_has_required_rows():
    snapshot = pd.read_csv(EVENT_SNAPSHOT)

    assert set(snapshot["symbol"].astype(str).str.zfill(5)) >= {"02800", "03750", "03993"}
    assert snapshot["effective_date"].notna().all()
    assert snapshot["estimated_slippage_bps"].notna().all()


def test_build_and_write_index_rebalance_event_outputs_artifact_contract(tmp_path):
    result = build_and_write_snapshot(
        event_snapshot_path=EVENT_SNAPSHOT,
        output_dir=tmp_path,
    )
    contract = get_profile_contract("hk_rebalance_event")
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
