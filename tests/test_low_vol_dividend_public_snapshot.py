from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from hk_equity_snapshot_pipelines import low_vol_dividend_public_snapshot as module
from hk_equity_snapshot_pipelines.low_vol_dividend_public_snapshot import (
    YahooFinanceHkProvider,
    _normalise_yfinance_history,
    _yfinance_hk_symbol,
    write_low_vol_dividend_public_factor_snapshot,
)


def _universe(path: Path) -> Path:
    pd.DataFrame(
        {
            "symbol": ["00700", "00005"],
            "sector": ["Technology", "Financials"],
            "eligible": [True, True],
            "lot_size": [100, 400],
        }
    ).to_csv(path, index=False)
    return path


def _price_frame(symbol: str) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=320, freq="B")
    base = 100 if symbol == "2800.HK" else 40 if symbol == "0700.HK" else 20
    return pd.DataFrame(
        {
            "Close": [base + index * 0.05 for index in range(len(dates))],
            "Volume": [2_000_000 + index * 1000 for index in range(len(dates))],
        },
        index=dates,
    )


class FakeTicker:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.dividends = pd.Series(
            [5.3, 4.5, 3.5],
            index=pd.to_datetime(["2026-05-15", "2025-05-15", "2024-05-15"]),
        )

    def get_info(self) -> dict[str, object]:
        return {
            "marketCap": 3_500_000_000_000,
            "dividendYield": 3.2,
            "payoutRatio": 0.42,
            "trailingPE": 18.5,
            "sector": "Financial Services",
            "currency": "HKD",
        }


class FakeDataFrameDividendTicker(FakeTicker):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.dividends = pd.DataFrame(
            {"Dividends": [5.3, 4.5, 3.5]},
            index=pd.to_datetime(["2026-05-15", "2025-05-15", "2024-05-15"]),
        )


def test_yfinance_hk_symbol_uses_padded_hk_ticker_format():
    assert _yfinance_hk_symbol("00005") == "0005.HK"
    assert _yfinance_hk_symbol("00700") == "0700.HK"
    assert _yfinance_hk_symbol("2800.HK") == "2800.HK"


def test_normalise_yfinance_history_accepts_flat_and_multiindex_columns():
    flat = _price_frame("0700.HK")
    normalised_flat = _normalise_yfinance_history(flat)

    multi = flat.copy()
    multi.columns = pd.MultiIndex.from_product([multi.columns, ["0700.HK"]])
    normalised_multi = _normalise_yfinance_history(multi)

    assert {"date", "close", "volume"} == set(normalised_flat.columns)
    assert len(normalised_flat) == len(flat)
    assert normalised_multi["close"].equals(normalised_flat["close"])


def test_write_public_factor_snapshot_uses_yfinance_symbol_format_and_runtime_labels(tmp_path):
    requested_symbols: list[str] = []

    def fake_download(symbol: str, **_: object) -> pd.DataFrame:
        requested_symbols.append(symbol)
        return _price_frame(symbol)

    provider = YahooFinanceHkProvider(download_fn=fake_download, ticker_factory=FakeTicker)

    payload = write_low_vol_dividend_public_factor_snapshot(
        universe_path=_universe(tmp_path / "universe.csv"),
        output_path=tmp_path / "factor_snapshot.csv",
        provider=provider,
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
    )

    assert payload["row_count"] == 2
    assert payload["source_name"] == "public_yfinance_staging"
    assert payload["source_quality"] == "public_yfinance_generated"
    assert payload["artifact_evidence_role"] == "runtime_artifact_input"
    assert payload["live_enablement_evidence_status"] == "runtime_artifact_evidence_ready_final_live_order_approval_pending"
    assert requested_symbols == ["2800.HK", "0700.HK", "0005.HK"]
    output = pd.read_csv(tmp_path / "factor_snapshot.csv")
    assert output["source_name"].eq("public_yfinance_staging").all()
    assert output["source_quality"].eq("public_yfinance_generated").all()
    assert output["market_cap_hkd"].min() > 0
    assert output["payout_ratio"].eq(0.42).all()


def test_public_provider_accepts_yfinance_dataframe_dividends():
    provider = YahooFinanceHkProvider(download_fn=lambda symbol, **_: _price_frame(symbol), ticker_factory=FakeDataFrameDividendTicker)

    dividends = provider.dividends("0005.HK")

    assert dividends[0] == {"ex_date": "2026-05-15", "amount": 5.3}


def test_public_factor_snapshot_research_defaults_are_marked_research_only(tmp_path):
    class MissingInfoTicker(FakeTicker):
        def get_info(self) -> dict[str, object]:
            return {}

    provider = YahooFinanceHkProvider(download_fn=lambda symbol, **_: _price_frame(symbol), ticker_factory=MissingInfoTicker)

    payload = write_low_vol_dividend_public_factor_snapshot(
        universe_path=_universe(tmp_path / "universe.csv"),
        output_path=tmp_path / "factor_snapshot.csv",
        provider=provider,
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
        allow_research_defaults=True,
    )

    assert payload["row_count"] == 2
    assert payload["source_quality"] == "public_yfinance_generated_with_research_defaults"
    assert payload["artifact_evidence_role"] == "research_smoke_input"
    assert payload["live_enablement_evidence_status"] == "research_smoke_only_not_runtime_artifact_evidence"


def test_public_cli_json_stdout_is_machine_readable(tmp_path, monkeypatch, capfd):
    class FakeProvider(YahooFinanceHkProvider):
        def __init__(self) -> None:
            super().__init__(download_fn=lambda symbol, **_: _price_frame(symbol), ticker_factory=FakeTicker)

    monkeypatch.setattr(module, "YahooFinanceHkProvider", FakeProvider)

    status = module.main(
        [
            "--universe",
            str(_universe(tmp_path / "universe.csv")),
            "--output",
            str(tmp_path / "factor_snapshot.csv"),
            "--as-of",
            "2026-06-03",
            "--history-start",
            "2025-01-01",
            "--json",
        ]
    )

    captured = capfd.readouterr()
    assert status == 0
    payload = json.loads(captured.out)
    assert payload["row_count"] == 2
    assert payload["source_name"] == "public_yfinance_staging"
