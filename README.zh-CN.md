# HkEquitySnapshotPipelines

[English README](README.md)

> 投资有风险。本项目不构成投资建议，仅用于学习、研究和工程审阅。

## 这个仓库是什么

`HkEquitySnapshotPipelines` 是 QuantStrategyLab 的港股 snapshot 与证据流水线，用于生成 snapshot-backed 港股策略 runtime 所需的 feature-snapshot artifact、manifest、ranking preview、readiness report 和 live-enable evidence 模板。

本仓库产出证据和 artifact，不负责券商下单，不保存券商凭据，不部署 runtime 服务，也不会单独把某个策略变成 live。

## 策略和证据边界

### 普通 runtime 策略

直接使用 market-history 的港股策略在 `HkEquityStrategies`。本仓库不应该重复实现这些 runtime 逻辑，也不应该维护平台配置。

### 本仓库处理的 snapshot-backed 工作

当前 active contract 面只保留一个 snapshot profile：

| Profile | 展示名 | Snapshot 类型 | Builder 命令 | 状态 |
| --- | --- | --- | --- | --- |
| `hk_low_vol_dividend_quality_snapshot` | HK Low-Vol Dividend Quality Snapshot | `factor_snapshot` | `hkeq-build-low-vol-dividend-quality-snapshot` | `architecture_scaffold` |

之前 scaffold 出来的 snapshot 想法已经从 active contract 和 entrypoint 中移除，只在 [`docs/research/hk_snapshot_strategy_candidates.md`](docs/research/hk_snapshot_strategy_candidates.md) 里保留为被拒绝的研究记录。被移除的 profile 如果要重新加入，必须通过新的 research PR、point-in-time 数据、长/中/短周期回测和 live-enable 证据。

### 下游如何使用

`HkEquityStrategies`、`InteractiveBrokersPlatform` 和 `LongBridgePlatform` 只应消费已验证 artifact 和 runtime-enabled profile。不能只根据一次样例构建或 README 描述判断某个策略适合 live。

## 这些 artifact 用来做什么

保留 profile 的有效 snapshot pack 包含：

- `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_snapshot_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_snapshot_ranking_latest.csv`
- `release_status_summary.json`

这些文件是证据输入，不是收益宣传。下游仓库提升或执行 snapshot-backed profile 前，需要在适用场景下检查最新短、中、长周期表现，以及数据 lineage、成本、回撤、换手、artifact 新鲜度、dry-run 订单、通知、上线控制和人工审批。

## 快速开始

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## 本地构建和检查 artifact

构建保留策略的样例 artifact pack：

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

或调用安装后的 entrypoint：

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --output-dir data/output/low_vol_dividend_quality
```

查看 promotion 和 readiness 状态：

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality_snapshot --json
```

校验 artifact pack：

```bash
hkeq-validate-snapshot-artifact-pack \
  --artifact-dir data/output/low_vol_dividend_quality \
  --profile hk_low_vol_dividend_quality_snapshot \
  --json
```

生成 live-enable evidence 模板：

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

## 安全发布

Artifact 发布应先从 dry run 开始。只有确认 source CSV、GCS prefix、artifact contract 和 secret 边界后，才使用手动 GitHub workflow：

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality_snapshot \
  -f factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality_snapshot/factor_snapshot_YYYYMMDD.csv \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_snapshot_staging \
  -f execute_publish=false
```

这个 workflow 不会创建 production 数据，不会批准实盘，不会部署 Cloud Run，也不会提交券商订单。

## 月度 AI 审计

定时 workflow [`monthly_snapshot_audit.yml`](.github/workflows/monthly_snapshot_audit.yml) 会创建月度 GitHub issue，并把 review 工作派发到 `QuantStrategyLab/CodexAuditBridge`。

它只会在 `data/output/monthly_snapshot_audit` 下生成审计包，不会发布 artifact、部署 Cloud Run、修改券商配置或下单。

## 仓库结构

- `src/`：保留的 snapshot builder、artifact contract、validation policy 和证据工具。
- `tests/`：单元测试、契约测试和回归测试。
- `docs/`：artifact contract、promotion runbook、evidence guide 和被拒绝候选的研究记录。
- `.github/workflows/`：手动和定时 artifact / audit workflow。
- `scripts/`：本地 builder、研究回测、readiness 检查和证据辅助工具。
- `examples/`：样例输入文件和生产 CSV 模板。

## 延伸文档

- [`docs/artifact_contract.md`](docs/artifact_contract.md)
- [`docs/hk_snapshot_publish_workflow.zh-CN.md`](docs/hk_snapshot_publish_workflow.zh-CN.md)
- [`docs/first_snapshot_promotion_runbook.zh-CN.md`](docs/first_snapshot_promotion_runbook.zh-CN.md)
- [`docs/first_snapshot_evidence_tools.zh-CN.md`](docs/first_snapshot_evidence_tools.zh-CN.md)
- [`docs/low_vol_dividend_artifact_evidence.zh-CN.md`](docs/low_vol_dividend_artifact_evidence.zh-CN.md)
- [`docs/low_vol_dividend_backtest_evidence.zh-CN.md`](docs/low_vol_dividend_backtest_evidence.zh-CN.md)
- [`docs/low_vol_dividend_live_enablement_gate.zh-CN.md`](docs/low_vol_dividend_live_enablement_gate.zh-CN.md)
- [`docs/research/hk_snapshot_strategy_candidates.md`](docs/research/hk_snapshot_strategy_candidates.md)

## 安全和贡献说明

- 不要提交私人输入数据、券商凭据、签名 URL、token、Cookie、账户标识或私人订单数据。
- 除非是明确设计为公开的 example，否则不要把生成 artifact 放进 Git。
- 优先提供可复现命令，并显式指定输出目录。
- 没有通过生产数据、回测、dry-run 证据、中英文通知、上线控制和人工审批前，不要把研究 artifact 提升为 live 使用。

## 许可证

详见 [LICENSE](LICENSE)。
