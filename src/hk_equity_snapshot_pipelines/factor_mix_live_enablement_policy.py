from __future__ import annotations

from typing import Any

from .contracts import HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE as HK_FACTOR_MIX_QVLM_RISK_PARITY_PROFILE
from .policy_catalog import build_strategy_family_policy, get_strategy_family_spec

_SPEC = get_strategy_family_spec("factor_mix")

FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION = _SPEC.policy_version
FACTOR_MIX_STOCK_SELECTION_PROFILES: tuple[str, ...] = _SPEC.profiles
FACTOR_MIX_REQUIRED_ABLATION_TESTS: tuple[str, ...] = _SPEC.required_ablation_tests
FACTOR_MIX_REQUIRED_STRESS_TESTS: tuple[str, ...] = _SPEC.required_stress_tests
FACTOR_MIX_REQUIRED_DATA_PROVENANCE: tuple[str, ...] = _SPEC.required_data_provenance
FACTOR_MIX_SOURCE_URLS: tuple[str, ...] = _SPEC.source_reference_urls


def build_factor_mix_live_enablement_policy() -> dict[str, Any]:
    return build_strategy_family_policy("factor_mix")


__all__ = [
    "FACTOR_MIX_LIVE_ENABLEMENT_POLICY_VERSION",
    "FACTOR_MIX_REQUIRED_ABLATION_TESTS",
    "FACTOR_MIX_REQUIRED_DATA_PROVENANCE",
    "FACTOR_MIX_REQUIRED_STRESS_TESTS",
    "FACTOR_MIX_SOURCE_URLS",
    "FACTOR_MIX_STOCK_SELECTION_PROFILES",
    "build_factor_mix_live_enablement_policy",
]
