from __future__ import annotations

from pathlib import Path

from hk_equity_snapshot_pipelines.index_rebalance_event import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    result = build_and_write_snapshot(
        event_snapshot_path=ROOT / "examples" / "index_rebalance_event" / "event_snapshot.sample.csv",
        output_dir=ROOT / "data" / "output" / "index_rebalance_event",
    )
    print(f"snapshot={result.artifact_paths['snapshot']}")
    print(f"manifest={result.artifact_paths['manifest']}")
    print(f"ranking={result.artifact_paths['ranking']}")
    print(f"release_summary={result.artifact_paths['release_summary']}")
