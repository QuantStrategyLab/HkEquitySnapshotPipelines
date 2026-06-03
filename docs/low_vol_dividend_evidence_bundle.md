# HK Low-Vol Dividend Production Evidence Bundle

[中文版本](./low_vol_dividend_evidence_bundle.zh-CN.md)

This bundle is the next step after the live-enable evidence package for `hk_low_vol_dividend_quality_snapshot`.
It creates operator-facing templates for production source audit, walk-forward backtest, quality/yield policy evidence, and platform live-enable evidence.

The bundle is still non-live. It must not remove `LONGBRIDGE_DRY_RUN_ONLY=true` or `IBKR_DRY_RUN_ONLY=true`.

## Generate templates

```bash
python scripts/build_low_vol_dividend_evidence_bundle.py
```

The command writes:

- `data/output/low_vol_dividend_evidence_bundle/low_vol_dividend_evidence_bundle.json`
- `data/output/low_vol_dividend_evidence_bundle/README.md`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/production_source_audit.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/walk_forward_backtest.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/quality_yield_strategy_policy_evidence.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/longbridge_live_enablement_evidence.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/ibkr_live_enablement_evidence.template.json`

## Evidence requirements

The operator must replace pending template fields with validated evidence:

- point-in-time dividend, forecast dividend yield, trailing yield, payout, volatility, financial-soundness and Southbound eligibility history;
- no current-constituent historical universe, future financials, post-trade data, or full-sample parameter search;
- walk-forward backtest with at least three OOS folds, max drawdown `<= 30%`, positive annual return, positive benchmark excess return, turnover `<= 100%`, and net HK costs;
- LongBridge and IBKR dry-run order previews with raw preview, quotes, fee breakdown, sha256 provenance, bilingual notification evidence, and delivery logs.
