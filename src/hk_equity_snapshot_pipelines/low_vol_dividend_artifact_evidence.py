from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE, get_profile_contract
from .live_enablement_evidence import build_live_enablement_evidence_template, validate_live_enablement_evidence
from .snapshot_artifact_validation import validate_snapshot_artifact_pack

DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_artifact_evidence")
DRAFT_VERSION = "hk_low_vol_dividend_quality.artifact_evidence_draft.v1"
MUTABLE_RELEASE_IDS = {"latest", "sample", "dev", "test"}


def _stable(value: str | None) -> str:
    return str(value or "").strip()


def _artifact_section_can_pass(
    *,
    validation: dict[str, Any],
    artifact_release_id: str,
    published_snapshot_uri: str,
    published_manifest_uri: str,
    published_ranking_uri: str,
    published_release_summary_uri: str,
    evidence_uri: str,
    confirm_immutable_release: bool,
    confirm_published_artifacts_not_sample: bool,
    confirm_manifest_provenance: bool,
    confirm_release_summary_ready: bool,
) -> bool:
    normalized_release_id = artifact_release_id.strip().lower()
    return all(
        (
            validation.get("valid") is True,
            bool(artifact_release_id.strip()),
            normalized_release_id not in MUTABLE_RELEASE_IDS,
            bool(published_snapshot_uri.strip()),
            bool(published_manifest_uri.strip()),
            bool(published_ranking_uri.strip()),
            bool(published_release_summary_uri.strip()),
            bool(evidence_uri.strip()),
            confirm_immutable_release,
            confirm_published_artifacts_not_sample,
            confirm_manifest_provenance,
            confirm_release_summary_ready,
        )
    )


def build_low_vol_dividend_artifact_evidence_draft(
    *,
    artifact_dir: str | Path,
    evidence_generated_at: str,
    evidence_uri: str = "",
    artifact_release_id: str = "",
    published_snapshot_uri: str = "",
    published_manifest_uri: str = "",
    published_ranking_uri: str = "",
    published_release_summary_uri: str = "",
    confirm_immutable_release: bool = False,
    confirm_published_artifacts_not_sample: bool = False,
    confirm_manifest_provenance: bool = False,
    confirm_release_summary_ready: bool = False,
) -> dict[str, Any]:
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE)
    validation = validate_snapshot_artifact_pack(contract.profile, artifact_dir)
    local_valid = validation.get("valid") is True
    release_id = _stable(artifact_release_id)
    snapshot_uri = _stable(published_snapshot_uri)
    manifest_uri = _stable(published_manifest_uri)
    ranking_uri = _stable(published_ranking_uri)
    release_summary_uri = _stable(published_release_summary_uri)
    section_can_pass = _artifact_section_can_pass(
        validation=validation,
        artifact_release_id=release_id,
        published_snapshot_uri=snapshot_uri,
        published_manifest_uri=manifest_uri,
        published_ranking_uri=ranking_uri,
        published_release_summary_uri=release_summary_uri,
        evidence_uri=evidence_uri,
        confirm_immutable_release=confirm_immutable_release,
        confirm_published_artifacts_not_sample=confirm_published_artifacts_not_sample,
        confirm_manifest_provenance=confirm_manifest_provenance,
        confirm_release_summary_ready=confirm_release_summary_ready,
    )
    section = {
        "valid": bool(section_can_pass),
        "validation_status": "passed" if local_valid else "failed",
        "profile": contract.profile,
        "artifact_dir": str(Path(artifact_dir)),
        "validator_command": (
            "hkeq-validate-snapshot-artifact-pack "
            f"--profile {contract.profile} --artifact-dir {Path(artifact_dir)} --json"
        ),
        "artifact_release_id": release_id,
        "contract_version": contract.contract_version,
        "snapshot_sha256": validation.get("snapshot_sha256") or "",
        "row_count": validation.get("snapshot_row_count"),
        "published_snapshot_uri": snapshot_uri,
        "published_manifest_uri": manifest_uri,
        "published_ranking_uri": ranking_uri,
        "published_release_summary_uri": release_summary_uri,
        "immutable_release_id": bool(confirm_immutable_release),
        "published_artifacts_not_sample": bool(confirm_published_artifacts_not_sample),
        "manifest_snapshot_sha256_verified": bool(confirm_manifest_provenance),
        "manifest_row_count_verified": bool(confirm_manifest_provenance),
        "release_summary_ready": bool(confirm_release_summary_ready),
        "evidence_generated_at": evidence_generated_at,
        "evidence_uri": _stable(evidence_uri),
        "local_artifact_validation": validation,
    }
    template = build_live_enablement_evidence_template(contract.profile, platform="longbridge")
    template["validation_as_of"] = evidence_generated_at
    template["artifact_pack_validation"] = section
    validation_after_merge = validate_live_enablement_evidence(template, validation_as_of=evidence_generated_at)
    artifact_errors = [
        error
        for error in validation_after_merge.get("errors", [])
        if str(error).startswith("artifact_pack_validation.")
    ]
    return {
        "draft_version": DRAFT_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "artifact_dir": str(Path(artifact_dir)),
        "local_artifact_valid": local_valid,
        "artifact_section_status": "passed" if section_can_pass else "pending",
        "artifact_section_can_pass": section_can_pass,
        "artifact_section_errors_preview": artifact_errors[:30],
        "live_enablement_allowed": False,
        "validation_status_after_merge": validation_after_merge.get("validation_status"),
        "validation_errors_count_after_merge": len(validation_after_merge.get("errors") or []),
        "artifact_pack_validation_draft": section,
    }


