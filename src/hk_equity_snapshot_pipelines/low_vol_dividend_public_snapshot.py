from __future__ import annotations

import argparse
import signal
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from .low_vol_dividend_longbridge_snapshot import (
    DEFAULT_BENCHMARK_SYMBOL,
    DEFAULT_HISTORY_START_DAYS,
    FINAL_LIVE_ORDER_APPROVAL_STATUS,
    MarketFundamentalProvider,
    SnapshotBuildDiagnostics,
    _artifact_evidence_role,
    _live_enablement_evidence_status,
    _normalise_hk_symbol,
    build_low_vol_dividend_factor_snapshot_from_provider,
)

DEFAULT_OUTPUT_PATH = Path("data/input/generated/low_vol_dividend_quality/factor_snapshot.public_yfinance_staging.csv")
PUBLIC_SOURCE_NAME = "public_yfinance_staging"
PUBLIC_RUNTIME_SOURCE_QUALITY = "public_yfinance_generated"
PUBLIC_RESEARCH_DEFAULT_SOURCE_QUALITY = "public_yfinance_generated_with_research_defaults"

DownloadFn = Callable[..., pd.DataFrame]
TickerFactory = Callable[[str], Any]


class _CallTimedOut(Exception):
    pass


def _public_source_quality(*, allow_research_defaults: bool) -> str:
    return PUBLIC_RESEARCH_DEFAULT_SOURCE_QUALITY if allow_research_defaults else PUBLIC_RUNTIME_SOURCE_QUALITY


def _yfinance_hk_symbol(symbol: str) -> str:
    return f"{int(_normalise_hk_symbol(symbol)):04d}.HK"


def _find_column(frame: pd.DataFrame, names: set[str]) -> Any | None:
    for column in frame.columns:
        parts = column if isinstance(column, tuple) else (column,)
        if any(str(part).strip().lower() in names for part in parts):
            return column
    return None


def _normalise_yfinance_history(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(columns=["date", "close", "volume"])

    frame = raw.copy()
    close_column = _find_column(frame, {"close", "adj close"})
    volume_column = _find_column(frame, {"volume"})
    if close_column is None:
        return pd.DataFrame(columns=["date", "close", "volume"])

    dates = frame.index
    if not isinstance(dates, pd.DatetimeIndex):
        date_column = _find_column(frame, {"date", "datetime"})
        if date_column is None:
            return pd.DataFrame(columns=["date", "close", "volume"])
        dates = pd.to_datetime(frame[date_column], errors="coerce")

    output = pd.DataFrame({"date": dates, "close": frame[close_column].to_numpy()})
    output["volume"] = frame[volume_column].to_numpy() if volume_column is not None else 0.0
    return output


class YahooFinanceHkProvider:
    def __init__(
        self,
        *,
        download_fn: DownloadFn | None = None,
        ticker_factory: TickerFactory | None = None,
        download_timeout_seconds: int = 10,
        metadata_timeout_seconds: int = 8,
    ) -> None:
        if download_fn is None or ticker_factory is None:
            try:
                import yfinance as yf
            except ImportError as exc:
                raise RuntimeError(
                    "yfinance package is required; install hk-equity-snapshot-pipelines[public-data]"
                ) from exc
            download_fn = download_fn or yf.download
            ticker_factory = ticker_factory or yf.Ticker
        self._download = download_fn
        self._ticker_factory = ticker_factory
        self._download_timeout_seconds = int(download_timeout_seconds)
        self._metadata_timeout_seconds = int(metadata_timeout_seconds)

    def _call_with_timeout(self, fn: Callable[[], Any]) -> Any:
        if self._metadata_timeout_seconds <= 0 or threading.current_thread() is not threading.main_thread():
            return fn()

        def _handle_timeout(signum: int, frame: Any) -> None:
            raise _CallTimedOut()

        previous_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handle_timeout)
        previous_timer = signal.setitimer(signal.ITIMER_REAL, self._metadata_timeout_seconds)
        try:
            return fn()
        except _CallTimedOut:
            return {}
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
            if previous_timer[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, previous_timer[0], previous_timer[1])

    def price_history(self, symbol: str, *, start: date, end: date) -> pd.DataFrame:
        raw = self._download(
            symbol,
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
            auto_adjust=True,
            progress=False,
            threads=False,
            timeout=self._download_timeout_seconds,
        )
        return _normalise_yfinance_history(raw)

    def dividends(self, symbol: str) -> list[dict[str, Any]]:
        ticker = self._ticker_factory(symbol)
        try:
            raw = self._call_with_timeout(lambda: ticker.dividends)
        except Exception:
            return []
        if raw is None or len(raw) == 0:
            return []
        if isinstance(raw, pd.DataFrame):
            amount_column = _find_column(raw, {"dividends", "dividend", "amount"})
            if amount_column is None:
                return []
            iterator = ((event_date, row[amount_column]) for event_date, row in raw.iterrows())
        else:
            iterator = raw.items()
        items: list[dict[str, Any]] = []
        for event_date, amount in iterator:
            parsed_date = pd.Timestamp(event_date).date()
            items.append({"ex_date": parsed_date.isoformat(), "amount": amount})
        return items

    def valuation(self, symbol: str) -> dict[str, Any]:
        ticker = self._ticker_factory(symbol)
        try:
            info = self._call_with_timeout(ticker.get_info)
        except Exception:
            try:
                info = self._call_with_timeout(lambda: ticker.info)
            except Exception:
                info = {}
        return {"yfinance_info": info} if isinstance(info, dict) else {}


