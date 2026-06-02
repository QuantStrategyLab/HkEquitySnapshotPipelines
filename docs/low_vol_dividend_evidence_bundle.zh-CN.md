# 港股低波红利生产证据 Bundle

[English version](./low_vol_dividend_evidence_bundle.md)

该 bundle 是 `hk_low_vol_dividend_quality` live-enable evidence package 之后的下一步。
它为 operator 生成 production source audit、walk-forward backtest、quality/yield policy evidence 和平台 live-enable evidence 模板。

该 bundle 仍然不是 live。不能用它移除 `LONGBRIDGE_DRY_RUN_ONLY=true` 或 `IBKR_DRY_RUN_ONLY=true`。

## 生成模板

```bash
python scripts/build_low_vol_dividend_evidence_bundle.py
```

该命令会写入：

- `data/output/low_vol_dividend_evidence_bundle/low_vol_dividend_evidence_bundle.json`
- `data/output/low_vol_dividend_evidence_bundle/README.md`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/production_source_audit.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/walk_forward_backtest.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/quality_yield_strategy_policy_evidence.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/longbridge_live_enablement_evidence.template.json`
- `data/output/low_vol_dividend_evidence_bundle/evidence_templates/ibkr_live_enablement_evidence.template.json`

## Evidence 要求

Operator 必须把 pending 模板字段替换为已验证证据：

- point-in-time dividend、forecast dividend yield、trailing yield、payout、volatility、financial-soundness 和 Southbound eligibility history；
- 不允许使用当前成分股回填历史 universe、未来财务数据、交易后数据或全样本参数搜索；
- walk-forward backtest 至少 3 个 OOS folds、最大回撤 `<= 30%`、年化收益为正、benchmark excess return 为正、换手 `<= 100%`，并扣除港股成本；
- LongBridge 和 IBKR dry-run order preview 必须包含 raw preview、quotes、fee breakdown、sha256 provenance、双语通知证据和 delivery logs。
