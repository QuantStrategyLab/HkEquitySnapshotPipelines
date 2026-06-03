# 港股低波股息质量 Evidence 组装工具

[English version](./low_vol_dividend_evidence_assembler.md)

该工具把 section 级 evidence 草稿组装成 `hk_low_vol_dividend_quality_snapshot` 按平台区分的 live-enable evidence pack。
它是 operator 采集证据之后、执行最终 `hkeq-validate-live-enable-evidence` / `hkeq-audit-low-vol-dividend-live-enable` 之前的交接点。

该命令不会部署 Cloud Run、不会下单、不会上传 artifact、不会合并审批，也不会移除 dry-run 控制。
它只写出 evidence JSON、validation JSON 和一个精简 summary 文件。

## 输入

组装工具会从 `hk_low_vol_dividend_quality_snapshot` 标准 live-enable template 开始，并可合并以下文件：

- production source audit：`--production-source-audit-file`
- artifact-pack validation：`--artifact-pack-validation-file`
- walk-forward backtest：`--walk-forward-backtest-file`
- platform dry-run order preview：`--platform-dry-run-file`
- broker permission and fee verification：`--broker-permission-file`
- paper/dry-run rebalance window：`--rebalance-window-file`
- runtime rollout plan：`--runtime-rollout-file`
- risk approval：`--risk-approval-file`
- quality/yield strategy-policy evidence：`--strategy-policy-evidence-file`

每个输入可以是：

- 直接的 section object；
- 草稿工具输出的 wrapper，例如 `artifact_pack_validation_draft` 或 `walk_forward_backtest_draft`；
- `evidence` key 下的完整 evidence 文件。

`--base-evidence-file` 可以先从已有 assembled pack 复制所有已知 section，再由 section-specific 文件覆盖。

## 使用方式

```bash
python scripts/assemble_low_vol_dividend_live_enablement_evidence.py \
  --platform longbridge \
  --validation-as-of 2026-06-03 \
  --production-source-audit-file evidence/production_source_audit.json \
  --artifact-pack-validation-file evidence/artifact_pack_validation.json \
  --walk-forward-backtest-file evidence/walk_forward_backtest.json \
  --platform-dry-run-file evidence/longbridge_platform_dry_run.json \
  --broker-permission-file evidence/longbridge_broker_permissions.json \
  --rebalance-window-file evidence/longbridge_rebalance_window.json \
  --runtime-rollout-file evidence/longbridge_rollout_plan.json \
  --risk-approval-file evidence/risk_approval.json \
  --strategy-policy-evidence-file evidence/quality_yield_strategy_policy.json \
  --output-dir evidence/assembled \
  --json
```

输出文件：

- `longbridge_live_enablement_evidence.json`
- `longbridge_live_enablement_evidence.validation.json`
- `longbridge_live_enablement_evidence.assembly_summary.json`

IBKR 需要用 `--platform ibkr` 和 IBKR 对应 dry-run / broker evidence 再执行一次。

## 退出行为

默认情况下，即使 assembled pack 仍然 blocked，命令也返回 0。这样 operator 可以安全生成未完成草稿并查看 validation errors。

如果用于 CI 或 release gate，需要 blocked 时返回非 0，可以加 `--fail-on-blocked`。

## Live-enable 规则

只有最终 validator 返回以下结果时，assembled evidence pack 才具备 live-enable 资格：

```json
{
  "validation_status": "passed",
  "live_enablement_allowed": true
}
```

在此之前，平台 dry-run 控制和生产部署保护都必须保留。
