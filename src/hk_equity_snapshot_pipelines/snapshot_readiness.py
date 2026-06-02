from __future__ import annotations

import argparse
import json
from typing import Any

from .artifact_provenance_policy import build_artifact_provenance_policy
from .baseline_rotation_live_enablement_policy import (
    BASELINE_ROTATION_PROFILES,
    build_baseline_rotation_live_enablement_policy,
)
from .contracts import (
    HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    SnapshotProfileContract,
    get_profile_contract,
    list_profile_contracts,
)
from .dry_run_order_preview_policy import build_dry_run_order_preview_policy
from .evidence_freshness_policy import build_evidence_freshness_policy
from .evidence_uri_policy import build_evidence_uri_policy
from .factor_mix_live_enablement_policy import (
    FACTOR_MIX_STOCK_SELECTION_PROFILES,
    build_factor_mix_live_enablement_policy,
)
from .live_enablement_policy import (
    build_execution_capacity_policy,
    build_live_enablement_thresholds,
    build_production_source_audit_policy,
)
from .momentum_live_enablement_policy import MOMENTUM_STOCK_SELECTION_PROFILES, build_momentum_live_enablement_policy
from .notification_audit_policy import SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE, build_notification_audit_policy
from .policy_value_live_enablement_policy import (
    POLICY_VALUE_STOCK_SELECTION_PROFILES,
    build_policy_value_live_enablement_policy,
)
from .quality_yield_live_enablement_policy import (
    QUALITY_YIELD_STOCK_SELECTION_PROFILES,
    build_quality_yield_live_enablement_policy,
)
from .quality_growth_live_enablement_policy import (
    QUALITY_GROWTH_STOCK_SELECTION_PROFILES,
    build_quality_growth_live_enablement_policy,
)
from .rollout_risk_policy import build_rollout_risk_policy
from .special_situation_live_enablement_policy import (
    SPECIAL_SITUATION_STOCK_SELECTION_PROFILES,
    build_special_situation_live_enablement_policy,
)

SUPPORTED_SNAPSHOT_PLATFORMS = frozenset({"ibkr", "longbridge"})
SNAPSHOT_STATUS = "architecture_scaffold_not_live_enabled"
FIRST_SNAPSHOT_PROMOTION_SCOPE = "first_snapshot_live_enablement_candidate"
RESEARCH_ONLY_SCAFFOLD_SCOPE = "research_only_scaffold"
FIRST_SNAPSHOT_READINESS_PROFILES = frozenset(
    {
        HK_LOW_VOL_DIVIDEND_QUALITY_PROFILE,
    }
)

PLATFORM_SNAPSHOT_ENV_TEMPLATES: dict[str, dict[str, str]] = {
    "ibkr": {
        "IBKR_MARKET": "HK",
        "IBKR_MARKET_EXCHANGE": "SEHK",
        "IBKR_MARKET_CURRENCY": "HKD",
        "IBKR_DRY_RUN_ONLY": "true",
        "IBKR_FEATURE_SNAPSHOT_PATH": "<published-snapshot-path>",
        "IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH": "<published-manifest-path>",
    },
    "longbridge": {
        "ACCOUNT_REGION": "HK",
        "LONGBRIDGE_MARKET": "HK",
        "LONGBRIDGE_TRADING_CURRENCY": "HKD",
        "LONGBRIDGE_DRY_RUN_ONLY": "true",
        "LONGBRIDGE_FEATURE_SNAPSHOT_PATH": "<published-snapshot-path>",
        "LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH": "<published-manifest-path>",
    },
}

