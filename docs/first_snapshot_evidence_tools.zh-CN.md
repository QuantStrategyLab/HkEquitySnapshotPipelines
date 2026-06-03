# 首个港股 Snapshot Evidence 工具

[English version](./first_snapshot_evidence_tools.md)

共用 first-snapshot evidence 工具现在只支持保留候选：

1. `hk_low_vol_dividend_quality_snapshot`

已剔除的 snapshot scaffold 不再由这些命令支持。若要重新打开，必须通过新的 research PR，并补齐 long / medium / short 回测。

## 命令

生成 live-enable package 模板：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

生成 evidence bundle 模板：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --json
```

基于运营侧复核过的 factor snapshot 生成 production-source audit 草稿：

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_production_source_audit.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --source-name operator-prod-source \
  --evidence-generated-at 2026-06-03 \
  --json
```

基于 walk-forward summary JSON 生成回测证据草稿：

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_backtest_evidence.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --summary walk_forward_summary.json \
  --evidence-generated-at 2026-06-03 \
  --json
```

生成的草稿仍是 `pending`，不会批准实盘交易。
