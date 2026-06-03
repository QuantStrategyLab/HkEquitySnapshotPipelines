# 港股低波股息质量 Live-Enable Gate Runner

[English version](./low_vol_dividend_live_enablement_gate.md)

该命令用于运行 `hk_low_vol_dividend_quality` 的端到端 evidence gate。
它会从约定目录读取 evidence 文件，分别组装 LongBridge 和 IBKR evidence pack，然后运行最终 live-enable audit。

该命令不会部署 Cloud Run、不会下单、不会发布 artifact、不会批准风险，也不会移除 dry-run 控制。
它只做本地 evidence 组装和校验。

## 文件约定

默认 evidence 目录：

```text
evidence/low_vol_dividend_quality/
```

共享文件：

```text
production_source_audit.draft.json
artifact_pack_validation.draft.json
walk_forward_backtest.draft.json
```

平台文件：

```text
longbridge_live_enablement_evidence.draft.json
longbridge_broker_permission_and_fee_verification.draft.json
longbridge_paper_or_dry_run_rebalance_window.draft.json
longbridge_runtime_rollout_plan.draft.json
longbridge_risk_approval.draft.json
longbridge_strategy_policy_evidence.draft.json

ibkr_live_enablement_evidence.draft.json
ibkr_broker_permission_and_fee_verification.draft.json
ibkr_paper_or_dry_run_rebalance_window.draft.json
ibkr_runtime_rollout_plan.draft.json
ibkr_risk_approval.draft.json
ibkr_strategy_policy_evidence.draft.json
```

## 使用方式

先从一个或多个目录预览 evidence intake，不复制任何文件：

```bash
hkeq-intake-low-vol-dividend-live-enable-evidence \
  --source-dir /path/to/operator-evidence \
  --evidence-dir evidence/low_vol_dividend_quality \
  --platform longbridge \
  --platform ibkr \
  --json
```

只有当这些文件是真实的 operator / broker / backtest evidence，且文件名符合上面的约定时，再执行复制：

```bash
hkeq-intake-low-vol-dividend-live-enable-evidence \
  --source-dir /path/to/operator-evidence \
  --evidence-dir evidence/low_vol_dividend_quality \
  --platform longbridge \
  --platform ibkr \
  --apply \
  --json
```

intake 命令只会复制符合约定命名的文件，并随后运行同一个 gate summary。它不会创建缺失证据、不会批准风险，也不会把 pending section 标记成 passed。

运行 gate：

```bash
hkeq-run-low-vol-dividend-live-enable-gate \
  --evidence-dir evidence/low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --validation-as-of 2026-06-03 \
  --output-dir data/output/low_vol_dividend_live_enablement_gate \
  --json
```

在申请 live-enable 之前，可以打印面向 operator 的 readiness checklist：

```bash
hkeq-print-low-vol-dividend-live-enable-readiness \
  --evidence-dir evidence/low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --validation-as-of 2026-06-03 \
  --json
```

readiness report 会把每个约定文件标记为 `present` 或 `missing`，展示每个平台的 validation status，并且在最终 gate 允许前保持 `ready_to_request_live_enable=false`。

输出文件：

```text
data/output/low_vol_dividend_live_enablement_gate/assembled/longbridge_live_enablement_evidence.json
data/output/low_vol_dividend_live_enablement_gate/assembled/ibkr_live_enablement_evidence.json
data/output/low_vol_dividend_live_enablement_gate/final_live_enablement_audit.json
data/output/low_vol_dividend_live_enablement_gate/live_enablement_gate_summary.json
```

summary 会包含：

- `missing_files`：未找到的约定 evidence 文件；
- `external_evidence_blockers`：每个缺失文件背后的外部证据依赖；
- `next_evidence_commands`：用于生成缺失 evidence 草稿的建议命令。

## 退出行为

默认情况下，即使 gate blocked，命令也返回 0，方便 operator 查看缺失证据和 validation errors。

如果用于 CI 或 release gate，可以加 `--fail-on-blocked`：

```bash
hkeq-run-low-vol-dividend-live-enable-gate \
  --evidence-dir evidence/low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --validation-as-of 2026-06-03 \
  --fail-on-blocked
```

## 通过规则

只有同时满足以下条件，gate 才会通过：

- 本地 artifact directory 通过 `hkeq-validate-snapshot-artifact-pack`，且 snapshot 至少包含 20 行；
- LongBridge assembled evidence 返回 `live_enablement_allowed=true`；
- IBKR assembled evidence 返回 `live_enablement_allowed=true`；
- 最终 audit 返回 `live_enablement_allowed=true`。

在最终 audit 通过前，该策略必须继续保持 blocked，不能真正 live-enable。