SNAPSHOT_LIVE_ENABLEMENT_REQUIREMENTS: tuple[str, ...] = (
    "Production snapshot data source must be audited for corporate actions, suspensions, stale prices, and missing fields.",
    "Published snapshot CSV and manifest JSON must match the declared contract_version and profile.",
    "Strategy package must explicitly promote the snapshot-backed profile to runtime_enabled before platform selection.",
    "Platform dry-run must load the artifact, preview orders, enforce lot size, and emit bilingual EN/ZH-Hans operator notifications with a stable delivery-log URI.",
    "Broker account must have HK market data, SEHK trading permission, HKD cash handling, and approved product permissions.",
    "Backtest evidence must include at least three independent OOS folds and max single-period return contribution <= 60%.",
    "Paper trading or dry-run evidence must cover the profile-required rebalance/event windows before live order submission.",
    "Each snapshot profile family must provide matching strategy_policy_evidence before dry-run removal.",
)

SNAPSHOT_BLOCKING_REASONS: tuple[str, ...] = (
    "Current snapshot profiles are architecture scaffolds, not runtime_enabled strategies.",
    "Sample artifacts are not production data feeds and must not drive scheduled live trading.",
    "This readiness output is a validation plan only; it does not deploy Cloud Run or change platform settings.",
)

