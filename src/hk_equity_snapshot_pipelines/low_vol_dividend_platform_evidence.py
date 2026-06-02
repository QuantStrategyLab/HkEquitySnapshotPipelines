from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .artifacts import sha256_file, write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .live_enablement_evidence import (
    validate_live_enablement_evidence,
    build_live_enablement_evidence_template,
)
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_platform_evidence")
DRAFT_VERSION = "hk_low_vol_dividend_quality.platform_evidence_draft.v1"


def _read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _stable_uri(value: str | None) -> str:
    return str(value or "").strip()


def _optional_sha(path: str | Path | None) -> str:
    if path is None:
        return ""
    resolved = Path(path)
    if not resolved.exists():
        return ""
    return sha256_file(resolved)


def _normalize_platform(platform: str) -> str:
    normalized = str(platform or "").strip().lower()
    if normalized not in SUPPORTED_SNAPSHOT_PLATFORMS:
        known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
        raise ValueError(f"Unsupported snapshot platform {platform!r}; known platforms: {known}")
    return normalized


def _infer_orders(runtime_report: Mapping[str, Any], reconciliation_record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    summary = _as_mapping(runtime_report.get("summary"))
    candidates = (
        summary.get("orders_submitted"),
        reconciliation_record.get("orders_submitted"),
        _as_mapping(runtime_report.get("diagnostics")).get("orders_submitted"),
    )
    for candidate in candidates:
        orders = [order for order in _as_list(candidate) if isinstance(order, Mapping)]
        if orders:
            return orders
    return []


def _infer_order_count(
    runtime_report: Mapping[str, Any],
    reconciliation_record: Mapping[str, Any],
    *,
    orders_previewed: int | None,
) -> int:
    if orders_previewed is not None:
        return max(0, int(orders_previewed))
    orders = _infer_orders(runtime_report, reconciliation_record)
    if orders:
        return len(orders)
    summary = _as_mapping(runtime_report.get("summary"))
    for field in ("orders_submitted_count", "orders_previewed"):
        try:
            return max(0, int(summary.get(field) or 0))
        except (TypeError, ValueError):
            continue
    return 0


def _infer_fractional_share_errors(orders: list[Mapping[str, Any]]) -> int:
    errors = 0
    for order in orders:
        try:
            quantity = float(order.get("quantity") or 0.0)
        except (TypeError, ValueError):
            errors += 1
            continue
        if quantity < 0 or not quantity.is_integer():
            errors += 1
    return errors


def _runtime_report_checks(
    runtime_report: Mapping[str, Any],
    *,
    platform: str,
    profile: str,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if runtime_report.get("dry_run") is not True:
        errors.append("runtime_report.dry_run must be true")
    if str(runtime_report.get("status") or "").strip().lower() != "ok":
        errors.append("runtime_report.status must be 'ok'")
    if str(runtime_report.get("platform") or "").strip().lower() != platform:
        errors.append(f"runtime_report.platform must be {platform!r}")
    if str(runtime_report.get("strategy_profile") or "").strip() != profile:
        errors.append(f"runtime_report.strategy_profile must be {profile!r}")
    return not errors, errors


def _all_present(*values: Any) -> bool:
    return all(str(value or "").strip() for value in values)


def _copy_shared_sections(target: dict[str, Any], shared: Mapping[str, Any]) -> None:
    for section in (
        "production_snapshot_source_audit",
        "artifact_pack_validation",
        "walk_forward_backtest",
        "broker_permission_and_fee_verification",
        "paper_or_dry_run_rebalance_window",
        "runtime_rollout_plan",
        "risk_approval",
        "strategy_policy_evidence",
    ):
        if isinstance(shared.get(section), Mapping):
            target[section] = dict(shared[section])


def build_low_vol_dividend_platform_evidence_draft(
    *,
    platform: str,
    runtime_report_path: str | Path,
    evidence_generated_at: str,
    runtime_report_uri: str = "",
    base_evidence_file: str | Path | None = None,
    reconciliation_record_path: str | Path | None = None,
    orders_previewed: int | None = None,
    lot_size_errors: int = 0,
    quote_snapshot_uri: str = "",
    quote_snapshot_file: str | Path | None = None,
    fee_breakdown_uri: str = "",
    fee_breakdown_file: str | Path | None = None,
    notification_delivery_log_uri: str = "",
    notification_correlation_id: str = "",
    adv_window_trading_days: int = 0,
    median_daily_turnover_hkd: float | None = None,
    max_single_order_adv_fraction: float | None = None,
    rebalance_adv_fraction: float | None = None,
    confirm_order_preview_provenance: bool = False,
    confirm_notification_audit: bool = False,
    confirm_execution_capacity: bool = False,
) -> dict[str, Any]:
    normalized_platform = _normalize_platform(platform)
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    runtime_report_path = Path(runtime_report_path)
    runtime_report = _read_json(runtime_report_path)
    reconciliation_record: dict[str, Any] = {}
    if reconciliation_record_path is None:
        report_artifacts = _as_mapping(runtime_report.get("artifacts"))
        candidate = report_artifacts.get("reconciliation_record_path")
        if candidate and Path(str(candidate)).exists():
            reconciliation_record_path = str(candidate)
    if reconciliation_record_path is not None and Path(reconciliation_record_path).exists():
        reconciliation_record = _read_json(reconciliation_record_path)

    payload = (
        _read_json(base_evidence_file)
        if base_evidence_file is not None
        else build_live_enablement_evidence_template(contract.profile, platform=normalized_platform)
    )
    payload["profile"] = contract.profile
    payload["platform"] = normalized_platform
    payload["contract_version"] = contract.contract_version
    if base_evidence_file is not None:
        _copy_shared_sections(payload, _read_json(base_evidence_file))

    orders = _infer_orders(runtime_report, reconciliation_record)
    resolved_orders_previewed = _infer_order_count(
        runtime_report,
        reconciliation_record,
        orders_previewed=orders_previewed,
    )
    fractional_share_errors = _infer_fractional_share_errors(orders) if orders else 0
    raw_order_preview_uri = _stable_uri(runtime_report_uri)
    raw_order_preview_sha256 = sha256_file(runtime_report_path)
    quote_snapshot_sha256 = _optional_sha(quote_snapshot_file)
    fee_breakdown_sha256 = _optional_sha(fee_breakdown_file)
    report_ok, report_errors = _runtime_report_checks(
        runtime_report,
        platform=normalized_platform,
        profile=contract.profile,
    )

    section = dict(payload.get("platform_dry_run_order_preview") or {})
    section.update(
        {
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": raw_order_preview_uri,
            "orders_previewed": resolved_orders_previewed,
            "fractional_share_errors": fractional_share_errors,
            "lot_size_errors": int(lot_size_errors),
            "notification_sent": bool(notification_delivery_log_uri),
            "notification_correlation_id": str(notification_correlation_id or runtime_report.get("run_id") or ""),
            "notification_locale_en": bool(confirm_notification_audit),
            "notification_locale_zh_hans": bool(confirm_notification_audit),
            "notification_contains_profile": bool(confirm_notification_audit),
            "notification_contains_platform": bool(confirm_notification_audit),
            "notification_contains_validation_status": bool(confirm_notification_audit),
            "notification_contains_order_preview_summary": bool(confirm_notification_audit),
            "notification_redacts_sensitive_fields": bool(confirm_notification_audit),
            "notification_delivery_log_uri": _stable_uri(notification_delivery_log_uri),
            "dry_run_session_id": str(runtime_report.get("run_id") or ""),
            "raw_order_preview_uri": raw_order_preview_uri,
            "raw_order_preview_sha256": raw_order_preview_sha256,
            "quote_snapshot_uri": _stable_uri(quote_snapshot_uri),
            "quote_snapshot_sha256": quote_snapshot_sha256,
            "fee_breakdown_uri": _stable_uri(fee_breakdown_uri),
            "fee_breakdown_sha256": fee_breakdown_sha256,
            "order_preview_artifact_not_sample": bool(confirm_order_preview_provenance),
            "order_preview_redacts_sensitive_fields": bool(confirm_order_preview_provenance),
            "quote_snapshot_covers_all_symbols": bool(confirm_order_preview_provenance),
            "fee_breakdown_reconciled_to_broker_preview": bool(confirm_order_preview_provenance),
            "order_preview_reconciled_to_strategy_decision": bool(confirm_order_preview_provenance),
            "adv_window_trading_days": int(adv_window_trading_days),
            "median_daily_turnover_hkd": median_daily_turnover_hkd,
            "max_single_order_adv_fraction": max_single_order_adv_fraction,
            "rebalance_adv_fraction": rebalance_adv_fraction,
            "liquidity_cap_verified": bool(confirm_execution_capacity),
            "board_lot_rounding_verified": bool(confirm_execution_capacity),
            "odd_lot_avoidance_verified": bool(confirm_execution_capacity),
            "market_session_routing_verified": bool(confirm_execution_capacity),
            "vcm_price_band_controls_verified": bool(confirm_execution_capacity),
        }
    )
    dry_run_section_can_pass = all(
        (
            report_ok,
            resolved_orders_previewed > 0,
            fractional_share_errors == 0,
            int(lot_size_errors) == 0,
            confirm_order_preview_provenance,
            confirm_notification_audit,
            confirm_execution_capacity,
            _all_present(
                raw_order_preview_uri,
                raw_order_preview_sha256,
                quote_snapshot_uri,
                quote_snapshot_sha256,
                fee_breakdown_uri,
                fee_breakdown_sha256,
                notification_delivery_log_uri,
                section.get("dry_run_session_id"),
            ),
            int(adv_window_trading_days) > 0,
            median_daily_turnover_hkd is not None,
            max_single_order_adv_fraction is not None,
            rebalance_adv_fraction is not None,
        )
    )
    section["status"] = "passed" if dry_run_section_can_pass else "pending"
    payload["platform_dry_run_order_preview"] = section
    validation = validate_live_enablement_evidence(payload)
    return {
        "draft_version": DRAFT_VERSION,
        "profile": contract.profile,
        "platform": normalized_platform,
        "runtime_report_path": str(runtime_report_path),
        "runtime_report_uri": raw_order_preview_uri,
        "reconciliation_record_path": str(reconciliation_record_path) if reconciliation_record_path is not None else None,
        "runtime_report_checks_passed": report_ok,
        "runtime_report_errors": report_errors,
        "orders_previewed": resolved_orders_previewed,
        "platform_dry_run_section_status": section["status"],
        "live_enablement_allowed": bool(validation.get("live_enablement_allowed")),
        "validation_status": validation.get("validation_status"),
        "validation_errors_count": len(validation.get("errors") or []),
        "validation_errors_preview": list(validation.get("errors") or [])[:30],
        "evidence": payload,
    }


def write_low_vol_dividend_platform_evidence_draft(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_platform_evidence_draft(**kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / f"{payload['platform']}_live_enablement_evidence.draft.json"
    summary_path = output_dir / f"{payload['platform']}_platform_evidence_draft_summary.json"
    write_json(evidence_path, payload["evidence"])
    write_json(summary_path, {key: value for key, value in payload.items() if key != "evidence"})
    return {
        **payload,
        "evidence_path": str(evidence_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft platform live-enable evidence from an HK low-vol dry-run report.")
    parser.add_argument("--platform", required=True, choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--runtime-report", required=True, help="Local runtime report JSON generated by the platform dry-run.")
    parser.add_argument("--runtime-report-uri", default="", help="Stable gs://, s3://, or https:// URI for the runtime report.")
    parser.add_argument("--base-evidence-file", help="Optional existing evidence JSON to merge shared sections from.")
    parser.add_argument("--reconciliation-record", help="Optional local reconciliation record JSON with detailed orders.")
    parser.add_argument("--orders-previewed", type=int, help="Override previewed order count when the report lacks structured orders.")
    parser.add_argument("--lot-size-errors", type=int, default=0)
    parser.add_argument("--quote-snapshot-uri", default="")
    parser.add_argument("--quote-snapshot-file")
    parser.add_argument("--fee-breakdown-uri", default="")
    parser.add_argument("--fee-breakdown-file")
    parser.add_argument("--notification-delivery-log-uri", default="")
    parser.add_argument("--notification-correlation-id", default="")
    parser.add_argument("--adv-window-trading-days", type=int, default=0)
    parser.add_argument("--median-daily-turnover-hkd", type=float)
    parser.add_argument("--max-single-order-adv-fraction", type=float)
    parser.add_argument("--rebalance-adv-fraction", type=float)
    parser.add_argument("--confirm-order-preview-provenance", action="store_true")
    parser.add_argument("--confirm-notification-audit", action="store_true")
    parser.add_argument("--confirm-execution-capacity", action="store_true")
    parser.add_argument("--evidence-generated-at", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_platform_evidence_draft(
        output_dir=args.output_dir,
        platform=args.platform,
        runtime_report_path=args.runtime_report,
        runtime_report_uri=args.runtime_report_uri,
        base_evidence_file=args.base_evidence_file,
        reconciliation_record_path=args.reconciliation_record,
        orders_previewed=args.orders_previewed,
        lot_size_errors=args.lot_size_errors,
        quote_snapshot_uri=args.quote_snapshot_uri,
        quote_snapshot_file=args.quote_snapshot_file,
        fee_breakdown_uri=args.fee_breakdown_uri,
        fee_breakdown_file=args.fee_breakdown_file,
        notification_delivery_log_uri=args.notification_delivery_log_uri,
        notification_correlation_id=args.notification_correlation_id,
        adv_window_trading_days=args.adv_window_trading_days,
        median_daily_turnover_hkd=args.median_daily_turnover_hkd,
        max_single_order_adv_fraction=args.max_single_order_adv_fraction,
        rebalance_adv_fraction=args.rebalance_adv_fraction,
        confirm_order_preview_provenance=args.confirm_order_preview_provenance,
        confirm_notification_audit=args.confirm_notification_audit,
        confirm_execution_capacity=args.confirm_execution_capacity,
        evidence_generated_at=args.evidence_generated_at,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"platform={payload['platform']}")
        print(f"platform_dry_run_section_status={payload['platform_dry_run_section_status']}")
        print(f"live_enablement_allowed={payload['live_enablement_allowed']}")
        print(f"evidence_path={payload['evidence_path']}")
        print(f"summary_path={payload['summary_path']}")
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DRAFT_VERSION",
    "build_low_vol_dividend_platform_evidence_draft",
    "main",
    "write_low_vol_dividend_platform_evidence_draft",
]
