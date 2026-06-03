from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .artifacts import sha256_file, write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .low_vol_dividend_platform_evidence import (
    _infer_orders,
    _normalize_platform,
    _runtime_report_checks,
)

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_dry_run_support_artifacts")
SUPPORT_ARTIFACT_VERSION = "hk_low_vol_dividend_quality.dry_run_support_artifacts.v1"
SUPPORT_ARTIFACT_TYPE_PREFIX = "hk_low_vol_dividend_quality.dry_run_support"

QUOTE_SNAPSHOT_FIELDS = (
    "quote_snapshot",
    "quote_snapshots",
    "quotes",
    "market_quotes",
    "market_quote_snapshots",
)
FEE_BREAKDOWN_FIELDS = (
    "fee_breakdown",
    "fee_breakdowns",
    "fees",
    "fee_preview",
    "broker_fee_preview",
    "broker_fee_breakdown",
)
NOTIFICATION_DELIVERY_LOG_FIELDS = (
    "notification_delivery_log",
    "notification_delivery_logs",
    "notification_audit",
    "bilingual_notification_delivery_log",
)


def _read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _clean_symbol(value: Any) -> str:
    symbol = str(value or "").strip().upper()
    if not symbol:
        return ""
    if "." in symbol:
        base, suffix = symbol.rsplit(".", 1)
        if suffix in {"HK", "HKG", "SEHK"}:
            symbol = base
    if symbol.isdigit():
        return symbol.zfill(5)
    return symbol


def _collect_symbols(value: Any) -> set[str]:
    symbols: set[str] = set()
    if isinstance(value, Mapping):
        direct = value.get("symbol") or value.get("ticker") or value.get("code")
        cleaned = _clean_symbol(direct)
        if cleaned:
            symbols.add(cleaned)
        raw_symbols = value.get("symbols")
        if isinstance(raw_symbols, list):
            symbols.update(cleaned for item in raw_symbols if (cleaned := _clean_symbol(item)))
        for nested in value.values():
            if isinstance(nested, (Mapping, list)):
                symbols.update(_collect_symbols(nested))
    elif isinstance(value, list):
        for item in value:
            symbols.update(_collect_symbols(item))
    return symbols


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _redact_order(order: Mapping[str, Any]) -> dict[str, Any]:
    allowed_fields = (
        "symbol",
        "side",
        "quantity",
        "order_type",
        "limit_price",
        "price",
        "status",
        "reason",
    )
    return {field: _json_safe(order[field]) for field in allowed_fields if field in order}


def _find_payload(runtime_report: Mapping[str, Any], fields: tuple[str, ...]) -> tuple[Any, str]:
    scopes: tuple[tuple[str, Mapping[str, Any]], ...] = (
        ("summary", _as_mapping(runtime_report.get("summary"))),
        ("diagnostics", _as_mapping(runtime_report.get("diagnostics"))),
        ("artifacts", _as_mapping(runtime_report.get("artifacts"))),
    )
    for scope_name, scope in scopes:
        for field in fields:
            value = scope.get(field)
            if value not in (None, "", [], {}):
                return _json_safe(value), f"{scope_name}.{field}"
    return None, ""


def _load_external_payload(path: str | Path | None) -> tuple[Any, str, str]:
    if path is None:
        return None, "", ""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Support artifact source file does not exist: {resolved}")
    return _read_json(resolved), str(resolved), sha256_file(resolved)