SNAPSHOT_PROFILE_PROMOTION_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "hk_ah_premium_relative_value": (
        "Audit AH pair mapping, A/H close alignment, FX source, Stock Connect eligibility history, and AH price-ratio formula lineage.",
        "Recompute AH premium percentiles from survivorship-safe raw history instead of relying on sample fields.",
        "Validate long-only H-share execution with HK costs, lot sizes, liquidity caps, corporate-action handling, and A-share access / shorting / settlement constraint review.",
        "Stress extreme-premium false reversals and compare AH Smart-style share-class switch thresholds against the long-only H-share overlay.",
    ),
    "hk_blue_chip_leader_rotation": (
        "Replace sample price/universe files with an audited production feature snapshot source.",
        "Validate total-return adjustments, stale-price detection, suspensions, and benchmark-relative momentum fields.",
    ),
    "hk_central_soe_value_quality_select": (
        "Audit point-in-time central-SOE largest-shareholder classification, look-through ownership chains, SASAC/MOF source-list effective dates, and methodology versions.",
        "Validate central-SOE value-quality ranks against broad value/quality, HSI Central SOEs value/quality factor indexes, and existing quality-yield ablations.",
        "Reconcile HKEX Southbound eligibility, HSI factor Z-score standardisation, missing-measure averaging, 40% factor screening with buffer rules, and 5% factor-index / 10% base-index capping lineage before accepting production factors.",
        "Audit source-list effective-date drift for SASAC/MOF parent mergers, splits, and reclassifications before treating largest-shareholder flags as point-in-time.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector caps, cap-induced turnover, Southbound eligibility removal, parent restructuring, public-float, sanctions, dividend-cut, and policy-event stress windows.",
    ),
    "hk_composite_factor_quality_value_momentum": (
        "Audit quality, value, momentum, low-volatility, factor-score normalization, and Southbound eligibility fields from production factor data.",
        "Reconcile the momentum sleeve against HSI close-to-high descriptors and MSCI-style 6/12-month one-month-skip risk-adjusted momentum.",
        "Validate composite-factor ranks with survivorship-safe history and profile annualized turnover <= 120%.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, and sector caps before any platform exposure.",
    ),
    "hk_factor_mix_qvlm_risk_parity": (
        "Audit point-in-time quality, value, momentum, low-volatility, and factor-volatility histories.",
        "Reconcile HSI QVLM parent Large-Mid Cap Investable universe, Quality/Value/Low Volatility/Momentum component-index return history, risk-parity weight, and 12% capping lineage against MSCI equal-weight Q/V/L factor-mix controls.",
        "Validate MSCI HK Factor Mix A-Series component-index equal weighting and capped-methodology history before treating it as an external Q/V/L control.",
        "Validate factor covariance/correlation history, risk-parity rebalance-window sensitivity, factor score winsorization, component overlap, and cap-induced turnover.",
        "Validate risk-parity factor weights against equal-weight QVLM and composite QVM on the same universe.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector/single-name caps, factor-correlation breakdowns, and factor-crowding stress windows.",
    ),
    "hk_free_cash_flow_quality": (
        "Audit free-cash-flow formula lineage, enterprise-value market-cap/debt/cash/FX inputs, ROE, revenue-growth, and reporting-date availability fields.",
        "Validate FCF-quality ranks with survivorship-safe history, benchmark excess return, and profile annualized turnover <= 100%.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector caps, FCF restatement/as-of handling, and negative-FCF / financial-real-estate exception handling.",
    ),
    "hk_index_rebalance_event": (
        "Audit HSI index methodology / operation-guide versions, review calendars, regular rebalancing schedule files, next-review notices, announcement timestamps, effective dates, and constituent-change identifiers.",
        "Validate event sample construction against official review-result press releases, constituent weights / pro-forma files, add/delete labels, and schedule-file versions to avoid look-ahead bias.",
        "Run event-window backtests with candidate-probability, confirmed add/delete, pro-forma-weighted versus equal-weight event-trade ablations, crowding, capacity, slippage, fast-entry / suspension / buffer-rule exceptions, and effective-date order timing controls.",
        "Validate HKEX Closing Auction Session / market-on-close order type, random-close, two-stage price-limit, order-rejection, passive-flow imbalance, and auction-liquidity controls before dry-run removal.",
    ),
    "hk_liquid_momentum_quality": (
        "Run walk-forward tests on production adjusted history with realistic HK costs and turnover controls.",
        "Validate 52-week-high, 12-1 price momentum, MSCI-style 6/12-month one-month-skip risk-adjusted momentum, volatility, drawdown, suspension, and corporate-action fields.",
        "Prove hold buffers, sector caps, capacity, and momentum-crash controls before platform selection.",
    ),
    "hk_quality_growth_low_volatility": (
        "Audit point-in-time growth, ROE, accruals, cash-flow-to-debt, Growth in ROA adjusted by P/B, volatility, sector, and Southbound eligibility fields.",
        "Reconcile HSI QGLV four-component score lineage with MSCI quality variables: ROE, stable earnings growth, low leverage, and cash-conversion / quality-trap controls.",
        "Validate HSI low-volatility quality screening and minimum-volatility optimizer constraints against simple 12-month-volatility, beta, residual-volatility, drawdown, and liquidity filters.",
        "Audit HSI QGLV winsorized z-scores, Financials-only component handling, negative-equity treatment, and missing-factor policy before backtests.",
        "Validate quality-growth low-vol ranks with same-universe factor ablation and profile annualized turnover <= 100%.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector caps, real-estate/financial concentration checks, and growth-deceleration stress windows.",
    ),
    "hk_low_vol_dividend_quality": (
        "Audit fundamentals, Southbound eligibility, large/mid-cap shortlist, forecast-dividend-yield estimate history, three-year cash-dividend records, payout-ratio bounds, earnings-positive flags, and corporate-action adjustments.",
        "Ablate forecast dividend yield versus trailing dividend yield and reject stale estimate revisions before accepting forward-yield signals.",
        "Validate yield-trap filters, price-crash screens, one-year high-volatility exclusion, financial-soundness screens, sector caps, and dividend cash treatment against broker reporting.",
    ),
    "hk_residual_momentum_quality": (
        "Audit residual momentum, industry-relative momentum, benchmark-relative momentum, one-month reversal skip, beta, volatility, and model-fit-window fields.",
        "Reconcile residual / industry-neutral ranks against HSI close-to-high descriptors and MSCI-style 6/12-month risk-adjusted momentum.",
        "Validate industry-neutral momentum ranks with survivorship-safe history and profile annualized turnover <= 120%.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector caps, and benchmark excess-return checks.",
    ),
    "hk_shareholder_yield_quality": (
        "Audit dividend, forecast-dividend-yield estimate history, HKEX next-day buyback returns, treasury-share retention/cancellation/resale, share-count, FCF, ROE, and debt fields from production disclosures.",
        "Ablate forecast dividend yield versus trailing dividend yield and stress stale estimate revisions plus financials-sector forward-yield concentration.",
        "Validate shareholder-yield ranks with survivorship-safe history and profile annualized turnover <= 100%.",
        "Run walk-forward tests with HK costs, lot sizes, suspensions, sector caps, dilution controls, treasury-share moratorium/blackout controls, post-buyback financing checks, and benchmark excess-return checks.",
    ),
    "hk_southbound_flow_momentum": (
        "Build and audit a production Stock Connect flow collector with holiday-aware smoothing, point-in-time eligibility, and data-dissemination-change handling.",
        "Recompute flow z-score and persistence from raw HKEX daily turnover, top-10 turnover, and CCASS Southbound shareholding data; validate missing-flow-day handling.",
        "Reconcile raw HKEX/CCASS records against any vendor-derived flow feed before using the signal in platform dry-run.",
    ),
}


