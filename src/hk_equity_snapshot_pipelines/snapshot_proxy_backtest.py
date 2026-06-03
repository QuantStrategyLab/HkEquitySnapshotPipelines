from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import ssl
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .contracts import (
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
    HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
    HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
    HK_INDEX_REBALANCE_EVENT_PROFILE,
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
    HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE,
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
)
from .snapshot_promotion_matrix import FIRST_SNAPSHOT_PROMOTION_SCOPE, RESEARCH_ONLY_SCAFFOLD_SCOPE


PROXY_BACKTEST_VERSION = "hk_snapshot_proxy_cycle_backtest.v1"
PROXY_RESEARCH_STATUS = "research_proxy_not_live_enablement_evidence"
DEFAULT_BENCHMARK_SYMBOL = "2800.HK"
DEFAULT_COST_BPS = 20.0
DEFAULT_TOP_N = 5
DEFAULT_START_DATE = "2016-01-01"
DEFAULT_CACHE_DIR = Path("data/output/research_proxy_price_cache")
DEFAULT_OUTPUT_DIR = Path("data/output/research_snapshot_proxy_backtest")
DEFAULT_SYMBOLS: tuple[str, ...] = (
    "0002.HK",
    "0003.HK",
    "0005.HK",
    "0016.HK",
    "0027.HK",
    "0066.HK",
    "0388.HK",
    "0700.HK",
    "0823.HK",
    "0883.HK",
    "0939.HK",
    "0941.HK",
    "1299.HK",
    "1398.HK",
    "1810.HK",
    "2318.HK",
    "2388.HK",
    "2628.HK",
    "3690.HK",
    "3988.HK",
    "9988.HK",
    "9999.HK",
)


@dataclass(frozen=True)
class ProxyProfile:
    profile: str
    scope: str
    proxy_kind: str
    description: str


PROXY_PROFILES: tuple[ProxyProfile, ...] = (
    ProxyProfile(
        HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE,
        FIRST_SNAPSHOT_PROMOTION_SCOPE,
        "price_proxy_plus_simulated_dividend_quality",
        "Low realized volatility, smaller drawdown, mild momentum, and deterministic simulated dividend-quality factor.",
    ),
    ProxyProfile(
        HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_shareholder_yield",
        "Deferred retest proxy: deterministic simulated shareholder-yield / buyback factor plus FCF-quality proxy and volatility control.",
    ),
    ProxyProfile(
        HK_FREE_CASH_FLOW_QUALITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_fcf_quality",
        "Deferred retest proxy: deterministic simulated FCF-quality factor plus growth, relative momentum, and drawdown control.",
    ),
    ProxyProfile(
        HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_only_residual_momentum_proxy",
        "Benchmark-relative / residual momentum proxy with volatility penalty.",
    ),
    ProxyProfile(
        HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_qvlm_factors",
        "Equal-weight quality, value, low-volatility, and momentum factor proxy.",
    ),
    ProxyProfile(
        HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_quality_growth",
        "Quality-growth and FCF simulated factors with low-volatility and drawdown controls.",
    ),
    ProxyProfile(
        HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_southbound_flow",
        "Deterministic simulated Southbound flow factor plus momentum.",
    ),
    ProxyProfile(
        HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_policy_value",
        "Deterministic simulated policy-value / central-SOE factor plus value-quality controls.",
    ),
    ProxyProfile(
        HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_proxy_plus_simulated_composite_qvm",
        "Composite quality, value, and momentum proxy.",
    ),
    ProxyProfile(
        HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_only_liquid_momentum_proxy",
        "Price momentum proxy with deterministic liquidity preference and volatility penalty.",
    ),
    ProxyProfile(
        HK_BLUE_CHIP_LEADER_ROTATION_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "price_only_blue_chip_leader_proxy",
        "Simple blue-chip momentum leader proxy.",
    ),
    ProxyProfile(
        HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "simulated_valuation_overlay_proxy",
        "Deterministic valuation / A-H premium proxy; no real A-share leg or FX data is used.",
    ),
    ProxyProfile(
        HK_INDEX_REBALANCE_EVENT_PROFILE,
        RESEARCH_ONLY_SCAFFOLD_SCOPE,
        "simulated_event_score_proxy",
        "Deterministic event-score proxy; no official index event timestamps are used.",
    ),
)


