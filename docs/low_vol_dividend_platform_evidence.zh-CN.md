# 港股低波股息质量平台 Evidence 草稿

[English version](./low_vol_dividend_platform_evidence.md)

该工具把平台 dry-run runtime report 转成 `hk_low_vol_dividend_quality_snapshot` 的 `platform_dry_run_order_preview` evidence 草稿。
支持 LongBridge 和 IBKR。
IBKR 在 CLI 中使用 `--platform ibkr`，同时兼容 runtime report 顶层 `platform` 为 `ibkr` 或平台运行时 ID `interactive_brokers`。

该命令不会部署 Cloud Run、不会下单、不会上传 artifact，也不会批准 live trading。
在 production source、artifact、backtest、broker permission、rebalance window、rollout、risk approval 和 strategy-policy evidence 全部补齐前，完整 evidence pack 仍会保持 blocked。

## 使用方式

推荐从真实平台 dry-run runtime report 直接一条命令生成平台 convention evidence：

```bash
python scripts/draft_low_vol_dividend_platform_evidence_from_runtime.py \
  --platform longbridge \
  --runtime-report runtime-report.json \
  --runtime-report-uri gs://.../runtime-report.json \
  --quote-snapshot-uri gs://.../quotes.json \
  --fee-breakdown-uri gs://.../fees.json \
  --notification-delivery-log-uri gs://.../notification-log.json \
  --adv-window-trading-days 20 \
  --median-daily-turnover-hkd 50000000 \
  --max-single-order-adv-fraction 0.01 \
  --rebalance-adv-fraction 0.05 \
  --confirm-order-preview-provenance \
  --confirm-notification-audit \
  --confirm-execution-capacity \
  --evidence-generated-at 2026-06-03 \
  --evidence-dir evidence/low_vol_dividend_quality \
  --json
```

该命令会把 support artifacts 写到 `evidence/low_vol_dividend_quality/support/<platform>/`，并生成约定文件
`evidence/low_vol_dividend_quality/<platform>_live_enablement_evidence.draft.json`。
如果 quote、fee、notification、capacity 或确认项证据缺失，平台 section 仍会保持 `pending`。

手动两步流程：

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

collector 会写出 `raw_order_preview`、`quote_snapshot`、`fee_breakdown` 和 `notification_delivery_log` support files。
它不会伪造缺失证据：只有 runtime report 已包含完整 payload，或在支持时显式提供外部 broker/runtime JSON 文件时，生成的 quote、fee 或 notification 文件才会标记为 `passed`；否则标记为 `missing`。
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
  --notification-delivery-log-file notification-log.json \
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
- 提供本地 quote、fee 和 notification delivery-log 文件，用于计算 sha256 provenance；
- 如果使用生成的 support-artifact 文件，其 `status` 必须是 `passed`；
- 显式确认 order-preview provenance、notification audit 和 execution-capacity controls；
- notification delivery log 通过 schema、dry-run correlation id、中英文双语（`en` 和 `zh-Hans`）、profile、platform、validation status、order-preview summary 和敏感字段脱敏检查。

即使平台 dry-run section 为 `passed`，只要其他 live-enable evidence gate 未补齐，完整 evidence 文件仍可能无法通过校验。

## Notification delivery log 格式

使用 secret-safe JSON object。平台 evidence 草稿会校验该文件，不再只依赖确认 flag：

```json
{
  "notification_schema_version": "hk_live_enablement_notification.v1",
  "notification_event_type": "hk_snapshot_live_enablement_dry_run",
  "notification_correlation_id": "run-001",
  "locales": ["en", "zh-Hans"],
  "profile": "hk_low_vol_dividend_quality_snapshot",
  "platform": "longbridge",
  "validation_status": "passed",
  "orders_previewed": 2,
  "notification_redacts_sensitive_fields": true,
  "messages": {
    "en": "HK low-vol dividend quality dry-run preview passed with 2 orders.",
    "zh-Hans": "港股低波股息质量 dry-run 订单预览已通过，共 2 笔订单。"
  }
}
```

不要在 delivery log 中包含 token、Cookie、API key、账号 ID 或订单账号标识。如果诊断字段必须提到敏感 key 名称，对应值必须脱敏。
