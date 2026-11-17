from __future__ import annotations

from .policy_catalog import (
    build_execution_capacity_policy,
    build_live_enablement_thresholds,
    build_production_source_audit_policy,
    get_live_enablement_data,
    get_max_allowed_annualized_turnover,
    get_min_median_daily_turnover_hkd,
    get_min_required_rebalance_windows,
    get_production_source_reference_urls,
    get_profile_policy_map,
    get_required_benchmark_symbol,
    get_required_production_source_audit_fields,
)

_DATA = get_live_enablement_data()
_DEFAULTS = _DATA["defaults"]

MAX_ALLOWED_BACKTEST_DRAWDOWN = float(_DEFAULTS["max_allowed_backtest_drawdown"])
MIN_RETURN_TO_DRAWDOWN_RATIO = float(_DEFAULTS["min_return_to_drawdown_ratio"])
MIN_REQUIRED_OOS_FOLD_COUNT = int(_DEFAULTS["min_required_oos_fold_count"])
MAX_SINGLE_PERIOD_RETURN_CONTRIBUTION = float(_DEFAULTS["max_single_period_return_contribution"])
DEFAULT_MAX_ALLOWED_ANNUALIZED_TURNOVER = float(_DEFAULTS["max_allowed_annualized_turnover"])
DEFAULT_MIN_REQUIRED_REBALANCE_WINDOWS = int(_DEFAULTS["min_required_rebalance_windows"])
DEFAULT_MIN_ADV_WINDOW_TRADING_DAYS = int(_DEFAULTS["min_adv_window_trading_days"])
DEFAULT_MIN_MEDIAN_DAILY_TURNOVER_HKD = int(_DEFAULTS["min_median_daily_turnover_hkd"])
DEFAULT_MAX_SINGLE_ORDER_ADV_FRACTION = float(_DEFAULTS["max_single_order_adv_fraction"])
DEFAULT_MAX_REBALANCE_ADV_FRACTION = float(_DEFAULTS["max_rebalance_adv_fraction"])
MIN_REQUIRED_WALK_FORWARD_YEARS = float(_DEFAULTS["min_required_walk_forward_years"])

MAX_ALLOWED_ANNUALIZED_TURNOVER_BY_PROFILE: dict[str, float] = get_profile_policy_map(
    "max_allowed_annualized_turnover"
)
MIN_REQUIRED_REBALANCE_WINDOWS_BY_PROFILE: dict[str, int] = get_profile_policy_map(
    "min_required_rebalance_windows"
)
MIN_MEDIAN_DAILY_TURNOVER_HKD_BY_PROFILE: dict[str, int] = get_profile_policy_map(
    "min_median_daily_turnover_hkd"
)
REQUIRED_BENCHMARK_SYMBOL_BY_PROFILE: dict[str, str] = get_profile_policy_map("required_benchmark_symbol")
REQUIRED_PRODUCTION_SOURCE_AUDIT_FIELDS_BY_PROFILE: dict[str, tuple[str, ...]] = get_profile_policy_map(
    "required_production_source_audit_fields",
    as_tuple=True,
)
PRODUCTION_SOURCE_REFERENCE_URLS_BY_PROFILE: dict[str, tuple[str, ...]] = get_profile_policy_map(
    "production_source_reference_urls",
    as_tuple=True,
)

REQUIRED_BACKTEST_COST_MODEL_FIELDS: tuple[str, ...] = tuple(_DATA["required_backtest_cost_model_fields"])
REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS: tuple[str, ...] = tuple(_DATA["required_backtest_bias_control_fields"])
REQUIRED_EXECUTION_CAPACITY_FIELDS: tuple[str, ...] = tuple(_DATA["required_execution_capacity_fields"])
COMMON_PRODUCTION_SOURCE_AUDIT_FIELDS: tuple[str, ...] = tuple(_DATA["common_production_source_audit_fields"])
PRODUCTION_SOURCE_AUDIT_REQUIRED_FIELDS: tuple[str, ...] = tuple(_DATA["production_source_audit_required_fields"])
PRODUCTION_SOURCE_AUDIT_URI_FIELDS: tuple[str, ...] = tuple(_DATA["production_source_audit_uri_fields"])
COMMON_PRODUCTION_SOURCE_REFERENCE_URLS: tuple[str, ...] = tuple(_DATA["common_production_source_reference_urls"])
EXECUTION_CAPACITY_REFERENCE_URLS: tuple[str, ...] = tuple(_DATA["execution_capacity_reference_urls"])

__all__ = [
    "DEFAULT_MAX_ALLOWED_ANNUALIZED_TURNOVER",
    "DEFAULT_MAX_REBALANCE_ADV_FRACTION",
    "DEFAULT_MAX_SINGLE_ORDER_ADV_FRACTION",
    "DEFAULT_MIN_ADV_WINDOW_TRADING_DAYS",
    "DEFAULT_MIN_MEDIAN_DAILY_TURNOVER_HKD",
    "DEFAULT_MIN_REQUIRED_REBALANCE_WINDOWS",
    "EXECUTION_CAPACITY_REFERENCE_URLS",
    "MAX_ALLOWED_ANNUALIZED_TURNOVER_BY_PROFILE",
    "MAX_ALLOWED_BACKTEST_DRAWDOWN",
    "MAX_SINGLE_PERIOD_RETURN_CONTRIBUTION",
    "MIN_REQUIRED_OOS_FOLD_COUNT",
    "MIN_RETURN_TO_DRAWDOWN_RATIO",
    "MIN_MEDIAN_DAILY_TURNOVER_HKD_BY_PROFILE",
    "MIN_REQUIRED_REBALANCE_WINDOWS_BY_PROFILE",
    "MIN_REQUIRED_WALK_FORWARD_YEARS",
    "COMMON_PRODUCTION_SOURCE_AUDIT_FIELDS",
    "COMMON_PRODUCTION_SOURCE_REFERENCE_URLS",
    "PRODUCTION_SOURCE_REFERENCE_URLS_BY_PROFILE",
    "REQUIRED_BACKTEST_BIAS_CONTROL_FIELDS",
    "REQUIRED_BACKTEST_COST_MODEL_FIELDS",
    "REQUIRED_BENCHMARK_SYMBOL_BY_PROFILE",
    "REQUIRED_EXECUTION_CAPACITY_FIELDS",
    "REQUIRED_PRODUCTION_SOURCE_AUDIT_FIELDS_BY_PROFILE",
    "build_execution_capacity_policy",
    "build_production_source_audit_policy",
    "build_live_enablement_thresholds",
    "get_min_median_daily_turnover_hkd",
    "get_max_allowed_annualized_turnover",
    "get_min_required_rebalance_windows",
    "get_production_source_reference_urls",
    "get_required_production_source_audit_fields",
    "get_required_benchmark_symbol",
]
