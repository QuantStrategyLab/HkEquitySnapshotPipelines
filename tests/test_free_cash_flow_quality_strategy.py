from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.free_cash_flow_quality_strategy import (
    REQUIRED_FACTOR_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "02800",
                "sector": "ETF",
                "close_hkd": 20.8,
                "adv20_hkd": 1_200_000_000,
                "market_cap_hkd": 350_000_000_000,
                "free_cash_flow_hkd": 10_000_000_000,
                "enterprise_value_hkd": 360_000_000_000,
                "free_cash_flow_yield": 0.028,
                "fcf_yield_percentile_3y": 0.45,
                "roe_ttm": 0.08,
                "revenue_growth_ttm": 0.02,
                "realized_vol_252": 0.18,
                "maxdd_252": -0.18,
                "sma200_gap": 0.02,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "lot_size": 500,
                "earnings_yield": 0.04,
                "debt_to_equity": 0.20,
            },
            {
                "symbol": "00941.HK",
                "sector": "Telecommunications",
                "close_hkd": 75.0,
                "adv20_hkd": 1_300_000_000,
                "market_cap_hkd": 1_500_000_000_000,
                "free_cash_flow_hkd": 125_000_000_000,
                "enterprise_value_hkd": 1_550_000_000_000,
                "free_cash_flow_yield": 0.081,
                "fcf_yield_percentile_3y": 0.92,
                "roe_ttm": 0.18,
                "revenue_growth_ttm": 0.06,
                "realized_vol_252": 0.16,
                "maxdd_252": -0.10,
                "sma200_gap": 0.10,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "lot_size": 500,
                "earnings_yield": 0.08,
                "debt_to_equity": 0.35,
            },
            {
                "symbol": "00883",
                "sector": "Energy",
                "close_hkd": 20.2,
                "adv20_hkd": 900_000_000,
                "market_cap_hkd": 820_000_000_000,
                "free_cash_flow_hkd": 78_000_000_000,
                "enterprise_value_hkd": 900_000_000_000,
                "free_cash_flow_yield": 0.087,
                "fcf_yield_percentile_3y": 0.95,
                "roe_ttm": 0.16,
                "revenue_growth_ttm": 0.04,
                "realized_vol_252": 0.24,
                "maxdd_252": -0.20,
                "sma200_gap": 0.06,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "lot_size": 1000,
                "earnings_yield": 0.10,
                "debt_to_equity": 0.28,
            },
            {
                "symbol": "00002",
                "sector": "Utilities",
                "close_hkd": 45.0,
                "adv20_hkd": 250_000_000,
                "market_cap_hkd": 120_000_000_000,
                "free_cash_flow_hkd": 9_000_000_000,
                "enterprise_value_hkd": 150_000_000_000,
                "free_cash_flow_yield": 0.060,
                "fcf_yield_percentile_3y": 0.80,
                "roe_ttm": 0.12,
                "revenue_growth_ttm": 0.02,
                "realized_vol_252": 0.14,
                "maxdd_252": -0.12,
                "sma200_gap": 0.07,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "lot_size": 500,
                "earnings_yield": 0.06,
                "debt_to_equity": 0.42,
            },
            {
                "symbol": "09999",
                "sector": "Technology",
                "close_hkd": 80.0,
                "adv20_hkd": 500_000_000,
                "market_cap_hkd": 300_000_000_000,
                "free_cash_flow_hkd": -2_000_000_000,
                "enterprise_value_hkd": 320_000_000_000,
                "free_cash_flow_yield": -0.006,
                "fcf_yield_percentile_3y": 0.10,
                "roe_ttm": -0.02,
                "revenue_growth_ttm": 0.18,
                "realized_vol_252": 0.45,
                "maxdd_252": -0.52,
                "sma200_gap": 0.04,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "lot_size": 100,
                "earnings_yield": -0.01,
                "debt_to_equity": 1.20,
            },
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("883.HK") == "00883"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_filters_negative_fcf_and_ranks_quality_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00883"]
    assert "09999" not in set(ranked["symbol"])
    assert {"fcf_score", "quality_score", "risk_score", "trend_score"}.issubset(ranked.columns)
    assert ranked.loc[ranked["symbol"] == "00941", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00002", "score"
    ].iloc[0]


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.08,
        sector_cap=0.16,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "00883", "00002"]
    assert weights["00941"] == pytest.approx(0.08)
    assert weights["00883"] == pytest.approx(0.08)
    assert weights["00002"] == pytest.approx(0.08)
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
    assert "hk free cash flow quality" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_free_cash_flow_quality.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
