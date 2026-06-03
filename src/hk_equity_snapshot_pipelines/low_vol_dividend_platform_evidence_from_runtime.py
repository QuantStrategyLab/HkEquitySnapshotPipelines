from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .low_vol_dividend_dry_run_support_artifacts import write_low_vol_dividend_dry_run_support_artifacts
from .low_vol_dividend_platform_evidence import write_low_vol_dividend_platform_evidence_draft
from .low_vol_dividend_live_enablement_gate import DEFAULT_EVIDENCE_DIR
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_platform_evidence_from_runtime")
DEFAULT_SUPPORT_SUBDIR = "support"
BUILDER_VERSION = "hk_low_vol_dividend_quality_snapshot.platform_evidence_from_runtime.v1"


def build_low_vol_dividend_platform_evidence_from_runtime(
    *,
    platform: str,
    runtime_report_path: str | Path,
    evidence_generated_at: str,
    evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    support_output_dir: str | Path | None = None,
    runtime_report_uri: str = "",
    quote_snapshot_uri: str = "",
    fee_breakdown_uri: str = "",
    notification_delivery_log_uri: str = "",
    external_quote_snapshot_file: str | Path | None = None,
    external_fee_breakdown_file: str | Path | None = None,
    base_evidence_file: str | Path | None = None,
    notification_correlation_id: str = "",
    orders_previewed: int | None = None,
    lot_size_errors: int = 0,
    adv_window_trading_days: int = 0,
    median_daily_turnover_hkd: float | None = None,
    max_single_order_adv_fraction: float | None = None,
    rebalance_adv_fraction: float | None = None,
    confirm_order_preview_provenance: bool = False,
    confirm_notification_audit: bool = False,
    confirm_execution_capacity: bool = False,
) -> dict[str, Any]:
    evidence_dir = Path(evidence_dir)
    output_dir = Path(output_dir)
    support_dir = Path(support_output_dir) if support_output_dir is not None else evidence_dir / DEFAULT_SUPPORT_SUBDIR / platform
    support = write_low_vol_dividend_dry_run_support_artifacts(
        output_dir=support_dir,
        platform=platform,
        runtime_report_path=runtime_report_path,
        quote_snapshot_file=external_quote_snapshot_file,
        fee_breakdown_file=external_fee_breakdown_file,
        evidence_generated_at=evidence_generated_at,
    )
    platform_draft = write_low_vol_dividend_platform_evidence_draft(
        output_dir=evidence_dir,
        platform=platform,
        runtime_report_path=runtime_report_path,
        runtime_report_uri=runtime_report_uri,
        base_evidence_file=base_evidence_file,
        orders_previewed=orders_previewed,
        lot_size_errors=lot_size_errors,
        quote_snapshot_uri=quote_snapshot_uri,
        quote_snapshot_file=support["quote_snapshot_path"],
        fee_breakdown_uri=fee_breakdown_uri,
        fee_breakdown_file=support["fee_breakdown_path"],
        notification_delivery_log_uri=notification_delivery_log_uri,
        notification_delivery_log_file=support["notification_delivery_log_path"],
        notification_correlation_id=notification_correlation_id,
        adv_window_trading_days=adv_window_trading_days,
        median_daily_turnover_hkd=median_daily_turnover_hkd,
        max_single_order_adv_fraction=max_single_order_adv_fraction,
        rebalance_adv_fraction=rebalance_adv_fraction,
        confirm_order_preview_provenance=confirm_order_preview_provenance,
        confirm_notification_audit=confirm_notification_audit,
        confirm_execution_capacity=confirm_execution_capacity,
        evidence_generated_at=evidence_generated_at,
    )
    return {
        "builder_version": BUILDER_VERSION,
        "platform": platform_draft["platform"],
        "profile": platform_draft["profile"],
        "runtime_report_path": str(runtime_report_path),
        "runtime_report_uri": runtime_report_uri,
        "evidence_dir": str(evidence_dir),
        "output_dir": str(output_dir),
        "support_output_dir": str(support_dir),
        "support_statuses": support["support_statuses"],
        "support_ready_for_platform_evidence_draft": bool(support["ready_for_platform_evidence_draft"]),
        "platform_dry_run_section_status": platform_draft["platform_dry_run_section_status"],
        "platform_live_enablement_allowed": bool(platform_draft["live_enablement_allowed"]),
        "platform_validation_status": platform_draft["validation_status"],
        "platform_validation_errors_count": platform_draft["validation_errors_count"],
        "platform_validation_errors_preview": platform_draft["validation_errors_preview"],
        "support_paths": {
            "raw_order_preview_path": support["raw_order_preview_path"],
            "quote_snapshot_path": support["quote_snapshot_path"],
            "fee_breakdown_path": support["fee_breakdown_path"],
            "notification_delivery_log_path": support["notification_delivery_log_path"],
            "summary_path": support["summary_path"],
        },
        "platform_evidence_path": platform_draft["evidence_path"],
        "platform_summary_path": platform_draft["summary_path"],
        "next_gate_command": (
            "hkeq-run-low-vol-dividend-live-enable-gate "
            f"--evidence-dir {evidence_dir} --json"
        ),
    }


