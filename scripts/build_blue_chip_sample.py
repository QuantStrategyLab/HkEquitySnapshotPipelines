from __future__ import annotations

from pathlib import Path

from hk_equity_snapshot_pipelines.blue_chip_leader_rotation import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_and_write_snapshot(
        prices_path=ROOT / "examples" / "blue_chip" / "prices.sample.csv",
        universe_path=ROOT / "examples" / "blue_chip" / "universe.sample.csv",
        output_dir=ROOT / "data" / "output",
    )
    for key, path in result.artifact_paths.items():
        print(f"{key}: {path}")
