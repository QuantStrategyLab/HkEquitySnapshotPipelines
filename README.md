# HkEquitySnapshotPipelines

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
