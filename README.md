# HkEquitySnapshotPipelines

> ⚠️ 投资有风险，不构成投资建议，仅供学习交流用途。


## 中文摘要

- 用途：本文档围绕 `HkEquitySnapshotPipelines`，用于理解 `HkEquitySnapshotPipelines` 的配置、运行、部署、研究或验收边界。
- 主要覆盖：`Scope`、`Local build from sample data`、`Enablement status`、`Platform integration`。
- 阅读顺序：先确认边界、输入输出和权限要求，再执行文档里的命令、CI、dry-run、发布或切换步骤。
- 风险提示：涉及实盘、密钥、权限、Cloud Run、交易所或券商 API 的变更，必须先在测试环境或 dry-run 验证；不要只凭示例直接修改生产。
- 英文正文保留更完整的命令、字段名和配置键；如果摘要和正文不一致，以正文中的实际命令和配置为准。
Feature-snapshot pipeline scaffold repository for `HkEquityStrategies`.

## Scope

This repository defines the portable snapshot artifact contract and sample builder. It does not submit orders and does not store broker credentials. The current data builder is a scaffold/reference implementation, not a production HK data feed.

The first pipeline scaffold builds `hk_blue_chip_leader_rotation` artifacts:

- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv`
- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json`
- `hk_blue_chip_leader_rotation_ranking_latest.csv`
- `release_status_summary.json`

## Local build from sample data

```bash
PYTHONPATH=../HkEquityStrategies/src:src python scripts/build_blue_chip_sample.py
```

Or call the package entrypoint after installing locally:

```bash
hkeq-build-blue-chip-leader-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output
```

## Enablement status

`hk_blue_chip_leader_rotation` is currently an architecture scaffold. Do not wire these sample artifacts into scheduled Cloud Run trading until the strategy package is promoted to `runtime_enabled` and the data source is validated.

## Platform integration

After the profile is promoted, publish the snapshot and manifest to the platform runtime artifact location, then set:

- `IBKR_FEATURE_SNAPSHOT_PATH` and `IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH` for `InteractiveBrokersPlatform`.
- `LONGBRIDGE_FEATURE_SNAPSHOT_PATH` and `LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH` for `LongBridgePlatform`.

The platform service should also run in HK market mode:

- IBKR: `IBKR_MARKET=HK`, `IBKR_MARKET_EXCHANGE=SEHK`, `IBKR_MARKET_CURRENCY=HKD`.
- LongBridge: `ACCOUNT_REGION=HK` or `LONGBRIDGE_MARKET=HK`.
