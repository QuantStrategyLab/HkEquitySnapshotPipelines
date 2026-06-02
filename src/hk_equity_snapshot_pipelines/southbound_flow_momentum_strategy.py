from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

HK_EQUITY_DOMAIN = "hk_equity"
SIGNAL_SOURCE = "flow_snapshot"
STATUS_ICON = "🇭🇰"
PROFILE_NAME = "hk_southbound_flow_momentum"
SAFE_HAVEN = "02800"
DEFAULT_HOLDINGS_COUNT = 8
DEFAULT_SINGLE_NAME_CAP = 0.12
DEFAULT_SECTOR_CAP = 0.30
DEFAULT_MIN_ADV20_HKD = 50_000_000.0
DEFAULT_MIN_MARKET_CAP_HKD = 10_000_000_000.0
DEFAULT_MIN_FLOW_ZSCORE = 0.0
DEFAULT_MIN_FLOW_PERSISTENCE = 0.0
DEFAULT_MAX_SUSPENSION_DAYS_63 = 0
DEFAULT_HOLD_BUFFER = 2
DEFAULT_HOLD_BONUS = 0.05
DEFAULT_RISK_ON_EXPOSURE = 1.0
DEFAULT_SOFT_DEFENSE_EXPOSURE = 0.50
DEFAULT_HARD_DEFENSE_EXPOSURE = 0.00
DEFAULT_SOFT_BREADTH_THRESHOLD = 0.45
DEFAULT_HARD_BREADTH_THRESHOLD = 0.30
DEFAULT_EXECUTION_CASH_RESERVE_RATIO = 0.02
SNAPSHOT_CONTRACT_VERSION = "hk_southbound_flow_momentum.flow_snapshot.v1"
REQUIRE_SNAPSHOT_MANIFEST = True

