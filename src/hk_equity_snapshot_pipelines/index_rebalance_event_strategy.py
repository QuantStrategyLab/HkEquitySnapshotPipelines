from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

HK_EQUITY_DOMAIN = "hk_equity"
SIGNAL_SOURCE = "event_calendar_snapshot"
STATUS_ICON = "🇭🇰"
PROFILE_NAME = "hk_index_rebalance_event"
SAFE_HAVEN = "02800"
DEFAULT_HOLDINGS_COUNT = 6
DEFAULT_SINGLE_NAME_CAP = 0.08
DEFAULT_SECTOR_CAP = 0.20
DEFAULT_MIN_ADV20_HKD = 80_000_000.0
DEFAULT_MIN_MARKET_CAP_HKD = 10_000_000_000.0
DEFAULT_MIN_ADD_PROBABILITY = 0.60
DEFAULT_MIN_EVENT_LIQUIDITY_SCORE = 0.50
DEFAULT_MAX_ESTIMATED_SLIPPAGE_BPS = 80.0
DEFAULT_MIN_DAYS_TO_EFFECTIVE = 1
DEFAULT_MAX_DAYS_TO_EFFECTIVE = 15
DEFAULT_MAX_SUSPENSION_DAYS_63 = 0
DEFAULT_HOLD_BUFFER = 1
DEFAULT_HOLD_BONUS = 0.03
DEFAULT_RISK_ON_EXPOSURE = 0.50
DEFAULT_SOFT_DEFENSE_EXPOSURE = 0.25
DEFAULT_HARD_DEFENSE_EXPOSURE = 0.00
DEFAULT_MIN_EVENT_CANDIDATES_FOR_RISK_ON = 2
DEFAULT_EXECUTION_CASH_RESERVE_RATIO = 0.02
SNAPSHOT_CONTRACT_VERSION = "hk_index_rebalance_event.event_calendar_snapshot.v1"
REQUIRE_SNAPSHOT_MANIFEST = True

