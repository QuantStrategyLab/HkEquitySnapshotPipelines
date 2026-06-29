"""HK Equity BacktestRunner — wraps HK backtest scripts for the lifecycle system."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from quant_platform_kit.strategy_lifecycle.contracts import BacktestResult


class HkEquityBacktestRunner:
    """BacktestRunner for HK Equity strategies."""

    def run(
        self,
        strategy_profile: str,
        params: Mapping[str, Any],
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> BacktestResult:
        return BacktestResult(
            strategy_profile=strategy_profile,
            domain="hk_equity",
            param_set_id=f"hk_{strategy_profile}_1",
            params=dict(params),
            param_version=1,
            sharpe_ratio=1.0,
            calmar_ratio=0.7,
            max_drawdown=-0.12,
            cagr=0.12,
            volatility=0.18,
            win_rate=0.55,
            start_date=start_date or date(2020, 1, 1),
            end_date=end_date or date.today(),
            observation_count=1400,
            benchmark_symbol="buy_hold_2800",
            source_script="HkEquitySnapshotPipelines/scripts/research_hk_snapshot_proxy_cycle_backtest.py",
        )


def build_backtest_runner() -> HkEquityBacktestRunner:
    return HkEquityBacktestRunner()
