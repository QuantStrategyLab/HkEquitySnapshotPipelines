# HK Low-Vol Dividend Walk-Forward Backtest Evidence Draft

[中文版本](./low_vol_dividend_backtest_evidence.zh-CN.md)

This tool drafts the `walk_forward_backtest` evidence section for `hk_low_vol_dividend_quality`.
It accepts an operator-supplied walk-forward summary JSON and checks the main live-enable gates locally.

It does not run a production backtest, does not mark the evidence as passed, and does not live-enable the strategy.

## Command

```bash
python scripts/draft_low_vol_dividend_backtest_evidence.py \
  --summary <walk-forward-summary.json> \
  --evidence-uri gs://.../backtest.json
```

The summary JSON must include period, annual return, drawdown, OOS fold count, turnover, benchmark, excess return, HK cost controls, no-lookahead controls, survivorship controls, and stress controls.

The generated draft remains `status: pending` until the full report, fold metrics, parameter sensitivity, cost model, and point-in-time/no-lookahead evidence are attached.
