# HkEquitySnapshotPipelines


## QSL architecture role

- **Layer**: `pipeline`.
- **Responsibility**: Hong Kong equity snapshot and evidence pipeline.
- **Owns**: HK snapshot artifacts, manifests, readiness reports.
- **Consumes**: HkEquityStrategies metadata and upstream market inputs.
- **Must not**: place broker orders or infer live suitability from sample builds.

[Chinese README](README.zh-CN.md)

> Investing involves risk. This project does not provide investment advice and is for education, research, and engineering review only.

## What this repository is

`HkEquitySnapshotPipelines` is the Hong Kong equity snapshot and evidence pipeline for QuantStrategyLab. It builds feature-snapshot artifacts, manifests, ranking previews, readiness reports, and live-enable evidence templates for snapshot-backed HK strategy runtimes.

This repository produces evidence and artifacts. It does not place broker orders, store broker credentials, deploy runtime services, or make a strategy live by itself.

## Strategy and evidence boundary

### Direct runtime strategies

Direct market-history HK strategies live in `HkEquityStrategies`. This repository should not duplicate their runtime logic or platform configuration.

### Snapshot-backed work handled here

Only one snapshot profile remains in the active contract surface:

| Profile | Display name | Snapshot type | Builder command | Status |
| --- | --- | --- | --- | --- |
| `hk_low_vol_dividend_quality_snapshot` | HK Low-Vol Dividend Quality Snapshot | `factor_snapshot` | `hkeq-build-low-vol-dividend-quality-snapshot` | `architecture_scaffold` |

Previously scaffolded snapshot ideas were removed from active contracts and entrypoints. They remain as rejected research notes in [`docs/research/hk_snapshot_strategy_candidates.md`](docs/research/hk_snapshot_strategy_candidates.md). A removed profile must return through a new research PR with point-in-time data, long/medium/short backtests, and live-enable evidence before becoming an active contract again.

### Downstream use

`HkEquityStrategies`, `InteractiveBrokersPlatform`, and `LongBridgePlatform` should consume only validated artifacts and runtime-enabled profiles. They should not infer live suitability from a single sample build or README description.

## What the artifacts are for

A valid retained snapshot pack contains:

- `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_snapshot_ranking_latest.csv`
- `release_status_summary.json`

These files are evidence inputs, not marketing claims. Before a downstream repository promotes or executes a snapshot-backed profile, review the latest short, medium, and long windows where applicable, plus data lineage, costs, drawdown, turnover, artifact freshness, dry-run orders, notifications, rollout controls, and operator approval.

## Quick start

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Build and inspect artifacts locally

Build the retained sample artifact pack:

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

Or call the installed entrypoint:

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --output-dir data/output/low_vol_dividend_quality
```

Inspect promotion and readiness state:

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality_snapshot --json
```

Validate an artifact pack:

```bash
hkeq-validate-snapshot-artifact-pack \
  --artifact-dir data/output/low_vol_dividend_quality \
  --profile hk_low_vol_dividend_quality_snapshot \
  --json
```

Generate a live-enable evidence template:

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

## Publish safely

Artifact publication should start as a dry run. Use the manual GitHub workflow only after checking the source CSV, GCS prefix, artifact contract, and secret boundaries:

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality_snapshot \
  -f factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality_snapshot/factor_snapshot_YYYYMMDD.csv \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_snapshot_staging \
  -f execute_publish=false
```

This workflow does not create production data, approve live trading, deploy Cloud Run, or submit broker orders.

## Monthly AI audit

The scheduled [`monthly_snapshot_audit.yml`](.github/workflows/monthly_snapshot_audit.yml) workflow creates a monthly GitHub issue and dispatches review work to `QuantStrategyLab/AIAuditBridge`.

It only writes an audit package under `data/output/monthly_snapshot_audit`; it does not publish artifacts, deploy Cloud Run, change broker configuration, or place orders.

## Repository layout

- `src/`: retained snapshot builders, artifact contracts, validation policies, and evidence tooling.
- `tests/`: unit, contract, and regression tests.
- `docs/`: artifact contracts, promotion runbooks, evidence guides, and rejected-candidate research notes.
- `.github/workflows/`: manual and scheduled artifact/audit workflows.
- `scripts/`: local builders, research backtests, readiness checks, and evidence helpers.
- `examples/`: sample input files and production CSV templates.

## Useful docs

- [`docs/artifact_contract.md`](docs/artifact_contract.md)
- [`docs/hk_snapshot_publish_workflow.md`](docs/hk_snapshot_publish_workflow.md)
- [`docs/first_snapshot_promotion_runbook.md`](docs/first_snapshot_promotion_runbook.md)
- [`docs/first_snapshot_evidence_tools.md`](docs/first_snapshot_evidence_tools.md)
- [`docs/low_vol_dividend_artifact_evidence.md`](docs/low_vol_dividend_artifact_evidence.md)
- [`docs/low_vol_dividend_backtest_evidence.md`](docs/low_vol_dividend_backtest_evidence.md)
- [`docs/low_vol_dividend_live_enablement_gate.md`](docs/low_vol_dividend_live_enablement_gate.md)
- [`docs/research/hk_snapshot_strategy_candidates.md`](docs/research/hk_snapshot_strategy_candidates.md)

## Safety and contribution notes

- Do not commit private input data, broker credentials, signed URLs, tokens, cookies, account identifiers, or private order data.
- Keep generated artifacts out of Git unless they are intentional public examples.
- Prefer reproducible commands and explicit output directories.
- Do not promote a research artifact to live use without validated production data, backtests, dry-run evidence, bilingual notifications, rollout controls, and operator approval.

## Community and security

- See [CONTRIBUTING.md](CONTRIBUTING.md) for pull request scope, local verification, and documentation expectations.
- Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for maintainer and contributor conduct.
- Report credential, automation, broker, exchange, or cloud-resource vulnerabilities through [SECURITY.md](SECURITY.md); do not open public issues for secrets or live-execution risk.

## License

See [LICENSE](LICENSE).
