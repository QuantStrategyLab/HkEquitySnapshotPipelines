from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hk_equity_snapshot_pipelines.low_vol_dividend_live_enablement_package import (
    LOW_VOL_DIVIDEND_PACKAGE_STATUS,
    LOW_VOL_DIVIDEND_PACKAGE_VERSION,
    build_low_vol_dividend_live_enablement_package,
    write_low_vol_dividend_live_enablement_package,
)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_low_vol_dividend_live_enablement_package.py"


def test_low_vol_dividend_package_is_first_candidate_but_not_live_enabled():
    payload = build_low_vol_dividend_live_enablement_package()

    assert payload["package_version"] == LOW_VOL_DIVIDEND_PACKAGE_VERSION
    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["status"] == LOW_VOL_DIVIDEND_PACKAGE_STATUS
    assert payload["runtime_enabled"] is False
    assert payload["live_enablement_allowed"] is False
    assert payload["production_deployment_allowed"] is False
    assert payload["dry_run_only_until_all_gates_pass"] is True
    assert payload["candidate_rank"] == 1
    assert payload["promotion_bucket"] == "first_snapshot_candidate"
    assert payload["platforms"] == ["longbridge", "ibkr"]
    assert payload["live_enablement_thresholds"]["max_allowed_backtest_drawdown"] == 0.30
    assert payload["live_enablement_thresholds"]["min_required_oos_fold_count"] == 3
    assert payload["live_enablement_thresholds"]["max_allowed_annualized_turnover"] == 1.00
    assert "strategy_policy_evidence" in payload["required_evidence_sections"]
    assert "hkeq-validate-snapshot-artifact-pack" in payload["commands"]["artifact_pack_validation"]
    assert "hkeq-validate-live-enable-evidence" in payload["commands"]["live_enablement_evidence_validation"]
    assert payload["platform_env_templates"]["longbridge"]["LONGBRIDGE_DRY_RUN_ONLY"] == "true"
    assert payload["platform_env_templates"]["ibkr"]["IBKR_DRY_RUN_ONLY"] == "true"
    assert any(item["section"] == "longbridge_live_enablement_evidence" for item in payload["required_evidence_files"])
    assert any(item["section"] == "ibkr_live_enablement_evidence" for item in payload["required_evidence_files"])
    assert "any_oos_fold_drawdown_above_30_percent" in payload["stop_conditions"]


def test_low_vol_dividend_package_writes_json_and_markdown(tmp_path):
    payload = write_low_vol_dividend_live_enablement_package(output_dir=tmp_path, platforms=("longbridge",))

    json_path = Path(payload["json_path"])
    markdown_path = Path(payload["markdown_path"])
    assert json_path.exists()
    assert markdown_path.exists()

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert saved["platforms"] == ["longbridge"]
    assert saved["runtime_enabled"] is False
    assert "does not enable live trading" in markdown
    assert "Max drawdown" in markdown
    assert "`longbridge`" in markdown


def test_low_vol_dividend_package_cli_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--json", "--platform", "ibkr"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["platforms"] == ["ibkr"]
    assert payload["platform_env_templates"]["ibkr"]["IBKR_DRY_RUN_ONLY"] == "true"
