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
from .notification_audit_policy import NOTIFICATION_SCHEMA_VERSION, SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_platform_evidence")
DRAFT_VERSION = "hk_low_vol_dividend_quality.platform_evidence_draft.v1"
RUNTIME_REPORT_PLATFORM_ALIASES = {
    "ibkr": {"ibkr", "interactive_brokers"},
    "longbridge": {"longbridge"},
}
SUPPORT_ARTIFACT_TYPE_PREFIX = "hk_low_vol_dividend_quality.dry_run_support"
SENSITIVE_NOTIFICATION_FIELD_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "jwt",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
)
SENSITIVE_NOTIFICATION_VALUE_MARKERS = (
    "bearer ",
    "gho_",
    "github_pat_",
    "sk-",
    "xoxb-",
)
REDACTED_MARKERS = ("***", "redacted", "[redacted]", "<redacted>")


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


def _support_artifact_passed(path: str | Path | None) -> bool:
    if path is None:
        return False
    resolved = Path(path)
    if not resolved.exists():
        return False
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return True
    if not isinstance(payload, Mapping):
        return True
    artifact_type = str(payload.get("artifact_type") or "").strip()
    if artifact_type.startswith(SUPPORT_ARTIFACT_TYPE_PREFIX):
        return str(payload.get("status") or "").strip().lower() == "passed"
    return True


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).lower()


def _bool_field(payload: Mapping[str, Any], *fields: str) -> bool:
    return any(payload.get(field) is True for field in fields)


