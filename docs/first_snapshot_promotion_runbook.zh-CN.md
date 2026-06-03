# 首批港股 Snapshot Promotion Runbook

[English version](./first_snapshot_promotion_runbook.md)

本 runbook 将港股 snapshot promotion 工作限定到 1 个保留的 evidence-gated 候选：

1. `hk_low_vol_dividend_quality_snapshot`

其他 snapshot scaffold 已经在 proxy triage 后从 package entrypoint 中剔除或拒绝。本 runbook 不会 live-enable、不发布 production artifact、不部署 Cloud Run，也不会下券商订单。

## 为什么先推进这个 profile

`hk_low_vol_dividend_quality_snapshot` 是低换手、质量/收益类候选，更符合当前港股最大回撤控制目标；相比事件、资金流、AH 溢价或高换手动量 scaffold，生产数据和执行风险更可控。但它仍必须证明最大回撤 `<= 30%`、至少 3 个独立样本外 fold、扣费后收益、港股流动性/容量、artifact provenance、dry-run order preview、双语通知证据和人工审批。

## 打印 promotion plan

首批候选以这个命令输出为准：

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
```

也可以限制到单一 profile 或平台：

```bash
python scripts/print_first_snapshot_promotion_plan.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

该命令只读，只输出计划命令、artifact 文件名、readiness 模板、evidence gate 和阻塞原因。

## 推进顺序

### 1. Sample artifact smoke

先用样例 artifact 验证本地 contract wiring：

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

样例 artifact 不是生产数据，不能用于计划任务或实盘交易。

### 2. Production source audit

用 point-in-time 生产数据替换样例输入。至少需要覆盖：

- source coverage start/end 和 data dictionary
- source quality report URI
- corporate actions、停牌、stale quote、缺失字段、symbol mapping
- fundamentals 的 reporting-date / availability-date lineage
- dividend、payout、volatility、liquidity、corporate action、停牌、可选 ROE/FCF 质量字段和 sector lineage
- evidence URI 不得包含 token/password/signature 等 secret-like query 参数

### 3. Walk-forward backtest

平台 dry-run promotion 前必须先跑 survivorship-safe walk-forward 回测：

- 至少 3 个独立样本外 fold
- 最大回撤 `<= 30%`，若 profile 有更严格阈值则按更严格阈值
- 年化收益 / 最大回撤比 `>= 0.50`
- 单一周期收益贡献 `<= 60%`
- 保留候选的年化换手 `<= 100%`
- 覆盖港股费用、征费、滑点、bid/ask spread、lot-size、停牌、VCM、CAS 和容量压力
- 如果未来重新加入新 snapshot contract，需要同 universe 对比被剔除的 quality/yield 变体

### 4. Artifact-pack validation

校验发布后的 artifact 目录：

```bash
hkeq-validate-snapshot-artifact-pack \
  --profile hk_low_vol_dividend_quality_snapshot \
  --artifact-dir data/output/hk_low_vol_dividend_quality_snapshot \
  --json
```

被剔除的 profile 已不再是 package contract，因此不在这里校验。

### 5. Platform dry-run evidence

平台接线前先打印 readiness 模板：

```bash
python scripts/print_snapshot_readiness.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

生成 evidence 模板：

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json > snapshot-live-enable-evidence.json
```

校验补齐后的 evidence：

```bash
hkeq-validate-live-enable-evidence \
  --evidence-file snapshot-live-enable-evidence.json \
  --json
```

Dry-run evidence 必须包括 raw order preview、quote snapshot、fee breakdown、sha256 provenance、中英文通知 payload、delivery-log URI、人工审批引用、分阶段 rollout、tripwire、kill switch 和 rollback plan。

## Profile 专项重点

| Profile | Promotion 前重点 |
| --- | --- |
| `hk_low_vol_dividend_quality_snapshot` | forecast vs trailing dividend yield ablation、yield-trap 控制、南向 eligible、三年现金分红记录、payout-ratio、price-crash screen、高波动剔除和财务稳健 screen。 |

## 停止条件

出现以下任一情况，不允许 promotion：

- 使用 sample artifact 作为生产数据
- evidence URI 包含 token/password/signature 等 secret-like query 参数
- 少于 3 个独立样本外 fold
- 任一样本外 fold 超过回撤门槛
- 费用/滑点/价差压力测试后超额收益不为正
- artifact manifest sha256 与发布 snapshot 不一致
- 缺少 dry-run order preview 或双语通知证据
- 缺少人工审批和 rollback plan
