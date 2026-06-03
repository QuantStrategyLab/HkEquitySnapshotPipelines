from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .contracts import HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE, get_profile_contract
from .live_enablement_evidence import build_live_enablement_evidence_template
from .low_vol_dividend_quality_strategy import REQUIRED_FACTOR_COLUMNS, normalize_symbol


LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION = "hk_low_vol_dividend_production_source_audit_draft.v1"
DEFAULT_OUTPUT_DIR = Path("data/output/low_vol_dividend_production_source_audit")
PRODUCTION_REQUIRED_COLUMNS = tuple(
    sorted(
        REQUIRED_FACTOR_COLUMNS
        | {
            "as_of",
            "snapshot_date",
            "eligible",
            "lot_size",
            "corporate_action_flag",
        }
    )
)
NUMERIC_SOURCE_COLUMNS = (
    "adv20_hkd",
    "beta_252",
    "close_hkd",
    "dividend_stability_3y",
    "dividend_yield_net",
    "lot_size",
    "market_cap_hkd",
    "maxdd_252",
    "mom_12_1",
    "mom_6m",
    "payout_ratio",
    "realized_vol_126",
    "sma200_gap",
    "suspension_days_63",
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


def analyze_low_vol_dividend_production_source(
    factor_snapshot_path: str | Path,
) -> dict[str, Any]:
    path = Path(factor_snapshot_path)
    frame = _read_csv(path)
    errors: list[str] = []
    warnings = _source_path_warnings(path)
    missing_columns = sorted(set(PRODUCTION_REQUIRED_COLUMNS) - set(frame.columns))
    if missing_columns:
        errors.append("missing required production source columns: " + ", ".join(missing_columns))
    if frame.empty:
        errors.append("production source must contain at least one row")

    date_summary: dict[str, str] = {"source_coverage_start": "", "source_coverage_end": ""}
    if "as_of" in frame.columns:
        parsed_as_of = pd.to_datetime(frame["as_of"], errors="coerce")
        if parsed_as_of.isna().any():
            errors.append("as_of contains invalid or missing dates")
        elif not frame.empty:
            date_summary = {
                "source_coverage_start": _iso_or_empty(parsed_as_of.min()),
                "source_coverage_end": _iso_or_empty(parsed_as_of.max()),
            }
    if "snapshot_date" in frame.columns:
        parsed_snapshot_date = pd.to_datetime(frame["snapshot_date"], errors="coerce")
        if parsed_snapshot_date.isna().any():
            errors.append("snapshot_date contains invalid or missing dates")

    invalid_symbols: list[str] = []
    if "symbol" in frame.columns:
        normalized_symbols = frame["symbol"].map(normalize_symbol)
        invalid_symbols = sorted({str(value) for value in frame.loc[normalized_symbols.eq(""), "symbol"].tolist()})
        if invalid_symbols:
            errors.append("symbol contains empty or unparseable values")

    numeric_missing: dict[str, int] = {}
    numeric_non_positive: dict[str, int] = {}
    for column in NUMERIC_SOURCE_COLUMNS:
        if column not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[column], errors="coerce")
        missing_count = int(numeric.isna().sum())
        if missing_count:
            numeric_missing[column] = missing_count
        if column in {"adv20_hkd", "close_hkd", "lot_size", "market_cap_hkd"}:
            non_positive_count = int(numeric.le(0).sum())
            if non_positive_count:
                numeric_non_positive[column] = non_positive_count
    if numeric_missing:
        errors.append("numeric required columns contain missing/non-numeric values")
    if numeric_non_positive:
        errors.append("price/liquidity/lot-size columns must be positive")

    dividend_yield_outlier_count = 0
    if "dividend_yield_net" in frame.columns:
        dividend_yield = pd.to_numeric(frame["dividend_yield_net"], errors="coerce")
        dividend_yield_outlier_count = int((dividend_yield.lt(0) | dividend_yield.gt(0.5)).sum())
        if dividend_yield_outlier_count:
            warnings.append("dividend_yield_net has values outside [0, 0.5]; verify stale prices and special dividends")

    corporate_action_count = 0
    if "corporate_action_flag" in frame.columns:
        corporate_action_count = int(frame["corporate_action_flag"].astype(str).str.lower().isin({"true", "1", "yes"}).sum())
        if corporate_action_count:
            warnings.append("corporate_action_flag is set on some rows; verify adjustment and exclusion evidence")

    return {
        "audit_draft_version": LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION,
        "profile": HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE,
        "factor_snapshot_path": str(path),
        "local_schema_status": "failed" if errors else "passed_with_warnings" if warnings else "passed",
        "row_count": int(len(frame)),
        "symbol_count": int(frame["symbol"].map(normalize_symbol).nunique()) if "symbol" in frame.columns else 0,
        "missing_columns": missing_columns,
        "numeric_missing": numeric_missing,
        "numeric_non_positive": numeric_non_positive,
        "invalid_symbols": invalid_symbols,
        "dividend_yield_outlier_count": dividend_yield_outlier_count,
        "corporate_action_count": corporate_action_count,
        **date_summary,
        "warnings": warnings,
        "errors": errors,
    }


