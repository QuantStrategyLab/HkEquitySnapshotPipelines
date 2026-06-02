from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .live_enablement_evidence import validate_live_enablement_evidence_file
from .snapshot_artifact_validation import validate_snapshot_artifact_pack

DEFAULT_PLATFORMS = ("longbridge", "ibkr")
AUDIT_VERSION = "hk_low_vol_dividend_quality.live_enablement_audit.v1"
MIN_PRODUCTION_SNAPSHOT_ROW_COUNT = 20


def _path_status(path: str | Path | None) -> tuple[str | None, bool]:
    if path is None:
        return None, False
    resolved = Path(path)
    return str(resolved), resolved.exists()


def _error_section(error: str) -> str:
    prefix = str(error or "").split(".", 1)[0].split(" ", 1)[0].strip()
    return prefix or "unknown"


def _summarize_errors(errors: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(_error_section(error) for error in errors).items()))


def _artifact_audit(artifact_dir: str | Path | None) -> dict[str, Any]:
    path, exists = _path_status(artifact_dir)
    if not path:
        return {
            "status": "missing",
            "artifact_dir": None,
            "valid": False,
            "validation_status": "missing",
            "errors": ["artifact_dir is required"],
            "warnings": [],
            "blockers": ["artifact_pack_validation_missing"],
        }
    if not exists:
        return {
            "status": "missing",
            "artifact_dir": path,
            "valid": False,
            "validation_status": "missing",
            "errors": [f"artifact_dir does not exist: {path}"],
            "warnings": [],
            "blockers": ["artifact_pack_validation_missing"],
        }
    validation = validate_snapshot_artifact_pack(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, path)
    errors = list(validation.get("errors") or [])
    warnings = list(validation.get("warnings") or [])
    snapshot_row_count = int(validation.get("snapshot_row_count") or 0)
    if validation.get("valid") is True and snapshot_row_count < MIN_PRODUCTION_SNAPSHOT_ROW_COUNT:
        errors.append(
            "snapshot_row_count below production threshold: "
            f"got {snapshot_row_count}, min={MIN_PRODUCTION_SNAPSHOT_ROW_COUNT}"
        )
    blockers = [] if validation.get("valid") is True and not errors else ["artifact_pack_validation_failed"]
    return {
        "status": "passed" if validation.get("valid") is True and not errors else "failed",
        "artifact_dir": path,
        "valid": bool(validation.get("valid") and not errors),
        "validation_status": validation.get("validation_status"),
        "min_production_snapshot_row_count": MIN_PRODUCTION_SNAPSHOT_ROW_COUNT,
        "snapshot_row_count": validation.get("snapshot_row_count"),
        "ranking_row_count": validation.get("ranking_row_count"),
        "snapshot_sha256": validation.get("snapshot_sha256"),
        "manifest_snapshot_as_of": validation.get("manifest_snapshot_as_of"),
        "release_snapshot_as_of": validation.get("release_snapshot_as_of"),
        "errors": errors,
        "warnings": warnings,
        "error_sections": _summarize_errors(errors),
        "blockers": blockers,
    }


def _platform_audit(
    platform: str,
    *,
    evidence_file: str | Path | None,
    validation_as_of: str | None,
) -> dict[str, Any]:
    path, exists = _path_status(evidence_file)
    if not path:
        return {
            "platform": platform,
            "status": "missing",
            "evidence_file": None,
            "validation_status": "missing",
            "live_enablement_allowed": False,
            "errors": [f"{platform} evidence_file is required"],
            "warnings": [],
            "error_sections": {platform: 1},
            "blockers": [f"{platform}_live_enablement_evidence_missing"],
        }
    if not exists:
        return {
            "platform": platform,
            "status": "missing",
            "evidence_file": path,
            "validation_status": "missing",
            "live_enablement_allowed": False,
            "errors": [f"{platform} evidence_file does not exist: {path}"],
            "warnings": [],
            "error_sections": {platform: 1},
            "blockers": [f"{platform}_live_enablement_evidence_missing"],
        }
    validation = validate_live_enablement_evidence_file(path, validation_as_of=validation_as_of)
    errors = list(validation.get("errors") or [])
    warnings = list(validation.get("warnings") or [])
    allowed = validation.get("live_enablement_allowed") is True
    return {
        "platform": platform,
        "status": "passed" if allowed else "failed",
        "evidence_file": path,
        "validation_status": validation.get("validation_status"),
        "live_enablement_allowed": allowed,
        "validation_as_of": validation.get("validation_as_of"),
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "errors": errors[:50],
        "warnings": warnings[:50],
        "error_sections": _summarize_errors(errors),
        "blockers": [] if allowed else [f"{platform}_live_enablement_evidence_failed"],
    }