def _is_redacted(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return True
    return any(marker in text for marker in REDACTED_MARKERS)


def _contains_unredacted_sensitive_value(value: Any, *, field_name: str = "") -> bool:
    lowered_field_name = field_name.lower()
    if isinstance(value, Mapping):
        return any(
            _contains_unredacted_sensitive_value(item, field_name=str(key))
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_unredacted_sensitive_value(item, field_name=field_name) for item in value)
    if isinstance(value, tuple):
        return any(_contains_unredacted_sensitive_value(item, field_name=field_name) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        sensitive_field = any(marker in lowered_field_name for marker in SENSITIVE_NOTIFICATION_FIELD_MARKERS)
        if sensitive_field and not _is_redacted(value):
            return True
        if any(marker in lowered for marker in SENSITIVE_NOTIFICATION_VALUE_MARKERS) and not _is_redacted(value):
            return True
    return False


def _notification_locale_present(payload: Mapping[str, Any], *, locale: str) -> bool:
    if locale == "en" and _bool_field(payload, "notification_locale_en", "locale_en"):
        return True
    if locale == "zh_hans" and _bool_field(payload, "notification_locale_zh_hans", "locale_zh_hans"):
        return True
    accepted = {"en": {"en", "en-us", "en_us"}, "zh_hans": {"zh-hans", "zh_hans", "zh-cn", "zh_cn", "zh"}}[
        locale
    ]
    locales = payload.get("locales") or payload.get("delivered_locales")
    if isinstance(locales, list) and any(str(item).strip().lower() in accepted for item in locales):
        return True
    messages = payload.get("messages") or payload.get("localized_messages")
    if isinstance(messages, Mapping) and any(str(key).strip().lower() in accepted for key in messages):
        return True
    deliveries = payload.get("deliveries") or payload.get("events")
    if isinstance(deliveries, list):
        for item in deliveries:
            if not isinstance(item, Mapping):
                continue
            item_locale = str(item.get("locale") or item.get("language") or "").strip().lower()
            if item_locale in accepted:
                return True
    return False


def _notification_log_audit(
    *,
    notification_delivery_log_file: str | Path | None,
    platform: str,
    profile: str,
    expected_correlation_id: str,
    orders_previewed: int,
) -> dict[str, Any]:
    if notification_delivery_log_file is None:
        return {
            "status": "pending",
            "sha256": "",
            "errors": ["notification_delivery_log_file is required for live-enable platform evidence"],
            "payload": {},
            "notification_correlation_id": expected_correlation_id,
            "notification_locale_en": False,
            "notification_locale_zh_hans": False,
            "notification_contains_profile": False,
            "notification_contains_platform": False,
            "notification_contains_validation_status": False,
            "notification_contains_order_preview_summary": False,
            "notification_redacts_sensitive_fields": False,
        }
    path = Path(notification_delivery_log_file)
    payload = _read_json(path)
    artifact_type = str(payload.get("artifact_type") or "").strip()
    if artifact_type.startswith(f"{SUPPORT_ARTIFACT_TYPE_PREFIX}.notification_delivery_log."):
        if str(payload.get("status") or "").strip().lower() != "passed":
            return {
                "status": "pending",
                "sha256": sha256_file(path),
                "errors": ["notification_delivery_log support artifact status must be passed"],
                "payload": payload,
                "notification_correlation_id": expected_correlation_id,
                "notification_locale_en": False,
                "notification_locale_zh_hans": False,
                "notification_contains_profile": False,
                "notification_contains_platform": False,
                "notification_contains_validation_status": False,
                "notification_contains_order_preview_summary": False,
                "notification_redacts_sensitive_fields": False,
            }
        nested_payload = payload.get("notification_delivery_log")
        if not isinstance(nested_payload, Mapping):
            return {
                "status": "pending",
                "sha256": sha256_file(path),
                "errors": ["notification_delivery_log support artifact must contain a notification_delivery_log object"],
                "payload": payload,
                "notification_correlation_id": expected_correlation_id,
                "notification_locale_en": False,
                "notification_locale_zh_hans": False,
                "notification_contains_profile": False,
                "notification_contains_platform": False,
                "notification_contains_validation_status": False,
                "notification_contains_order_preview_summary": False,
                "notification_redacts_sensitive_fields": False,
            }
        payload = nested_payload
    text = _json_text(payload)
    correlation_id = str(
        payload.get("notification_correlation_id")
        or payload.get("correlation_id")
        or expected_correlation_id
        or ""
    ).strip()
    profile_present = _bool_field(payload, "notification_contains_profile") or profile.lower() in text
    platform_aliases = RUNTIME_REPORT_PLATFORM_ALIASES.get(platform, {platform})
    platform_present = _bool_field(payload, "notification_contains_platform") or any(alias in text for alias in platform_aliases)
    validation_status_present = _bool_field(payload, "notification_contains_validation_status") or any(
        marker in text
        for marker in (
            "validation_status",
            "live_enablement_allowed",
            "platform_dry_run_section_status",
            "passed",
            "pending",
            "blocked",
        )
    )
    order_preview_present = _bool_field(payload, "notification_contains_order_preview_summary") or (
        ("order_preview" in text or "orders_previewed" in text or "orders" in text)
        and (orders_previewed <= 0 or str(orders_previewed) in text)
    )
    redacts_sensitive_fields = (
        _bool_field(payload, "notification_redacts_sensitive_fields", "redacts_sensitive_fields")
        and not _contains_unredacted_sensitive_value(payload)
    )
    checks = {
        "notification_locale_en": _notification_locale_present(payload, locale="en"),
        "notification_locale_zh_hans": _notification_locale_present(payload, locale="zh_hans"),
        "notification_contains_profile": profile_present,
        "notification_contains_platform": platform_present,
        "notification_contains_validation_status": validation_status_present,
        "notification_contains_order_preview_summary": order_preview_present,
        "notification_redacts_sensitive_fields": redacts_sensitive_fields,
    }
    errors: list[str] = []
    if payload.get("notification_schema_version") != NOTIFICATION_SCHEMA_VERSION:
        errors.append("notification_schema_version must match the live-enable notification schema")
    if payload.get("notification_event_type") != SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE:
        errors.append("notification_event_type must match the HK snapshot dry-run event type")
    if not correlation_id:
        errors.append("notification_correlation_id is required")
    elif expected_correlation_id and correlation_id != expected_correlation_id:
        errors.append("notification_correlation_id must match the dry-run correlation id")
    for field, passed in checks.items():
        if not passed:
            errors.append(f"{field} must be true in the delivery log audit")
    return {
        "status": "passed" if not errors else "pending",
        "sha256": sha256_file(path),
        "errors": errors,
        "payload": payload,
        "notification_correlation_id": correlation_id,
        **checks,
    }


def _normalize_platform(platform: str) -> str:
    normalized = str(platform or "").strip().lower()
    if normalized not in SUPPORTED_SNAPSHOT_PLATFORMS:
        known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
        raise ValueError(f"Unsupported snapshot platform {platform!r}; known platforms: {known}")
    return normalized


def _infer_orders(runtime_report: Mapping[str, Any], reconciliation_record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    summary = _as_mapping(runtime_report.get("summary"))
    candidates = (
        summary.get("orders_previewed"),
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
    for field in ("orders_previewed_count", "orders_submitted_count", "orders_previewed"):
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
    runtime_platform = str(runtime_report.get("platform") or "").strip().lower()
    accepted_platforms = RUNTIME_REPORT_PLATFORM_ALIASES.get(platform, {platform})
    if runtime_report.get("dry_run") is not True:
        errors.append("runtime_report.dry_run must be true")
    if str(runtime_report.get("status") or "").strip().lower() != "ok":
        errors.append("runtime_report.status must be 'ok'")
    if runtime_platform not in accepted_platforms:
        accepted = ", ".join(repr(item) for item in sorted(accepted_platforms))
        errors.append(f"runtime_report.platform must be one of {accepted}")
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
    notification_delivery_log_file: str | Path | None = None,
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
    quote_snapshot_artifact_passed = _support_artifact_passed(quote_snapshot_file)
    fee_breakdown_artifact_passed = _support_artifact_passed(fee_breakdown_file)
    report_ok, report_errors = _runtime_report_checks(
        runtime_report,
        platform=normalized_platform,
        profile=contract.profile,
    )
    resolved_notification_correlation_id = str(notification_correlation_id or runtime_report.get("run_id") or "")
    notification_log_audit = _notification_log_audit(
        notification_delivery_log_file=notification_delivery_log_file,
        platform=normalized_platform,
        profile=contract.profile,
        expected_correlation_id=resolved_notification_correlation_id,
        orders_previewed=resolved_orders_previewed,
    )
    notification_log_artifact_passed = notification_log_audit["status"] == "passed"

    section = dict(payload.get("platform_dry_run_order_preview") or {})
    section.update(
        {
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": raw_order_preview_uri,
            "orders_previewed": resolved_orders_previewed,
            "fractional_share_errors": fractional_share_errors,
            "lot_size_errors": int(lot_size_errors),
            "notification_sent": bool(notification_delivery_log_uri),
            "notification_correlation_id": notification_log_audit["notification_correlation_id"],
            "notification_locale_en": bool(notification_log_audit["notification_locale_en"]),
            "notification_locale_zh_hans": bool(notification_log_audit["notification_locale_zh_hans"]),
            "notification_contains_profile": bool(notification_log_audit["notification_contains_profile"]),
            "notification_contains_platform": bool(notification_log_audit["notification_contains_platform"]),
            "notification_contains_validation_status": bool(notification_log_audit["notification_contains_validation_status"]),
            "notification_contains_order_preview_summary": bool(
                notification_log_audit["notification_contains_order_preview_summary"],
            ),
            "notification_redacts_sensitive_fields": bool(notification_log_audit["notification_redacts_sensitive_fields"]),
            "notification_delivery_log_uri": _stable_uri(notification_delivery_log_uri),
            "notification_delivery_log_sha256": notification_log_audit["sha256"],
            "notification_log_artifact_status": notification_log_audit["status"],
            "notification_log_artifact_errors": notification_log_audit["errors"],
            "notification_operator_confirmed": bool(confirm_notification_audit),
            "dry_run_session_id": str(runtime_report.get("run_id") or ""),
            "raw_order_preview_uri": raw_order_preview_uri,
            "raw_order_preview_sha256": raw_order_preview_sha256,
            "quote_snapshot_uri": _stable_uri(quote_snapshot_uri),
            "quote_snapshot_sha256": quote_snapshot_sha256,
            "quote_snapshot_artifact_status": "passed" if quote_snapshot_artifact_passed else "pending",
            "fee_breakdown_uri": _stable_uri(fee_breakdown_uri),
            "fee_breakdown_sha256": fee_breakdown_sha256,
            "fee_breakdown_artifact_status": "passed" if fee_breakdown_artifact_passed else "pending",
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
                notification_log_audit["sha256"],
                section.get("dry_run_session_id"),
            ),
            quote_snapshot_artifact_passed,
            fee_breakdown_artifact_passed,
            notification_log_artifact_passed,
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
        "quote_snapshot_artifact_passed": quote_snapshot_artifact_passed,
        "fee_breakdown_artifact_passed": fee_breakdown_artifact_passed,
        "notification_log_artifact_passed": notification_log_artifact_passed,
        "notification_log_artifact_errors": notification_log_audit["errors"],
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
    parser.add_argument("--notification-delivery-log-file")
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
        notification_delivery_log_file=args.notification_delivery_log_file,
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
    "RUNTIME_REPORT_PLATFORM_ALIASES",
    "SUPPORT_ARTIFACT_TYPE_PREFIX",
    "build_low_vol_dividend_platform_evidence_draft",
    "main",
    "write_low_vol_dividend_platform_evidence_draft",
]
