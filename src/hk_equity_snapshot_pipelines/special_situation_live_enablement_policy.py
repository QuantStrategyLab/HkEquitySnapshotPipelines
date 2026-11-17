from __future__ import annotations

from typing import Any

from .contracts import (
    HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE as HK_AH_PREMIUM_RELATIVE_VALUE_PROFILE,
    HK_INDEX_REBALANCE_EVENT_PROFILE as HK_INDEX_REBALANCE_EVENT_PROFILE,
    HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE as HK_SOUTHBOUND_FLOW_MOMENTUM_PROFILE,
)
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("special_situation")

SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
SPECIAL_SITUATION_STOCK_SELECTION_PROFILES: tuple[str, ...] = _SPEC.profiles
SPECIAL_SITUATION_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
SPECIAL_SITUATION_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
SPECIAL_SITUATION_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
SPECIAL_SITUATION_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_special_situation_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("special_situation")


__all__ = [
    "SPECIAL_SITUATION_LIVE_ENABLEMENT_POLICY_VERSION",
    "SPECIAL_SITUATION_REQUIRED_ABLATION_TESTS",
    "SPECIAL_SITUATION_REQUIRED_DATA_PROVENANCE",
    "SPECIAL_SITUATION_REQUIRED_STRESS_TESTS",
    "SPECIAL_SITUATION_SOURCE_URLS",
    "SPECIAL_SITUATION_STOCK_SELECTION_PROFILES",
    "build_special_situation_live_enablement_policy",
]