def _normalize_platform(platform_id: str) -> str:
    normalized = str(platform_id or "").strip().lower()
    if normalized not in SUPPORTED_SNAPSHOT_PLATFORMS:
        known = ", ".join(sorted(SUPPORTED_SNAPSHOT_PLATFORMS))
        raise ValueError(f"Unsupported snapshot readiness platform {platform_id!r}; known platforms: {known}")
    return normalized


def _artifact_filenames(contract: SnapshotProfileContract) -> dict[str, str]:
    return {
        "snapshot": contract.snapshot_filename,
        "manifest": contract.manifest_filename,
        "ranking": contract.ranking_filename,
        "release_summary": contract.release_summary_filename,
    }


def _artifact_validation_command(contract: SnapshotProfileContract) -> str:
    return (
        "hkeq-validate-snapshot-artifact-pack "
        f"--profile {contract.profile} --artifact-dir <published-artifact-dir> --json"
    )


def _live_enablement_evidence_command() -> str:
    return "hkeq-validate-live-enable-evidence --evidence-file <live-enable-evidence.json> --json"


def _live_enablement_evidence_template_command(contract: SnapshotProfileContract, *, platform: str) -> str:
    return (
        "hkeq-validate-live-enable-evidence "
        f"--print-template --profile {contract.profile} --platform {platform} --json"
    )