REQUIRED_FLOW_COLUMNS = frozenset(
    {
        "symbol",
        "sector",
        "close_hkd",
        "adv20_hkd",
        "southbound_eligible",
        "southbound_net_buy_hkd_5d",
        "southbound_net_buy_hkd_20d",
        "southbound_net_buy_hkd_60d",
        "southbound_turnover_share_20d",
        "southbound_holding_pct",
        "southbound_holding_pct_change_20d",
        "southbound_holding_pct_change_60d",
        "flow_zscore_20d",
        "flow_persistence_score",
        "mom_6m",
        "sma200_gap",
        "suspension_days_63",
    }
)
OPTIONAL_FLOW_COLUMNS = frozenset(
    {
        "as_of",
        "snapshot_date",
        "eligible",
        "market_cap_hkd",
        "lot_size",
        "holiday_adjusted_flow_flag",
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


def _to_frame(flow_snapshot: Any) -> pd.DataFrame:
    frame = flow_snapshot.copy() if isinstance(flow_snapshot, pd.DataFrame) else pd.DataFrame(list(flow_snapshot))
    if frame.empty:
        raise ValueError("flow_snapshot must contain at least one row")
    missing = REQUIRED_FLOW_COLUMNS - set(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"flow_snapshot missing required columns: {missing_text}")

    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame["sector"] = frame["sector"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    if "as_of" in frame.columns:
        frame["as_of"] = pd.to_datetime(frame["as_of"], utc=False).dt.tz_localize(None).dt.normalize()
    if "snapshot_date" in frame.columns:
        frame["snapshot_date"] = pd.to_datetime(frame["snapshot_date"], utc=False).dt.tz_localize(None).dt.normalize()
    if "eligible" not in frame.columns:
        frame["eligible"] = True
    frame["eligible"] = frame["eligible"].map(_coerce_bool)
    frame["southbound_eligible"] = frame["southbound_eligible"].map(_coerce_bool)
    for bool_column in ("holiday_adjusted_flow_flag", "corporate_action_flag"):
        if bool_column in frame.columns:
            frame[bool_column] = frame[bool_column].map(_coerce_bool)
        else:
            frame[bool_column] = False
    if "market_cap_hkd" not in frame.columns:
        frame["market_cap_hkd"] = pd.NA

    numeric_columns = (REQUIRED_FLOW_COLUMNS | OPTIONAL_FLOW_COLUMNS) - {
        "symbol",
        "sector",
        "as_of",
        "snapshot_date",
        "eligible",
        "southbound_eligible",
        "holiday_adjusted_flow_flag",
        "corporate_action_flag",
    }
    for column in sorted(numeric_columns & set(frame.columns)):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
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
    safe_haven: str,
    min_adv20_hkd: float,
    min_market_cap_hkd: float,
    min_flow_zscore: float,
    min_flow_persistence: float,
    max_suspension_days_63: int,
) -> pd.DataFrame:
    safe_haven = normalize_symbol(safe_haven)
    required_numeric = [
        "adv20_hkd",
        "southbound_net_buy_hkd_5d",
        "southbound_net_buy_hkd_20d",
        "southbound_net_buy_hkd_60d",
        "southbound_turnover_share_20d",
        "southbound_holding_pct",
        "southbound_holding_pct_change_20d",
        "southbound_holding_pct_change_60d",
        "flow_zscore_20d",
        "flow_persistence_score",
        "mom_6m",
        "sma200_gap",
        "suspension_days_63",
    ]
    candidates = frame.loc[
        (frame["symbol"] != safe_haven)
        & frame["eligible"]
        & frame["southbound_eligible"]
        & ~frame["corporate_action_flag"]
        & frame["adv20_hkd"].ge(float(min_adv20_hkd))
        & frame["southbound_net_buy_hkd_20d"].gt(0.0)
        & frame["southbound_holding_pct_change_20d"].gt(0.0)
        & frame["flow_zscore_20d"].ge(float(min_flow_zscore))
        & frame["flow_persistence_score"].ge(float(min_flow_persistence))
        & frame["mom_6m"].gt(0.0)
        & frame["sma200_gap"].gt(0.0)
        & frame["suspension_days_63"].le(int(max_suspension_days_63))
        & frame[required_numeric].notna().all(axis=1)
    ].copy()
    if candidates.empty or candidates["market_cap_hkd"].isna().all():
        return candidates
    return candidates.loc[
        candidates["market_cap_hkd"].isna() | candidates["market_cap_hkd"].ge(float(min_market_cap_hkd))
    ].copy()


def score_candidates(
    flow_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    safe_haven: str = SAFE_HAVEN,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_flow_zscore: float = DEFAULT_MIN_FLOW_ZSCORE,
    min_flow_persistence: float = DEFAULT_MIN_FLOW_PERSISTENCE,
    max_suspension_days_63: int = DEFAULT_MAX_SUSPENSION_DAYS_63,
    hold_bonus: float = DEFAULT_HOLD_BONUS,
) -> pd.DataFrame:
    frame = _to_frame(flow_snapshot)
    eligible = _candidate_frame(
        frame,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_flow_zscore=float(min_flow_zscore),
        min_flow_persistence=float(min_flow_persistence),
        max_suspension_days_63=int(max_suspension_days_63),
    )
    if eligible.empty:
        return pd.DataFrame(columns=["rank", "symbol", "sector", "score", "eligible"])

    eligible["score"] = (
        _zscore(eligible["southbound_net_buy_hkd_20d"]) * 0.25
        + _zscore(eligible["southbound_net_buy_hkd_60d"]) * 0.15
        + _zscore(eligible["southbound_holding_pct_change_20d"]) * 0.20
        + _zscore(eligible["southbound_holding_pct_change_60d"]) * 0.10
        + _zscore(eligible["flow_zscore_20d"]) * 0.15
        + _zscore(eligible["flow_persistence_score"]) * 0.10
        + _zscore(eligible["mom_6m"]) * 0.05
    )
    current_holdings_set = _normalize_holdings(current_holdings)
    if current_holdings_set:
        eligible.loc[eligible["symbol"].isin(current_holdings_set), "score"] += float(hold_bonus)
    ranked = eligible.sort_values(
        by=["score", "southbound_net_buy_hkd_20d", "adv20_hkd", "symbol"],
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
        "southbound_net_buy_hkd_5d",
        "southbound_net_buy_hkd_20d",
        "southbound_net_buy_hkd_60d",
        "southbound_turnover_share_20d",
        "southbound_holding_pct",
        "southbound_holding_pct_change_20d",
        "southbound_holding_pct_change_60d",
        "flow_zscore_20d",
        "flow_persistence_score",
        "mom_6m",
        "sma200_gap",
        "suspension_days_63",
        "lot_size",
    ]
    return ranked.loc[:, [column for column in output_columns if column in ranked.columns]]


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


def _resolve_stock_exposure(
    ranked: pd.DataFrame,
    *,
    risk_on_exposure: float,
    soft_defense_exposure: float,
    hard_defense_exposure: float,
    soft_breadth_threshold: float,
    hard_breadth_threshold: float,
) -> tuple[float, str, float]:
    breadth_ratio = float((ranked["sma200_gap"] > 0).mean()) if not ranked.empty else 0.0
    if breadth_ratio < float(hard_breadth_threshold):
        return float(hard_defense_exposure), "hard_defense", breadth_ratio
    if breadth_ratio < float(soft_breadth_threshold):
        return float(soft_defense_exposure), "soft_defense", breadth_ratio
    return float(risk_on_exposure), "risk_on", breadth_ratio


def build_target_weights(
    flow_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    safe_haven: str = SAFE_HAVEN,
    holdings_count: int = DEFAULT_HOLDINGS_COUNT,
    single_name_cap: float = DEFAULT_SINGLE_NAME_CAP,
    sector_cap: float = DEFAULT_SECTOR_CAP,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_flow_zscore: float = DEFAULT_MIN_FLOW_ZSCORE,
    min_flow_persistence: float = DEFAULT_MIN_FLOW_PERSISTENCE,
    max_suspension_days_63: int = DEFAULT_MAX_SUSPENSION_DAYS_63,
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

    safe_haven = normalize_symbol(safe_haven)
    ranked = score_candidates(
        flow_snapshot,
        current_holdings,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_flow_zscore=float(min_flow_zscore),
        min_flow_persistence=float(min_flow_persistence),
        max_suspension_days_63=int(max_suspension_days_63),
        hold_bonus=float(hold_bonus),
    )
    stock_exposure, regime, breadth_ratio = _resolve_stock_exposure(
        ranked,
        risk_on_exposure=float(risk_on_exposure),
        soft_defense_exposure=float(soft_defense_exposure),
        hard_defense_exposure=float(hard_defense_exposure),
        soft_breadth_threshold=float(soft_breadth_threshold),
        hard_breadth_threshold=float(hard_breadth_threshold),
    )
    metadata: dict[str, object] = {
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


def extract_managed_symbols(flow_snapshot: Any, *, safe_haven: str = SAFE_HAVEN) -> tuple[str, ...]:
    frame = _to_frame(flow_snapshot)
    safe_haven = normalize_symbol(safe_haven)
    symbols = [symbol for symbol in frame["symbol"].tolist() if symbol != safe_haven]
    if safe_haven and safe_haven not in symbols:
        symbols.append(safe_haven)
    return tuple(dict.fromkeys(symbols))


def compute_signals(flow_snapshot: Any, current_holdings: Any, *, safe_haven: str = SAFE_HAVEN, **kwargs: Any):
    kwargs.pop("translator", None)
    kwargs.pop("signal_text_fn", None)
    kwargs.pop("execution_cash_reserve_ratio", None)
    managed_symbols = extract_managed_symbols(flow_snapshot, safe_haven=safe_haven)
    weights, ranked, metadata = build_target_weights(
        flow_snapshot,
        current_holdings,
        safe_haven=safe_haven,
        **kwargs,
    )
    top_preview = ", ".join(
        f"{row.symbol}({row.score:.2f})"
        for row in ranked.head(5).itertuples(index=False)
    )
    signal_desc = (
        f"hk southbound flow momentum regime={metadata['regime']} breadth={metadata['breadth_ratio']:.1%} "
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
