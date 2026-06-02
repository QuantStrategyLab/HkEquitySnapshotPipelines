# 港股低波股息质量平台 Evidence 草稿

[English version](./low_vol_dividend_platform_evidence.md)

该工具把平台 dry-run runtime report 转成 `hk_low_vol_dividend_quality` 的 `platform_dry_run_order_preview` evidence 草稿。
支持 LongBridge 和 IBKR。

该命令不会部署 Cloud Run、不会下单、不会上传 artifact，也不会批准 live trading。
在 production source、artifact、backtest、broker permission、rebalance window、rollout、risk approval 和 strategy-policy evidence 全部补齐前，完整 evidence pack 仍会保持 blocked。

## 使用方式

```bash
python scripts/draft_low_vol_dividend_platform_evidence.py \
  --platform longbridge \
  --runtime-report runtime-report.json \
  --runtime-report-uri gs://.../runtime-report.json \
  --quote-snapshot-file quotes.json \
  --quote-snapshot-uri gs://.../quotes.json \
  --fee-breakdown-file fees.json \
  --fee-breakdown-uri gs://.../fees.json \
  --notification-delivery-log-uri gs://.../notification-log.json \
  --notification-correlation-id run-001 \
  --orders-previewed 2 \
  --adv-window-trading-days 20 \
  --median-daily-turnover-hkd 50000000 \
  --max-single-order-adv-fraction 0.01 \
  --rebalance-adv-fraction 0.05 \
  --confirm-order-preview-provenance \
  --confirm-notification-audit \
  --confirm-execution-capacity \
  --evidence-generated-at 2026-06-03
```

如果 production source、artifact、backtest、broker permission、rollout、risk approval 和 strategy-policy sections 已经存在，可以用 `--base-evidence-file` 复制这些共享 section。

## 通过行为

只有同时满足以下条件，平台 dry-run section 才会标记为 `passed`：

- runtime report 是 `dry_run=true`、`status=ok`，并且 platform/profile 匹配；
- previewed order 数量大于 0；
- fractional-share 和 lot-size errors 都为 0；
- 提供稳定的 runtime-report、quote-snapshot、fee-breakdown 和 notification-log URI；
- 提供本地 quote 和 fee 文件，用于计算 sha256 provenance；
- 显式确认 order-preview provenance、notification audit 和 execution-capacity controls。

即使平台 dry-run section 为 `passed`，只要其他 live-enable evidence gate 未补齐，完整 evidence 文件仍可能无法通过校验。
