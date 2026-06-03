# First HK Snapshot Promotion Runbook

[Chinese version](./first_snapshot_promotion_runbook.zh-CN.md)

This runbook narrows HK snapshot promotion work to one retained evidence-gated candidate:

1. `hk_low_vol_dividend_quality_snapshot`

Other snapshot scaffolds were rejected or removed from package entrypoints after proxy triage. This runbook does not live-enable the retained profile, publish production artifacts, deploy Cloud Run, or place broker orders.

## Why this profile first

`hk_low_vol_dividend_quality_snapshot` is a lower-turnover quality/yield candidate that fits the current HK risk objective better than event, flow, AH-premium, or high-turnover momentum scaffolds, and it passed the proxy long/medium/short 30% drawdown gate. It must still prove max drawdown `<= 30%`, at least three independent out-of-sample folds, net-of-cost performance, HK liquidity/capacity, artifact provenance, dry-run order preview, bilingual notification evidence, and operator approval with real point-in-time data.

## Print the promotion plan

Use the plan command as the source of truth for the first batch:

```bash
python scripts/print_first_snapshot_promotion_plan.py --json
```

Limit to one profile or one platform when needed:

```bash
python scripts/print_first_snapshot_promotion_plan.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

The command is read-only. It only prints planned commands, artifact filenames, readiness templates, evidence gates, and blocking reasons.

## Promotion sequence

### 1. Sample artifact smoke

Build sample artifacts only to verify local contract wiring:

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

Sample artifacts are not production data and must not drive scheduled trading.

### 2. Production source audit

Replace sample inputs with point-in-time production data. At minimum, evidence must cover:

- source coverage start/end and data dictionary
- source quality report URI
- corporate actions, suspensions, stale quotes, missing fields, and symbol mapping
- reporting-date / availability-date lineage for fundamentals
- dividend, payout, volatility, liquidity, corporate-action, suspension, ROE/FCF optional quality-field, and sector lineage
- no secret-like query parameters in evidence URIs

### 3. Walk-forward backtest

Run survivorship-safe walk-forward backtests before any platform dry-run promotion:

- at least 3 independent out-of-sample folds
- max drawdown `<= 30%`, or stricter profile threshold if configured
- annual return / max drawdown ratio `>= 0.50`
- max single-period return contribution `<= 60%`
- annualized turnover `<= 100%` for the retained quality/yield candidate
- HK fees, levies, slippage, bid/ask spread, lot-size, suspension, VCM, CAS, and capacity stress
- same-universe ablation against rejected quality/yield variants before adding any new snapshot contract

### 4. Artifact-pack validation

Validate the published artifact directory:

```bash
hkeq-validate-snapshot-artifact-pack \
  --profile hk_low_vol_dividend_quality_snapshot \
  --artifact-dir data/output/hk_low_vol_dividend_quality_snapshot \
  --json
```

Rejected profiles are not validated here because they are no longer package contracts.

### 5. Platform dry-run evidence

Print readiness templates before platform wiring:

```bash
python scripts/print_snapshot_readiness.py \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json
```

Generate the evidence template:

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality_snapshot \
  --platform longbridge \
  --json > snapshot-live-enable-evidence.json
```

Validate completed evidence:

```bash
hkeq-validate-live-enable-evidence \
  --evidence-file snapshot-live-enable-evidence.json \
  --json
```

Dry-run evidence must include raw order preview, quote snapshot, fee breakdown, sha256 provenance, bilingual EN/ZH-Hans notification payloads, delivery-log URI, operator approval reference, staged rollout, tripwires, kill switch, and rollback plan.

## Profile-specific focus

| Profile | Focus before promotion |
| --- | --- |
| `hk_low_vol_dividend_quality_snapshot` | Forecast versus trailing dividend yield ablation, yield-trap controls, Southbound eligibility, three-year cash-dividend records, payout-ratio bounds, price-crash screens, high-volatility exclusion, and financial-soundness screens. |

## Stop conditions

Do not promote a profile if any of these are true:

- sample artifacts are being used as production data
- evidence URIs contain token/password/signature-like query parameters
- fewer than 3 independent OOS folds are available
- any OOS fold exceeds the drawdown gate
- fee/slippage/spread stress turns excess return non-positive
- artifact manifest sha256 does not match the published snapshot
- dry-run order preview or bilingual notification evidence is missing
- operator approval and rollback plan are missing
