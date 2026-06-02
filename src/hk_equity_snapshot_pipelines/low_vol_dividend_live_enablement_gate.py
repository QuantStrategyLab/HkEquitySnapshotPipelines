from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .low_vol_dividend_evidence_assembler import write_low_vol_dividend_live_enablement_evidence_assembly
from .low_vol_dividend_live_enablement_audit import build_low_vol_dividend_live_enablement_audit
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_EVIDENCE_DIR = Path("evidence/low_vol_dividend_quality")
DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_live_enablement_gate")
GATE_RUNNER_VERSION = "hk_low_vol_dividend_quality.live_enablement_gate_runner.v1"
DEFAULT_PLATFORMS = ("longbridge", "ibkr")

SHARED_CONVENTION_FILES = {
    "production_source_audit_file": "production_source_audit.draft.json",
    "artifact_pack_validation_file": "artifact_pack_validation.draft.json",
    "walk_forward_backtest_file": "walk_forward_backtest.draft.json",
}
PLATFORM_CONVENTION_FILES = {
    "platform_dry_run_file": "{platform}_live_enablement_evidence.draft.json",
    "broker_permission_file": "{platform}_broker_permission_and_fee_verification.draft.json",
    "rebalance_window_file": "{platform}_paper_or_dry_run_rebalance_window.draft.json",
    "runtime_rollout_file": "{platform}_runtime_rollout_plan.draft.json",
    "risk_approval_file": "{platform}_risk_approval.draft.json",
    "strategy_policy_evidence_file": "{platform}_strategy_policy_evidence.draft.json",
}


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


def _existing(path: Path) -> str | None:
    return str(path) if path.exists() else None


def _inventory_item(*, section: str, path: Path, platform: str | None = None) -> dict[str, Any]:
    return {
        "section": section,
        "platform": platform,
        "path": str(path),
        "exists": path.exists(),
    }


def _shared_file_paths(evidence_dir: Path) -> dict[str, Path]:
    return {
        argument_name: evidence_dir / filename
        for argument_name, filename in SHARED_CONVENTION_FILES.items()
    }


def _platform_file_paths(evidence_dir: Path, *, platform: str) -> dict[str, Path]:
    return {
        argument_name: evidence_dir / filename.format(platform=platform)
        for argument_name, filename in PLATFORM_CONVENTION_FILES.items()
    }


def _file_inventory(evidence_dir: Path, *, platforms: tuple[str, ...]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    shared_sections = {
        "production_source_audit_file": "production_snapshot_source_audit",
        "artifact_pack_validation_file": "artifact_pack_validation",
        "walk_forward_backtest_file": "walk_forward_backtest",
    }
    for argument_name, path in _shared_file_paths(evidence_dir).items():
        inventory.append(_inventory_item(section=shared_sections[argument_name], path=path))
    platform_sections = {
        "platform_dry_run_file": "platform_dry_run_order_preview",
        "broker_permission_file": "broker_permission_and_fee_verification",
        "rebalance_window_file": "paper_or_dry_run_rebalance_window",
        "runtime_rollout_file": "runtime_rollout_plan",
        "risk_approval_file": "risk_approval",
        "strategy_policy_evidence_file": "strategy_policy_evidence",
    }
    for platform in platforms:
        for argument_name, path in _platform_file_paths(evidence_dir, platform=platform).items():
            inventory.append(_inventory_item(section=platform_sections[argument_name], path=path, platform=platform))
    return inventory


def _strip_large_assembly_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in {"evidence", "validation"}}


