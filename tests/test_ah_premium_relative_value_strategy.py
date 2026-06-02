from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.ah_premium_relative_value_strategy import (
    REQUIRED_VALUATION_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot(*, trend: float = 0.08) -> pd.DataFrame:
    rows = [
        {
            "symbol": "02800",
            "a_symbol": "N/A",
            "sector": "ETF",
            "h_close_hkd": 20.8,
            "a_close_cny": 0.0,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 1_200_000_000,
            "h_market_cap_hkd": 350_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "connect_eligible_h": False,
            "connect_eligible_a": False,
            "ah_premium_pct": 0.00,
            "ah_premium_percentile_3y": 0.00,
            "ah_premium_change_20d": 0.000,
            "southbound_holding_pct_change_20d": 0.000,
            "h_liquidity_score": 1.00,
            "h_mom_6m": 0.03,
            "h_sma200_gap": trend,
            "h_vol_63": 0.02,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "03968.HK",
            "a_symbol": "600036",
            "sector": "Financials",
            "h_close_hkd": 44.0,
            "a_close_cny": 43.5,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 950_000_000,
            "h_market_cap_hkd": 780_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": True,
            "ah_premium_pct": 0.32,
            "ah_premium_percentile_3y": 0.86,
            "ah_premium_change_20d": -0.035,
            "southbound_holding_pct_change_20d": 0.006,
            "h_liquidity_score": 0.92,
            "h_mom_6m": 0.16,
            "h_sma200_gap": trend,
            "h_vol_63": 0.030,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "02318",
            "a_symbol": "601318",
            "sector": "Financials",
            "h_close_hkd": 48.0,
            "a_close_cny": 54.8,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 1_100_000_000,
            "h_market_cap_hkd": 980_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": True,
            "ah_premium_pct": 0.28,
            "ah_premium_percentile_3y": 0.82,
            "ah_premium_change_20d": -0.018,
            "southbound_holding_pct_change_20d": 0.007,
            "h_liquidity_score": 0.95,
            "h_mom_6m": 0.15,
            "h_sma200_gap": trend,
            "h_vol_63": 0.035,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "01088",
            "a_symbol": "601088",
            "sector": "Energy",
            "h_close_hkd": 33.0,
            "a_close_cny": 40.0,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 620_000_000,
            "h_market_cap_hkd": 520_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": True,
            "ah_premium_pct": 0.22,
            "ah_premium_percentile_3y": 0.74,
            "ah_premium_change_20d": -0.012,
            "southbound_holding_pct_change_20d": 0.004,
            "h_liquidity_score": 0.74,
            "h_mom_6m": 0.11,
            "h_sma200_gap": trend,
            "h_vol_63": 0.028,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "01919",
            "a_symbol": "601919",
            "sector": "Industrials",
            "h_close_hkd": 13.5,
            "a_close_cny": 15.4,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 240_000_000,
            "h_market_cap_hkd": 180_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": True,
            "ah_premium_pct": 0.13,
            "ah_premium_percentile_3y": 0.56,
            "ah_premium_change_20d": -0.003,
            "southbound_holding_pct_change_20d": 0.001,
            "h_liquidity_score": 0.43,
            "h_mom_6m": 0.18,
            "h_sma200_gap": trend,
            "h_vol_63": 0.070,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "01288",
            "a_symbol": "601288",
            "sector": "Financials",
            "h_close_hkd": 3.9,
            "a_close_cny": 4.4,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 800_000_000,
            "h_market_cap_hkd": 1_500_000_000_000,
            "lot_size": 1000,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": False,
            "ah_premium_pct": 0.14,
            "ah_premium_percentile_3y": 0.62,
            "ah_premium_change_20d": -0.004,
            "southbound_holding_pct_change_20d": 0.002,
            "h_liquidity_score": 0.70,
            "h_mom_6m": 0.06,
            "h_sma200_gap": trend,
            "h_vol_63": 0.020,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
        {
            "symbol": "00386",
            "a_symbol": "600028",
            "sector": "Energy",
            "h_close_hkd": 4.6,
            "a_close_cny": 5.2,
            "fx_cnyhkd": 1.08,
            "h_adv20_hkd": 700_000_000,
            "h_market_cap_hkd": 520_000_000_000,
            "lot_size": 2000,
            "eligible": True,
            "connect_eligible_h": True,
            "connect_eligible_a": True,
            "ah_premium_pct": 0.16,
            "ah_premium_percentile_3y": 0.64,
            "ah_premium_change_20d": -0.003,
            "southbound_holding_pct_change_20d": 0.003,
            "h_liquidity_score": 0.78,
            "h_mom_6m": -0.02,
            "h_sma200_gap": -0.01,
            "h_vol_63": 0.036,
            "suspension_days_63": 0,
            "corporate_action_flag": False,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("3968.HK") == "03968"
    assert normalize_symbol("02318") == "02318"


def test_score_candidates_filters_non_connect_and_downtrend_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:3] == ["03968", "02318", "01088"]
    assert "01288" not in set(ranked["symbol"])
    assert "00386" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "03968", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "02318", "score"
    ].iloc[0]


def test_build_target_weights_applies_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=4,
        single_name_cap=0.12,
        sector_cap=0.24,
    )

    assert ranked["symbol"].tolist()[:4] == ["03968", "02318", "01088", "01919"]
    assert weights["03968"] == pytest.approx(0.12)
    assert weights["02318"] == pytest.approx(0.12)
    assert weights["01088"] == pytest.approx(0.12)
    assert weights["01919"] == pytest.approx(0.12)
    assert weights["02800"] == pytest.approx(0.52)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("03968", "02318", "01088", "01919")


def test_build_target_weights_goes_defensive_when_no_valuation_candidate_survives():
    snapshot = _snapshot(trend=-0.03)

    weights, _ranked, metadata = build_target_weights(snapshot, holdings_count=4)

    assert weights == {"02800": 1.0}
    assert metadata["regime"] == "hard_defense"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"02318"},
        holdings_count=3,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk ah premium relative value" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "valuation_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_ah_premium_relative_value.valuation_snapshot.v1"
    assert "03968" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1
    assert "03968" in symbols


def test_score_candidates_requires_valuation_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_VALUATION_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="valuation_snapshot missing required columns"):
        score_candidates(snapshot)
