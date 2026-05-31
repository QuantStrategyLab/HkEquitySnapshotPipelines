# HK Equity Snapshot Artifact Contract


## 中文摘要

- 用途：本文档围绕 `HK Equity Snapshot Artifact Contract`，用于理解 `HkEquitySnapshotPipelines` 的配置、运行、部署、研究或验收边界。
- 主要覆盖：`Profile`、`Files`、`Required snapshot columns`、`Runtime mapping`。
- 阅读顺序：先确认边界、输入输出和权限要求，再执行文档里的命令、CI、dry-run、发布或切换步骤。
- 风险提示：涉及实盘、密钥、权限、Cloud Run、交易所或券商 API 的变更，必须先在测试环境或 dry-run 验证；不要只凭示例直接修改生产。
- 英文正文保留更完整的命令、字段名和配置键；如果摘要和正文不一致，以正文中的实际命令和配置为准。

## Profile

`hk_blue_chip_leader_rotation`

> Current status: architecture scaffold. These contracts are stable enough for platform wiring tests, but not yet a production trading feed.

## Files

| Artifact | Filename |
| --- | --- |
| Feature snapshot | `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv` |
| Manifest | `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json` |
| Ranking preview | `hk_blue_chip_leader_rotation_ranking_latest.csv` |
| Release summary | `release_status_summary.json` |

## Required snapshot columns

- `symbol`: five-digit HK ticker without `.HK`, for example `00700`.
- `sector`
- `close_hkd`
- `adv20_hkd`
- `history_days`
- `mom_3m`
- `mom_6m`
- `mom_12_1`
- `rel_mom_6m_vs_benchmark`
- `high_252_gap`
- `sma200_gap`
- `vol_63`
- `maxdd_126`

Optional columns: `as_of`, `snapshot_date`, `eligible`, `market_cap_hkd`, `lot_size`.

## Runtime mapping

- IBKR should use `SEHK` + `HKD` for contracts and `.HK` only for yfinance fallback.
- LongBridge should use `.HK` market-data symbols and `HKD` cash reporting.
- Both platforms should point their feature snapshot and manifest env vars to the published files above.
