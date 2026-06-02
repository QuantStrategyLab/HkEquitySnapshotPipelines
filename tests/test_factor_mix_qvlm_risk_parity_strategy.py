from __future__ import annotations

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.factor_mix_qvlm_risk_parity_strategy import (
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
        "quality_score": 0.0,
        "value_score": 0.0,
        "momentum_score": 0.0,
        "low_volatility_score": 0.0,
        "quality_factor_vol_126": 0.10,
        "value_factor_vol_126": 0.18,
        "momentum_factor_vol_126": 0.26,
        "low_vol_factor_vol_126": 0.09,
        "realized_vol_252": 0.20,
        "beta_252": 0.80,
        "maxdd_252": -0.15,
        "sma200_gap": 0.05,
        "suspension_days_63": 0,
        "eligible": True,
        "southbound_eligible": True,
        "lot_size": 500,
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
                close_hkd=20.8,
                adv20_hkd=1_200_000_000,
                market_cap_hkd=350_000_000_000,
                beta_252=1.0,
                sma200_gap=0.02,
            ),
            _row(
                "00941.HK",
                "Telecommunications",
                close_hkd=75.0,
                adv20_hkd=1_300_000_000,
                market_cap_hkd=1_500_000_000_000,
                quality_score=1.4,
                value_score=1.0,
                momentum_score=0.8,
                low_volatility_score=1.3,
                realized_vol_252=0.16,
                beta_252=0.55,
                maxdd_252=-0.10,
                sma200_gap=0.10,
            ),
            _row(
                "00002",
                "Utilities",
                close_hkd=45.0,
                adv20_hkd=250_000_000,
                market_cap_hkd=120_000_000_000,
                quality_score=0.8,
                value_score=1.2,
                momentum_score=0.4,
                low_volatility_score=1.5,
                realized_vol_252=0.14,
                beta_252=0.50,
                maxdd_252=-0.12,
                sma200_gap=0.07,
            ),
            _row(
                "03968",
                "Financials",
                close_hkd=44.0,
                adv20_hkd=950_000_000,
                market_cap_hkd=780_000_000_000,
                quality_score=1.0,
                value_score=1.5,
                momentum_score=0.5,
                low_volatility_score=0.6,
                realized_vol_252=0.22,
                beta_252=0.85,
                maxdd_252=-0.18,
                sma200_gap=0.08,
            ),
            _row(
                "01378",
                "Materials",
                close_hkd=13.0,
                adv20_hkd=160_000_000,
                market_cap_hkd=90_000_000_000,
                quality_score=-0.4,
                value_score=0.2,
                momentum_score=-1.0,
                low_volatility_score=-1.0,
                realized_vol_252=0.42,
                beta_252=1.35,
                maxdd_252=-0.50,
                sma200_gap=-0.12,
            ),
        ]
    )


def test_normalize_symbol_preserves_hk_leading_zeroes():
    assert normalize_symbol("941.HK") == "00941"
    assert normalize_symbol("00002") == "00002"


def test_score_candidates_ranks_risk_parity_factor_mix_names():
    ranked = score_candidates(_snapshot())

    assert ranked["symbol"].tolist()[:2] == ["00941", "00002"]
    assert "01378" not in set(ranked["symbol"])
    assert "risk_parity_low_volatility_weight" in ranked.columns
    assert ranked["risk_parity_low_volatility_weight"].iloc[0] > ranked["risk_parity_momentum_weight"].iloc[0]

    weight_columns = [column for column in ranked.columns if column.startswith("risk_parity_")]
    assert ranked.loc[0, weight_columns].sum() == pytest.approx(1.0)


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
    assert "hk factor mix qvlm risk parity" in signal_desc
    assert "regime=risk_on" in status_desc
    assert diagnostics["signal_source"] == "factor_snapshot"
    assert diagnostics["snapshot_contract_version"] == "hk_factor_mix_qvlm_risk_parity.factor_snapshot.v1"
    assert "00941" in diagnostics["managed_symbols"]


def test_extract_managed_symbols_includes_safe_haven_once():
    symbols = extract_managed_symbols(_snapshot())

    assert symbols[-1] == "02800"
    assert symbols.count("02800") == 1


def test_score_candidates_requires_factor_columns():
    snapshot = _snapshot().drop(columns=[next(iter(REQUIRED_FACTOR_COLUMNS - {"symbol"}))])

    with pytest.raises(ValueError, match="factor_snapshot missing required columns"):
        score_candidates(snapshot)
