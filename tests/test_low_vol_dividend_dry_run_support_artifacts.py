from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_dry_run_support_artifacts import (
    SUPPORT_ARTIFACT_VERSION,
    build_low_vol_dividend_dry_run_support_artifacts,
    write_low_vol_dividend_dry_run_support_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect_low_vol_dividend_dry_run_support_artifacts.py"


def _runtime_report(tmp_path: Path, *, include_quote: bool = True, include_fee: bool = True) -> Path:
    summary = {
        "orders_previewed": [
            {"symbol": "02800.HK", "side": "buy", "quantity": 100, "order_type": "market", "status": "dry_run"},
            {"symbol": "03033.HK", "side": "buy", "quantity": 200, "order_type": "limit", "limit_price": 20.0, "status": "dry_run"},
        ],
        "orders_previewed_count": 2,
    }
    if include_quote:
        summary["quote_snapshot"] = {
            "quotes": [
                {"symbol": "02800.HK", "last_price": 30.0, "as_of": "2026-06-03T08:00:00Z"},
                {"symbol": "03033.HK", "last_price": 20.0, "as_of": "2026-06-03T08:00:00Z"},
            ],
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


def test_build_dry_run_support_artifacts_accepts_complete_runtime_report(tmp_path):
    payload = build_low_vol_dividend_dry_run_support_artifacts(
        platform="longbridge",
        runtime_report_path=_runtime_report(tmp_path),
        evidence_generated_at="2026-06-03",
    )

    assert payload["support_artifact_version"] == SUPPORT_ARTIFACT_VERSION
    assert payload["ready_for_platform_evidence_draft"] is True
    assert payload["support_statuses"] == {
        "raw_order_preview": "passed",
        "quote_snapshot": "passed",
        "fee_breakdown": "passed",
    }
    assert payload["raw_order_preview"]["orders_previewed"] == 2
    assert payload["quote_snapshot"]["missing_symbols"] == []


def test_build_dry_run_support_artifacts_does_not_fabricate_missing_quote_or_fee(tmp_path):
    payload = build_low_vol_dividend_dry_run_support_artifacts(
        platform="longbridge",
        runtime_report_path=_runtime_report(tmp_path, include_quote=False, include_fee=False),
        evidence_generated_at="2026-06-03",
    )

    assert payload["ready_for_platform_evidence_draft"] is False
    assert payload["support_statuses"]["raw_order_preview"] == "passed"
    assert payload["support_statuses"]["quote_snapshot"] == "missing"
    assert payload["support_statuses"]["fee_breakdown"] == "missing"
    assert payload["quote_snapshot"]["quote_snapshot"] == {}
    assert payload["fee_breakdown"]["fee_breakdown"] == {}


def test_write_dry_run_support_artifacts_outputs_files_and_command(tmp_path):
    payload = write_low_vol_dividend_dry_run_support_artifacts(
        output_dir=tmp_path / "out",
        platform="longbridge",
        runtime_report_path=_runtime_report(tmp_path),
        evidence_generated_at="2026-06-03",
    )

    assert Path(payload["raw_order_preview_path"]).exists()
    assert Path(payload["quote_snapshot_path"]).exists()
    assert Path(payload["fee_breakdown_path"]).exists()
    assert Path(payload["summary_path"]).exists()
    assert "hkeq-draft-low-vol-dividend-platform-evidence" in payload["suggested_platform_evidence_command"]


def test_dry_run_support_artifacts_cli_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--platform",
            "longbridge",
            "--runtime-report",
            str(_runtime_report(tmp_path)),
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

    assert payload["platform"] == "longbridge"
    assert payload["ready_for_platform_evidence_draft"] is True
    assert payload["quote_snapshot_path"].endswith("longbridge_quote_snapshot.json")