def _stable_unit_interval(*parts: str) -> float:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def _stable_score(symbol: str, key: str, as_of: pd.Timestamp) -> float:
    base = _stable_unit_interval(symbol, key) * 2.0 - 1.0
    month = as_of.strftime("%Y-%m")
    drift = (_stable_unit_interval(symbol, key, month) * 2.0 - 1.0) * 0.25
    return base + drift


def _zscore(values: pd.Series) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce")
    std = float(values.std(ddof=0))
    if not math.isfinite(std) or std == 0.0:
        return pd.Series(0.0, index=values.index, dtype=float)
    return ((values - values.mean()) / std).fillna(0.0)


def _period1_period2(start: str, end: str) -> tuple[int, int]:
    start_dt = dt.datetime.fromisoformat(start[:10]).replace(tzinfo=dt.UTC)
    end_dt = dt.datetime.fromisoformat(end[:10]).replace(tzinfo=dt.UTC) + dt.timedelta(days=1)
    return int(start_dt.timestamp()), int(end_dt.timestamp())


def _download_yahoo_symbol(symbol: str, *, start: str, end: str, timeout: float = 20.0) -> pd.DataFrame:
    period1, period2 = _period1_period2(start, end)
    query = urllib.parse.urlencode(
        {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
        }
    )
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 hk-equity-snapshot-research-proxy-backtest",
        },
    )
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, context=context, timeout=timeout) as response:  # noqa: S310 - research-only public market data fetch
        payload = json.loads(response.read().decode("utf-8"))
    result = payload.get("chart", {}).get("result") or []
    if not result:
        raise ValueError(f"Yahoo chart response has no result for {symbol}")
    row = result[0]
    timestamps = row.get("timestamp") or []
    quote = (row.get("indicators", {}).get("quote") or [{}])[0]
    adjclose = (row.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose") or quote.get("close") or []
    frame = pd.DataFrame(
        {
            "date": [pd.Timestamp(ts, unit="s").tz_localize("UTC").tz_convert(None).normalize() for ts in timestamps],
            "symbol": symbol,
            "close": adjclose,
            "volume": quote.get("volume") or [None] * len(timestamps),
        }
    )
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"]).drop_duplicates(subset=["date", "symbol"], keep="last")
    if frame.empty:
        raise ValueError(f"Yahoo chart response has no valid close prices for {symbol}")
    return frame


def download_yahoo_price_history(
    *,
    symbols: tuple[str, ...],
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    start: str = DEFAULT_START_DATE,
    end: str | None = None,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    refresh: bool = False,
    throttle_seconds: float = 0.25,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    end = end or dt.date.today().isoformat()
    cache_dir.mkdir(parents=True, exist_ok=True)
    selected_symbols = tuple(dict.fromkeys((*symbols, benchmark_symbol)))
    frames: list[pd.DataFrame] = []
    failures: dict[str, str] = {}
    for symbol in selected_symbols:
        cache_path = cache_dir / f"{symbol.replace('.', '_')}_{start}_{end}.csv"
        try:
            if cache_path.exists() and not refresh:
                frame = pd.read_csv(cache_path, parse_dates=["date"])
            else:
                frame = _download_yahoo_symbol(symbol, start=start, end=end)
                frame.to_csv(cache_path, index=False)
                time.sleep(max(0.0, float(throttle_seconds)))
            frames.append(frame)
        except Exception as exc:  # pragma: no cover - live network errors vary
            failures[symbol] = str(exc)
    if not frames:
        raise ValueError("No Yahoo price history could be downloaded or loaded from cache")
    prices = pd.concat(frames, ignore_index=True)
    meta = {
        "price_source": "yahoo_chart_public_api",
        "start": start,
        "end": end,
        "symbols_requested": list(selected_symbols),
        "symbols_loaded": sorted(prices["symbol"].unique().tolist()),
        "download_failures": failures,
        "cache_dir": str(cache_dir),
        "ssl_verification": "disabled_due_local_ca_issue_research_only",
    }
    return prices, meta


def generate_synthetic_price_history(
    *,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    start: str = DEFAULT_START_DATE,
    end: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    end = end or dt.date.today().isoformat()
    dates = pd.bdate_range(start=start, end=end)
    rows: list[dict[str, Any]] = []
    all_symbols = tuple(dict.fromkeys((*symbols, benchmark_symbol)))
    for symbol in all_symbols:
        price = 100.0 + _stable_unit_interval(symbol, "base") * 50.0
        drift = (_stable_unit_interval(symbol, "drift") - 0.45) / 252.0
        vol = 0.010 + _stable_unit_interval(symbol, "vol") * 0.018
        for i, date in enumerate(dates):
            shock = math.sin(i * 0.071 + _stable_unit_interval(symbol, "phase") * 10.0) * vol
            cycle = math.sin(i * 0.009 + _stable_unit_interval(symbol, "cycle") * 10.0) * vol * 0.55
            price = max(0.5, price * (1.0 + drift + shock + cycle))
            rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "close": price,
                    "volume": 1_000_000 + int(_stable_unit_interval(symbol, "volume") * 20_000_000),
                }
            )
    return pd.DataFrame(rows), {
        "price_source": "deterministic_synthetic_price_history",
        "start": start,
        "end": end,
        "symbols_requested": list(all_symbols),
        "symbols_loaded": list(all_symbols),
        "download_failures": {},
    }


def _close_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    frame = prices.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None).dt.normalize()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    close = frame.dropna(subset=["date", "symbol", "close"]).pivot_table(
        index="date",
        columns="symbol",
        values="close",
        aggfunc="last",
    )
    close = close.sort_index().ffill().dropna(how="all")
    if close.empty:
        raise ValueError("prices must contain at least one valid close series")
    return close


