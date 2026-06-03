from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE, get_profile_contract
from .live_enablement_evidence import (
    STRATEGY_POLICY_EVIDENCE_SECTION,
    build_live_enablement_evidence_template,
    validate_live_enablement_evidence,
)
from .live_enablement_policy import get_min_required_rebalance_windows
from .quality_yield_live_enablement_policy import build_quality_yield_live_enablement_policy
from .rollout_risk_policy import REQUIRED_ROLLOUT_RISK_FIELDS, build_rollout_risk_policy
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_operator_evidence")
DRAFT_VERSION = "hk_low_vol_dividend_quality_snapshot.operator_evidence_draft.v1"
BROKER_PERMISSION_FIELDS = (
    "hk_market_data",
    "sehk_trading_permission",
    "hkd_cash_handling",
    "fees_verified",
    "stamp_duty_or_exemption_verified",
)
RISK_APPROVAL_FIELDS = (
    "operator_approved",
    "strategy_runtime_enablement_approved",
    "dry_run_removal_approved",
)
OPERATOR_EVIDENCE_SECTIONS = (
    "broker_permission_and_fee_verification",
    "paper_or_dry_run_rebalance_window",
    "runtime_rollout_plan",
    "risk_approval",
    STRATEGY_POLICY_EVIDENCE_SECTION,
)


def _read_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def _stable(value: str | None) -> str:
    return str(value or "").strip()


def _normalize_platform(platform: str) -> str:
    normalized = str(platform or "").strip().lower()
    if normalized not in SUPPORTED_SNAPSHOT_PLATFORMS:
        known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
        raise ValueError(f"Unsupported snapshot platform {platform!r}; known platforms: {known}")
    return normalized


def _all_true(section: Mapping[str, Any], fields: tuple[str, ...]) -> bool:
    return all(section.get(field) is True for field in fields)


def _number_within(value: float | None, *, maximum: float) -> bool:
    return value is not None and 0 <= float(value) <= maximum


def _strategy_policy_required_fields() -> tuple[str, ...]:
    policy = build_quality_yield_live_enablement_policy()
    return tuple(
        str(field)
        for field in (
            *policy["required_ablation_tests"],
            *policy["required_stress_tests"],
            *policy["required_data_provenance"],
        )
    )


def _apply_strategy_policy_controls(
    section: dict[str, Any],
    *,
    controls_file: str | Path | None,
    confirm_all: bool,
) -> None:
    required_fields = _strategy_policy_required_fields()
    if controls_file is not None:
        controls = _read_json_object(controls_file)
        for field in required_fields:
            if field in controls:
                section[field] = controls[field] is True
    if confirm_all:
        for field in required_fields:
            section[field] = True


