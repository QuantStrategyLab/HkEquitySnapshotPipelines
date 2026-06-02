# 港股低波红利 Walk-Forward 回测证据草稿

[English version](./low_vol_dividend_backtest_evidence.md)

该工具用于为 `hk_low_vol_dividend_quality` 生成 `walk_forward_backtest` evidence 草稿。
它接收 operator 提供的 walk-forward summary JSON，并在本地检查主要 live-enable 门槛。

它不会运行生产回测，不会把 evidence 标记为 passed，也不会 live-enable 策略。

## 命令

```bash
python scripts/draft_low_vol_dividend_backtest_evidence.py \
  --summary <walk-forward-summary.json> \
  --evidence-uri gs://.../backtest.json
```

summary JSON 必须包含 period、annual return、drawdown、OOS fold count、turnover、benchmark、excess return、港股成本控制、no-lookahead 控制、survivorship 控制和压力测试控制。

生成的草稿会保持 `status: pending`，直到完整报告、fold metrics、参数敏感性、成本模型和 point-in-time/no-lookahead evidence 都补齐。
