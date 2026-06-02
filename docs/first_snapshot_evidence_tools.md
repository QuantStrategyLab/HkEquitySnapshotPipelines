# First HK Snapshot Evidence Tools

[中文版本](./first_snapshot_evidence_tools.zh-CN.md)

This document describes the shared evidence tooling for the first three HK snapshot candidates:

1. `hk_low_vol_dividend_quality`
2. `hk_shareholder_yield_quality`
3. `hk_free_cash_flow_quality`

These tools are intentionally evidence-gated. They do not enable live trading, deploy Cloud Run, publish production artifacts, or place broker orders.

## Scope

The tools generate the same live-enable scaffolding for all first-three profiles:

- live-enable evidence packages;
- production evidence template bundles;
- production source audit drafts;
- walk-forward backtest evidence drafts.

The existing low-vol dividend-specific commands remain available for backward compatibility. Prefer the shared first-snapshot commands when preparing the first-three candidate evidence set.

## Generate live-enable evidence packages

Generate packages for all first-three profiles:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py
```

Generate one profile only:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py \
  --profile hk_shareholder_yield_quality \
  --platform longbridge \
  --json
```

Default output:

```text
data/output/first_snapshot_live_enablement_packages/<profile>/live_enablement_package.json
data/output/first_snapshot_live_enablement_packages/<profile>/live_enablement_package.md
```

Every package explicitly keeps:

- `runtime_enabled: false`
- `live_enablement_allowed: false`
- `production_deployment_allowed: false`
- `dry_run_only_until_all_gates_pass: true`

## Generate evidence template bundles

Generate template bundles for all first-three profiles:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py
```

Generate one profile only:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py \
  --profile hk_free_cash_flow_quality \
  --json
```

Default output:

```text
data/output/first_snapshot_evidence_bundles/<profile>/evidence_bundle.json
data/output/first_snapshot_evidence_bundles/<profile>/evidence_templates/
```

The bundles include production source, walk-forward, quality/yield strategy-policy, LongBridge, and IBKR templates.

## Draft production source audit evidence

The production source audit draft checks only local schema and basic data-quality gates. Passing the local check is not live-enable approval.

Example:

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_production_source_audit.py \
  --profile hk_free_cash_flow_quality \
  --factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv \
  --source-name operator-prod-source \
  --evidence-generated-at 2026-06-03 \
  --json
```

The tool warns if the path looks like sample data. Sample artifacts must never be used as production evidence.

Profile-specific required operational columns:

| Profile | Required operational columns |
| --- | --- |
| `hk_low_vol_dividend_quality` | `as_of`, `snapshot_date`, `eligible`, `lot_size`, `corporate_action_flag` |
| `hk_shareholder_yield_quality` | `as_of`, `eligible`, `southbound_eligible`, `lot_size`, `corporate_action_flag` |
| `hk_free_cash_flow_quality` | `as_of`, `snapshot_date`, `eligible`, `southbound_eligible`, `lot_size`, `corporate_action_flag` |

## Draft walk-forward backtest evidence

The backtest draft validates operator-supplied summary metrics against the shared live-enable gates:

- positive annual return and positive benchmark excess return;
- max drawdown and rolling OOS fold drawdown `<= 30%`;
- at least three OOS folds;
- profile turnover cap;
- aligned benchmark symbol;
- HK fees, stamp duty or exemption, slippage, board-lot, suspension, survivorship, no-lookahead, regime-stress, and capacity controls.

Example:

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_backtest_evidence.py \
  --profile hk_shareholder_yield_quality \
  --summary walk_forward_summary.json \
  --evidence-generated-at 2026-06-03 \
  --json
```

The generated evidence draft remains `status: pending` until the full walk-forward report, fold metrics, parameter sensitivity, cost model, and point-in-time/no-lookahead evidence are attached.

## Promotion gates

Before any live-enable change, each first-three profile still needs:

- point-in-time production source audit;
- no future functions and no survivorship bias;
- at least three independent OOS folds;
- max drawdown `<= 30%`;
- positive excess return after HK costs and liquidity stress;
- snapshot artifact-pack validation;
- LongBridge and IBKR dry-run order previews;
- bilingual EN/ZH-Hans notification evidence using the unified notification format;
- operator approval, tripwires, kill switch, and rollback plan.
