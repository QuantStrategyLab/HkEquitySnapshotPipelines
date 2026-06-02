from __future__ import annotations

import argparse
import json
from typing import Any

from .contracts import (
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
)
from .snapshot_promotion_matrix import build_snapshot_promotion_matrix
from .snapshot_readiness import build_snapshot_readiness

FIRST_SNAPSHOT_PROMOTION_PLAN_VERSION = "hk_snapshot_first_promotion_plan.v1"
FIRST_SNAPSHOT_PROFILE_ORDER = (
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE,
    HK_FREE_CASH_FLOW_QUALITY_PROFILE,
)
DEFAULT_PLATFORMS = ("longbridge", "ibkr")

_SAMPLE_BUILD_COMMANDS: dict[str, dict[str, str]] = {
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE: {
        "sample_script": "PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py",
        "package_entrypoint": (
            "hkeq-build-low-vol-dividend-quality-snapshot "
            "--factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv "
            "--output-dir data/output/low_vol_dividend_quality"
        ),
    },
    HK_SHAREHOLDER_YIELD_QUALITY_PROFILE: {
        "sample_script": "PYTHONPATH=src python scripts/build_shareholder_yield_sample.py",
        "package_entrypoint": (
            "hkeq-build-shareholder-yield-quality-snapshot "
            "--factor-snapshot examples/shareholder_yield_quality/factor_snapshot.sample.csv "
            "--output-dir data/output/shareholder_yield_quality"
        ),
    },
    HK_FREE_CASH_FLOW_QUALITY_PROFILE: {
        "sample_script": "PYTHONPATH=src python scripts/build_free_cash_flow_sample.py",
        "package_entrypoint": (
            "hkeq-build-free-cash-flow-quality-snapshot "
            "--factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv "
            "--output-dir data/output/free_cash_flow_quality"
        ),
    },
}

_PROMOTION_STEPS = (
    {
        "step": 1,
        "name": "sample_artifact_smoke",
        "required": True,
        "description": "Build sample artifacts only to verify contract wiring; sample artifacts are not live data.",
    },
    {
        "step": 2,
        "name": "production_source_audit",
        "required": True,
        "description": (
            "Replace sample inputs with point-in-time production data and document source coverage, "
            "quality reports, corporate actions, suspensions, and missingness controls."
        ),
    },
    {
        "step": 3,
        "name": "walk_forward_backtest",
        "required": True,
        "description": (
            "Run survivorship-safe walk-forward backtests with at least three independent OOS folds, "
            "net HK costs, and max drawdown at or below the profile gate."
        ),
    },
    {
        "step": 4,
        "name": "artifact_pack_validation",
        "required": True,
        "description": "Validate the published snapshot CSV, manifest, ranking, release summary, and provenance.",
    },
    {
        "step": 5,
        "name": "platform_dry_run_evidence",
        "required": True,
        "description": (
            "Run IBKR and LongBridge dry-run order previews with lot-size, liquidity, fee, quote, "
            "bilingual notification, and delivery-log evidence."
        ),
    },
    {
        "step": 6,
        "name": "operator_approval_and_rollout_plan",
        "required": True,
        "description": "Collect approval reference, staged rollout plan, tripwires, kill switch, and rollback plan.",
    },
)


def _profiles_by_name(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["profile"]): row for row in matrix["profiles"]}


def _filter_profiles(profiles: tuple[str, ...], profile: str | None) -> tuple[str, ...]:
    if profile is None:
        return profiles
    normalized = str(profile).strip().lower().replace("-", "_")
    matched = tuple(candidate for candidate in profiles if candidate == normalized)
    if not matched:
        known = ", ".join(profiles)
        raise ValueError(f"Unsupported first snapshot promotion profile {profile!r}; known profiles: {known}")
    return matched


