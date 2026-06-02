from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.index_rebalance_event_strategy import (
    REQUIRED_EVENT_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot(*, days_to_effective: int = 6) -> pd.DataFrame:
    rows = [
        {
            "symbol": "02800",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "hold",
            "predicted_add_probability": 0.00,
            "predicted_remove_probability": 0.00,
            "official_add_flag": False,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 1.00,
            "estimated_slippage_bps": 5.0,
            "index_weight_estimate": 0.00,
            "crowding_score": 0.00,
            "post_announcement_momentum_5d": 0.01,
            "close_hkd": 20.8,
            "adv20_hkd": 1_200_000_000,
            "market_cap_hkd": 350_000_000_000,
            "sector": "ETF",
            "lot_size": 500,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "03750.HK",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "add",
            "predicted_add_probability": 0.95,
            "predicted_remove_probability": 0.02,
            "official_add_flag": True,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.92,
            "estimated_slippage_bps": 35.0,
            "index_weight_estimate": 0.012,
            "crowding_score": 0.35,
            "post_announcement_momentum_5d": 0.08,
            "close_hkd": 285.0,
            "adv20_hkd": 900_000_000,
            "market_cap_hkd": 1_200_000_000_000,
            "sector": "Industrials",
            "lot_size": 100,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "03993",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "add",
            "predicted_add_probability": 0.90,
            "predicted_remove_probability": 0.04,
            "official_add_flag": True,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.86,
            "estimated_slippage_bps": 42.0,
            "index_weight_estimate": 0.010,
            "crowding_score": 0.32,
            "post_announcement_momentum_5d": 0.06,
            "close_hkd": 7.2,
            "adv20_hkd": 420_000_000,
            "market_cap_hkd": 260_000_000_000,
            "sector": "Materials",
            "lot_size": 1000,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "06181",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "add",
            "predicted_add_probability": 0.88,
            "predicted_remove_probability": 0.05,
            "official_add_flag": True,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.74,
            "estimated_slippage_bps": 58.0,
            "index_weight_estimate": 0.008,
            "crowding_score": 0.45,
            "post_announcement_momentum_5d": 0.10,
            "close_hkd": 730.0,
            "adv20_hkd": 260_000_000,
            "market_cap_hkd": 180_000_000_000,
            "sector": "Consumer Discretionary",
            "lot_size": 100,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "02618",
            "index_family": "HSTECH",
            "review_cycle": "2025Q2",
            "data_cutoff_date": "2025-06-30",
            "announcement_date": "2025-08-22",
            "effective_date": "2025-09-08",
            "event_side": "add",
            "predicted_add_probability": 0.76,
            "predicted_remove_probability": 0.10,
            "official_add_flag": False,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.68,
            "estimated_slippage_bps": 50.0,
            "index_weight_estimate": 0.006,
            "crowding_score": 0.40,
            "post_announcement_momentum_5d": 0.05,
            "close_hkd": 12.5,
            "adv20_hkd": 220_000_000,
            "market_cap_hkd": 90_000_000_000,
            "sector": "Industrials",
            "lot_size": 500,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "00881",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "remove",
            "predicted_add_probability": 0.02,
            "predicted_remove_probability": 0.95,
            "official_add_flag": False,
            "official_remove_flag": True,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.70,
            "estimated_slippage_bps": 38.0,
            "index_weight_estimate": -0.010,
            "crowding_score": 0.20,
            "post_announcement_momentum_5d": -0.05,
            "close_hkd": 12.0,
            "adv20_hkd": 260_000_000,
            "market_cap_hkd": 60_000_000_000,
            "sector": "Consumer Discretionary",
            "lot_size": 500,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "05555",
            "index_family": "HSI",
            "review_cycle": "2025Q4",
            "data_cutoff_date": "2025-12-31",
            "announcement_date": "2026-02-13",
            "effective_date": "2026-03-09",
            "event_side": "add",
            "predicted_add_probability": 0.80,
            "predicted_remove_probability": 0.10,
            "official_add_flag": True,
            "official_remove_flag": False,
            "days_to_effective": days_to_effective,
            "event_liquidity_score": 0.73,
            "estimated_slippage_bps": 120.0,
            "index_weight_estimate": 0.007,
            "crowding_score": 0.80,
            "post_announcement_momentum_5d": 0.11,
            "close_hkd": 88.0,
            "adv20_hkd": 300_000_000,
            "market_cap_hkd": 150_000_000_000,
            "sector": "Technology",
            "lot_size": 100,
            "eligible": True,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("3750.HK") == "03750"
    assert normalize_symbol("03993") == "03993"


def test_score_candidates_filters_removals_and_high_slippage_events():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:3] == ["03750", "03993", "06181"]
    assert "00881" not in set(ranked["symbol"])
    assert "05555" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "03750", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "03993", "score"
    ].iloc[0]


def test_build_target_weights_uses_event_exposure_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=4,
        single_name_cap=0.08,
        sector_cap=0.16,
    )

    assert ranked["symbol"].tolist()[:4] == ["03750", "03993", "06181", "02618"]
    assert weights["03750"] == pytest.approx(0.08)
    assert weights["03993"] == pytest.approx(0.08)
    assert weights["06181"] == pytest.approx(0.08)
    assert weights["02618"] == pytest.approx(0.08)
    assert weights["02800"] == pytest.approx(0.68)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("03750", "03993", "06181", "02618")


def test_build_target_weights_goes_defensive_when_event_window_is_stale():
    weights, _ranked, metadata = build_target_weights(_snapshot(days_to_effective=25), holdings_count=4)

    assert weights == {"02800": 1.0}
    assert metadata["regime"] == "hard_defense"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"03993"},
        holdings_count=3,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk index rebalance event" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "event_calendar_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_index_rebalance_event.event_calendar_snapshot.v1"
    assert "03750" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1
    assert "03750" in symbols


def test_score_candidates_requires_event_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_EVENT_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="event_snapshot missing required columns"):
        score_candidates(snapshot)
