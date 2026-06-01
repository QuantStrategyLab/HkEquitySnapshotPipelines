# HkEquitySnapshotPipelines

> ⚠️ 投资有风险，不构成投资建议，仅供学习交流用途。


## 中文摘要

- 用途：本文档围绕 `HkEquitySnapshotPipelines`，用于理解 `HkEquitySnapshotPipelines` 的配置、运行、部署、研究或验收边界。
- 主要覆盖：`Scope`、`Local build from sample data`、`Enablement status`、`Platform integration`。
- 阅读顺序：先确认边界、输入输出和权限要求，再执行文档里的命令、CI、dry-run、发布或切换步骤。
- 风险提示：涉及实盘、密钥、权限、Cloud Run、交易所或券商 API 的变更，必须先在测试环境或 dry-run 验证；不要只凭示例直接修改生产。
- 英文正文保留更完整的命令、字段名和配置键；如果摘要和正文不一致，以正文中的实际命令和配置为准。

## 中文

港股 snapshot 管线仓库，和非 snapshot 港股策略仓库 `HkEquityStrategies` 分开维护。

### 范围

本仓库定义可移植的 snapshot artifact contract、样例构建器和后续发布边界。它不提交订单，不保存券商凭据，也不负责 Cloud Run 切换。当前数据构建器是 scaffold/reference implementation，不是生产级港股数据源。

当前 snapshot scaffold 只覆盖 `hk_blue_chip_leader_rotation`：

- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv`
- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json`
- `hk_blue_chip_leader_rotation_ranking_latest.csv`
- `release_status_summary.json`

非 snapshot 港股策略，例如 `hk_listed_global_etf_rotation`，保留在 `HkEquityStrategies`，并直接使用 `market_history`，不经过本仓库发布 snapshot。

### 本地样例构建

```bash
PYTHONPATH=src python scripts/build_blue_chip_sample.py
```

或本地安装后调用 package entrypoint：

```bash
hkeq-build-blue-chip-leader-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output
```

### 启用状态

`hk_blue_chip_leader_rotation` 当前只是架构 scaffold。不要把这些样例 artifact 接入定时 Cloud Run 交易，除非同时满足：

- snapshot 数据源已验证；
- 策略包明确把对应 profile 提升为 `runtime_enabled`；
- 平台 dry-run 订单预览、lot-size、HKD 现金口径和人工审批都完成。

### 平台集成

如果未来 profile 被提升，先把 snapshot 和 manifest 发布到平台 runtime artifact 位置，然后设置：

- `IBKR_FEATURE_SNAPSHOT_PATH` and `IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH` for `InteractiveBrokersPlatform`.
- `LONGBRIDGE_FEATURE_SNAPSHOT_PATH` and `LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH` for `LongBridgePlatform`.

平台服务也必须运行在港股市场模式：

- IBKR: `IBKR_MARKET=HK`, `IBKR_MARKET_EXCHANGE=SEHK`, `IBKR_MARKET_CURRENCY=HKD`.
- LongBridge: `ACCOUNT_REGION=HK` or `LONGBRIDGE_MARKET=HK`.

## English

Feature-snapshot pipeline scaffold repository for QuantStrategyLab HK snapshot-backed profiles.

## Scope

This repository owns HK snapshot-backed artifact contracts, sample builders, and future publication boundaries. It is intentionally separate from the non-snapshot HK strategy repository. It does not submit orders, store broker credentials, or switch Cloud Run services. The current data builder is a scaffold/reference implementation, not a production HK data feed.

The current snapshot scaffold covers only `hk_blue_chip_leader_rotation`:

- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv`
- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json`
- `hk_blue_chip_leader_rotation_ranking_latest.csv`
- `release_status_summary.json`

Non-snapshot HK strategies such as `hk_listed_global_etf_rotation` stay in `HkEquityStrategies` and consume direct `market_history`; they do not publish snapshots through this repository.

## Local build from sample data

```bash
PYTHONPATH=src python scripts/build_blue_chip_sample.py
```

Or call the package entrypoint after installing locally:

```bash
hkeq-build-blue-chip-leader-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output
```

## Enablement status

`hk_blue_chip_leader_rotation` is currently an architecture scaffold. Do not wire these sample artifacts into scheduled Cloud Run trading until:

- the snapshot data source is validated;
- the strategy package explicitly promotes the profile to `runtime_enabled`;
- platform dry-run order previews, lot-size behavior, HKD cash handling, and operator approval are complete.

## Platform integration

After the profile is promoted, publish the snapshot and manifest to the platform runtime artifact location, then set:

- `IBKR_FEATURE_SNAPSHOT_PATH` and `IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH` for `InteractiveBrokersPlatform`.
- `LONGBRIDGE_FEATURE_SNAPSHOT_PATH` and `LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH` for `LongBridgePlatform`.

The platform service should also run in HK market mode:

- IBKR: `IBKR_MARKET=HK`, `IBKR_MARKET_EXCHANGE=SEHK`, `IBKR_MARKET_CURRENCY=HKD`.
- LongBridge: `ACCOUNT_REGION=HK` or `LONGBRIDGE_MARKET=HK`.