def build_snapshot_readiness(profile: str, *, platform_id: str) -> dict[str, Any]:
    platform = _normalize_platform(platform_id)
    contract = get_profile_contract(profile)
    is_first_snapshot_candidate = contract.profile in FIRST_SNAPSHOT_READINESS_PROFILES
    platform_env = dict(PLATFORM_SNAPSHOT_ENV_TEMPLATES[platform])
    feature_key = next(key for key in platform_env if key.endswith("FEATURE_SNAPSHOT_PATH"))
    manifest_key = next(key for key in platform_env if key.endswith("FEATURE_SNAPSHOT_MANIFEST_PATH"))
    platform_env[feature_key] = contract.snapshot_filename
    platform_env[manifest_key] = contract.manifest_filename

    payload = {
        "platform": platform,
        "profile": contract.profile,
        "display_name": contract.display_name,
        "status": SNAPSHOT_STATUS,
        "promotion_scope": (
            FIRST_SNAPSHOT_PROMOTION_SCOPE
            if is_first_snapshot_candidate
            else RESEARCH_ONLY_SCAFFOLD_SCOPE
        ),
        "live_enablement_work_queue": is_first_snapshot_candidate,
        "requires_full_backtest_now": is_first_snapshot_candidate,
        "evidence_tooling_scope": (
            "active_first_snapshot_shared_evidence_tools"
            if is_first_snapshot_candidate
            else "research_only_no_live_enablement_package"
        ),
        "runtime_enabled": False,
        "manifest_required_by_runtime": contract.manifest_required_by_runtime,
        "contract_version": contract.contract_version,
        "artifact_filenames": _artifact_filenames(contract),
        "artifact_validation": {
            "required": True,
            "command": _artifact_validation_command(contract),
        },
        "live_enablement_evidence_validation": {
            "required": True,
            "command": _live_enablement_evidence_command(),
            "template_command": _live_enablement_evidence_template_command(contract, platform=platform),
        },
        "live_enablement_thresholds": build_live_enablement_thresholds(contract.profile),
        "production_source_audit_policy": build_production_source_audit_policy(contract.profile),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "evidence_uri_policy": build_evidence_uri_policy(),
        "evidence_freshness_policy": build_evidence_freshness_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(contract.profile),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "neutral_gcs_prefix_hint": contract.neutral_gcs_prefix_hint,
        "platform_env_template": platform_env,
        "live_enablement_requirements": list(SNAPSHOT_LIVE_ENABLEMENT_REQUIREMENTS),
        "profile_live_enablement_requirements": list(
            SNAPSHOT_PROFILE_PROMOTION_REQUIREMENTS.get(contract.profile, ())
        ),
        "blocking_reasons": list(SNAPSHOT_BLOCKING_REASONS)
        + (
            []
            if is_first_snapshot_candidate
            else [
                "This profile is retained as a research-only scaffold and is outside the active live-enable work queue."
            ]
        ),
    }
    if contract.profile in BASELINE_ROTATION_PROFILES:
        payload["baseline_rotation_live_enablement_policy"] = build_baseline_rotation_live_enablement_policy()
    if contract.profile in QUALITY_YIELD_STOCK_SELECTION_PROFILES:
        payload["quality_yield_live_enablement_policy"] = build_quality_yield_live_enablement_policy()
    if contract.profile in QUALITY_GROWTH_STOCK_SELECTION_PROFILES:
        payload["quality_growth_live_enablement_policy"] = build_quality_growth_live_enablement_policy()
    if contract.profile in FACTOR_MIX_STOCK_SELECTION_PROFILES:
        payload["factor_mix_live_enablement_policy"] = build_factor_mix_live_enablement_policy()
    if contract.profile in MOMENTUM_STOCK_SELECTION_PROFILES:
        payload["momentum_live_enablement_policy"] = build_momentum_live_enablement_policy()
    if contract.profile in POLICY_VALUE_STOCK_SELECTION_PROFILES:
        payload["policy_value_live_enablement_policy"] = build_policy_value_live_enablement_policy()
    if contract.profile in SPECIAL_SITUATION_STOCK_SELECTION_PROFILES:
        payload["special_situation_live_enablement_policy"] = build_special_situation_live_enablement_policy()
    return payload


