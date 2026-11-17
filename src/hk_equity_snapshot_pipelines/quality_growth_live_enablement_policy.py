from __future__ import annotations

from typing import Any

from .contracts import (
    HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE as HK_QUALITY_GROWTH_LOW_VOLATILITY_PROFILE,
)
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("quality_growth")

QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
QUALITY_GROWTH_STOCK_SELECTION_PROFILES: tuple[str, ...] = _SPEC.profiles
QUALITY_GROWTH_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
QUALITY_GROWTH_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
QUALITY_GROWTH_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
QUALITY_GROWTH_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_quality_growth_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("quality_growth")


__all__ = [
    "QUALITY_GROWTH_LIVE_ENABLEMENT_POLICY_VERSION",
    "QUALITY_GROWTH_REQUIRED_ABLATION_TESTS",
    "QUALITY_GROWTH_REQUIRED_DATA_PROVENANCE",
    "QUALITY_GROWTH_REQUIRED_STRESS_TESTS",
    "QUALITY_GROWTH_SOURCE_URLS",
    "QUALITY_GROWTH_STOCK_SELECTION_PROFILES",
    "build_quality_growth_live_enablement_policy",
]
