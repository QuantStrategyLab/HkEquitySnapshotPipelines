from __future__ import annotations

import argparse
import datetime as dt
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .live_enablement_evidence import (
    REQUIRED_SECTIONS,
    STRATEGY_POLICY_EVIDENCE_SECTION,
    build_live_enablement_evidence_template,
    validate_live_enablement_evidence,
)
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_live_enablement_evidence")
ASSEMBLY_VERSION = "hk_low_vol_dividend_quality.live_enablement_evidence_assembly.v1"

SECTION_WRAPPER_KEYS: dict[str, tuple[str, ...]] = {
    "production_snapshot_source_audit": ("production_source_audit_draft",),
    "artifact_pack_validation": ("artifact_pack_validation_draft",),
    "walk_forward_backtest": ("walk_forward_backtest_draft",),
    "platform_dry_run_order_preview": ("platform_dry_run_order_preview_draft",),
    "broker_permission_and_fee_verification": ("broker_permission_and_fee_verification_draft",),
    "paper_or_dry_run_rebalance_window": ("paper_or_dry_run_rebalance_window_draft",),
    "runtime_rollout_plan": ("runtime_rollout_plan_draft",),
    "risk_approval": ("risk_approval_draft",),
    STRATEGY_POLICY_EVIDENCE_SECTION: ("strategy_policy_evidence_draft",),
}
ASSEMBLABLE_SECTIONS = (*REQUIRED_SECTIONS, STRATEGY_POLICY_EVIDENCE_SECTION)


def _read_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return payload


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalize_platform(platform: str) -> str:
    normalized = str(platform or "").strip().lower()
    if normalized not in SUPPORTED_SNAPSHOT_PLATFORMS:
        known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
        raise ValueError(f"Unsupported snapshot platform {platform!r}; known platforms: {known}")
    return normalized


def _extract_section(payload: Mapping[str, Any], section_name: str) -> dict[str, Any]:
    direct = payload.get(section_name)
    if isinstance(direct, Mapping):
        return dict(direct)

    nested_evidence = _as_mapping(payload.get("evidence"))
    nested_direct = nested_evidence.get(section_name)
    if isinstance(nested_direct, Mapping):
        return dict(nested_direct)

    for wrapper_key in SECTION_WRAPPER_KEYS[section_name]:
        wrapped = payload.get(wrapper_key)
        if isinstance(wrapped, Mapping):
            return dict(wrapped)
        nested_wrapped = nested_evidence.get(wrapper_key)
        if isinstance(nested_wrapped, Mapping):
            return dict(nested_wrapped)

    # Section-specific CLI arguments often point at files that already contain
    # the section object directly, e.g. artifact_pack_validation.draft.json.
    # Accept the object as-is when no wrapper is present; final validation still
    # enforces the real live-enable contract and catches wrong files.
    return dict(payload)


