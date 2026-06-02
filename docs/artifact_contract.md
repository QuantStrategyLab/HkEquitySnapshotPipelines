# HK Equity Snapshot Artifact Contract


## 中文摘要

- 用途：本文档围绕 `HK Equity Snapshot Artifact Contract`，用于理解 `HkEquitySnapshotPipelines` 的配置、运行、部署、研究或验收边界。
- 主要覆盖：`Profile`、`Files`、`Required snapshot columns`、`Runtime mapping`。
- 阅读顺序：先确认边界、输入输出和权限要求，再执行文档里的命令、CI、dry-run、发布或切换步骤。
- 风险提示：涉及实盘、密钥、权限、Cloud Run、交易所或券商 API 的变更，必须先在测试环境或 dry-run 验证；不要只凭示例直接修改生产。
- 英文正文保留更完整的命令、字段名和配置键；如果摘要和正文不一致，以正文中的实际命令和配置为准。

## Profiles

### `hk_blue_chip_leader_rotation`

> Current status: architecture scaffold. These contracts are stable enough for platform wiring tests, but not yet a production trading feed.

The snapshot strategy helper and feature-column contract live in this repository. The non-snapshot
`HkEquityStrategies` runtime catalog should not expose this profile until the snapshot data source
and publication flow are promoted.

## Files

### `hk_ah_premium_relative_value`

| Artifact | Filename |
| --- | --- |
| Valuation snapshot | `hk_ah_premium_relative_value_valuation_snapshot_latest.csv` |
| Manifest | `hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_ah_premium_relative_value_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_blue_chip_leader_rotation`

| Artifact | Filename |
| --- | --- |
| Feature snapshot | `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv` |
| Manifest | `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_blue_chip_leader_rotation_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_central_soe_value_quality_select`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_central_soe_value_quality_select_factor_snapshot_latest.csv` |
| Manifest | `hk_central_soe_value_quality_select_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_central_soe_value_quality_select_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_composite_factor_quality_value_momentum`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv` |
| Manifest | `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_composite_factor_quality_value_momentum_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_factor_mix_qvlm_risk_parity`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv` |
| Manifest | `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_factor_mix_qvlm_risk_parity_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_free_cash_flow_quality`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_free_cash_flow_quality_factor_snapshot_latest.csv` |
| Manifest | `hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_free_cash_flow_quality_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_index_rebalance_event`

| Artifact | Filename |
| --- | --- |
| Event calendar snapshot | `hk_index_rebalance_event_event_calendar_snapshot_latest.csv` |
| Manifest | `hk_index_rebalance_event_event_calendar_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_index_rebalance_event_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_low_vol_dividend_quality`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_low_vol_dividend_quality_factor_snapshot_latest.csv` |
| Manifest | `hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_low_vol_dividend_quality_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_quality_growth_low_volatility`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_quality_growth_low_volatility_factor_snapshot_latest.csv` |
| Manifest | `hk_quality_growth_low_volatility_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_quality_growth_low_volatility_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_liquid_momentum_quality`

| Artifact | Filename |
| --- | --- |
| Feature snapshot | `hk_liquid_momentum_quality_feature_snapshot_latest.csv` |
| Manifest | `hk_liquid_momentum_quality_feature_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_liquid_momentum_quality_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_residual_momentum_quality`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_residual_momentum_quality_factor_snapshot_latest.csv` |
| Manifest | `hk_residual_momentum_quality_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_residual_momentum_quality_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_shareholder_yield_quality`

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_shareholder_yield_quality_factor_snapshot_latest.csv` |
| Manifest | `hk_shareholder_yield_quality_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_shareholder_yield_quality_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

### `hk_southbound_flow_momentum`

| Artifact | Filename |
| --- | --- |
| Flow snapshot | `hk_southbound_flow_momentum_flow_snapshot_latest.csv` |
| Manifest | `hk_southbound_flow_momentum_flow_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_southbound_flow_momentum_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

## Required snapshot columns

### `hk_ah_premium_relative_value`