def build_low_vol_dividend_live_enablement_audit(
    *,
    artifact_dir: str | Path | None = None,
    longbridge_evidence_file: str | Path | None = None,
    ibkr_evidence_file: str | Path | None = None,
    validation_as_of: str | None = None,
) -> dict[str, Any]:
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    artifact = _artifact_audit(artifact_dir)
    evidence_files = {
        "longbridge": longbridge_evidence_file,
        "ibkr": ibkr_evidence_file,
    }
    platforms = {
        platform: _platform_audit(platform, evidence_file=evidence_files[platform], validation_as_of=validation_as_of)
        for platform in DEFAULT_PLATFORMS
    }
    blockers = [*artifact["blockers"]]
    for platform_result in platforms.values():
        blockers.extend(platform_result["blockers"])
    live_allowed = artifact["valid"] is True and all(
        platform_result["live_enablement_allowed"] is True for platform_result in platforms.values()
    )
    status = "passed" if live_allowed else "blocked"
    gates = {
        "artifact_pack_validation": artifact["status"],
        **{f"{platform}_live_enablement_evidence": result["status"] for platform, result in platforms.items()},
    }
    next_actions: list[str] = []
    if artifact["status"] != "passed":
        next_actions.append("Provide a non-sample production artifact directory and pass hkeq-validate-snapshot-artifact-pack.")
    for platform, result in platforms.items():
        if result["status"] == "missing":
            next_actions.append(f"Create {platform} live-enable evidence from the platform dry-run preview and validate it.")
        elif result["status"] == "failed":
            sections = ", ".join(result["error_sections"].keys())
            next_actions.append(f"Fix {platform} evidence sections: {sections}.")
    return {
        "audit_version": AUDIT_VERSION,
        "profile": contract.profile,
        "display_name": contract.display_name,
        "contract_version": contract.contract_version,
        "status": status,
        "runtime_enabled": live_allowed,
        "live_enablement_allowed": live_allowed,
        "production_deployment_allowed": live_allowed,
        "gates": gates,
        "blockers": blockers,
        "artifact_pack_validation": artifact,
        "platform_live_enablement_evidence": platforms,
        "next_actions": next_actions,
        "stop_conditions": [
            "Do not enable live trading while any gate is missing or failed.",
            "Do not use sample artifacts or synthetic data as production evidence.",
            "Do not remove dry-run controls until both platform evidence files pass validation.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit HK low-vol dividend true live-enable readiness.")
    parser.add_argument("--artifact-dir", help="Production artifact directory to validate.")
    parser.add_argument("--longbridge-evidence-file", help="LongBridge live-enable evidence JSON.")
    parser.add_argument("--ibkr-evidence-file", help="IBKR live-enable evidence JSON.")
    parser.add_argument("--validation-as-of", help="Override validation date for evidence freshness checks.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args(argv)

    payload = build_low_vol_dividend_live_enablement_audit(
        artifact_dir=args.artifact_dir,
        longbridge_evidence_file=args.longbridge_evidence_file,
        ibkr_evidence_file=args.ibkr_evidence_file,
        validation_as_of=args.validation_as_of,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"status={payload['status']}")
        print(f"live_enablement_allowed={payload['live_enablement_allowed']}")
        for gate, status in payload["gates"].items():
            print(f"gate={gate} status={status}")
        for blocker in payload["blockers"]:
            print(f"blocker={blocker}")
    return 0 if payload["live_enablement_allowed"] else 1


__all__ = [
    "AUDIT_VERSION",
    "DEFAULT_PLATFORMS",
    "MIN_PRODUCTION_SNAPSHOT_ROW_COUNT",
    "build_low_vol_dividend_live_enablement_audit",
    "main",
]
