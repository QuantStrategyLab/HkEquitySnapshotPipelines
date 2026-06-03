# HkEquitySnapshotPipelines

[English README](./README.md)

> 风险提示：本仓库仅用于工程实现、研究和运行审查，不构成投资建议。

`HkEquitySnapshotPipelines` 是 QuantStrategyLab 港股 snapshot-backed 策略管线仓库。
它和 `HkEquityStrategies` 明确分开：`HkEquityStrategies` 只负责直接消费 `market_history` 的非 snapshot runtime 策略。

## 仓库边界

本仓库负责：

- 港股 snapshot strategy scaffold 的 artifact contract
- feature / factor / flow / valuation / event-calendar snapshot 的样例/参考 builder
- ranking artifact 与 release-status summary 生成
- snapshot readiness、artifact-pack validation、promotion matrix、live-enable evidence validator
- snapshot-backed 港股策略候选研究记录

本仓库不负责：

- 非 snapshot runtime 策略
- 券商 API、下单或账户对账
- Cloud Run / Google Run 服务配置
- 平台通知或券商专项执行报告
- 生产级港股行情、fundamentals 或披露数据源

非 snapshot 港股 runtime profile 统一保留在 [`../HkEquityStrategies`](../HkEquityStrategies)。Snapshot profile 文档放在本仓库，非 snapshot runtime 文档放在策略仓库，避免混在一起。

## 当前状态

本仓库全部 profile 都还是 `architecture_scaffold` / evidence-gated 候选，本身不是平台 live profile。
只有在补齐 production 数据、point-in-time 回测、artifact-pack 校验、券商 dry-run 证据、双语通知证据和人工审批后，才允许推动 promotion。

当前 active snapshot live-enable 工作队列：

1. `hk_low_vol_dividend_quality`

保留但仅用于重新回测的 quality/yield scaffold：`hk_shareholder_yield_quality` 和 `hk_free_cash_flow_quality`。
它们在 proxy 周期回测里长周期回撤超过 30%，因此不进入默认 live-enable 工作队列。
这些只是工作状态，不是 live 开关。

## Snapshot profile 索引

当前只有 `hk_low_vol_dividend_quality` 进入 active live-enable 工作队列。其他已 scaffold 的 profile 保留为 research-only 资产：保留 sample builder 和基础测试，但除非明确重新打开，不要求现在补完整 walk-forward 回测或 live-enable evidence package。

| Profile | Snapshot 类型 | Builder 命令 | 工作范围 | 状态 |
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

Active promotion 顺序由 promotion matrix 命令输出，不应该硬编码到平台仓库。保留的非首批 scaffold 使用 `research_only_scaffold_sequence` 查看。

## Artifact contract

每个 builder 生成对应策略的 snapshot pack：

- `<profile>_<snapshot_type>_latest.csv`
- `<profile>_<snapshot_type>_latest.csv.manifest.json`
- `<profile>_ranking_latest.csv`
- `release_status_summary.json`

Contract 细节见 [`docs/artifact_contract.md`](./docs/artifact_contract.md)。不要在 `HkEquityStrategies` 里重复维护 snapshot column contract。

## 本地样例构建

直接从源码运行样例 builder：

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
PYTHONPATH=src python scripts/build_shareholder_yield_sample.py
PYTHONPATH=src python scripts/build_free_cash_flow_sample.py
```

或调用安装后的 package entrypoint：

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

其他样例脚本在 [`scripts/`](./scripts/) 下。

## 港股 snapshot artifact 发布

手动 workflow [`Publish HK Snapshot Artifacts`](./.github/workflows/publish-hk-snapshot-artifacts.yml) 可以把运营侧提供的真实 CSV 或 LongBridge OpenAPI 生成的 runtime input 构建并校验为 active 港股 snapshot artifact pack。它只支持手动触发，默认只打印 dry-run 发布计划。

先使用生产 CSV 表头模板 [`examples/low_vol_dividend_quality/production_factor_snapshot.template.csv`](./examples/low_vol_dividend_quality/production_factor_snapshot.template.csv)，再按照 [`docs/hk_snapshot_publish_workflow.zh-CN.md`](./docs/hk_snapshot_publish_workflow.zh-CN.md) 操作。

示例 dry-run 触发：

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality \
  -f factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  -f execute_publish=false
```

该 workflow 不会创建 production 数据、不会批准实盘、不会部署 Cloud Run，也不会下单。

如果还没有 CSV，可以设置 `input_source_mode=longbridge_openapi_staging`；workflow 会用默认 seed universe 和 LongBridge HK Secret Manager 凭据（`longport-app-key-hk`、`longport-app-secret-hk`、`longport_token_hk`）生成 LongBridge API 支撑的 CSV。通过 artifact validation 并发布到稳定 GCS 路径后，它可以作为平台接线用的 runtime artifact evidence。最终实盘下单批准仍需要回测、券商 dry-run、通知、rollout 和人工审批 evidence。

## Promotion 与 evidence 工具

修改平台配置前，先用只读工具查看 promotion 状态：

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality --json
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py --json
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py --json
```

校验 snapshot artifact pack：

```bash
hkeq-validate-snapshot-artifact-pack \
  --artifact-dir data/output/low_vol_dividend_quality \
  --profile hk_low_vol_dividend_quality \
  --json
```

生成并校验 live-enable evidence：

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality \
  --json > snapshot-live-enable-evidence.json

hkeq-validate-live-enable-evidence \
  --evidence-file snapshot-live-enable-evidence.json \
  --json
```

Validator 要求稳定 evidence URI、不能带 token/password/signature 等 secret-like query 参数、point-in-time 数据证明、样本外回测、港股成本/滑点/lot-size/容量检查、dry-run order-preview provenance、双语通知证据、上线控制和人工审批引用。

