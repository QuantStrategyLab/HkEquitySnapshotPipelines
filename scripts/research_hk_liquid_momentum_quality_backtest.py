#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from hk_equity_snapshot_pipelines.blue_chip_leader_rotation import build_feature_snapshot
from hk_equity_snapshot_pipelines.liquid_momentum_quality_strategy import compute_signals
from hk_equity_snapshot_pipelines.research_backtest import run_snapshot_backtest, summarize_backtest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRICES = ROOT / "examples" / "blue_chip" / "prices.sample.csv"
DEFAULT_UNIVERSE = ROOT / "examples" / "blue_chip" / "universe.sample.csv"


def run(
    *,
    prices_path: Path = DEFAULT_PRICES,
    universe_path: Path | None = DEFAULT_UNIVERSE,
    cost_bps: float = 10.0,
    rebalance_frequency: str = "monthly",
) -> dict[str, Any]:
    prices = pd.read_csv(prices_path)
    universe = pd.read_csv(universe_path) if universe_path else None

    def snapshot_builder(history: pd.DataFrame, local_universe: pd.DataFrame | None) -> pd.DataFrame:
        return build_feature_snapshot(history, local_universe)

    def signal_builder(snapshot: pd.DataFrame, current_holdings: set[str]):
        return compute_signals(
            snapshot,
            current_holdings=current_holdings,
            min_adv20_hkd=0.0,
            min_market_cap_hkd=0.0,
        )

    backtest = run_snapshot_backtest(
        prices=prices,
        universe=universe,
        snapshot_builder=snapshot_builder,
        signal_builder=signal_builder,
        rebalance_frequency=rebalance_frequency,  # type: ignore[arg-type]
        cost_bps=float(cost_bps),
    )
    close = backtest["close"]
    start = pd.Timestamp(close.index.min()).date().isoformat()
    end = pd.Timestamp(close.index.max()).date().isoformat()
    payload = summarize_backtest(
        backtest=backtest,
        periods={
            "full": (start, end),
            "sample_first_half": (start, pd.Timestamp(close.index[len(close) // 2]).date().isoformat()),
            "sample_second_half": (pd.Timestamp(close.index[len(close) // 2 + 1]).date().isoformat(), end),
        },
    )
    payload["profile"] = "hk_liquid_momentum_quality"
    payload["config"] = {
        "prices_path": str(prices_path),
        "universe_path": str(universe_path) if universe_path else None,
        "cost_bps": float(cost_bps),
        "rebalance_frequency": rebalance_frequency,
        "data_source": "local_csv",
    }
    payload["research_status"] = "sample_harness_only_not_production_backtest"
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest HK liquid momentum quality snapshot scaffold from local CSV inputs.")
    parser.add_argument("--prices", type=Path, default=DEFAULT_PRICES)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--rebalance-frequency", choices=("monthly", "weekly"), default="monthly")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    payload = run(
        prices_path=args.prices,
        universe_path=args.universe,
        cost_bps=args.cost_bps,
        rebalance_frequency=args.rebalance_frequency,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_output:
        args.json_output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
