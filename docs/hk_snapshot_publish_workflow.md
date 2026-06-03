# HK Snapshot Publish Workflow

[中文版本](./hk_snapshot_publish_workflow.zh-CN.md)

This runbook explains how to build, validate, and optionally publish the active HK snapshot artifact pack when an operator has prepared a real factor snapshot CSV, or when the workflow generates one from public yfinance data or LongBridge OpenAPI.

The workflow does **not** approve live trading, deploy Cloud Run, or place broker orders. It only turns a real CSV or generated runtime input into a validated artifact pack and, when explicitly requested, uploads the pack to GCS.

## Scope

Current supported profile:

- `hk_low_vol_dividend_quality`

The workflow is manual-only. There is no schedule until a production HK data-source refresh is implemented and audited.

## Required input CSV

Use [`../examples/low_vol_dividend_quality/production_factor_snapshot.template.csv`](../examples/low_vol_dividend_quality/production_factor_snapshot.template.csv) as the header template.

Required columns:

```text
symbol, sector, close_hkd, adv20_hkd, market_cap_hkd,
dividend_yield_net, dividend_stability_3y, earnings_positive, payout_ratio,
realized_vol_126, beta_252, maxdd_252, mom_6m, mom_12_1,
sma200_gap, suspension_days_63
```

Recommended columns:

```text
as_of, snapshot_date, eligible, lot_size, pe_ratio,
free_cash_flow_yield, realized_vol_252, corporate_action_flag
```

Final live order approval still requires more than a valid CSV:

- at least 20 real rows, not sample/smoke rows;
- point-in-time source lineage for prices, fundamentals, dividends, corporate actions, suspensions, and symbol mapping;
- walk-forward out-of-sample backtest evidence;
- broker dry-run order preview, quote, fee, bilingual notification, rollout, and operator approval evidence.

## If you do not know how to prepare the CSV: generated input modes

If no real factor snapshot CSV exists yet, prefer `input_source_mode=public_yfinance_staging`. It generates a public-data runtime input CSV without requiring LongBridge historical market-data permission:

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality \
  -f input_source_mode=public_yfinance_staging \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  -f execute_publish=false
```

The default universe is [`../examples/low_vol_dividend_quality/longbridge_universe.seed.csv`](../examples/low_vol_dividend_quality/longbridge_universe.seed.csv). You may override it with `universe_path=gs://.../universe.csv`. Public yfinance mode stores `source_name=public_yfinance_staging` and `source_quality=public_yfinance_generated` when `allow_research_defaults=false`.

LongBridge OpenAPI mode remains available when the account has the required HK historical market-data entitlement:

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality \
  -f input_source_mode=longbridge_openapi_staging \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  -f execute_publish=false
```

LongBridge mode reads these Google Secret Manager secrets by default, matching the HK LongBridgePlatform naming convention:

- `longport-app-key-hk`
- `longport-app-secret-hk`
- `longport_token_hk`

The default `longbridge_credentials_mode=secret_manager` reads these secrets from the `longbridgequant` GCP project and uses the same Workload Identity Federation naming convention as `LongBridgePlatform`. If your secret project or secret names differ, override these workflow inputs:

- `longbridge_secret_project_id`
- `longbridge_app_key_secret_name`
- `longbridge_app_secret_secret_name`
- `longbridge_access_token_secret_name`

If the GCP Workload Identity binding is not ready yet, set `longbridge_credentials_mode=github_secrets` and provide these GitHub Actions secrets instead:

- `LONGBRIDGE_APP_KEY_HK` (alias supported: `LONG_BRIDGE_APP_KEY_HK`)
- `LONGBRIDGE_APP_SECRET_HK` (alias supported: `LONG_BRIDGE_APP_SECRET_HK`)
- `LONGBRIDGE_ACCESS_TOKEN_HK` (aliases supported: `LONG_BRIDGE_ACCESS_TOKEN_HK`, `LONGPORT_ACCESS_TOKEN_HK`)

In `github_secrets` mode, LongBridge input generation does not require GCP auth unless `universe_path` / `factor_snapshot_path` uses `gs://` or `execute_publish=true` uploads to GCS.

