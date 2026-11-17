"""Declarative JSON policy catalog loader and builders for HK snapshot pipelines."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Any


@dataclass(frozen=True, slots=True)
class StrategyFamilyPolicySpec:
    """Declarative specification for a snapshot strategy family's live-enablement policy."""

    key: str
    family_label: str
    section_key: str
    policy_version: str
    profiles: tuple[str, ...]
    required_ablation_tests: tuple[str, ...]
    required_stress_tests: tuple[str, ...]
    required_data_provenance: tuple[str, ...]
    source_reference_urls: tuple[str, ...]
    description: str


@lru_cache(maxsize=8)
def _load_policy_json(filename: str) -> dict[str, Any]:
    raw_text = files(__package__).joinpath("policies", filename).read_text(encoding="utf-8")
    data = json.loads(raw_text)
    if not isinstance(data, dict):
        raise ValueError(f"Policy catalog file {filename!r} must contain a JSON object")
    return data


def get_core_policy_spec(policy_name: str) -> Mapping[str, Any]:
    core = _load_policy_json("core_policies.json")
    try:
        spec = core[policy_name]
    except KeyError as exc:
        raise KeyError(f"Unknown core policy {policy_name!r}") from exc
    if not isinstance(spec, Mapping):
        raise ValueError(f"Core policy {policy_name!r} must be a mapping")
    return spec


def build_artifact_provenance_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("artifact_provenance")
    return {
        "required": bool(spec["required"]),
        "required_fields": list(spec["required_fields"]),
        "required_boolean_fields": list(spec["required_boolean_fields"]),
        "required_uri_fields": list(spec["required_uri_fields"]),
        "sha256_hex_length": int(spec["sha256_hex_length"]),
        "min_production_snapshot_row_count": int(spec["min_production_artifact_row_count"]),
        "source_reference_urls": list(spec["source_reference_urls"]),
        "description": str(spec["description"]),
    }


def build_backtest_validation_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("backtest_validation")
    return {
        "required": bool(spec["required"]),
        "policy_version": str(spec["policy_version"]),
        "scope": str(spec["scope"]),
        "live_enablement_allowed_without_policy_evidence": bool(
            spec["live_enablement_allowed_without_policy_evidence"]
        ),
        "max_allowed_drawdown": float(spec["max_allowed_drawdown"]),
        "min_return_to_drawdown_ratio": float(spec["min_return_to_drawdown_ratio"]),
        "min_required_oos_fold_count": int(spec["min_required_oos_fold_count"]),
        "max_single_period_return_contribution": float(spec["max_single_period_return_contribution"]),
        "required_controls": list(spec["required_controls"]),
        "required_risk_constraints": list(spec["required_risk_constraints"]),
        "required_metrics": list(spec["required_metrics"]),
        "reject_criteria": list(spec["reject_criteria"]),
        "description": str(spec["description"]),
    }


def build_dry_run_order_preview_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("dry_run_order_preview")
    return {
        "required": bool(spec["required"]),
        "policy_version": str(spec["policy_version"]),
        "required_fields": list(spec["required_fields"]),
        "required_uri_fields": list(spec["required_uri_fields"]),
        "required_sha256_fields": list(spec["required_sha256_fields"]),
        "required_boolean_fields": list(spec["required_boolean_fields"]),
        "source_reference_urls": list(spec["source_reference_urls"]),
        "description": str(spec["description"]),
    }


def build_evidence_freshness_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("evidence_freshness")
    return {
        "required": bool(spec["required"]),
        "required_field": str(spec["required_field"]),
        "max_allowed_age_days_by_section": dict(spec["max_allowed_age_days_by_section"]),
    }


def build_evidence_uri_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("evidence_uri")
    return {
        "required": bool(spec["required"]),
        "allowed_schemes": [f"{scheme}://" for scheme in spec["allowed_schemes"]],
        "rejected_query_markers": list(spec["rejected_query_markers"]),
        "description": str(spec["description"]),
    }


