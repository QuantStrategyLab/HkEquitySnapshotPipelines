# First HK Snapshot Evidence Tools

[Chinese version](./first_snapshot_evidence_tools.zh-CN.md)

The shared first-snapshot evidence tools now support only the retained candidate:

1. `hk_low_vol_dividend_quality_snapshot`

Removed snapshot scaffolds are not supported by these commands. Reopen a removed profile only through a new research PR and fresh long / medium / short backtests.

## Commands

Build the live-enable package template:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

Build the evidence bundle template:

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --json
```

Draft production-source audit evidence from an operator-reviewed factor snapshot:

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_production_source_audit.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --source-name operator-prod-source \
  --evidence-generated-at 2026-06-03 \
  --json
```

Draft walk-forward backtest evidence from a summary JSON:

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_backtest_evidence.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --summary walk_forward_summary.json \
  --evidence-generated-at 2026-06-03 \
  --json
```

The generated drafts stay `pending`; they do not approve live trading.
