from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .artifact_provenance_policy import (
    ARTIFACT_PROVENANCE_URI_FIELDS,
    REQUIRED_ARTIFACT_PROVENANCE_BOOLEAN_FIELDS,
    REQUIRED_ARTIFACT_PROVENANCE_FIELDS,
    build_artifact_provenance_policy,
)
from .baseline_rotation_live_enablement_policy import (
    BASELINE_ROTATION_PROFILES,
    build_baseline_rotation_live_enablement_policy,
)
from .evidence_freshness_policy import (
    EVIDENCE_GENERATED_AT_FIELD,
    MAX_ALLOWED_EVIDENCE_AGE_DAYS_BY_SECTION,
    build_evidence_freshness_policy,
)
from .dry_run_order_preview_policy import (
    REQUIRED_DRY_RUN_ORDER_PREVIEW_BOOLEAN_FIELDS,
    REQUIRED_DRY_RUN_ORDER_PREVIEW_FIELDS,
    REQUIRED_DRY_RUN_ORDER_PREVIEW_SHA256_FIELDS,
    REQUIRED_DRY_RUN_ORDER_PREVIEW_URI_FIELDS,
    build_dry_run_order_preview_policy,
)
from .evidence_uri_policy import (
    ALLOWED_EVIDENCE_URI_SCHEMES,
    SENSITIVE_EVIDENCE_URI_MARKERS,
    build_evidence_uri_policy,
)
from .factor_mix_live_enablement_policy import (
    FACTOR_MIX_STOCK_SELECTION_PROFILES,
    build_factor_mix_live_enablement_policy,
)
from .contracts import get_profile_contract
from .live_enablement_policy import (
    MAX_ALLOWED_BACKTEST_DRAWDOWN,
    MIN_REQUIRED_WALK_FORWARD_YEARS,
    REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS,
    REQUIRED_BACKTEST_COST_MODEL_FIELDS,
    REQUIRED_EXECUTION_CAPACITY_FIELDS,
    PRODUCTION_SOURCE_AUDIT_REQUIRED_FIELDS,
    PRODUCTION_SOURCE_AUDIT_URI_FIELDS,
    build_execution_capacity_policy,
    build_live_enablement_thresholds,
    build_production_source_audit_policy,
    get_max_allowed_annualized_turnover,
    get_min_median_daily_turnover_hkd,
    get_min_required_rebalance_windows,
    get_required_benchmark_symbol,
    get_required_production_source_audit_fields,
)
from .momentum_live_enablement_policy import (
    MOMENTUM_STOCK_SELECTION_PROFILES,
    build_momentum_live_enablement_policy,
)
from .notification_audit_policy import (
    NOTIFICATION_SCHEMA_VERSION,
    REQUIRED_NOTIFICATION_AUDIT_BOOLEAN_FIELDS,
    REQUIRED_NOTIFICATION_AUDIT_FIELDS,
    SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE,
    build_notification_audit_policy,
)
from .policy_value_live_enablement_policy import (
    POLICY_VALUE_STOCK_SELECTION_PROFILES,
    build_policy_value_live_enablement_policy,
)
from .quality_yield_live_enablement_policy import (
    QUALITY_YIELD_STOCK_SELECTION_PROFILES,
    build_quality_yield_live_enablement_policy,
)
from .quality_growth_live_enablement_policy import (
    QUALITY_GROWTH_STOCK_SELECTION_PROFILES,
    build_quality_growth_live_enablement_policy,
)
from .rollout_risk_policy import REQUIRED_ROLLOUT_RISK_FIELDS, build_rollout_risk_policy
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS
from .special_situation_live_enablement_policy import (
    SPECIAL_SITUATION_STOCK_SELECTION_PROFILES,
    build_special_situation_live_enablement_policy,
)

EVIDENCE_TYPE = "hk_snapshot_live_enablement"
REQUIRED_SECTIONS: tuple[str, ...] = (
    "production_snapshot_source_audit",
    "artifact_pack_validation",
    "walk_forward_backtest",
    "platform_dry_run_order_preview",
    "broker_permission_and_fee_verification",
    "paper_or_dry_run_rebalance_window",
    "runtime_rollout_plan",
    "risk_approval",
)
STRATEGY_POLICY_EVIDENCE_SECTION = "strategy_policy_evidence"
STRATEGY_POLICY_EVIDENCE_MAX_AGE_DAYS = 90


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _is_passed(section: Mapping[str, Any]) -> bool:
    return str(section.get("status", "")).strip().lower() == "passed"


def _bool_is_true(section: Mapping[str, Any], field: str) -> bool:
    return section.get(field) is True


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _drawdown_abs(value: Any) -> float | None:
    number = _number(value)
    if number is None:
        return None
    return abs(number)


def _parse_iso_date(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).strip()[:10])
    except (TypeError, ValueError):
        return None


def _resolve_validation_as_of(evidence: Mapping[str, Any], validation_as_of: str | None) -> tuple[datetime, list[str]]:
    raw_value = validation_as_of if validation_as_of is not None else evidence.get("validation_as_of")
    if raw_value is None or not str(raw_value).strip():
        return datetime.now(), []
    parsed_value = _parse_iso_date(raw_value)
    if parsed_value is None:
        return datetime.now(), ["validation_as_of must be an ISO date"]
    return parsed_value, []