def write_low_vol_dividend_artifact_evidence_draft(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_low_vol_dividend_artifact_evidence_draft(**kwargs)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    draft_path = output_dir / "artifact_pack_validation.draft.json"
    summary_path = output_dir / "artifact_pack_validation_draft_summary.json"
    write_json(draft_path, payload["artifact_pack_validation_draft"])
    write_json(summary_path, {key: value for key, value in payload.items() if key != "artifact_pack_validation_draft"})
    return {
        **payload,
        "draft_path": str(draft_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft HK low-vol dividend artifact-pack evidence.")
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--artifact-release-id", default="")
    parser.add_argument("--published-snapshot-uri", default="")
    parser.add_argument("--published-manifest-uri", default="")
    parser.add_argument("--published-ranking-uri", default="")
    parser.add_argument("--published-release-summary-uri", default="")
    parser.add_argument("--evidence-uri", default="")
    parser.add_argument("--evidence-generated-at", required=True)
    parser.add_argument("--confirm-immutable-release", action="store_true")
    parser.add_argument("--confirm-published-artifacts-not-sample", action="store_true")
    parser.add_argument("--confirm-manifest-provenance", action="store_true")
    parser.add_argument("--confirm-release-summary-ready", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = write_low_vol_dividend_artifact_evidence_draft(
        output_dir=args.output_dir,
        artifact_dir=args.artifact_dir,
        artifact_release_id=args.artifact_release_id,
        published_snapshot_uri=args.published_snapshot_uri,
        published_manifest_uri=args.published_manifest_uri,
        published_ranking_uri=args.published_ranking_uri,
        published_release_summary_uri=args.published_release_summary_uri,
        evidence_uri=args.evidence_uri,
        evidence_generated_at=args.evidence_generated_at,
        confirm_immutable_release=args.confirm_immutable_release,
        confirm_published_artifacts_not_sample=args.confirm_published_artifacts_not_sample,
        confirm_manifest_provenance=args.confirm_manifest_provenance,
        confirm_release_summary_ready=args.confirm_release_summary_ready,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"profile={payload['profile']}")
        print(f"local_artifact_valid={payload['local_artifact_valid']}")
        print(f"artifact_section_status={payload['artifact_section_status']}")
        print(f"draft_path={payload['draft_path']}")
        print(f"summary_path={payload['summary_path']}")
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DRAFT_VERSION",
    "build_low_vol_dividend_artifact_evidence_draft",
    "main",
    "write_low_vol_dividend_artifact_evidence_draft",
]