- `symbol`: five-digit HK H-share ticker without `.HK`, for example `03968`.
- `a_symbol`: corresponding A-share ticker, for example `600036`.
- `sector`
- `h_close_hkd`
- `a_close_cny`
- `fx_cnyhkd`
- `h_adv20_hkd`
- `h_market_cap_hkd`
- `connect_eligible_h`
- `connect_eligible_a`
- `ah_premium_pct`
- `ah_premium_percentile_3y`
- `h_mom_6m`
- `h_sma200_gap`
- `h_vol_63`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `southbound_holding_pct_change_20d`, `ah_premium_change_20d`, `h_liquidity_score`, `corporate_action_flag`.

### `hk_blue_chip_leader_rotation`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `history_days`
- `mom_3m`
- `mom_6m`
- `mom_12_1`
- `rel_mom_6m_vs_benchmark`
- `high_252_gap`
- `sma200_gap`
- `vol_63`
- `maxdd_126`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `market_cap_hkd`, `lot_size`.

### `hk_central_soe_value_quality_select`

- `symbol`: five-digit HK ticker without `.HK`, for example `00941`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `central_soe_flag`
- `government_largest_shareholder`
- `government_ownership_pct`
- `value_score`
- `quality_score`
- `low_volatility_score`
- `momentum_score`
- `dividend_yield_net`
- `earnings_yield`
- `book_to_price`
- `roe_ttm`
- `debt_to_equity`
- `realized_vol_252`
- `beta_252`
- `maxdd_252`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `southbound_eligible`, `lot_size`, `government_shareholder_type`, `policy_event_risk_flag`, `corporate_action_flag`.

### `hk_composite_factor_quality_value_momentum`

- `symbol`: five-digit HK ticker without `.HK`, for example `00941`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `roe_ttm`
- `earnings_variability_3y`
- `debt_to_equity`
- `book_to_price`
- `earnings_yield`
- `free_cash_flow_yield`
- `mom_12m_to_high`
- `realized_vol_252`
- `beta_252`
- `maxdd_252`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `dividend_yield_net`, `southbound_eligible`, `corporate_action_flag`.

### `hk_factor_mix_qvlm_risk_parity`

- `symbol`: five-digit HK ticker without `.HK`, for example `00941`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `quality_score`
- `value_score`
- `momentum_score`
- `low_volatility_score`
- `quality_factor_vol_126`
- `value_factor_vol_126`
- `momentum_factor_vol_126`
- `low_vol_factor_vol_126`
- `realized_vol_252`
- `beta_252`
- `maxdd_252`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `southbound_eligible`, `lot_size`, `corporate_action_flag`.

### `hk_free_cash_flow_quality`

- `symbol`: five-digit HK ticker without `.HK`, for example `00941`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `free_cash_flow_hkd`
- `enterprise_value_hkd`
- `free_cash_flow_yield`
- `roe_ttm`
- `revenue_growth_ttm`
- `realized_vol_252`
- `maxdd_252`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `southbound_eligible`, `corporate_action_flag`, `earnings_yield`, `debt_to_equity`, `fcf_yield_percentile_3y`.

### `hk_index_rebalance_event`

- `symbol`: five-digit HK ticker without `.HK`, for example `03750`.
- `index_family`
- `review_cycle`
- `data_cutoff_date`
- `announcement_date`
- `effective_date`
- `event_side`
- `predicted_add_probability`
- `predicted_remove_probability`
- `official_add_flag`
- `official_remove_flag`
- `days_to_effective`
- `event_liquidity_score`
- `estimated_slippage_bps`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `post_announcement_momentum_5d`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `sector`, `lot_size`, `index_weight_estimate`, `proforma_weight_estimate`, `review_result_source_uri`, `schedule_file_version`, `press_release_timestamp`, `moc_vs_next_open_ablation_bucket`, `closing_auction_imbalance_hkd`, `order_rejection_risk_flag`, `crowding_score`, `corporate_action_flag`.

### `hk_low_vol_dividend_quality`

- `symbol`: five-digit HK ticker without `.HK`, for example `00941`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `dividend_yield_net`
- `dividend_stability_3y`
- `earnings_positive`
- `payout_ratio`
- `realized_vol_126`
- `beta_252`
- `maxdd_252`
- `mom_6m`
- `mom_12_1`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `pe_ratio`, `free_cash_flow_yield`, `realized_vol_252`, `corporate_action_flag`.

