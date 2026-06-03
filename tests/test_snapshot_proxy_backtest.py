from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.snapshot_proxy_backtest import (
    DEFAULT_SYMBOLS,
    PROXY_BACKTEST_VERSION,
    PROXY_RESEARCH_STATUS,
    build_proxy_cycle_backtest,
    generate_synthetic_price_history,
    run_proxy_cycle_backtest,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "research_hk_snapshot_proxy_cycle_backtest.py"


def test_proxy_cycle_backtest_summarizes_long_medium_short_periods():
    prices, meta = generate_synthetic_price_history(
        symbols=DEFAULT_SYMBOLS[:8],
        start="2020-01-01",
        end="2026-06-03",
    )

    payload = build_proxy_cycle_backtest(prices=prices, price_meta=meta, top_n=3, cost_bps=20.0)

    assert payload["backtest_version"] == PROXY_BACKTEST_VERSION
    assert payload["research_status"] == PROXY_RESEARCH_STATUS
    assert payload["config"]["max_drawdown_gate"] == 0.30
    assert set(payload["periods"]) == {"long", "medium", "short"}
    assert payload["ranking"]
    assert len(payload["profiles"]) == 13
    for row in payload["profiles"]:
        assert set(row["metrics"]) == {"long", "medium", "short"}
        assert set(row["drawdown_30_pass_by_period"]) == {"long", "medium", "short"}
        assert "promotion_scope" in row
        assert "proxy_kind" in row


def test_run_proxy_cycle_backtest_supports_synthetic_source():
    payload = run_proxy_cycle_backtest(
        price_source="synthetic",
        symbols=DEFAULT_SYMBOLS[:4],
        start="2024-01-01",
        end="2026-06-03",
        top_n=2,
    )

    assert payload["price_meta"]["price_source"] == "deterministic_synthetic_price_history"
    assert payload["data"]["trading_days"] > 500
    assert payload["ranking"][0]["proxy_rank"] == 1
    assert any(row["profile"] == "hk_low_vol_dividend_quality_snapshot" for row in payload["profiles"])


def test_proxy_cycle_backtest_script_json_synthetic():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--price-source",
            "synthetic",
            "--start",
            "2024-01-01",
            "--end",
            "2026-06-03",
            "--symbol",
            "0005.HK",
            "--symbol",
            "0700.HK",
            "--symbol",
            "0941.HK",
            "--symbol",
            "1299.HK",
            "--top-n",
            "2",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["backtest_version"] == PROXY_BACKTEST_VERSION
    assert payload["research_status"] == PROXY_RESEARCH_STATUS
    assert payload["periods"]["short"]["end"] == "2026-06-03"
    assert payload["price_meta"]["price_source"] == "deterministic_synthetic_price_history"
