from __future__ import annotations

from pathlib import Path

from hk_equity_snapshot_pipelines.shareholder_yield_quality import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    result = build_and_write_snapshot(
        factor_snapshot_path=ROOT / "examples" / "shareholder_yield_quality" / "factor_snapshot.sample.csv",
        output_dir=ROOT / "data" / "output" / "shareholder_yield_quality",
    )
    print(f"snapshot={result.artifact_paths['snapshot']}")
    print(f"manifest={result.artifact_paths['manifest']}")
    print(f"ranking={result.artifact_paths['ranking']}")
    print(f"release_summary={result.artifact_paths['release_summary']}")
