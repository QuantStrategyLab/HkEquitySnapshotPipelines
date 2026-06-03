from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from hk_equity_snapshot_pipelines.contracts import list_profile_contracts
from hk_equity_snapshot_pipelines.snapshot_promotion_matrix import (
    BACKTEST_VALIDATION_POLICY_VERSION,
    CURATED_SNAPSHOT_STRATEGY_RANKING_VERSION,
    SNAPSHOT_PROMOTION_GATE,
    build_curated_snapshot_strategy_ranking,
    build_momentum_live_enablement_comparison,
    build_snapshot_promotion_matrix,
    build_snapshot_promotion_row,
    list_snapshot_promotion_candidates,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "print_snapshot_promotion_matrix.py"


def test_snapshot_promotion_matrix_covers_only_retained_contract_profile():
    matrix = build_snapshot_promotion_matrix()
    contract_profiles = {contract.profile for contract in list_profile_contracts()}
    matrix_profiles = {row["profile"] for row in matrix["profiles"]}

    assert contract_profiles == {"hk_low_vol_dividend_quality_snapshot"}
    assert matrix_profiles == contract_profiles
    assert matrix["profile_count"] == 1
    assert matrix["runtime_enabled_count"] == 0
    assert matrix["blocked_profile_count"] == 1
    assert matrix["active_live_enablement_candidate_count"] == 1
    assert matrix["deferred_proxy_retest_candidate_count"] == 0
    assert matrix["research_only_scaffold_count"] == 0
    assert matrix["first_snapshot_candidates"] == ["hk_low_vol_dividend_quality_snapshot"]
    assert matrix["recommended_live_enablement_sequence"] == ["hk_low_vol_dividend_quality_snapshot"]
    assert matrix["research_only_scaffold_sequence"] == []
    assert "hk_shareholder_yield_quality" in {row["profile"] for row in matrix["rejected_snapshot_profiles"]}
    assert matrix["backtest_validation_policy"]["policy_version"] == BACKTEST_VALIDATION_POLICY_VERSION
    assert matrix["backtest_validation_policy"]["max_allowed_drawdown"] == 0.30
    assert matrix["backtest_validation_policy"]["min_return_to_drawdown_ratio"] == 0.50
    assert matrix["backtest_validation_policy"]["min_required_oos_fold_count"] == 3
    assert matrix["evidence_uri_policy"]["allowed_schemes"] == ["gs://", "https://", "s3://"]
    assert matrix["artifact_provenance_policy"]["required"] is True
    assert matrix["notification_audit_policy"]["schema_version"] == "hk_live_enablement_notification.v1"


def test_snapshot_promotion_row_for_retained_profile():
    row = build_snapshot_promotion_row("hk_low_vol_dividend_quality_snapshot")

    assert row["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert row["priority"] == 1
    assert row["promotion_scope"] == "first_snapshot_live_enablement_candidate"
    assert row["live_enablement_work_queue"] is True
    assert row["requires_full_backtest_now"] is True
    assert row["live_enablement_gate"] == SNAPSHOT_PROMOTION_GATE
    assert row["contract_version"] == "hk_low_vol_dividend_quality_snapshot.factor_snapshot.v1"
    assert row["artifact_filenames"]["snapshot"] == "hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv"
    assert row["quality_yield_live_enablement_policy"]["policy_version"] == (
        "hk_snapshot_quality_yield_live_enablement_policy.v1"
    )


def test_snapshot_promotion_row_rejects_removed_profile():
    with pytest.raises(ValueError, match="Unknown snapshot profile"):
        build_snapshot_promotion_row("hk_shareholder_yield_quality")


def test_curated_snapshot_strategy_ranking_keeps_only_low_vol_active():
    ranking = build_curated_snapshot_strategy_ranking()

    assert ranking["ranking_version"] == CURATED_SNAPSHOT_STRATEGY_RANKING_VERSION
    assert ranking["live_enablement_allowed_without_evidence"] is False
    assert ranking["max_allowed_drawdown"] == 0.30
    assert [row["profile"] for row in ranking["ranking"]] == ["hk_low_vol_dividend_quality_snapshot"]
    assert "hk_free_cash_flow_quality" in {row["profile"] for row in ranking["deprioritized_profiles"]}
    assert any("not package entrypoints" in note for note in ranking["notes"])


def test_momentum_comparison_has_no_active_momentum_profile_after_pruning():
    comparison = build_momentum_live_enablement_comparison()

    assert comparison["recommended_first_momentum_candidate"] is None
    assert comparison["must_compare_before_live_enablement"] is False
    assert comparison["profiles"] == []


def test_list_snapshot_promotion_candidates_only_returns_retained_contract():
    assert [candidate.profile for candidate in list_snapshot_promotion_candidates()] == ["hk_low_vol_dividend_quality_snapshot"]


def test_snapshot_promotion_matrix_cli_json():
    completed = subprocess.run([sys.executable, str(SCRIPT), "--json"], check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)

    assert payload["profile_count"] == 1
    assert payload["first_snapshot_candidates"] == ["hk_low_vol_dividend_quality_snapshot"]


def test_snapshot_promotion_row_cli_json():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--profile", "hk_low_vol_dividend_quality_snapshot", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["profile"] == "hk_low_vol_dividend_quality_snapshot"
    assert payload["priority"] == 1
