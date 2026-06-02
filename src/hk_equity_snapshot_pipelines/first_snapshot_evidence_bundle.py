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
from .first_snapshot_promotion_plan import (
    DEFAULT_PLATFORMS,
    FIRST_SNAPSHOT_PROFILE_ORDER,
    SUPPORTED_FIRST_SNAPSHOT_EVIDENCE_PROFILE_ORDER,
)
from .live_enablement_evidence import STRATEGY_POLICY_EVIDENCE_SECTION, build_live_enablement_evidence_template
from .quality_yield_live_enablement_policy import build_quality_yield_live_enablement_policy
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS


FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION = "hk_first_snapshot_evidence_bundle.v1"
FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS = "pending_operator_production_evidence"
DEFAULT_OUTPUT_DIR = Path("data/output/first_snapshot_evidence_bundles")


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
        raise ValueError("At least one platform is required")
    return tuple(normalized)


def _bool_fields(section: dict[str, Any]) -> list[str]:
    return [key for key, value in section.items() if value is False]


def _metric_fields(section: dict[str, Any]) -> list[str]:
    return [
        key
        for key, value in section.items()
        if value is None or isinstance(value, (int, float))
    ]


def _template_section(template: dict[str, Any], section_name: str) -> dict[str, Any]:
    section = dict(template[section_name])
    section["section_name"] = section_name
    section["profile"] = template["profile"]
    section["contract_version"] = template["contract_version"]
    section["template_status"] = "pending_operator_evidence"
    return section