def _build_quote_snapshot_artifact(
    *,
    platform: str,
    profile: str,
    evidence_generated_at: str,
    runtime_report: Mapping[str, Any],
    runtime_report_sha256: str,
    order_symbols: set[str],
    external_quote_snapshot: Any = None,
    external_quote_snapshot_path: str = "",
    external_quote_snapshot_sha256: str = "",
) -> dict[str, Any]:
    if external_quote_snapshot is not None:
        payload, source_field = external_quote_snapshot, "external_file"
    else:
        payload, source_field = _find_payload(runtime_report, QUOTE_SNAPSHOT_FIELDS)
    quote_symbols = _collect_symbols(payload) if payload is not None else set()
    missing_symbols = sorted(order_symbols - quote_symbols) if quote_symbols else sorted(order_symbols)
    status = "passed" if payload is not None and not missing_symbols else "missing"
    return {
        "artifact_type": f"{SUPPORT_ARTIFACT_TYPE_PREFIX}.quote_snapshot.v1",
        "support_artifact_version": SUPPORT_ARTIFACT_VERSION,
        "profile": profile,
        "platform": platform,
        "status": status,
        "evidence_generated_at": evidence_generated_at,
        "source_runtime_report_sha256": runtime_report_sha256,
        "source_field": source_field,
        "source_file": external_quote_snapshot_path,
        "source_file_sha256": external_quote_snapshot_sha256,
        "order_symbols": sorted(order_symbols),
        "quote_symbols": sorted(quote_symbols),
        "missing_symbols": missing_symbols,
        "quote_snapshot": payload if payload is not None else {},
        "notes": []
        if status == "passed"
        else [
            "No complete quote snapshot payload was found in the runtime report. Provide a broker/runtime quote snapshot file before live-enable.",
        ],
    }


def _build_fee_breakdown_artifact(
    *,
    platform: str,
    profile: str,
    evidence_generated_at: str,
    runtime_report: Mapping[str, Any],
    runtime_report_sha256: str,
    order_count: int,
    external_fee_breakdown: Any = None,
    external_fee_breakdown_path: str = "",
    external_fee_breakdown_sha256: str = "",
) -> dict[str, Any]:
    if external_fee_breakdown is not None:
        payload, source_field = external_fee_breakdown, "external_file"
    else:
        payload, source_field = _find_payload(runtime_report, FEE_BREAKDOWN_FIELDS)
    status = "passed" if payload is not None else "missing"
    return {
        "artifact_type": f"{SUPPORT_ARTIFACT_TYPE_PREFIX}.fee_breakdown.v1",
        "support_artifact_version": SUPPORT_ARTIFACT_VERSION,
        "profile": profile,
        "platform": platform,
        "status": status,
        "evidence_generated_at": evidence_generated_at,
        "source_runtime_report_sha256": runtime_report_sha256,
        "source_field": source_field,
        "source_file": external_fee_breakdown_path,
        "source_file_sha256": external_fee_breakdown_sha256,
        "orders_previewed": int(order_count),
        "fee_breakdown": payload if payload is not None else {},
        "notes": []
        if status == "passed"
        else [
            "No broker fee breakdown payload was found in the runtime report. Provide a broker-preview fee breakdown before live-enable.",
        ],
    }


def _build_notification_delivery_log_artifact(
    *,
    platform: str,
    profile: str,
    evidence_generated_at: str,
    runtime_report: Mapping[str, Any],
    runtime_report_sha256: str,
) -> dict[str, Any]:
    payload, source_field = _find_payload(runtime_report, NOTIFICATION_DELIVERY_LOG_FIELDS)
    status = "passed" if isinstance(payload, Mapping) else "missing"
    return {
        "artifact_type": f"{SUPPORT_ARTIFACT_TYPE_PREFIX}.notification_delivery_log.v1",
        "support_artifact_version": SUPPORT_ARTIFACT_VERSION,
        "profile": profile,
        "platform": platform,
        "status": status,
        "evidence_generated_at": evidence_generated_at,
        "source_runtime_report_sha256": runtime_report_sha256,
        "source_field": source_field,
        "notification_delivery_log": payload if isinstance(payload, Mapping) else {},
        "notes": []
        if status == "passed"
        else [
            "No bilingual notification delivery log payload was found in the runtime report. Provide a schema-versioned delivery log before live-enable.",
        ],
    }