def _require_evidence_freshness(
    errors: list[str],
    section_name: str,
    section: Mapping[str, Any],
    *,
    validation_as_of: datetime,
) -> None:
    max_allowed_age_days = MAX_ALLOWED_EVIDENCE_AGE_DAYS_BY_SECTION[section_name]
    raw_generated_at = section.get(EVIDENCE_GENERATED_AT_FIELD)
    if raw_generated_at is None or not str(raw_generated_at).strip():
        errors.append(f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} is required")
        return
    generated_at = _parse_iso_date(raw_generated_at)
    if generated_at is None:
        errors.append(f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} must be an ISO date")
        return
    generated_date = generated_at.date()
    validation_date = validation_as_of.date()
    if generated_date > validation_date:
        errors.append(
            f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} must not be after validation_as_of: "
            f"got {generated_date.isoformat()}, validation_as_of={validation_date.isoformat()}"
        )
        return
    age_days = (validation_date - generated_date).days
    if age_days > max_allowed_age_days:
        errors.append(
            f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} is stale: "
            f"age_days={age_days}, max_allowed_age_days={max_allowed_age_days}"
        )


def _require_evidence_freshness_max_age(
    errors: list[str],
    section_name: str,
    section: Mapping[str, Any],
    *,
    validation_as_of: datetime,
    max_allowed_age_days: int,
) -> None:
    raw_generated_at = section.get(EVIDENCE_GENERATED_AT_FIELD)
    if raw_generated_at is None or not str(raw_generated_at).strip():
        errors.append(f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} is required")
        return
    generated_at = _parse_iso_date(raw_generated_at)
    if generated_at is None:
        errors.append(f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} must be an ISO date")
        return
    generated_date = generated_at.date()
    validation_date = validation_as_of.date()
    if generated_date > validation_date:
        errors.append(
            f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} must not be after validation_as_of: "
            f"got {generated_date.isoformat()}, validation_as_of={validation_date.isoformat()}"
        )
        return
    age_days = (validation_date - generated_date).days
    if age_days > max_allowed_age_days:
        errors.append(
            f"{section_name}.{EVIDENCE_GENERATED_AT_FIELD} is stale: "
            f"age_days={age_days}, max_allowed_age_days={max_allowed_age_days}"
        )


def _add_missing_bool_errors(errors: list[str], section_name: str, section: Mapping[str, Any], fields: tuple[str, ...]) -> None:
    for field in fields:
        if not _bool_is_true(section, field):
            errors.append(f"{section_name}.{field} must be true")


def _require_evidence_uri(errors: list[str], section_name: str, section: Mapping[str, Any]) -> None:
    raw_uri = str(section.get("evidence_uri", "")).strip()
    if not raw_uri:
        errors.append(f"{section_name}.evidence_uri is required")
        return
    parsed_uri = urlparse(raw_uri)
    if parsed_uri.scheme.lower() not in ALLOWED_EVIDENCE_URI_SCHEMES or not parsed_uri.netloc or not parsed_uri.path:
        allowed = ", ".join(f"{scheme}://" for scheme in ALLOWED_EVIDENCE_URI_SCHEMES)
        errors.append(f"{section_name}.evidence_uri must be a stable URI using one of: {allowed}")
    lowered_uri = raw_uri.lower()
    if any(marker in lowered_uri for marker in SENSITIVE_EVIDENCE_URI_MARKERS):
        errors.append(f"{section_name}.evidence_uri must not contain secret-like query parameters")


def _require_stable_uri_field(errors: list[str], section_name: str, section: Mapping[str, Any], field: str) -> None:
    raw_uri = str(section.get(field, "")).strip()
    if not raw_uri:
        errors.append(f"{section_name}.{field} is required")
        return
    parsed_uri = urlparse(raw_uri)
    if parsed_uri.scheme.lower() not in ALLOWED_EVIDENCE_URI_SCHEMES or not parsed_uri.netloc or not parsed_uri.path:
        allowed = ", ".join(f"{scheme}://" for scheme in ALLOWED_EVIDENCE_URI_SCHEMES)
        errors.append(f"{section_name}.{field} must be a stable URI using one of: {allowed}")
    lowered_uri = raw_uri.lower()
    if any(marker in lowered_uri for marker in SENSITIVE_EVIDENCE_URI_MARKERS):
        errors.append(f"{section_name}.{field} must not contain secret-like query parameters")


def _sha256_is_hex(value: Any) -> bool:
    text = str(value or "").strip()
    if len(text) != 64:
        return False
    return all(char in "0123456789abcdefABCDEF" for char in text)


def _validate_notification_audit(
    errors: list[str],
    section_name: str,
    section: Mapping[str, Any],
    *,
    expected_event_type: str,
) -> None:
    for field in REQUIRED_NOTIFICATION_AUDIT_FIELDS:
        if not str(section.get(field, "")).strip():
            errors.append(f"{section_name}.{field} is required")
    if section.get("notification_schema_version") != NOTIFICATION_SCHEMA_VERSION:
        errors.append(
            f"{section_name}.notification_schema_version must be {NOTIFICATION_SCHEMA_VERSION!r}: "
            f"got {section.get('notification_schema_version')!r}"
        )
    if section.get("notification_event_type") != expected_event_type:
        errors.append(
            f"{section_name}.notification_event_type must be {expected_event_type!r}: "
            f"got {section.get('notification_event_type')!r}"
        )
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_NOTIFICATION_AUDIT_BOOLEAN_FIELDS)
    _require_stable_uri_field(errors, section_name, section, "notification_delivery_log_uri")