def _section_errors(errors: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {section: [] for section in OPERATOR_EVIDENCE_SECTIONS}
    for error in errors:
        for section in OPERATOR_EVIDENCE_SECTIONS:
            if str(error).startswith(f"{section}.") or str(error).startswith("missing required evidence section for"):
                grouped.setdefault(section, []).append(str(error))
                break
    return {section: values for section, values in grouped.items() if values}


def build_low_vol_dividend_operator_evidence_draft(
    *,
    platform: str,
    evidence_generated_at: str,
    broker_evidence_uri: str = "",
    confirm_hk_market_data: bool = False,
    confirm_sehk_trading_permission: bool = False,
    confirm_hkd_cash_handling: bool = False,
    confirm_fees_verified: bool = False,
    confirm_stamp_duty_or_exemption_verified: bool = False,
    rebalance_evidence_uri: str = "",
    rebalance_window_count: int = 0,
    confirm_rebalance_or_event_window_covered: bool = False,
    rollout_evidence_uri: str = "",
    initial_capital_fraction: float | None = None,
    per_symbol_capital_fraction: float | None = None,
    intraday_drawdown_tripwire: float | None = None,
    cumulative_drawdown_tripwire: float | None = None,
    observation_trading_days_before_scale_up: int = 0,
    confirm_staged_rollout_plan: bool = False,
    confirm_kill_switch: bool = False,
    confirm_rollback_plan: bool = False,
    confirm_post_deploy_monitoring: bool = False,
    confirm_operator_notification: bool = False,
    confirm_severe_weather_trading_runbook: bool = False,
    confirm_vcm_cooling_off_handling: bool = False,
    approval_reference: str = "",
    confirm_operator_approved: bool = False,
    confirm_strategy_runtime_enablement_approved: bool = False,
    confirm_dry_run_removal_approved: bool = False,
    strategy_policy_evidence_uri: str = "",
    strategy_policy_controls_file: str | Path | None = None,
    confirm_all_strategy_policy_evidence: bool = False,
) -> dict[str, Any]:
    normalized_platform = _normalize_platform(platform)
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE)
    template = build_live_enablement_evidence_template(contract.profile, platform=normalized_platform)
    template["validation_as_of"] = evidence_generated_at

    broker_section = dict(template["broker_permission_and_fee_verification"])
    broker_section.update(
        {
            "hk_market_data": bool(confirm_hk_market_data),
            "sehk_trading_permission": bool(confirm_sehk_trading_permission),
            "hkd_cash_handling": bool(confirm_hkd_cash_handling),
            "fees_verified": bool(confirm_fees_verified),
            "stamp_duty_or_exemption_verified": bool(confirm_stamp_duty_or_exemption_verified),
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": _stable(broker_evidence_uri),
        }
    )
    broker_section["status"] = "passed" if _stable(broker_evidence_uri) and _all_true(broker_section, BROKER_PERMISSION_FIELDS) else "pending"

    rebalance_section = dict(template["paper_or_dry_run_rebalance_window"])
    min_window_count = get_min_required_rebalance_windows(contract.profile)
    rebalance_section.update(
        {
            "window_count": int(rebalance_window_count),
            "min_required_window_count": min_window_count,
            "rebalance_or_event_window_covered": bool(confirm_rebalance_or_event_window_covered),
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": _stable(rebalance_evidence_uri),
        }
    )
    rebalance_section["status"] = (
        "passed"
        if _stable(rebalance_evidence_uri)
        and int(rebalance_window_count) >= min_window_count
        and confirm_rebalance_or_event_window_covered
        else "pending"
    )

    rollout_policy = build_rollout_risk_policy()
    rollout_section = dict(template["runtime_rollout_plan"])
    rollout_section.update(
        {
            "staged_rollout_plan_ready": bool(confirm_staged_rollout_plan),
            "initial_capital_fraction": initial_capital_fraction,
            "per_symbol_capital_fraction": per_symbol_capital_fraction,
            "intraday_drawdown_tripwire": intraday_drawdown_tripwire,
            "cumulative_drawdown_tripwire": cumulative_drawdown_tripwire,
            "observation_trading_days_before_scale_up": int(observation_trading_days_before_scale_up),
            "kill_switch_ready": bool(confirm_kill_switch),
            "rollback_plan_ready": bool(confirm_rollback_plan),
            "post_deploy_monitoring_ready": bool(confirm_post_deploy_monitoring),
            "operator_notification_ready": bool(confirm_operator_notification),
            "severe_weather_trading_runbook_ready": bool(confirm_severe_weather_trading_runbook),
            "vcm_cooling_off_handling_ready": bool(confirm_vcm_cooling_off_handling),
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": _stable(rollout_evidence_uri),
        }
    )
    rollout_section["status"] = (
        "passed"
        if all(
            (
                _stable(rollout_evidence_uri),
                _all_true(rollout_section, REQUIRED_ROLLOUT_RISK_FIELDS),
                _number_within(
                    initial_capital_fraction,
                    maximum=float(rollout_policy["max_initial_capital_fraction"]),
                ),
                _number_within(
                    per_symbol_capital_fraction,
                    maximum=float(rollout_policy["max_per_symbol_capital_fraction"]),
                ),
                _number_within(
                    intraday_drawdown_tripwire,
                    maximum=float(rollout_policy["max_intraday_drawdown_tripwire"]),
                ),
                _number_within(
                    cumulative_drawdown_tripwire,
                    maximum=float(rollout_policy["max_cumulative_drawdown_tripwire"]),
                ),
                int(observation_trading_days_before_scale_up)
                >= int(rollout_policy["min_observation_trading_days_before_scale_up"]),
            )
        )
        else "pending"
    )

    risk_section = dict(template["risk_approval"])
    risk_section.update(
        {
            "operator_approved": bool(confirm_operator_approved),
            "strategy_runtime_enablement_approved": bool(confirm_strategy_runtime_enablement_approved),
            "dry_run_removal_approved": bool(confirm_dry_run_removal_approved),
            "approval_reference": _stable(approval_reference),
        }
    )
    risk_status = "passed" if _stable(approval_reference) and _all_true(risk_section, RISK_APPROVAL_FIELDS) else "pending"

    strategy_policy_section = dict(template[STRATEGY_POLICY_EVIDENCE_SECTION])
    _apply_strategy_policy_controls(
        strategy_policy_section,
        controls_file=strategy_policy_controls_file,
        confirm_all=confirm_all_strategy_policy_evidence,
    )
    strategy_policy_section.update(
        {
            "evidence_generated_at": evidence_generated_at,
            "evidence_uri": _stable(strategy_policy_evidence_uri),
        }
    )
    strategy_policy_fields = _strategy_policy_required_fields()
    strategy_policy_section["status"] = (
        "passed"
        if _stable(strategy_policy_evidence_uri) and _all_true(strategy_policy_section, strategy_policy_fields)
        else "pending"
    )

    template["broker_permission_and_fee_verification"] = broker_section
    template["paper_or_dry_run_rebalance_window"] = rebalance_section
    template["runtime_rollout_plan"] = rollout_section
    template["risk_approval"] = risk_section
    template[STRATEGY_POLICY_EVIDENCE_SECTION] = strategy_policy_section
    validation = validate_live_enablement_evidence(template, validation_as_of=evidence_generated_at)
    operator_errors = _section_errors(list(validation.get("errors") or []))
    section_statuses = {
        "broker_permission_and_fee_verification": broker_section["status"],
        "paper_or_dry_run_rebalance_window": rebalance_section["status"],
        "runtime_rollout_plan": rollout_section["status"],
        "risk_approval": risk_status,
        STRATEGY_POLICY_EVIDENCE_SECTION: strategy_policy_section["status"],
    }
    operator_sections_can_pass = all(status == "passed" for status in section_statuses.values()) and not operator_errors
    return {
        "draft_version": DRAFT_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "platform": normalized_platform,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "operator_sections_can_pass": operator_sections_can_pass,
        "section_statuses": section_statuses,
        "operator_section_errors_preview": {
            section: errors[:20]
            for section, errors in operator_errors.items()
        },
        "validation_status_after_merge": validation.get("validation_status"),
        "validation_errors_count_after_merge": len(validation.get("errors") or []),
        "broker_permission_and_fee_verification_draft": broker_section,
        "paper_or_dry_run_rebalance_window_draft": rebalance_section,
        "runtime_rollout_plan_draft": rollout_section,
        "risk_approval_draft": risk_section,
        "risk_approval_section_status": risk_status,
        "strategy_policy_evidence_draft": strategy_policy_section,
    }