def build_first_snapshot_evidence_bundle(
    profile: str,
    *,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_profile = normalize_first_snapshot_profile(profile)
    selected_platforms = _normalize_platforms(platforms)
    contract = get_profile_contract(selected_profile)
    evidence_profile = get_first_snapshot_evidence_profile(contract.profile)
    reference_template = build_live_enablement_evidence_template(contract.profile, platform=selected_platforms[0])
    production_source_template = _template_section(reference_template, "production_snapshot_source_audit")
    walk_forward_template = _template_section(reference_template, "walk_forward_backtest")
    strategy_policy_template = _template_section(reference_template, STRATEGY_POLICY_EVIDENCE_SECTION)
    platform_templates = {
        platform: build_live_enablement_evidence_template(contract.profile, platform=platform)
        for platform in selected_platforms
    }
    quality_yield_policy = build_quality_yield_live_enablement_policy()
    return {
        "bundle_version": FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION,
        "status": FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS,
        "profile": contract.profile,
        "display_name": contract.display_name,
        "contract_version": contract.contract_version,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_deployment_allowed": False,
        "platforms": list(selected_platforms),
        "production_source_audit_template": production_source_template,
        "walk_forward_backtest_template": walk_forward_template,
        "strategy_policy_evidence_template": strategy_policy_template,
        "platform_live_enablement_templates": platform_templates,
        "production_source_required_columns": list(evidence_profile.required_production_columns),
        "production_source_focus": list(evidence_profile.production_source_focus),
        "quality_yield_focus": list(evidence_profile.quality_yield_focus),
        "production_source_required_boolean_fields": _bool_fields(production_source_template),
        "walk_forward_required_metric_fields": _metric_fields(walk_forward_template),
        "walk_forward_required_boolean_controls": _bool_fields(walk_forward_template),
        "quality_yield_required_ablation_tests": quality_yield_policy["required_ablation_tests"],
        "quality_yield_required_stress_tests": quality_yield_policy["required_stress_tests"],
        "quality_yield_required_data_provenance": quality_yield_policy["required_data_provenance"],
        "validation_commands": {
            platform: (
                "hkeq-validate-live-enable-evidence "
                f"--evidence-file evidence_templates/{platform}_live_enablement_evidence.template.json --json"
            )
            for platform in selected_platforms
        },
        "operator_next_steps": [
            "Replace every pending template field with point-in-time production evidence.",
            "Attach immutable gs://, s3://, or https:// evidence URIs without secret-like query parameters.",
            "Run survivorship-safe walk-forward backtests with at least three OOS folds and max drawdown <= 30%.",
            "Run LongBridge and IBKR dry-run order previews before any runtime promotion.",
            "Submit the completed evidence through CodexAuditBridge monthly audit before live-enable approval.",
        ],
        "stop_conditions": [
            "sample_artifacts_or_synthetic_data_used_as_evidence",
            "current_constituents_used_for_historical_universe",
            "future_financials_or_post_trade_data_used_in_signal",
            "full_sample_parameter_selection_or_unbounded_grid_search",
            "missing_hk_cost_slippage_lot_size_or_suspension_model",
            "drawdown_above_30_percent_or_fewer_than_three_oos_folds",
            "missing_platform_dry_run_or_bilingual_notification_evidence",
        ],
    }


def build_first_snapshot_evidence_bundles(
    *,
    profiles: tuple[str, ...] = FIRST_SNAPSHOT_PROFILE_ORDER,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_profiles = tuple(profile.profile for profile in iter_first_snapshot_evidence_profiles(profiles))
    bundles = [build_first_snapshot_evidence_bundle(profile, platforms=platforms) for profile in selected_profiles]
    return {
        "bundle_version": FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION,
        "status": FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS,
        "profiles_in_scope": list(selected_profiles),
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_deployment_allowed": False,
        "bundles": bundles,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _markdown(payload: dict[str, Any]) -> str:
    bool_fields = "\n".join(f"- `{field}`" for field in payload["production_source_required_boolean_fields"])
    metric_fields = "\n".join(f"- `{field}`" for field in payload["walk_forward_required_metric_fields"])
    controls = "\n".join(f"- `{field}`" for field in payload["walk_forward_required_boolean_controls"])
    source_focus = "\n".join(f"- `{field}`" for field in payload["production_source_focus"])
    platforms = ", ".join(payload["platforms"])
    return "\n".join(
        [
            f"# {payload['display_name']} Evidence Bundle",
            "",
            "This bundle provides production-source and walk-forward backtest evidence templates.",
            "It is non-live and must not be used to remove dry-run controls.",
            "",
            "## Status",
            "",
            f"- Profile: `{payload['profile']}`",
            f"- Status: `{payload['status']}`",
            f"- Platforms: `{platforms}`",
            f"- Runtime enabled: `{payload['runtime_enabled']}`",
            f"- Live enablement allowed: `{payload['live_enablement_allowed']}`",
            "",
            "## Production source focus",
            "",
            source_focus,
            "",
            "## Production source required boolean fields",
            "",
            bool_fields,
            "",
            "## Walk-forward required metric fields",
            "",
            metric_fields,
            "",
            "## Walk-forward required boolean controls",
            "",
            controls,
            "",
        ]
    )


def write_first_snapshot_evidence_bundles(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    profiles: tuple[str, ...] = FIRST_SNAPSHOT_PROFILE_ORDER,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_first_snapshot_evidence_bundles(profiles=profiles, platforms=platforms)
    bundle_paths: dict[str, dict[str, Any]] = {}
    for bundle in payload["bundles"]:
        profile_dir = output_dir / bundle["profile"]
        evidence_dir = profile_dir / "evidence_templates"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = profile_dir / "evidence_bundle.json"
        readme_path = profile_dir / "README.md"
        production_source_path = evidence_dir / "production_source_audit.template.json"
        walk_forward_path = evidence_dir / "walk_forward_backtest.template.json"
        strategy_policy_path = evidence_dir / "quality_yield_strategy_policy_evidence.template.json"
        _write_json(bundle_path, bundle)
        readme_path.write_text(_markdown(bundle), encoding="utf-8")
        _write_json(production_source_path, bundle["production_source_audit_template"])
        _write_json(walk_forward_path, bundle["walk_forward_backtest_template"])
        _write_json(strategy_policy_path, bundle["strategy_policy_evidence_template"])
        platform_template_paths: dict[str, str] = {}
        for platform, template in bundle["platform_live_enablement_templates"].items():
            template_path = evidence_dir / f"{platform}_live_enablement_evidence.template.json"
            _write_json(template_path, template)
            platform_template_paths[platform] = str(template_path)
        bundle_paths[bundle["profile"]] = {
            "bundle_path": str(bundle_path),
            "readme_path": str(readme_path),
            "production_source_audit_template_path": str(production_source_path),
            "walk_forward_backtest_template_path": str(walk_forward_path),
            "strategy_policy_evidence_template_path": str(strategy_policy_path),
            "platform_live_enablement_template_paths": platform_template_paths,
        }
    index_path = output_dir / "first_snapshot_evidence_bundles.json"
    _write_json(index_path, payload)
    return {**payload, "index_path": str(index_path), "bundle_paths": bundle_paths}


def _parse_profiles(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return FIRST_SNAPSHOT_PROFILE_ORDER
    return tuple(normalize_first_snapshot_profile(value) for value in values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build evidence templates for the first HK snapshot candidates.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for generated bundles.")
    parser.add_argument(
        "--profile",
        action="append",
        choices=SUPPORTED_FIRST_SNAPSHOT_EVIDENCE_PROFILE_ORDER,
        help="Profile to include; may be repeated. Defaults to the active first snapshot candidate.",
    )
    parser.add_argument(
        "--platform",
        action="append",
        choices=sorted(SUPPORTED_SNAPSHOT_PLATFORMS),
        help="Platform to include; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--json", action="store_true", help="Print bundle JSON without writing files.")
    args = parser.parse_args(argv)
    profiles = _parse_profiles(args.profile)
    platforms = tuple(args.platform or DEFAULT_PLATFORMS)
    if args.json:
        payload = build_first_snapshot_evidence_bundles(profiles=profiles, platforms=platforms)
    else:
        payload = write_first_snapshot_evidence_bundles(output_dir=Path(args.output_dir), profiles=profiles, platforms=platforms)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "FIRST_SNAPSHOT_EVIDENCE_BUNDLE_STATUS",
    "FIRST_SNAPSHOT_EVIDENCE_BUNDLE_VERSION",
    "build_first_snapshot_evidence_bundle",
    "build_first_snapshot_evidence_bundles",
    "main",
    "write_first_snapshot_evidence_bundles",
]
