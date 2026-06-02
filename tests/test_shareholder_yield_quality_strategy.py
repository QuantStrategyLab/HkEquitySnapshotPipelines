from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.shareholder_yield_quality_strategy import (
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
                "dividend_yield_net": 0.025,
                "buyback_yield_12m": 0.000,
                "net_payout_yield": 0.025,
                "free_cash_flow_yield": 0.025,
                "roe_ttm": 0.08,
                "debt_to_equity": 0.20,
                "realized_vol_252": 0.18,
                "maxdd_252": -0.16,
                "sma200_gap": 0.03,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": 0.000,
                "payout_ratio": 0.40,
                "earnings_yield": 0.04,
                "treasury_share_ratio": 0.000,
                "buyback_days_63": 0,
                "lot_size": 500,
            },
            {
                "symbol": "00700.HK",
                "sector": "Technology",
                "close_hkd": 390.0,
                "adv20_hkd": 2_500_000_000,
                "market_cap_hkd": 3_600_000_000_000,
                "dividend_yield_net": 0.010,
                "buyback_yield_12m": 0.055,
                "net_payout_yield": 0.065,
                "free_cash_flow_yield": 0.060,
                "roe_ttm": 0.22,
                "debt_to_equity": 0.18,
                "realized_vol_252": 0.28,
                "maxdd_252": -0.18,
                "sma200_gap": 0.14,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": -0.030,
                "payout_ratio": 0.35,
                "earnings_yield": 0.050,
                "treasury_share_ratio": 0.012,
                "buyback_days_63": 38,
                "lot_size": 100,
            },
            {
                "symbol": "01299",
                "sector": "Insurance",
                "close_hkd": 70.0,
                "adv20_hkd": 1_200_000_000,
                "market_cap_hkd": 780_000_000_000,
                "dividend_yield_net": 0.025,
                "buyback_yield_12m": 0.035,
                "net_payout_yield": 0.060,
                "free_cash_flow_yield": 0.045,
                "roe_ttm": 0.14,
                "debt_to_equity": 0.28,
                "realized_vol_252": 0.22,
                "maxdd_252": -0.16,
                "sma200_gap": 0.08,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": -0.025,
                "payout_ratio": 0.42,
                "earnings_yield": 0.055,
                "treasury_share_ratio": 0.006,
                "buyback_days_63": 24,
                "lot_size": 200,
            },
            {
                "symbol": "00941",
                "sector": "Telecommunications",
                "close_hkd": 75.0,
                "adv20_hkd": 1_300_000_000,
                "market_cap_hkd": 1_500_000_000_000,
                "dividend_yield_net": 0.060,
                "buyback_yield_12m": 0.010,
                "net_payout_yield": 0.070,
                "free_cash_flow_yield": 0.080,
                "roe_ttm": 0.18,
                "debt_to_equity": 0.35,
                "realized_vol_252": 0.16,
                "maxdd_252": -0.10,
                "sma200_gap": 0.10,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": -0.005,
                "payout_ratio": 0.65,
                "earnings_yield": 0.080,
                "treasury_share_ratio": 0.000,
                "buyback_days_63": 6,
                "lot_size": 500,
            },
            {
                "symbol": "02020",
                "sector": "Consumer Discretionary",
                "close_hkd": 77.0,
                "adv20_hkd": 260_000_000,
                "market_cap_hkd": 190_000_000_000,
                "dividend_yield_net": 0.006,
                "buyback_yield_12m": 0.020,
                "net_payout_yield": 0.026,
                "free_cash_flow_yield": 0.020,
                "roe_ttm": 0.07,
                "debt_to_equity": 0.60,
                "realized_vol_252": 0.30,
                "maxdd_252": -0.30,
                "sma200_gap": -0.04,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": 0.080,
                "payout_ratio": 0.30,
                "earnings_yield": 0.030,
                "treasury_share_ratio": 0.000,
                "buyback_days_63": 12,
                "lot_size": 1000,
            },
            {
                "symbol": "09999",
                "sector": "Technology",
                "close_hkd": 80.0,
                "adv20_hkd": 500_000_000,
                "market_cap_hkd": 300_000_000_000,
                "dividend_yield_net": 0.000,
                "buyback_yield_12m": 0.030,
                "net_payout_yield": 0.030,
                "free_cash_flow_yield": -0.010,
                "roe_ttm": -0.02,
                "debt_to_equity": 1.20,
                "realized_vol_252": 0.45,
                "maxdd_252": -0.52,
                "sma200_gap": 0.04,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "share_count_change_12m": -0.010,
                "payout_ratio": 0.00,
                "earnings_yield": -0.010,
                "treasury_share_ratio": 0.000,
                "buyback_days_63": 18,
                "lot_size": 100,
            },
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("700.HK") == "00700"
    assert normalize_symbol("01299") == "01299"


def test_score_candidates_filters_dilution_and_negative_fcf_then_ranks_yield_quality():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00700"]
    assert "02020" not in set(ranked["symbol"])
    assert "09999" not in set(ranked["symbol"])
    assert {"capital_return_score", "quality_score", "risk_score", "trend_score"}.issubset(ranked.columns)


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.08,
        sector_cap=0.16,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "00700", "01299"]
    assert weights["00941"] == pytest.approx(0.08)
    assert weights["00700"] == pytest.approx(0.08)
    assert weights["01299"] == pytest.approx(0.08)
    assert weights["02800"] == pytest.approx(0.76)
    assert metadata["regime"] == "risk_on"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"01299"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk shareholder yield quality" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_shareholder_yield_quality.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