def _window_return(history: pd.Series, lag: int, skip: int = 0) -> float:
    clean = history.dropna()
    if len(clean) <= lag + skip:
        return 0.0
    end = clean.iloc[-1 - skip] if skip else clean.iloc[-1]
    start = clean.iloc[-1 - skip - lag]
    if start == 0 or pd.isna(start) or pd.isna(end):
        return 0.0
    return float(end / start - 1.0)


def _max_drawdown(history: pd.Series, lookback: int) -> float:
    clean = history.dropna().tail(lookback)
    if clean.empty:
        return 0.0
    dd = clean / clean.cummax() - 1.0
    return float(dd.min())


def _feature_frame(close: pd.DataFrame, as_of: pd.Timestamp, benchmark_symbol: str) -> pd.DataFrame:
    history = close.loc[:as_of]
    benchmark_history = history[benchmark_symbol] if benchmark_symbol in history.columns else history.mean(axis=1)
    benchmark_mom = _window_return(benchmark_history, 252, skip=21)
    rows: list[dict[str, Any]] = []
    for symbol in [column for column in history.columns if column != benchmark_symbol]:
        series = history[symbol].dropna()
        if len(series) < 126:
            continue
        daily_returns = series.pct_change().dropna().tail(126)
        vol_126 = float(daily_returns.std(ddof=0) * math.sqrt(252)) if not daily_returns.empty else 0.0
        mom_12_1 = _window_return(series, 252, skip=21)
        mom_6m = _window_return(series, 126)
        mom_3m = _window_return(series, 63)
        drawdown = _max_drawdown(series, 252)
        rows.append(
            {
                "symbol": symbol,
                "mom_12_1": mom_12_1,
                "mom_6m": mom_6m,
                "mom_3m": mom_3m,
                "relative_momentum": mom_12_1 - benchmark_mom,
                "vol_126": vol_126,
                "drawdown_252": drawdown,
                "dividend_quality": _stable_score(symbol, "dividend_quality", as_of),
                "shareholder_yield": _stable_score(symbol, "shareholder_yield", as_of),
                "fcf_quality": _stable_score(symbol, "fcf_quality", as_of),
                "growth_quality": _stable_score(symbol, "growth_quality", as_of),
                "value_quality": _stable_score(symbol, "value_quality", as_of),
                "policy_value": _stable_score(symbol, "policy_value", as_of),
                "southbound_flow": _stable_score(symbol, "southbound_flow", as_of),
                "event_score": _stable_score(symbol, "event_score", as_of),
                "liquidity": _stable_score(symbol, "liquidity", as_of),
            }
        )
    frame = pd.DataFrame(rows).set_index("symbol") if rows else pd.DataFrame()
    if frame.empty:
        return frame
    for column in frame.columns:
        frame[f"z_{column}"] = _zscore(frame[column])
    frame["z_low_vol"] = _zscore(-frame["vol_126"])
    frame["z_drawdown_control"] = _zscore(frame["drawdown_252"])
    return frame


