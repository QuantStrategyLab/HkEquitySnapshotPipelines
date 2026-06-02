# 首批港股 Snapshot Evidence 工具

[English version](./first_snapshot_evidence_tools.md)

本文档说明首批 3 个港股 snapshot 候选共用的 evidence 工具：

1. `hk_low_vol_dividend_quality`
2. `hk_shareholder_yield_quality`
3. `hk_free_cash_flow_quality`

这些工具全部是 evidence-gated。它们不会 live-enable 策略、不会部署 Cloud Run、不会发布生产 artifact，也不会下券商订单。

## 范围

工具会为首批 3 个 profile 生成同一套 live-enable scaffold：

- live-enable evidence package；
- production evidence template bundle；
- production source audit draft；
- walk-forward backtest evidence draft。

原来的低波红利专项命令继续保留，用于兼容已有流程。准备首批 3 个候选的 evidence 时，优先使用这里的共用 first-snapshot 命令。

## 生成 live-enable evidence package

为首批 3 个 profile 全部生成 package：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py
```

只生成一个 profile：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_live_enablement_packages.py \
  --profile hk_shareholder_yield_quality \
  --platform longbridge \
  --json
```

默认输出：

```text
data/output/first_snapshot_live_enablement_packages/<profile>/live_enablement_package.json
data/output/first_snapshot_live_enablement_packages/<profile>/live_enablement_package.md
```

每个 package 都会显式保持：

- `runtime_enabled: false`
- `live_enablement_allowed: false`
- `production_deployment_allowed: false`
- `dry_run_only_until_all_gates_pass: true`

## 生成 evidence template bundle

为首批 3 个 profile 全部生成模板包：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py
```

只生成一个 profile：

```bash
PYTHONPATH=src python scripts/build_first_snapshot_evidence_bundles.py \
  --profile hk_free_cash_flow_quality \
  --json
```

默认输出：

```text
data/output/first_snapshot_evidence_bundles/<profile>/evidence_bundle.json
data/output/first_snapshot_evidence_bundles/<profile>/evidence_templates/
```

模板包包含 production source、walk-forward、quality/yield strategy-policy、LongBridge 和 IBKR 证据模板。

## 生成 production source audit 草稿

production source audit draft 只检查本地 schema 和基础数据质量门槛。本地检查通过不等于 live-enable 审批通过。

示例：

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_production_source_audit.py \
  --profile hk_free_cash_flow_quality \
  --factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv \
  --source-name operator-prod-source \
  --evidence-generated-at 2026-06-03 \
  --json
```

如果路径看起来像 sample data，工具会给出 warning。Sample artifact 不能作为生产 evidence 使用。

Profile 专项 required operational columns：

| Profile | Required operational columns |
| --- | --- |
| `hk_low_vol_dividend_quality` | `as_of`, `snapshot_date`, `eligible`, `lot_size`, `corporate_action_flag` |
| `hk_shareholder_yield_quality` | `as_of`, `eligible`, `southbound_eligible`, `lot_size`, `corporate_action_flag` |
| `hk_free_cash_flow_quality` | `as_of`, `snapshot_date`, `eligible`, `southbound_eligible`, `lot_size`, `corporate_action_flag` |

## 生成 walk-forward backtest evidence 草稿

Backtest draft 会校验 operator 提供的 summary metrics 是否满足共用 live-enable gates：

- 年化收益为正，且对基准有正超额收益；
- 最大回撤和 rolling OOS fold 最大回撤 `<= 30%`；
- 至少 3 个 OOS folds；
- 满足 profile turnover cap；
- benchmark symbol 对齐；
- 覆盖港股费用、印花税或豁免、滑点、board-lot、停牌、幸存者偏差、未来函数、市场压力和容量控制。

示例：

```bash
PYTHONPATH=src python scripts/draft_first_snapshot_backtest_evidence.py \
  --profile hk_shareholder_yield_quality \
  --summary walk_forward_summary.json \
  --evidence-generated-at 2026-06-03 \
  --json
```

生成的 evidence draft 会保持 `status: pending`，直到完整 walk-forward report、fold metrics、参数敏感性、成本模型和 point-in-time/no-lookahead 证据都补齐。

## Promotion gates

任何 live-enable 变更前，每个首批 profile 都仍然需要：

- point-in-time 生产数据源审计；
- 无未来函数、无幸存者偏差；
- 至少 3 个独立 OOS folds；
- 最大回撤 `<= 30%`；
- 扣除港股成本和流动性压力后仍有正超额收益；
- snapshot artifact-pack validation；
- LongBridge 和 IBKR dry-run order preview；
- 使用统一通知格式的 EN/ZH-Hans 双语通知证据；
- 人工审批、tripwire、kill switch 和 rollback plan。
