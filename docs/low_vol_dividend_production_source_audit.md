# HK Low-Vol Dividend Production Source Audit Draft

[中文版本](./low_vol_dividend_production_source_audit.zh-CN.md)

This tool starts the real-evidence phase for `hk_low_vol_dividend_quality_snapshot`.
It checks an operator-supplied factor snapshot CSV for local schema quality and creates a pending production source audit draft.

It does not prove point-in-time lineage by itself, does not mark the source audit as passed, and does not live-enable the strategy.

## Command

```bash
python scripts/draft_low_vol_dividend_production_source_audit.py \
  --factor-snapshot <production-factor-snapshot.csv> \
  --source-name <audited-source-name> \
  --production-source-uri gs://.../source.csv \
  --source-quality-report-uri gs://.../quality.json \
  --point-in-time-data-dictionary-uri gs://.../dictionary.json \
  --evidence-uri gs://.../source-audit.json
```

The command writes:

- `production_source_audit.draft.json`
- `source_quality_summary.json`

under `data/output/low_vol_dividend_production_source_audit`.

## Important boundary

The generated evidence remains `status: pending`.
An operator must still attach immutable evidence proving point-in-time inputs, no survivorship bias, adjusted prices, corporate actions, suspensions, dividend history, forecast dividend yield history, yield-trap controls, and Southbound eligibility before the live-enable validator can pass.