def build_snapshot_readiness_matrix(*, platform_id: str) -> dict[str, Any]:
    platform = _normalize_platform(platform_id)
    profiles = [
        build_snapshot_readiness(contract.profile, platform_id=platform)
        for contract in sorted(list_profile_contracts(), key=lambda item: item.profile)
    ]
    blocked_profiles = [item["profile"] for item in profiles if not item["runtime_enabled"]]
    return {
        "platform": platform,
        "status": SNAPSHOT_STATUS,
        "live_enable_gate": "blocked_until_production_evidence",
        "runtime_enabled_count": sum(1 for item in profiles if item["runtime_enabled"]),
        "blocked_profile_count": len(blocked_profiles),
        "blocked_profiles": blocked_profiles,
        "profile_count": len(profiles),
        "profiles": profiles,
        "evidence_uri_policy": build_evidence_uri_policy(),
        "artifact_provenance_policy": build_artifact_provenance_policy(),
        "evidence_freshness_policy": build_evidence_freshness_policy(),
        "execution_capacity_policy": build_execution_capacity_policy(""),
        "dry_run_order_preview_policy": build_dry_run_order_preview_policy(),
        "rollout_risk_policy": build_rollout_risk_policy(),
        "notification_audit_policy": build_notification_audit_policy(SNAPSHOT_DRY_RUN_NOTIFICATION_EVENT_TYPE),
        "baseline_rotation_live_enablement_policy": build_baseline_rotation_live_enablement_policy(),
        "quality_yield_live_enablement_policy": build_quality_yield_live_enablement_policy(),
        "quality_growth_live_enablement_policy": build_quality_growth_live_enablement_policy(),
        "factor_mix_live_enablement_policy": build_factor_mix_live_enablement_policy(),
        "momentum_live_enablement_policy": build_momentum_live_enablement_policy(),
        "policy_value_live_enablement_policy": build_policy_value_live_enablement_policy(),
        "special_situation_live_enablement_policy": build_special_situation_live_enablement_policy(),
        "required_evidence_categories": [
            "production_snapshot_source_audit",
            "production_source_uri_and_quality_report_provenance",
            "production_source_profile_specific_fields",
            "baseline_rotation_ablation_hsi_constituent_and_execution_controls",
            "quality_yield_ablation_and_yield_trap_controls",
            "quality_growth_ablation_growth_deceleration_and_low_vol_controls",
            "factor_mix_risk_parity_ablation_and_factor_volatility_controls",
            "momentum_factor_ablation_descriptor_reconciliation_and_crash_controls",
            "policy_value_government_ownership_and_concentration_controls",
            "special_situation_signal_decay_crowding_and_calendar_alignment_controls",
            "artifact_publication_provenance",
            "fresh_section_evidence_generated_at",
            "execution_capacity_and_liquidity_limits",
            "dry_run_order_preview_artifact_provenance",
            "staged_rollout_tripwires_and_rollback",
            "contract_manifest_publication",
            "artifact_pack_validation",
            "live_enablement_evidence_validation",
            "walk_forward_backtest",
            "turnover_and_cost_model_limits",
            "platform_dry_run_order_preview",
            "bilingual_notification_delivery_log",
            "broker_permission_and_fee_verification",
            "paper_or_dry_run_rebalance_window",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print HK snapshot profile readiness plan.")
    parser.add_argument("--profile")
    parser.add_argument("--all", action="store_true", help="Print readiness for every snapshot profile")
    parser.add_argument("--platform", required=True, choices=tuple(sorted(SUPPORTED_SNAPSHOT_PLATFORMS)))
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args(argv)

    if args.all:
        payload = build_snapshot_readiness_matrix(platform_id=args.platform)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        print(f"platform={payload['platform']}")
        print(f"status={payload['status']}")
        print(f"live_enable_gate={payload['live_enable_gate']}")
        print(f"profile_count={payload['profile_count']}")
        print(f"blocked_profile_count={payload['blocked_profile_count']}")
        for profile in payload["profiles"]:
            print(f"- {profile['profile']}: runtime_enabled={profile['runtime_enabled']}")
        return 0

    if not args.profile:
        parser.error("--profile is required unless --all is set")

    payload = build_snapshot_readiness(args.profile, platform_id=args.platform)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"profile={payload['profile']}")
    print(f"platform={payload['platform']}")
    print(f"status={payload['status']}")
    print(f"runtime_enabled={payload['runtime_enabled']}")
    print("blocking_reasons:")
    for reason in payload["blocking_reasons"]:
        print(f"- {reason}")
    return 0


__all__ = [
    "PLATFORM_SNAPSHOT_ENV_TEMPLATES",
    "SNAPSHOT_BLOCKING_REASONS",
    "SNAPSHOT_LIVE_ENABLEMENT_REQUIREMENTS",
    "SNAPSHOT_PROFILE_PROMOTION_REQUIREMENTS",
    "SUPPORTED_SNAPSHOT_PLATFORMS",
    "build_snapshot_readiness_matrix",
    "build_snapshot_readiness",
    "main",
]