def build_low_vol_dividend_dry_run_support_artifacts(
    *,
    platform: str,
    runtime_report_path: str | Path,
    evidence_generated_at: str,
    quote_snapshot_file: str | Path | None = None,
    fee_breakdown_file: str | Path | None = None,
) -> dict[str, Any]:
    normalized_platform = _normalize_platform(platform)
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    runtime_report_path = Path(runtime_report_path)
    runtime_report = _read_json(runtime_report_path)
    runtime_report_sha256 = sha256_file(runtime_report_path)
    report_ok, report_errors = _runtime_report_checks(
        runtime_report,
        platform=normalized_platform,
        profile=contract.profile,
    )
    orders = [_redact_order(order) for order in _infer_orders(runtime_report, {})]
    order_symbols = _collect_symbols(orders)
    external_quote_snapshot, external_quote_snapshot_path, external_quote_snapshot_sha256 = _load_external_payload(
        quote_snapshot_file,
    )
    external_fee_breakdown, external_fee_breakdown_path, external_fee_breakdown_sha256 = _load_external_payload(
        fee_breakdown_file,
    )
    raw_order_status = "passed" if report_ok and orders else "missing"
    raw_order_preview = {
        "artifact_type": f"{SUPPORT_ARTIFACT_TYPE_PREFIX}.raw_order_preview.v1",
        "support_artifact_version": SUPPORT_ARTIFACT_VERSION,
        "profile": contract.profile,
        "platform": normalized_platform,
        "status": raw_order_status,
        "evidence_generated_at": evidence_generated_at,
        "source_runtime_report_path": str(runtime_report_path),
        "source_runtime_report_sha256": runtime_report_sha256,
        "runtime_report_checks_passed": report_ok,
        "runtime_report_errors": report_errors,
        "dry_run_session_id": str(runtime_report.get("run_id") or ""),
        "orders_previewed": len(orders),
        "orders": orders,
        "notes": []
        if raw_order_status == "passed"
        else [
            "The runtime report did not contain a passing dry-run order preview. Run a platform dry-run that produces structured orders.",
        ],
    }
    quote_snapshot = _build_quote_snapshot_artifact(
        platform=normalized_platform,
        profile=contract.profile,
        evidence_generated_at=evidence_generated_at,
        runtime_report=runtime_report,
        runtime_report_sha256=runtime_report_sha256,
        order_symbols=order_symbols,
        external_quote_snapshot=external_quote_snapshot,
        external_quote_snapshot_path=external_quote_snapshot_path,
        external_quote_snapshot_sha256=external_quote_snapshot_sha256,
    )
    fee_breakdown = _build_fee_breakdown_artifact(
        platform=normalized_platform,
        profile=contract.profile,
        evidence_generated_at=evidence_generated_at,
        runtime_report=runtime_report,
        runtime_report_sha256=runtime_report_sha256,
        order_count=len(orders),
        external_fee_breakdown=external_fee_breakdown,
        external_fee_breakdown_path=external_fee_breakdown_path,
        external_fee_breakdown_sha256=external_fee_breakdown_sha256,
    )
    notification_delivery_log = _build_notification_delivery_log_artifact(
        platform=normalized_platform,
        profile=contract.profile,
        evidence_generated_at=evidence_generated_at,
        runtime_report=runtime_report,
        runtime_report_sha256=runtime_report_sha256,
    )
    support_statuses = {
        "raw_order_preview": raw_order_preview["status"],
        "quote_snapshot": quote_snapshot["status"],
        "fee_breakdown": fee_breakdown["status"],
        "notification_delivery_log": notification_delivery_log["status"],
    }
    return {
        "support_artifact_version": SUPPORT_ARTIFACT_VERSION,
        "profile": contract.profile,
        "platform": normalized_platform,
        "runtime_report_path": str(runtime_report_path),
        "runtime_report_sha256": runtime_report_sha256,
        "runtime_report_checks_passed": report_ok,
        "runtime_report_errors": report_errors,
        "external_quote_snapshot_file": external_quote_snapshot_path,
        "external_fee_breakdown_file": external_fee_breakdown_path,
        "support_statuses": support_statuses,
        "ready_for_platform_evidence_draft": all(status == "passed" for status in support_statuses.values()),
        "raw_order_preview": raw_order_preview,
        "quote_snapshot": quote_snapshot,
        "fee_breakdown": fee_breakdown,
        "notification_delivery_log": notification_delivery_log,
    }