def write_low_vol_dividend_operator_evidence_draft(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_operator_evidence_draft(**kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    platform = payload["platform"]
    paths = {
        "broker_permission_and_fee_verification_path": output_dir / f"{platform}_broker_permission_and_fee_verification.draft.json",
        "paper_or_dry_run_rebalance_window_path": output_dir / f"{platform}_paper_or_dry_run_rebalance_window.draft.json",
        "runtime_rollout_plan_path": output_dir / f"{platform}_runtime_rollout_plan.draft.json",
        "risk_approval_path": output_dir / f"{platform}_risk_approval.draft.json",
        "strategy_policy_evidence_path": output_dir / f"{platform}_strategy_policy_evidence.draft.json",
        "summary_path": output_dir / f"{platform}_operator_evidence_draft_summary.json",
    }
    write_json(paths["broker_permission_and_fee_verification_path"], payload["broker_permission_and_fee_verification_draft"])
    write_json(paths["paper_or_dry_run_rebalance_window_path"], payload["paper_or_dry_run_rebalance_window_draft"])
    write_json(paths["runtime_rollout_plan_path"], payload["runtime_rollout_plan_draft"])
    write_json(paths["risk_approval_path"], payload["risk_approval_draft"])
    write_json(paths["strategy_policy_evidence_path"], payload["strategy_policy_evidence_draft"])
    write_json(
        paths["summary_path"],
        {
            key: value
            for key, value in payload.items()
            if not key.endswith("_draft")
        },
    )
    return {
        **payload,
        **{key: str(value) for key, value in paths.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft HK low-vol dividend operator evidence sections.")
    parser.add_argument("--platform", required=True, choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--evidence-generated-at", required=True)
    parser.add_argument("--broker-evidence-uri", default="")
    parser.add_argument("--confirm-hk-market-data", action="store_true")
    parser.add_argument("--confirm-sehk-trading-permission", action="store_true")
    parser.add_argument("--confirm-hkd-cash-handling", action="store_true")
    parser.add_argument("--confirm-fees-verified", action="store_true")
    parser.add_argument("--confirm-stamp-duty-or-exemption-verified", action="store_true")
    parser.add_argument("--rebalance-evidence-uri", default="")
    parser.add_argument("--rebalance-window-count", type=int, default=0)
    parser.add_argument("--confirm-rebalance-or-event-window-covered", action="store_true")
    parser.add_argument("--rollout-evidence-uri", default="")
    parser.add_argument("--initial-capital-fraction", type=float)
    parser.add_argument("--per-symbol-capital-fraction", type=float)
    parser.add_argument("--intraday-drawdown-tripwire", type=float)
    parser.add_argument("--cumulative-drawdown-tripwire", type=float)
    parser.add_argument("--observation-trading-days-before-scale-up", type=int, default=0)
    parser.add_argument("--confirm-staged-rollout-plan", action="store_true")
    parser.add_argument("--confirm-kill-switch", action="store_true")
    parser.add_argument("--confirm-rollback-plan", action="store_true")
    parser.add_argument("--confirm-post-deploy-monitoring", action="store_true")
    parser.add_argument("--confirm-operator-notification", action="store_true")
    parser.add_argument("--confirm-severe-weather-trading-runbook", action="store_true")
    parser.add_argument("--confirm-vcm-cooling-off-handling", action="store_true")
    parser.add_argument("--approval-reference", default="")
    parser.add_argument("--confirm-operator-approved", action="store_true")
    parser.add_argument("--confirm-strategy-runtime-enablement-approved", action="store_true")
    parser.add_argument("--confirm-dry-run-removal-approved", action="store_true")
    parser.add_argument("--strategy-policy-evidence-uri", default="")
    parser.add_argument("--strategy-policy-controls-file")
    parser.add_argument("--confirm-all-strategy-policy-evidence", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_operator_evidence_draft(
        output_dir=args.output_dir,
        platform=args.platform,
        evidence_generated_at=args.evidence_generated_at,
        broker_evidence_uri=args.broker_evidence_uri,
        confirm_hk_market_data=args.confirm_hk_market_data,
        confirm_sehk_trading_permission=args.confirm_sehk_trading_permission,
        confirm_hkd_cash_handling=args.confirm_hkd_cash_handling,
        confirm_fees_verified=args.confirm_fees_verified,
        confirm_stamp_duty_or_exemption_verified=args.confirm_stamp_duty_or_exemption_verified,
        rebalance_evidence_uri=args.rebalance_evidence_uri,
        rebalance_window_count=args.rebalance_window_count,
        confirm_rebalance_or_event_window_covered=args.confirm_rebalance_or_event_window_covered,
        rollout_evidence_uri=args.rollout_evidence_uri,
        initial_capital_fraction=args.initial_capital_fraction,
        per_symbol_capital_fraction=args.per_symbol_capital_fraction,
        intraday_drawdown_tripwire=args.intraday_drawdown_tripwire,
        cumulative_drawdown_tripwire=args.cumulative_drawdown_tripwire,
        observation_trading_days_before_scale_up=args.observation_trading_days_before_scale_up,
        confirm_staged_rollout_plan=args.confirm_staged_rollout_plan,
        confirm_kill_switch=args.confirm_kill_switch,
        confirm_rollback_plan=args.confirm_rollback_plan,
        confirm_post_deploy_monitoring=args.confirm_post_deploy_monitoring,
        confirm_operator_notification=args.confirm_operator_notification,
        confirm_severe_weather_trading_runbook=args.confirm_severe_weather_trading_runbook,
        confirm_vcm_cooling_off_handling=args.confirm_vcm_cooling_off_handling,
        approval_reference=args.approval_reference,
        confirm_operator_approved=args.confirm_operator_approved,
        confirm_strategy_runtime_enablement_approved=args.confirm_strategy_runtime_enablement_approved,
        confirm_dry_run_removal_approved=args.confirm_dry_run_removal_approved,
        strategy_policy_evidence_uri=args.strategy_policy_evidence_uri,
        strategy_policy_controls_file=args.strategy_policy_controls_file,
        confirm_all_strategy_policy_evidence=args.confirm_all_strategy_policy_evidence,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"platform={payload['platform']}")
        print(f"operator_sections_can_pass={payload['operator_sections_can_pass']}")
        for section, status in payload["section_statuses"].items():
            print(f"section={section} status={status}")
        print(f"summary_path={payload['summary_path']}")
    return 0


__all__ = [
    "BROKER_PERMISSION_FIELDS",
    "DEFAULT_OUTPUT_DIR",
    "DRAFT_VERSION",
    "OPERATOR_EVIDENCE_SECTIONS",
    "RISK_APPROVAL_FIELDS",
    "build_low_vol_dividend_operator_evidence_draft",
    "main",
    "write_low_vol_dividend_operator_evidence_draft",
]
