from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

HK_EQUITY_DOMAIN = "hk_equity"
SIGNAL_SOURCE = "feature_snapshot"
STATUS_ICON = "🇭🇰"
PROFILE_NAME = "hk_liquid_momentum_quality"
BENCHMARK_SYMBOL = "02800"
SAFE_HAVEN = "02800"
DEFAULT_HOLDINGS_COUNT = 8
DEFAULT_SINGLE_NAME_CAP = 0.12
DEFAULT_SECTOR_CAP = 0.30
DEFAULT_MIN_ADV20_HKD = 50_000_000.0
DEFAULT_MIN_MARKET_CAP_HKD = 10_000_000_000.0
DEFAULT_MIN_HISTORY_DAYS = 252
DEFAULT_MAX_VOL_63 = 0.08
DEFAULT_MAX_DRAWDOWN_126 = -0.40
DEFAULT_HOLD_BUFFER = 2
DEFAULT_HOLD_BONUS = 0.05
DEFAULT_RISK_ON_EXPOSURE = 1.0
DEFAULT_SOFT_DEFENSE_EXPOSURE = 0.50
DEFAULT_HARD_DEFENSE_EXPOSURE = 0.00
DEFAULT_SOFT_BREADTH_THRESHOLD = 0.45
DEFAULT_HARD_BREADTH_THRESHOLD = 0.30
DEFAULT_EXECUTION_CASH_RESERVE_RATIO = 0.02
SNAPSHOT_CONTRACT_VERSION = "hk_liquid_momentum_quality.feature_snapshot.v1"
REQUIRE_SNAPSHOT_MANIFEST = True

REQUIRED_FEATURE_COLUMNS = frozenset(
    {
        "symbol",
        "sector",
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
    }
)
OPTIONAL_FEATURE_COLUMNS = frozenset(
    {
        "as_of",
        "snapshot_date",
        "eligible",
        "high_63_gap",
        "market_cap_hkd",
        "lot_size",
        "suspension_days_63",
        "corporate_action_flag",
    }
)


def _coerce_bool(value: Any) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return bool(normalized)


