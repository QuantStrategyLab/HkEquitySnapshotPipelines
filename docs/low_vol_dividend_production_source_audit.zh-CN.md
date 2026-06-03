# 港股低波红利生产数据源审计草稿

[English version](./low_vol_dividend_production_source_audit.md)

该工具用于启动 `hk_low_vol_dividend_quality_snapshot` 的真实 evidence 阶段。
它会检查 operator 提供的 factor snapshot CSV 的本地 schema 质量，并生成 pending 状态的 production source audit 草稿。

它本身不能证明 point-in-time lineage，不会把 source audit 标记为 passed，也不会 live-enable 策略。

## 命令

```bash
python scripts/draft_low_vol_dividend_production_source_audit.py \
  --factor-snapshot <production-factor-snapshot.csv> \
  --source-name <audited-source-name> \
  --production-source-uri gs://.../source.csv \
  --source-quality-report-uri gs://.../quality.json \
  --point-in-time-data-dictionary-uri gs://.../dictionary.json \
  --evidence-uri gs://.../source-audit.json
```

该命令会写入：

- `production_source_audit.draft.json`
- `source_quality_summary.json`

目录为 `data/output/low_vol_dividend_production_source_audit`。

## 重要边界

生成的 evidence 仍然是 `status: pending`。
Operator 仍必须补齐 immutable evidence，用于证明 point-in-time input、无幸存者偏差、调整后价格、corporate actions、停牌、dividend history、forecast dividend yield history、yield-trap controls 和 Southbound eligibility，之后 live-enable validator 才可能通过。