### `hk_quality_growth_low_volatility`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `southbound_eligible`
- `roe`
- `accruals_ratio`
- `cash_flow_to_debt_ratio`
- `growth_roa_to_pb`
- `realized_vol_252`
- `beta_252`
- `maxdd_252`
- `mom_6m`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `quality_growth_score`, `roe_zscore`, `accruals_zscore`, `cash_flow_to_debt_zscore`, `growth_roa_to_pb_zscore`, `negative_equity_flag`, `financials_sector_flag`, `missing_factor_policy`, `corporate_action_flag`.

### `hk_liquid_momentum_quality`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `history_days`
- `mom_3m`
- `mom_6m`
- `mom_12_1`
- `rel_mom_6m_vs_benchmark`
- `high_252_gap`
- `sma200_gap`
- `vol_63`
- `maxdd_126`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `market_cap_hkd`, `lot_size`, `high_63_gap`, `suspension_days_63`, `corporate_action_flag`.

### `hk_residual_momentum_quality`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `history_days`
- `mom_3m`
- `mom_6m`
- `mom_12_1`
- `residual_mom_12_1`
- `industry_relative_mom_6m`
- `rel_mom_6m_vs_benchmark`
- `high_252_gap`
- `sma200_gap`
- `realized_vol_126`
- `beta_252`
- `maxdd_252`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `high_63_gap`, `lot_size`, `southbound_eligible`, `corporate_action_flag`.

### `hk_shareholder_yield_quality`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `market_cap_hkd`
- `dividend_yield_net`
- `buyback_yield_12m`
- `net_payout_yield`
- `free_cash_flow_yield`
- `roe_ttm`
- `debt_to_equity`
- `realized_vol_252`
- `maxdd_252`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `lot_size`, `southbound_eligible`, `corporate_action_flag`, `share_count_change_12m`, `payout_ratio`, `earnings_yield`, `treasury_share_ratio`, `buyback_days_63`.

### `hk_southbound_flow_momentum`

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `southbound_eligible`
- `southbound_net_buy_hkd_5d`
- `southbound_net_buy_hkd_20d`
- `southbound_net_buy_hkd_60d`
- `southbound_turnover_share_20d`
- `southbound_holding_pct`
- `southbound_holding_pct_change_20d`
- `southbound_holding_pct_change_60d`
- `flow_zscore_20d`
- `flow_persistence_score`
- `mom_6m`
- `sma200_gap`
- `suspension_days_63`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `market_cap_hkd`, `lot_size`, `holiday_adjusted_flow_flag`, `corporate_action_flag`.

## Future snapshot candidate backlog

Research-only candidate contracts are tracked in `docs/research/hk_snapshot_strategy_candidates.md`.
The current scaffolded promotion order is machine-readable in `hkeq-print-snapshot-promotion-matrix --json` and starts with the lower-turnover quality/yield candidates:

