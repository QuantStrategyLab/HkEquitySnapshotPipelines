# HkEquitySnapshotPipelines

[Chinese README](./README.zh-CN.md)

> Investment risk notice: this repository is for engineering, research, and operational review only. It is not investment advice.

`HkEquitySnapshotPipelines` is the snapshot-backed Hong Kong equity strategy pipeline repository for QuantStrategyLab.
It is intentionally separate from `HkEquityStrategies`, which owns non-snapshot runtime strategies that consume direct `market_history`.

## Repository boundary

This repository owns:

- snapshot artifact contracts for HK equity strategy scaffolds
- sample/reference builders for feature, factor, flow, valuation, and event-calendar snapshots
- ranking artifact generation and release-status summaries
- snapshot readiness, artifact-pack validation, promotion matrix, and live-enable evidence validators
- research notes for snapshot-backed HK strategy candidates

This repository does not own:

- non-snapshot runtime strategies
- broker API access, order placement, or account reconciliation
- Cloud Run / Google Run service configuration
- platform notifications or broker-specific execution reports
- production-grade HK market-data or fundamentals sourcing

Non-snapshot HK runtime profiles stay in [`../HkEquityStrategies`](../HkEquityStrategies). Keep snapshot profile documentation here and non-snapshot runtime documentation there.

## Current status

All profiles in this repository are `architecture_scaffold` / evidence-gated candidates. They are not platform live profiles by themselves.
A profile can only be promoted after production data, point-in-time backtests, artifact-pack validation, broker dry-run evidence, bilingual notification evidence, and operator approval are complete.

Current active snapshot live-enable work queue:

1. `hk_low_vol_dividend_quality`

Deferred quality/yield scaffolds retained for retest only: `hk_shareholder_yield_quality` and `hk_free_cash_flow_quality`.
They are not in the default live-enable work queue after the proxy cycle backtest because their long-cycle proxy drawdowns exceeded 30%.
All of these are work-priority states, not live switches.

## Snapshot profile index

Only `hk_low_vol_dividend_quality` is in the active live-enable work queue. The remaining scaffolded profiles are retained as research-only assets: keep their sample builders and basic tests, but do not require full walk-forward backtests or live-enable evidence packages unless they are explicitly reopened.

| Profile | Snapshot type | Builder command | Work scope | Status |
| --- | --- | --- | --- | --- |
| `hk_low_vol_dividend_quality` | `factor_snapshot` | `hkeq-build-low-vol-dividend-quality-snapshot` | active first snapshot candidate | `architecture_scaffold` |
| `hk_shareholder_yield_quality` | `factor_snapshot` | `hkeq-build-shareholder-yield-quality-snapshot` | deferred proxy retest scaffold | `architecture_scaffold` |
| `hk_free_cash_flow_quality` | `factor_snapshot` | `hkeq-build-free-cash-flow-quality-snapshot` | deferred proxy retest scaffold | `architecture_scaffold` |
| `hk_quality_growth_low_volatility` | `factor_snapshot` | `hkeq-build-quality-growth-low-volatility-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_factor_mix_qvlm_risk_parity` | `factor_snapshot` | `hkeq-build-factor-mix-qvlm-risk-parity-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_central_soe_value_quality_select` | `factor_snapshot` | `hkeq-build-central-soe-value-quality-select-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_residual_momentum_quality` | `factor_snapshot` | `hkeq-build-residual-momentum-quality-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_liquid_momentum_quality` | `feature_snapshot` | `hkeq-build-liquid-momentum-quality-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_composite_factor_quality_value_momentum` | `factor_snapshot` | `hkeq-build-composite-factor-qvm-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_southbound_flow_momentum` | `flow_snapshot` | `hkeq-build-southbound-flow-momentum-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_ah_premium_relative_value` | `valuation_snapshot` | `hkeq-build-ah-premium-relative-value-snapshot` | research-only scaffold | `architecture_scaffold` |
| `hk_blue_chip_leader_rotation` | `feature_snapshot` | `hkeq-build-blue-chip-leader-snapshot` | research-only baseline scaffold | `architecture_scaffold` |
| `hk_index_rebalance_event` | `event_calendar_snapshot` | `hkeq-build-index-rebalance-event-snapshot` | research-only scaffold | `architecture_scaffold` |