def normalize_symbol(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    text = text.removesuffix(".HK")
    if text.isdigit():
        return text.zfill(5)
    return text


def _normalize_holdings(current_holdings: Any) -> set[str]:
    if current_holdings is None:
        return set()
    raw_symbols = current_holdings.keys() if isinstance(current_holdings, Mapping) else current_holdings
    normalized: set[str] = set()
    for item in raw_symbols:
        symbol = getattr(item, "symbol", item)
        symbol_text = normalize_symbol(symbol)
        if symbol_text:
            normalized.add(symbol_text)
    return normalized


def _to_frame(feature_snapshot: Any) -> pd.DataFrame:
    frame = feature_snapshot.copy() if isinstance(feature_snapshot, pd.DataFrame) else pd.DataFrame(list(feature_snapshot))
    if frame.empty:
        raise ValueError("feature_snapshot must contain at least one row")

    missing = REQUIRED_FEATURE_COLUMNS - set(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"feature_snapshot missing required columns: {missing_text}")

    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame["sector"] = frame["sector"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    if "as_of" in frame.columns:
        frame["as_of"] = pd.to_datetime(frame["as_of"], utc=False).dt.tz_localize(None).dt.normalize()
    if "snapshot_date" in frame.columns:
        frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"], utc=False).dt.tz_localize(None).dt.normalize()
    if "eligible" not in frame.columns:
        frame["eligible"] = True
    frame["eligible"] = frame["eligible"].map(_coerce_bool)
    if "corporate_action_flag" in frame.columns:
        frame["corporate_action_flag"] = frame["corporate_action_flag"].map(_coerce_bool)
    else:
        frame["corporate_action_flag"] = False
    if "suspension_days_63" not in frame.columns:
        frame["suspension_days_63"] = 0

    numeric_columns = (REQUIRED_FEATURE_COLUMNS | OPTIONAL_FEATURE_COLUMNS) - {
        "symbol",
        "sector",
        "as_of",
        "snapshot_date",
        "eligible",
        "corporate_action_flag",
    }
    for column in sorted(numeric_columns & set(frame.columns)):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "market_cap_hkd" not in frame.columns:
        frame["market_cap_hkd"] = pd.NA
    return frame


def _zscore(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    std = float(numeric.std(ddof=0))
    if pd.isna(std) or std == 0:
        return pd.Series(0.0, index=values.index, dtype=float)
    return ((numeric - numeric.mean()) / std).fillna(0.0)


def _candidate_frame(
    frame: pd.DataFrame,
    *,
    benchmark_symbol: str,
    safe_haven: str,
    min_adv20_hkd: float,
    min_market_cap_hkd: float,
    min_history_days: int,
    max_vol_63: float,
    max_drawdown_126: float,
) -> pd.DataFrame:
    excluded = {normalize_symbol(benchmark_symbol), normalize_symbol(safe_haven)}
    required_numeric = [
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
    ]
    candidates = frame.loc[
        ~frame["symbol"].isin(excluded)
        & frame["eligible"]
        & ~frame["corporate_action_flag"]
        & frame["adv20_hkd"].ge(float(min_adv20_hkd))
        & frame["history_days"].ge(int(min_history_days))
        & frame["mom_6m"].gt(0.0)
        & frame["mom_12_1"].gt(0.0)
        & frame["sma200_gap"].gt(0.0)
        & frame["vol_63"].le(float(max_vol_63))
        & frame["maxdd_126"].ge(float(max_drawdown_126))
        & frame["suspension_days_63"].le(0)
        & frame[required_numeric].notna().all(axis=1)
    ].copy()
    if candidates.empty or candidates["market_cap_hkd"].isna().all():
        return candidates
    return candidates.loc[
        candidates["market_cap_hkd"].isna() | candidates["market_cap_hkd"].ge(float(min_market_cap_hkd))
    ].copy()


def score_candidates(
    feature_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    safe_haven: str = SAFE_HAVEN,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_history_days: int = DEFAULT_MIN_HISTORY_DAYS,
    max_vol_63: float = DEFAULT_MAX_VOL_63,
    max_drawdown_126: float = DEFAULT_MAX_DRAWDOWN_126,
    hold_bonus: float = DEFAULT_HOLD_BONUS,
) -> pd.DataFrame:
    frame = _to_frame(feature_snapshot)
    eligible = _candidate_frame(
        frame,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_history_days=int(min_history_days),
        max_vol_63=float(max_vol_63),
        max_drawdown_126=float(max_drawdown_126),
    )
    if eligible.empty:
        return pd.DataFrame(columns=["rank", "symbol", "sector", "score", "eligible"])

    safe_vol = eligible["vol_63"].replace(0.0, pd.NA)
    eligible["risk_adjusted_mom_6m"] = (eligible["mom_6m"] / safe_vol).astype(float)
    eligible["risk_adjusted_mom_12_1"] = (eligible["mom_12_1"] / safe_vol).astype(float)
    eligible["drawdown_abs"] = eligible["maxdd_126"].abs()
    high_63_gap = eligible["high_63_gap"] if "high_63_gap" in eligible.columns else eligible["high_252_gap"]
    eligible["cth_combo_score"] = (_zscore(high_63_gap) + _zscore(eligible["high_252_gap"])) * 0.5
    eligible["score"] = (
        _zscore(eligible["risk_adjusted_mom_6m"]) * 0.25
        + _zscore(eligible["risk_adjusted_mom_12_1"]) * 0.20
        + _zscore(eligible["rel_mom_6m_vs_benchmark"]) * 0.20
        + eligible["cth_combo_score"] * 0.15
        + _zscore(eligible["sma200_gap"]) * 0.10
        - _zscore(eligible["vol_63"]) * 0.05
        - _zscore(eligible["drawdown_abs"]) * 0.05
    )
    current_holdings_set = _normalize_holdings(current_holdings)
    if current_holdings_set:
        eligible.loc[eligible["symbol"].isin(current_holdings_set), "score"] += float(hold_bonus)
    ranked = eligible.sort_values(
        by=["score", "risk_adjusted_mom_6m", "adv20_hkd", "symbol"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    output_columns = [
        "rank",
        "symbol",
        "sector",
        "score",
        "eligible",
        "close_hkd",
        "adv20_hkd",
        "market_cap_hkd",
        "history_days",
        "mom_3m",
        "mom_6m",
        "mom_12_1",
        "rel_mom_6m_vs_benchmark",
        "risk_adjusted_mom_6m",
        "risk_adjusted_mom_12_1",
        "high_63_gap",
        "high_252_gap",
        "cth_combo_score",
        "sma200_gap",
        "vol_63",
        "maxdd_126",
        "suspension_days_63",
        "lot_size",
    ]
    return ranked.loc[:, [column for column in output_columns if column in ranked.columns]]


def _resolve_stock_exposure(
    frame: pd.DataFrame,
    *,
    benchmark_symbol: str,
    safe_haven: str,
    min_adv20_hkd: float,
    min_market_cap_hkd: float,
    min_history_days: int,
    max_vol_63: float,
    max_drawdown_126: float,
    risk_on_exposure: float,
    soft_defense_exposure: float,
    hard_defense_exposure: float,
    soft_breadth_threshold: float,
    hard_breadth_threshold: float,
) -> tuple[float, str, float, bool]:
    candidates = _candidate_frame(
        frame,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_history_days=int(min_history_days),
        max_vol_63=float(max_vol_63),
        max_drawdown_126=float(max_drawdown_126),
    )
    breadth_ratio = float((candidates["sma200_gap"] > 0).mean()) if not candidates.empty else 0.0
    benchmark_rows = frame.loc[frame["symbol"] == normalize_symbol(benchmark_symbol)]
    benchmark_trend_positive = bool(
        not benchmark_rows.empty
        and pd.notna(benchmark_rows["sma200_gap"].iloc[-1])
        and float(benchmark_rows["sma200_gap"].iloc[-1]) > 0
    )
    if (not benchmark_trend_positive) and breadth_ratio < float(hard_breadth_threshold):
        return float(hard_defense_exposure), "hard_defense", breadth_ratio, benchmark_trend_positive
    if (not benchmark_trend_positive) or breadth_ratio < float(soft_breadth_threshold):
        return float(soft_defense_exposure), "soft_defense", breadth_ratio, benchmark_trend_positive
    return float(risk_on_exposure), "risk_on", breadth_ratio, benchmark_trend_positive


def _select_with_sector_cap(
    ranked: pd.DataFrame,
    *,
    holdings_count: int,
    single_name_cap: float,
    sector_cap: float,
    current_holdings: set[str],
    hold_buffer: int,
) -> list[str]:
    if ranked.empty or holdings_count <= 0:
        return []
    max_names_by_sector = max(1, int(math.floor(float(sector_cap) / max(float(single_name_cap), 1e-12))))
    selected: list[str] = []
    sector_counts: dict[str, int] = {}
    rank_map = dict(zip(ranked["symbol"].astype(str), ranked["rank"].astype(int)))
    sector_map = dict(zip(ranked["symbol"].astype(str), ranked["sector"].astype(str)))
    max_hold_rank = int(holdings_count) + max(int(hold_buffer), 0)
    preferred_symbols = [
        symbol
        for symbol in ranked["symbol"].astype(str).tolist()
        if symbol in current_holdings and int(rank_map[symbol]) <= max_hold_rank
    ]
    all_symbols = preferred_symbols + [symbol for symbol in ranked["symbol"].astype(str).tolist() if symbol not in preferred_symbols]
    for symbol in all_symbols:
        if len(selected) >= int(holdings_count):
            break
        sector = sector_map.get(symbol, "unknown")
        if sector_counts.get(sector, 0) >= max_names_by_sector:
            continue
        selected.append(symbol)
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    return selected


def build_target_weights(
    feature_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    safe_haven: str = SAFE_HAVEN,
    holdings_count: int = DEFAULT_HOLDINGS_COUNT,
    single_name_cap: float = DEFAULT_SINGLE_NAME_CAP,
    sector_cap: float = DEFAULT_SECTOR_CAP,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_history_days: int = DEFAULT_MIN_HISTORY_DAYS,
    max_vol_63: float = DEFAULT_MAX_VOL_63,
    max_drawdown_126: float = DEFAULT_MAX_DRAWDOWN_126,
    hold_buffer: int = DEFAULT_HOLD_BUFFER,
    hold_bonus: float = DEFAULT_HOLD_BONUS,
    risk_on_exposure: float = DEFAULT_RISK_ON_EXPOSURE,
    soft_defense_exposure: float = DEFAULT_SOFT_DEFENSE_EXPOSURE,
    hard_defense_exposure: float = DEFAULT_HARD_DEFENSE_EXPOSURE,
    soft_breadth_threshold: float = DEFAULT_SOFT_BREADTH_THRESHOLD,
    hard_breadth_threshold: float = DEFAULT_HARD_BREADTH_THRESHOLD,
) -> tuple[dict[str, float], pd.DataFrame, dict[str, object]]:
    if holdings_count <= 0:
        raise ValueError("holdings_count must be positive")
    if single_name_cap <= 0:
        raise ValueError("single_name_cap must be positive")
    if sector_cap <= 0:
        raise ValueError("sector_cap must be positive")

    frame = _to_frame(feature_snapshot)
    benchmark_symbol = normalize_symbol(benchmark_symbol)
    safe_haven = normalize_symbol(safe_haven)
    stock_exposure, regime, breadth_ratio, benchmark_trend_positive = _resolve_stock_exposure(
        frame,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_history_days=int(min_history_days),
        max_vol_63=float(max_vol_63),
        max_drawdown_126=float(max_drawdown_126),
        risk_on_exposure=float(risk_on_exposure),
        soft_defense_exposure=float(soft_defense_exposure),
        hard_defense_exposure=float(hard_defense_exposure),
        soft_breadth_threshold=float(soft_breadth_threshold),
        hard_breadth_threshold=float(hard_breadth_threshold),
    )
    ranked = score_candidates(
        frame,
        current_holdings,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_history_days=int(min_history_days),
        max_vol_63=float(max_vol_63),
        max_drawdown_126=float(max_drawdown_126),
        hold_bonus=float(hold_bonus),
    )
    metadata: dict[str, object] = {
        "benchmark_symbol": benchmark_symbol,
        "benchmark_trend_positive": benchmark_trend_positive,
        "regime": regime,
        "breadth_ratio": breadth_ratio,
        "target_stock_weight": float(stock_exposure),
        "realized_stock_weight": 0.0,
        "safe_haven_weight": 1.0,
        "selected_symbols": (),
        "selected_count": 0,
        "candidate_count": int(len(ranked)),
        "requested_holdings_count": int(holdings_count),
        "single_name_cap": float(single_name_cap),
        "sector_cap": float(sector_cap),
    }
    if ranked.empty or stock_exposure <= 0:
        return {safe_haven: 1.0}, ranked, metadata

    selected = _select_with_sector_cap(
        ranked,
        holdings_count=int(holdings_count),
        single_name_cap=float(single_name_cap),
        sector_cap=float(sector_cap),
        current_holdings=_normalize_holdings(current_holdings),
        hold_buffer=int(hold_buffer),
    )
    if not selected:
        return {safe_haven: 1.0}, ranked, metadata

    per_name_weight = min(float(single_name_cap), float(stock_exposure) / len(selected))
    weights = {symbol: float(per_name_weight) for symbol in selected}
    invested_weight = float(sum(weights.values()))
    safe_weight = max(0.0, float(1.0 - invested_weight))
    if safe_weight > 1e-12:
        weights[safe_haven] = safe_weight

    metadata.update(
        {
            "realized_stock_weight": invested_weight,
            "safe_haven_weight": safe_weight,
            "selected_symbols": tuple(selected),
            "selected_count": int(len(selected)),
            "effective_single_name_cap": float(single_name_cap),
        }
    )
    return weights, ranked, metadata


def extract_managed_symbols(
    feature_snapshot: Any,
    *,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    safe_haven: str = SAFE_HAVEN,
) -> tuple[str, ...]:
    frame = _to_frame(feature_snapshot)
    excluded = {normalize_symbol(benchmark_symbol)}
    safe_haven = normalize_symbol(safe_haven)
    symbols = [symbol for symbol in frame["symbol"].tolist() if symbol not in excluded]
    if safe_haven and safe_haven not in symbols:
        symbols.append(safe_haven)
    return tuple(dict.fromkeys(symbols))


def compute_signals(
    feature_snapshot: Any,
    current_holdings: Any,
    *,
    benchmark_symbol: str = BENCHMARK_SYMBOL,
    safe_haven: str = SAFE_HAVEN,
    **kwargs: Any,
):
    kwargs.pop("translator", None)
    kwargs.pop("signal_text_fn", None)
    kwargs.pop("execution_cash_reserve_ratio", None)
    managed_symbols = extract_managed_symbols(
        feature_snapshot,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
    )
    weights, ranked, metadata = build_target_weights(
        feature_snapshot,
        current_holdings,
        benchmark_symbol=benchmark_symbol,
        safe_haven=safe_haven,
        **kwargs,
    )
    top_preview = ", ".join(
        f"{row.symbol}({row.score:.2f})"
        for row in ranked.head(5).itertuples(index=False)
    )
    signal_desc = (
        f"hk liquid momentum quality regime={metadata['regime']} breadth={metadata['breadth_ratio']:.1%} "
        f"benchmark_trend={'up' if metadata['benchmark_trend_positive'] else 'down'} "
        f"target_stock={metadata['target_stock_weight']:.1%} realized_stock={metadata['realized_stock_weight']:.1%} "
        f"selected={metadata['selected_count']} top={top_preview}"
    )
    status_desc = (
        f"regime={metadata['regime']} | breadth={metadata['breadth_ratio']:.1%} | "
        f"target_stock={metadata['target_stock_weight']:.1%} | realized_stock={metadata['realized_stock_weight']:.1%}"
    )
    return (
        weights,
        signal_desc,
        metadata["regime"] == "hard_defense",
        status_desc,
        {
            **metadata,
            "managed_symbols": managed_symbols,
            "status_icon": STATUS_ICON,
            "signal_source": SIGNAL_SOURCE,
            "snapshot_contract_version": SNAPSHOT_CONTRACT_VERSION,
        },
    )