1. `hk_low_vol_dividend_quality` - scaffolded contract and ranking helper added; live-enable source audit now also requires forecast-dividend-yield estimate history, forecast-versus-trailing-yield ablation, stale estimate-revision controls, HSHYLV/HSSCHYS-style Southbound, large/mid-cap shortlist, three-year cash-dividend, payout-ratio, high-volatility-exclusion, financial-soundness, S&P Access HK Low Volatility High Dividend reconciliation, and price-crash-screen evidence; still not production/live.
2. `hk_shareholder_yield_quality` - scaffolded dividend/buyback shareholder-yield quality contract and ranking helper added; live-enable source audit now also requires forecast-dividend-yield estimate history, forecast-versus-trailing-yield ablation, stale estimate-revision / financials-sector concentration controls, HKEX share-repurchase reports, next-day repurchase returns, share-count and treasury-share treatment, moratorium/blackout controls, and post-buyback financing / public-float review; still not production/live.
3. `hk_free_cash_flow_quality` - scaffolded FCF-quality contract and ranking helper added; live-enable source audit now also requires HSI/S&P-style FCF formula, EV market-cap/debt/cash/FX inputs, point-in-time reporting-date/restatement handling, sector-normalization/concentration, and financial/real-estate/negative-FCF exception evidence; still not production/live.
4. `hk_quality_growth_low_volatility` - scaffolded quality-growth low-volatility contract and ranking helper added; live-enable source audit now also requires HSI QGLV four-component score lineage (ROE, accruals ratio, cash-flow-to-debt, Growth in ROA adjusted by P/B), winsorized z-score / component-averaging / Financials / negative-equity / missing-factor handling, MSCI quality ROE / stable-earnings / low-leverage reconciliation, HSI low-volatility quality screen, minimum-volatility optimizer constraints, cash-conversion / accrual quality-trap controls, sector concentration, Southbound universe capacity, and growth-deceleration / valuation / low-vol crowding stress; still not production/live.
5. `hk_factor_mix_qvlm_risk_parity` - scaffolded QVLM risk-parity factor-mix contract and ranking helper added; live-enable source audit now also requires HSI QVLM parent Large-Mid Cap Investable universe, Quality/Value/Low Volatility/Momentum component-index return history, risk-parity weight / 12% cap lineage, HSI equal-weight factor-mix benchmark comparison, MSCI Factor Mix A-Series component-index equal-weight and capped-methodology controls, factor covariance/correlation history, factor-score winsorization, component overlap, sector/single-name cap, turnover/capacity/crowding evidence, and factor-correlation breakdown stress; still not production/live.
6. `hk_central_soe_value_quality_select` - scaffolded central-SOE value-quality contract and ranking helper added; live-enable source audit now also requires SASAC/MOF source-list effective-date drift, largest-shareholder look-through, HSI factor Z-score / missing-measure / 40% screening / buffer-rule lineage, 5% factor-index and 10% base-index cap evidence, Southbound eligibility, connected-transaction/public-float/dividend-policy review, and policy/cap-turnover stress; still not production/live.
7. `hk_residual_momentum_quality` - scaffolded residual / industry-neutral momentum contract and ranking helper added; live-enable source audit now also requires HSI close-to-high descriptor and MSCI 6/12-month one-month-skip risk-adjusted momentum reconciliation, residual model-fit-window audit, volatility normalization, sector neutralization, turnover buffers, and momentum-crash controls; still not production/live.
8. `hk_liquid_momentum_quality` - scaffolded momentum contract and ranking helper added; live-enable source audit now also requires HSI/MSCI momentum descriptor reconciliation, volatility normalization, high-watermark / 12-1 / 6-12 month comparison, hold-buffer turnover control, liquidity capacity, and high-beta reversal stress; still not production/live.
9. `hk_composite_factor_quality_value_momentum` - scaffolded multi-factor contract and ranking helper added; live-enable source audit now also requires Q/V/M/L factor formula lineage, momentum-sleeve ablation, factor score winsorization/neutralization, MSCI/HSI momentum descriptor reconciliation, and factor-turnover capacity controls; still not production/live.
10. `hk_southbound_flow_momentum` - scaffolded flow contract and ranking helper added; live-enable source audit now also requires HKEX historical daily turnover, top-10 active-stock turnover, CCASS Southbound shareholding percent-issued history, point-in-time eligible-security lists, market-data dissemination change controls, and raw-vs-vendor reconciliation; still not production/live.
11. `hk_ah_premium_relative_value` - scaffolded valuation contract and ranking helper added; live-enable source audit now also requires AH pair/index-constituent history, AH price-ratio formula and adjusted-market-cap/FX lineage, AH Smart share-class-switch threshold validation, extreme-premium false-reversal stress, and A-share access / shorting / settlement constraint review; still not production/live.
12. `hk_blue_chip_leader_rotation` - baseline scaffold kept for artifact contract plumbing; still not a preferred live candidate.
13. `hk_index_rebalance_event` - scaffolded event-calendar contract and ranking helper added; live-enable source audit now also requires HSI methodology / operation-guide versioning, schedule-file version / effective-date history, next-review notice scope, review-result press-release timestamps, constituent weight / pro-forma records, add/delete effective-date labels, MOC-vs-next-open and pro-forma-weighted-vs-equal-weight ablations, fast-entry / suspension / buffer-rule exception handling, and HKEX CAS random-close / two-stage price-limit / order-rejection / passive-flow imbalance controls; still not production/live.