def _validate_dry_run_order_preview_provenance(
    errors: list[str],
    section_name: str,
    section: Mapping[str, Any],
) -> None:
    for field in REQUIRED_DRY_RUN_ORDER_PREVIEW_FIELDS:
        if not str(section.get(field, "")).strip():
            errors.append(f"{section_name}.{field} is required")
    for field in REQUIRED_DRY_RUN_ORDER_PREVIEW_URI_FIELDS:
        _require_stable_uri_field(errors, section_name, section, field)
    for field in REQUIRED_DRY_RUN_ORDER_PREVIEW_SHA256_FIELDS:
        if not _sha256_is_hex(section.get(field)):
            errors.append(f"{section_name}.{field} must be a 64-character hex sha256")
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_DRY_RUN_ORDER_PREVIEW_BOOLEAN_FIELDS)


def _validate_production_snapshot_source(errors: list[str], evidence: Mapping[str, Any], *, profile: str) -> None:
    section_name = "production_snapshot_source_audit"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    for field in PRODUCTION_SOURCE_AUDIT_REQUIRED_FIELDS:
        if not str(section.get(field, "")).strip():
            errors.append(f"{section_name}.{field} is required")
    source_coverage_start = _parse_iso_date(section.get("source_coverage_start"))
    source_coverage_end = _parse_iso_date(section.get("source_coverage_end"))
    if section.get("source_coverage_start") and source_coverage_start is None:
        errors.append(f"{section_name}.source_coverage_start must be an ISO date")
    if section.get("source_coverage_end") and source_coverage_end is None:
        errors.append(f"{section_name}.source_coverage_end must be an ISO date")
    if source_coverage_start is not None and source_coverage_end is not None and source_coverage_end < source_coverage_start:
        errors.append(f"{section_name}.source_coverage_end must not be before source_coverage_start")
    for field in PRODUCTION_SOURCE_AUDIT_URI_FIELDS:
        _require_stable_uri_field(errors, section_name, section, field)
    _add_missing_bool_errors(errors, section_name, section, get_required_production_source_audit_fields(profile))


def _validate_artifact_pack(errors: list[str], evidence: Mapping[str, Any], *, profile: str) -> None:
    section_name = "artifact_pack_validation"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if section.get("valid") is not True:
        errors.append(f"{section_name}.valid must be true")
    if str(section.get("validation_status", "")).strip().lower() != "passed":
        errors.append(f"{section_name}.validation_status must be 'passed'")
    if section.get("profile") != profile:
        errors.append(f"{section_name}.profile mismatch: expected {profile!r}, got {section.get('profile')!r}")
    try:
        contract = get_profile_contract(profile)
    except Exception as exc:
        errors.append(str(exc))
        return
    for field in REQUIRED_ARTIFACT_PROVENANCE_FIELDS:
        if not str(section.get(field, "")).strip():
            errors.append(f"{section_name}.{field} is required")
    if section.get("contract_version") != contract.contract_version:
        errors.append(
            f"{section_name}.contract_version mismatch: expected {contract.contract_version!r}, "
            f"got {section.get('contract_version')!r}"
        )
    if not _sha256_is_hex(section.get("snapshot_sha256")):
        errors.append(f"{section_name}.snapshot_sha256 must be a 64-character hex sha256")
    row_count = _number(section.get("row_count"))
    if row_count is None or row_count <= 0:
        errors.append(f"{section_name}.row_count must be positive")
    artifact_release_id = str(section.get("artifact_release_id", "")).strip().lower()
    if artifact_release_id in {"latest", "sample", "dev", "test"}:
        errors.append(f"{section_name}.artifact_release_id must be immutable and not a mutable alias")
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_ARTIFACT_PROVENANCE_BOOLEAN_FIELDS)
    for field in ARTIFACT_PROVENANCE_URI_FIELDS:
        _require_stable_uri_field(errors, section_name, section, field)