def build_notification_audit_policy(expected_event_type: str | None = None) -> dict[str, Any]:
    spec = get_core_policy_spec("notification_audit")
    return {
        "required": bool(spec["required"]),
        "schema_version": str(spec["schema_version"]),
        "expected_event_type": expected_event_type or str(spec["default_event_type"]),
        "supported_event_types": list(spec["supported_event_types"]),
        "required_fields": list(spec["required_fields"]),
        "required_boolean_fields": list(spec["required_boolean_fields"]),
        "required_uri_fields": list(spec["required_uri_fields"]),
        "source_reference_urls": list(spec["source_reference_urls"]),
        "description": str(spec["description"]),
    }


def build_rollout_risk_policy() -> dict[str, Any]:
    spec = get_core_policy_spec("rollout_risk")
    return {
        "required": bool(spec["required"]),
        "max_initial_capital_fraction": float(spec["max_initial_capital_fraction"]),
        "max_per_symbol_capital_fraction": float(spec["max_per_symbol_capital_fraction"]),
        "max_intraday_drawdown_tripwire": float(spec["max_intraday_drawdown_tripwire"]),
        "max_cumulative_drawdown_tripwire": float(spec["max_cumulative_drawdown_tripwire"]),
        "min_observation_trading_days_before_scale_up": int(spec["min_observation_trading_days_before_scale_up"]),
        "required_boolean_fields": list(spec["required_boolean_fields"]),
        "source_reference_urls": list(spec["source_reference_urls"]),
        "description": str(spec["description"]),
    }


@lru_cache(maxsize=1)
def _strategy_family_specs_map() -> dict[str, StrategyFamilyPolicySpec]:
    raw = _load_policy_json("strategy_family_policies.json")
    specs: dict[str, StrategyFamilyPolicySpec] = {}
    for key, item in raw.items():
        specs[key] = StrategyFamilyPolicySpec(
            key=key,
            family_label=str(item["family_label"]),
            section_key=str(item["section_key"]),
            policy_version=str(item["policy_version"]),
            profiles=tuple(item["profiles"]),
            required_ablation_tests=tuple(item["required_ablation_tests"]),
            required_stress_tests=tuple(item["required_stress_tests"]),
            required_data_provenance=tuple(item["required_data_provenance"]),
            source_reference_urls=tuple(item["source_reference_urls"]),
            description=str(item["description"]),
        )
    return specs


def list_strategy_family_specs() -> tuple[StrategyFamilyPolicySpec, ...]:
    return tuple(_strategy_family_specs_map().values())


def get_strategy_family_spec(family_key: str) -> StrategyFamilyPolicySpec:
    specs = _strategy_family_specs_map()
    try:
        return specs[family_key]
    except KeyError as exc:
        raise KeyError(f"Unknown strategy family policy {family_key!r}") from exc


def find_strategy_family_for_profile(profile: str) -> StrategyFamilyPolicySpec | None:
    normalized = str(profile or "").strip()
    for spec in _strategy_family_specs_map().values():
        if normalized in spec.profiles:
            return spec
    return None


def build_strategy_family_policy(family_key: str) -> dict[str, Any]:
    spec = get_strategy_family_spec(family_key)
    return {
        "required": True,
        "policy_version": spec.policy_version,
        "source_reference_urls": list(spec.source_reference_urls),
        "required_ablation_tests": list(spec.required_ablation_tests),
        "required_stress_tests": list(spec.required_stress_tests),
        "required_data_provenance": list(spec.required_data_provenance),
        "required_profile_order": list(spec.profiles),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": spec.description,
    }


def build_all_strategy_family_policies() -> dict[str, dict[str, Any]]:
    return {
        spec.section_key: build_strategy_family_policy(spec.key)
        for spec in list_strategy_family_specs()
    }


def get_live_enablement_data() -> Mapping[str, Any]:
    return _load_policy_json("live_enablement_policy.json")


def get_profile_policy_map(field: str, *, as_tuple: bool = False) -> dict[str, Any]:
    by_profile = get_live_enablement_data()["by_profile"]
    result: dict[str, Any] = {}
    for profile, entry in by_profile.items():
        if field in entry:
            value = entry[field]
            result[profile] = tuple(value) if as_tuple else value
    return result


def _lookup_profile_value(profile: str, field: str, default: Any) -> Any:
    normalized = str(profile or "").strip()
    entry = get_live_enablement_data()["by_profile"].get(normalized)
    if entry is not None and field in entry:
        return entry[field]
    return default