def _extract_evidence_object(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = _as_mapping(payload.get("evidence"))
    if nested.get("evidence_type"):
        return nested
    return payload


def _copy_known_sections(
    target: dict[str, Any],
    source: Mapping[str, Any],
    *,
    section_sources: dict[str, str],
    source_label: str,
) -> None:
    evidence = _extract_evidence_object(source)
    for section_name in ASSEMBLABLE_SECTIONS:
        section = evidence.get(section_name)
        if isinstance(section, Mapping):
            target[section_name] = dict(section)
            section_sources[section_name] = source_label


def _section_file_specs(
    *,
    production_source_audit_file: str | Path | None,
    artifact_pack_validation_file: str | Path | None,
    walk_forward_backtest_file: str | Path | None,
    platform_dry_run_file: str | Path | None,
    broker_permission_file: str | Path | None,
    rebalance_window_file: str | Path | None,
    runtime_rollout_file: str | Path | None,
    risk_approval_file: str | Path | None,
    strategy_policy_evidence_file: str | Path | None,
) -> tuple[tuple[str, str | Path | None], ...]:
    return (
        ("production_snapshot_source_audit", production_source_audit_file),
        ("artifact_pack_validation", artifact_pack_validation_file),
        ("walk_forward_backtest", walk_forward_backtest_file),
        ("platform_dry_run_order_preview", platform_dry_run_file),
        ("broker_permission_and_fee_verification", broker_permission_file),
        ("paper_or_dry_run_rebalance_window", rebalance_window_file),
        ("runtime_rollout_plan", runtime_rollout_file),
        ("risk_approval", risk_approval_file),
        (STRATEGY_POLICY_EVIDENCE_SECTION, strategy_policy_evidence_file),
    )


def build_low_vol_dividend_live_enablement_evidence_assembly(
    *,
    platform: str,
    validation_as_of: str | None = None,
    base_evidence_file: str | Path | None = None,
    production_source_audit_file: str | Path | None = None,
    artifact_pack_validation_file: str | Path | None = None,
    walk_forward_backtest_file: str | Path | None = None,
    platform_dry_run_file: str | Path | None = None,
    broker_permission_file: str | Path | None = None,
    rebalance_window_file: str | Path | None = None,
    runtime_rollout_file: str | Path | None = None,
    risk_approval_file: str | Path | None = None,
    strategy_policy_evidence_file: str | Path | None = None,
) -> dict[str, Any]:
    normalized_platform = _normalize_platform(platform)
    resolved_validation_as_of = validation_as_of or dt.date.today().isoformat()
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    evidence = build_live_enablement_evidence_template(contract.profile, platform=normalized_platform)
    evidence["validation_as_of"] = resolved_validation_as_of
    evidence["template_status"] = "assembled_pending_validation"
    evidence["assembly_version"] = ASSEMBLY_VERSION

    section_sources: dict[str, str] = {}
    if base_evidence_file is not None:
        base_payload = _read_json_object(base_evidence_file)
        _copy_known_sections(
            evidence,
            base_payload,
            section_sources=section_sources,
            source_label=str(base_evidence_file),
        )

    for section_name, file_path in _section_file_specs(
        production_source_audit_file=production_source_audit_file,
        artifact_pack_validation_file=artifact_pack_validation_file,
        walk_forward_backtest_file=walk_forward_backtest_file,
        platform_dry_run_file=platform_dry_run_file,
        broker_permission_file=broker_permission_file,
        rebalance_window_file=rebalance_window_file,
        runtime_rollout_file=runtime_rollout_file,
        risk_approval_file=risk_approval_file,
        strategy_policy_evidence_file=strategy_policy_evidence_file,
    ):
        if file_path is None:
            continue
        payload = _read_json_object(file_path)
        evidence[section_name] = _extract_section(payload, section_name)
        section_sources[section_name] = str(file_path)

    validation = validate_live_enablement_evidence(evidence, validation_as_of=resolved_validation_as_of)
    evidence["template_status"] = (
        "assembled_live_enablement_allowed"
        if validation.get("live_enablement_allowed") is True
        else "assembled_blocked_by_validation"
    )
    missing_section_sources = [section for section in ASSEMBLABLE_SECTIONS if section not in section_sources]
    return {
        "assembly_version": ASSEMBLY_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "platform": normalized_platform,
        "validation_as_of": validation["validation_as_of"],
        "provided_sections": sorted(section_sources),
        "missing_section_sources": missing_section_sources,
        "section_sources": section_sources,
        "validation_status": validation["validation_status"],
        "live_enablement_allowed": bool(validation.get("live_enablement_allowed")),
        "validation_errors_count": len(validation.get("errors") or []),
        "validation_errors_preview": list(validation.get("errors") or [])[:50],
        "evidence": evidence,
        "validation": validation,
    }


def write_low_vol_dividend_live_enablement_evidence_assembly(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_live_enablement_evidence_assembly(**kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    platform = payload["platform"]
    evidence_path = output_dir / f"{platform}_live_enablement_evidence.json"
    validation_path = output_dir / f"{platform}_live_enablement_evidence.validation.json"
    summary_path = output_dir / f"{platform}_live_enablement_evidence.assembly_summary.json"
    write_json(evidence_path, payload["evidence"])
    write_json(validation_path, payload["validation"])
    write_json(summary_path, {key: value for key, value in payload.items() if key not in {"evidence", "validation"}})
    return {
        **payload,
        "evidence_path": str(evidence_path),
        "validation_path": str(validation_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble HK low-vol dividend live-enable evidence files.")
    parser.add_argument("--platform", required=True, choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--validation-as-of", help="Validation date in YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--base-evidence-file", help="Optional existing evidence JSON to seed all known sections.")
    parser.add_argument("--production-source-audit-file")
    parser.add_argument("--artifact-pack-validation-file")
    parser.add_argument("--walk-forward-backtest-file")
    parser.add_argument("--platform-dry-run-file")
    parser.add_argument("--broker-permission-file")
    parser.add_argument("--rebalance-window-file")
    parser.add_argument("--runtime-rollout-file")
    parser.add_argument("--risk-approval-file")
    parser.add_argument("--strategy-policy-evidence-file")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fail-on-blocked", action="store_true", help="Return non-zero when validation blocks live-enable.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_live_enablement_evidence_assembly(
        output_dir=args.output_dir,
        platform=args.platform,
        validation_as_of=args.validation_as_of,
        base_evidence_file=args.base_evidence_file,
        production_source_audit_file=args.production_source_audit_file,
        artifact_pack_validation_file=args.artifact_pack_validation_file,
        walk_forward_backtest_file=args.walk_forward_backtest_file,
        platform_dry_run_file=args.platform_dry_run_file,
        broker_permission_file=args.broker_permission_file,
        rebalance_window_file=args.rebalance_window_file,
        runtime_rollout_file=args.runtime_rollout_file,
        risk_approval_file=args.risk_approval_file,
        strategy_policy_evidence_file=args.strategy_policy_evidence_file,
    )
    summary = {key: value for key, value in payload.items() if key not in {"evidence", "validation"}}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"platform={payload['platform']}")
        print(f"validation_status={payload['validation_status']}")
        print(f"live_enablement_allowed={payload['live_enablement_allowed']}")
        print(f"evidence_path={payload['evidence_path']}")
        print(f"validation_path={payload['validation_path']}")
        print(f"summary_path={payload['summary_path']}")
        for error in payload["validation_errors_preview"]:
            print(f"error={error}")
    if args.fail_on_blocked and payload["live_enablement_allowed"] is not True:
        return 1
    return 0


__all__ = [
    "ASSEMBLABLE_SECTIONS",
    "ASSEMBLY_VERSION",
    "DEFAULT_OUTPUT_DIR",
    "build_low_vol_dividend_live_enablement_evidence_assembly",
    "main",
    "write_low_vol_dividend_live_enablement_evidence_assembly",
]