def _validate_backtest(errors: list[str], evidence: Mapping[str, Any], *, profile: str) -> None:
    section_name = "walk_forward_backtest"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    if section.get("out_of_sample") is not True:
        errors.append(f"{section_name}.out_of_sample must be true")
    for field in ("period_start", "period_end"):
        if not str(section.get(field, "")).strip():
            errors.append(f"{section_name}.{field} is required")
    period_start = _parse_iso_date(section.get("period_start"))
    period_end = _parse_iso_date(section.get("period_end"))
    if period_start is not None and period_end is not None:
        walk_forward_years = (period_end - period_start).days / 365.25
        if walk_forward_years < MIN_REQUIRED_WALK_FORWARD_YEARS:
            errors.append(
                f"{section_name}.period must cover at least {MIN_REQUIRED_WALK_FORWARD_YEARS:.1f} years: "
                f"got {walk_forward_years:.2f}"
            )
    annual_return = _number(section.get("annual_return"))
    if annual_return is None:
        errors.append(f"{section_name}.annual_return is required")
    elif annual_return <= 0:
        errors.append(f"{section_name}.annual_return must be positive")
    max_drawdown = _drawdown_abs(section.get("max_drawdown"))
    if max_drawdown is None:
        errors.append(f"{section_name}.max_drawdown is required")
    elif max_drawdown > MAX_ALLOWED_BACKTEST_DRAWDOWN:
        errors.append(
            f"{section_name}.max_drawdown exceeds {MAX_ALLOWED_BACKTEST_DRAWDOWN:.0%}: "
            f"got {max_drawdown:.2%}"
        )
    rolling_oos_fold_max_drawdown = _drawdown_abs(section.get("rolling_oos_fold_max_drawdown"))
    if rolling_oos_fold_max_drawdown is None:
        errors.append(f"{section_name}.rolling_oos_fold_max_drawdown is required")
    elif rolling_oos_fold_max_drawdown > MAX_ALLOWED_BACKTEST_DRAWDOWN:
        errors.append(
            f"{section_name}.rolling_oos_fold_max_drawdown exceeds {MAX_ALLOWED_BACKTEST_DRAWDOWN:.0%}: "
            f"got {rolling_oos_fold_max_drawdown:.2%}"
        )
    max_turnover = get_max_allowed_annualized_turnover(profile)
    annualized_turnover = _number(section.get("annualized_turnover"))
    if annualized_turnover is None:
        errors.append(f"{section_name}.annualized_turnover is required")
    elif annualized_turnover > max_turnover:
        errors.append(
            f"{section_name}.annualized_turnover exceeds {max_turnover:.0%}: "
            f"got {annualized_turnover:.2%}"
        )
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_BACKTEST_COST_MODEL_FIELDS)
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS)
    benchmark_symbol = str(section.get("benchmark_symbol", "")).strip()
    required_benchmark_symbol = get_required_benchmark_symbol(profile)
    if not benchmark_symbol:
        errors.append(f"{section_name}.benchmark_symbol is required")
    elif benchmark_symbol != required_benchmark_symbol:
        errors.append(
            f"{section_name}.benchmark_symbol must be {required_benchmark_symbol!r}: got {benchmark_symbol!r}"
        )
    if _number(section.get("benchmark_annual_return")) is None:
        errors.append(f"{section_name}.benchmark_annual_return is required")
    strategy_excess_return = _number(section.get("strategy_excess_return"))
    if strategy_excess_return is None:
        errors.append(f"{section_name}.strategy_excess_return is required")
    elif strategy_excess_return <= 0:
        errors.append(f"{section_name}.strategy_excess_return must be positive")


def _validate_dry_run(errors: list[str], evidence: Mapping[str, Any], *, profile: str) -> None:
    section_name = "platform_dry_run_order_preview"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    orders_previewed = _number(section.get("orders_previewed"))
    if orders_previewed is None or orders_previewed <= 0:
        errors.append(f"{section_name}.orders_previewed must be positive")
    for field in ("fractional_share_errors", "lot_size_errors"):
        value = _number(section.get(field))
        if value is None or value != 0:
            errors.append(f"{section_name}.{field} must be 0")
    if section.get("notification_sent") is not True:
        errors.append(f"{section_name}.notification_sent must be true")
    adv_window_trading_days = _number(section.get("adv_window_trading_days"))
    min_adv_window_trading_days = build_execution_capacity_policy(profile)["min_adv_window_trading_days"]
    if adv_window_trading_days is None or adv_window_trading_days < min_adv_window_trading_days:
        errors.append(f"{section_name}.adv_window_trading_days must be >= {min_adv_window_trading_days}")
    median_daily_turnover_hkd = _number(section.get("median_daily_turnover_hkd"))
    min_median_daily_turnover_hkd = get_min_median_daily_turnover_hkd(profile)
    if median_daily_turnover_hkd is None or median_daily_turnover_hkd < min_median_daily_turnover_hkd:
        errors.append(
            f"{section_name}.median_daily_turnover_hkd must be >= {min_median_daily_turnover_hkd}"
        )
    execution_capacity_policy = build_execution_capacity_policy(profile)
    for field, threshold_key in (
        ("max_single_order_adv_fraction", "max_single_order_adv_fraction"),
        ("rebalance_adv_fraction", "max_rebalance_adv_fraction"),
    ):
        value = _number(section.get(field))
        threshold = float(execution_capacity_policy[threshold_key])
        if value is None:
            errors.append(f"{section_name}.{field} is required")
        elif value > threshold:
            errors.append(f"{section_name}.{field} exceeds {threshold:.2%}: got {value:.2%}")
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_EXECUTION_CAPACITY_FIELDS)
    _validate_dry_run_order_preview_provenance(errors, section_name, section)
    _validate_notification_audit(
        errors,
        section_name,
        section,
        expected_event_type=SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE,
    )


def _validate_broker_permissions(errors: list[str], evidence: Mapping[str, Any]) -> None:
    section_name = "broker_permission_and_fee_verification"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    _add_missing_bool_errors(
        errors,
        section_name,
        section,
        (
            "hk_market_data",
            "sehk_trading_permission",
            "hkd_cash_handling",
            "fees_verified",
            "stamp_duty_or_exemption_verified",
        ),
    )