def _profile_score(profile: str, features: pd.DataFrame) -> pd.Series:
    if profile == HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE:
        return (
            0.50 * features["z_dividend_quality"]
            + 0.30 * features["z_low_vol"]
            + 0.20 * features["z_drawdown_control"]
            + 0.10 * features["z_mom_6m"]
        )
    if profile == HK_SHAREHOLDER_YIELD_QUALITY_PROFILE:
        return (
            0.55 * features["z_shareholder_yield"]
            + 0.25 * features["z_fcf_quality"]
            + 0.10 * features["z_mom_6m"]
            + 0.10 * features["z_low_vol"]
        )
    if profile == HK_FREE_CASH_FLOW_QUALITY_PROFILE:
        return (
            0.60 * features["z_fcf_quality"]
            + 0.20 * features["z_growth_quality"]
            + 0.10 * features["z_drawdown_control"]
            + 0.10 * features["z_relative_momentum"]
        )
    if profile == HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE:
        return 0.70 * features["z_relative_momentum"] + 0.30 * features["z_mom_12_1"] + 0.15 * features["z_low_vol"]
    if profile == HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE:
        return (
            0.25 * features["z_fcf_quality"]
            + 0.25 * features["z_value_quality"]
            + 0.25 * features["z_low_vol"]
            + 0.25 * features["z_mom_12_1"]
        )
    if profile == HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE:
        return (
            0.40 * features["z_growth_quality"]
            + 0.25 * features["z_low_vol"]
            + 0.15 * features["z_fcf_quality"]
            + 0.10 * features["z_mom_6m"]
            + 0.10 * features["z_drawdown_control"]
        )
    if profile == HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE:
        return 0.55 * features["z_southbound_flow"] + 0.35 * features["z_mom_6m"] + 0.10 * features["z_liquidity"]
    if profile == HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE:
        return 0.55 * features["z_policy_value"] + 0.25 * features["z_value_quality"] + 0.20 * features["z_fcf_quality"]
    if profile == HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE:
        return 0.35 * features["z_fcf_quality"] + 0.35 * features["z_value_quality"] + 0.30 * features["z_mom_12_1"]
    if profile == HK_LIQUID_MOMENTUM_QUALITY_PROFILE:
        return 0.50 * features["z_mom_6m"] + 0.30 * features["z_mom_12_1"] + 0.20 * features["z_liquidity"] + 0.10 * features["z_low_vol"]
    if profile == HK_BLUE_CHIP_LEADER_ROTATION_PROFILE:
        return 0.75 * features["z_mom_6m"] + 0.15 * features["z_mom_3m"] + 0.10 * features["z_low_vol"]
    if profile == HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE:
        return 0.75 * features["z_value_quality"] + 0.25 * features["z_drawdown_control"]
    if profile == HK_INDEX_REBALANCE_EVENT_PROFILE:
        return 0.80 * features["z_event_score"] + 0.20 * features["z_liquidity"]
    raise ValueError(f"Unsupported proxy profile {profile!r}")


def _rebalance_dates(close: pd.DataFrame, frequency: str) -> pd.DatetimeIndex:
    if frequency == "monthly":
        return close.resample("ME").last().index
    if frequency == "weekly":
        return close.resample("W-FRI").last().index
    raise ValueError("rebalance frequency must be monthly or weekly")


