from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.ah_premium_relative_value import build_and_write_snapshot
from hk_equity_snapshot_pipelines.contracts import get_profile_contract

ROOT = Path(__file__).resolve().parents[1]
VALUATION_SNAPSHOT = ROOT / "examples" / "ah_premium_relative_value" / "valuation_snapshot.sample.csv"


def test_ah_premium_sample_snapshot_has_required_rows():
    snapshot = pd.read_csv(VALUATION_SNAPSHOT)

    assert set(snapshot["symbol"].astype(str).str.zfill(5)) >= {"02800", "03968", "02318"}
    assert snapshot["ah_premium_pct"].notna().all()
    assert snapshot["ah_premium_percentile_3y"].notna().all()


def test_build_and_write_ah_premium_outputs_artifact_contract(tmp_path):
    result = build_and_write_snapshot(
        valuation_snapshot_path=VALUATION_SNAPSHOT,
        output_dir=tmp_path,
    )
    contract = get_profile_contract("hk_ah_relative_value")
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