def _validate_rebalance_window(errors: list[str], evidence: Mapping[str, Any], *, profile: str) -> None:
    section_name = "paper_or_dry_run_rebalance_window"
    section = _as_mapping(evidence.get(section_name))
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    window_count = _number(section.get("window_count"))
    min_window_count = get_min_required_rebalance_windows(profile)
    if window_count is None or window_count < min_window_count:
        errors.append(f"{section_name}.window_count must be >= {min_window_count}")
    if section.get("rebalance_or_event_window_covered") is not True:
        errors.append(f"{section_name}.rebalance_or_event_window_covered must be true")


def _validate_runtime_rollout_plan(errors: list[str], evidence: Mapping[str, Any]) -> None:
    section_name = "runtime_rollout_plan"
    section = _as_mapping(evidence.get(section_name))
    rollout_policy = build_rollout_risk_policy()
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    _add_missing_bool_errors(errors, section_name, section, REQUIRED_ROLLOUT_RISK_FIELDS)
    for field, threshold_key in (
        ("initial_capital_fraction", "max_initial_capital_fraction"),
        ("per_symbol_capital_fraction", "max_per_symbol_capital_fraction"),
        ("intraday_drawdown_tripwire", "max_intraday_drawdown_tripwire"),
        ("cumulative_drawdown_tripwire", "max_cumulative_drawdown_tripwire"),
    ):
        value = _number(section.get(field))
        threshold = float(rollout_policy[threshold_key])
        if value is None:
            errors.append(f"{section_name}.{field} is required")
        elif value > threshold:
            errors.append(f"{section_name}.{field} exceeds {threshold:.2%}: got {value:.2%}")
    observation_days = _number(section.get("observation_trading_days_before_scale_up"))
    min_observation_days = int(rollout_policy["min_observation_trading_days_before_scale_up"])
    if observation_days is None or observation_days < min_observation_days:
        errors.append(f"{section_name}.observation_trading_days_before_scale_up must be >= {min_observation_days}")


def _validate_risk_approval(errors: list[str], evidence: Mapping[str, Any]) -> None:
    section_name = "risk_approval"
    section = _as_mapping(evidence.get(section_name))
    _add_missing_bool_errors(
        errors,
        section_name,
        section,
        ("operator_approved", "strategy_runtime_enablement_approved", "dry_run_removal_approved"),
    )
    if not str(section.get("approval_reference", "")).strip():
        errors.append(f"{section_name}.approval_reference is required")


def _strategy_policy_required_bool_fields(policy: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(field)
        for field in (
            *policy["required_ablation_tests"],
            *policy["required_stress_tests"],
            *policy["required_data_provenance"],
        )
    )


def _validate_strategy_policy_evidence(
    errors: list[str],
    evidence: Mapping[str, Any],
    *,
    validation_as_of: datetime,
    policy: Mapping[str, Any],
    profile_family_label: str,
) -> None:
    section_name = STRATEGY_POLICY_EVIDENCE_SECTION
    section = _as_mapping(evidence.get(section_name))
    if not section:
        errors.append(f"missing required evidence section for {profile_family_label} profile: {section_name}")
        return
    _require_evidence_uri(errors, section_name, section)
    if not _is_passed(section):
        errors.append(f"{section_name}.status must be 'passed'")
    expected_policy_version = policy["policy_version"]
    if section.get("policy_version") != expected_policy_version:
        errors.append(
            f"{section_name}.policy_version must be {expected_policy_version!r}: "
            f"got {section.get('policy_version')!r}"
        )
    _require_evidence_freshness_max_age(
        errors,
        section_name,
        section,
        validation_as_of=validation_as_of,
        max_allowed_age_days=STRATEGY_POLICY_EVIDENCE_MAX_AGE_DAYS,
    )
    _add_missing_bool_errors(errors, section_name, section, _strategy_policy_required_bool_fields(policy))


def _build_strategy_policy_evidence_template(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": "pending",
        "policy_version": policy["policy_version"],
        **{field: False for field in _strategy_policy_required_bool_fields(policy)},
        EVIDENCE_GENERATED_AT_FIELD: "",
        "evidence_uri": "",
    }


