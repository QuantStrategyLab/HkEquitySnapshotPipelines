from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.low_vol_dividend_quality_strategy import (
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
            "close_hkd": 20.0,
            "adv20_hkd": 500_000_000,
            "market_cap_hkd": 200_000_000_000,
            "dividend_yield_net": 0.03,
            "dividend_stability_3y": 0.80,
            "earnings_positive": True,
            "payout_ratio": 0.50,
            "realized_vol_126": 0.18,
            "beta_252": 1.00,
            "maxdd_252": -0.20,
            "mom_6m": 0.02,
            "mom_12_1": 0.04,
            "sma200_gap": 0.02,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00941.HK",
            "sector": "Telecommunications",
            "close_hkd": 75.0,
            "adv20_hkd": 1_200_000_000,
            "market_cap_hkd": 1_500_000_000_000,
            "dividend_yield_net": 0.07,
            "dividend_stability_3y": 0.95,
            "earnings_positive": True,
            "payout_ratio": 0.62,
            "realized_vol_126": 0.12,
            "beta_252": 0.55,
            "maxdd_252": -0.10,
            "mom_6m": 0.10,
            "mom_12_1": 0.15,
            "sma200_gap": 0.08,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00002",
            "sector": "Utilities",
            "close_hkd": 45.0,
            "adv20_hkd": 250_000_000,
            "market_cap_hkd": 120_000_000_000,
            "dividend_yield_net": 0.055,
            "dividend_stability_3y": 0.90,
            "earnings_positive": True,
            "payout_ratio": 0.58,
            "realized_vol_126": 0.14,
            "beta_252": 0.50,
            "maxdd_252": -0.12,
            "mom_6m": 0.06,
            "mom_12_1": 0.08,
            "sma200_gap": 0.06,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00003",
            "sector": "Utilities",
            "close_hkd": 6.0,
            "adv20_hkd": 180_000_000,
            "market_cap_hkd": 70_000_000_000,
            "dividend_yield_net": 0.045,
            "dividend_stability_3y": 0.85,
            "earnings_positive": True,
            "payout_ratio": 0.55,
            "realized_vol_126": 0.16,
            "beta_252": 0.60,
            "maxdd_252": -0.15,
            "mom_6m": 0.04,
            "mom_12_1": 0.06,
            "sma200_gap": 0.04,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 1000,
        },
        {
            "symbol": "01378",
            "sector": "Materials",
            "close_hkd": 13.0,
            "adv20_hkd": 160_000_000,
            "market_cap_hkd": 90_000_000_000,
            "dividend_yield_net": 0.15,
            "dividend_stability_3y": 0.70,
            "earnings_positive": True,
            "payout_ratio": 1.20,
            "realized_vol_126": 0.40,
            "beta_252": 1.40,
            "maxdd_252": -0.35,
            "mom_6m": 0.25,
            "mom_12_1": 0.30,
            "sma200_gap": 0.15,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "09999",
            "sector": "Technology",
            "close_hkd": 80.0,
            "adv20_hkd": 500_000_000,
            "market_cap_hkd": 300_000_000_000,
            "dividend_yield_net": 0.03,
            "dividend_stability_3y": 0.40,
            "earnings_positive": False,
            "payout_ratio": 0.0,
            "realized_vol_126": 0.35,
            "beta_252": 1.20,
            "maxdd_252": -0.45,
            "mom_6m": 0.20,
            "mom_12_1": 0.30,
            "sma200_gap": 0.12,
            "suspension_days_63": 0,
            "eligible": True,
            "lot_size": 100,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("941.HK") == "00941"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_filters_yield_traps_and_ranks_quality_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00002"]
    assert "01378" not in set(ranked["symbol"])
    assert "09999" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "00941", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00003", "score"
    ].iloc[0]


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.10,
        sector_cap=0.20,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "00002", "00003"]
    assert weights["00941"] == pytest.approx(0.10)
    assert weights["00002"] == pytest.approx(0.10)
    assert weights["00003"] == pytest.approx(0.10)
    assert weights["02800"] == pytest.approx(0.70)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("00941", "00002", "00003")


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"00002"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk low vol dividend quality" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_low_vol_dividend_quality.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