The active promotion order is exposed by the promotion matrix command instead of hard-coded in platform repositories. Use `research_only_scaffold_sequence` for retained non-first scaffolds.

## Artifact contract

Each builder writes a strategy-specific snapshot pack:

- `<profile>_<snapshot_type>_latest.csv`
- `<profile>_<snapshot_type>_latest.csv.manifest.json`
- `<profile>_ranking_latest.csv`
- `release_status_summary.json`

Contract details are documented in [`docs/artifact_contract.md`](./docs/artifact_contract.md).
Do not duplicate snapshot column contracts in `HkEquityStrategies`.

## Local sample builds

Run sample builders directly from source:

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
PYTHONPATH=src python scripts/build_shareholder_yield_sample.py
PYTHONPATH=src python scripts/build_free_cash_flow_sample.py
```

Or call installed package entrypoints:

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --output-dir data/output/low_vol_dividend_quality

hkeq-build-shareholder-yield-quality-snapshot \
  --factor-snapshot examples/shareholder_yield_quality/factor_snapshot.sample.csv \
  --output-dir data/output/shareholder_yield_quality

hkeq-build-free-cash-flow-quality-snapshot \
  --factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv \
  --output-dir data/output/free_cash_flow_quality
```

Other sample scripts live in [`scripts/`](./scripts/).

## Promotion and evidence tools

Use these read-only tools to inspect promotion state before touching platform configuration:

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality --json
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py --json
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py --json
```

Validate a snapshot artifact pack:

```bash
hkeq-validate-snapshot-artifact-pack \
  --artifact-dir data/output/low_vol_dividend_quality \
  --profile hk_low_vol_dividend_quality \
  --json
```

Generate and validate live-enable evidence:

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality \
  --platform longbridge \
  --json > snapshot-live-enable-evidence.json

hkeq-validate-live-enable-evidence \
  --evidence-file snapshot-live-enable-evidence.json \
  --json
```

The validators require stable evidence URIs, no secret-like query parameters, point-in-time data proof, out-of-sample backtests, HK cost/slippage/lot-size/capacity checks, dry-run order-preview provenance, bilingual notification evidence, rollout controls, and operator approval references.

Audit the final live-enable gates after production artifact and platform evidence are available:

```bash
hkeq-audit-low-vol-dividend-live-enable \
  --artifact-dir data/output/low_vol_dividend_quality \
  --longbridge-evidence-file evidence/longbridge_live_enablement_evidence.json \
  --ibkr-evidence-file evidence/ibkr_live_enablement_evidence.json \
  --json
```

For the active and deferred quality/yield snapshot candidates, use the shared evidence draft commands. Deferred profiles should stay out of the default live-enable queue until real point-in-time walk-forward evidence passes the 30% drawdown gate:

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_production_source_audit.py \
  --profile hk_shareholder_yield_quality \
  --factor-snapshot examples/shareholder_yield_quality/factor_snapshot.sample.csv \
  --source-name operator-prod-source \
  --json

PYTHONPATH=src python scripts/draft_first_snapshot_backtest_evidence.py \
  --profile hk_shareholder_yield_quality \
  --summary walk_forward_summary.json \
  --json
```

These draft commands keep all evidence `status: pending` and do not approve live trading.

## Research proxy cycle backtest

Use the research-only proxy backtest to compare snapshot scaffolds across long, medium, and short windows before spending time on full production-source evidence:

```bash
PYTHONPATH=src python scripts/research_hk_snapshot_proxy_cycle_backtest.py \
  --start 2016-01-01 \
  --end 2026-06-03 \
  --output-dir data/output/research_snapshot_proxy_backtest
