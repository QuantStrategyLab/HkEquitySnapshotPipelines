# HK Equity Snapshot Artifact Contract

## Profile

`hk_blue_chip_leader_rotation`

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