def write_low_vol_dividend_platform_evidence_from_runtime(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_platform_evidence_from_runtime(output_dir=output_dir, **kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / f"{payload['platform']}_platform_evidence_from_runtime_summary.json"
    write_json(summary_path, payload)
    return {
        **payload,
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft HK low-vol platform evidence directly from a dry-run runtime report.")
    parser.add_argument("--platform", required=True, choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--runtime-report", required=True)
    parser.add_argument("--runtime-report-uri", default="")
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--support-output-dir")
    parser.add_argument("--base-evidence-file")
    parser.add_argument("--external-quote-snapshot-file")
    parser.add_argument("--external-fee-breakdown-file")
    parser.add_argument("--quote-snapshot-uri", default="")
    parser.add_argument("--fee-breakdown-uri", default="")
    parser.add_argument("--notification-delivery-log-uri", default="")
    parser.add_argument("--notification-correlation-id", default="")
    parser.add_argument("--orders-previewed", type=int)
    parser.add_argument("--lot-size-errors", type=int, default=0)
    parser.add_argument("--adv-window-trading-days", type=int, default=0)
    parser.add_argument("--median-daily-turnover-hkd", type=float)
    parser.add_argument("--max-single-order-adv-fraction", type=float)
    parser.add_argument("--rebalance-adv-fraction", type=float)
    parser.add_argument("--confirm-order-preview-provenance", action="store_true")
    parser.add_argument("--confirm-notification-audit", action="store_true")
    parser.add_argument("--confirm-execution-capacity", action="store_true")
    parser.add_argument("--evidence-generated-at", required=True)
    parser.add_argument("--fail-on-pending", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_platform_evidence_from_runtime(
        output_dir=args.output_dir,
        platform=args.platform,
        runtime_report_path=args.runtime_report,
        runtime_report_uri=args.runtime_report_uri,
        evidence_dir=args.evidence_dir,
        support_output_dir=args.support_output_dir,
        base_evidence_file=args.base_evidence_file,
        external_quote_snapshot_file=args.external_quote_snapshot_file,
        external_fee_breakdown_file=args.external_fee_breakdown_file,
        quote_snapshot_uri=args.quote_snapshot_uri,
        fee_breakdown_uri=args.fee_breakdown_uri,
        notification_delivery_log_uri=args.notification_delivery_log_uri,
        notification_correlation_id=args.notification_correlation_id,
        orders_previewed=args.orders_previewed,
        lot_size_errors=args.lot_size_errors,
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
        print(f"support_ready_for_platform_evidence_draft={payload['support_ready_for_platform_evidence_draft']}")
        print(f"platform_dry_run_section_status={payload['platform_dry_run_section_status']}")
        print(f"platform_evidence_path={payload['platform_evidence_path']}")
        print(f"summary_path={payload['summary_path']}")
    if args.fail_on_pending and payload["platform_dry_run_section_status"] != "passed":
        return 1
    return 0


__all__ = [
    "BUILDER_VERSION",
    "DEFAULT_OUTPUT_DIR",
    "build_low_vol_dividend_platform_evidence_from_runtime",
    "main",
    "write_low_vol_dividend_platform_evidence_from_runtime",
]
