from __future__ import annotations

from .policy_catalog import (
    build_artifact_provenance_policy as build_artifact_provenance_policy,
    get_core_policy_spec,
)

_SPEC = get_core_policy_spec("artifact_provenance")

MIN_PRODUCTION_ARTIFACT_ROW_COUNT = int(_SPEC["min_production_artifact_row_count"])
REQUIRED_ARTIFACT_PROVENANCE_FIELDS: tuple[str, ...] = tuple(_SPEC["required_fields"])
REQUIRED_ARTIFACT_PROVENANCE_BOOLEAN_FIELDS: tuple[str, ...] = tuple(_SPEC["required_boolean_fields"])
ARTIFACT_PROVENANCE_URI_FIELDS: tuple[str, ...] = tuple(_SPEC["required_uri_fields"])
ARTIFACT_PROVENANCE_REFERENCE_URLS: tuple[str, ...] = tuple(_SPEC["source_reference_urls"])