def build_low_vol_dividend_public_factor_snapshot(
    *,
    universe_path: str | Path,
    provider: MarketFundamentalProvider,
    as_of: date,
    history_start: date,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    allow_research_defaults: bool = False,
) -> tuple[pd.DataFrame, SnapshotBuildDiagnostics]:
    return build_low_vol_dividend_factor_snapshot_from_provider(
        universe_path=universe_path,
        provider=provider,
        as_of=as_of,
        history_start=history_start,
        benchmark_symbol=benchmark_symbol,
        allow_research_defaults=allow_research_defaults,
        source_name=PUBLIC_SOURCE_NAME,
        source_quality=_public_source_quality(allow_research_defaults=allow_research_defaults),
        artifact_evidence_role=_artifact_evidence_role(allow_research_defaults=allow_research_defaults),
        symbol_formatter=_yfinance_hk_symbol,
    )


def write_low_vol_dividend_public_factor_snapshot(
    *,
    universe_path: str | Path,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    provider: MarketFundamentalProvider | None = None,
    as_of: date,
    history_start: date,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    allow_research_defaults: bool = False,
) -> dict[str, Any]:
    snapshot, diagnostics = build_low_vol_dividend_public_factor_snapshot(
        universe_path=universe_path,
        provider=provider or YahooFinanceHkProvider(),
        as_of=as_of,
        history_start=history_start,
        benchmark_symbol=benchmark_symbol,
        allow_research_defaults=allow_research_defaults,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(path, index=False)
    return {
        "profile": "hk_low_vol_dividend_quality",
        "output_path": str(path),
        "row_count": diagnostics.row_count,
        "symbols_requested": diagnostics.symbols_requested,
        "symbols_failed": diagnostics.symbols_failed,
        "failed_symbols": list(diagnostics.failed_symbols),
        "source_name": diagnostics.source_name,
        "source_quality": diagnostics.source_quality,
        "allow_research_defaults": diagnostics.allow_research_defaults,
        "artifact_evidence_role": _artifact_evidence_role(
            allow_research_defaults=diagnostics.allow_research_defaults
        ),
        "live_enablement_evidence_status": _live_enablement_evidence_status(
            allow_research_defaults=diagnostics.allow_research_defaults
        ),
        "live_order_approval_status": FINAL_LIVE_ORDER_APPROVAL_STATUS,
    }


def _parse_date(value: str | None, *, default: date) -> date:
    if not value:
        return default
    return pd.Timestamp(value).date()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a staging hk_low_vol_dividend_quality factor snapshot from public yfinance data."
    )
    parser.add_argument("--universe", required=True, help="Universe CSV with at least symbol and sector columns.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output factor snapshot CSV path.")
    parser.add_argument("--as-of", help="Snapshot as-of date. Defaults to today in UTC.")
    parser.add_argument("--history-start", help="History start date. Defaults to as_of - 450 days.")
    parser.add_argument("--benchmark-symbol", default=DEFAULT_BENCHMARK_SYMBOL)
    parser.add_argument("--allow-research-defaults", action="store_true", help="Fill missing non-price fields for staging only.")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    import json
    import sys
    from contextlib import redirect_stdout

    args = build_parser().parse_args(argv)
    as_of = _parse_date(args.as_of, default=datetime.now(timezone.utc).date())
    history_start = _parse_date(args.history_start, default=as_of - timedelta(days=DEFAULT_HISTORY_START_DAYS))

    def _build_payload() -> dict[str, Any]:
        return write_low_vol_dividend_public_factor_snapshot(
            universe_path=args.universe,
            output_path=args.output,
            as_of=as_of,
            history_start=history_start,
            benchmark_symbol=args.benchmark_symbol,
            allow_research_defaults=args.allow_research_defaults,
        )

    if args.json:
        with redirect_stdout(sys.stderr):
            payload = _build_payload()
    else:
        payload = _build_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}={value}")
    if payload["row_count"] <= 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