The matrix also exposes `backtest_validation_policy` for all HK snapshot and runtime strategy candidates. It sets a hard max-drawdown ceiling of 30% unless a profile-specific threshold is stricter, and requires point-in-time inputs, no look-ahead / survivorship bias, pre-registered small parameter grids, walk-forward or OOS evidence, multi-period robustness, benchmark alignment, HK cost/slippage/lot-size/suspension handling, and capacity controls before any live enablement.

The matrix also exposes `future_research_backlog` for non-scaffolded ideas found during external research. The backlog currently contains research-only `hk_earnings_revision_quality_overlay`, `hk_low_size_quality_liquidity_premium`, `hk_stock_connect_inclusion_event_flow`, `hk_short_selling_pressure_risk_overlay`, `hk_director_dealing_disclosure_quality_overlay`, `hk_dually_traded_liquid_reversal_overlay`, and `hk_earnings_announcement_drift_overlay`; they need point-in-time consensus estimate/revision, free-float market-cap/size-factor, Stock Connect eligibility-change, designated short-selling / short-turnover history, or disclosed SFC/HKEX Disclosure of Interests / director-dealing notice history, analyst coverage, HSICS/quality-screen, official eligible-security methodology, HKEX regulated-short-selling controls, filing-lag / correction / blackout / moratorium context, dual-listing mapping / foreign-close / FX alignment / reversal-cost controls, HKEXnews announcement / profit-warning / earnings-surprise timestamp history, same-universe ablation, walk-forward evidence, dry-run order previews, bilingual notifications, rollout controls, and operator approval before any scaffold can be created. New external research hints must still use a new profile name and new contract version if promoted later; do not add their fields to an existing contract without an explicit migration.

## Runtime mapping

- IBKR should use `SEHK` + `HKD` for contracts and `.HK` only for yfinance fallback.
- LongBridge should use `.HK` market-data symbols and `HKD` cash reporting.
- Both platforms should point their feature snapshot and manifest env vars to the published files above.

Before selecting any snapshot-backed strategy for promotion, print the machine-readable promotion matrix. It ties each contract to its research evidence, production data dependencies, threshold caps, next evidence gates, recommended live-enable stage, and next live-enable action:

```bash
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --json
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --profile hk_shareholder_yield_quality --json
```

The matrix also exposes `recommended_live_enablement_sequence`, `momentum_live_enablement_comparison`, `momentum_live_enablement_policy`, `quality_growth_live_enablement_policy`, `factor_mix_live_enablement_policy`, `policy_value_live_enablement_policy`, `future_research_backlog`, `production_source_audit_policy` with source coverage and stable production-source / quality-report URI requirements, `artifact_provenance_policy`, `evidence_uri_policy`, `evidence_freshness_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `notification_audit_policy`, and `rollout_risk_policy`, so platform switch-plan tooling can preserve the intended promotion order, compare residual/liquid/composite momentum candidates before treating any of them as live momentum evidence, require profile-specific production data-source proof, display the suggested first-party source references, and enforce immutable artifact provenance, stable `https://`, `gs://`, or `s3://` evidence URIs, section-level freshness, quality/yield HSHYLV/HSSCHYS-style, S&P Access HK Low Volatility High Dividend reconciliation, HKEX buyback/treasury-share, and HSI/S&P FCF formula/EV/restatement/sector-exception source-audit fields, quality-growth HSI QGLV four-factor / z-score / missing-factor / low-vol-quality-screen lineage, factor-mix HSI QVLM component-index / MSCI equal-weight Q/V/L / capping provenance, policy-value central-SOE source-list / HSI screening-capping provenance, and momentum ablation/stress tests, execution-capacity windows, raw order-preview / quote-snapshot / fee-breakdown sha256 provenance, bilingual notification delivery logs, and staged-rollout tripwires before accepting an evidence pack.

