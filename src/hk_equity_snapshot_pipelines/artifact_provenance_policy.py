from __future__ import annotations

from typing import Any

MIN_PRODUCTION_ARTIFACT_ROW_COUNT = 20

REQUIRED_ARTIFACT_PROVENANCE_FIELDS: tuple[str, ...] = (
    "artifact_release_id",
    "contract_version",
    "snapshot_sha256",
    "row_count",
    "published_snapshot_uri",
    "published_manifest_uri",
    "published_ranking_uri",
    "published_release_summary_uri",
)

REQUIRED_ARTIFACT_PROVENANCE_BOOLEAN_FIELDS: tuple[str, ...] = (
    "immutable_release_id",
    "published_artifacts_not_sample",
    "manifest_snapshot_sha256_verified",
    "manifest_row_count_verified",
    "release_summary_ready",
)

ARTIFACT_PROVENANCE_URI_FIELDS: tuple[str, ...] = (
    "published_snapshot_uri",
    "published_manifest_uri",
    "published_ranking_uri",
    "published_release_summary_uri",
)

ARTIFACT_PROVENANCE_REFERENCE_URLS: tuple[str, ...] = (
    "https://www.sfc.hk/en/faqs/intermediaries/supervision/Use-of-External-Electronic-Data-Storage/Use-of-External-Electronic-Data-Storage",
    "https://www.hkex.com.hk/products/securities/exchange-traded-products/overview?sc_lang=en",
    "https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Exchange-Traded-Products/Launch/HKEX_ETF-Handbook.pdf",
)


def build_artifact_provenance_policy() -> dict[str, Any]:
    return {
        "required": True,
        "required_fields": list(REQUIRED_ARTIFACT_PROVENANCE_FIELDS),
        "required_boolean_fields": list(REQUIRED_ARTIFACT_PROVENANCE_BOOLEAN_FIELDS),
        "required_uri_fields": list(ARTIFACT_PROVENANCE_URI_FIELDS),
        "sha256_hex_length": 64,
        "min_production_snapshot_row_count": MIN_PRODUCTION_ARTIFACT_ROW_COUNT,
        "source_reference_urls": list(ARTIFACT_PROVENANCE_REFERENCE_URLS),
        "description": "Snapshot live enablement must prove immutable artifact release identity, stable published snapshot/manifest/ranking/summary URIs, contract version, row count, and snapshot sha256 before platform runtime can consume artifacts.",
    }
