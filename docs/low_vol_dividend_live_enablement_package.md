# HK Low-Vol Dividend Live-Enable Evidence Package

[中文版本](./low_vol_dividend_live_enablement_package.zh-CN.md)

This document defines the first live-enable evidence package for `hk_low_vol_dividend_quality`.
It does not live-enable the strategy, deploy Cloud Run, publish production artifacts, or place broker orders.

## Why this profile first

`hk_low_vol_dividend_quality` is the first HK snapshot candidate because it is a lower-turnover quality/yield profile.
It should be easier to control drawdown, turnover, and HK execution frictions than event, AH-premium, flow, or high-turnover momentum scaffolds.

## Package command

Generate the package locally:

```bash
python scripts/build_low_vol_dividend_live_enablement_package.py
```

Print JSON without writing files:

```bash
python scripts/build_low_vol_dividend_live_enablement_package.py --json
```

The generated package writes:

- `low_vol_dividend_live_enablement_package.json`
- `low_vol_dividend_live_enablement_package.md`

under `data/output/low_vol_dividend_live_enablement_package`.

## Evidence gates

Before any live-enable change, the package requires:

- point-in-time production source audit;
- no look-ahead bias or survivorship bias;
- at least three independent OOS folds;
- max drawdown `<= 30%`;
- positive excess return after HK costs, fees, spread, slippage, board-lot, suspension, VCM, CAS, and capacity stress;
- snapshot artifact-pack validation;
- LongBridge and IBKR dry-run order previews;
- bilingual EN/ZH-Hans notification evidence using the unified notification format;
- operator approval, tripwires, kill switch, and rollback plan.

## Explicit non-live state

The package intentionally emits:

- `runtime_enabled: false`
- `live_enablement_allowed: false`
- `production_deployment_allowed: false`
- `dry_run_only_until_all_gates_pass: true`

Do not use this package to remove platform dry-run controls.
