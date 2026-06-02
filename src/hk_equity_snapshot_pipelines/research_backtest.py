from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any, Literal

import pandas as pd

from .blue_chip_leader_rotation import _normalize_prices

RebalanceFrequency = Literal["monthly", "weekly"]
SnapshotBuilder = Callable[[pd.DataFrame, pd.DataFrame | None], pd.DataFrame]
SignalBuilder = Callable[[pd.DataFrame, set[str]], tuple[dict[str, float], str, bool, str, dict[str, Any]]]


def build_close_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    price_frame = _normalize_prices(prices)
    close = price_frame.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
    close = close.sort_index().ffill().dropna(how="all")
    if close.empty:
        raise ValueError("prices must contain at least one valid close series")
    return close


def rebalance_dates(close: pd.DataFrame, frequency: RebalanceFrequency) -> pd.DatetimeIndex:
    if frequency == "monthly":
        return close.resample("ME").last().index
    if frequency == "weekly":
        return close.resample("W-FRI").last().index
    raise ValueError("rebalance_frequency must be 'monthly' or 'weekly'")


def run_snapshot_backtest(
    *,
    prices: pd.DataFrame,
    universe: pd.DataFrame | None,
    snapshot_builder: SnapshotBuilder,
    signal_builder: SignalBuilder,
    rebalance_frequency: RebalanceFrequency = "monthly",
    cost_bps: float = 10.0,
    initial_holdings: set[str] | None = None,
) -> dict[str, Any]:
    close = build_close_matrix(prices)
    price_frame = _normalize_prices(prices)
    current_holdings = set(initial_holdings or set())
    rows: list[dict[str, Any]] = []
    diagnostics_by_date: dict[str, dict[str, Any]] = {}

    for target_date in rebalance_dates(close, rebalance_frequency):
        position = close.index.searchsorted(target_date, side="right") - 1
        if position < 0:
            continue
        as_of = pd.Timestamp(close.index[position])
        history = price_frame.loc[price_frame["date"] <= as_of].copy()
        snapshot = snapshot_builder(history, universe)
        weights, signal_description, _is_defensive, status_description, diagnostics = signal_builder(
            snapshot,
            current_holdings,
        )
        normalized_weights = {str(symbol): float(weight) for symbol, weight in weights.items() if float(weight) > 1e-12}
        current_holdings = set(normalized_weights)
        rows.append({"date": as_of, **{symbol: normalized_weights.get(symbol, 0.0) for symbol in close.columns}})
        diagnostics_by_date[as_of.date().isoformat()] = {
            "signal_description": signal_description,
            "status_description": status_description,
            "selected_symbols": list(diagnostics.get("selected_symbols", ())),
            "regime": diagnostics.get("regime"),
            "candidate_count": diagnostics.get("candidate_count"),
        }

    if not rows:
        targets = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    else:
        targets = pd.DataFrame(rows).set_index("date")
        targets = targets.reindex(close.index, method="ffill").fillna(0.0)
        targets = targets.reindex(columns=close.columns, fill_value=0.0)
    shifted_targets = targets.shift(1).fillna(0.0)
    returns = close.pct_change().fillna(0.0)
    turnover = shifted_targets.diff().abs().sum(axis=1).fillna(0.0)
    strategy_returns = (shifted_targets * returns).sum(axis=1) - turnover * float(cost_bps) / 10_000.0
    return {
        "returns": strategy_returns,
        "targets": shifted_targets,
        "close": close,
        "turnover": turnover,
        "diagnostics_by_date": diagnostics_by_date,
    }


def metrics(returns: pd.Series) -> dict[str, float | int]:
    returns = returns.dropna()
    if returns.empty:
        return {
            "days": 0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "annual_volatility": 0.0,
            "total_return": 0.0,
        }
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    drawdown = equity / equity.cummax() - 1.0
    return {
        "days": int(len(returns)),
        "annual_return": float(equity.iloc[-1] ** (1 / years) - 1.0) if years > 0 else 0.0,
        "max_drawdown": float(drawdown.min()),
        "annual_volatility": float(returns.std(ddof=0) * math.sqrt(252)),
        "total_return": float(equity.iloc[-1] - 1.0),
    }


def slice_returns(returns: pd.Series, start: str | None, end: str | None) -> pd.Series:
    output = returns
    if start:
        output = output.loc[pd.Timestamp(start) :]
    if end:
        output = output.loc[: pd.Timestamp(end)]
    return output


def summarize_backtest(
    *,
    backtest: Mapping[str, Any],
    periods: Mapping[str, tuple[str | None, str | None]],
) -> dict[str, Any]:
    returns = backtest["returns"]
    targets = backtest["targets"]
    close = backtest["close"]
    benchmark_returns = {
        "strategy": returns,
        "static_equal_weight": close.pct_change().fillna(0.0).mean(axis=1),
        **{f"{symbol}_buy_hold": close[symbol].pct_change().fillna(0.0) for symbol in close.columns},
    }
    return {
        "data": {
            "start": pd.Timestamp(close.index.min()).date().isoformat(),
            "end": pd.Timestamp(close.index.max()).date().isoformat(),
            "rows": int(len(close)),
            "last_weights": targets.tail(1).to_dict("records")[0] if not targets.empty else {},
            "average_gross_exposure": float(targets.sum(axis=1).mean()) if not targets.empty else 0.0,
            "average_daily_turnover": float(targets.diff().abs().sum(axis=1).mean()) if not targets.empty else 0.0,
        },
        "metrics": {
            name: {period: metrics(slice_returns(series, start, end)) for period, (start, end) in periods.items()}
            for name, series in benchmark_returns.items()
        },
        "diagnostics_by_date": dict(backtest["diagnostics_by_date"]),
    }
