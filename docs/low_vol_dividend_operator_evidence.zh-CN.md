# 港股低波股息质量 Operator Evidence 草稿

[English version](./low_vol_dividend_operator_evidence.md)

该工具为 `hk_low_vol_dividend_quality` 生成 operator 控制的 live-enable evidence section 草稿。
它覆盖 artifact validation、production-source audit、walk-forward backtest、broker dry-run runtime report 不能直接生成的部分。

该命令不会部署 Cloud Run、不会下单、不会上传 artifact、不会批准风险，也不会移除 dry-run 控制。
它只把 operator 的显式确认写成 validator 可识别的 JSON 草稿。

## Sections

该工具会按平台写出以下 draft 文件：

- `broker_permission_and_fee_verification`
- `paper_or_dry_run_rebalance_window`
- `runtime_rollout_plan`
- `risk_approval`
- `strategy_policy_evidence`

这些文件可以传给 `hkeq-assemble-low-vol-dividend-live-enable-evidence`。

## 使用方式

```bash
python scripts/draft_low_vol_dividend_operator_evidence.py \
  --platform longbridge \
  --evidence-generated-at 2026-06-03 \
  --broker-evidence-uri gs://.../longbridge/broker-permissions.json \
  --confirm-hk-market-data \
  --confirm-sehk-trading-permission \
  --confirm-hkd-cash-handling \
  --confirm-fees-verified \
  --confirm-stamp-duty-or-exemption-verified \
  --rebalance-evidence-uri gs://.../longbridge/rebalance-window.json \
  --rebalance-window-count 3 \
  --confirm-rebalance-or-event-window-covered \
  --rollout-evidence-uri gs://.../longbridge/rollout-plan.json \
  --initial-capital-fraction 0.10 \
  --per-symbol-capital-fraction 0.05 \
  --intraday-drawdown-tripwire 0.02 \
  --cumulative-drawdown-tripwire 0.04 \
  --observation-trading-days-before-scale-up 20 \
  --confirm-staged-rollout-plan \
  --confirm-kill-switch \
  --confirm-rollback-plan \
  --confirm-post-deploy-monitoring \
  --confirm-operator-notification \
  --confirm-severe-weather-trading-runbook \
  --confirm-vcm-cooling-off-handling \
  --approval-reference operator-approval://hk-low-vol-dividend-quality/20260603 \
  --confirm-operator-approved \
  --confirm-strategy-runtime-enablement-approved \
  --confirm-dry-run-removal-approved \
  --strategy-policy-evidence-uri gs://.../policy/quality-yield-policy-evidence.json \
  --confirm-all-strategy-policy-evidence \
  --output-dir evidence/operator \
  --json
```

## Strategy-policy controls

`--confirm-all-strategy-policy-evidence` 会把 quality/yield 所需的 ablation、stress-test、data-provenance controls 全部标记为已确认。
只有当 `--strategy-policy-evidence-uri` 指向完整 review pack 时才应使用该参数。

如果只是部分 review，可以通过 `--strategy-policy-controls-file` 传入 JSON object；只有显式设置为 `true` 的字段才会被标记为 true。

## 交给 assembler

```bash
hkeq-assemble-low-vol-dividend-live-enable-evidence \
  --platform longbridge \
  --validation-as-of 2026-06-03 \
  --broker-permission-file evidence/operator/longbridge_broker_permission_and_fee_verification.draft.json \
  --rebalance-window-file evidence/operator/longbridge_paper_or_dry_run_rebalance_window.draft.json \
  --runtime-rollout-file evidence/operator/longbridge_runtime_rollout_plan.draft.json \
  --risk-approval-file evidence/operator/longbridge_risk_approval.draft.json \
  --strategy-policy-evidence-file evidence/operator/longbridge_strategy_policy_evidence.draft.json
```

最终 validator 仍然是唯一权威。单个 draft 文件标记为 `passed` 不代表已经 live-enable；完整 assembled pack 必须返回 `live_enablement_allowed=true`。
