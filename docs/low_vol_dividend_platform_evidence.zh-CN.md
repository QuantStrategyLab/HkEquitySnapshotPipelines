# 港股低波股息质量平台 Evidence 草稿

[English version](./low_vol_dividend_platform_evidence.md)

该工具把平台 dry-run runtime report 转成 `hk_low_vol_dividend_quality` 的 `platform_dry_run_order_preview` evidence 草稿。
支持 LongBridge 和 IBKR。
IBKR 在 CLI 中使用 `--platform ibkr`，同时兼容 runtime report 顶层 `platform` 为 `ibkr` 或平台运行时 ID `interactive_brokers`。

该命令不会部署 Cloud Run、不会下单、不会上传 artifact，也不会批准 live trading。
在 production source、artifact、backtest、broker permission、rebalance window、rollout、risk approval 和 strategy-policy evidence 全部补齐前，完整 evidence pack 仍会保持 blocked。

## 使用方式

先从真实平台 dry-run runtime report 收集 support artifacts：

```bash
python scripts/collect_low_vol_dividend_dry_run_support_artifacts.py \
  --platform longbridge \
  --runtime-report runtime-report.json \
  --quote-snapshot-file broker-quotes.json \
  --fee-breakdown-file broker-fees.json \
  --evidence-generated-at 2026-06-03 \
  --output-dir evidence/low_vol_dividend_quality/support \
  --json
```

collector 会写出 `raw_order_preview`、`quote_snapshot` 和 `fee_breakdown` support files。
它不会伪造缺失证据：只有 runtime report 已包含完整 payload，或显式提供外部 broker/runtime JSON 文件时，生成的 quote 或 fee 文件才会标记为 `passed`；否则标记为 `missing`。
后续即使传入确认 flags，`missing` support artifact 也会让平台 evidence section 保持 `pending`。

然后再生成平台 evidence：

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
- 如果使用生成的 support-artifact 文件，其 `status` 必须是 `passed`；
- 显式确认 order-preview provenance、notification audit 和 execution-capacity controls。

即使平台 dry-run section 为 `passed`，只要其他 live-enable evidence gate 未补齐，完整 evidence 文件仍可能无法通过校验。
