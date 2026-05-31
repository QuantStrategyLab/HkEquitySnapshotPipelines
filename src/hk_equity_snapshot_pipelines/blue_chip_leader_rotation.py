from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from hk_equity_strategies.strategies.blue_chip_leader_rotation import (
    REQUIRED_FEATURE_COLUMNS,
    compute_signals,
    normalize_symbol,
    score_candidates,
)

from .artifacts import write_release_status_summary, write_snapshot_manifest
from .contracts import HK_BLUE_CHIP_LEADER_ROTATION_PROFILE, get_profile_contract

BENCHMARK_SYMBOL = "02800"
DEFAULT_LOOKBACK_DAYS = 260


@dataclass(frozen=True)
class SnapshotBuildResult:
    snapshot: pd.DataFrame
    ranking: pd.DataFrame
    artifact_paths: dict[str, Path]
    signal_description: str
    status_description: str
    diagnostics: dict[str, Any]


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(path))


def _normalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "symbol", "close"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices CSV missing required columns: {', '.join(sorted(missing))}")
    frame = prices.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None).dt.normalize()
    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    if "volume" in frame.columns:
        frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    else:
        frame["volume"] = 0.0
    if "turnover_hkd" in frame.columns:
        frame["turnover_hkd"] = pd.to_numeric(frame["turnover_hkd"], errors="coerce")
    else:
        frame["turnover_hkd"] = frame["close"] * frame["volume"]
    frame = frame.dropna(subset=["date", "symbol", "close"]).sort_values(["symbol", "date"])
    if frame.empty:
        raise ValueError("prices CSV did not contain any valid rows")
    return frame


def _normalize_universe(universe: pd.DataFrame | None, symbols: set[str]) -> pd.DataFrame:
    if universe is None or universe.empty:
        return pd.DataFrame(
            {
                "symbol": sorted(symbols),
                "sector": "unknown",
                "eligible": True,
            }
        )
    frame = universe.copy()
    if "symbol" not in frame.columns:
        raise ValueError("universe CSV missing required column: symbol")
    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    if "sector" not in frame.columns:
        frame["sector"] = "unknown"
    if "eligible" not in frame.columns:
        frame["eligible"] = True
    for column in ("market_cap_hkd", "lot_size"):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.drop_duplicates(subset=["symbol"], keep="last")


def _return(series: pd.Series, periods: int) -> float | None:
    if len(series) <= periods:
        return None
    current = float(series.iloc[-1])
    previous = float(series.iloc[-periods - 1])
    if previous == 0:
        return None
    return current / previous - 1.0


def _max_drawdown(series: pd.Series) -> float | None:
    if series.empty:
        return None
    running_max = series.cummax()
    drawdown = series / running_max - 1.0
    return float(drawdown.min())


def build_feature_snapshot(
    prices: pd.DataFrame,
    universe: pd.DataFrame | None = None,
    *,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> pd.DataFrame:
    price_frame = _normalize_prices(prices)
    benchmark_symbol = normalize_symbol(benchmark_symbol)
    symbols = set(price_frame["symbol"].dropna().astype(str))
    universe_frame = _normalize_universe(universe, symbols)
    latest_date = price_frame["date"].max()
    start_date = latest_date - pd.Timedelta(days=max(int(lookback_days) * 2, 365))
    price_frame = price_frame.loc[price_frame["date"] >= start_date].copy()

    benchmark_series = (
        price_frame.loc[price_frame["symbol"] == benchmark_symbol]
        .sort_values("date")
        .set_index("date")["close"]
    )
    benchmark_6m = _return(benchmark_series, 126) or 0.0

    rows: list[dict[str, Any]] = []
    for symbol, group in price_frame.groupby("symbol"):
        sorted_group = group.sort_values("date")
        close = sorted_group["close"].astype(float).reset_index(drop=True)
        turnover = sorted_group["turnover_hkd"].astype(float).reset_index(drop=True)
        if close.empty:
            continue
        latest = sorted_group.iloc[-1]
        recent_252 = close.tail(252)
        recent_63 = close.tail(63)
        row = {
            "as_of": pd.Timestamp(latest_date).date().isoformat(),
            "snapshot_date": pd.Timestamp(latest_date).date().isoformat(),
            "symbol": symbol,
            "close_hkd": float(close.iloc[-1]),
            "adv20_hkd": float(turnover.tail(20).mean()) if len(turnover) else 0.0,
            "history_days": int(len(close)),
            "mom_3m": _return(close, 63),
            "mom_6m": _return(close, 126),
            "mom_12_1": _return(close, 252),
            "rel_mom_6m_vs_benchmark": (_return(close, 126) or 0.0) - benchmark_6m,
            "high_252_gap": float(close.iloc[-1] / recent_252.max() - 1.0) if not recent_252.empty else None,
            "sma200_gap": float(close.iloc[-1] / close.tail(200).mean() - 1.0) if len(close) >= 200 else None,
            "vol_63": float(recent_63.pct_change().dropna().std()) if len(recent_63) >= 20 else None,
            "maxdd_126": _max_drawdown(close.tail(126)),
        }
        rows.append(row)

    snapshot = pd.DataFrame(rows)
    if snapshot.empty:
        raise ValueError("No snapshot rows could be built from the provided prices")
    snapshot = snapshot.merge(universe_frame, on="symbol", how="left")
    snapshot["sector"] = snapshot["sector"].fillna("unknown")
    snapshot["eligible"] = snapshot["eligible"].fillna(True)
    for column in sorted(REQUIRED_FEATURE_COLUMNS - set(snapshot.columns)):
        snapshot[column] = pd.NA
    preferred = [
        "as_of",
        "snapshot_date",
        "symbol",
        "sector",
        "eligible",
        "close_hkd",
        "adv20_hkd",
        "history_days",
        "mom_3m",
        "mom_6m",
        "mom_12_1",
        "rel_mom_6m_vs_benchmark",
        "high_252_gap",
        "sma200_gap",
        "vol_63",
        "maxdd_126",
        "market_cap_hkd",
        "lot_size",
    ]
    return snapshot.loc[:, [column for column in preferred if column in snapshot.columns]].sort_values("symbol")


def build_and_write_snapshot(
    *,
    prices_path: str | Path,
    output_dir: str | Path,
    universe_path: str | Path | None = None,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
) -> SnapshotBuildResult:
    contract = get_profile_contract(HK_BLUE_CHIP_LEADER_ROTATION_PROFILE)
    artifact_paths = contract.artifact_paths(output_dir)
    prices = _read_csv(prices_path)
    universe = _read_csv(universe_path) if universe_path else None
    snapshot = build_feature_snapshot(prices, universe, benchmark_symbol=benchmark_symbol)
    ranking = score_candidates(snapshot, min_adv20_hkd=0.0)

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
        run_as_of=None,
        min_adv20_hkd=0.0,
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
    args = parser.parse_args(argv)

    result = build_and_write_snapshot(
        prices_path=args.prices,
        universe_path=args.universe,
        output_dir=args.output_dir,
        benchmark_symbol=args.benchmark_symbol,
    )
    print(f"snapshot={result.artifact_paths['snapshot']}")
    print(f"manifest={result.artifact_paths['manifest']}")
    print(f"ranking={result.artifact_paths['ranking']}")
    print(f"release_summary={result.artifact_paths['release_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