REQUIRED_EVENT_COLUMNS = frozenset(
    {
        "symbol",
        "index_family",
        "review_cycle",
        "data_cutoff_date",
        "announcement_date",
        "effective_date",
        "event_side",
        "predicted_add_probability",
        "predicted_remove_probability",
        "official_add_flag",
        "official_remove_flag",
        "days_to_effective",
        "event_liquidity_score",
        "estimated_slippage_bps",
        "close_hkd",
        "adv20_hkd",
        "market_cap_hkd",
        "post_announcement_momentum_5d",
        "suspension_days_63",
    }
)
OPTIONAL_EVENT_COLUMNS = frozenset(
    {
        "as_of",
        "snapshot_date",
        "eligible",
        "sector",
        "lot_size",
        "index_weight_estimate",
        "crowding_score",
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


def _to_frame(event_snapshot: Any) -> pd.DataFrame:
    frame = event_snapshot.copy() if isinstance(event_snapshot, pd.DataFrame) else pd.DataFrame(list(event_snapshot))
    if frame.empty:
        raise ValueError("event_snapshot must contain at least one row")
    missing = REQUIRED_EVENT_COLUMNS - set(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"event_snapshot missing required columns: {missing_text}")

    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame["index_family"] = frame["index_family"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    frame["review_cycle"] = frame["review_cycle"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    frame["event_side"] = frame["event_side"].fillna("unknown").astype(str).str.strip().str.lower()
    if "sector" not in frame.columns:
        frame["sector"] = "unknown"
    frame["sector"] = frame["sector"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    for date_column in ("as_of", "snapshot_date", "data_cutoff_date", "announcement_date", "effective_date"):
        if date_column in frame.columns:
            frame[date_column] = pd.to_datetime(frame[date_column], utc=False).dt.tz_localize(None).dt.normalize()
    if "eligible" not in frame.columns:
        frame["eligible"] = True
    frame["eligible"] = frame["eligible"].map(_coerce_bool)
    frame["official_add_flag"] = frame["official_add_flag"].map(_coerce_bool)
    frame["official_remove_flag"] = frame["official_remove_flag"].map(_coerce_bool)
    if "corporate_action_flag" in frame.columns:
        frame["corporate_action_flag"] = frame["corporate_action_flag"].map(_coerce_bool)
    else:
        frame["corporate_action_flag"] = False
    if "index_weight_estimate" not in frame.columns:
        frame["index_weight_estimate"] = 0.0
    if "crowding_score" not in frame.columns:
        frame["crowding_score"] = 0.0

    numeric_columns = (REQUIRED_EVENT_COLUMNS | OPTIONAL_EVENT_COLUMNS) - {
        "symbol",
        "index_family",
        "review_cycle",
        "data_cutoff_date",
        "announcement_date",
        "effective_date",
        "event_side",
        "as_of",
        "snapshot_date",
        "eligible",
        "sector",
        "official_add_flag",
        "official_remove_flag",
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
    min_add_probability: float,
    min_event_liquidity_score: float,
    max_estimated_slippage_bps: float,
    min_days_to_effective: int,
    max_days_to_effective: int,
    max_suspension_days_63: int,
) -> pd.DataFrame:
    safe_haven = normalize_symbol(safe_haven)
    required_numeric = [
        "predicted_add_probability",
        "predicted_remove_probability",
        "days_to_effective",
        "event_liquidity_score",
        "estimated_slippage_bps",
        "close_hkd",
        "adv20_hkd",
        "market_cap_hkd",
        "post_announcement_momentum_5d",
        "suspension_days_63",
        "index_weight_estimate",
        "crowding_score",
    ]
    add_candidate = frame["official_add_flag"] | frame["event_side"].isin({"add", "inclusion", "include"})
    probability_candidate = frame["predicted_add_probability"].ge(float(min_add_probability))
    return frame.loc[
        (frame["symbol"] != safe_haven)
        & frame["eligible"]
        & ~frame["official_remove_flag"]
        & ~frame["corporate_action_flag"]
        & (add_candidate | probability_candidate)
        & frame["predicted_remove_probability"].lt(0.40)
        & frame["days_to_effective"].between(
            int(min_days_to_effective), int(max_days_to_effective), inclusive="both"
        )
        & frame["event_liquidity_score"].ge(float(min_event_liquidity_score))
        & frame["estimated_slippage_bps"].le(float(max_estimated_slippage_bps))
        & frame["adv20_hkd"].ge(float(min_adv20_hkd))
        & frame["market_cap_hkd"].ge(float(min_market_cap_hkd))
        & frame["suspension_days_63"].le(int(max_suspension_days_63))
        & frame[required_numeric].notna().all(axis=1)
    ].copy()


def score_candidates(
    event_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    safe_haven: str = SAFE_HAVEN,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_add_probability: float = DEFAULT_MIN_ADD_PROBABILITY,
    min_event_liquidity_score: float = DEFAULT_MIN_EVENT_LIQUIDITY_SCORE,
    max_estimated_slippage_bps: float = DEFAULT_MAX_ESTIMATED_SLIPPAGE_BPS,
    min_days_to_effective: int = DEFAULT_MIN_DAYS_TO_EFFECTIVE,
    max_days_to_effective: int = DEFAULT_MAX_DAYS_TO_EFFECTIVE,
    max_suspension_days_63: int = DEFAULT_MAX_SUSPENSION_DAYS_63,
    hold_bonus: float = DEFAULT_HOLD_BONUS,
) -> pd.DataFrame:
    frame = _to_frame(event_snapshot)
    eligible = _candidate_frame(
        frame,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_add_probability=float(min_add_probability),
        min_event_liquidity_score=float(min_event_liquidity_score),
        max_estimated_slippage_bps=float(max_estimated_slippage_bps),
        min_days_to_effective=int(min_days_to_effective),
        max_days_to_effective=int(max_days_to_effective),
        max_suspension_days_63=int(max_suspension_days_63),
    )
    if eligible.empty:
        return pd.DataFrame(columns=["rank", "symbol", "sector", "score", "eligible"])

    eligible["official_add_score"] = eligible["official_add_flag"].astype(float)
    eligible["score"] = (
        eligible["official_add_score"] * 0.25
        + _zscore(eligible["predicted_add_probability"]) * 0.20
        - _zscore(eligible["predicted_remove_probability"]) * 0.10
        + _zscore(eligible["event_liquidity_score"]) * 0.15
        + _zscore(eligible["index_weight_estimate"]) * 0.10
        + _zscore(eligible["post_announcement_momentum_5d"]) * 0.10
        - _zscore(eligible["estimated_slippage_bps"]) * 0.15
        - _zscore(eligible["crowding_score"]) * 0.05
    )
    current_holdings_set = _normalize_holdings(current_holdings)
    if current_holdings_set:
        eligible.loc[eligible["symbol"].isin(current_holdings_set), "score"] += float(hold_bonus)
    ranked = eligible.sort_values(
        by=["score", "official_add_flag", "predicted_add_probability", "event_liquidity_score", "symbol"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    output_columns = [
        "rank",
        "symbol",
        "index_family",
        "review_cycle",
        "sector",
        "event_side",
        "score",
        "eligible",
        "official_add_flag",
        "predicted_add_probability",
        "predicted_remove_probability",
        "days_to_effective",
        "event_liquidity_score",
        "estimated_slippage_bps",
        "index_weight_estimate",
        "crowding_score",
        "post_announcement_momentum_5d",
        "close_hkd",
        "adv20_hkd",
        "market_cap_hkd",
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
    min_event_candidates_for_risk_on: int,
) -> tuple[float, str, float]:
    event_coverage_ratio = min(1.0, float(len(ranked)) / max(float(min_event_candidates_for_risk_on), 1.0))
    if ranked.empty:
        return float(hard_defense_exposure), "hard_defense", event_coverage_ratio
    if len(ranked) < int(min_event_candidates_for_risk_on):
        return float(soft_defense_exposure), "soft_defense", event_coverage_ratio
    return float(risk_on_exposure), "risk_on", event_coverage_ratio


def build_target_weights(
    event_snapshot: Any,
    current_holdings: Iterable[str] | None = None,
    *,
    safe_haven: str = SAFE_HAVEN,
    holdings_count: int = DEFAULT_HOLDINGS_COUNT,
    single_name_cap: float = DEFAULT_SINGLE_NAME_CAP,
    sector_cap: float = DEFAULT_SECTOR_CAP,
    min_adv20_hkd: float = DEFAULT_MIN_ADV20_HKD,
    min_market_cap_hkd: float = DEFAULT_MIN_MARKET_CAP_HKD,
    min_add_probability: float = DEFAULT_MIN_ADD_PROBABILITY,
    min_event_liquidity_score: float = DEFAULT_MIN_EVENT_LIQUIDITY_SCORE,
    max_estimated_slippage_bps: float = DEFAULT_MAX_ESTIMATED_SLIPPAGE_BPS,
    min_days_to_effective: int = DEFAULT_MIN_DAYS_TO_EFFECTIVE,
    max_days_to_effective: int = DEFAULT_MAX_DAYS_TO_EFFECTIVE,
    max_suspension_days_63: int = DEFAULT_MAX_SUSPENSION_DAYS_63,
    hold_buffer: int = DEFAULT_HOLD_BUFFER,
    hold_bonus: float = DEFAULT_HOLD_BONUS,
    risk_on_exposure: float = DEFAULT_RISK_ON_EXPOSURE,
    soft_defense_exposure: float = DEFAULT_SOFT_DEFENSE_EXPOSURE,
    hard_defense_exposure: float = DEFAULT_HARD_DEFENSE_EXPOSURE,
    min_event_candidates_for_risk_on: int = DEFAULT_MIN_EVENT_CANDIDATES_FOR_RISK_ON,
) -> tuple[dict[str, float], pd.DataFrame, dict[str, object]]:
    if holdings_count <= 0:
        raise ValueError("holdings_count must be positive")
    if single_name_cap <= 0:
        raise ValueError("single_name_cap must be positive")
    if sector_cap <= 0:
        raise ValueError("sector_cap must be positive")

    safe_haven = normalize_symbol(safe_haven)
    ranked = score_candidates(
        event_snapshot,
        current_holdings,
        safe_haven=safe_haven,
        min_adv20_hkd=float(min_adv20_hkd),
        min_market_cap_hkd=float(min_market_cap_hkd),
        min_add_probability=float(min_add_probability),
        min_event_liquidity_score=float(min_event_liquidity_score),
        max_estimated_slippage_bps=float(max_estimated_slippage_bps),
        min_days_to_effective=int(min_days_to_effective),
        max_days_to_effective=int(max_days_to_effective),
        max_suspension_days_63=int(max_suspension_days_63),
        hold_bonus=float(hold_bonus),
    )
    stock_exposure, regime, event_coverage_ratio = _resolve_stock_exposure(
        ranked,
        risk_on_exposure=float(risk_on_exposure),
        soft_defense_exposure=float(soft_defense_exposure),
        hard_defense_exposure=float(hard_defense_exposure),
        min_event_candidates_for_risk_on=int(min_event_candidates_for_risk_on),
    )
    metadata: dict[str, object] = {
        "regime": regime,
        "event_coverage_ratio": event_coverage_ratio,
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


def extract_managed_symbols(event_snapshot: Any, *, safe_haven: str = SAFE_HAVEN) -> tuple[str, ...]:
    frame = _to_frame(event_snapshot)
    safe_haven = normalize_symbol(safe_haven)
    symbols = [symbol for symbol in frame["symbol"].tolist() if symbol != safe_haven]
    if safe_haven and safe_haven not in symbols:
        symbols.append(safe_haven)
    return tuple(dict.fromkeys(symbols))


def compute_signals(event_snapshot: Any, current_holdings: Any, *, safe_haven: str = SAFE_HAVEN, **kwargs: Any):
    kwargs.pop("translator", None)
    kwargs.pop("signal_text_fn", None)
    kwargs.pop("execution_cash_reserve_ratio", None)
    managed_symbols = extract_managed_symbols(event_snapshot, safe_haven=safe_haven)
    weights, ranked, metadata = build_target_weights(
        event_snapshot,
        current_holdings,
        safe_haven=safe_haven,
        **kwargs,
    )
    top_preview = ", ".join(
        f"{row.symbol}({row.score:.2f})"
        for row in ranked.head(5).itertuples(index=False)
    )
    signal_desc = (
        f"hk index rebalance event regime={metadata['regime']} "
        f"event_coverage={metadata['event_coverage_ratio']:.1%} "
        f"target_stock={metadata['target_stock_weight']:.1%} realized_stock={metadata['realized_stock_weight']:.1%} "
        f"selected={metadata['selected_count']} top={top_preview}"
    )
    status_desc = (
        f"regime={metadata['regime']} | event_coverage={metadata['event_coverage_ratio']:.1%} | "
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
