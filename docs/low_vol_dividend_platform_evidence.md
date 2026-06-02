# HK Low-Volatility Dividend Quality Platform Evidence Draft

[中文版本](./low_vol_dividend_platform_evidence.zh-CN.md)

This tool turns a platform dry-run runtime report into a draft `platform_dry_run_order_preview` evidence section for `hk_low_vol_dividend_quality`.
It supports LongBridge and IBKR.
For IBKR, the CLI uses `--platform ibkr` while accepting runtime reports whose top-level `platform` is either `ibkr` or the platform runtime ID `interactive_brokers`.

The command does not deploy Cloud Run, place orders, upload artifacts, or approve live trading.
It keeps the full evidence pack blocked until the production source, artifact, backtest, broker permission, rebalance window, rollout, risk approval, and strategy-policy sections are also complete.

## Usage

First collect support artifacts from a real platform dry-run runtime report:

```bash
python scripts/collect_low_vol_dividend_dry_run_support_artifacts.py \
  --platform longbridge \
  --runtime-report runtime-report.json \
  --evidence-generated-at 2026-06-03 \
  --output-dir evidence/low_vol_dividend_quality/support \
  --json
```

The collector writes `raw_order_preview`, `quote_snapshot`, and `fee_breakdown` support files.
It does not fabricate missing evidence: generated quote or fee files are marked `missing` unless the runtime report already contains a complete payload.
Files marked `missing` keep the platform evidence section `pending`, even if confirmation flags are supplied later.

Then draft the platform evidence:

```bash
python scripts/draft_low_vol_dividend_platform_evidence.py \
  --platform longbridge \
  --runtime-report runtime-report.json \
  --runtime-report-uri gs://.../runtime-report.json \
  --quote-snapshot-file quotes.json \
  --quote-snapshot-uri gs://.../quotes.json \
  --fee-breakdown-file fees.json \
  --fee-breakdown-uri gs://.../fees.json \
  --notification-delivery-log-uri gs://.../notification-log.json \
  --notification-correlation-id run-001 \
  --orders-previewed 2 \
  --adv-window-trading-days 20 \
  --median-daily-turnover-hkd 50000000 \
  --max-single-order-adv-fraction 0.01 \
  --rebalance-adv-fraction 0.05 \
  --confirm-order-preview-provenance \
  --confirm-notification-audit \
  --confirm-execution-capacity \
  --evidence-generated-at 2026-06-03
```

Use `--base-evidence-file` when production source, artifact, backtest, broker permission, rollout, risk approval, and strategy-policy sections already exist and should be copied into the output evidence file.

## Passing behavior

The platform dry-run section is marked `passed` only when:

- the runtime report is `dry_run=true`, `status=ok`, and matches the requested platform/profile;
- the previewed order count is positive;
- fractional-share and lot-size errors are zero;
- stable runtime-report, quote-snapshot, fee-breakdown, and notification-log URIs are provided;
- local quote and fee files are provided so sha256 provenance can be computed;
- generated support-artifact files, when used, are marked `status=passed`;
- order-preview provenance, notification audit, and execution-capacity confirmations are explicitly supplied.

Even if the platform dry-run section is `passed`, the full evidence file can still fail validation until every other live-enable evidence gate is complete.