active 和 deferred quality/yield snapshot 候选可以继续使用共用 evidence 草稿命令。Deferred profile 在真实 point-in-time walk-forward 证据通过 30% 回撤门槛前，不进入默认 live-enable 队列：

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

这些 draft 命令会保持所有 evidence `status: pending`，不会批准实盘交易。

## 研究用 proxy 周期回测

在投入完整生产数据源证据前，可以先用 research-only proxy 回测对 snapshot scaffold 做长、中、短周期比较：

```bash
PYTHONPATH=src python scripts/research_hk_snapshot_proxy_cycle_backtest.py \
  --start 2016-01-01 \
  --end 2026-06-03 \
  --output-dir data/output/research_snapshot_proxy_backtest
```

该命令优先下载公开 Yahoo chart 价格；只有显式指定 synthetic 或公开价格拉取失败时才回退到确定性模拟价格。缺失的 fundamentals、buyback、FCF、南向资金、政策、估值和事件字段都是确定性 proxy 模拟，因此输出只用于研究收口，不属于 live-enable 证据。30% 最大回撤门槛会分别应用到长、中、短三个周期。

## 月度 AI 审计

定时 workflow [`monthly_snapshot_audit.yml`](./.github/workflows/monthly_snapshot_audit.yml) 会创建月度 GitHub issue，并以 `monthly_snapshot_audit` 任务派发到 `QuantStrategyLab/CodexAuditBridge`。
这和已有 snapshot 仓库的月度 review 架构保持一致，同时避免把 AI provider key 放在本源仓库。

该 workflow 只生成 `data/output/monthly_snapshot_audit` 下的审计包：

- `ai_review_input.md`：发送给 AI 审计的 issue 正文
- `job_summary.md`：GitHub Actions summary
- `monthly_snapshot_audit_issue.json`：issue metadata 和 artifact name

它不会发布 artifact、不会部署 Cloud Run、不会修改券商配置，也不会下单。
默认月度审计范围只包含 `hk_low_vol_dividend_quality`；未入选或 deferred 的 snapshot scaffold 继续保持 research-only / deprioritized，除非后续补齐已验证证据并明确重新打开。

本地手动生成审计包：

```bash
python scripts/write_monthly_snapshot_audit_issue.py --as-of-month 2026-06
```

手动触发 workflow：

```bash
gh workflow run monthly_snapshot_audit.yml --repo QuantStrategyLab/HkEquitySnapshotPipelines
```

源仓库配置：

- `SELFHOSTED_CODEX_REVIEW_REPOSITORY` 默认是 `QuantStrategyLab/CodexAuditBridge`。
- `SELFHOSTED_CODEX_REVIEW_MODE` 默认是 `review_and_fix`。
- `SELFHOSTED_CODEX_REVIEW_PROVIDER` 默认是 `auto`。
- `SELFHOSTED_CODEX_REVIEW_AUTO_MERGE` 默认是 `false`。
- 跨仓 dispatch 需要 `CROSS_REPO_GITHUB_APP_ID` + `CROSS_REPO_GITHUB_APP_PRIVATE_KEY`，或具备作用域的 `CODEX_AUDIT_DISPATCH_TOKEN`。
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` 应配置在 `CodexAuditBridge`，不要放在本源仓库。

## 本地 smoke 命令

```bash
python -m pytest -q
```

## 文档

- [`docs/artifact_contract.md`](./docs/artifact_contract.md)：snapshot artifact schema 和 manifest contract。
- [`docs/hk_snapshot_publish_workflow.zh-CN.md`](./docs/hk_snapshot_publish_workflow.zh-CN.md)：港股 snapshot artifact 手动构建、校验和可选 GCS 发布 workflow。
- [`docs/first_snapshot_promotion_runbook.md`](./docs/first_snapshot_promotion_runbook.md)：当前 active 港股 snapshot 候选的 promotion runbook。
- [`docs/first_snapshot_evidence_tools.zh-CN.md`](./docs/first_snapshot_evidence_tools.zh-CN.md)：active/deferred quality-yield 候选共用的 evidence package、bundle、source-audit 和 backtest draft 工具。
- [`docs/low_vol_dividend_live_enablement_package.zh-CN.md`](./docs/low_vol_dividend_live_enablement_package.zh-CN.md)：`hk_low_vol_dividend_quality` 首个候选 evidence package。
- [`docs/low_vol_dividend_evidence_bundle.zh-CN.md`](./docs/low_vol_dividend_evidence_bundle.zh-CN.md)：`hk_low_vol_dividend_quality` 的生产数据源和 walk-forward 回测证据模板。
- [`docs/low_vol_dividend_production_source_audit.zh-CN.md`](./docs/low_vol_dividend_production_source_audit.zh-CN.md)：`hk_low_vol_dividend_quality` 的生产数据源审计草稿工具。
- [`docs/low_vol_dividend_backtest_evidence.zh-CN.md`](./docs/low_vol_dividend_backtest_evidence.zh-CN.md)：`hk_low_vol_dividend_quality` 的 walk-forward 回测证据草稿工具。
- [`docs/research/hk_snapshot_strategy_candidates.md`](./docs/research/hk_snapshot_strategy_candidates.md)：snapshot 策略研究队列、候选排序和门槛依据。

## 相关仓库

- [`../HkEquityStrategies`](../HkEquityStrategies)：非 snapshot 港股 runtime 策略。
- [`../QuantPlatformKit`](../QuantPlatformKit)：共享策略 contract 与 component loader。
- `InteractiveBrokersPlatform` / `LongBridgePlatform`：券商 runtime、部署、订单路由和通知归属。
