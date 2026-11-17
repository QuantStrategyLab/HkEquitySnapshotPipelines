from __future__ import annotations

from typing import Any

from .contracts import (
    HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE as HK_COMPOSITE_FACTOR_QUALITY_VALUE_MOMENTUM_PROFILE,
    HK_LIQUID_MOMENTUM_QUALITY_PROFILE as HK_LIQUID_MOMENTUM_QUALITY_PROFILE,
    HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE as HK_RESIDUAL_MOMENTUM_QUALITY_PROFILE,
)
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("momentum")

MOMENTUM_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
MOMENTUM_STOCK_SELECTION_PROFILES: tuple[str, ...] = _SPEC.profiles
MOMENTUM_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
MOMENTUM_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
MOMENTUM_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
MOMENTUM_LIVE_ENABLEMENT_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_momentum_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("momentum")