def run_profile_proxy_backtest(
    close: pd.DataFrame,
    *,
    profile: str,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    rebalance_frequency: str = "monthly",
    top_n: int = DEFAULT_TOP_N,
    cost_bps: float = DEFAULT_COST_BPS,
    feature_cache: dict[pd.Timestamp, pd.DataFrame] | None = None,
) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}
    for target_date in _rebalance_dates(close, rebalance_frequency):
        position = close.index.searchsorted(target_date, side="right") - 1
        if position < 0:
            continue
        as_of = pd.Timestamp(close.index[position])
        features = feature_cache.get(as_of) if feature_cache is not None else None
        if features is None:
            features = _feature_frame(close, as_of, benchmark_symbol)
        if features.empty:
            continue
        scores = _profile_score(profile, features).dropna().sort_values(ascending=False)
        selected = scores.head(max(1, int(top_n))).index.tolist()
        weight = 1.0 / len(selected)
        targets.append({"date": as_of, **{symbol: weight for symbol in selected}})
        diagnostics[as_of.date().isoformat()] = {
            "selected_symbols": selected,
            "top_score": float(scores.iloc[0]) if not scores.empty else None,
            "candidate_count": int(len(scores)),
        }
    if not targets:
        weights = pd.DataFrame(0.0, index=close.index, columns=[c for c in close.columns if c != benchmark_symbol])
    else:
        weights = pd.DataFrame(targets).set_index("date").reindex(close.index, method="ffill").fillna(0.0)
        weights = weights.reindex(columns=[c for c in close.columns if c != benchmark_symbol], fill_value=0.0)
    shifted_weights = weights.shift(1).fillna(0.0)
    returns = close.pct_change().fillna(0.0)
    turnover = shifted_weights.diff().abs().sum(axis=1).fillna(0.0)
    strategy_returns = (shifted_weights * returns.reindex(columns=shifted_weights.columns).fillna(0.0)).sum(axis=1)
    strategy_returns = strategy_returns - turnover * float(cost_bps) / 10_000.0
    return {
        "returns": strategy_returns,
        "weights": shifted_weights,
        "turnover": turnover,
        "diagnostics_by_date": diagnostics,
    }


def _metrics(returns: pd.Series) -> dict[str, float | int]:
    returns = returns.dropna()
    if returns.empty:
        return {
            "days": 0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "annual_volatility": 0.0,
            "total_return": 0.0,
            "annual_return_to_max_drawdown_ratio": 0.0,
        }
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    drawdown = equity / equity.cummax() - 1.0
    annual_return = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else 0.0
    max_drawdown = float(drawdown.min())
    return {
        "days": int(len(returns)),
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "annual_volatility": float(returns.std(ddof=0) * math.sqrt(252)),
        "total_return": float(equity.iloc[-1] - 1.0),
        "annual_return_to_max_drawdown_ratio": float(annual_return / abs(max_drawdown)) if max_drawdown else 0.0,
    }


def _cycle_periods(index: pd.DatetimeIndex) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    end = pd.Timestamp(index.max())
    periods = {
        "long": (pd.Timestamp(index.min()), end),
        "medium": (end - pd.Timedelta(days=365 * 3), end),
        "short": (end - pd.Timedelta(days=365), end),
    }
    return {
        name: (max(start, pd.Timestamp(index.min())), end)
        for name, (start, end) in periods.items()
    }