Important: generated CSVs with `allow_research_defaults=false` can be runtime artifact inputs after artifact validation and stable GCS publishing, similar to the US snapshot publish flow. They are not final live order approval by themselves; that still requires backtest, broker dry-run, notification, rollout, and operator approval evidence. `allow_research_defaults=true` remains research smoke only.

## GCP Workload Identity prerequisites

For `input_source_mode=longbridge_openapi_staging`, or any run that reads `gs://` inputs or publishes to GCS, the workflow needs a Google Cloud Workload Identity Provider and service account that explicitly allow this repository: `QuantStrategyLab/HkEquitySnapshotPipelines`. Reusing a provider that is restricted to `LongBridgePlatform` or `UsEquitySnapshotPipelines` will fail at the auth step with `unauthorized_client` / `attribute condition`. Public yfinance mode without `gs://` inputs and without `execute_publish=true` does not need GCP auth.

Set these repository variables after the GCP binding is created:

- `GCP_PROJECT_ID`: project used by the publish/auth workflow.
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: provider whose attribute condition allows `QuantStrategyLab/HkEquitySnapshotPipelines`.
- `GCP_WORKLOAD_IDENTITY_SERVICE_ACCOUNT`: service account allowed to impersonate through that provider.

The service account needs:

- Secret Manager access to the LongBridge HK secrets in `longbridge_secret_project_id` (`longport-app-key-hk`, `longport-app-secret-hk`, `longport_token_hk` by default).
- GCS write access to `gcs_prefix` only when `execute_publish=true`.

A workflow smoke test with `input_source_mode=factor_snapshot_csv`, a repository-local sample CSV, and no `gcs_prefix` does not require GCP auth. It proves workflow packaging only; it is not runtime artifact evidence.

## Manual GitHub Actions run

Open **Actions → Publish HK Snapshot Artifacts → Run workflow** and set:

```text
profile=hk_low_vol_dividend_quality
factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv
gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging
execute_publish=false
```

Keep `execute_publish=false` for the first run. The workflow will build the pack, validate it, print the GCS copy plan, and upload the generated files as a GitHub Actions artifact.

After reviewing the generated files, re-run with `execute_publish=true` to upload to GCS. The publish plan includes:

- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_ranking_latest.csv`
- `release_status_summary.json`
- `artifact_pack_validation.json`
- optional `source_input_summary.json` when the workflow generated the input from public yfinance or LongBridge OpenAPI

## Local equivalent

Resolve a remote CSV into a local file:

```bash
python scripts/resolve_hk_snapshot_inputs.py \
  --factor-snapshot gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv \
  --output-dir data/input/resolved/hk_low_vol_dividend_quality \
  --env-output /tmp/resolved_hk_snapshot_inputs.env
source /tmp/resolved_hk_snapshot_inputs.env
```

Build and validate:

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot "$FACTOR_SNAPSHOT_PATH" \
  --output-dir data/output/low_vol_dividend_quality \
  --min-adv20-hkd 5000000 \
  --min-market-cap-hkd 2000000000

hkeq-validate-snapshot-artifact-pack \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --json > data/output/low_vol_dividend_quality/artifact_pack_validation.json
```

Print the GCS publish plan:

```bash
python scripts/publish_hk_snapshot_artifacts.py \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --gcs-prefix gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging
```

Upload only after review:

```bash
python scripts/publish_hk_snapshot_artifacts.py \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --gcs-prefix gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  --execute
```

## Safety rules

- Do not use `examples/*/factor_snapshot.sample.csv` as production evidence.
- Do not pass signed URLs or URLs containing `token=`, `password=`, `signature=`, or similar secret-like query parameters.
- Use a staging GCS prefix first; only promote to a production prefix after runtime artifact evidence, source lineage, backtest, and operator approval evidence are reviewed.
- This workflow does not remove dry-run controls from LongBridge or IBKR.