def get_max_allowed_annualized_turnover(profile: str) -> float:
    default = float(get_live_enablement_data()["defaults"]["max_allowed_annualized_turnover"])
    return float(_lookup_profile_value(profile, "max_allowed_annualized_turnover", default))


def get_min_required_rebalance_windows(profile: str) -> int:
    default = int(get_live_enablement_data()["defaults"]["min_required_rebalance_windows"])
    return int(_lookup_profile_value(profile, "min_required_rebalance_windows", default))


def get_min_median_daily_turnover_hkd(profile: str) -> int:
    default = int(get_live_enablement_data()["defaults"]["min_median_daily_turnover_hkd"])
    return int(_lookup_profile_value(profile, "min_median_daily_turnover_hkd", default))


def get_required_benchmark_symbol(profile: str) -> str:
    default = str(get_live_enablement_data()["defaults"]["required_benchmark_symbol"])
    return str(_lookup_profile_value(profile, "required_benchmark_symbol", default))


def get_required_production_source_audit_fields(profile: str) -> tuple[str, ...]:
    data = get_live_enablement_data()
    common = tuple(data["common_production_source_audit_fields"])
    extra = tuple(_lookup_profile_value(profile, "required_production_source_audit_fields", ()))
    return (*common, *extra)


def get_production_source_reference_urls(profile: str) -> tuple[str, ...]:
    data = get_live_enablement_data()
    common = tuple(data["common_production_source_reference_urls"])
    extra = tuple(_lookup_profile_value(profile, "production_source_reference_urls", ()))
    return tuple(dict.fromkeys((*common, *extra)))


def build_production_source_audit_policy(profile: str) -> dict[str, object]:
    data = get_live_enablement_data()
    return {
        "required": True,
        "required_fields": list(data["production_source_audit_required_fields"]),
        "required_uri_fields": list(data["production_source_audit_uri_fields"]),
        "required_boolean_fields": list(get_required_production_source_audit_fields(profile)),
        "source_reference_urls": list(get_production_source_reference_urls(profile)),
        "description": str(data["descriptions"]["production_source_audit_policy"]),
    }


def build_execution_capacity_policy(profile: str) -> dict[str, object]:
    data = get_live_enablement_data()
    defaults = data["defaults"]
    return {
        "required": True,
        "min_adv_window_trading_days": int(defaults["min_adv_window_trading_days"]),
        "min_median_daily_turnover_hkd": get_min_median_daily_turnover_hkd(profile),
        "max_single_order_adv_fraction": float(defaults["max_single_order_adv_fraction"]),
        "max_rebalance_adv_fraction": float(defaults["max_rebalance_adv_fraction"]),
        "required_boolean_fields": list(data["required_execution_capacity_fields"]),
        "source_reference_urls": list(data["execution_capacity_reference_urls"]),
        "description": str(data["descriptions"]["execution_capacity_policy"]),
    }


def build_live_enablement_thresholds(profile: str) -> dict[str, float | int]:
    defaults = get_live_enablement_data()["defaults"]
    return {
        "max_allowed_backtest_drawdown": float(defaults["max_allowed_backtest_drawdown"]),
        "min_return_to_drawdown_ratio": float(defaults["min_return_to_drawdown_ratio"]),
        "min_required_oos_fold_count": int(defaults["min_required_oos_fold_count"]),
        "max_single_period_return_contribution": float(defaults["max_single_period_return_contribution"]),
        "max_allowed_annualized_turnover": get_max_allowed_annualized_turnover(profile),
        "min_required_walk_forward_years": float(defaults["min_required_walk_forward_years"]),
        "min_required_rebalance_windows": get_min_required_rebalance_windows(profile),
    }


def build_shared_evidence_policies(
    profile: str,
    *,
    expected_notification_event_type: str | None = None,
) -> dict[str, Any]:
    return {
        "production_source_audit_policy": build_production_source_audit_policy(profile),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "evidence_uri_policy": build_evidence_uri_policy(),
        "evidence_freshness_policy": build_evidence_freshness_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(profile),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(expected_notification_event_type),
    }


