from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

import pandas as pd

DEFAULT_BENCHMARK_SYMBOL = "2800.HK"
DEFAULT_HISTORY_START_DAYS = 450
DEFAULT_OUTPUT_PATH = Path("data/input/generated/low_vol_dividend_quality/factor_snapshot.longbridge_staging.csv")
STAGING_SOURCE_NAME = "longbridge_openapi_staging"
RUNTIME_SOURCE_QUALITY = "longbridge_openapi_generated"
RESEARCH_DEFAULT_SOURCE_QUALITY = "longbridge_openapi_generated_with_research_defaults"
RUNTIME_ARTIFACT_EVIDENCE_STATUS = "runtime_artifact_evidence_ready_final_live_order_approval_pending"
RESEARCH_DEFAULT_EVIDENCE_STATUS = "research_smoke_only_not_runtime_artifact_evidence"
RUNTIME_ARTIFACT_ROLE = "runtime_artifact_input"
RESEARCH_DEFAULT_ARTIFACT_ROLE = "research_smoke_input"
FINAL_LIVE_ORDER_APPROVAL_STATUS = "pending_backtest_dry_run_and_operator_approval"


class MarketFundamentalProvider(Protocol):
    def price_history(self, symbol: str, *, start: date, end: date) -> pd.DataFrame: ...

    def dividends(self, symbol: str) -> list[dict[str, Any]]: ...

    def valuation(self, symbol: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SnapshotBuildDiagnostics:
    row_count: int
    symbols_requested: int
    symbols_failed: int
    failed_symbols: tuple[str, ...]
    source_name: str
    source_quality: str
    allow_research_defaults: bool


def _normalise_hk_symbol(symbol: str) -> str:
    raw = str(symbol or "").strip().upper().replace("HK.", "").replace(".HK", "")
    if not raw:
        raise ValueError("symbol is required")
    if not raw.isdigit():
        raise ValueError(f"HK symbol must be numeric or .HK-suffixed: {symbol!r}")
    return raw.zfill(5)


def _source_quality(*, allow_research_defaults: bool) -> str:
    return RESEARCH_DEFAULT_SOURCE_QUALITY if allow_research_defaults else RUNTIME_SOURCE_QUALITY


def _live_enablement_evidence_status(*, allow_research_defaults: bool) -> str:
    return RESEARCH_DEFAULT_EVIDENCE_STATUS if allow_research_defaults else RUNTIME_ARTIFACT_EVIDENCE_STATUS


def _artifact_evidence_role(*, allow_research_defaults: bool) -> str:
    return RESEARCH_DEFAULT_ARTIFACT_ROLE if allow_research_defaults else RUNTIME_ARTIFACT_ROLE


def _longbridge_symbol(symbol: str) -> str:
    return f"{int(_normalise_hk_symbol(symbol))}.HK"


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip().replace(",", "")
        if not stripped or stripped.lower() in {"nan", "none", "null", "--", "-"}:
            return None
        if stripped.endswith("%"):
            parsed = _as_float(stripped[:-1])
            return None if parsed is None else parsed / 100.0
        value = stripped
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return None


def _object_to_plain(value: Any, *, depth: int = 0) -> Any:
    if depth > 4:
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_object_to_plain(item, depth=depth + 1) for item in value]
    if isinstance(value, dict):
        return {str(key): _object_to_plain(item, depth=depth + 1) for key, item in value.items()}
    result: dict[str, Any] = {}
    for name in dir(value):
        if name.startswith("_"):
            continue
        try:
            item = getattr(value, name)
        except Exception:
            continue
        if callable(item):
            continue
        plain = _object_to_plain(item, depth=depth + 1)
        if plain is not None:
            result[name] = plain
    return result


def _iter_nested(value: Any) -> list[Any]:
    items = [value]
    if isinstance(value, dict):
        for nested in value.values():
            items.extend(_iter_nested(nested))
    elif isinstance(value, list):
        for nested in value:
            items.extend(_iter_nested(nested))
    return items


def _lookup_number(payload: dict[str, Any], names: tuple[str, ...]) -> float | None:
    normalized_names = {name.lower() for name in names}
    for node in _iter_nested(payload):
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if str(key).lower() in normalized_names:
                parsed = _as_float(value)
                if parsed is not None:
                    return parsed
    return None


