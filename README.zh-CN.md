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

当前首批 snapshot 候选：

1. `hk_low_vol_dividend_quality`
2. `hk_shareholder_yield_quality`
3. `hk_free_cash_flow_quality`

这些只是工作优先级，不是 live 开关。

## Snapshot profile 索引

| Profile | Snapshot 类型 | Builder 命令 | 状态 |
| --- | --- | --- | --- |
| `hk_low_vol_dividend_quality` | `factor_snapshot` | `hkeq-build-low-vol-dividend-quality-snapshot` | `architecture_scaffold` |
| `hk_shareholder_yield_quality` | `factor_snapshot` | `hkeq-build-shareholder-yield-quality-snapshot` | `architecture_scaffold` |
| `hk_free_cash_flow_quality` | `factor_snapshot` | `hkeq-build-free-cash-flow-quality-snapshot` | `architecture_scaffold` |
| `hk_quality_growth_low_volatility` | `factor_snapshot` | `hkeq-build-quality-growth-low-volatility-snapshot` | `architecture_scaffold` |
| `hk_factor_mix_qvlm_risk_parity` | `factor_snapshot` | `hkeq-build-factor-mix-qvlm-risk-parity-snapshot` | `architecture_scaffold` |
| `hk_central_soe_value_quality_select` | `factor_snapshot` | `hkeq-build-central-soe-value-quality-select-snapshot` | `architecture_scaffold` |
| `hk_residual_momentum_quality` | `factor_snapshot` | `hkeq-build-residual-momentum-quality-snapshot` | `architecture_scaffold` |
| `hk_liquid_momentum_quality` | `feature_snapshot` | `hkeq-build-liquid-momentum-quality-snapshot` | `architecture_scaffold` |
| `hk_composite_factor_quality_value_momentum` | `factor_snapshot` | `hkeq-build-composite-factor-qvm-snapshot` | `architecture_scaffold` |
| `hk_southbound_flow_momentum` | `flow_snapshot` | `hkeq-build-southbound-flow-momentum-snapshot` | `architecture_scaffold` |
| `hk_ah_premium_relative_value` | `valuation_snapshot` | `hkeq-build-ah-premium-relative-value-snapshot` | `architecture_scaffold` |
| `hk_blue_chip_leader_rotation` | `feature_snapshot` | `hkeq-build-blue-chip-leader-snapshot` | `architecture_scaffold` |
| `hk_index_rebalance_event` | `event_calendar_snapshot` | `hkeq-build-index-rebalance-event-snapshot` | `architecture_scaffold` |

推荐 promotion 顺序由 promotion matrix 命令输出，不应该硬编码到平台仓库。

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

## Promotion 与 evidence 工具

修改平台配置前，先用只读工具查看 promotion 状态：

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality --json
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

## 月度 AI 审计

定时 workflow [`monthly_snapshot_audit.yml`](./.github/workflows/monthly_snapshot_audit.yml) 会创建月度 GitHub issue，并以 `monthly_snapshot_audit` 任务派发到 `QuantStrategyLab/CodexAuditBridge`。
这和已有 snapshot 仓库的月度 review 架构保持一致，同时避免把 AI provider key 放在本源仓库。

该 workflow 只生成 `data/output/monthly_snapshot_audit` 下的审计包：

- `ai_review_input.md`：发送给 AI 审计的 issue 正文
- `job_summary.md`：GitHub Actions summary
- `monthly_snapshot_audit_issue.json`：issue metadata 和 artifact name

它不会发布 artifact、不会部署 Cloud Run、不会修改券商配置，也不会下单。
首批审计范围只包含 `hk_low_vol_dividend_quality`、`hk_shareholder_yield_quality`、`hk_free_cash_flow_quality`；未入选的 snapshot scaffold 继续保持 research-only / deprioritized，除非后续补齐已验证证据。

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
- [`docs/first_snapshot_promotion_runbook.md`](./docs/first_snapshot_promotion_runbook.md)：首批 3 个港股 snapshot 候选的 promotion runbook。
- [`docs/low_vol_dividend_live_enablement_package.zh-CN.md`](./docs/low_vol_dividend_live_enablement_package.zh-CN.md)：`hk_low_vol_dividend_quality` 首个候选 evidence package。
- [`docs/low_vol_dividend_evidence_bundle.zh-CN.md`](./docs/low_vol_dividend_evidence_bundle.zh-CN.md)：`hk_low_vol_dividend_quality` 的生产数据源和 walk-forward 回测证据模板。
- [`docs/research/hk_snapshot_strategy_candidates.md`](./docs/research/hk_snapshot_strategy_candidates.md)：snapshot 策略研究队列、候选排序和门槛依据。

## 相关仓库

- [`../HkEquityStrategies`](../HkEquityStrategies)：非 snapshot 港股 runtime 策略。
- [`../QuantPlatformKit`](../QuantPlatformKit)：共享策略 contract 与 component loader。
- `InteractiveBrokersPlatform` / `LongBridgePlatform`：券商 runtime、部署、订单路由和通知归属。
