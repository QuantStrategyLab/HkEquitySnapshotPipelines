from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_platform_evidence_from_runtime import (
    BUILDER_VERSION,
    build_low_vol_dividend_platform_evidence_from_runtime,
    write_low_vol_dividend_platform_evidence_from_runtime,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_platform_evidence_from_runtime.py"


def _runtime_report(tmp_path: Path, *, include_fee: bool = True) -> Path:
    summary = {
        "orders_previewed": [
            {"symbol": "02800.HK", "side": "buy", "quantity": 100, "order_type": "market", "status": "dry_run"},
            {"symbol": "03033.HK", "side": "buy", "quantity": 200, "order_type": "limit", "limit_price": 20.0, "status": "dry_run"},
        ],
        "orders_previewed_count": 2,
        "quote_snapshot": {
            "quotes": [
                {"symbol": "02800.HK", "last_price": 30.0, "as_of": "2026-06-03T08:00:00Z"},
                {"symbol": "03033.HK", "last_price": 20.0, "as_of": "2026-06-03T08:00:00Z"},
            ],
        },
        "notification_delivery_log": {
            "notification_schema_version": "hk_live_enablement_notification.v1",
            "notification_event_type": "hk_snapshot_live_enablement_dry_run",
            "notification_correlation_id": "longbridge-dry-run-001",
            "locales": ["en", "zh-Hans"],
            "profile": "hk_low_vol_dividend_quality",
            "platform": "longbridge",
            "validation_status": "passed",
            "orders_previewed": 2,
            "notification_redacts_sensitive_fields": True,
            "delivery_events": [
                {
                    "sink": "telegram",
                    "delivery_status": "sent",
                    "compact_text_sha256": "a" * 64,
                    "compact_text_length": 42,
                }
            ],
        },
    }
    if include_fee:
        summary["fee_breakdown"] = {
            "currency": "HKD",
            "orders": [
                {"symbol": "02800.HK", "estimated_fee_hkd": 10.0},
                {"symbol": "03033.HK", "estimated_fee_hkd": 12.0},
            ],
        }
    path = tmp_path / "runtime-report.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "runtime_report.v1",
                "platform": "longbridge",
                "strategy_profile": "hk_low_vol_dividend_quality",
                "strategy_domain": "hk_equity",
                "run_id": "longbridge-dry-run-001",
                "run_source": "cloud_run",
                "status": "ok",
                "dry_run": True,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _build_kwargs(tmp_path: Path, **overrides):
    runtime_report_path = overrides.pop("runtime_report_path", None) or _runtime_report(tmp_path)
    kwargs = {
        "platform": "longbridge",
        "runtime_report_path": runtime_report_path,
        "runtime_report_uri": "gs://qsl-evidence/hk-low-vol/longbridge/runtime-report.json",
        "quote_snapshot_uri": "gs://qsl-evidence/hk-low-vol/longbridge/quotes.json",
        "fee_breakdown_uri": "gs://qsl-evidence/hk-low-vol/longbridge/fees.json",
        "notification_delivery_log_uri": "gs://qsl-evidence/hk-low-vol/longbridge/notification-log.json",
        "evidence_generated_at": "2026-06-03",
        "evidence_dir": tmp_path / "evidence",
        "output_dir": tmp_path / "out",
        "adv_window_trading_days": 20,
        "median_daily_turnover_hkd": 50_000_000,
        "max_single_order_adv_fraction": 0.01,
        "rebalance_adv_fraction": 0.05,
        "confirm_order_preview_provenance": True,
        "confirm_notification_audit": True,
        "confirm_execution_capacity": True,
    }
    kwargs.update(overrides)
    return kwargs


def test_platform_evidence_from_runtime_collects_support_and_writes_convention_file(tmp_path):
    payload = build_low_vol_dividend_platform_evidence_from_runtime(**_build_kwargs(tmp_path))

    assert payload["builder_version"] == BUILDER_VERSION
    assert payload["support_ready_for_platform_evidence_draft"] is True
    assert payload["support_statuses"] == {
        "raw_order_preview": "passed",
        "quote_snapshot": "passed",
        "fee_breakdown": "passed",
        "notification_delivery_log": "passed",
    }
    assert payload["platform_dry_run_section_status"] == "passed"
    assert Path(payload["support_paths"]["quote_snapshot_path"]).exists()
    assert Path(payload["support_paths"]["notification_delivery_log_path"]).exists()
    evidence_path = Path(payload["platform_evidence_path"])
    assert evidence_path == tmp_path / "evidence" / "longbridge_live_enablement_evidence.draft.json"
    assert json.loads(evidence_path.read_text(encoding="utf-8"))["platform_dry_run_order_preview"]["status"] == "passed"
    assert payload["platform_live_enablement_allowed"] is False


def test_platform_evidence_from_runtime_keeps_section_pending_when_support_missing(tmp_path):
    payload = build_low_vol_dividend_platform_evidence_from_runtime(
        **_build_kwargs(tmp_path, runtime_report_path=_runtime_report(tmp_path, include_fee=False)),
    )

    assert payload["support_ready_for_platform_evidence_draft"] is False
    assert payload["support_statuses"]["fee_breakdown"] == "missing"
    assert payload["platform_dry_run_section_status"] == "pending"


def test_write_platform_evidence_from_runtime_outputs_summary(tmp_path):
    payload = write_low_vol_dividend_platform_evidence_from_runtime(**_build_kwargs(tmp_path))

    assert Path(payload["summary_path"]).exists()
    summary = json.loads(Path(payload["summary_path"]).read_text(encoding="utf-8"))
    assert summary["platform"] == "longbridge"
    assert summary["platform_dry_run_section_status"] == "passed"


def test_platform_evidence_from_runtime_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "longbridge",
            "--runtime-report",
            str(_runtime_report(tmp_path)),
            "--runtime-report-uri",
            "gs://qsl-evidence/hk-low-vol/longbridge/runtime-report.json",
            "--quote-snapshot-uri",
            "gs://qsl-evidence/hk-low-vol/longbridge/quotes.json",
            "--fee-breakdown-uri",
            "gs://qsl-evidence/hk-low-vol/longbridge/fees.json",
            "--notification-delivery-log-uri",
            "gs://qsl-evidence/hk-low-vol/longbridge/notification-log.json",
            "--evidence-generated-at",
            "2026-06-03",
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--output-dir",
            str(tmp_path / "out"),
            "--adv-window-trading-days",
            "20",
            "--median-daily-turnover-hkd",
            "50000000",
            "--max-single-order-adv-fraction",
            "0.01",
            "--rebalance-adv-fraction",
            "0.05",
            "--confirm-order-preview-provenance",
            "--confirm-notification-audit",
            "--confirm-execution-capacity",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["platform"] == "longbridge"
    assert payload["support_ready_for_platform_evidence_draft"] is True
    assert payload["platform_dry_run_section_status"] == "passed"
    assert payload["platform_evidence_path"].endswith("longbridge_live_enablement_evidence.draft.json")
