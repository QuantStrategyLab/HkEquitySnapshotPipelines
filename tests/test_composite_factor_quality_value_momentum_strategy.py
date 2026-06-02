from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.composite_factor_quality_value_momentum_strategy import (
    REQUIRED_FACTOR_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot() -> pd.DataFrame:
    rows = [
        {
            "symbol": "02800",
            "sector": "ETF",
            "close_hkd": 20.8,
            "adv20_hkd": 1_200_000_000,
            "market_cap_hkd": 350_000_000_000,
            "roe_ttm": 0.08,
            "earnings_variability_3y": 0.20,
            "debt_to_equity": 0.20,
            "book_to_price": 0.45,
            "earnings_yield": 0.04,
            "free_cash_flow_yield": 0.03,
            "mom_12m_to_high": -0.08,
            "realized_vol_252": 0.18,
            "beta_252": 1.00,
            "maxdd_252": -0.18,
            "sma200_gap": 0.02,
            "suspension_days_63": 0,
            "eligible": True,
            "southbound_eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00941.HK",
            "sector": "Telecommunications",
            "close_hkd": 75.0,
            "adv20_hkd": 1_300_000_000,
            "market_cap_hkd": 1_500_000_000_000,
            "roe_ttm": 0.18,
            "earnings_variability_3y": 0.08,
            "debt_to_equity": 0.35,
            "book_to_price": 0.58,
            "earnings_yield": 0.08,
            "free_cash_flow_yield": 0.06,
            "mom_12m_to_high": -0.03,
            "realized_vol_252": 0.16,
            "beta_252": 0.55,
            "maxdd_252": -0.10,
            "sma200_gap": 0.10,
            "suspension_days_63": 0,
            "eligible": True,
            "southbound_eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00002",
            "sector": "Utilities",
            "close_hkd": 45.0,
            "adv20_hkd": 250_000_000,
            "market_cap_hkd": 120_000_000_000,
            "roe_ttm": 0.12,
            "earnings_variability_3y": 0.10,
            "debt_to_equity": 0.42,
            "book_to_price": 0.62,
            "earnings_yield": 0.06,
            "free_cash_flow_yield": 0.05,
            "mom_12m_to_high": -0.06,
            "realized_vol_252": 0.14,
            "beta_252": 0.50,
            "maxdd_252": -0.12,
            "sma200_gap": 0.07,
            "suspension_days_63": 0,
            "eligible": True,
            "southbound_eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "03968",
            "sector": "Financials",
            "close_hkd": 44.0,
            "adv20_hkd": 950_000_000,
            "market_cap_hkd": 780_000_000_000,
            "roe_ttm": 0.16,
            "earnings_variability_3y": 0.09,
            "debt_to_equity": 0.68,
            "book_to_price": 0.72,
            "earnings_yield": 0.09,
            "free_cash_flow_yield": 0.04,
            "mom_12m_to_high": -0.07,
            "realized_vol_252": 0.22,
            "beta_252": 0.85,
            "maxdd_252": -0.18,
            "sma200_gap": 0.08,
            "suspension_days_63": 0,
            "eligible": True,
            "southbound_eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "01378",
            "sector": "Materials",
            "close_hkd": 13.0,
            "adv20_hkd": 160_000_000,
            "market_cap_hkd": 90_000_000_000,
            "roe_ttm": 0.04,
            "earnings_variability_3y": 0.35,
            "debt_to_equity": 1.60,
            "book_to_price": 0.30,
            "earnings_yield": 0.02,
            "free_cash_flow_yield": -0.01,
            "mom_12m_to_high": -0.45,
            "realized_vol_252": 0.42,
            "beta_252": 1.35,
            "maxdd_252": -0.50,
            "sma200_gap": -0.12,
            "suspension_days_63": 0,
            "eligible": True,
            "southbound_eligible": True,
            "lot_size": 500,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("941.HK") == "00941"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_filters_weak_quality_and_ranks_composite_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00002"]
    assert "01378" not in set(ranked["symbol"])
    assert {"quality_score", "value_score", "momentum_score", "low_vol_score"}.issubset(ranked.columns)
    assert ranked.loc[ranked["symbol"] == "00941", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "03968", "score"
    ].iloc[0]


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.08,
        sector_cap=0.16,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "00002", "03968"]
    assert weights["00941"] == pytest.approx(0.08)
    assert weights["00002"] == pytest.approx(0.08)
    assert weights["03968"] == pytest.approx(0.08)
    assert weights["02800"] == pytest.approx(0.76)
    assert metadata["regime"] == "risk_on"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"00002"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk composite factor qvm" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_composite_factor_quality_value_momentum.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
