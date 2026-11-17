from __future__ import annotations

from typing import Any

from .contracts import HK_BLUE_CHIP_LEADER_ROTATION_PROFILE as HK_BLUE_CHIP_LEADER_ROTATION_PROFILE
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("baseline_rotation")

BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
BASELINE_ROTATION_PROFILES: tuple[str, ...] = _SPEC.profiles
BASELINE_ROTATION_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
BASELINE_ROTATION_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
BASELINE_ROTATION_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
BASELINE_ROTATION_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_baseline_rotation_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("baseline_rotation")


__all__ = [
    "BASELINE_ROTATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "BASELINE_ROTATION_PROFILES",
    "BASELINE_ROTATION_REQUIRED_ABLATION_TESTS",
    "BASELINE_ROTATION_REQUIRED_DATA_PROVENANCE",
    "BASELINE_ROTATION_REQUIRED_STRESS_TESTS",
    "BASELINE_ROTATION_SOURCE_URLS",
    "build_baseline_rotation_live_enablement_policy",
]
