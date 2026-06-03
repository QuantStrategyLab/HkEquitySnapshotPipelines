from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from hk_equity_snapshot_pipelines.low_vol_dividend_longbridge_snapshot import (
    build_low_vol_dividend_factor_snapshot_from_provider,
    write_low_vol_dividend_longbridge_factor_snapshot,
)


class FakeProvider:
    def __init__(self) -> None:
        dates = pd.date_range("2025-01-01", periods=320, freq="B")
        self._benchmark = pd.DataFrame({"date": dates, "close": [100 + i * 0.02 for i in range(len(dates))], "volume": 10_000_000})

    def price_history(self, symbol: str, *, start: date, end: date) -> pd.DataFrame:
        dates = pd.date_range("2025-01-01", periods=320, freq="B")
        if symbol == "2800.HK":
            return self._benchmark
        base = 40 if symbol == "700.HK" else 20
        return pd.DataFrame(
            {
                "date": dates,
                "close": [base + i * 0.05 for i in range(len(dates))],
                "volume": [2_000_000 + i * 1000 for i in range(len(dates))],
            }
        )

    def dividends(self, symbol: str) -> list[dict[str, object]]:
        return [
            {"ex_date": "2026-05-15", "desc": "Dividend: HKD 5.3/share"},
            {"ex_date": "2025-05-15", "desc": "Dividend: HKD 4.5/share"},
            {"ex_date": "2024-05-15", "desc": "Dividend: HKD 3.5/share"},
        ]

    def valuation(self, symbol: str) -> dict[str, object]:
        return {
            "metrics": {
                "market_cap": "3500000000000",
                "pe": "18.5",
                "div_payout_ratio": "0.42",
            }
        }


def _universe(path: Path, *, include_required_metadata: bool = False) -> Path:
    payload = {"symbol": ["00700", "00005"], "sector": ["Technology", "Financials"], "eligible": [True, True]}
    if include_required_metadata:
        payload.update({"market_cap_hkd": [3_500_000_000_000, 900_000_000_000], "payout_ratio": [0.42, 0.5]})
    pd.DataFrame(payload).to_csv(path, index=False)
    return path


def test_build_longbridge_factor_snapshot_from_fake_provider(tmp_path):
    snapshot, diagnostics = build_low_vol_dividend_factor_snapshot_from_provider(
        universe_path=_universe(tmp_path / "universe.csv"),
        provider=FakeProvider(),
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
    )

    assert diagnostics.row_count == 2
    assert diagnostics.symbols_failed == 0
    assert list(snapshot["symbol"]) == ["00700", "00005"]
    assert set(snapshot["sector"]) == {"Technology", "Financials"}
    assert snapshot["close_hkd"].min() > 0
    assert snapshot["adv20_hkd"].min() > 0
    assert snapshot["market_cap_hkd"].min() > 0
    assert snapshot["dividend_yield_net"].min() > 0
    assert snapshot["dividend_stability_3y"].min() > 0
    assert snapshot["source_quality"].eq("longbridge_openapi_generated").all()
    assert snapshot["artifact_evidence_role"].eq("runtime_artifact_input").all()
    assert snapshot["live_order_approval_status"].eq("pending_backtest_dry_run_and_operator_approval").all()
    assert snapshot["requires_operator_audit"].eq(True).all()


def test_build_longbridge_factor_snapshot_rejects_missing_non_price_fields_without_defaults(tmp_path):
    class MissingValuationProvider(FakeProvider):
        def valuation(self, symbol: str) -> dict[str, object]:
            return {}

    snapshot, diagnostics = build_low_vol_dividend_factor_snapshot_from_provider(
        universe_path=_universe(tmp_path / "universe.csv"),
        provider=MissingValuationProvider(),
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
    )

    assert snapshot.empty
    assert diagnostics.symbols_failed == 2
    assert "market_cap_hkd" in diagnostics.failed_symbols[0]


def test_build_longbridge_factor_snapshot_allows_research_defaults_for_staging(tmp_path):
    class MissingValuationProvider(FakeProvider):
        def valuation(self, symbol: str) -> dict[str, object]:
            return {}

    snapshot, diagnostics = build_low_vol_dividend_factor_snapshot_from_provider(
        universe_path=_universe(tmp_path / "universe.csv"),
        provider=MissingValuationProvider(),
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
        allow_research_defaults=True,
    )

    assert diagnostics.row_count == 2
    assert diagnostics.allow_research_defaults is True
    assert diagnostics.source_quality == "longbridge_openapi_generated_with_research_defaults"
    assert snapshot["market_cap_hkd"].eq(0.0).all()
    assert snapshot["payout_ratio"].eq(0.55).all()
    assert snapshot["artifact_evidence_role"].eq("research_smoke_input").all()


def test_write_longbridge_factor_snapshot_outputs_csv(tmp_path):
    payload = write_low_vol_dividend_longbridge_factor_snapshot(
        universe_path=_universe(tmp_path / "universe.csv"),
        output_path=tmp_path / "factor_snapshot.csv",
        provider=FakeProvider(),
        as_of=date(2026, 6, 3),
        history_start=date(2025, 1, 1),
    )

    assert payload["row_count"] == 2
    assert payload["source_quality"] == "longbridge_openapi_generated"
    assert payload["artifact_evidence_role"] == "runtime_artifact_input"
    assert payload["live_enablement_evidence_status"] == "runtime_artifact_evidence_ready_final_live_order_approval_pending"
    assert payload["live_order_approval_status"] == "pending_backtest_dry_run_and_operator_approval"
    output = pd.read_csv(tmp_path / "factor_snapshot.csv")
    assert len(output) == 2


def test_build_longbridge_factor_snapshot_requires_symbol_column(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"ticker": ["00700"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="universe CSV must contain symbol"):
        build_low_vol_dividend_factor_snapshot_from_provider(
            universe_path=path,
            provider=FakeProvider(),
            as_of=date(2026, 6, 3),
            history_start=date(2025, 1, 1),
        )


def test_main_json_stdout_stays_machine_readable_when_provider_writes_stdout(tmp_path, monkeypatch, capsys):
    import json

    from hk_equity_snapshot_pipelines import low_vol_dividend_longbridge_snapshot as module

    class NoisyProvider(FakeProvider):
        def __init__(self, *, app_key: str, app_secret: str, access_token: str) -> None:
            print("LongBridge SDK stdout diagnostic")
            super().__init__()

    monkeypatch.setattr(module, "LongBridgeOpenApiProvider", NoisyProvider)

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
            "--app-key",
            "dummy-app-key",
            "--app-secret",
            "dummy-app-secret",
            "--access-token",
            "dummy-access-token",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert status == 0
    payload = json.loads(captured.out)
    assert payload["row_count"] == 2
    assert "LongBridge SDK stdout diagnostic" not in captured.out
    assert "LongBridge SDK stdout diagnostic" in captured.err
