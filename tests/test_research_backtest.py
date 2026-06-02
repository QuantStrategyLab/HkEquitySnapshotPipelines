from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines.blue_chip_leader_rotation import build_feature_snapshot
from hk_equity_snapshot_pipelines.liquid_momentum_quality_strategy import compute_signals
from hk_equity_snapshot_pipelines.research_backtest import run_snapshot_backtest, summarize_backtest

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "examples" / "blue_chip" / "prices.sample.csv"
UNIVERSE = ROOT / "examples" / "blue_chip" / "universe.sample.csv"
SCRIPT = ROOT / "scripts" / "research_hk_liquid_momentum_quality_backtest.py"


def test_run_snapshot_backtest_returns_metrics_from_sample_inputs():
    prices = pd.read_csv(PRICES)
    universe = pd.read_csv(UNIVERSE)

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
        cost_bps=10.0,
    )
    summary = summarize_backtest(backtest=backtest, periods={"full": (None, None)})

    assert summary["data"]["rows"] > 200
    assert summary["data"]["average_gross_exposure"] >= 0.0
    assert summary["metrics"]["strategy"]["full"]["days"] > 200
    assert backtest["diagnostics_by_date"]


def test_liquid_momentum_research_script_json_output():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--prices", str(PRICES), "--universe", str(UNIVERSE)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_liquid_momentum_quality"
    assert payload["research_status"] == "sample_harness_only_not_production_backtest"
    assert payload["metrics"]["strategy"]["full"]["days"] > 200