```

The command downloads public Yahoo chart prices when available and falls back to deterministic synthetic prices only when requested or when public price retrieval fails. Missing fundamentals, buyback, FCF, Southbound-flow, policy, valuation, and event fields are deterministic simulated proxies, so the output is for research triage only and is not live-enable evidence. The 30% max-drawdown gate is applied separately to long, medium, and short windows.

## Monthly AI audit

The scheduled [`monthly_snapshot_audit.yml`](./.github/workflows/monthly_snapshot_audit.yml) workflow creates a monthly GitHub issue and dispatches `QuantStrategyLab/CodexAuditBridge` with task `monthly_snapshot_audit`.
This mirrors the snapshot monthly-review architecture used by the existing snapshot repositories while keeping AI provider keys out of this source repository.

The workflow only builds an audit bundle under `data/output/monthly_snapshot_audit`:

- `ai_review_input.md`: issue body sent to the AI auditor
- `job_summary.md`: GitHub Actions summary
- `monthly_snapshot_audit_issue.json`: issue metadata and artifact name

It does **not** publish artifacts, deploy Cloud Run, change broker configuration, or place orders.
The default monthly audit scope is limited to `hk_low_vol_dividend_quality`; non-selected and deferred snapshot scaffolds remain research-only / deprioritized unless validated evidence explicitly reopens them.

Manual local bundle generation:

```bash
python scripts/write_monthly_snapshot_audit_issue.py --as-of-month 2026-06
```

Manual workflow dispatch:

```bash
gh workflow run monthly_snapshot_audit.yml --repo QuantStrategyLab/HkEquitySnapshotPipelines
```

Source-repo settings:

- `SELFHOSTED_CODEX_REVIEW_REPOSITORY` defaults to `QuantStrategyLab/CodexAuditBridge`.
- `SELFHOSTED_CODEX_REVIEW_MODE` defaults to `review_and_fix`.
- `SELFHOSTED_CODEX_REVIEW_PROVIDER` defaults to `auto`.
- `SELFHOSTED_CODEX_REVIEW_AUTO_MERGE` defaults to `false`.
- Cross-repo dispatch needs either `CROSS_REPO_GITHUB_APP_ID` + `CROSS_REPO_GITHUB_APP_PRIVATE_KEY`, or a scoped `CODEX_AUDIT_DISPATCH_TOKEN`.
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` belong in `CodexAuditBridge`, not in this source repository.

## Local smoke command

```bash
python -m pytest -q
```

## Documentation

- [`docs/artifact_contract.md`](./docs/artifact_contract.md): snapshot artifact schema and manifest contract.
- [`docs/first_snapshot_promotion_runbook.md`](./docs/first_snapshot_promotion_runbook.md): promotion runbook for the active HK snapshot candidate.
- [`docs/first_snapshot_evidence_tools.md`](./docs/first_snapshot_evidence_tools.md): shared evidence package, bundle, source-audit, and backtest draft tools for active/deferred quality-yield candidates.
- [`docs/low_vol_dividend_live_enablement_package.md`](./docs/low_vol_dividend_live_enablement_package.md): first-candidate evidence package for `hk_low_vol_dividend_quality`.
- [`docs/low_vol_dividend_evidence_bundle.md`](./docs/low_vol_dividend_evidence_bundle.md): production source and walk-forward evidence templates for `hk_low_vol_dividend_quality`.
- [`docs/low_vol_dividend_live_enablement_audit.md`](./docs/low_vol_dividend_live_enablement_audit.md): final artifact + platform evidence audit for `hk_low_vol_dividend_quality`.
- [`docs/low_vol_dividend_production_source_audit.md`](./docs/low_vol_dividend_production_source_audit.md): production source audit draft tool for `hk_low_vol_dividend_quality`.
- [`docs/low_vol_dividend_backtest_evidence.md`](./docs/low_vol_dividend_backtest_evidence.md): walk-forward backtest evidence draft tool for `hk_low_vol_dividend_quality`.
- [`docs/research/hk_snapshot_strategy_candidates.md`](./docs/research/hk_snapshot_strategy_candidates.md): snapshot strategy research queue, curated candidates, and gating rationale.

## Related repositories

- [`../HkEquityStrategies`](../HkEquityStrategies): non-snapshot HK runtime strategies.
- [`../QuantPlatformKit`](../QuantPlatformKit): shared strategy contract and component loader.
- `InteractiveBrokersPlatform` / `LongBridgePlatform`: broker-specific runtime, deployment, order routing, and notification ownership.
