from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.quality_growth_low_volatility_strategy import (
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
                "close_hkd": 20.0,
                "adv20_hkd": 500_000_000,
                "market_cap_hkd": 200_000_000_000,
                "southbound_eligible": True,
                "roe": 0.10,
                "accruals_ratio": 0.02,
                "cash_flow_to_debt_ratio": 0.35,
                "growth_roa_to_pb": 0.08,
                "realized_vol_252": 0.18,
                "beta_252": 1.00,
                "maxdd_252": -0.20,
                "mom_6m": 0.02,
                "sma200_gap": 0.01,
                "suspension_days_63": 0,
                "eligible": True,
                "lot_size": 500,
            },
            {
                "symbol": "00700.HK",
                "sector": "Technology",
                "close_hkd": 390.0,
                "adv20_hkd": 1_800_000_000,
                "market_cap_hkd": 3_800_000_000_000,
                "southbound_eligible": True,
                "roe": 0.24,
                "accruals_ratio": -0.02,
                "cash_flow_to_debt_ratio": 0.85,
                "growth_roa_to_pb": 0.18,
                "realized_vol_252": 0.22,
                "beta_252": 0.95,
                "maxdd_252": -0.16,
                "mom_6m": 0.12,
                "sma200_gap": 0.08,
                "suspension_days_63": 0,
                "eligible": True,
                "lot_size": 100,
            },
            {
                "symbol": "01299",
                "sector": "Insurance",
                "close_hkd": 78.0,
                "adv20_hkd": 900_000_000,
                "market_cap_hkd": 850_000_000_000,
                "southbound_eligible": True,
                "roe": 0.16,
                "accruals_ratio": 0.01,
                "cash_flow_to_debt_ratio": 0.70,
                "growth_roa_to_pb": 0.14,
                "realized_vol_252": 0.16,
                "beta_252": 0.65,
                "maxdd_252": -0.12,
                "mom_6m": 0.08,
                "sma200_gap": 0.05,
                "suspension_days_63": 0,
                "eligible": True,
                "financials_sector_flag": True,
                "lot_size": 200,
            },
            {
                "symbol": "00941",
                "sector": "Telecommunications",
                "close_hkd": 75.0,
                "adv20_hkd": 1_200_000_000,
                "market_cap_hkd": 1_500_000_000_000,
                "southbound_eligible": True,
                "roe": 0.18,
                "accruals_ratio": 0.00,
                "cash_flow_to_debt_ratio": 0.90,
                "growth_roa_to_pb": 0.12,
                "realized_vol_252": 0.13,
                "beta_252": 0.55,
                "maxdd_252": -0.10,
                "mom_6m": 0.10,
                "sma200_gap": 0.07,
                "suspension_days_63": 0,
                "eligible": True,
                "lot_size": 500,
            },
            {
                "symbol": "09988",
                "sector": "Technology",
                "close_hkd": 82.0,
                "adv20_hkd": 700_000_000,
                "market_cap_hkd": 1_500_000_000_000,
                "southbound_eligible": True,
                "roe": 0.08,
                "accruals_ratio": 0.08,
                "cash_flow_to_debt_ratio": 0.10,
                "growth_roa_to_pb": 0.04,
                "realized_vol_252": 0.40,
                "beta_252": 1.25,
                "maxdd_252": -0.45,
                "mom_6m": 0.20,
                "sma200_gap": 0.12,
                "suspension_days_63": 0,
                "eligible": True,
                "lot_size": 100,
            },
            {
                "symbol": "02020",
                "sector": "Consumer Discretionary",
                "close_hkd": 16.0,
                "adv20_hkd": 120_000_000,
                "market_cap_hkd": 80_000_000_000,
                "southbound_eligible": False,
                "roe": 0.20,
                "accruals_ratio": -0.01,
                "cash_flow_to_debt_ratio": 0.75,
                "growth_roa_to_pb": 0.16,
                "realized_vol_252": 0.18,
                "beta_252": 0.80,
                "maxdd_252": -0.18,
                "mom_6m": 0.09,
                "sma200_gap": 0.05,
                "suspension_days_63": 0,
                "eligible": True,
                "lot_size": 500,
            },
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("700.HK") == "00700"
    assert normalize_symbol("01299") == "01299"


def test_score_candidates_filters_high_volatility_and_non_southbound_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00700"]
    assert "09988" not in set(ranked["symbol"])
    assert "02020" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "00941", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00700", "score"
    ].iloc[0]


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.10,
        sector_cap=0.20,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "00700", "01299"]
    assert weights["00941"] == pytest.approx(0.10)
    assert weights["01299"] == pytest.approx(0.10)
    assert weights["00700"] == pytest.approx(0.10)
    assert weights["02800"] == pytest.approx(0.70)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("00941", "00700", "01299")


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"01299"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk quality growth low volatility" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_quality_growth_low_volatility.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