@lru_cache(maxsize=1)
def get_future_research_exports() -> dict[str, Any]:
    data = _load_policy_json("future_research_policy.json")
    profile_hints: dict[str, str] = {str(k): str(v) for k, v in data["profile_hints"].items()}
    named_urls: dict[str, str] = {str(k): str(v) for k, v in data["named_source_urls"].items()}

    candidate_order = tuple(profile_hints.values())
    curated_candidate_order = tuple(profile_hints.get(ref, ref) for ref in data["curated_candidate_order"])
    deprioritized_candidate_order = tuple(
        profile for profile in candidate_order if profile not in curated_candidate_order
    )
    source_urls = tuple(named_urls.get(ref, ref) for ref in data["source_url_refs"])

    exports: dict[str, Any] = {
        "FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION": str(data["policy_version"]),
        "FUTURE_RESEARCH_CANDIDATE_ORDER": candidate_order,
        "FUTURE_RESEARCH_CURATED_CANDIDATE_ORDER": curated_candidate_order,
        "FUTURE_RESEARCH_DEPRIORITIZED_CANDIDATE_ORDER": deprioritized_candidate_order,
        "FUTURE_RESEARCH_REQUIRED_PRE_SCAFFOLD_GATES": tuple(data["required_pre_scaffold_gates"]),
        "FUTURE_RESEARCH_REQUIRED_REJECT_CRITERIA": tuple(data["required_reject_criteria"]),
        "FUTURE_RESEARCH_REQUIRED_DATA_PROVENANCE": tuple(data["required_data_provenance"]),
        "FUTURE_RESEARCH_SOURCE_URLS": source_urls,
        **profile_hints,
        **named_urls,
    }
    return exports


def build_future_research_live_enablement_policy() -> dict[str, Any]:
    data = _load_policy_json("future_research_policy.json")
    exports = get_future_research_exports()
    return {
        "required": bool(data["required"]),
        "policy_version": exports["FUTURE_RESEARCH_LIVE_ENABLEMENT_POLICY_VERSION"],
        "status": str(data["status"]),
        "live_enablement_allowed": bool(data["live_enablement_allowed"]),
        "source_reference_urls": list(exports["FUTURE_RESEARCH_SOURCE_URLS"]),
        "candidate_order": list(exports["FUTURE_RESEARCH_CANDIDATE_ORDER"]),
        "curated_candidate_order": list(exports["FUTURE_RESEARCH_CURATED_CANDIDATE_ORDER"]),
        "deprioritized_candidate_order": list(exports["FUTURE_RESEARCH_DEPRIORITIZED_CANDIDATE_ORDER"]),
        "required_pre_scaffold_gates": list(exports["FUTURE_RESEARCH_REQUIRED_PRE_SCAFFOLD_GATES"]),
        "required_reject_criteria": list(exports["FUTURE_RESEARCH_REQUIRED_REJECT_CRITERIA"]),
        "required_data_provenance": list(exports["FUTURE_RESEARCH_REQUIRED_DATA_PROVENANCE"]),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "description": str(data["description"]),
    }


__all__ = [
    "StrategyFamilyPolicySpec",
    "build_all_strategy_family_policies",
    "build_artifact_provenance_policy",
    "build_backtest_validation_policy",
    "build_dry_run_order_preview_policy",
    "build_evidence_freshness_policy",
    "build_evidence_uri_policy",
    "build_execution_capacity_policy",
    "build_future_research_live_enablement_policy",
    "build_live_enablement_thresholds",
    "build_notification_audit_policy",
    "build_production_source_audit_policy",
    "build_rollout_risk_policy",
    "build_shared_evidence_policies",
    "build_strategy_family_policy",
    "find_strategy_family_for_profile",
    "get_core_policy_spec",
    "get_future_research_exports",
    "get_live_enablement_data",
    "get_max_allowed_annualized_turnover",
    "get_min_median_daily_turnover_hkd",
    "get_min_required_rebalance_windows",
    "get_production_source_reference_urls",
    "get_profile_policy_map",
    "get_required_benchmark_symbol",
    "get_required_production_source_audit_fields",
    "get_strategy_family_spec",
    "list_strategy_family_specs",
]
