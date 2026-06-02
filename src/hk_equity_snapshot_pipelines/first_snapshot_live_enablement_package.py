from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .contracts import get_profile_contract
from .first_snapshot_evidence_profiles import (
    get_first_snapshot_evidence_profile,
    iter_first_snapshot_evidence_profiles,
    normalize_first_snapshot_profile,
)
from .first_snapshot_promotion_plan import DEFAULT_PLATFORMS, FIRST_SNAPSHOT_PROFILE_ORDER, build_first_snapshot_promotion_plan
from .live_enablement_evidence import REQUIRED_SECTIONS, STRATEGY_POLICY_EVIDENCE_SECTION
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS, build_snapshot_readiness


FIRST_SNAPSHOT_PACKAGE_VERSION = "hk_first_snapshot_live_enablement_package.v1"
FIRST_SNAPSHOT_PACKAGE_STATUS = "evidence_package_not_live_enabled"
DEFAULT_OUTPUT_DIR = Path("data/output/first_snapshot_live_enablement_packages")


def _normalize_platforms(platforms: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for platform in platforms:
        candidate = str(platform or "").strip().lower()
        if candidate not in SUPPORTED_SNAPSHOT_PLATFORMS:
            known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
            raise ValueError(f"Unsupported snapshot platform {platform!r}; known platforms: {known}")
        if candidate not in normalized:
            normalized.append(candidate)
    if not normalized:
        raise ValueError("At least one snapshot platform is required")
    return tuple(normalized)


def _evidence_files(platforms: tuple[str, ...]) -> list[dict[str, Any]]:
    shared = [
        ("production_snapshot_source_audit", "production_source_audit.json"),
        ("walk_forward_backtest", "walk_forward_backtest.json"),
        ("artifact_pack_validation", "artifact_pack_validation.json"),
        (STRATEGY_POLICY_EVIDENCE_SECTION, "quality_yield_strategy_policy_evidence.json"),
        ("operator_approval_and_rollout_plan", "operator_approval_and_rollout_plan.json"),
    ]
    files = [
        {
            "section": section,
            "path": f"evidence/{filename}",
            "required": True,
            "status": "missing_until_operator_supplies_validated_evidence",
        }
        for section, filename in shared
    ]
    for platform in platforms:
        files.append(
            {
                "section": f"{platform}_live_enablement_evidence",
                "path": f"evidence/{platform}_live_enablement_evidence.json",
                "required": True,
                "status": "missing_until_platform_dry_run_evidence_passes",
                "validation_command": (
                    "hkeq-validate-live-enable-evidence "
                    f"--evidence-file evidence/{platform}_live_enablement_evidence.json --json"
                ),
            }
        )
    return files


def _gate_summary(profile_plan: dict[str, Any], *, profile: str) -> list[dict[str, Any]]:
    evidence_profile = get_first_snapshot_evidence_profile(profile)
    gates = [
        {
            "gate": "production_source_audit",
            "required": True,
            "evidence_section": "production_snapshot_source_audit",
            "success_condition": "point-in-time production source audit passes; sample artifacts are not used",
        },
        {
            "gate": "walk_forward_backtest",
            "required": True,
            "evidence_section": "walk_forward_backtest",
            "success_condition": "at least 3 independent OOS folds, max drawdown <= 30%, net HK costs",
        },
        {
            "gate": "artifact_pack_validation",
            "required": True,
            "evidence_section": "artifact_pack_validation",
            "success_condition": "snapshot, manifest, ranking, release summary, and sha256 provenance validate",
        },
        {
            "gate": "platform_dry_run_evidence",
            "required": True,
            "evidence_section": "platform_dry_run_order_preview",
            "success_condition": "LongBridge and IBKR previews include quotes, fee breakdown, lots, capacity, and sha256",
        },
        {
            "gate": "bilingual_notification_evidence",
            "required": True,
            "evidence_section": "platform_dry_run_order_preview.notification_audit",
            "success_condition": "EN and ZH-Hans notification previews plus delivery-log URI use the unified format",
        },
        {
            "gate": "operator_approval_and_rollout_plan",
            "required": True,
            "evidence_section": "risk_approval",
            "success_condition": "operator approval, staged rollout, tripwires, kill switch, and rollback plan exist",
        },
    ]
    return [
        {
            **gate,
            "profile_specific_focus": (
                [*profile_plan["profile_specific_next_evidence"], *evidence_profile.production_source_focus]
                if gate["gate"] == "production_source_audit"
                else []
            ),
        }
        for gate in gates
    ]


def build_first_snapshot_live_enablement_package(
    profile: str,
    *,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_profile = normalize_first_snapshot_profile(profile)
    selected_platforms = _normalize_platforms(platforms)
    contract = get_profile_contract(selected_profile)
    plan = build_first_snapshot_promotion_plan(profile=contract.profile, platforms=selected_platforms)
    profile_plan = plan["profiles"][0]
    readiness_by_platform = {
        platform: build_snapshot_readiness(contract.profile, platform_id=platform)
        for platform in selected_platforms
    }
    readiness_commands = {
        platform: f"python scripts/print_snapshot_readiness.py --profile {contract.profile} --platform {platform} --json"
        for platform in selected_platforms
    }
    evidence_template_commands = {
        platform: readiness["live_enablement_evidence_validation"]["template_command"]
        for platform, readiness in readiness_by_platform.items()
    }
    thresholds = profile_plan["live_enablement_thresholds"]
    return {
        "package_version": FIRST_SNAPSHOT_PACKAGE_VERSION,
        "profile": contract.profile,
        "display_name": contract.display_name,
        "status": FIRST_SNAPSHOT_PACKAGE_STATUS,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_deployment_allowed": False,
        "dry_run_only_until_all_gates_pass": True,
        "candidate_rank": profile_plan["rank"],
        "promotion_bucket": profile_plan["promotion_bucket"],
        "recommended_live_enablement_stage": profile_plan["recommended_live_enablement_stage"],
        "contract_version": contract.contract_version,
        "artifact_filenames": profile_plan["artifact_filenames"],
        "platforms": list(selected_platforms),
        "live_enablement_thresholds": thresholds,
        "required_evidence_sections": [*REQUIRED_SECTIONS, STRATEGY_POLICY_EVIDENCE_SECTION],
        "required_evidence_files": _evidence_files(selected_platforms),
        "gate_summary": _gate_summary(profile_plan, profile=contract.profile),
        "commands": {
            "sample_artifact_smoke": profile_plan["sample_build_commands"],
            "print_first_snapshot_promotion_plan": (
                f"python scripts/print_first_snapshot_promotion_plan.py --profile {contract.profile} --json"
            ),
            "artifact_pack_validation": profile_plan["artifact_validation_command"],
            "readiness": readiness_commands,
            "live_enablement_evidence_templates": evidence_template_commands,
            "live_enablement_evidence_validation": profile_plan["live_enablement_evidence_validation_command"],
        },
        "platform_env_templates": profile_plan["platform_env_templates"],
        "neutral_gcs_prefix_hints": profile_plan["neutral_gcs_prefix_hints"],
        "blocking_reasons": [
            *plan["blocking_reasons"],
            "This package is an evidence architecture bundle only; it must not flip runtime_enabled.",
            "LongBridge and IBKR must remain dry-run-only until validated evidence and approval are present.",
        ],
        "stop_conditions": [
            "sample_artifacts_used_as_production_data",
            "fewer_than_three_independent_oos_folds",
            "any_oos_fold_drawdown_above_30_percent",
            "fee_slippage_spread_stress_excess_return_non_positive",
            "missing_longbridge_or_ibkr_dry_run_order_preview",
            "missing_bilingual_notification_delivery_log",
            "missing_operator_approval_or_rollback_plan",
        ],
    }


def build_first_snapshot_live_enablement_packages(
    *,
    profiles: tuple[str, ...] = FIRST_SNAPSHOT_PROFILE_ORDER,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_profiles = tuple(profile.profile for profile in iter_first_snapshot_evidence_profiles(profiles))
    packages = [
        build_first_snapshot_live_enablement_package(profile, platforms=platforms)
        for profile in selected_profiles
    ]
    return {
        "package_version": FIRST_SNAPSHOT_PACKAGE_VERSION,
        "status": FIRST_SNAPSHOT_PACKAGE_STATUS,
        "profiles_in_scope": list(selected_profiles),
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_deployment_allowed": False,
        "packages": packages,
    }


def _markdown(payload: dict[str, Any]) -> str:
    gates = "\n".join(
        f"- **{gate['gate']}**: {gate['success_condition']}"
        for gate in payload["gate_summary"]
    )
    evidence_files = "\n".join(
        f"- `{item['path']}` — {item['section']}"
        for item in payload["required_evidence_files"]
    )
    stop_conditions = "\n".join(f"- `{item}`" for item in payload["stop_conditions"])
    platforms = ", ".join(payload["platforms"])
    thresholds = payload["live_enablement_thresholds"]
    return "\n".join(
        [
            f"# {payload['display_name']} Live-Enable Evidence Package",
            "",
            "This package defines the evidence architecture for one of the first three HK snapshot candidates.",
            "It does not enable live trading, deploy Cloud Run, or remove platform dry-run controls.",
            "",
            "## Status",
            "",
            f"- Profile: `{payload['profile']}`",
            f"- Status: `{payload['status']}`",
            f"- Runtime enabled: `{payload['runtime_enabled']}`",
            f"- Live enablement allowed: `{payload['live_enablement_allowed']}`",
            f"- Production deployment allowed: `{payload['production_deployment_allowed']}`",
            f"- Platforms in scope: `{platforms}`",
            "",
            "## Thresholds",
            "",
            f"- Max drawdown: `{thresholds['max_allowed_backtest_drawdown']:.2f}`",
            f"- Minimum OOS folds: `{thresholds['min_required_oos_fold_count']}`",
            f"- Max annualized turnover: `{thresholds['max_allowed_annualized_turnover']:.2f}`",
            f"- Max single-period contribution: `{thresholds['max_single_period_return_contribution']:.2f}`",
            "",
            "## Gates",
            "",
            gates,
            "",
            "## Required evidence files",
            "",
            evidence_files,
            "",
            "## Stop conditions",
            "",
            stop_conditions,
            "",
        ]
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_first_snapshot_live_enablement_packages(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    profiles: tuple[str, ...] = FIRST_SNAPSHOT_PROFILE_ORDER,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_first_snapshot_live_enablement_packages(profiles=profiles, platforms=platforms)
    package_paths: dict[str, dict[str, str]] = {}
    for package in payload["packages"]:
        profile_dir = output_dir / package["profile"]
        profile_dir.mkdir(parents=True, exist_ok=True)
        json_path = profile_dir / "live_enablement_package.json"
        markdown_path = profile_dir / "live_enablement_package.md"
        _write_json(json_path, package)
        markdown_path.write_text(_markdown(package), encoding="utf-8")
        package_paths[package["profile"]] = {
            "json_path": str(json_path),
            "markdown_path": str(markdown_path),
        }
    index_path = output_dir / "first_snapshot_live_enablement_packages.json"
    _write_json(index_path, payload)
    return {
        **payload,
        "index_path": str(index_path),
        "package_paths": package_paths,
    }


def _parse_profiles(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return FIRST_SNAPSHOT_PROFILE_ORDER
    return tuple(normalize_first_snapshot_profile(value) for value in values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build live-enable evidence packages for the first HK snapshot candidates.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for generated packages.")
    parser.add_argument(
        "--profile",
        action="append",
        choices=FIRST_SNAPSHOT_PROFILE_ORDER,
        help="Profile to include; may be repeated. Defaults to the first three snapshot candidates.",
    )
    parser.add_argument(
        "--platform",
        action="append",
        choices=sorted(SUPPORTED_SNAPSHOT_PLATFORMS),
        help="Platform to include; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--json", action="store_true", help="Print package JSON without writing files.")
    args = parser.parse_args(argv)
    profiles = _parse_profiles(args.profile)
    platforms = tuple(args.platform or DEFAULT_PLATFORMS)
    if args.json:
        payload = build_first_snapshot_live_enablement_packages(profiles=profiles, platforms=platforms)
    else:
        payload = write_first_snapshot_live_enablement_packages(
            output_dir=Path(args.output_dir),
            profiles=profiles,
            platforms=platforms,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "FIRST_SNAPSHOT_PACKAGE_STATUS",
    "FIRST_SNAPSHOT_PACKAGE_VERSION",
    "build_first_snapshot_live_enablement_package",
    "build_first_snapshot_live_enablement_packages",
    "main",
    "write_first_snapshot_live_enablement_packages",
]
