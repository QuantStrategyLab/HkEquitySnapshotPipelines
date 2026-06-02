from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.residual_momentum_quality_strategy import (
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
                "history_days": 252,
                "mom_3m": 0.04,
                "mom_6m": 0.08,
                "mom_12_1": 0.10,
                "residual_mom_12_1": 0.00,
                "industry_relative_mom_6m": 0.00,
                "rel_mom_6m_vs_benchmark": 0.00,
                "high_63_gap": -0.02,
                "high_252_gap": -0.04,
                "sma200_gap": 0.03,
                "realized_vol_126": 0.18,
                "beta_252": 1.00,
                "maxdd_252": -0.16,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 500,
            },
            {
                "symbol": "00700.HK",
                "sector": "Technology",
                "close_hkd": 390.0,
                "adv20_hkd": 2_500_000_000,
                "market_cap_hkd": 3_600_000_000_000,
                "history_days": 252,
                "mom_3m": 0.12,
                "mom_6m": 0.26,
                "mom_12_1": 0.38,
                "residual_mom_12_1": 0.24,
                "industry_relative_mom_6m": 0.12,
                "rel_mom_6m_vs_benchmark": 0.18,
                "high_63_gap": -0.01,
                "high_252_gap": -0.03,
                "sma200_gap": 0.16,
                "realized_vol_126": 0.34,
                "beta_252": 1.12,
                "maxdd_252": -0.18,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 100,
            },
            {
                "symbol": "09988",
                "sector": "Consumer Discretionary",
                "close_hkd": 83.0,
                "adv20_hkd": 1_800_000_000,
                "market_cap_hkd": 1_700_000_000_000,
                "history_days": 252,
                "mom_3m": 0.10,
                "mom_6m": 0.22,
                "mom_12_1": 0.32,
                "residual_mom_12_1": 0.21,
                "industry_relative_mom_6m": 0.10,
                "rel_mom_6m_vs_benchmark": 0.14,
                "high_63_gap": -0.02,
                "high_252_gap": -0.06,
                "sma200_gap": 0.12,
                "realized_vol_126": 0.36,
                "beta_252": 1.20,
                "maxdd_252": -0.22,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 100,
            },
            {
                "symbol": "03690",
                "sector": "Technology",
                "close_hkd": 112.0,
                "adv20_hkd": 900_000_000,
                "market_cap_hkd": 420_000_000_000,
                "history_days": 252,
                "mom_3m": 0.20,
                "mom_6m": 0.34,
                "mom_12_1": 0.48,
                "residual_mom_12_1": 0.18,
                "industry_relative_mom_6m": 0.05,
                "rel_mom_6m_vs_benchmark": 0.20,
                "high_63_gap": -0.03,
                "high_252_gap": -0.08,
                "sma200_gap": 0.18,
                "realized_vol_126": 0.62,
                "beta_252": 1.90,
                "maxdd_252": -0.40,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 100,
            },
            {
                "symbol": "00941",
                "sector": "Telecommunications",
                "close_hkd": 75.0,
                "adv20_hkd": 1_300_000_000,
                "market_cap_hkd": 1_500_000_000_000,
                "history_days": 252,
                "mom_3m": 0.06,
                "mom_6m": 0.14,
                "mom_12_1": 0.20,
                "residual_mom_12_1": 0.10,
                "industry_relative_mom_6m": 0.06,
                "rel_mom_6m_vs_benchmark": 0.07,
                "high_63_gap": -0.01,
                "high_252_gap": -0.03,
                "sma200_gap": 0.08,
                "realized_vol_126": 0.18,
                "beta_252": 0.72,
                "maxdd_252": -0.10,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 500,
            },
            {
                "symbol": "02020",
                "sector": "Consumer Discretionary",
                "close_hkd": 77.0,
                "adv20_hkd": 260_000_000,
                "market_cap_hkd": 190_000_000_000,
                "history_days": 252,
                "mom_3m": 0.03,
                "mom_6m": 0.05,
                "mom_12_1": 0.18,
                "residual_mom_12_1": -0.02,
                "industry_relative_mom_6m": 0.02,
                "rel_mom_6m_vs_benchmark": 0.01,
                "high_63_gap": -0.07,
                "high_252_gap": -0.18,
                "sma200_gap": -0.04,
                "realized_vol_126": 0.30,
                "beta_252": 1.10,
                "maxdd_252": -0.30,
                "suspension_days_63": 0,
                "eligible": True,
                "southbound_eligible": True,
                "corporate_action_flag": False,
                "lot_size": 1000,
            },
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("700.HK") == "00700"
    assert normalize_symbol("02020") == "02020"


def test_score_candidates_filters_high_beta_and_negative_residual_momentum():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00700", "09988"]
    assert "03690" not in set(ranked["symbol"])
    assert "02020" not in set(ranked["symbol"])
    assert {"raw_momentum_score", "residual_momentum_score", "trend_quality_score", "risk_control_score"}.issubset(
        ranked.columns
    )


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.10,
        sector_cap=0.20,
    )

    assert ranked["symbol"].tolist()[:3] == ["00700", "09988", "00941"]
    assert weights["00700"] == pytest.approx(0.10)
    assert weights["09988"] == pytest.approx(0.10)
    assert weights["00941"] == pytest.approx(0.10)
    assert weights["02800"] == pytest.approx(0.70)
    assert metadata["regime"] == "risk_on"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"00941"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk residual momentum quality" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_residual_momentum_quality.factor_snapshot.v1"
    assert "00700" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
