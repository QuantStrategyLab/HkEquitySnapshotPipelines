# 港股低波红利 Live-Enable 证据包

[English version](./low_vol_dividend_live_enablement_package.md)

本文档定义 `hk_low_vol_dividend_quality` 的首个 live-enable evidence package。
它不会 live-enable 策略、不会部署 Cloud Run、不会发布生产 artifact，也不会下券商订单。

## 为什么先推进这个 profile

`hk_low_vol_dividend_quality` 是首个港股 snapshot 候选，因为它属于低换手的质量/收益类 profile。
相比事件、AH 溢价、资金流或高换手动量 scaffold，它更容易控制回撤、换手和港股执行摩擦。

## Package 命令

本地生成 package：

```bash
python scripts/build_low_vol_dividend_live_enablement_package.py
```

只打印 JSON、不写文件：

```bash
python scripts/build_low_vol_dividend_live_enablement_package.py --json
```

生成文件位于 `data/output/low_vol_dividend_live_enablement_package`：

- `low_vol_dividend_live_enablement_package.json`
- `low_vol_dividend_live_enablement_package.md`

## Evidence gates

任何 live-enable 变更前，必须补齐：

- point-in-time 生产数据源审计；
- 无未来函数、无幸存者偏差；
- 至少 3 个独立 OOS folds；
- 最大回撤 `<= 30%`；
- 扣除港股成本、费用、价差、滑点、board-lot、停牌、VCM、CAS 和容量压力后仍有正超额收益；
- snapshot artifact-pack validation；
- LongBridge 和 IBKR dry-run order preview；
- 使用统一通知格式的 EN/ZH-Hans 双语通知证据；
- 人工审批、tripwire、kill switch 和 rollback plan。

## 明确非 live 状态

该 package 会显式输出：

- `runtime_enabled: false`
- `live_enablement_allowed: false`
- `production_deployment_allowed: false`
- `dry_run_only_until_all_gates_pass: true`

不要用这个 package 移除平台 dry-run 控制。
