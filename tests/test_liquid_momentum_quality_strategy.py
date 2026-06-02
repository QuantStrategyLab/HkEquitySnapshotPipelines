from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.liquid_momentum_quality_strategy import (
    REQUIRED_FEATURE_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot(*, benchmark_trend: float = 0.05) -> pd.DataFrame:
    rows = [
        {
            "symbol": "02800",
            "sector": "ETF",
            "close_hkd": 20.0,
            "adv20_hkd": 900_000_000,
            "market_cap_hkd": 200_000_000_000,
            "history_days": 300,
            "mom_3m": 0.04,
            "mom_6m": 0.05,
            "mom_12_1": 0.08,
            "rel_mom_6m_vs_benchmark": 0.0,
            "high_252_gap": -0.04,
            "sma200_gap": benchmark_trend,
            "vol_63": 0.018,
            "maxdd_126": -0.12,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00700.HK",
            "sector": "Technology",
            "close_hkd": 420.0,
            "adv20_hkd": 4_000_000_000,
            "market_cap_hkd": 3_800_000_000_000,
            "history_days": 300,
            "mom_3m": 0.18,
            "mom_6m": 0.32,
            "mom_12_1": 0.45,
            "rel_mom_6m_vs_benchmark": 0.27,
            "high_252_gap": -0.01,
            "sma200_gap": 0.16,
            "vol_63": 0.030,
            "maxdd_126": -0.14,
            "eligible": True,
            "lot_size": 100,
        },
        {
            "symbol": "00941",
            "sector": "Telecommunications",
            "close_hkd": 75.0,
            "adv20_hkd": 1_200_000_000,
            "market_cap_hkd": 1_500_000_000_000,
            "history_days": 300,
            "mom_3m": 0.10,
            "mom_6m": 0.20,
            "mom_12_1": 0.28,
            "rel_mom_6m_vs_benchmark": 0.15,
            "high_252_gap": -0.02,
            "sma200_gap": 0.11,
            "vol_63": 0.016,
            "maxdd_126": -0.08,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00002",
            "sector": "Utilities",
            "close_hkd": 45.0,
            "adv20_hkd": 250_000_000,
            "market_cap_hkd": 120_000_000_000,
            "history_days": 300,
            "mom_3m": 0.07,
            "mom_6m": 0.12,
            "mom_12_1": 0.18,
            "rel_mom_6m_vs_benchmark": 0.07,
            "high_252_gap": -0.05,
            "sma200_gap": 0.08,
            "vol_63": 0.014,
            "maxdd_126": -0.09,
            "eligible": True,
            "lot_size": 500,
        },
        {
            "symbol": "00003",
            "sector": "Utilities",
            "close_hkd": 6.0,
            "adv20_hkd": 180_000_000,
            "market_cap_hkd": 70_000_000_000,
            "history_days": 300,
            "mom_3m": 0.06,
            "mom_6m": 0.09,
            "mom_12_1": 0.16,
            "rel_mom_6m_vs_benchmark": 0.04,
            "high_252_gap": -0.06,
            "sma200_gap": 0.06,
            "vol_63": 0.015,
            "maxdd_126": -0.11,
            "eligible": True,
            "lot_size": 1000,
        },
        {
            "symbol": "09999",
            "sector": "Technology",
            "close_hkd": 80.0,
            "adv20_hkd": 600_000_000,
            "market_cap_hkd": 300_000_000_000,
            "history_days": 300,
            "mom_3m": 0.30,
            "mom_6m": 0.42,
            "mom_12_1": 0.60,
            "rel_mom_6m_vs_benchmark": 0.37,
            "high_252_gap": -0.01,
            "sma200_gap": 0.22,
            "vol_63": 0.120,
            "maxdd_126": -0.55,
            "eligible": True,
            "lot_size": 100,
        },
        {
            "symbol": "01378",
            "sector": "Materials",
            "close_hkd": 13.0,
            "adv20_hkd": 20_000_000,
            "market_cap_hkd": 90_000_000_000,
            "history_days": 300,
            "mom_3m": 0.12,
            "mom_6m": 0.25,
            "mom_12_1": 0.31,
            "rel_mom_6m_vs_benchmark": 0.20,
            "high_252_gap": -0.03,
            "sma200_gap": 0.10,
            "vol_63": 0.035,
            "maxdd_126": -0.18,
            "eligible": True,
            "lot_size": 500,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("700.HK") == "00700"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_filters_illiquid_and_high_volatility_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00700"]
    assert "09999" not in set(ranked["symbol"])
    assert "01378" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "00941", "risk_adjusted_mom_6m"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00002", "risk_adjusted_mom_6m"
    ].iloc[0]


def test_score_candidates_uses_optional_short_horizon_cth_gap():
    snapshot = _snapshot()
    snapshot["high_63_gap"] = [-0.03, -0.08, -0.01, -0.05, -0.06, -0.04, -0.03]

    ranked = score_candidates(snapshot)

    assert "high_63_gap" in ranked.columns
    assert "cth_combo_score" in ranked.columns
    assert ranked.loc[ranked["symbol"] == "00941", "cth_combo_score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00700", "cth_combo_score"
    ].iloc[0]


def test_build_target_weights_applies_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=4,
        single_name_cap=0.12,
        sector_cap=0.24,
    )

    assert ranked["symbol"].tolist()[:4] == ["00941", "00700", "00002", "00003"]
    assert weights["00941"] == pytest.approx(0.12)
    assert weights["00700"] == pytest.approx(0.12)
    assert weights["00002"] == pytest.approx(0.12)
    assert weights["00003"] == pytest.approx(0.12)
    assert weights["02800"] == pytest.approx(0.52)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("00941", "00700", "00002", "00003")


def test_build_target_weights_goes_defensive_when_benchmark_trend_is_down():
    snapshot = _snapshot(benchmark_trend=-0.05)
    snapshot.loc[snapshot["symbol"] != "02800", "sma200_gap"] = -0.01

    weights, _ranked, metadata = build_target_weights(
        snapshot,
        holdings_count=4,
    )

    assert weights == {"02800": 1.0}
    assert metadata["regime"] == "hard_defense"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"00700"},
        holdings_count=3,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk liquid momentum quality" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "feature_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_liquid_momentum_quality.feature_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1
    assert "00700" in symbols


def test_score_candidates_requires_feature_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FEATURE_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="feature_snapshot missing required columns"):
        score_candidates(snapshot)
