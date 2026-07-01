from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
from typing import Any

from .first_snapshot_promotion_plan import build_first_snapshot_promotion_plan
from .snapshot_promotion_matrix import build_snapshot_promotion_matrix


DEFAULT_SOURCE_REPO = "QuantStrategyLab/HkEquitySnapshotPipelines"
DEFAULT_SOURCE_REF = "main"
DEFAULT_CODEX_AUDIT_REPOSITORY = "QuantStrategyLab/CodexAuditBridge"
MONTHLY_SNAPSHOT_AUDIT_TASK = "monthly_snapshot_audit"
MONTHLY_SNAPSHOT_AUDIT_BUNDLE_VERSION = "hk_snapshot_monthly_audit_bundle.v1"
DEFAULT_OUTPUT_DIR = Path("data/output/monthly_snapshot_audit")


def normalize_as_of_month(value: str | None = None) -> str:
    if value is None or not value.strip():
        return dt.datetime.now(dt.UTC).strftime("%Y-%m")
    normalized = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}", normalized):
        raise ValueError(f"as-of month must use YYYY-MM format, got {value!r}")
    year, month = normalized.split("-")
    if not 1 <= int(month) <= 12:
        raise ValueError(f"as-of month has invalid month value, got {value!r}")
    return f"{int(year):04d}-{int(month):02d}"


def _profile_table(plan: dict[str, Any]) -> str:
    lines = [
        "| Rank | Profile | Stage | Required drawdown gate | Next evidence focus |",
        "| --- | --- | --- | --- | --- |",
    ]
    for profile in plan["profiles"]:
        thresholds = profile["live_enablement_thresholds"]
        max_drawdown = int(round(float(thresholds["max_allowed_backtest_drawdown"]) * 100))
        lines.append(
            "| {rank} | `{profile}` | `{stage}` | max drawdown <= {max_drawdown}% | {next_action} |".format(
                rank=profile["rank"],
                profile=profile["profile"],
                stage=profile["recommended_live_enablement_stage"],
                max_drawdown=max_drawdown,
                next_action=profile["next_live_enablement_action"],
            )
        )
    return "\n".join(lines)


def _excluded_profiles(plan: dict[str, Any]) -> str:
    excluded = plan["excluded_from_scope"]
    if not excluded:
        return "None."
    return "\n".join(f"- `{profile}` — research-only / deprioritized until stronger validated evidence exists." for profile in excluded)


def _promotion_steps(plan: dict[str, Any]) -> str:
    return "\n".join(
        f"{step['step']}. **{step['name']}** — {step['description']}"
        for step in plan["promotion_steps"]
    )


def build_monthly_snapshot_audit_issue(
    *,
    as_of_month: str | None = None,
    source_repo: str = DEFAULT_SOURCE_REPO,
    source_ref: str = DEFAULT_SOURCE_REF,
    codex_audit_repository: str = DEFAULT_CODEX_AUDIT_REPOSITORY,
) -> dict[str, Any]:
    month = normalize_as_of_month(as_of_month)
    plan = build_first_snapshot_promotion_plan()
    matrix = build_snapshot_promotion_matrix()
    backtest_policy = plan["shared_gates"]["backtest_validation_policy"]
    min_oos_folds = backtest_policy["min_required_oos_fold_count"]
    title = f"HK Snapshot Monthly Audit: {month}"
    body = "\n".join(
        [
            f"# {title}",
            "",
            "This issue is the monthly AI audit input for HK snapshot-backed strategy scaffolds.",
            "It is intended for `CodexAuditBridge` and does not publish artifacts, deploy Cloud Run, or place broker orders.",
            "",
            "## Routing",
            "",
            f"- Source repo: `{source_repo}`",
            f"- Source ref: `{source_ref}`",
            f"- Codex audit repo: `{codex_audit_repository}`",
            f"- Codex task: `{MONTHLY_SNAPSHOT_AUDIT_TASK}`",
            f"- Bundle version: `{MONTHLY_SNAPSHOT_AUDIT_BUNDLE_VERSION}`",
            "",
            "## Active snapshot candidate",
            "",
            _profile_table(plan),
            "",
            "This profile remains an `architecture_scaffold` candidate until the evidence gates below pass.",
            "No live-enable approval should be inferred from sample artifacts or from this monthly audit issue alone.",
            "",
            "## Non-selected snapshot profiles",
            "",
            _excluded_profiles(plan),
            "",
            "## Required gates for AI review",
            "",
            _promotion_steps(plan),
            "",
            "The backtest gate requires point-in-time inputs, no look-ahead bias, no survivorship bias, "
            f"at least {min_oos_folds} independent OOS folds, and max drawdown <= 30% after HK costs.",
            "",
            "The dry-run gate requires LongBridge and IBKR order-preview evidence with lot-size, liquidity, "
            "fee, quote, capacity, and bilingual notification evidence. Operator approval is still required "
            "before any live-enable change.",
            "",
            "## Operator checklist for this month",
            "",
            "- Confirm whether production factor snapshots replaced all sample inputs.",
            "- Confirm artifact pack validation outputs and immutable evidence URIs are attached.",
            "- Confirm walk-forward backtests remain net of HK costs/slippage and within the 30% drawdown cap.",
            "- Confirm dry-run order previews exist for both LongBridge and IBKR before promotion.",
            "- Confirm English and Chinese notification previews/delivery logs use the unified notification format.",
            "",
            "## Reproducible local commands",
            "",
            "```bash",
            "python scripts/print_first_snapshot_promotion_plan.py --json",
            "python scripts/print_snapshot_promotion_matrix.py --json",
            "python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality_snapshot --platform longbridge --json",
            "python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality_snapshot --platform ibkr --json",
            "hkeq-validate-live-enable-evidence --evidence-file <live-enable-evidence.json> --json",
            "```",
            "",
            "## Snapshot matrix summary",
            "",
            f"- Matrix status: `{matrix['status']}`",
            f"- Source project: `{matrix['source_project']}`",
            f"- Active candidates: `{', '.join(plan['profiles_in_scope'])}`",
            f"- Live enablement without evidence: `{plan['live_enablement_allowed_without_evidence']}`",
            "",
            "## Requested Codex output",
            "",
            "Please provide a concise bilingual review covering release consistency, evidence gaps, downstream impact, "
            "and operator action items. Do not recommend production trading changes unless all evidence gates are present.",
        ]
    )
    return {
        "bundle_version": MONTHLY_SNAPSHOT_AUDIT_BUNDLE_VERSION,
        "as_of_month": month,
        "issue_title": title,
        "source_repo": source_repo,
        "source_ref": source_ref,
        "codex_audit_repository": codex_audit_repository,
        "codex_task": MONTHLY_SNAPSHOT_AUDIT_TASK,
        "profiles_in_scope": plan["profiles_in_scope"],
        "excluded_from_scope": plan["excluded_from_scope"],
        "issue_body": body,
    }