def _extract_dividend_amount(item: dict[str, Any]) -> float | None:
    for key in ("amount", "cash", "dividend", "dps", "dividend_per_share"):
        parsed = _as_float(item.get(key))
        if parsed is not None:
            return parsed
    desc = str(item.get("desc") or "")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:HKD|HK\$|港元|/share|每股)", desc, flags=re.IGNORECASE)
    if match:
        return _as_float(match.group(1))
    match = re.search(r"(?:HKD|HK\$|港元)\s*([0-9]+(?:\.[0-9]+)?)", desc, flags=re.IGNORECASE)
    if match:
        return _as_float(match.group(1))
    return None


def _parse_event_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip().replace(".", "-").replace("/", "-")
    if not text:
        return None
    try:
        return pd.Timestamp(text).date()
    except Exception:
        return None


def _prepare_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        raise ValueError("price history is empty")
    frame = history.copy()
    if "date" not in frame.columns:
        raise ValueError("price history must contain date")
    if "close" not in frame.columns:
        raise ValueError("price history must contain close")
    if "volume" not in frame.columns:
        frame["volume"] = 0.0
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None).dt.normalize()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce").fillna(0.0)
    frame = frame.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last")
    if frame.empty:
        raise ValueError("price history has no valid close rows")
    return frame.reset_index(drop=True)


def _latest_ratio(close: pd.Series, lookback: int, *, skip: int = 0) -> float:
    if len(close) <= lookback + skip:
        return 0.0
    latest = close.iloc[-1 - skip]
    base = close.iloc[-1 - skip - lookback]
    if base == 0 or pd.isna(base) or pd.isna(latest):
        return 0.0
    return float(latest / base - 1.0)


def _max_drawdown(close: pd.Series) -> float:
    if close.empty:
        return 0.0
    running_high = close.cummax()
    drawdown = close / running_high - 1.0
    return float(drawdown.min()) if not drawdown.empty else 0.0


def _beta(symbol_history: pd.DataFrame, benchmark_history: pd.DataFrame | None) -> float:
    if benchmark_history is None or benchmark_history.empty:
        return 1.0
    lhs = symbol_history.set_index("date")["close"].pct_change(fill_method=None).dropna().rename("symbol")
    rhs = benchmark_history.set_index("date")["close"].pct_change(fill_method=None).dropna().rename("benchmark")
    returns = pd.concat([lhs, rhs], axis=1).dropna().tail(252)
    if len(returns) < 30:
        return 1.0
    variance = float(returns["benchmark"].var())
    if variance <= 0 or not math.isfinite(variance):
        return 1.0
    covariance = float(returns["symbol"].cov(returns["benchmark"]))
    if not math.isfinite(covariance):
        return 1.0
    return max(-2.0, min(3.0, covariance / variance))


def _suspension_days(symbol_history: pd.DataFrame, benchmark_history: pd.DataFrame | None) -> int:
    if benchmark_history is None or benchmark_history.empty:
        return 0
    benchmark_dates = set(benchmark_history["date"].tail(63))
    symbol_dates = set(symbol_history["date"].tail(80))
    return max(0, len(benchmark_dates - symbol_dates))


def _price_metrics(symbol_history: pd.DataFrame, benchmark_history: pd.DataFrame | None) -> dict[str, float | int]:
    frame = _prepare_history(symbol_history)
    close = frame["close"]
    returns = close.pct_change(fill_method=None).dropna()
    realized_vol_126 = float(returns.tail(126).std() * math.sqrt(252)) if len(returns) >= 20 else 0.0
    realized_vol_252 = float(returns.tail(252).std() * math.sqrt(252)) if len(returns) >= 20 else realized_vol_126
    sma200 = float(close.tail(200).mean()) if len(close) >= 20 else float(close.mean())
    latest_close = float(close.iloc[-1])
    return {
        "close_hkd": latest_close,
        "adv20_hkd": float((frame["close"] * frame["volume"]).tail(20).mean()),
        "realized_vol_126": max(0.0, realized_vol_126),
        "realized_vol_252": max(0.0, realized_vol_252),
        "beta_252": _beta(frame, benchmark_history),
        "maxdd_252": _max_drawdown(close.tail(252)),
        "mom_6m": _latest_ratio(close, 126),
        "mom_12_1": _latest_ratio(close, 252, skip=21),
        "sma200_gap": float(latest_close / sma200 - 1.0) if sma200 > 0 else 0.0,
        "suspension_days_63": _suspension_days(frame, benchmark_history),
    }


