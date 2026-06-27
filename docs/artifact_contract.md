# HK Equity Snapshot Artifact Contract

## Active profile

### `hk_low_vol_dividend_quality_snapshot`

> Current status: retained first HK snapshot candidate. It is still evidence-gated and not approved for live order submission by this repository alone.

## Live-enable backtest evidence boundary

Snapshot artifacts are not sufficient for live trading by themselves. The live-enable evidence pack must include at least 3 independent out-of-sample folds, every fold's max drawdown <= 30%, overall max drawdown <= 30%, max single-period return contribution <= 60%, and annual-return-to-max-drawdown ratio >= 0.50 before platform dry-run removal can be considered.

## Files

| Artifact | Filename |
| --- | --- |
| Factor snapshot | `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv` |
| Manifest | `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_low_vol_dividend_quality_snapshot_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

## Required snapshot columns

- `symbol`: five-digit HK ticker without `.HK`, for example `00005`.
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

Optional columns include `as_of`, `snapshot_date`, `eligible`, `lot_size`, `pe_ratio`, `free_cash_flow_yield`, `realized_vol_252`, `corporate_action_flag`, and related quality/yield controls used by the retained strategy helper.

## Runtime mapping

- Strategy repo: `HkEquityStrategies`
- Runtime profile: `hk_low_vol_dividend_quality_snapshot`
- Required runtime input: `feature_snapshot`
- Manifest required by runtime: `true`
- Supported platform wiring: IBKR and LongBridge, subject to each platform's dry-run and evidence gates.

## Rejected profile policy

A removed snapshot profile must not be re-added by editing this contract in place. Reopen it only with a new research PR that includes:

- production point-in-time data source plan;
- long / medium / short backtest evidence with max drawdown <= 30%;
- same-universe ablation against the retained low-vol dividend strategy;
- HK cost, lot-size, liquidity, suspension and capacity checks;
- artifact provenance, bilingual notification evidence, rollout controls and operator approval requirements.
