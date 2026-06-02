from __future__ import annotations

from pathlib import Path

from hk_equity_snapshot_pipelines.central_soe_value_quality_select import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_and_write_snapshot(
        factor_snapshot_path=ROOT / "examples" / "central_soe_value_quality_select" / "factor_snapshot.sample.csv",
        output_dir=ROOT / "data" / "output" / "central_soe_value_quality_select",
    )
    for key, path in result.artifact_paths.items():
        print(f"{key}: {path}")
