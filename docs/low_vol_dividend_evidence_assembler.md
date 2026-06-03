# HK Low-Volatility Dividend Quality Evidence Assembler

[中文版本](./low_vol_dividend_evidence_assembler.zh-CN.md)

This tool assembles section-level evidence drafts into a platform-specific live-enable evidence pack for `hk_low_vol_dividend_quality_snapshot`.
It is the handoff point between operator evidence collection and the final `hkeq-validate-live-enable-evidence` / `hkeq-audit-low-vol-dividend-live-enable` gates.

The command does not deploy Cloud Run, place orders, upload artifacts, merge approvals, or remove dry-run controls.
It only writes evidence JSON, validation JSON, and a small summary file.

## Inputs

The assembler starts from the canonical `hk_low_vol_dividend_quality_snapshot` live-enable template and can merge these files:

- production source audit: `--production-source-audit-file`
- artifact-pack validation: `--artifact-pack-validation-file`
- walk-forward backtest: `--walk-forward-backtest-file`
- platform dry-run order preview: `--platform-dry-run-file`
- broker permission and fee verification: `--broker-permission-file`
- paper/dry-run rebalance window: `--rebalance-window-file`
- runtime rollout plan: `--runtime-rollout-file`
- risk approval: `--risk-approval-file`
- quality/yield strategy-policy evidence: `--strategy-policy-evidence-file`

Each input may be either:

- the direct section object;
- a wrapper produced by a draft tool, such as `artifact_pack_validation_draft` or `walk_forward_backtest_draft`;
- a full evidence file under the `evidence` key.

`--base-evidence-file` can seed all known sections from an existing assembled pack before section-specific files override it.

## Usage

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

Output files:

- `longbridge_live_enablement_evidence.json`
- `longbridge_live_enablement_evidence.validation.json`
- `longbridge_live_enablement_evidence.assembly_summary.json`

Repeat the command for `--platform ibkr` with IBKR dry-run and broker evidence.

## Exit behavior

By default, the command returns zero even when the assembled pack is blocked. This makes it safe for operators to create incomplete drafts and inspect validation errors.

Use `--fail-on-blocked` in CI or release gates when a non-zero exit is required unless `live_enablement_allowed=true`.

## Live-enable rule

The assembled evidence pack is live-enable eligible only when the final validator returns:

```json
{
  "validation_status": "passed",
  "live_enablement_allowed": true
}
```

Until then, platform dry-run controls and production deployment protections must remain in place.