def _slice(series: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    return series.loc[start:end]


def _rank_score(metrics_by_period: dict[str, dict[str, float | int]]) -> float:
    score = 0.0
    weights = {"long": 0.50, "medium": 0.30, "short": 0.20}
    for period, weight in weights.items():
        metrics = metrics_by_period[period]
        annual_return = float(metrics["annual_return"])
        max_drawdown = abs(float(metrics["max_drawdown"]))
        volatility = float(metrics["annual_volatility"])
        drawdown_penalty = max(0.0, max_drawdown - 0.30) * 2.0
        score += weight * (annual_return - 0.35 * max_drawdown - 0.15 * volatility - drawdown_penalty)
    return score


def build_proxy_cycle_backtest(
    *,
    prices: pd.DataFrame,
    price_meta: dict[str, Any],
    profiles: tuple[ProxyProfile, ...] = PROXY_PROFILES,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    rebalance_frequency: str = "monthly",
    top_n: int = DEFAULT_TOP_N,
    cost_bps: float = DEFAULT_COST_BPS,
) -> dict[str, Any]:
    close = _close_matrix(prices)
    close = close.loc[:, close.notna().sum(axis=0) >= 126]
    periods = _cycle_periods(close.index)
    benchmark_returns = (
        close[benchmark_symbol].pct_change().fillna(0.0)
        if benchmark_symbol in close.columns
        else close.pct_change().fillna(0.0).mean(axis=1)
    )
    feature_cache: dict[pd.Timestamp, pd.DataFrame] = {}
    for target_date in _rebalance_dates(close, rebalance_frequency):
        position = close.index.searchsorted(target_date, side="right") - 1
        if position >= 0:
            as_of = pd.Timestamp(close.index[position])
            feature_cache[as_of] = _feature_frame(close, as_of, benchmark_symbol)
    profile_rows: list[dict[str, Any]] = []
    for proxy_profile in profiles:
        backtest = run_profile_proxy_backtest(
            close,
            profile=proxy_profile.profile,
            benchmark_symbol=benchmark_symbol,
            rebalance_frequency=rebalance_frequency,
            top_n=top_n,
            cost_bps=cost_bps,
            feature_cache=feature_cache,
        )
        returns = backtest["returns"]
        metrics_by_period = {
            name: _metrics(_slice(returns, start, end))
            for name, (start, end) in periods.items()
        }
        benchmark_by_period = {
            name: _metrics(_slice(benchmark_returns, start, end))
            for name, (start, end) in periods.items()
        }
        pass_30 = {name: abs(float(metrics["max_drawdown"])) <= 0.30 for name, metrics in metrics_by_period.items()}
        profile_rows.append(
            {
                "profile": proxy_profile.profile,
                "promotion_scope": proxy_profile.scope,
                "proxy_kind": proxy_profile.proxy_kind,
                "description": proxy_profile.description,
                "metrics": metrics_by_period,
                "benchmark_metrics": benchmark_by_period,
                "drawdown_30_pass_by_period": pass_30,
                "passes_all_cycle_drawdown_gate": all(pass_30.values()),
                "average_daily_turnover": float(backtest["turnover"].mean()),
                "last_weights": backtest["weights"].tail(1).to_dict("records")[0] if not backtest["weights"].empty else {},
                "rank_score": _rank_score(metrics_by_period),
            }
        )
    ranking = sorted(profile_rows, key=lambda item: float(item["rank_score"]), reverse=True)
    for index, row in enumerate(ranking, start=1):
        row["proxy_rank"] = index
        row["research_recommendation"] = (
            "keep_first_wave_candidate"
            if row["promotion_scope"] == FIRST_SNAPSHOT_PROMOTION_SCOPE and row["passes_all_cycle_drawdown_gate"]
            else "research_only_or_reject_pending_real_factor_history"
        )
    return {
        "backtest_version": PROXY_BACKTEST_VERSION,
        "research_status": PROXY_RESEARCH_STATUS,
        "data_boundary": (
            "Price history can be real Yahoo chart data or deterministic synthetic fallback. Fundamental, buyback, "
            "FCF, Southbound-flow, policy, valuation, and event fields are deterministic simulations where real "
            "point-in-time histories are unavailable. Results are for research triage only and are not live-enable evidence."
        ),
        "config": {
            "benchmark_symbol": benchmark_symbol,
            "rebalance_frequency": rebalance_frequency,
            "top_n": int(top_n),
            "cost_bps": float(cost_bps),
            "max_drawdown_gate": 0.30,
        },
        "price_meta": price_meta,
        "data": {
            "start": pd.Timestamp(close.index.min()).date().isoformat(),
            "end": pd.Timestamp(close.index.max()).date().isoformat(),
            "trading_days": int(len(close)),
            "symbols": list(close.columns),
        },
        "periods": {
            name: {"start": start.date().isoformat(), "end": end.date().isoformat()}
            for name, (start, end) in periods.items()
        },
        "profiles": profile_rows,
        "ranking": ranking,
    }


def run_proxy_cycle_backtest(
    *,
    start: str = DEFAULT_START_DATE,
    end: str | None = None,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    price_source: str = "yahoo",
    cache_dir: Path = DEFAULT_CACHE_DIR,
    allow_synthetic_fallback: bool = True,
    refresh: bool = False,
    rebalance_frequency: str = "monthly",
    top_n: int = DEFAULT_TOP_N,
    cost_bps: float = DEFAULT_COST_BPS,
) -> dict[str, Any]:
    if price_source not in {"yahoo", "synthetic"}:
        raise ValueError("price_source must be yahoo or synthetic")
    price_meta: dict[str, Any]
    if price_source == "synthetic":
        prices, price_meta = generate_synthetic_price_history(symbols=symbols, benchmark_symbol=benchmark_symbol, start=start, end=end)
    else:
        try:
            prices, price_meta = download_yahoo_price_history(
                symbols=symbols,
                benchmark_symbol=benchmark_symbol,
                start=start,
                end=end,
                cache_dir=cache_dir,
                refresh=refresh,
            )
        except Exception as exc:
            if not allow_synthetic_fallback:
                raise
            prices, price_meta = generate_synthetic_price_history(
                symbols=symbols,
                benchmark_symbol=benchmark_symbol,
                start=start,
                end=end,
            )
            price_meta["fallback_reason"] = str(exc)
    return build_proxy_cycle_backtest(
        prices=prices,
        price_meta=price_meta,
        benchmark_symbol=benchmark_symbol,
        rebalance_frequency=rebalance_frequency,
        top_n=top_n,
        cost_bps=cost_bps,
    )


def _write_outputs(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "snapshot_proxy_cycle_backtest.json"
    markdown_path = output_dir / "snapshot_proxy_cycle_backtest.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# HK Snapshot Proxy Cycle Backtest",
        "",
        f"- Version: `{payload['backtest_version']}`",
        f"- Research status: `{payload['research_status']}`",
        f"- Data source: `{payload['price_meta']['price_source']}`",
        f"- Window: `{payload['data']['start']}` to `{payload['data']['end']}`",
        f"- Symbols: `{len(payload['data']['symbols'])}`",
        "",
        "> This is research triage only. Simulated factor fields are not live-enable evidence.",
        "",
        "| Rank | Profile | Scope | Long ann. return | Long max DD | Medium ann. return | Medium max DD | Short ann. return | Short max DD | DD gate |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["ranking"]:
        metrics = row["metrics"]
        gate = "PASS" if row["passes_all_cycle_drawdown_gate"] else "FAIL"
        lines.append(
            "| {rank} | `{profile}` | {scope} | {long_ret:.2%} | {long_dd:.2%} | {mid_ret:.2%} | {mid_dd:.2%} | {short_ret:.2%} | {short_dd:.2%} | {gate} |".format(
                rank=row["proxy_rank"],
                profile=row["profile"],
                scope=row["promotion_scope"],
                long_ret=float(metrics["long"]["annual_return"]),
                long_dd=float(metrics["long"]["max_drawdown"]),
                mid_ret=float(metrics["medium"]["annual_return"]),
                mid_dd=float(metrics["medium"]["max_drawdown"]),
                short_ret=float(metrics["short"]["annual_return"]),
                short_dd=float(metrics["short"]["max_drawdown"]),
                gate=gate,
            )
        )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json_path": str(json_path), "markdown_path": str(markdown_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run research-only HK snapshot proxy cycle backtests.")
    parser.add_argument("--start", default=DEFAULT_START_DATE)
    parser.add_argument("--end")
    parser.add_argument("--price-source", choices=("yahoo", "synthetic"), default="yahoo")
    parser.add_argument("--benchmark-symbol", default=DEFAULT_BENCHMARK_SYMBOL)
    parser.add_argument("--symbol", action="append", help="HK Yahoo symbol to include; may be repeated")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--no-synthetic-fallback", action="store_true")
    parser.add_argument("--rebalance-frequency", choices=("monthly", "weekly"), default="monthly")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS)
    parser.add_argument("--json", action="store_true", help="Print JSON only and do not write output files")
    args = parser.parse_args(argv)
    payload = run_proxy_cycle_backtest(
        start=args.start,
        end=args.end,
        symbols=tuple(args.symbol or DEFAULT_SYMBOLS),
        benchmark_symbol=args.benchmark_symbol,
        price_source=args.price_source,
        cache_dir=args.cache_dir,
        allow_synthetic_fallback=not args.no_synthetic_fallback,
        refresh=args.refresh,
        rebalance_frequency=args.rebalance_frequency,
        top_n=args.top_n,
        cost_bps=args.cost_bps,
    )
    if not args.json:
        payload = {**payload, "output_paths": _write_outputs(args.output_dir, payload)}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_SYMBOLS",
    "PROXY_BACKTEST_VERSION",
    "PROXY_PROFILES",
    "PROXY_RESEARCH_STATUS",
    "build_proxy_cycle_backtest",
    "download_yahoo_price_history",
    "generate_synthetic_price_history",
    "main",
    "run_profile_proxy_backtest",
    "run_proxy_cycle_backtest",
]
