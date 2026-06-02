# HK Low-Volatility Dividend Quality Operator Evidence Draft

[中文版本](./low_vol_dividend_operator_evidence.zh-CN.md)

This tool drafts the operator-controlled live-enable evidence sections for `hk_low_vol_dividend_quality`.
It covers the sections that are not produced directly by artifact validation, production-source audit, walk-forward backtest, or broker dry-run runtime reports.

The command does not deploy Cloud Run, place orders, upload artifacts, approve risk, or remove dry-run controls.
It only records explicit operator confirmations into validator-compatible draft JSON files.

## Sections

The tool writes one draft file per platform for:

- `broker_permission_and_fee_verification`
- `paper_or_dry_run_rebalance_window`
- `runtime_rollout_plan`
- `risk_approval`
- `strategy_policy_evidence`

These files can be passed to `hkeq-assemble-low-vol-dividend-live-enable-evidence`.

## Usage

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

`--confirm-all-strategy-policy-evidence` marks all required quality/yield ablation, stress-test, and data-provenance controls as confirmed.
Use it only when the referenced `--strategy-policy-evidence-uri` contains the complete review pack.

For partial review, provide a JSON object via `--strategy-policy-controls-file`; only fields explicitly set to `true` are marked true.

## Handoff to assembler

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

The final validator is still authoritative. Draft files marked `passed` are not sufficient by themselves; the full assembled pack must return `live_enablement_allowed=true`.
