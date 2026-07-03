from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE, get_profile_contract
from .live_enablement_evidence import STRATEGY_POLICY_EVIDENCE_SECTION, build_live_enablement_evidence_template
from .quality_yield_live_enablement_policy import build_quality_yield_live_enablement_policy
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS


LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_VERSION = "hk_low_vol_dividend_evidence_bundle.v1"
LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_STATUS = "pending_operator_production_evidence"
DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_evidence_bundle")
DEFAULT_PLATFORMS = ("longbridge", "ibkr")


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


def build_low_vol_dividend_evidence_bundle(
    *,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_platforms = _normalize_platforms(platforms)
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE)
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
        "bundle_version": LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_VERSION,
        "status": LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_STATUS,
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
            "Submit the completed evidence through AIAuditBridge monthly audit before live-enable approval.",
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _markdown(payload: dict[str, Any]) -> str:
    bool_fields = "\n".join(f"- `{field}`" for field in payload["production_source_required_boolean_fields"])
    metric_fields = "\n".join(f"- `{field}`" for field in payload["walk_forward_required_metric_fields"])
    controls = "\n".join(f"- `{field}`" for field in payload["walk_forward_required_boolean_controls"])
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


def write_low_vol_dividend_evidence_bundle(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence_templates"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    payload = build_low_vol_dividend_evidence_bundle(platforms=platforms)

    bundle_path = output_dir / "low_vol_dividend_evidence_bundle.json"
    readme_path = output_dir / "README.md"
    production_source_path = evidence_dir / "production_source_audit.template.json"
    walk_forward_path = evidence_dir / "walk_forward_backtest.template.json"
    strategy_policy_path = evidence_dir / "quality_yield_strategy_policy_evidence.template.json"
    _write_json(bundle_path, payload)
    readme_path.write_text(_markdown(payload), encoding="utf-8")
    _write_json(production_source_path, payload["production_source_audit_template"])
    _write_json(walk_forward_path, payload["walk_forward_backtest_template"])
    _write_json(strategy_policy_path, payload["strategy_policy_evidence_template"])

    platform_template_paths: dict[str, str] = {}
    for platform, template in payload["platform_live_enablement_templates"].items():
        template_path = evidence_dir / f"{platform}_live_enablement_evidence.template.json"
        _write_json(template_path, template)
        platform_template_paths[platform] = str(template_path)

    return {
        **payload,
        "bundle_path": str(bundle_path),
        "readme_path": str(readme_path),
        "production_source_audit_template_path": str(production_source_path),
        "walk_forward_backtest_template_path": str(walk_forward_path),
        "strategy_policy_evidence_template_path": str(strategy_policy_path),
        "platform_live_enablement_template_paths": platform_template_paths,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build HK low-vol dividend production evidence templates.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for the bundle.")
    parser.add_argument(
        "--platform",
        action="append",
        choices=sorted(SUPPORTED_SNAPSHOT_PLATFORMS),
        help="Platform to include; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--json", action="store_true", help="Print bundle JSON without writing files.")
    args = parser.parse_args(argv)
    platforms = tuple(args.platform or DEFAULT_PLATFORMS)
    if args.json:
        payload = build_low_vol_dividend_evidence_bundle(platforms=platforms)
    else:
        payload = write_low_vol_dividend_evidence_bundle(output_dir=Path(args.output_dir), platforms=platforms)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_PLATFORMS",
    "LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_STATUS",
    "LOW_VOL_DIVIDEND_EVIDENCE_BUNDLE_VERSION",
    "build_low_vol_dividend_evidence_bundle",
    "main",
    "write_low_vol_dividend_evidence_bundle",
]