def _build_profile_plan(row: dict[str, Any], *, platforms: tuple[str, ...]) -> dict[str, Any]:
    profile = str(row["profile"])
    readiness_by_platform = {
        platform: build_snapshot_readiness(profile, platform_id=platform)
        for platform in platforms
    }
    readiness_commands = {
        platform: f"python scripts/print_snapshot_readiness.py --profile {profile} --platform {platform} --json"
        for platform in platforms
    }
    evidence_template_commands = {
        platform: readiness["live_enablement_evidence_validation"]["template_command"]
        for platform, readiness in readiness_by_platform.items()
    }
    platform_env_templates = {
        platform: readiness["platform_env_template"]
        for platform, readiness in readiness_by_platform.items()
    }
    neutral_gcs_prefix_hints = {
        platform: readiness["neutral_gcs_prefix_hint"]
        for platform, readiness in readiness_by_platform.items()
    }
    artifact_dir = f"data/output/{profile}"
    return {
        "rank": row["priority"],
        "profile": profile,
        "display_name": row["display_name"],
        "status": row["status"],
        "runtime_enabled": row["runtime_enabled"],
        "promotion_bucket": row["promotion_bucket"],
        "recommended_live_enablement_stage": row["recommended_live_enablement_stage"],
        "next_live_enablement_action": row["next_live_enablement_action"],
        "contract_version": row["contract_version"],
        "snapshot_type": row["snapshot_type"],
        "style_family": row["style_family"],
        "artifact_filenames": row["artifact_filenames"],
        "sample_build_commands": _SAMPLE_BUILD_COMMANDS[profile],
        "artifact_validation_command": (
            "hkeq-validate-snapshot-artifact-pack "
            f"--profile {profile} --artifact-dir {artifact_dir} --json"
        ),
        "readiness_commands": readiness_commands,
        "live_enablement_evidence_template_commands": evidence_template_commands,
        "live_enablement_evidence_validation_command": (
            "hkeq-validate-live-enable-evidence --evidence-file <live-enable-evidence.json> --json"
        ),
        "platform_env_templates": platform_env_templates,
        "neutral_gcs_prefix_hints": neutral_gcs_prefix_hints,
        "live_enablement_thresholds": row["live_enablement_thresholds"],
        "production_data_dependencies": row["production_data_dependencies"],
        "profile_specific_next_evidence": row["profile_specific_next_evidence"],
    }


def build_first_snapshot_promotion_plan(
    *,
    profile: str | None = None,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    matrix = build_snapshot_promotion_matrix()
    first_snapshot_candidates = tuple(matrix["first_snapshot_candidates"])
    if first_snapshot_candidates != FIRST_SNAPSHOT_PROFILE_ORDER:
        raise ValueError(
            "First snapshot candidate order drifted; update the first promotion plan before using it. "
            f"expected={FIRST_SNAPSHOT_PROFILE_ORDER!r} actual={first_snapshot_candidates!r}"
        )

    selected_profiles = _filter_profiles(first_snapshot_candidates, profile)
    rows_by_name = _profiles_by_name(matrix)
    return {
        "plan_version": FIRST_SNAPSHOT_PROMOTION_PLAN_VERSION,
        "source_project": matrix["source_project"],
        "status": "first_snapshot_promotion_plan_not_live_enabled",
        "live_enablement_allowed_without_evidence": False,
        "profiles_in_scope": list(selected_profiles),
        "excluded_from_scope": [
            candidate for candidate in matrix["recommended_live_enablement_sequence"] if candidate not in selected_profiles
        ],
        "promotion_steps": list(_PROMOTION_STEPS),
        "shared_gates": {
            "backtest_validation_policy": matrix["backtest_validation_policy"],
            "artifact_provenance_policy": matrix["artifact_provenance_policy"],
            "evidence_uri_policy": matrix["evidence_uri_policy"],
            "evidence_freshness_policy": matrix["evidence_freshness_policy"],
            "dry_run_order_preview_policy": matrix["dry_run_order_preview_policy"],
            "rollout_risk_policy": matrix["rollout_risk_policy"],
            "notification_audit_policy": matrix["notification_audit_policy"],
            "quality_yield_live_enablement_policy": matrix["quality_yield_live_enablement_policy"],
        },
        "profiles": [
            _build_profile_plan(rows_by_name[candidate], platforms=platforms)
            for candidate in selected_profiles
        ],
        "blocking_reasons": [
            "The three profiles remain architecture scaffolds until production data and evidence validators pass.",
            "Sample artifacts must never be used for scheduled live trading.",
            "This plan is read-only and does not deploy Cloud Run, publish artifacts, or place broker orders.",
        ],
    }


def _print_text(payload: dict[str, Any]) -> None:
    print(f"plan_version={payload['plan_version']}")
    print(f"status={payload['status']}")
    print("profiles_in_scope=" + ",".join(payload["profiles_in_scope"]))
    for profile in payload["profiles"]:
        print(f"- {profile['rank']}: {profile['profile']} ({profile['recommended_live_enablement_stage']})")
        print(f"  sample_script={profile['sample_build_commands']['sample_script']}")
        print(f"  artifact_validation={profile['artifact_validation_command']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the first HK snapshot promotion plan.")
    parser.add_argument("--profile", help="Limit output to one first snapshot candidate profile")
    parser.add_argument(
        "--platform",
        action="append",
        choices=DEFAULT_PLATFORMS,
        help="Platform readiness template to include; may be repeated. Defaults to both platforms.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args(argv)

    platforms = tuple(args.platform or DEFAULT_PLATFORMS)
    payload = build_first_snapshot_promotion_plan(profile=args.profile, platforms=platforms)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    return 0


__all__ = [
    "DEFAULT_PLATFORMS",
    "FIRST_SNAPSHOT_PROFILE_ORDER",
    "FIRST_SNAPSHOT_PROMOTION_PLAN_VERSION",
    "build_first_snapshot_promotion_plan",
    "main",
]
