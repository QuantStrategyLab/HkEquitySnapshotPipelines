from __future__ import annotations

from pathlib import Path

from hk_equity_snapshot_pipelines.factor_mix_qvlm_risk_parity import build_and_write_snapshot

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    result = build_and_write_snapshot(
        factor_snapshot_path=ROOT / "examples" / "factor_mix_qvlm_risk_parity" / "factor_snapshot.sample.csv",
        output_dir=ROOT / "data" / "output" / "factor_mix_qvlm_risk_parity",
    )
    for key, path in result.artifact_paths.items():
        print(f"{key}: {path}")
