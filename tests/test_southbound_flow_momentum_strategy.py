from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.southbound_flow_momentum_strategy import (
    REQUIRED_FLOW_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _snapshot(*, trend: float = 0.10) -> pd.DataFrame:
    rows = [
        {
            "symbol": "02800",
            "sector": "ETF",
            "close_hkd": 20.8,
            "adv20_hkd": 1_200_000_000,
            "market_cap_hkd": 350_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": 50_000_000,
            "southbound_net_buy_hkd_20d": 200_000_000,
            "southbound_net_buy_hkd_60d": 500_000_000,
            "southbound_turnover_share_20d": 0.05,
            "southbound_holding_pct": 0.02,
            "southbound_holding_pct_change_20d": 0.001,
            "southbound_holding_pct_change_60d": 0.002,
            "flow_zscore_20d": 0.20,
            "flow_persistence_score": 0.10,
            "mom_6m": 0.03,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "00700.HK",
            "sector": "Technology",
            "close_hkd": 420.0,
            "adv20_hkd": 4_200_000_000,
            "market_cap_hkd": 3_800_000_000_000,
            "lot_size": 100,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": 1_500_000_000,
            "southbound_net_buy_hkd_20d": 7_200_000_000,
            "southbound_net_buy_hkd_60d": 16_000_000_000,
            "southbound_turnover_share_20d": 0.18,
            "southbound_holding_pct": 0.085,
            "southbound_holding_pct_change_20d": 0.012,
            "southbound_holding_pct_change_60d": 0.030,
            "flow_zscore_20d": 2.80,
            "flow_persistence_score": 0.92,
            "mom_6m": 0.32,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "00941",
            "sector": "Telecommunications",
            "close_hkd": 75.0,
            "adv20_hkd": 1_300_000_000,
            "market_cap_hkd": 1_500_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": 900_000_000,
            "southbound_net_buy_hkd_20d": 4_300_000_000,
            "southbound_net_buy_hkd_60d": 9_500_000_000,
            "southbound_turnover_share_20d": 0.22,
            "southbound_holding_pct": 0.115,
            "southbound_holding_pct_change_20d": 0.010,
            "southbound_holding_pct_change_60d": 0.026,
            "flow_zscore_20d": 2.20,
            "flow_persistence_score": 0.88,
            "mom_6m": 0.20,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "03690",
            "sector": "Technology",
            "close_hkd": 130.0,
            "adv20_hkd": 900_000_000,
            "market_cap_hkd": 980_000_000_000,
            "lot_size": 100,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": 700_000_000,
            "southbound_net_buy_hkd_20d": 3_300_000_000,
            "southbound_net_buy_hkd_60d": 7_600_000_000,
            "southbound_turnover_share_20d": 0.16,
            "southbound_holding_pct": 0.073,
            "southbound_holding_pct_change_20d": 0.009,
            "southbound_holding_pct_change_60d": 0.022,
            "flow_zscore_20d": 1.80,
            "flow_persistence_score": 0.80,
            "mom_6m": 0.25,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "00002",
            "sector": "Utilities",
            "close_hkd": 45.0,
            "adv20_hkd": 260_000_000,
            "market_cap_hkd": 120_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": 210_000_000,
            "southbound_net_buy_hkd_20d": 1_300_000_000,
            "southbound_net_buy_hkd_60d": 3_600_000_000,
            "southbound_turnover_share_20d": 0.14,
            "southbound_holding_pct": 0.092,
            "southbound_holding_pct_change_20d": 0.006,
            "southbound_holding_pct_change_60d": 0.016,
            "flow_zscore_20d": 1.25,
            "flow_persistence_score": 0.68,
            "mom_6m": 0.12,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "01299",
            "sector": "Financials",
            "close_hkd": 52.0,
            "adv20_hkd": 600_000_000,
            "market_cap_hkd": 900_000_000_000,
            "lot_size": 200,
            "eligible": True,
            "southbound_eligible": True,
            "southbound_net_buy_hkd_5d": -120_000_000,
            "southbound_net_buy_hkd_20d": -500_000_000,
            "southbound_net_buy_hkd_60d": -900_000_000,
            "southbound_turnover_share_20d": 0.07,
            "southbound_holding_pct": 0.035,
            "southbound_holding_pct_change_20d": -0.002,
            "southbound_holding_pct_change_60d": -0.006,
            "flow_zscore_20d": -0.80,
            "flow_persistence_score": -0.20,
            "mom_6m": 0.06,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
        {
            "symbol": "01378",
            "sector": "Materials",
            "close_hkd": 13.0,
            "adv20_hkd": 180_000_000,
            "market_cap_hkd": 90_000_000_000,
            "lot_size": 500,
            "eligible": True,
            "southbound_eligible": False,
            "southbound_net_buy_hkd_5d": 220_000_000,
            "southbound_net_buy_hkd_20d": 800_000_000,
            "southbound_net_buy_hkd_60d": 1_500_000_000,
            "southbound_turnover_share_20d": 0.12,
            "southbound_holding_pct": 0.040,
            "southbound_holding_pct_change_20d": 0.005,
            "southbound_holding_pct_change_60d": 0.010,
            "flow_zscore_20d": 0.90,
            "flow_persistence_score": 0.55,
            "mom_6m": 0.22,
            "sma200_gap": trend,
            "suspension_days_63": 0,
            "holiday_adjusted_flow_flag": False,
            "corporate_action_flag": False,
        },
    ]
    return pd.DataFrame(rows)


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("700.HK") == "00700"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_filters_flow_reversal_and_non_connect_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:3] == ["00700", "00941", "03690"]
    assert "01299" not in set(ranked["symbol"])
    assert "01378" not in set(ranked["symbol"])
    assert ranked.loc[ranked["symbol"] == "00700", "score"].iloc[0] > ranked.loc[
        ranked["symbol"] == "00941", "score"
    ].iloc[0]


def test_build_target_weights_applies_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=4,
        single_name_cap=0.12,
        sector_cap=0.24,
    )

    assert ranked["symbol"].tolist()[:4] == ["00700", "00941", "03690", "00002"]
    assert weights["00700"] == pytest.approx(0.12)
    assert weights["00941"] == pytest.approx(0.12)
    assert weights["03690"] == pytest.approx(0.12)
    assert weights["00002"] == pytest.approx(0.12)
    assert weights["02800"] == pytest.approx(0.52)
    assert metadata["regime"] == "risk_on"
    assert metadata["selected_symbols"] == ("00700", "00941", "03690", "00002")


def test_build_target_weights_goes_defensive_when_no_flow_candidate_survives():
    snapshot = _snapshot(trend=-0.05)

    weights, _ranked, metadata = build_target_weights(snapshot, holdings_count=4)

    assert weights == {"02800": 1.0}
    assert metadata["regime"] == "hard_defense"


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"00941"},
        holdings_count=3,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk southbound flow momentum" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "flow_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_southbound_flow_momentum.flow_snapshot.v1"
    assert "00700" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1
    assert "00700" in symbols


def test_score_candidates_requires_flow_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FLOW_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="flow_snapshot missing required columns"):
        score_candidates(snapshot)
