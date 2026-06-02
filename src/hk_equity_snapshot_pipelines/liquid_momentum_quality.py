from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import write_release_status_summary, write_snapshot_manifest
from .blue_chip_leader_rotation import (
    BENCHMARK_SYMBOL,
    SnapshotBuildResult,
    _read_csv,
    build_feature_snapshot,
)
from .contracts import HK_LIQUID_MOMENTUM_QUALITY_PROFILE, get_profile_contract
from .liquid_momentum_quality_strategy import compute_signals, score_candidates


def build_and_write_snapshot(
    *,
    prices_path: str | Path,
    output_dir: str | Path,
    universe_path: str | Path | None = None,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    min_adv20_hkd: float = 0.0,
    min_market_cap_hkd: float = 0.0,
) -> SnapshotBuildResult:
    contract = get_profile_contract(HK_LIQUID_MOMENTUM_QUALITY_PROFILE)
    artifact_paths = contract.artifact_paths(output_dir)
    prices = _read_csv(prices_path)
    universe = _read_csv(universe_path) if universe_path else None
    snapshot = build_feature_snapshot(prices, universe, benchmark_symbol=benchmark_symbol)
    ranking = score_candidates(
        snapshot,
        benchmark_symbol=benchmark_symbol,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
    )

    for path in artifact_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(artifact_paths["snapshot"], index=False)
    ranking.to_csv(artifact_paths["ranking"], index=False)
    write_snapshot_manifest(
        contract=contract,
        snapshot_path=artifact_paths["snapshot"],
        snapshot=snapshot,
        manifest_path=artifact_paths["manifest"],
    )
    weights, signal_description, _is_hard_defense, status_description, diagnostics = compute_signals(
        snapshot,
        current_holdings=set(),
        benchmark_symbol=benchmark_symbol,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
    )
    write_release_status_summary(
        contract=contract,
        snapshot_path=artifact_paths["snapshot"],
        manifest_path=artifact_paths["manifest"],
        ranking_path=artifact_paths["ranking"],
        summary_path=artifact_paths["release_summary"],
        snapshot=snapshot,
        signal_description=signal_description,
        status_description=status_description,
        diagnostics={**diagnostics, "target_weights": weights},
    )
    return SnapshotBuildResult(
        snapshot=snapshot,
        ranking=ranking,
        artifact_paths=artifact_paths,
        signal_description=signal_description,
        status_description=status_description,
        diagnostics=dict(diagnostics),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prices", required=True, help="CSV with date,symbol,close and optional volume/turnover_hkd columns")
    parser.add_argument("--universe", help="CSV with symbol,sector and optional eligible/market_cap_hkd/lot_size")
    parser.add_argument("--output-dir", default="data/output")
    parser.add_argument("--benchmark-symbol", default=BENCHMARK_SYMBOL)
    parser.add_argument("--min-adv20-hkd", type=float, default=0.0)
    parser.add_argument("--min-market-cap-hkd", type=float, default=0.0)
    args = parser.parse_args(argv)

    result = build_and_write_snapshot(
        prices_path=args.prices,
        universe_path=args.universe,
        output_dir=args.output_dir,
        benchmark_symbol=args.benchmark_symbol,
        min_adv20_hkd=args.min_adv20_hkd,
        min_market_cap_hkd=args.min_market_cap_hkd,
    )
    print(f"snapshot={result.artifact_paths['snapshot']}")
    print(f"manifest={result.artifact_paths['manifest']}")
    print(f"ranking={result.artifact_paths['ranking']}")
    print(f"release_summary={result.artifact_paths['release_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
