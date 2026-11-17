from __future__ import annotations

import pytest

from hk_equity_snapshot_pipelines import (
    artifact_provenance_policy,
    backtest_validation_policy,
    baseline_rotation_live_enablement_policy,
    dry_run_order_preview_policy,
    evidence_freshness_policy,
    evidence_uri_policy,
    factor_mix_live_enablement_policy,
    future_research_live_enablement_policy,
    live_enablement_policy,
    momentum_live_enablement_policy,
    notification_audit_policy,
    policy_catalog,
    policy_value_live_enablement_policy,
    quality_growth_live_enablement_policy,
    quality_yield_live_enablement_policy,
    rollout_risk_policy,
    special_situation_live_enablement_policy,
)


def test_policy_catalog_matches_thin_module_builders():
    assert artifact_provenance_policy.build_artifact_provenance_policy() == policy_catalog.build_artifact_provenance_policy()
    assert backtest_validation_policy.build_backtest_validation_policy() == policy_catalog.build_backtest_validation_policy()
    assert dry_run_order_preview_policy.build_dry_run_order_preview_policy() == policy_catalog.build_dry_run_order_preview_policy()
    assert evidence_freshness_policy.build_evidence_freshness_policy() == policy_catalog.build_evidence_freshness_policy()
    assert evidence_uri_policy.build_evidence_uri_policy() == policy_catalog.build_evidence_uri_policy()
    assert notification_audit_policy.build_notification_audit_policy() == policy_catalog.build_notification_audit_policy()
    assert rollout_risk_policy.build_rollout_risk_policy() == policy_catalog.build_rollout_risk_policy()
    assert future_research_live_enablement_policy.build_future_research_live_enablement_policy() == (
        policy_catalog.build_future_research_live_enablement_policy()
    )
    assert baseline_rotation_live_enablement_policy.build_baseline_rotation_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("baseline_rotation")
    )
    assert factor_mix_live_enablement_policy.build_factor_mix_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("factor_mix")
    )
    assert momentum_live_enablement_policy.build_momentum_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("momentum")
    )
    assert policy_value_live_enablement_policy.build_policy_value_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("policy_value")
    )
    assert quality_growth_live_enablement_policy.build_quality_growth_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("quality_growth")
    )
    assert quality_yield_live_enablement_policy.build_quality_yield_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("quality_yield")
    )
    assert special_situation_live_enablement_policy.build_special_situation_live_enablement_policy() == (
        policy_catalog.build_strategy_family_policy("special_situation")
    )
    assert live_enablement_policy.get_required_benchmark_symbol("hk_low_vol_dividend_quality_snapshot") == "02800"


def test_policy_catalog_returns_isolated_copies():
    first = policy_catalog.build_evidence_freshness_policy()
    first["max_allowed_age_days_by_section"]["walk_forward_backtest"] = 1
    second = policy_catalog.build_evidence_freshness_policy()
    assert second["max_allowed_age_days_by_section"]["walk_forward_backtest"] == 90


def test_policy_catalog_family_lookup_and_error_handling():
    spec = policy_catalog.find_strategy_family_for_profile("hk_low_vol_dividend_quality_snapshot")
    assert spec is not None
    assert spec.section_key == "quality_yield_live_enablement_policy"
    assert policy_catalog.find_strategy_family_for_profile("unknown_profile") is None

    with pytest.raises(KeyError):
        policy_catalog.get_core_policy_spec("missing_policy")
    with pytest.raises(KeyError):
        policy_catalog.get_strategy_family_spec("missing_family")
