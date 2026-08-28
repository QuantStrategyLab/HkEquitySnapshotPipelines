from __future__ import annotations

import datetime as dt
import hashlib
import json

from hk_equity_snapshot_pipelines.published_snapshot_health import verify_published_snapshot


SNAPSHOT_URI = "gs://example/hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv"
MANIFEST_URI = f"{SNAPSHOT_URI}.manifest.json"


def _objects(*, snapshot_as_of: str = "2026-08-28") -> dict[str, bytes]:
    snapshot = b"symbol,score\n0700.HK,1\n"
    manifest = {
        "strategy_profile": "hk_low_vol_dividend_quality_snapshot",
        "contract_version": "hk_low_vol_dividend_quality_snapshot.factor_snapshot.v1",
        "source_project": "HkEquitySnapshotPipelines",
        "snapshot_sha256": hashlib.sha256(snapshot).hexdigest(),
        "snapshot_as_of": snapshot_as_of,
    }
    return {SNAPSHOT_URI: snapshot, MANIFEST_URI: json.dumps(manifest).encode("utf-8")}


def test_published_snapshot_health_accepts_verified_fresh_artifact():
    objects = _objects()

    receipt = verify_published_snapshot(
        profile="hk_low_vol_dividend_quality_snapshot",
        snapshot_uri=SNAPSHOT_URI,
        manifest_uri=MANIFEST_URI,
        max_age_days=40,
        fetch_bytes=objects.__getitem__,
        today=dt.date(2026, 8, 28),
    )

    assert receipt["status"] == "verified"
    assert receipt["age_days"] == 0
    assert receipt["errors"] == []


def test_published_snapshot_health_fails_closed_on_digest_or_freshness_error():
    objects = _objects(snapshot_as_of="2026-07-01")
    manifest = json.loads(objects[MANIFEST_URI])
    manifest["snapshot_sha256"] = "invalid"
    objects[MANIFEST_URI] = json.dumps(manifest).encode("utf-8")

    receipt = verify_published_snapshot(
        profile="hk_low_vol_dividend_quality_snapshot",
        snapshot_uri=SNAPSHOT_URI,
        manifest_uri=MANIFEST_URI,
        max_age_days=40,
        fetch_bytes=objects.__getitem__,
        today=dt.date(2026, 8, 28),
    )

    assert receipt["status"] == "failed"
    assert "manifest.snapshot_sha256 does not match snapshot bytes" in receipt["errors"]
    assert any("snapshot is stale" in error for error in receipt["errors"])


def test_published_snapshot_health_fails_closed_when_object_is_unreadable():
    def unavailable(_: str) -> bytes:
        raise RuntimeError("forbidden")

    receipt = verify_published_snapshot(
        profile="hk_low_vol_dividend_quality_snapshot",
        snapshot_uri=SNAPSHOT_URI,
        manifest_uri=MANIFEST_URI,
        max_age_days=40,
        fetch_bytes=unavailable,
        today=dt.date(2026, 8, 28),
    )

    assert receipt["status"] == "failed"
    assert receipt["errors"] == ["snapshot_read_failed: forbidden"]
