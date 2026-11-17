from __future__ import annotations

from typing import Any

from .contracts import (
    HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE as HK_CENTRAL_SOE_VALUE_QUALITY_SELECT_PROFILE,
)
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("policy_value")

POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
POLICY_VALUE_STOCK_SELECTION_PROFILES: tuple[str, ...] = _SPEC.profiles
POLICY_VALUE_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
POLICY_VALUE_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
POLICY_VALUE_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
POLICY_VALUE_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_policy_value_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("policy_value")


__all__ = [
    "POLICY_VALUE_LIVE_ENABLEMENT_POLICY_VERSION",
    "POLICY_VALUE_REQUIRED_ABLATION_TESTS",
    "POLICY_VALUE_REQUIRED_DATA_PROVENANCE",
    "POLICY_VALUE_REQUIRED_STRESS_TESTS",
    "POLICY_VALUE_SOURCE_URLS",
    "POLICY_VALUE_STOCK_SELECTION_PROFILES",
    "build_policy_value_live_enablement_policy",
]
