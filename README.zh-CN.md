# HkEquitySnapshotPipelines

[English README](README.md)

> 投资有风险。本项目不构成投资建议，仅用于学习、研究和工程审阅。

## 这个仓库是什么

`HkEquitySnapshotPipelines` 是 QuantStrategyLab 的港股 snapshot 与证据流水线，用于生成 snapshot-backed 港股策略所需的 feature、factor、flow、valuation 和 event-calendar artifact。

本仓库产出证据和 artifact，不负责券商下单，不保存券商凭据，不部署 runtime 服务，也不会单独把某个策略变成 live。

## 策略和证据边界

### 普通 runtime 策略

直接使用 market-history 的港股策略在 `HkEquityStrategies`。本仓库不应该重复实现这些 runtime 逻辑，也不应该维护平台配置。

### 本仓库处理的 snapshot-backed 工作

本仓库负责 snapshot-backed 港股策略的 artifact 部分：

- snapshot profile contract 和 manifest
- 样例 builder 和参考 builder
- ranking 输出和 release-status summary
- artifact validation、promotion matrix 和 readiness check
- 供策略仓和平台仓使用的 live-enablement evidence 模板

### 下游如何使用

`HkEquityStrategies`、`InteractiveBrokersPlatform` 和 `LongBridgePlatform` 只应消费已验证 artifact 和 runtime-enabled profile。不能只根据一次样例构建或 README 描述判断某个策略适合 live。

## 当前 snapshot 工作队列

| 范围 | Profile | 含义 |
| --- | --- | --- |
| 首个 active snapshot 候选 | `hk_low_vol_dividend_quality` | 正在准备 runtime evidence review 的第一个 snapshot-backed 港股 profile。 |
| 延后 proxy retest | `hk_shareholder_yield_quality`, `hk_free_cash_flow_quality` | 保留给后续真实数据复测；不在默认 live-enable 队列。 |
| research-only scaffold | `hk_quality_growth_low_volatility`, `hk_factor_mix_qvlm_risk_parity`, `hk_central_soe_value_quality_select`, `hk_residual_momentum_quality`, `hk_liquid_momentum_quality`, `hk_composite_factor_quality_value_momentum`, `hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, `hk_blue_chip_leader_rotation`, `hk_index_rebalance_event` | 保留 builder 和 contract test；除非明确重新打开，否则不要求补完整 live evidence。 |

Promotion 状态由代码生成，不由 README 文本决定。改策略仓或平台配置前，请先查看 matrix 命令输出。

## 这些 artifact 用来做什么

Snapshot artifact 的作用是让策略判断可复现。一次典型发布包含：

- `<profile>_<snapshot_type>_latest.csv`
- `<profile>_<snapshot_type>_latest.csv.manifest.json`
- `<profile>_ranking_latest.csv`
- `release_status_summary.json`

这些文件是证据输入，不是收益宣传。下游仓库提升或执行 snapshot-backed profile 前，需要在适用场景下检查最新短、中、长周期表现，以及数据 lineage、成本、回撤、换手、artifact 新鲜度、dry-run 订单、通知、上线控制和人工审批。

## 快速开始

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## 本地构建和检查 artifact

运行样例构建：

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

查看 promotion 和 readiness 状态：

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
python scripts/print_snapshot_promotion_matrix.py --json
python scripts/print_snapshot_readiness.py --profile hk_low_vol_dividend_quality --json
```

校验 artifact pack：

```bash
hkeq-validate-snapshot-artifact-pack \
  --artifact-dir data/output/low_vol_dividend_quality \
  --profile hk_low_vol_dividend_quality \
  --json
```

生成 live-enable evidence 模板：

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality \
  --platform longbridge \
  --json
```

## 安全发布

Artifact 发布应先从 dry run 开始。只有确认 source CSV、GCS prefix、artifact contract 和 secret 边界后，才使用手动 GitHub workflow：

```bash
gh workflow run publish-hk-snapshot-artifacts.yml \
  --repo QuantStrategyLab/HkEquitySnapshotPipelines \
  -f profile=hk_low_vol_dividend_quality \
  -f factor_snapshot_path=gs://<bucket>/hk_equity/inputs/hk_low_vol_dividend_quality/factor_snapshot_YYYYMMDD.csv \
  -f gcs_prefix=gs://<bucket>/strategy-artifacts/hk_equity/hk_low_vol_dividend_quality_staging \
  -f execute_publish=false
```

这个 workflow 不会创建 production 数据，不会批准实盘，不会部署 Cloud Run，也不会提交券商订单。

## 仓库结构

- `src/`：snapshot builder、artifact contract、validation policy 和证据工具。
- `tests/`：单元测试、契约测试和回归测试。
- `docs/`：artifact contract、promotion runbook 和 evidence guide。
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