Before wiring any snapshot artifact into a platform runtime, render the readiness plan:

```bash
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_liquid_momentum_quality --platform longbridge --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality --platform ibkr --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_southbound_flow_momentum --platform longbridge --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_ah_premium_relative_value --platform ibkr --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_composite_factor_quality_value_momentum --platform longbridge --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_free_cash_flow_quality --platform ibkr --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_residual_momentum_quality --platform longbridge --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_shareholder_yield_quality --platform ibkr --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --profile hk_index_rebalance_event --platform longbridge --json
PYTHONPATH=src python scripts/print_snapshot_readiness.py --all --platform longbridge --json
```

The current readiness status is `architecture_scaffold_not_live_enabled` for every snapshot profile. The plan includes generic and profile-specific live-enable requirements; it is a checklist and blocking report, not a deployment command.
The `--all` matrix is the preferred pre-switch gate because it confirms every scaffold remains blocked until production evidence is available. Readiness output, the live-enable evidence template, and the validation result also include `production_source_audit_policy.required_boolean_fields`, `production_source_audit_policy.source_reference_urls`, `artifact_provenance_policy`, `evidence_uri_policy`, `evidence_freshness_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `rollout_risk_policy`, and `notification_audit_policy` so platform tooling can reject missing production data-source proof, missing artifact publication provenance, unstable evidence links, stale audit/backtest/dry-run evidence, over-capacity dry-run order previews, missing dry-run order-preview artifact provenance, missing bilingual notification delivery-log proof, or missing staged-rollout/rollback controls before accepting an evidence pack.

Before a platform runtime consumes a published artifact directory, validate the contract pack:

```bash
hkeq-validate-snapshot-artifact-pack --profile hk_low_vol_dividend_quality --artifact-dir <published-artifact-dir> --json
```

The validator fails when any required file is missing or when manifest `strategy_profile`, `contract_version`, `snapshot_sha256`, or `row_count` no longer matches the declared contract and actual snapshot file.

The final promotion gate is a live-enable evidence pack:

```bash
hkeq-validate-live-enable-evidence --print-template --profile hk_low_vol_dividend_quality --platform longbridge --json > live-enable-evidence.json
hkeq-validate-live-enable-evidence --evidence-file <live-enable-evidence.json> --json
```

This validator requires production source audit, artifact-pack validation and publication provenance, walk-forward out-of-sample backtest, platform dry-run order preview, broker permission/fee verification, the required rebalance/event windows, runtime rollout plan, and operator approval. The template and validation result expose the shared `production_source_audit_policy`, `artifact_provenance_policy`, `evidence_uri_policy`, `evidence_freshness_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `rollout_risk_policy`, and `notification_audit_policy`. It rejects missing production source coverage/provenance fields, missing stable production source / quality-report / data-dictionary URIs, missing profile-specific source-audit fields, missing immutable artifact release identity, missing published snapshot/manifest/ranking/release-summary URIs, invalid snapshot sha256, row-count/contract-version mismatch, sample artifact proof gaps, backtests with max drawdown above 30%, non-positive annual return, less than three out-of-sample years, non-positive excess return versus the required profile benchmark, annualized turnover above the profile cap, missing HK cost-model flags, missing survivorship/look-ahead bias controls, missing section-level stable `evidence_uri` (`https://`, `gs://`, or `s3://`), missing/stale/future-dated section-level `evidence_generated_at`, missing/over-limit ADV capacity evidence, missing HK board-lot / odd-lot / session-routing / VCM controls, missing dry-run session id, missing stable raw order-preview / quote-snapshot / fee-breakdown artifact URI and sha256 provenance, missing non-sample/redaction/quote-coverage/broker-fee-reconciliation/strategy-decision-reconciliation proof, missing bilingual notification audit fields (`hk_snapshot_live_enablement_dry_run`, EN/ZH-Hans locales, correlation id, redaction, stable delivery-log URI), missing staged-rollout / tripwire / kill-switch / SWT-runbook controls, secret-like query parameters in evidence URIs, missing `risk_approval.approval_reference`, or insufficient paper/dry-run windows.
