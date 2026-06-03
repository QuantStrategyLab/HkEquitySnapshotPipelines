# 港股 Snapshot Artifact 发布 Workflow

[English version](./hk_snapshot_publish_workflow.md)

本文档说明：当运营侧已经准备好真实 factor snapshot CSV，或 workflow 从 LongBridge OpenAPI 生成输入时，如何构建、校验并可选发布 active 港股 snapshot artifact pack。

该 workflow **不会**批准实盘、不会部署 Cloud Run、不会向券商下单。它只把真实 CSV 或 LongBridge 生成的 runtime input 转换成已校验的 artifact pack；只有显式设置时才上传到 GCS。

## 范围

当前支持的 profile：

- `hk_low_vol_dividend_quality`

该 workflow 只支持手动触发。在生产级港股数据源 refresh 完成并通过审计前，不启用定时发布。

## 输入 CSV 要求

使用 [`../examples/low_vol_dividend_quality/production_factor_snapshot.template.csv`](../examples/low_vol_dividend_quality/production_factor_snapshot.template.csv) 作为表头模板。

必需列：

```text
symbol, sector, close_hkd, adv20_hkd, market_cap_hkd,
dividend_yield_net, dividend_stability_3y, earnings_positive, payout_ratio,
realized_vol_126, beta_252, maxdd_252, mom_6m, mom_12_1,
sma200_gap, suspension_days_63
```

建议列：

```text
as_of, snapshot_date, eligible, lot_size, pe_ratio,
free_cash_flow_yield, realized_vol_252, corporate_action_flag
```

最终实盘下单批准仍然不只是 CSV 有效，还需要：

- 至少 20 行真实数据，不能是 sample/smoke 行；
- price、fundamentals、dividend、corporate actions、suspension、symbol mapping 的 point-in-time source lineage；
- walk-forward 样本外回测证据；
- 券商 dry-run order preview、quote、fee、双语通知、rollout 和人工审批证据。

## 不会手工准备 CSV 时：LongBridge 生成输入模式

如果你还没有真实 factor snapshot CSV，可以先用 `input_source_mode=longbridge_openapi_staging` 让 workflow 从 LongBridge OpenAPI 生成一份 API 支撑的 runtime input CSV：

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality \
  -f input_source_mode=longbridge_openapi_staging \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  -f execute_publish=false
```

默认 universe 是 [`../examples/low_vol_dividend_quality/longbridge_universe.seed.csv`](../examples/low_vol_dividend_quality/longbridge_universe.seed.csv)。也可以用 `universe_path=gs://.../universe.csv` 指定自己的 universe。

该模式会从 Google Secret Manager 读取以下 secret，默认名称和 LongBridgePlatform 的 HK 配置一致：

- `longport-app-key-hk`
- `longport-app-secret-hk`
- `longport_token_hk`

默认从 `longbridgequant` GCP 项目读取这些 secret，并复用 LongBridgePlatform 的 Workload Identity Federation 命名约定。如果 secret 所在项目或 secret 名称不同，可以在 workflow 输入里覆盖：

- `longbridge_secret_project_id`
- `longbridge_app_key_secret_name`
- `longbridge_app_secret_secret_name`
- `longbridge_access_token_secret_name`

注意：LongBridge 生成 CSV 是真实接口数据生成的运行输入，并标记为 `longbridge_openapi_generated`。通过 artifact validation 并发布到稳定 GCS 路径后，它可以像美股 snapshot publish flow 一样作为平台接线用的 runtime artifact evidence。但它本身不等于最终实盘下单批准；最终批准仍需要回测、券商 dry-run、通知、rollout 和人工审批 evidence。

## GCP Workload Identity 前置条件

当 `input_source_mode=longbridge_openapi_staging` 时，workflow 需要一个明确允许本仓库 `QuantStrategyLab/HkEquitySnapshotPipelines` 的 Google Cloud Workload Identity Provider 和 service account。直接复用只允许 `LongBridgePlatform` 或 `UsEquitySnapshotPipelines` 的 provider，会在 auth 步骤报 `unauthorized_client` / `attribute condition`。

GCP 绑定完成后，设置以下 repository variables：

- `GCP_PROJECT_ID`：publish/auth workflow 使用的项目。
- `GCP_WORKLOAD_IDENTITY_PROVIDER`：attribute condition 允许 `QuantStrategyLab/HkEquitySnapshotPipelines` 的 provider。
- `GCP_WORKLOAD_IDENTITY_SERVICE_ACCOUNT`：允许通过该 provider impersonate 的 service account。

该 service account 需要：

- 能读取 `longbridge_secret_project_id` 中的 LongBridge HK secrets（默认 `longport-app-key-hk`、`longport-app-secret-hk`、`longport_token_hk`）。
- 仅在 `execute_publish=true` 时，需要对 `gcs_prefix` 有 GCS 写权限。

使用 `input_source_mode=factor_snapshot_csv`、仓库内 sample CSV 且不设置 `gcs_prefix` 的 workflow smoke test 不需要 GCP auth。它只能证明 workflow 打包路径可用，不能作为 runtime artifact evidence。

## 手动运行 GitHub Actions

打开 **Actions → Publish HK Snapshot Artifacts → Run workflow**，填写：

```text
profile=hk_low_vol_dividend_quality
factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv
gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging
execute_publish=false
```

第一次运行保持 `execute_publish=false`。Workflow 会构建 artifact pack、执行校验、打印 GCS copy plan，并把生成文件作为 GitHub Actions artifact 上传。

确认生成文件没问题后，再用 `execute_publish=true` 重新运行并上传到 GCS。发布计划包含：

- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_ranking_latest.csv`
- `release_status_summary.json`
- `artifact_pack_validation.json`
- 如果 workflow 从 LongBridge OpenAPI 生成输入，还会包含可选的 `source_input_summary.json`

## 本地等价命令

把远端 CSV 解析成本地文件：

```bash
python scripts/resolve_hk_snapshot_inputs.py \
  --factor-snapshot gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv \
  --output-dir data/input/resolved/hk_low_vol_dividend_quality \
  --env-output /tmp/resolved_hk_snapshot_inputs.env
source /tmp/resolved_hk_snapshot_inputs.env
```

构建并校验：

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

打印 GCS 发布计划：

```bash
python scripts/publish_hk_snapshot_artifacts.py \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --gcs-prefix gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging
```

审查通过后再上传：

```bash
python scripts/publish_hk_snapshot_artifacts.py \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir data/output/low_vol_dividend_quality \
  --gcs-prefix gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  --execute
```

## 安全规则

- 不要把 `examples/*/factor_snapshot.sample.csv` 当作 production evidence。
- 不要传入带 `token=`、`password=`、`signature=` 或类似 secret-like query 参数的 signed URL。
- 先使用 staging GCS prefix；只有 runtime artifact evidence、source lineage、backtest 和人工审批 evidence 审查通过后，才提升到 production prefix。
- 该 workflow 不会移除 LongBridge 或 IBKR 的 dry-run 控制。
