# HK Low-Volatility Dividend Quality Live-Enable Audit

[中文版本](./low_vol_dividend_live_enablement_audit.zh-CN.md)

This tool is the final machine-checkable audit before `hk_low_vol_dividend_quality` can be treated as true live-enable ready.
It combines three independent gates:

1. production snapshot artifact pack validation;
2. LongBridge live-enable evidence validation;
3. IBKR live-enable evidence validation.

It does not create evidence, deploy Cloud Run, publish artifacts, remove dry-run controls, or place broker orders.
If any gate is missing or failed, the audit returns a non-zero exit code.

## Usage

```bash
python scripts/audit_low_vol_dividend_live_enablement.py \
  --artifact-dir gs-mounted-or-local-production-artifacts \
  --longbridge-evidence-file evidence/longbridge_live_enablement_evidence.json \
  --ibkr-evidence-file evidence/ibkr_live_enablement_evidence.json \
  --validation-as-of 2026-06-03 \
  --json
```

The package entry point is also available after installation:

```bash
hkeq-audit-low-vol-dividend-live-enable \
  --artifact-dir gs-mounted-or-local-production-artifacts \
  --longbridge-evidence-file evidence/longbridge_live_enablement_evidence.json \
  --ibkr-evidence-file evidence/ibkr_live_enablement_evidence.json \
  --json
```

## Passing condition

The audit only passes when:

- the artifact pack passes `hkeq-validate-snapshot-artifact-pack`;
- both platform evidence files pass `hkeq-validate-live-enable-evidence`;
- all evidence is fresh, stable, secret-safe, and complete;
- both platform dry-run previews, bilingual notification logs, broker permissions, rollout controls, and operator approval are present.

Sample artifacts, pending templates, missing platform dry-run evidence, or stale evidence keep `live_enablement_allowed=false`.
