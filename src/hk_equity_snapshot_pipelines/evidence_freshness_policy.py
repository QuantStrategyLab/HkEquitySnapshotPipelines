from __future__ import annotations

from typing import Any

EVIDENCE_GENERATED_AT_FIELD = "evidence_generated_at"

MAX_ALLOWED_EVIDENCE_AGE_DAYS_BY_SECTION: dict[str, int] = {
    "production_snapshot_source_audit": 30,
    "artifact_pack_validation": 14,
    "walk_forward_backtest": 90,
    "platform_dry_run_order_preview": 14,
    "broker_permission_and_fee_verification": 30,
    "paper_or_dry_run_rebalance_window": 30,
    "runtime_rollout_plan": 30,
}


def build_evidence_freshness_policy() -> dict[str, Any]:
    return {
        "required": True,
        "required_field": EVIDENCE_GENERATED_AT_FIELD,
        "max_allowed_age_days_by_section": dict(MAX_ALLOWED_EVIDENCE_AGE_DAYS_BY_SECTION),
    }