def _suggested_platform_evidence_command(payload: Mapping[str, Any], *, output_dir: Path) -> str:
    platform = str(payload["platform"])
    return (
        "hkeq-draft-low-vol-dividend-platform-evidence "
        f"--platform {platform} "
        f"--runtime-report {payload['runtime_report_path']} "
        "--runtime-report-uri <stable-runtime-report-uri> "
        f"--quote-snapshot-file {output_dir / f'{platform}_quote_snapshot.json'} "
        "--quote-snapshot-uri <stable-quote-snapshot-uri> "
        f"--fee-breakdown-file {output_dir / f'{platform}_fee_breakdown.json'} "
        "--fee-breakdown-uri <stable-fee-breakdown-uri> "
        "--notification-delivery-log-uri <stable-notification-log-uri> "
        f"--notification-delivery-log-file {output_dir / f'{platform}_notification_delivery_log.json'} "
        "--notification-correlation-id <dry-run-correlation-id> "
        "--adv-window-trading-days <days> "
        "--median-daily-turnover-hkd <hkd> "
        "--max-single-order-adv-fraction <fraction> "
        "--rebalance-adv-fraction <fraction> "
        "--confirm-order-preview-provenance "
        "--confirm-notification-audit "
        "--confirm-execution-capacity "
        f"--evidence-generated-at <YYYY-MM-DD> --output-dir evidence/low_vol_dividend_quality"
    )


def write_low_vol_dividend_dry_run_support_artifacts(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_dry_run_support_artifacts(**kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    platform = str(payload["platform"])
    paths = {
        "raw_order_preview_path": output_dir / f"{platform}_raw_order_preview.json",
        "quote_snapshot_path": output_dir / f"{platform}_quote_snapshot.json",
        "fee_breakdown_path": output_dir / f"{platform}_fee_breakdown.json",
        "notification_delivery_log_path": output_dir / f"{platform}_notification_delivery_log.json",
        "summary_path": output_dir / f"{platform}_dry_run_support_artifacts_summary.json",
    }
    write_json(paths["raw_order_preview_path"], payload["raw_order_preview"])
    write_json(paths["quote_snapshot_path"], payload["quote_snapshot"])
    write_json(paths["fee_breakdown_path"], payload["fee_breakdown"])
    write_json(paths["notification_delivery_log_path"], payload["notification_delivery_log"])
    summary = {
        key: value
        for key, value in payload.items()
        if key not in {"raw_order_preview", "quote_snapshot", "fee_breakdown", "notification_delivery_log"}
    }
    summary["paths"] = {key: str(path) for key, path in paths.items() if key != "summary_path"}
    summary["suggested_platform_evidence_command"] = _suggested_platform_evidence_command(payload, output_dir=output_dir)
    write_json(paths["summary_path"], summary)
    return {
        **payload,
        **{key: str(path) for key, path in paths.items()},
        "suggested_platform_evidence_command": summary["suggested_platform_evidence_command"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect support artifacts from an HK low-vol platform dry-run report.")
    parser.add_argument("--platform", required=True, choices=("ibkr", "longbridge"))
    parser.add_argument("--runtime-report", required=True)
    parser.add_argument("--quote-snapshot-file", help="Optional external broker/runtime quote snapshot JSON.")
    parser.add_argument("--fee-breakdown-file", help="Optional external broker fee breakdown JSON.")
    parser.add_argument("--evidence-generated-at", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_dry_run_support_artifacts(
        output_dir=args.output_dir,
        platform=args.platform,
        runtime_report_path=args.runtime_report,
        quote_snapshot_file=args.quote_snapshot_file,
        fee_breakdown_file=args.fee_breakdown_file,
        evidence_generated_at=args.evidence_generated_at,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"platform={payload['platform']}")
        print(f"ready_for_platform_evidence_draft={payload['ready_for_platform_evidence_draft']}")
        print(f"raw_order_preview_path={payload['raw_order_preview_path']}")
        print(f"quote_snapshot_path={payload['quote_snapshot_path']}")
        print(f"fee_breakdown_path={payload['fee_breakdown_path']}")
        print(f"summary_path={payload['summary_path']}")
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "SUPPORT_ARTIFACT_TYPE_PREFIX",
    "SUPPORT_ARTIFACT_VERSION",
    "build_low_vol_dividend_dry_run_support_artifacts",
    "main",
    "write_low_vol_dividend_dry_run_support_artifacts",
]
