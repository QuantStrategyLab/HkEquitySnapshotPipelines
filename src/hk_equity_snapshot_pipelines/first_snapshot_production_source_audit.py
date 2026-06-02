from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .contracts import get_profile_contract
from .first_snapshot_evidence_profiles import get_first_snapshot_evidence_profile, normalize_first_snapshot_profile
from .live_enablement_evidence import build_live_enablement_evidence_template


FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION = "hk_first_snapshot_production_source_audit_draft.v1"
DEFAULT_OUTPUT_DIR = Path("data/output/first_snapshot_production_source_audits")
_POSITIVE_NUMERIC_COLUMNS = frozenset(
    {
        "adv20_hkd",
        "close_hkd",
        "enterprise_value_hkd",
        "lot_size",
        "market_cap_hkd",
    }
)


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(path))


def _iso_or_empty(value: Any) -> str:
    if pd.isna(value):
        return ""
    return pd.Timestamp(value).date().isoformat()


def _source_path_warnings(path: Path) -> list[str]:
    lowered = str(path).lower()
    warnings: list[str] = []
    if "/examples/" in lowered or ".sample." in lowered or "sample" in path.name.lower():
        warnings.append("source_path_looks_like_sample_data; sample artifacts must not be used as production evidence")
    return warnings


def _date_summary(frame: pd.DataFrame, errors: list[str]) -> dict[str, str]:
    date_summary = {"source_coverage_start": "", "source_coverage_end": ""}
    coverage_column = "as_of" if "as_of" in frame.columns else "snapshot_date" if "snapshot_date" in frame.columns else ""
    if coverage_column:
        parsed = pd.to_datetime(frame[coverage_column], errors="coerce")
        if parsed.isna().any():
            errors.append(f"{coverage_column} contains invalid or missing dates")
        elif not frame.empty:
            date_summary = {
                "source_coverage_start": _iso_or_empty(parsed.min()),
                "source_coverage_end": _iso_or_empty(parsed.max()),
            }
    if "as_of" in frame.columns and "snapshot_date" in frame.columns:
        parsed_snapshot_date = pd.to_datetime(frame["snapshot_date"], errors="coerce")
        if parsed_snapshot_date.isna().any():
            errors.append("snapshot_date contains invalid or missing dates")
    return date_summary


def analyze_first_snapshot_production_source(
    profile: str,
    factor_snapshot_path: str | Path,
) -> dict[str, Any]:
    selected_profile = normalize_first_snapshot_profile(profile)
    evidence_profile = get_first_snapshot_evidence_profile(selected_profile)
    path = Path(factor_snapshot_path)
    frame = _read_csv(path)
    errors: list[str] = []
    warnings = _source_path_warnings(path)
    missing_columns = sorted(set(evidence_profile.required_production_columns) - set(frame.columns))
    if missing_columns:
        errors.append("missing required production source columns: " + ", ".join(missing_columns))
    if frame.empty:
        errors.append("production source must contain at least one row")

    date_summary = _date_summary(frame, errors)

    invalid_symbols: list[str] = []
    if "symbol" in frame.columns:
        normalized_symbols = frame["symbol"].map(evidence_profile.normalize_symbol)
        invalid_symbols = sorted({str(value) for value in frame.loc[normalized_symbols.eq(""), "symbol"].tolist()})
        if invalid_symbols:
            errors.append("symbol contains empty or unparseable values")

    numeric_missing: dict[str, int] = {}
    numeric_non_positive: dict[str, int] = {}
    for column in evidence_profile.numeric_source_columns:
        if column not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[column], errors="coerce")
        missing_count = int(numeric.isna().sum())
        if missing_count:
            numeric_missing[column] = missing_count
        if column in _POSITIVE_NUMERIC_COLUMNS:
            non_positive_count = int(numeric.le(0).sum())
            if non_positive_count:
                numeric_non_positive[column] = non_positive_count
    if numeric_missing:
        errors.append("numeric required columns contain missing/non-numeric values")
    if numeric_non_positive:
        errors.append("price/liquidity/capitalization/lot-size columns must be positive")

    yield_outlier_counts: dict[str, int] = {}
    for column in ("dividend_yield_net", "buyback_yield_12m", "net_payout_yield", "free_cash_flow_yield"):
        if column not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[column], errors="coerce")
        outlier_count = int((numeric.lt(-0.5) | numeric.gt(0.5)).sum())
        if outlier_count:
            yield_outlier_counts[column] = outlier_count
    if yield_outlier_counts:
        warnings.append("yield fields have values outside [-0.5, 0.5]; verify stale prices and special events")

    corporate_action_count = 0
    if "corporate_action_flag" in frame.columns:
        corporate_action_count = int(frame["corporate_action_flag"].astype(str).str.lower().isin({"true", "1", "yes"}).sum())
        if corporate_action_count:
            warnings.append("corporate_action_flag is set on some rows; verify adjustment and exclusion evidence")

    symbol_count = 0
    if "symbol" in frame.columns:
        symbol_count = int(frame["symbol"].map(evidence_profile.normalize_symbol).nunique())
    return {
        "audit_draft_version": FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION,
        "profile": selected_profile,
        "factor_snapshot_path": str(path),
        "local_schema_status": "failed" if errors else "passed_with_warnings" if warnings else "passed",
        "row_count": int(len(frame)),
        "symbol_count": symbol_count,
        "required_production_columns": list(evidence_profile.required_production_columns),
        "missing_columns": missing_columns,
        "numeric_missing": numeric_missing,
        "numeric_non_positive": numeric_non_positive,
        "invalid_symbols": invalid_symbols,
        "yield_outlier_counts": yield_outlier_counts,
        "corporate_action_count": corporate_action_count,
        **date_summary,
        "warnings": warnings,
        "errors": errors,
    }


