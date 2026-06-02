# HK Low-Volatility Dividend Quality Live-Enable Gate Runner

[中文版本](./low_vol_dividend_live_enablement_gate.zh-CN.md)

This command runs the end-to-end evidence gate for `hk_low_vol_dividend_quality`.
It reads evidence files from a convention-based directory, assembles LongBridge and IBKR evidence packs, and runs the final live-enable audit.

The command does not deploy Cloud Run, place orders, publish artifacts, approve risk, or remove dry-run controls.
It only performs local evidence assembly and validation.

## Convention

Default evidence directory:

```text
evidence/low_vol_dividend_quality/
```

Shared files:

```text
production_source_audit.draft.json
artifact_pack_validation.draft.json
walk_forward_backtest.draft.json
```

Platform files:

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

## Usage

```bash
hkeq-run-low-vol-dividend-live-enable-gate \
  --evidence-dir evidence/low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --validation-as-of 2026-06-03 \
  --output-dir data/output/low_vol_dividend_live_enablement_gate \
  --json
```

Output files:

```text
data/output/low_vol_dividend_live_enablement_gate/assembled/longbridge_live_enablement_evidence.json
data/output/low_vol_dividend_live_enablement_gate/assembled/ibkr_live_enablement_evidence.json
data/output/low_vol_dividend_live_enablement_gate/final_live_enablement_audit.json
data/output/low_vol_dividend_live_enablement_gate/live_enablement_gate_summary.json
```

## Exit behavior

By default, the command returns zero even when the gate is blocked. This lets operators inspect missing evidence and validation errors.

Use `--fail-on-blocked` for CI or release gates:

```bash
hkeq-run-low-vol-dividend-live-enable-gate \
  --evidence-dir evidence/low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --validation-as-of 2026-06-03 \
  --fail-on-blocked
```

## Passing rule

The gate passes only when:

- the local artifact directory passes `hkeq-validate-snapshot-artifact-pack` and has at least 20 snapshot rows;
- LongBridge assembled evidence returns `live_enablement_allowed=true`;
- IBKR assembled evidence returns `live_enablement_allowed=true`;
- the final audit returns `live_enablement_allowed=true`.

Until the final audit passes, the strategy must remain blocked from true live-enable.
