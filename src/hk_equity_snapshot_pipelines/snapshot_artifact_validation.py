from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .artifacts import sha256_file
from .contracts import SOURCE_PROJECT, SnapshotProfileContract, get_profile_contract


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_equal(errors: list[str], field: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{field} mismatch: expected {expected!r}, got {actual!r}")


def _check_artifact_files(contract: SnapshotProfileContract, artifact_dir: str | Path) -> tuple[dict[str, Path], list[str]]:
    paths = contract.artifact_paths(artifact_dir)
    errors = [f"missing {name} artifact: {path}" for name, path in paths.items() if not path.exists()]
    return paths, errors


def validate_snapshot_artifact_pack(profile: str, artifact_dir: str | Path) -> dict[str, Any]:
    contract = get_profile_contract(profile)
    paths, errors = _check_artifact_files(contract, artifact_dir)
    warnings: list[str] = []
    checked_files = {name: str(path) for name, path in paths.items()}
    result: dict[str, Any] = {
        "profile": contract.profile,
        "display_name": contract.display_name,
        "contract_version": contract.contract_version,
        "artifact_dir": str(Path(artifact_dir)),
        "checked_files": checked_files,
        "validation_status": "failed",
        "valid": False,
        "errors": errors,
        "warnings": warnings,
    }
    if errors:
        return result

    snapshot = pd.read_csv(paths["snapshot"])
    ranking = pd.read_csv(paths["ranking"])
    manifest = _read_json(paths["manifest"])
    release_summary = _read_json(paths["release_summary"])
    snapshot_sha256 = sha256_file(paths["snapshot"])

    _check_equal(errors, "manifest.strategy_profile", manifest.get("strategy_profile"), contract.profile)
    _check_equal(errors, "manifest.contract_version", manifest.get("contract_version"), contract.contract_version)
    _check_equal(errors, "manifest.source_project", manifest.get("source_project"), SOURCE_PROJECT)
    _check_equal(errors, "manifest.snapshot_sha256", manifest.get("snapshot_sha256"), snapshot_sha256)
    _check_equal(errors, "manifest.row_count", manifest.get("row_count"), int(len(snapshot)))

    manifest_snapshot_path = manifest.get("snapshot_path")
    if manifest_snapshot_path and Path(str(manifest_snapshot_path)).name != paths["snapshot"].name:
        warnings.append(
            "manifest.snapshot_path basename differs from contract snapshot filename: "
            f"{manifest_snapshot_path!r}"
        )

    _check_equal(errors, "release_summary.strategy_profile", release_summary.get("strategy_profile"), contract.profile)
    _check_equal(errors, "release_summary.contract_version", release_summary.get("contract_version"), contract.contract_version)
    _check_equal(errors, "release_summary.release_status", release_summary.get("release_status"), "ready")
    _check_equal(errors, "release_summary.row_count", release_summary.get("row_count"), int(len(snapshot)))

    diagnostics = release_summary.get("diagnostics")
    if isinstance(diagnostics, dict):
        _check_equal(
            errors,
            "release_summary.diagnostics.snapshot_contract_version",
            diagnostics.get("snapshot_contract_version"),
            contract.contract_version,
        )
    else:
        warnings.append("release_summary.diagnostics is missing or not an object")

    if snapshot.empty:
        errors.append("snapshot CSV is empty")
    if ranking.empty:
        warnings.append("ranking CSV is empty; this may be valid only for defensive/no-candidate releases")

    result.update(
        {
            "snapshot_row_count": int(len(snapshot)),
            "ranking_row_count": int(len(ranking)),
            "snapshot_sha256": snapshot_sha256,
            "manifest_snapshot_as_of": manifest.get("snapshot_as_of"),
            "release_snapshot_as_of": release_summary.get("snapshot_as_of"),
        }
    )
    if not errors:
        result["validation_status"] = "passed"
        result["valid"] = True
    result["errors"] = errors
    result["warnings"] = warnings
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an HK snapshot artifact pack against its contract.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args(argv)

    payload = validate_snapshot_artifact_pack(args.profile, args.artifact_dir)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"contract_version={payload['contract_version']}")
        print(f"validation_status={payload['validation_status']}")
        for error in payload["errors"]:
            print(f"error={error}")
        for warning in payload["warnings"]:
            print(f"warning={warning}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