def build_low_vol_dividend_production_source_audit_draft(
    *,
    factor_snapshot_path: str | Path,
    source_name: str,
    production_source_uri: str = "",
    source_quality_report_uri: str = "",
    point_in_time_data_dictionary_uri: str = "",
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    contract = get_profile_contract(HK_LOW_VOL_DIVIDEND_QUALITY_SNAPSHOT_PROFILE)
    analysis = analyze_low_vol_dividend_production_source(factor_snapshot_path)
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
            "operator_note": (
                "This is a draft only. Keep status=pending until point-in-time, survivorship, "
                "dividend, Southbound eligibility, yield-trap, and source-quality evidence is attached."
            ),
        }
    )
    return {
        "draft_version": LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION,
        "profile": contract.profile,
        "contract_version": contract.contract_version,
        "runtime_enabled": False,
        "live_enablement_allowed": False,
        "production_source_audit_draft": draft,
        "local_schema_validation": analysis,
    }


def write_low_vol_dividend_production_source_audit_draft(
    *,
    factor_snapshot_path: str | Path,
    source_name: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    production_source_uri: str = "",
    source_quality_report_uri: str = "",
    point_in_time_data_dictionary_uri: str = "",
    evidence_uri: str = "",
    evidence_generated_at: str | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_low_vol_dividend_production_source_audit_draft(
        factor_snapshot_path=factor_snapshot_path,
        source_name=source_name,
        production_source_uri=production_source_uri,
        source_quality_report_uri=source_quality_report_uri,
        point_in_time_data_dictionary_uri=point_in_time_data_dictionary_uri,
        evidence_uri=evidence_uri,
        evidence_generated_at=evidence_generated_at,
    )
    draft_path = output_dir / "production_source_audit.draft.json"
    summary_path = output_dir / "source_quality_summary.json"
    draft_path.write_text(
        json.dumps(payload["production_source_audit_draft"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(payload["local_schema_validation"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        **payload,
        "draft_path": str(draft_path),
        "summary_path": str(summary_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft HK low-vol dividend production source audit evidence.")
    parser.add_argument("--factor-snapshot", required=True, help="Operator-supplied production factor snapshot CSV")
    parser.add_argument("--source-name", required=True, help="Human-readable audited source name")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for draft files")
    parser.add_argument("--production-source-uri", default="", help="Immutable production source URI")
    parser.add_argument("--source-quality-report-uri", default="", help="Immutable source quality report URI")
    parser.add_argument("--point-in-time-data-dictionary-uri", default="", help="Immutable PIT data dictionary URI")
    parser.add_argument("--evidence-uri", default="", help="Immutable evidence URI")
    parser.add_argument("--evidence-generated-at", help="Evidence generation date in YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Print payload after writing draft files")
    args = parser.parse_args(argv)
    kwargs = {
        "factor_snapshot_path": args.factor_snapshot,
        "source_name": args.source_name,
        "production_source_uri": args.production_source_uri,
        "source_quality_report_uri": args.source_quality_report_uri,
        "point_in_time_data_dictionary_uri": args.point_in_time_data_dictionary_uri,
        "evidence_uri": args.evidence_uri,
        "evidence_generated_at": args.evidence_generated_at,
    }
    payload = write_low_vol_dividend_production_source_audit_draft(output_dir=Path(args.output_dir), **kwargs)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "LOW_VOL_DIVIDEND_SOURCE_AUDIT_DRAFT_VERSION",
    "PRODUCTION_REQUIRED_COLUMNS",
    "analyze_low_vol_dividend_production_source",
    "build_low_vol_dividend_production_source_audit_draft",
    "main",
    "write_low_vol_dividend_production_source_audit_draft",
]