def _dividend_metrics(dividends: list[dict[str, Any]], *, as_of: date, close_hkd: float) -> dict[str, float]:
    one_year_start = as_of - timedelta(days=365)
    three_year_start = as_of - timedelta(days=365 * 3)
    one_year_amount = 0.0
    paid_years: set[int] = set()
    for item in dividends:
        event_date = _parse_event_date(item.get("ex_date") or item.get("payment_date") or item.get("record_date"))
        amount = _extract_dividend_amount(item)
        if event_date is None or amount is None or amount <= 0:
            continue
        if one_year_start <= event_date <= as_of:
            one_year_amount += amount
        if three_year_start <= event_date <= as_of:
            paid_years.add(event_date.year)
    return {
        "dividend_yield_net": float(one_year_amount / close_hkd) if close_hkd > 0 else 0.0,
        "dividend_stability_3y": min(1.0, len(paid_years) / 3.0),
    }


def _read_universe(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(Path(path))
    if "symbol" not in frame.columns:
        raise ValueError("universe CSV must contain symbol")
    if "sector" not in frame.columns:
        frame["sector"] = "Unknown"
    frame["symbol"] = frame["symbol"].map(_normalise_hk_symbol)
    return frame.drop_duplicates("symbol", keep="first").reset_index(drop=True)


def _metadata_number(row: pd.Series, name: str) -> float | None:
    if name not in row.index:
        return None
    return _as_float(row[name])


def _metadata_bool(row: pd.Series, name: str) -> bool | None:
    if name not in row.index:
        return None
    return _as_bool(row[name])


def _resolve_required_number(
    *,
    field: str,
    row: pd.Series,
    valuation: dict[str, Any],
    valuation_keys: tuple[str, ...],
    allow_research_defaults: bool,
    research_default: float,
    missing: list[str],
) -> float:
    value = _metadata_number(row, field)
    if value is None:
        value = _lookup_number(valuation, valuation_keys)
    if value is not None:
        return float(value)
    if allow_research_defaults:
        return float(research_default)
    missing.append(field)
    return float("nan")


def _resolve_required_bool(
    *,
    field: str,
    row: pd.Series,
    valuation: dict[str, Any],
    allow_research_defaults: bool,
    research_default: bool,
    missing: list[str],
) -> bool:
    value = _metadata_bool(row, field)
    if value is not None:
        return bool(value)
    pe = _lookup_number(valuation, ("pe", "pe_ratio", "trailing_pe", "trailingPE"))
    eps = _lookup_number(valuation, ("eps", "basic_eps", "diluted_eps"))
    if eps is not None:
        return eps > 0
    if pe is not None:
        return pe > 0
    if allow_research_defaults:
        return bool(research_default)
    missing.append(field)
    return False


def build_low_vol_dividend_factor_snapshot_from_provider(
    *,
    universe_path: str | Path,
    provider: MarketFundamentalProvider,
    as_of: date,
    history_start: date,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    allow_research_defaults: bool = False,
    source_name: str = STAGING_SOURCE_NAME,
    source_quality: str | None = None,
    artifact_evidence_role: str | None = None,
    symbol_formatter: Callable[[str], str] = _longbridge_symbol,
) -> tuple[pd.DataFrame, SnapshotBuildDiagnostics]:
    universe = _read_universe(universe_path)
    benchmark_history: pd.DataFrame | None = None
    try:
        benchmark_history = _prepare_history(
            provider.price_history(symbol_formatter(benchmark_symbol), start=history_start, end=as_of)
        )
    except Exception:
        benchmark_history = None

    rows: list[dict[str, Any]] = []
    failed: list[str] = []
    source_quality_label = source_quality or _source_quality(allow_research_defaults=allow_research_defaults)
    artifact_evidence_role_label = artifact_evidence_role or _artifact_evidence_role(
        allow_research_defaults=allow_research_defaults
    )
    for _, item in universe.iterrows():
        symbol = str(item["symbol"])
        provider_symbol = symbol_formatter(symbol)
        try:
            history = _prepare_history(provider.price_history(provider_symbol, start=history_start, end=as_of))
            price = _price_metrics(history, benchmark_history)
            dividends = provider.dividends(provider_symbol)
            valuation = provider.valuation(provider_symbol)
            dividend = _dividend_metrics(dividends, as_of=as_of, close_hkd=float(price["close_hkd"]))
            if dividend["dividend_yield_net"] <= 0:
                provider_yield = _lookup_number(
                    valuation,
                    ("dividend_yield", "dividendYield", "div_yld", "dvd_yld", "trailing_annual_dividend_yield"),
                )
                if provider_yield is not None:
                    dividend["dividend_yield_net"] = provider_yield / 100.0 if provider_yield > 1.0 else provider_yield

            missing: list[str] = []
            market_cap_hkd = _resolve_required_number(
                field="market_cap_hkd",
                row=item,
                valuation=valuation,
                valuation_keys=("market_cap", "marketCap", "market_cap_hkd", "marketCapitalization"),
                allow_research_defaults=allow_research_defaults,
                research_default=0.0,
                missing=missing,
            )
            payout_ratio = _resolve_required_number(
                field="payout_ratio",
                row=item,
                valuation=valuation,
                valuation_keys=("payout_ratio", "payoutRatio", "div_payout_ratio", "dividend_payout_ratio"),
                allow_research_defaults=allow_research_defaults,
                research_default=0.55,
                missing=missing,
            )
            earnings_positive = _resolve_required_bool(
                field="earnings_positive",
                row=item,
                valuation=valuation,
                allow_research_defaults=allow_research_defaults,
                research_default=True,
                missing=missing,
            )
            if missing:
                raise ValueError(f"missing required non-price fields: {', '.join(missing)}")

            pe_ratio = _metadata_number(item, "pe_ratio")
            if pe_ratio is None:
                pe_ratio = _lookup_number(valuation, ("pe", "pe_ratio", "trailing_pe", "trailingPE"))
            fcf_yield = _metadata_number(item, "free_cash_flow_yield")
            lot_size = _metadata_number(item, "lot_size")

            rows.append(
                {
                    "symbol": symbol,
                    "sector": str(item.get("sector") or "Unknown"),
                    **price,
                    "market_cap_hkd": market_cap_hkd,
                    **dividend,
                    "earnings_positive": earnings_positive,
                    "payout_ratio": payout_ratio,
                    "as_of": as_of.isoformat(),
                    "snapshot_date": as_of.isoformat(),
                    "eligible": _metadata_bool(item, "eligible") if _metadata_bool(item, "eligible") is not None else True,
                    "lot_size": lot_size if lot_size is not None else 100,
                    "pe_ratio": pe_ratio if pe_ratio is not None else "",
                    "free_cash_flow_yield": fcf_yield if fcf_yield is not None else "",
                    "corporate_action_flag": str(item.get("corporate_action_flag") or ""),
                    "source_name": source_name,
                    "source_quality": source_quality_label,
                    "artifact_evidence_role": artifact_evidence_role_label,
                    "live_order_approval_status": FINAL_LIVE_ORDER_APPROVAL_STATUS,
                    "requires_operator_audit": True,
                }
            )
        except Exception as exc:
            failed.append(f"{symbol}: {exc}")

    output = pd.DataFrame(rows)
    diagnostics = SnapshotBuildDiagnostics(
        row_count=int(len(output)),
        symbols_requested=int(len(universe)),
        symbols_failed=int(len(failed)),
        failed_symbols=tuple(failed),
        source_name=source_name,
        source_quality=source_quality_label,
        allow_research_defaults=bool(allow_research_defaults),
    )
    return output, diagnostics


class LongBridgeOpenApiProvider:
    def __init__(self, *, app_key: str, app_secret: str, access_token: str) -> None:
        try:
            from longbridge.openapi import AdjustType, Config, FundamentalContext, Period, QuoteContext, TradeSessions
        except ImportError as exc:
            raise RuntimeError("longbridge package is required; install hk-equity-snapshot-pipelines[longbridge]") from exc
        config = Config.from_apikey(app_key, app_secret, access_token)
        self._quote_context = QuoteContext(config)
        self._fundamental_context = FundamentalContext(config)
        self._period_day = Period.Day
        self._adjust_type = AdjustType.ForwardAdjust
        self._trade_sessions = TradeSessions.Intraday

    def price_history(self, symbol: str, *, start: date, end: date) -> pd.DataFrame:
        rows = self._quote_context.history_candlesticks_by_date(
            symbol,
            self._period_day,
            self._adjust_type,
            start,
            end,
            self._trade_sessions,
        )
        output = []
        for item in rows:
            plain = _object_to_plain(item)
            if not isinstance(plain, dict):
                continue
            event_date = plain.get("date") or plain.get("timestamp") or plain.get("time")
            output.append(
                {
                    "date": event_date,
                    "close": plain.get("close"),
                    "volume": plain.get("volume") or plain.get("turnover") or 0,
                }
            )
        return pd.DataFrame(output)

    def dividends(self, symbol: str) -> list[dict[str, Any]]:
        try:
            response = self._fundamental_context.dividend_detail(symbol)
        except Exception:
            response = self._fundamental_context.dividend(symbol)
        plain = _object_to_plain(response)
        if isinstance(plain, dict):
            items = plain.get("list") or plain.get("items") or []
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []

    def valuation(self, symbol: str) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for method in ("valuation", "industry_valuation"):
            try:
                response = getattr(self._fundamental_context, method)(symbol)
            except Exception:
                continue
            plain = _object_to_plain(response)
            if isinstance(plain, dict):
                payload[method] = plain
        return payload


def write_low_vol_dividend_longbridge_factor_snapshot(
    *,
    universe_path: str | Path,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    provider: MarketFundamentalProvider,
    as_of: date,
    history_start: date,
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL,
    allow_research_defaults: bool = False,
) -> dict[str, Any]:
    snapshot, diagnostics = build_low_vol_dividend_factor_snapshot_from_provider(
        universe_path=universe_path,
        provider=provider,
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
        "artifact_evidence_role": _artifact_evidence_role(allow_research_defaults=diagnostics.allow_research_defaults),
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
    parser = argparse.ArgumentParser(description="Build a staging hk_low_vol_dividend_quality factor snapshot from LongBridge OpenAPI.")
    parser.add_argument("--universe", required=True, help="Universe CSV with at least symbol and sector columns.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output factor snapshot CSV path.")
    parser.add_argument("--as-of", help="Snapshot as-of date. Defaults to today in UTC.")
    parser.add_argument("--history-start", help="History start date. Defaults to as_of - 450 days.")
    parser.add_argument("--benchmark-symbol", default=DEFAULT_BENCHMARK_SYMBOL)
    parser.add_argument("--allow-research-defaults", action="store_true", help="Fill missing non-price fields for staging only.")
    parser.add_argument("--app-key", default="", help="LongBridge app key. Prefer env LONG_BRIDGE_APP_KEY.")
    parser.add_argument("--app-secret", default="", help="LongBridge app secret. Prefer env LONG_BRIDGE_APP_SECRET.")
    parser.add_argument("--access-token", default="", help="LongBridge access token. Prefer env LONG_BRIDGE_ACCESS_TOKEN.")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    import json
    import os
    import sys
    from contextlib import contextmanager, redirect_stdout

    args = build_parser().parse_args(argv)
    as_of = _parse_date(args.as_of, default=datetime.now(timezone.utc).date())
    history_start = _parse_date(args.history_start, default=as_of - timedelta(days=DEFAULT_HISTORY_START_DAYS))
    app_key = args.app_key or os.getenv("LONG_BRIDGE_APP_KEY") or os.getenv("LONGPORT_APP_KEY") or ""
    app_secret = args.app_secret or os.getenv("LONG_BRIDGE_APP_SECRET") or os.getenv("LONGPORT_APP_SECRET") or ""
    access_token = args.access_token or os.getenv("LONG_BRIDGE_ACCESS_TOKEN") or os.getenv("LONGPORT_ACCESS_TOKEN") or ""
    missing = [name for name, value in (("app_key", app_key), ("app_secret", app_secret), ("access_token", access_token)) if not value]
    if missing:
        raise EnvironmentError(f"missing LongBridge credentials: {', '.join(missing)}")
    def _build_payload() -> dict[str, Any]:
        return write_low_vol_dividend_longbridge_factor_snapshot(
            universe_path=args.universe,
            output_path=args.output,
            provider=LongBridgeOpenApiProvider(app_key=app_key, app_secret=app_secret, access_token=access_token),
            as_of=as_of,
            history_start=history_start,
            benchmark_symbol=args.benchmark_symbol,
            allow_research_defaults=args.allow_research_defaults,
        )

    @contextmanager
    def _redirect_stdout_to_stderr():
        # Some LongBridge SDK diagnostics are written directly to stdout, bypassing Python print.
        # Redirect both Python sys.stdout and the underlying file descriptor while building payloads.
        sys.stdout.flush()
        sys.stderr.flush()
        original_stdout_fd = os.dup(sys.stdout.fileno())
        try:
            os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
            with redirect_stdout(sys.stderr):
                yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os.dup2(original_stdout_fd, sys.stdout.fileno())
            os.close(original_stdout_fd)

    if args.json:
        with _redirect_stdout_to_stderr():
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
