from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .low_vol_dividend_live_enablement_gate import (
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_OUTPUT_DIR as DEFAULT_GATE_OUTPUT_DIR,
    DEFAULT_PLATFORMS,
    build_low_vol_dividend_live_enablement_gate_run,
)
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_live_enablement_readiness")
READINESS_VERSION = "hk_low_vol_dividend_quality.live_enablement_readiness.v1"


def _blocker_lookup(gate: dict[str, Any]) -> dict[tuple[str, str | None], dict[str, Any]]:
    lookup: dict[tuple[str, str | None], dict[str, Any]] = {}
    for blocker in gate.get("external_evidence_blockers") or []:
        if not isinstance(blocker, dict):
            continue
        lookup[(str(blocker.get("section") or ""), blocker.get("platform"))] = blocker
    return lookup


def _required_file_statuses(gate: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = _blocker_lookup(gate)
    statuses: list[dict[str, Any]] = []
    for item in gate.get("file_inventory") or []:
        if not isinstance(item, dict):
            continue
        key = (str(item.get("section") or ""), item.get("platform"))
        blocker = blockers.get(key, {})
        exists = bool(item.get("exists"))
        statuses.append(
            {
                "section": item.get("section"),
                "platform": item.get("platform"),
                "path": item.get("path"),
                "status": "present" if exists else "missing",
                "external_dependency": blocker.get("external_dependency", ""),
                "suggested_command": blocker.get("suggested_command", ""),
            }
        )
    return statuses


def _platform_readiness(gate: dict[str, Any]) -> list[dict[str, Any]]:
    readiness: list[dict[str, Any]] = []
    assemblies = gate.get("assemblies") if isinstance(gate.get("assemblies"), dict) else {}
    for platform in sorted(assemblies):
        assembly = assemblies[platform]
        if not isinstance(assembly, dict):
            continue
        readiness.append(
            {
                "platform": platform,
                "validation_status": assembly.get("validation_status"),
                "live_enablement_allowed": bool(assembly.get("live_enablement_allowed")),
                "provided_sections": list(assembly.get("provided_sections") or []),
                "missing_section_sources": list(assembly.get("missing_section_sources") or []),
                "validation_errors_count": int(assembly.get("validation_errors_count") or 0),
                "validation_errors_preview": list(assembly.get("validation_errors_preview") or [])[:20],
                "evidence_path": assembly.get("evidence_path"),
                "summary_path": assembly.get("summary_path"),
            }
        )
    return readiness


def build_low_vol_dividend_live_enablement_readiness_report(
    *,
    evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    gate_output_dir: str | Path = DEFAULT_GATE_OUTPUT_DIR,
    artifact_dir: str | Path | None = None,
    validation_as_of: str | None = None,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    gate = build_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=evidence_dir,
        output_dir=gate_output_dir,
        artifact_dir=artifact_dir,
        validation_as_of=validation_as_of,
        platforms=platforms,
    )
    required_files = _required_file_statuses(gate)
    platform_readiness = _platform_readiness(gate)
    missing_required_files = [item for item in required_files if item["status"] == "missing"]
    return {
        "readiness_version": READINESS_VERSION,
        "profile": gate["profile"],
        "contract_version": gate["contract_version"],
        "evidence_dir": gate["evidence_dir"],
        "output_dir": str(output_dir),
        "gate_output_dir": str(gate_output_dir),
        "artifact_dir": gate.get("artifact_dir"),
        "validation_as_of": gate.get("validation_as_of"),
        "platforms": list(gate.get("platforms") or []),
        "status": gate["status"],
        "live_enablement_allowed": bool(gate["live_enablement_allowed"]),
        "missing_required_files_count": len(missing_required_files),
        "provided_required_files_count": len(required_files) - len(missing_required_files),
        "required_files": required_files,
        "platform_readiness": platform_readiness,
        "blockers": list(gate.get("audit", {}).get("blockers") or []),
        "next_evidence_commands": list(gate.get("next_evidence_commands") or []),
        "ready_to_request_live_enable": bool(
            gate["live_enablement_allowed"] is True
            and not missing_required_files
            and all(platform.get("live_enablement_allowed") for platform in platform_readiness)
        ),
    }


def write_low_vol_dividend_live_enablement_readiness_report(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_live_enablement_readiness_report(output_dir=output_dir, **kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "live_enablement_readiness_report.json"
    write_json(report_path, payload)
    return {
        **payload,
        "report_path": str(report_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print HK low-vol dividend live-enable evidence readiness.")
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--gate-output-dir", default=str(DEFAULT_GATE_OUTPUT_DIR))
    parser.add_argument("--artifact-dir")
    parser.add_argument("--validation-as-of")
    parser.add_argument(
        "--platform",
        action="append",
        choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)),
        help="Platform to inspect; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--fail-on-blocked", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_live_enablement_readiness_report(
        output_dir=args.output_dir,
        evidence_dir=args.evidence_dir,
        gate_output_dir=args.gate_output_dir,
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
        print(f"missing_required_files_count={payload['missing_required_files_count']}")
        print(f"ready_to_request_live_enable={payload['ready_to_request_live_enable']}")
        print(f"report_path={payload['report_path']}")
        for blocker in payload["blockers"]:
            print(f"blocker={blocker}")
    if args.fail_on_blocked and payload["live_enablement_allowed"] is not True:
        return 1
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "READINESS_VERSION",
    "build_low_vol_dividend_live_enablement_readiness_report",
    "main",
    "write_low_vol_dividend_live_enablement_readiness_report",
]
