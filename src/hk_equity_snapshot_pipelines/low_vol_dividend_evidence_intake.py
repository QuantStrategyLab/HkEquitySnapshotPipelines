from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .artifacts import sha256_file, write_json
from .low_vol_dividend_live_enablement_gate import (
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_PLATFORMS,
    PLATFORM_CONVENTION_FILES,
    SHARED_CONVENTION_FILES,
    build_low_vol_dividend_live_enablement_gate_run,
)
from .snapshot_readiness import SUPPORTED_SNAPSHOT_PLATFORMS

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_live_enablement_evidence_intake")
INTAKE_VERSION = "hk_low_vol_dividend_quality.live_enablement_evidence_intake.v1"


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


def _source_dirs(paths: tuple[str | Path, ...]) -> tuple[Path, ...]:
    resolved = tuple(Path(path) for path in paths)
    if not resolved:
        raise ValueError("At least one source directory is required")
    missing = [str(path) for path in resolved if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Evidence source directories do not exist: {', '.join(missing)}")
    not_dirs = [str(path) for path in resolved if not path.is_dir()]
    if not_dirs:
        raise NotADirectoryError(f"Evidence sources must be directories: {', '.join(not_dirs)}")
    return resolved


def _target_files(evidence_dir: Path, *, platforms: tuple[str, ...]) -> dict[str, Path]:
    targets = {
        filename: evidence_dir / filename
        for filename in SHARED_CONVENTION_FILES.values()
    }
    for platform in platforms:
        for filename_template in PLATFORM_CONVENTION_FILES.values():
            filename = filename_template.format(platform=platform)
            targets[filename] = evidence_dir / filename
    return targets


def _find_source_file(source_dirs: tuple[Path, ...], filename: str) -> Path | None:
    matches: list[Path] = []
    for source_dir in source_dirs:
        direct = source_dir / filename
        if direct.exists() and direct.is_file():
            matches.append(direct)
        matches.extend(path for path in source_dir.rglob(filename) if path.is_file())
    unique_matches = sorted({path.resolve() for path in matches}, key=lambda path: str(path))
    return Path(unique_matches[0]) if unique_matches else None


def _stage_item(
    *,
    filename: str,
    source: Path | None,
    target: Path,
    apply: bool,
    overwrite: bool,
) -> dict[str, Any]:
    if source is None:
        return {
            "filename": filename,
            "source_path": None,
            "target_path": str(target),
            "source_found": False,
            "target_exists_before": target.exists(),
            "action": "missing_source",
        }
    target_exists_before = target.exists()
    source_sha256 = sha256_file(source)
    target_sha256_before = sha256_file(target) if target.exists() else ""
    if target.exists() and not overwrite:
        action = "skipped_existing"
    elif not apply:
        action = "would_copy"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        action = "copied"
    return {
        "filename": filename,
        "source_path": str(source),
        "target_path": str(target),
        "source_found": True,
        "target_exists_before": target_exists_before,
        "source_sha256": source_sha256,
        "target_sha256_before": target_sha256_before,
        "target_sha256_after": sha256_file(target) if target.exists() else "",
        "action": action,
    }


def build_low_vol_dividend_live_enablement_evidence_intake(
    *,
    source_dirs: tuple[str | Path, ...],
    evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    artifact_dir: str | Path | None = None,
    validation_as_of: str | None = None,
    platforms: tuple[str, ...] = DEFAULT_PLATFORMS,
    apply: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    selected_platforms = _normalize_platforms(platforms)
    resolved_source_dirs = _source_dirs(source_dirs)
    evidence_dir = Path(evidence_dir)
    output_dir = Path(output_dir)
    target_files = _target_files(evidence_dir, platforms=selected_platforms)
    staged_files = [
        _stage_item(
            filename=filename,
            source=_find_source_file(resolved_source_dirs, filename),
            target=target,
            apply=apply,
            overwrite=overwrite,
        )
        for filename, target in sorted(target_files.items())
    ]
    gate = build_low_vol_dividend_live_enablement_gate_run(
        evidence_dir=evidence_dir,
        output_dir=output_dir / "gate",
        artifact_dir=artifact_dir,
        validation_as_of=validation_as_of,
        platforms=selected_platforms,
    )
    return {
        "intake_version": INTAKE_VERSION,
        "source_dirs": [str(path) for path in resolved_source_dirs],
        "evidence_dir": str(evidence_dir),
        "output_dir": str(output_dir),
        "artifact_dir": str(artifact_dir) if artifact_dir is not None else None,
        "validation_as_of": validation_as_of,
        "platforms": list(selected_platforms),
        "apply": bool(apply),
        "overwrite": bool(overwrite),
        "staged_files": staged_files,
        "copied_count": sum(1 for item in staged_files if item["action"] == "copied"),
        "would_copy_count": sum(1 for item in staged_files if item["action"] == "would_copy"),
        "missing_source_count": sum(1 for item in staged_files if item["action"] == "missing_source"),
        "skipped_existing_count": sum(1 for item in staged_files if item["action"] == "skipped_existing"),
        "gate_status": gate["status"],
        "gate_live_enablement_allowed": bool(gate["live_enablement_allowed"]),
        "gate_missing_files_count": len(gate["missing_files"]),
        "gate_blockers": list(gate.get("audit", {}).get("blockers") or []),
        "gate_summary": {key: value for key, value in gate.items() if key not in {"audit", "assemblies"}},
    }


def write_low_vol_dividend_live_enablement_evidence_intake(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_live_enablement_evidence_intake(output_dir=output_dir, **kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "live_enablement_evidence_intake_summary.json"
    write_json(summary_path, payload)
    return {
        **payload,
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage HK low-vol dividend live-enable evidence into the gate convention directory.")
    parser.add_argument(
        "--source-dir",
        action="append",
        required=True,
        help="Directory containing convention-named evidence files; may be repeated.",
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--artifact-dir")
    parser.add_argument("--validation-as-of")
    parser.add_argument(
        "--platform",
        action="append",
        choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)),
        help="Platform to stage; may be repeated. Defaults to LongBridge and IBKR.",
    )
    parser.add_argument("--apply", action="store_true", help="Copy matching evidence files into the convention directory.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing convention files when used with --apply.")
    parser.add_argument("--fail-on-blocked", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_live_enablement_evidence_intake(
        output_dir=args.output_dir,
        source_dirs=tuple(args.source_dir),
        evidence_dir=args.evidence_dir,
        artifact_dir=args.artifact_dir,
        validation_as_of=args.validation_as_of,
        platforms=tuple(args.platform or DEFAULT_PLATFORMS),
        apply=args.apply,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        mode = "apply" if payload["apply"] else "preview"
        print(f"mode={mode}")
        print(f"copied_count={payload['copied_count']}")
        print(f"would_copy_count={payload['would_copy_count']}")
        print(f"missing_source_count={payload['missing_source_count']}")
        print(f"skipped_existing_count={payload['skipped_existing_count']}")
        print(f"gate_status={payload['gate_status']}")
        print(f"gate_live_enablement_allowed={payload['gate_live_enablement_allowed']}")
        print(f"summary_path={payload['summary_path']}")
    if args.fail_on_blocked and payload["gate_live_enablement_allowed"] is not True:
        return 1
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "INTAKE_VERSION",
    "build_low_vol_dividend_live_enablement_evidence_intake",
    "main",
    "write_low_vol_dividend_live_enablement_evidence_intake",
]