def build_first_snapshot_production_source_audit_draft(
    *,
    profile: str,
    factor_snapshot_path: str | Path,
    source_name: str,
    production_source_uri: str = "",
    source_quality_report_uri: str = "",
    point_in_time_data_dictionary_uri: str = "",
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    selected_profile = normalize_first_snapshot_profile(profile)
    contract = get_profile_contract(selected_profile)
    evidence_profile = get_first_snapshot_evidence_profile(selected_profile)
    analysis = analyze_first_snapshot_production_source(selected_profile, factor_snapshot_path)
    template = build_live_enablement_evidence_template(contract.profile, platform="longbridge")
    draft = dict(template["production_snapshot_source_audit"])
    draft.update(
        {
            "status": "pending",
            "source_name": source_name,
            "source_coverage_start": analysis["source_coverage_start"],
            "source_coverage_end": analysis["source_coverage_end"],
            "production_source_uri": production_source_uri,
            "source_quality_report_uri": source_quality_report_uri,
            "point_in_time_data_dictionary_uri": point_in_time_data_dictionary_uri,
            "evidence_generated_at": evidence_generated_at or dt.date.today().isoformat(),
            "evidence_uri": evidence_uri,
            "local_schema_validation": analysis,
            "profile_specific_source_focus": list(evidence_profile.production_source_focus),
            "operator_note": (
                "This is a draft only. Keep status=pending until point-in-time, survivorship, "
                "corporate-action, eligibility, source-quality, and profile-specific quality/yield evidence is attached."
            ),
        }
    )
    return {
        "draft_version": FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_source_audit_draft": draft,
        "local_schema_validation": analysis,
    }


def _resolve_output_dir(output_dir: Path | None, profile: str) -> Path:
    return output_dir if output_dir is not None else DEFAULT_OUTPUT_DIR / profile


def write_first_snapshot_production_source_audit_draft(
    *,
    profile: str,
    factor_snapshot_path: str | Path,
    source_name: str,
    output_dir: Path | None = None,
    production_source_uri: str = "",
    source_quality_report_uri: str = "",
    point_in_time_data_dictionary_uri: str = "",
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    selected_profile = normalize_first_snapshot_profile(profile)
    resolved_output_dir = _resolve_output_dir(output_dir, selected_profile)
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_first_snapshot_production_source_audit_draft(
        profile=selected_profile,
        factor_snapshot_path=factor_snapshot_path,
        source_name=source_name,
        production_source_uri=production_source_uri,
        source_quality_report_uri=source_quality_report_uri,
        point_in_time_data_dictionary_uri=point_in_time_data_dictionary_uri,
        evidence_uri=evidence_uri,
        evidence_generated_at=evidence_generated_at,
    )
    draft_path = resolved_output_dir / "production_source_audit.draft.json"
    summary_path = resolved_output_dir / "source_quality_summary.json"
    draft_path.write_text(
        json.dumps(payload["production_source_audit_draft"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(payload["local_schema_validation"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {**payload, "draft_path": str(draft_path), "summary_path": str(summary_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft production source audit evidence for a first HK snapshot profile.")
    parser.add_argument("--profile", required=True, help="First snapshot candidate profile")
    parser.add_argument("--factor-snapshot", required=True, help="Operator-supplied production factor snapshot CSV")
    parser.add_argument("--source-name", required=True, help="Human-readable audited source name")
    parser.add_argument("--output-dir", help="Output directory for draft files; defaults to a profile-specific output dir")
    parser.add_argument("--production-source-uri", default="", help="Immutable production source URI")
    parser.add_argument("--source-quality-report-uri", default="", help="Immutable source quality report URI")
    parser.add_argument("--point-in-time-data-dictionary-uri", default="", help="Immutable PIT data dictionary URI")
    parser.add_argument("--evidence-uri", default="", help="Immutable evidence URI")
    parser.add_argument("--evidence-generated-at", help="Evidence generation date in YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Print payload without writing files")
    args = parser.parse_args(argv)
    kwargs = {
        "profile": args.profile,
        "factor_snapshot_path": args.factor_snapshot,
        "source_name": args.source_name,
        "production_source_uri": args.production_source_uri,
        "source_quality_report_uri": args.source_quality_report_uri,
        "point_in_time_data_dictionary_uri": args.point_in_time_data_dictionary_uri,
        "evidence_uri": args.evidence_uri,
        "evidence_generated_at": args.evidence_generated_at,
    }
    if args.json:
        payload = build_first_snapshot_production_source_audit_draft(**kwargs)
    else:
        payload = write_first_snapshot_production_source_audit_draft(
            output_dir=Path(args.output_dir) if args.output_dir else None,
            **kwargs,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "FIRST_SNAPSHOT_SOURCE_AUDIT_DRAFT_VERSION",
    "analyze_first_snapshot_production_source",
    "build_first_snapshot_production_source_audit_draft",
    "main",
    "write_first_snapshot_production_source_audit_draft",
]