def build_low_vol_dividend_live_enablement_gate_run(
    *,
    evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    artifact_dir: str | Path | None = None,
    validation_as_of: str | None = None,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    selected_platforms = _normalize_platforms(platforms)
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    evidence_dir = Path(evidence_dir)
    output_dir = Path(output_dir)
    assembled_dir = output_dir / "assembled"
    assembled_dir.mkdir(parents=True, exist_ok=True)

    shared_paths = _shared_file_paths(evidence_dir)
    assemblies: dict[str, dict[str, Any]] = {}
    evidence_files_for_audit: dict[str, str | None] = {}
    for platform in selected_platforms:
        platform_paths = _platform_file_paths(evidence_dir, platform=platform)
        assembly = write_low_vol_dividend_live_enablement_evidence_assembly(
            output_dir=assembled_dir,
            platform=platform,
            validation_as_of=validation_as_of,
            production_source_audit_file=_existing(shared_paths["production_source_audit_file"]),
            artifact_pack_validation_file=_existing(shared_paths["artifact_pack_validation_file"]),
            walk_forward_backtest_file=_existing(shared_paths["walk_forward_backtest_file"]),
            platform_dry_run_file=_existing(platform_paths["platform_dry_run_file"]),
            broker_permission_file=_existing(platform_paths["broker_permission_file"]),
            rebalance_window_file=_existing(platform_paths["rebalance_window_file"]),
            runtime_rollout_file=_existing(platform_paths["runtime_rollout_file"]),
            risk_approval_file=_existing(platform_paths["risk_approval_file"]),
            strategy_policy_evidence_file=_existing(platform_paths["strategy_policy_evidence_file"]),
        )
        assemblies[platform] = _strip_large_assembly_fields(assembly)
        evidence_files_for_audit[platform] = assembly["evidence_path"]

    longbridge_file = evidence_files_for_audit.get("longbridge")
    ibkr_file = evidence_files_for_audit.get("ibkr")
    audit = build_low_vol_dividend_live_enablement_audit(
        artifact_dir=artifact_dir,
        longbridge_evidence_file=longbridge_file,
        ibkr_evidence_file=ibkr_file,
        validation_as_of=validation_as_of,
    )
    missing_files = [item for item in _file_inventory(evidence_dir, platforms=selected_platforms) if not item["exists"]]
    return {
        "gate_runner_version": GATE_RUNNER_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "evidence_dir": str(evidence_dir),
        "output_dir": str(output_dir),
        "artifact_dir": str(artifact_dir) if artifact_dir is not None else None,
        "validation_as_of": audit.get("platform_live_enablement_evidence", {})
        .get(selected_platforms[0], {})
        .get("validation_as_of", validation_as_of),
        "platforms": list(selected_platforms),
        "file_inventory": _file_inventory(evidence_dir, platforms=selected_platforms),
        "missing_files": missing_files,
        "assemblies": assemblies,
        "audit": audit,
        "live_enablement_allowed": bool(audit.get("live_enablement_allowed")),
        "status": "passed" if audit.get("live_enablement_allowed") is True else "blocked",
    }


def write_low_vol_dividend_live_enablement_gate_run(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_live_enablement_gate_run(output_dir=output_dir, **kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "final_live_enablement_audit.json"
    summary_path = output_dir / "live_enablement_gate_summary.json"
    write_json(audit_path, payload["audit"])
    write_json(summary_path, {key: value for key, value in payload.items() if key != "audit"})
    return {
        **payload,
        "audit_path": str(audit_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the HK low-vol dividend live-enable evidence gate.")
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--artifact-dir")
    parser.add_argument("--validation-as-of")
    parser.add_argument(
        "--platform",
        action="append",
        choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)),
        help="Platform to assemble; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--fail-on-blocked", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=args.evidence_dir,
        output_dir=args.output_dir,
        artifact_dir=args.artifact_dir,
        validation_as_of=args.validation_as_of,
        platforms=tuple(args.platform or DEFAULT_PLATFORMS),
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"status={payload['status']}")
        print(f"live_enablement_allowed={payload['live_enablement_allowed']}")
        print(f"missing_files_count={len(payload['missing_files'])}")
        print(f"audit_path={payload['audit_path']}")
        print(f"summary_path={payload['summary_path']}")
        for blocker in payload["audit"].get("blockers", []):
            print(f"blocker={blocker}")
    if args.fail_on_blocked and payload["live_enablement_allowed"] is not True:
        return 1
    return 0


__all__ = [
    "DEFAULT_EVIDENCE_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_PLATFORMS",
    "GATE_RUNNER_VERSION",
    "PLATFORM_CONVENTION_FILES",
    "SHARED_CONVENTION_FILES",
    "build_low_vol_dividend_live_enablement_gate_run",
    "main",
    "write_low_vol_dividend_live_enablement_gate_run",
]
