from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_platform_evidence import (
    DRAFT_VERSION,
    build_low_vol_dividend_platform_evidence_draft,
    write_low_vol_dividend_platform_evidence_draft,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "draft_low_vol_dividend_platform_evidence.py"


def _runtime_report(tmp_path: Path, *, platform: str = "ibkr", dry_run: bool = True, status: str = "ok") -> Path:
    path = tmp_path / f"{platform}_runtime_report.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "runtime_report.v1",
                "platform": platform,
                "strategy_profile": "hk_low_vol_dividend_quality",
                "strategy_domain": "hk_equity",
                "run_id": f"{platform}-run-001",
                "run_source": "cloud_run",
                "status": status,
                "dry_run": dry_run,
                "summary": {
                    "orders_previewed_count": 2,
                },
                "artifacts": {},
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _artifact(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_platform_evidence_draft_fills_dry_run_section_but_full_evidence_remains_blocked(tmp_path):
    report_path = _runtime_report(tmp_path, platform="ibkr")
    quote_path = _artifact(tmp_path / "quotes.json", {"symbols": ["00941", "00002"]})
    fee_path = _artifact(tmp_path / "fees.json", {"orders": 2, "currency": "HKD"})

    payload = build_low_vol_dividend_platform_evidence_draft(
        platform="ibkr",
        runtime_report_path=report_path,
        runtime_report_uri="gs://qsl-evidence/hk-low-vol/ibkr/runtime-report.json",
        quote_snapshot_uri="gs://qsl-evidence/hk-low-vol/ibkr/quotes.json",
        quote_snapshot_file=quote_path,
        fee_breakdown_uri="gs://qsl-evidence/hk-low-vol/ibkr/fees.json",
        fee_breakdown_file=fee_path,
        notification_delivery_log_uri="gs://qsl-evidence/hk-low-vol/ibkr/notification-log.json",
        notification_correlation_id="ibkr-run-001",
        adv_window_trading_days=20,
        median_daily_turnover_hkd=50_000_000,
        max_single_order_adv_fraction=0.01,
        rebalance_adv_fraction=0.05,
        confirm_order_preview_provenance=True,
        confirm_notification_audit=True,
        confirm_execution_capacity=True,
        evidence_generated_at="2026-06-03",
    )

    section = payload["evidence"]["platform_dry_run_order_preview"]
    assert payload["draft_version"] == DRAFT_VERSION
    assert payload["runtime_report_checks_passed"] is True
    assert payload["orders_previewed"] == 2
    assert payload["platform_dry_run_section_status"] == "passed"
    assert section["raw_order_preview_sha256"]
    assert section["quote_snapshot_sha256"]
    assert section["fee_breakdown_sha256"]
    assert section["notification_locale_en"] is True
    assert payload["live_enablement_allowed"] is False
    assert payload["validation_errors_count"] > 0


def test_platform_evidence_accepts_ibkr_runtime_report_platform_alias(tmp_path):
    report_path = _runtime_report(tmp_path, platform="interactive_brokers")

    payload = build_low_vol_dividend_platform_evidence_draft(
        platform="ibkr",
        runtime_report_path=report_path,
        runtime_report_uri="gs://qsl-evidence/hk-low-vol/ibkr/runtime-report.json",
        orders_previewed=1,
        evidence_generated_at="2026-06-03",
    )

    assert payload["runtime_report_checks_passed"] is True
    assert payload["runtime_report_errors"] == []
    assert payload["platform"] == "ibkr"


def test_platform_evidence_reads_longbridge_structured_order_previews(tmp_path):
    report_path = _runtime_report(tmp_path, platform="longbridge")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["summary"]["orders_previewed_count"] = 0
    report["summary"]["orders_previewed"] = [
        {"symbol": "02800.HK", "side": "buy", "quantity": 100, "status": "dry_run"},
        {"symbol": "03033.HK", "side": "buy", "quantity": 200, "status": "dry_run"},
    ]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    payload = build_low_vol_dividend_platform_evidence_draft(
        platform="longbridge",
        runtime_report_path=report_path,
        runtime_report_uri="gs://qsl-evidence/hk-low-vol/longbridge/runtime-report.json",
        evidence_generated_at="2026-06-03",
    )

    assert payload["runtime_report_checks_passed"] is True
    assert payload["orders_previewed"] == 2
    assert payload["platform"] == "longbridge"


def test_platform_evidence_draft_keeps_section_pending_when_runtime_report_is_not_dry_run(tmp_path):
    report_path = _runtime_report(tmp_path, platform="longbridge", dry_run=False)

    payload = build_low_vol_dividend_platform_evidence_draft(
        platform="longbridge",
        runtime_report_path=report_path,
        runtime_report_uri="gs://qsl-evidence/hk-low-vol/longbridge/runtime-report.json",
        orders_previewed=1,
        evidence_generated_at="2026-06-03",
    )

    assert payload["runtime_report_checks_passed"] is False
    assert "runtime_report.dry_run must be true" in payload["runtime_report_errors"]
    assert payload["platform_dry_run_section_status"] == "pending"
    assert payload["evidence"]["platform_dry_run_order_preview"]["status"] == "pending"


def test_write_platform_evidence_draft_outputs_evidence_and_summary(tmp_path):
    report_path = _runtime_report(tmp_path, platform="longbridge")

    payload = write_low_vol_dividend_platform_evidence_draft(
        output_dir=tmp_path / "out",
        platform="longbridge",
        runtime_report_path=report_path,
        runtime_report_uri="gs://qsl-evidence/hk-low-vol/longbridge/runtime-report.json",
        orders_previewed=1,
        evidence_generated_at="2026-06-03",
    )

    evidence_path = Path(payload["evidence_path"])
    summary_path = Path(payload["summary_path"])
    assert evidence_path.exists()
    assert summary_path.exists()
    assert json.loads(evidence_path.read_text(encoding="utf-8"))["platform"] == "longbridge"
    assert "evidence" not in json.loads(summary_path.read_text(encoding="utf-8"))


def test_platform_evidence_cli_json(tmp_path):
    report_path = _runtime_report(tmp_path, platform="ibkr")
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "ibkr",
            "--runtime-report",
            str(report_path),
            "--runtime-report-uri",
            "gs://qsl-evidence/hk-low-vol/ibkr/runtime-report.json",
            "--evidence-generated-at",
            "2026-06-03",
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["platform"] == "ibkr"
    assert payload["evidence_path"].endswith("ibkr_live_enablement_evidence.draft.json")
    assert payload["live_enablement_allowed"] is False
