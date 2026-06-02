from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.central_soe_value_quality_select_strategy import (
    REQUIRED_FACTOR_COLUMNS,
    build_target_weights,
    compute_signals,
    extract_managed_symbols,
    normalize_symbol,
    score_candidates,
)


def _row(symbol: str, sector: str, **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "symbol": symbol,
        "sector": sector,
        "close_hkd": 20.0,
        "adv20_hkd": 100_000_000,
        "market_cap_hkd": 20_000_000_000,
        "central_soe_flag": True,
        "government_largest_shareholder": True,
        "government_ownership_pct": 0.55,
        "government_shareholder_type": "SASAC central SOE",
        "value_score": 0.0,
        "quality_score": 0.0,
        "low_volatility_score": 0.0,
        "momentum_score": 0.0,
        "dividend_yield_net": 0.04,
        "earnings_yield": 0.08,
        "book_to_price": 0.70,
        "roe_ttm": 0.10,
        "debt_to_equity": 0.40,
        "realized_vol_252": 0.20,
        "beta_252": 0.80,
        "maxdd_252": -0.15,
        "sma200_gap": 0.05,
        "suspension_days_63": 0,
        "eligible": True,
        "southbound_eligible": True,
        "lot_size": 500,
        "policy_event_risk_flag": False,
        "corporate_action_flag": False,
    }
    row.update(overrides)
    return row


def _snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _row(
                "02800",
                "ETF",
                central_soe_flag=False,
                government_largest_shareholder=False,
                government_ownership_pct=0.0,
                government_shareholder_type="none",
            ),
            _row(
                "00941.HK",
                "Telecommunications",
                adv20_hkd=1_300_000_000,
                market_cap_hkd=1_500_000_000_000,
                government_ownership_pct=0.72,
                value_score=1.2,
                quality_score=1.4,
                low_volatility_score=1.3,
                momentum_score=0.8,
                dividend_yield_net=0.060,
                earnings_yield=0.095,
                book_to_price=0.72,
                roe_ttm=0.13,
                debt_to_equity=0.18,
                realized_vol_252=0.16,
                beta_252=0.55,
                maxdd_252=-0.10,
                sma200_gap=0.10,
            ),
            _row(
                "01088",
                "Energy",
                adv20_hkd=420_000_000,
                market_cap_hkd=360_000_000_000,
                government_ownership_pct=0.69,
                value_score=1.1,
                quality_score=1.1,
                low_volatility_score=1.1,
                momentum_score=0.4,
                dividend_yield_net=0.075,
                earnings_yield=0.100,
                book_to_price=0.80,
                roe_ttm=0.12,
                debt_to_equity=0.20,
                realized_vol_252=0.18,
                beta_252=0.70,
                maxdd_252=-0.14,
                sma200_gap=0.06,
            ),
            _row(
                "00883",
                "Energy",
                adv20_hkd=900_000_000,
                market_cap_hkd=820_000_000_000,
                government_ownership_pct=0.64,
                value_score=1.4,
                quality_score=1.0,
                low_volatility_score=0.8,
                momentum_score=0.7,
                dividend_yield_net=0.055,
                earnings_yield=0.105,
                book_to_price=0.85,
                roe_ttm=0.11,
                debt_to_equity=0.32,
                realized_vol_252=0.23,
                beta_252=0.88,
                maxdd_252=-0.18,
                sma200_gap=0.08,
            ),
            _row(
                "00700",
                "Technology",
                central_soe_flag=False,
                government_largest_shareholder=False,
                government_ownership_pct=0.0,
                value_score=1.6,
                quality_score=2.0,
                low_volatility_score=1.6,
                momentum_score=1.8,
            ),
            _row(
                "00386",
                "Energy",
                value_score=1.0,
                quality_score=0.4,
                low_volatility_score=0.2,
                policy_event_risk_flag=True,
            ),
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("941.HK") == "00941"
    assert normalize_symbol("01088") == "01088"


def test_score_candidates_filters_to_central_soe_value_quality_universe():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:3] == ["00941", "01088", "00883"]
    assert "00700" not in set(ranked["symbol"])
    assert "00386" not in set(ranked["symbol"])
    assert ranked["central_soe_flag"].all()
    assert "government_ownership_pct" in ranked.columns
    assert "value_factor_score" in ranked.columns


def test_build_target_weights_uses_sector_cap_and_safe_haven_remainder():
    weights, ranked, metadata = build_target_weights(
        _snapshot(),
        holdings_count=3,
        single_name_cap=0.08,
        sector_cap=0.16,
    )

    assert ranked["symbol"].tolist()[:3] == ["00941", "01088", "00883"]
    assert weights["00941"] == pytest.approx(0.08)
    assert weights["01088"] == pytest.approx(0.08)
    assert weights["00883"] == pytest.approx(0.08)
    assert weights["02800"] == pytest.approx(0.76)
    assert metadata["regime"] == "risk_on"
    assert metadata["min_government_ownership_pct"] == pytest.approx(0.10)


def test_compute_signals_returns_snapshot_metadata():
    weights, signal_desc, is_hard_defense, status_desc, diagnostics = compute_signals(
        _snapshot(),
        current_holdings={"01088"},
        holdings_count=2,
    )

    assert weights
    assert is_hard_defense is False
    assert "hk central soe value quality select" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_central_soe_value_quality_select.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
