# HK Snapshot Strategy Candidate Ranking

> Research note only. This is not investment advice and does not approve live trading.

## Decision

The package keeps only one HK snapshot strategy contract:

1. `hk_low_vol_dividend_quality_snapshot`

All other previous snapshot scaffolds were removed from package entrypoints and active contracts. They remain listed here only as rejected research decisions so future work does not reopen weak ideas without new evidence.

## Proxy cycle triage

Selection rule used for this pruning pass:

- long / medium / short windows must stay within the 30% max-drawdown gate;
- strategy should be explainable and low-turnover enough for HK costs, board lots, suspensions, VCM/CAS and liquidity constraints;
- production data assumptions must be realistic for point-in-time artifact publication;
- passing a proxy test alone is not enough for live enablement.

| Rank | Profile | Long ann. return | Long max DD | Medium ann. return | Medium max DD | Short ann. return | Short max DD | Decision |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `hk_low_vol_dividend_quality_snapshot` | 13.34% | -23.05% | 23.24% | -11.12% | 12.21% | -10.59% | **Retain** as the only active snapshot contract. |
| 2 | `hk_quality_growth_low_volatility` | 10.06% | -27.98% | 25.00% | -12.23% | 21.06% | -10.53% | Reject from package surface for now: proxy passed, but production point-in-time fundamentals, same-universe ablation and live evidence are missing. |
| 3 | `hk_factor_mix_qvlm_risk_parity` | 11.65% | -30.86% | 23.25% | -20.74% | 18.51% | -9.73% | Reject: long-cycle drawdown exceeds 30%. |
| 4 | `hk_shareholder_yield_quality` | 9.83% | -35.82% | 24.74% | -19.21% | 30.68% | -13.70% | Reject: long-cycle drawdown exceeds 30%. |
| 5 | `hk_liquid_momentum_quality` | 16.42% | -35.86% | 26.96% | -23.71% | 11.09% | -17.41% | Reject: long-cycle drawdown exceeds 30% and HK momentum crash risk is high. |
| 6 | `hk_ah_premium_relative_value` | 10.47% | -34.87% | 22.36% | -14.09% | 9.76% | -12.91% | Reject: long-cycle drawdown exceeds 30%; A/H data, FX, access and shorting assumptions are too complex. |
| 7 | `hk_blue_chip_leader_rotation` | 17.15% | -44.09% | 31.46% | -23.17% | 27.64% | -9.81% | Reject: excessive long-cycle drawdown. |
| 8 | `hk_residual_momentum_quality` | 13.66% | -35.84% | 19.21% | -25.06% | 7.78% | -18.89% | Reject: long-cycle drawdown exceeds 30%. |
| 9 | `hk_composite_factor_quality_value_momentum` | 15.05% | -38.21% | 23.84% | -20.47% | 6.52% | -17.04% | Reject: long-cycle drawdown exceeds 30%. |
| 10 | `hk_free_cash_flow_quality` | 11.78% | -39.31% | 22.83% | -26.51% | 13.66% | -10.75% | Reject: long-cycle drawdown exceeds 30%. |
| 11 | `hk_index_rebalance_event` | 6.75% | -47.61% | 24.49% | -18.58% | 32.55% | -12.66% | Reject: excessive drawdown and event execution/crowding risk. |
| 12 | `hk_southbound_flow_momentum` | 12.54% | -48.19% | 21.63% | -18.68% | 7.50% | -8.95% | Reject: excessive drawdown and data/flow crowding risk. |
| 13 | `hk_central_soe_value_quality_select` | 12.24% | -52.01% | 8.84% | -29.54% | 4.10% | -12.08% | Reject: excessive drawdown and sector/policy concentration risk. |

## Retained strategy

### `hk_low_vol_dividend_quality_snapshot`

Rationale:

- passed the proxy 30% max-drawdown gate in long, medium and short windows;
- defensive low-volatility plus dividend-quality style is easier to explain and audit than high-turnover momentum or event strategies;
- monthly cadence and quality/yield inputs are more compatible with HK costs, liquidity and lot-size constraints;
- already has artifact builder, contract, evidence tools and runtime adapter separation with `HkEquityStrategies`.

Still required before live order submission:

- production point-in-time factor source audit;
- survivorship-safe walk-forward backtest with at least 3 independent OOS folds;
- HK fees, stamp duty, spread, lot-size, suspension, VCM/CAS and capacity model;
- artifact-pack validation with stable URI and sha256 provenance;
- IBKR / LongBridge dry-run order previews;
- bilingual notification and delivery-log evidence;
- rollout controls, kill switch, rollback plan and operator approval.

## Reopen policy for rejected profiles

A rejected profile must not be re-added by restoring an old builder file. Reopen only with a new research PR that includes:

1. a new profile/contract proposal;
2. production data-source design and point-in-time controls;
3. long / medium / short backtest evidence with max drawdown <= 30%;
4. same-universe ablation against `hk_low_vol_dividend_quality_snapshot`;
5. HK cost, liquidity, lot-size, suspension and capacity stress tests;
6. evidence plan for artifact provenance, dry-run order previews, bilingual notifications, rollout and approval.