def build_live_enablement_evidence_template(profile: str, *, platform: str) -> dict[str, Any]:
    contract = get_profile_contract(profile)
    normalized_platform = str(platform or "").strip().lower()
    if normalized_platform not in SUPPORTED_SNAPSHOT_PLATFORMS:
        raise ValueError(f"platform must be one of {sorted(SUPPORTED_SNAPSHOT_PLATFORMS)}")
    payload = {
        "evidence_type": EVIDENCE_TYPE,
        "template_status": "pending_operator_evidence",
        "profile": contract.profile,
        "platform": normalized_platform,
        "contract_version": contract.contract_version,
        "validation_as_of": "<YYYY-MM-DD>",
        "max_allowed_backtest_drawdown": MAX_ALLOWED_BACKTEST_DRAWDOWN,
        "max_allowed_annualized_turnover": get_max_allowed_annualized_turnover(contract.profile),
        "min_required_rebalance_windows": get_min_required_rebalance_windows(contract.profile),
        "required_benchmark_symbol": get_required_benchmark_symbol(contract.profile),
        "live_enablement_thresholds": build_live_enablement_thresholds(contract.profile),
        "production_source_audit_policy": build_production_source_audit_policy(contract.profile),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "evidence_uri_policy": build_evidence_uri_policy(),
        "evidence_freshness_policy": build_evidence_freshness_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(contract.profile),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "production_snapshot_source_audit": {
            "status": "pending",
            "source_name": "",
            "source_coverage_start": "",
            "source_coverage_end": "",
            "production_source_uri": "",
            "source_quality_report_uri": "",
            "point_in_time_data_dictionary_uri": "",
            **{field: False for field in get_required_production_source_audit_fields(contract.profile)},
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "artifact_pack_validation": {
            "valid": False,
            "validation_status": "pending",
            "profile": contract.profile,
            "artifact_dir": "",
            "validator_command": (
                "hkeq-validate-snapshot-artifact-pack "
                f"--profile {contract.profile} --artifact-dir <published-artifact-dir> --json"
            ),
            "artifact_release_id": "",
            "contract_version": contract.contract_version,
            "snapshot_sha256": "",
            "row_count": None,
            "published_snapshot_uri": "",
            "published_manifest_uri": "",
            "published_ranking_uri": "",
            "published_release_summary_uri": "",
            "immutable_release_id": False,
            "published_artifacts_not_sample": False,
            "manifest_snapshot_sha256_verified": False,
            "manifest_row_count_verified": False,
            "release_summary_ready": False,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "walk_forward_backtest": {
            "status": "pending",
            "out_of_sample": False,
            "period_start": "",
            "period_end": "",
            "annual_return": None,
            "max_drawdown": None,
            "rolling_oos_fold_max_drawdown": None,
            "annualized_turnover": None,
            "hk_fees_and_levies": False,
            "stamp_duty_or_exemption": False,
            "slippage": False,
            "lot_size_rounding": False,
            "suspension_handling": False,
            "survivorship_bias_controls": False,
            "lookahead_bias_controls": False,
            "benchmark_period_aligned": False,
            "rolling_oos_fold_drawdown_controls": False,
            "parameter_sensitivity_and_holdout_stability_controls": False,
            "regime_stress_and_liquidity_shock_controls": False,
            "fee_slippage_spread_stress_sensitivity_controls": False,
            "net_return_after_costs_controls": False,
            "data_vendor_reconciliation_and_missingness_controls": False,
            "corporate_action_delisting_and_stale_price_controls": False,
            "cash_leverage_short_borrow_and_margin_controls": False,
            "tail_loss_time_underwater_and_recovery_controls": False,
            "portfolio_correlation_and_aggregate_risk_budget_controls": False,
            "benchmark_symbol": get_required_benchmark_symbol(contract.profile),
            "benchmark_annual_return": None,
            "strategy_excess_return": None,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "platform_dry_run_order_preview": {
            "status": "pending",
            "orders_previewed": 0,
            "fractional_share_errors": None,
            "lot_size_errors": None,
            "notification_sent": False,
            "notification_schema_version": NOTIFICATION_SCHEMA_VERSION,
            "notification_event_type": SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE,
            "notification_correlation_id": "",
            "notification_locale_en": False,
            "notification_locale_zh_hans": False,
            "notification_contains_profile": False,
            "notification_contains_platform": False,
            "notification_contains_validation_status": False,
            "notification_contains_order_preview_summary": False,
            "notification_redacts_sensitive_fields": False,
            "notification_delivery_log_uri": "",
            "dry_run_session_id": "",
            "raw_order_preview_uri": "",
            "raw_order_preview_sha256": "",
            "quote_snapshot_uri": "",
            "quote_snapshot_sha256": "",
            "fee_breakdown_uri": "",
            "fee_breakdown_sha256": "",
            "order_preview_artifact_not_sample": False,
            "order_preview_redacts_sensitive_fields": False,
            "quote_snapshot_covers_all_symbols": False,
            "fee_breakdown_reconciled_to_broker_preview": False,
            "order_preview_reconciled_to_strategy_decision": False,
            "adv_window_trading_days": 0,
            "median_daily_turnover_hkd": None,
            "max_single_order_adv_fraction": None,
            "rebalance_adv_fraction": None,
            "liquidity_cap_verified": False,
            "board_lot_rounding_verified": False,
            "odd_lot_avoidance_verified": False,
            "market_session_routing_verified": False,
            "vcm_price_band_controls_verified": False,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "broker_permission_and_fee_verification": {
            "status": "pending",
            "hk_market_data": False,
            "sehk_trading_permission": False,
            "hkd_cash_handling": False,
            "fees_verified": False,
            "stamp_duty_or_exemption_verified": False,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "paper_or_dry_run_rebalance_window": {
            "status": "pending",
            "window_count": 0,
            "min_required_window_count": get_min_required_rebalance_windows(contract.profile),
            "rebalance_or_event_window_covered": False,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "runtime_rollout_plan": {
            "status": "pending",
            "staged_rollout_plan_ready": False,
            "initial_capital_fraction": None,
            "per_symbol_capital_fraction": None,
            "intraday_drawdown_tripwire": None,
            "cumulative_drawdown_tripwire": None,
            "observation_trading_days_before_scale_up": 0,
            "kill_switch_ready": False,
            "rollback_plan_ready": False,
            "post_deploy_monitoring_ready": False,
            "operator_notification_ready": False,
            "severe_weather_trading_runbook_ready": False,
            "vcm_cooling_off_handling_ready": False,
            EVIDENCE_GENERATED_AT_FIELD: "",
            "evidence_uri": "",
        },
        "risk_approval": {
            "operator_approved": False,
            "strategy_runtime_enablement_approved": False,
            "dry_run_removal_approved": False,
            "approval_reference": "",
        },
    }
    if contract.profile in BASELINE_ROTATION_PROFILES:
        baseline_rotation_policy = build_baseline_rotation_live_enablement_policy()
        payload["baseline_rotation_live_enablement_policy"] = baseline_rotation_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(
            baseline_rotation_policy
        )
    if contract.profile in QUALITY_YIELD_STOCK_SELECTION_PROFILES:
        quality_yield_policy = build_quality_yield_live_enablement_policy()
        payload["quality_yield_live_enablement_policy"] = quality_yield_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(quality_yield_policy)
    if contract.profile in QUALITY_GROWTH_STOCK_SELECTION_PROFILES:
        quality_growth_policy = build_quality_growth_live_enablement_policy()
        payload["quality_growth_live_enablement_policy"] = quality_growth_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(quality_growth_policy)
    if contract.profile in FACTOR_MIX_STOCK_SELECTION_PROFILES:
        factor_mix_policy = build_factor_mix_live_enablement_policy()
        payload["factor_mix_live_enablement_policy"] = factor_mix_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(factor_mix_policy)
    if contract.profile in MOMENTUM_STOCK_SELECTION_PROFILES:
        momentum_policy = build_momentum_live_enablement_policy()
        payload["momentum_live_enablement_policy"] = momentum_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(momentum_policy)
    if contract.profile in POLICY_VALUE_STOCK_SELECTION_PROFILES:
        policy_value_policy = build_policy_value_live_enablement_policy()
        payload["policy_value_live_enablement_policy"] = policy_value_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(policy_value_policy)
    if contract.profile in SPECIAL_SITUATION_STOCK_SELECTION_PROFILES:
        special_situation_policy = build_special_situation_live_enablement_policy()
        payload["special_situation_live_enablement_policy"] = special_situation_policy
        payload[STRATEGY_POLICY_EVIDENCE_SECTION] = _build_strategy_policy_evidence_template(special_situation_policy)
    return payload


def validate_live_enablement_evidence(evidence: Mapping[str, Any], *, validation_as_of: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    resolved_validation_as_of, validation_as_of_errors = _resolve_validation_as_of(evidence, validation_as_of)
    errors.extend(validation_as_of_errors)
    if evidence.get("evidence_type") != EVIDENCE_TYPE:
        errors.append(f"evidence_type must be {EVIDENCE_TYPE!r}")

    profile_input = str(evidence.get("profile", "")).strip()
    platform = str(evidence.get("platform", "")).strip().lower()
    try:
        contract = get_profile_contract(profile_input)
        profile = contract.profile
    except Exception as exc:
        profile = profile_input
        errors.append(str(exc))
    if platform not in SUPPORTED_SNAPSHOT_PLATFORMS:
        errors.append(f"platform must be one of {sorted(SUPPORTED_SNAPSHOT_PLATFORMS)}")

    missing_sections = [name for name in REQUIRED_SECTIONS if name not in evidence]
    for section in missing_sections:
        errors.append(f"missing required evidence section: {section}")

    if not missing_sections:
        for section_name in MAX_ALLOWED_EVIDENCE_AGE_DAYS_BY_SECTION:
            _require_evidence_freshness(
                errors,
                section_name,
                _as_mapping(evidence.get(section_name)),
                validation_as_of=resolved_validation_as_of,
            )
        _validate_production_snapshot_source(errors, evidence, profile=profile)
        _validate_artifact_pack(errors, evidence, profile=profile)
        _validate_backtest(errors, evidence, profile=profile)
        _validate_dry_run(errors, evidence, profile=profile)
        _validate_broker_permissions(errors, evidence)
        _validate_rebalance_window(errors, evidence, profile=profile)
        _validate_runtime_rollout_plan(errors, evidence)
        _validate_risk_approval(errors, evidence)
        if profile in BASELINE_ROTATION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_baseline_rotation_live_enablement_policy(),
                profile_family_label="baseline-rotation",
            )
        if profile in QUALITY_YIELD_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_quality_yield_live_enablement_policy(),
                profile_family_label="quality/yield",
            )
        if profile in QUALITY_GROWTH_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_quality_growth_live_enablement_policy(),
                profile_family_label="quality-growth",
            )
        if profile in FACTOR_MIX_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_factor_mix_live_enablement_policy(),
                profile_family_label="factor-mix",
            )
        if profile in MOMENTUM_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_momentum_live_enablement_policy(),
                profile_family_label="momentum",
            )
        if profile in POLICY_VALUE_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_policy_value_live_enablement_policy(),
                profile_family_label="policy-value",
            )
        if profile in SPECIAL_SITUATION_STOCK_SELECTION_PROFILES:
            _validate_strategy_policy_evidence(
                errors,
                evidence,
                validation_as_of=resolved_validation_as_of,
                policy=build_special_situation_live_enablement_policy(),
                profile_family_label="special-situation",
            )

    result = {
        "evidence_type": EVIDENCE_TYPE,
        "profile": profile,
        "platform": platform,
        "validation_as_of": resolved_validation_as_of.date().isoformat(),
        "validation_status": "failed",
        "live_enablement_allowed": False,
        "max_allowed_backtest_drawdown": MAX_ALLOWED_BACKTEST_DRAWDOWN,
        "max_allowed_annualized_turnover": get_max_allowed_annualized_turnover(profile),
        "min_required_rebalance_windows": get_min_required_rebalance_windows(profile),
        "required_benchmark_symbol": get_required_benchmark_symbol(profile),
        "required_sections": list(REQUIRED_SECTIONS),
        "production_source_audit_policy": build_production_source_audit_policy(profile),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "evidence_uri_policy": build_evidence_uri_policy(),
        "evidence_freshness_policy": build_evidence_freshness_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(profile),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "errors": errors,
        "warnings": warnings,
        "live_enablement_thresholds": build_live_enablement_thresholds(profile),
    }
    if profile in BASELINE_ROTATION_PROFILES:
        result["baseline_rotation_live_enablement_policy"] = build_baseline_rotation_live_enablement_policy()
    if profile in QUALITY_YIELD_STOCK_SELECTION_PROFILES:
        result["quality_yield_live_enablement_policy"] = build_quality_yield_live_enablement_policy()
    if profile in QUALITY_GROWTH_STOCK_SELECTION_PROFILES:
        result["quality_growth_live_enablement_policy"] = build_quality_growth_live_enablement_policy()
    if profile in FACTOR_MIX_STOCK_SELECTION_PROFILES:
        result["factor_mix_live_enablement_policy"] = build_factor_mix_live_enablement_policy()
    if profile in MOMENTUM_STOCK_SELECTION_PROFILES:
        result["momentum_live_enablement_policy"] = build_momentum_live_enablement_policy()
    if profile in POLICY_VALUE_STOCK_SELECTION_PROFILES:
        result["policy_value_live_enablement_policy"] = build_policy_value_live_enablement_policy()
    if profile in SPECIAL_SITUATION_STOCK_SELECTION_PROFILES:
        result["special_situation_live_enablement_policy"] = build_special_situation_live_enablement_policy()
    if not errors:
        result["validation_status"] = "passed"
        result["live_enablement_allowed"] = True
    return result


def validate_live_enablement_evidence_file(path: str | Path, *, validation_as_of: str | None = None) -> dict[str, Any]:
    evidence = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(evidence, Mapping):
        resolved_validation_as_of, validation_as_of_errors = _resolve_validation_as_of({}, validation_as_of)
        return {
            "evidence_type": EVIDENCE_TYPE,
            "profile": "",
            "platform": "",
            "validation_as_of": resolved_validation_as_of.date().isoformat(),
            "validation_status": "failed",
            "live_enablement_allowed": False,
            "max_allowed_backtest_drawdown": MAX_ALLOWED_BACKTEST_DRAWDOWN,
            "required_sections": list(REQUIRED_SECTIONS),
            "production_source_audit_policy": build_production_source_audit_policy(""),
            "artifact_provenance_policy": build_artifact_provenance_policy(),
            "evidence_uri_policy": build_evidence_uri_policy(),
            "evidence_freshness_policy": build_evidence_freshness_policy(),
            "execution_capacity_policy": build_execution_capacity_policy(""),
            "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
            "rollout_risk_policy": build_rollout_risk_policy(),
            "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
            "baseline_rotation_live_enablement_policy": build_baseline_rotation_live_enablement_policy(),
            "quality_yield_live_enablement_policy": build_quality_yield_live_enablement_policy(),
            "quality_growth_live_enablement_policy": build_quality_growth_live_enablement_policy(),
            "factor_mix_live_enablement_policy": build_factor_mix_live_enablement_policy(),
            "momentum_live_enablement_policy": build_momentum_live_enablement_policy(),
            "policy_value_live_enablement_policy": build_policy_value_live_enablement_policy(),
            "special_situation_live_enablement_policy": build_special_situation_live_enablement_policy(),
            "errors": [*validation_as_of_errors, "evidence file must contain a JSON object"],
            "warnings": [],
        }
    return validate_live_enablement_evidence(evidence, validation_as_of=validation_as_of)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an HK snapshot live-enable evidence pack.")
    parser.add_argument("--evidence-file")
    parser.add_argument("--print-template", action="store_true", help="Print a fillable evidence-pack template")
    parser.add_argument("--profile")
    parser.add_argument("--platform", choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--validation-as-of", help="Override validation date for evidence freshness checks")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args(argv)

    if args.print_template:
        if not args.profile or not args.platform:
            parser.error("--profile and --platform are required with --print-template")
        payload = build_live_enablement_evidence_template(args.profile, platform=args.platform)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if not args.evidence_file:
        parser.error("--evidence-file is required unless --print-template is set")

    payload = validate_live_enablement_evidence_file(args.evidence_file, validation_as_of=args.validation_as_of)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"platform={payload['platform']}")
        print(f"validation_status={payload['validation_status']}")
        print(f"live_enablement_allowed={payload['live_enablement_allowed']}")
        for error in payload["errors"]:
            print(f"error={error}")
    return 0 if payload["live_enablement_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
