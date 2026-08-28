from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .contracts import SOURCE_PROJECT, get_profile_contract


BytesFetcher = Callable[[str], bytes]


def _read_gcs(uri: str) -> bytes:
    completed = subprocess.run(
        ["gcloud", "storage", "cat", uri],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"gcloud storage cat exited {completed.returncode}")
    return completed.stdout


def _parse_snapshot_as_of(value: object) -> dt.date:
    if not isinstance(value, str):
        raise ValueError("manifest.snapshot_as_of must be an ISO date string")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("manifest.snapshot_as_of must be an ISO date string") from exc


def verify_published_snapshot(
    *,
    profile: str,
    snapshot_uri: str,
    manifest_uri: str,
    max_age_days: int,
    fetch_bytes: BytesFetcher,
    today: dt.date,
) -> dict[str, Any]:
    """Read and verify one published snapshot without changing remote state."""
    contract = get_profile_contract(profile)
    result: dict[str, Any] = {
        "profile": contract.profile,
        "snapshot_uri": snapshot_uri,
        "manifest_uri": manifest_uri,
        "max_age_days": max_age_days,
        "status": "failed",
        "errors": [],
    }
    errors: list[str] = result["errors"]
    if not snapshot_uri.startswith("gs://") or not manifest_uri.startswith("gs://"):
        errors.append("snapshot_uri and manifest_uri must be gs:// URIs")
        return result
    if isinstance(max_age_days, bool) or not isinstance(max_age_days, int) or max_age_days < 1:
        errors.append("max_age_days must be at least 1")
        return result
    try:
        snapshot_bytes = fetch_bytes(snapshot_uri)
    except Exception as exc:  # noqa: BLE001 - retain external read failure in the receipt.
        errors.append(f"snapshot_read_failed: {exc}")
        return result
    try:
        manifest = json.loads(fetch_bytes(manifest_uri).decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - retain external parse failure in the receipt.
        errors.append(f"manifest_read_failed: {exc}")
        return result
    if not isinstance(manifest, dict):
        errors.append("manifest must be a JSON object")
        return result

    expected = {
        "strategy_profile": contract.profile,
        "contract_version": contract.contract_version,
        "source_project": SOURCE_PROJECT,
    }
    for field, expected_value in expected.items():
        if manifest.get(field) != expected_value:
            errors.append(
                f"manifest.{field} mismatch: expected {expected_value!r}, got {manifest.get(field)!r}"
            )
    snapshot_sha256 = hashlib.sha256(snapshot_bytes).hexdigest()
    if manifest.get("snapshot_sha256") != snapshot_sha256:
        errors.append("manifest.snapshot_sha256 does not match snapshot bytes")
    try:
        snapshot_as_of = _parse_snapshot_as_of(manifest.get("snapshot_as_of"))
        age_days = (today - snapshot_as_of).days
        result["snapshot_as_of"] = snapshot_as_of.isoformat()
        result["age_days"] = age_days
        if age_days < 0:
            errors.append("manifest.snapshot_as_of is in the future")
        elif age_days > max_age_days:
            errors.append(
                f"snapshot is stale: age {age_days} days exceeds max_age_days {max_age_days}"
            )
    except ValueError as exc:
        errors.append(str(exc))
    if not errors:
        result["status"] = "verified"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only health verification for a published HK factor snapshot."
    )
    parser.add_argument("--profile", required=True)
    parser.add_argument("--snapshot-uri", required=True)
    parser.add_argument("--manifest-uri", required=True)
    parser.add_argument("--max-age-days", type=int, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--as-of", type=dt.date.fromisoformat)
    args = parser.parse_args(argv)
    receipt = verify_published_snapshot(
        profile=args.profile,
        snapshot_uri=args.snapshot_uri,
        manifest_uri=args.manifest_uri,
        max_age_days=args.max_age_days,
        fetch_bytes=_read_gcs,
        today=args.as_of or dt.datetime.now(tz=dt.UTC).date(),
    )
    payload = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if receipt["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
