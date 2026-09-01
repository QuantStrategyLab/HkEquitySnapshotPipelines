from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

import hk_equity_snapshot_pipelines.snapshot_proxy_backtest as proxy_backtest
from hk_equity_snapshot_pipelines.snapshot_proxy_backtest import (
    DEFAULT_SYMBOLS,
    PROXY_BACKTEST_VERSION,
    PROXY_RESEARCH_STATUS,
    build_proxy_cycle_backtest,
    generate_synthetic_price_history,
    run_proxy_cycle_backtest,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "research_hk_snapshot_proxy_cycle_backtest.py"


def test_proxy_cycle_backtest_summarizes_long_medium_short_periods():
    prices, meta = generate_synthetic_price_history(
        symbols=DEFAULT_SYMBOLS[:8],
        start="2020-01-01",
        end="2026-06-03",
    )
    meta.update(
        {
            "price_source": "fake_real_price_history",
            "source_kind": "real",
            "research_only": False,
            "reason_code": "PROXY_RESEARCH_ONLY",
        }
    )

    payload = build_proxy_cycle_backtest(prices=prices, price_meta=meta, top_n=3, cost_bps=20.0)

    assert payload["backtest_version"] == PROXY_BACKTEST_VERSION
    assert payload["source_kind"] == "real"
    assert payload["research_only"] is True
    assert payload["promotion_eligible"] is False
    assert payload["reason_code"] == "PROXY_RESEARCH_ONLY"
    assert payload["research_status"] == PROXY_RESEARCH_STATUS
    assert payload["config"]["max_drawdown_gate"] == 0.30
    assert set(payload["periods"]) == {"long", "medium", "short"}
    assert payload["ranking"]
    assert len(payload["profiles"]) == 13
    for row in payload["profiles"]:
        assert set(row["metrics"]) == {"long", "medium", "short"}
        assert set(row["drawdown_30_pass_by_period"]) == {"long", "medium", "short"}
        assert "promotion_scope" in row
        assert "proxy_kind" in row


def test_run_proxy_cycle_backtest_supports_synthetic_source():
    payload = run_proxy_cycle_backtest(
        price_source="synthetic",
        research_only=True,
        symbols=DEFAULT_SYMBOLS[:4],
        start="2024-01-01",
        end="2026-06-03",
        top_n=2,
    )

    assert payload["price_meta"]["price_source"] == "deterministic_synthetic_price_history"
    assert payload["source_kind"] == "synthetic"
    assert payload["fallback_used"] is False
    assert payload["research_only"] is True
    assert payload["promotion_eligible"] is False
    assert payload["reason_code"] == "SYNTHETIC_RESEARCH_ONLY"
    assert all(row["research_recommendation"] == "synthetic_research_only_not_promotion_eligible" for row in payload["profiles"])
    assert payload["data"]["trading_days"] > 500
    assert payload["ranking"][0]["proxy_rank"] == 1
    assert any(row["profile"] == "hk_low_vol_dividend_quality_snapshot" for row in payload["profiles"])


def test_proxy_cycle_backtest_script_json_synthetic():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--price-source",
            "synthetic",
            "--research-only",
            "--start",
            "2024-01-01",
            "--end",
            "2026-06-03",
            "--symbol",
            "0005.HK",
            "--symbol",
            "0700.HK",
            "--symbol",
            "0941.HK",
            "--symbol",
            "1299.HK",
            "--top-n",
            "2",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["backtest_version"] == PROXY_BACKTEST_VERSION
    assert payload["research_status"] == PROXY_RESEARCH_STATUS
    assert payload["periods"]["short"]["end"] == "2026-06-03"
    assert payload["price_meta"]["price_source"] == "deterministic_synthetic_price_history"
    assert payload["source_kind"] == "synthetic"
    assert payload["fallback_used"] is False
    assert payload["research_only"] is True
    assert payload["promotion_eligible"] is False


def test_run_proxy_cycle_backtest_parks_when_yahoo_download_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    def fail_downloader(**_: object):
        raise RuntimeError("fake downloader failure")

    monkeypatch.setattr(proxy_backtest, "download_yahoo_price_history", fail_downloader)

    payload = run_proxy_cycle_backtest(
        price_source="yahoo",
        symbols=DEFAULT_SYMBOLS[:4],
        start="2024-01-01",
        end="2026-06-03",
        cache_dir=tmp_path,
    )

    assert payload == {
        "backtest_version": PROXY_BACKTEST_VERSION,
        "run_status": "PARKED",
        "source_kind": "unavailable",
        "fallback_used": False,
        "research_only": True,
        "promotion_eligible": False,
        "reason_code": "SOURCE_DOWNLOAD_FAILED",
    }


def test_run_proxy_cycle_backtest_never_falls_back_after_provider_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    def fail_downloader(**_: object):
        raise RuntimeError("fake provider failure")

    monkeypatch.setattr(proxy_backtest, "download_yahoo_price_history", fail_downloader)

    payload = run_proxy_cycle_backtest(
        price_source="yahoo",
        symbols=DEFAULT_SYMBOLS[:4],
        start="2024-01-01",
        end="2026-06-03",
        cache_dir=tmp_path,
        allow_synthetic_fallback=True,
        research_only=True,
    )

    assert payload["run_status"] == "PARKED"
    assert payload["source_kind"] == "unavailable"
    assert payload["reason_code"] == "SOURCE_DOWNLOAD_FAILED"


def test_run_proxy_cycle_backtest_requires_research_only_for_synthetic():
    payload = run_proxy_cycle_backtest(
        price_source="synthetic",
        symbols=DEFAULT_SYMBOLS[:4],
        start="2024-01-01",
        end="2026-06-03",
        top_n=2,
    )

    assert payload["run_status"] == "PARKED"
    assert payload["source_kind"] == "synthetic"
    assert payload["fallback_used"] is False
    assert payload["research_only"] is True
    assert payload["promotion_eligible"] is False
    assert payload["reason_code"] == "SYNTHETIC_REQUIRES_RESEARCH_ONLY"


@pytest.mark.parametrize("missing_symbol", [DEFAULT_SYMBOLS[1], "2800.HK"])
def test_proxy_cycle_backtest_cli_parks_without_evidence_when_any_requested_symbol_fails(
    missing_symbol: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    def fake_download(symbol: str, **_: object) -> pd.DataFrame:
        if symbol == missing_symbol:
            raise RuntimeError("fake symbol download failure")
        return pd.DataFrame(
            {
                "date": [pd.Timestamp("2026-06-03")],
                "symbol": [symbol],
                "close": [100.0],
                "volume": [1_000_000],
            }
        )

    def reject_evidence_build(**_: object):
        pytest.fail("partial source data must not reach the evidence builder")

    monkeypatch.setattr(proxy_backtest, "_download_yahoo_symbol", fake_download)
    monkeypatch.setattr(proxy_backtest, "build_proxy_cycle_backtest", reject_evidence_build)
    output_dir = tmp_path / "evidence"

    exit_code = proxy_backtest.main(
        [
            "--start",
            "2026-06-01",
            "--end",
            "2026-06-03",
            "--symbol",
            DEFAULT_SYMBOLS[0],
            "--symbol",
            DEFAULT_SYMBOLS[1],
            "--cache-dir",
            str(tmp_path / "cache"),
            "--output-dir",
            str(output_dir),
            "--research-only",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["run_status"] == "PARKED"
    assert payload["reason_code"] == "SOURCE_DOWNLOAD_FAILED"
    assert payload["research_only"] is True
    assert payload["promotion_eligible"] is False
    assert not output_dir.exists()
