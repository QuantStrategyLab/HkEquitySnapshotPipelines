from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .artifacts import resolve_snapshot_as_of
from .contracts import get_profile_contract
from .published_snapshot_health import verify_published_snapshot
from .snapshot_artifact_validation import validate_snapshot_artifact_pack

VALIDATION_REPORT_FILENAME = "artifact_pack_validation.json"
SOURCE_INPUT_SUMMARY_FILENAME = "source_input_summary.json"
MAX_SNAPSHOT_AGE_DAYS = 40


@dataclass(frozen=True)
class PublishItem:
    source: Path
    destination: str


def build_publish_plan(*, profile: str, artifact_dir: str | Path, gcs_prefix: str) -> tuple[PublishItem, ...]:
    contract = get_profile_contract(profile)
    paths = contract.artifact_paths(artifact_dir)
    normalized_prefix = str(gcs_prefix).rstrip("/")
    sources = [
        paths["snapshot"],
        paths["manifest"],
        paths["ranking"],
        paths["release_summary"],
    ]
    validation_report = Path(artifact_dir) / VALIDATION_REPORT_FILENAME
    if validation_report.exists():
        sources.append(validation_report)
    source_input_summary = Path(artifact_dir) / SOURCE_INPUT_SUMMARY_FILENAME
    if source_input_summary.exists():
        sources.append(source_input_summary)
    return tuple(PublishItem(source=path, destination=f"{normalized_prefix}/{path.name}") for path in sources)


def validate_publish_plan(*, profile: str, plan: tuple[PublishItem, ...], today: date) -> dict[str, Any]:
    """Reuse pack and health validation against the bytes about to be uploaded."""
    if not plan:
        raise ValueError("publish plan is empty")
    artifact_dir = plan[0].source.parent
    paths = get_profile_contract(profile).artifact_paths(artifact_dir)
    destinations = {item.source: item.destination for item in plan}
    errors = [f"missing {name} artifact in publish plan" for name, path in paths.items() if path not in destinations]
    try:
        validation = validate_snapshot_artifact_pack(profile, artifact_dir)
        errors.extend(validation["errors"])
    except (OSError, ValueError) as exc:
        validation = {"valid": False, "errors": [str(exc)]}
        errors.extend(validation["errors"])
    objects = {item.destination: item.source for item in plan}
    health = verify_published_snapshot(
        profile=profile,
        snapshot_uri=destinations.get(paths["snapshot"], ""),
        manifest_uri=destinations.get(paths["manifest"], ""),
        max_age_days=MAX_SNAPSHOT_AGE_DAYS,
        fetch_bytes=lambda uri: objects[uri].read_bytes(),
        today=today,
    )
    errors.extend(health["errors"])
    if validation.get("valid"):
        snapshot = pd.read_csv(paths["snapshot"])
        snapshot_as_of = resolve_snapshot_as_of(snapshot)
        if validation.get("manifest_snapshot_as_of") != snapshot_as_of:
            errors.append("manifest.snapshot_as_of does not match snapshot CSV dates")
        if validation.get("release_snapshot_as_of") != snapshot_as_of:
            errors.append("release_summary.snapshot_as_of does not match snapshot CSV dates")
        for column in ("source_quality", "artifact_evidence_role"):
            if column in snapshot:
                labels = snapshot[column].fillna("").astype(str)
                if labels.str.contains("research_defaults|research_smoke", case=False, regex=True).any():
                    errors.append(f"snapshot.{column} identifies research-only input")
    summary_path = artifact_dir / SOURCE_INPUT_SUMMARY_FILENAME
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if not isinstance(summary, dict):
                errors.append("source_input_summary must be a JSON object")
            else:
                if summary.get("allow_research_defaults", False) is not False:
                    errors.append("source_input_summary.allow_research_defaults must be false")
                for field in ("source_quality", "artifact_evidence_role"):
                    label = str(summary.get(field, "")).lower()
                    if "research_defaults" in label or "research_smoke" in label:
                        errors.append(f"source_input_summary.{field} identifies research-only input")
        except (OSError, ValueError) as exc:
            errors.append(f"source_input_summary could not be read: {exc}")
    return {
        "status": "verified" if not errors else "failed",
        "checked_at": today.isoformat(),
        "snapshot_source": str(paths["snapshot"]),
        "artifact_pack_validation": validation,
        "published_snapshot_health": health,
        "errors": errors,
        "boundary": "Preflight checks local artifact bytes; it does not attest source lineage, authorize trading, or enable a runtime.",
    }


def publish_artifacts(
    plan: tuple[PublishItem, ...], *, dry_run: bool, profile: str | None = None,
    preflight_report: Path | None = None,
) -> None:
    if not dry_run or preflight_report is not None:
        if profile is None:
            raise ValueError("profile is required for publish preflight")
        receipt = validate_publish_plan(profile=profile, plan=plan, today=datetime.now(timezone.utc).date())
        if preflight_report is not None:
            preflight_report.parent.mkdir(parents=True, exist_ok=True)
            preflight_report.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if receipt["status"] != "verified":
            raise ValueError("publish preflight failed: " + "; ".join(receipt["errors"]))
    # Check the complete plan before the first transfer, including optional reports.
    for item in plan:
        if not item.source.is_file():
            raise FileNotFoundError(f"artifact not found: {item.source}")
    for item in plan:
        command = ["gcloud", "storage", "cp", str(item.source), item.destination]
        if dry_run:
            print("DRY-RUN " + " ".join(command))
            continue
        subprocess.run(command, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish HK equity snapshot artifacts to GCS.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--gcs-prefix", required=True)
    parser.add_argument("--execute", action="store_true", help="Actually run gcloud storage cp. Default is dry-run.")
    parser.add_argument(
        "--preflight-report", type=Path,
        help="Validate local upload bytes and save a receipt, including for a dry-run plan.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_publish_plan(profile=args.profile, artifact_dir=args.artifact_dir, gcs_prefix=args.gcs_prefix)
    try:
        publish_artifacts(
            plan, dry_run=not args.execute, profile=args.profile, preflight_report=args.preflight_report,
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