def write_monthly_snapshot_audit_issue(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    as_of_month: str | None = None,
    source_repo: str = DEFAULT_SOURCE_REPO,
    source_ref: str = DEFAULT_SOURCE_REF,
    codex_audit_repository: str = DEFAULT_CODEX_AUDIT_REPOSITORY,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_monthly_snapshot_audit_issue(
        as_of_month=as_of_month,
        source_repo=source_repo,
        source_ref=source_ref,
        codex_audit_repository=codex_audit_repository,
    )
    body_path = output_dir / "ai_review_input.md"
    summary_path = output_dir / "job_summary.md"
    metadata_path = output_dir / "monthly_snapshot_audit_issue.json"
    body_path.write_text(payload["issue_body"] + "\n", encoding="utf-8")
    summary_path.write_text(
        "\n".join(
            [
                f"## {payload['issue_title']}",
                "",
                f"- Source repo: `{payload['source_repo']}`",
                f"- Codex bridge: `{payload['codex_audit_repository']}`",
                f"- Codex task: `{payload['codex_task']}`",
                f"- Profiles in scope: `{', '.join(payload['profiles_in_scope'])}`",
                "- Scope: audit issue generation only; no publish, no deployment, no broker orders.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    metadata = {
        key: value
        for key, value in payload.items()
        if key != "issue_body"
    }
    metadata.update(
        {
            "artifact_name": f"hk-snapshot-monthly-audit-{payload['as_of_month']}",
            "ai_review_input_path": str(body_path),
            "job_summary_path": str(summary_path),
        }
    )
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        **metadata,
        "issue_body_path": str(body_path),
        "metadata_path": str(metadata_path),
        "job_summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the HK snapshot monthly audit issue bundle.")
    parser.add_argument("--as-of-month", help="Audit month in YYYY-MM format. Defaults to the current UTC month.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for the audit issue bundle.")
    parser.add_argument("--source-repo", default=DEFAULT_SOURCE_REPO, help="Source repository name.")
    parser.add_argument("--source-ref", default=DEFAULT_SOURCE_REF, help="Source branch or ref.")
    parser.add_argument(
        "--codex-audit-repository",
        default=DEFAULT_CODEX_AUDIT_REPOSITORY,
        help="Repository that owns the CodexAuditBridge workflow.",
    )
    args = parser.parse_args(argv)
    payload = write_monthly_snapshot_audit_issue(
        output_dir=Path(args.output_dir),
        as_of_month=args.as_of_month,
        source_repo=args.source_repo,
        source_ref=args.source_ref,
        codex_audit_repository=args.codex_audit_repository,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_CODEX_AUDIT_REPOSITORY",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SOURCE_REF",
    "DEFAULT_SOURCE_REPO",
    "MONTHLY_SNAPSHOT_AUDIT_BUNDLE_VERSION",
    "MONTHLY_SNAPSHOT_AUDIT_TASK",
    "build_monthly_snapshot_audit_issue",
    "main",
    "normalize_as_of_month",
    "write_monthly_snapshot_audit_issue",
]
