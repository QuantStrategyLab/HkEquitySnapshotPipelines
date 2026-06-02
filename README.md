# HkEquitySnapshotPipelines

> ⚠️ 投资有风险，不构成投资建议，仅供学习交流用途。


## 中文摘要

- 用途：本文档围绕 `HkEquitySnapshotPipelines`，用于理解 `HkEquitySnapshotPipelines` 的配置、运行、部署、研究或验收边界。
- 主要覆盖：`Scope`、`Local build from sample data`、`Enablement status`、`Platform integration`。
- 阅读顺序：先确认边界、输入输出和权限要求，再执行文档里的命令、CI、dry-run、发布或切换步骤。
- 风险提示：涉及实盘、密钥、权限、Cloud Run、交易所或券商 API 的变更，必须先在测试环境或 dry-run 验证；不要只凭示例直接修改生产。
- 英文正文保留更完整的命令、字段名和配置键；如果摘要和正文不一致，以正文中的实际命令和配置为准。

## 中文

港股 snapshot 管线仓库，和非 snapshot 港股策略仓库 `HkEquityStrategies` 分开维护。

### 范围

本仓库定义可移植的 snapshot artifact contract、样例构建器和后续发布边界。它不提交订单，不保存券商凭据，也不负责 Cloud Run 切换。当前数据构建器是 scaffold/reference implementation，不是生产级港股数据源。

当前 snapshot scaffold 覆盖：

#### `hk_ah_premium_relative_value`

- `hk_ah_premium_relative_value_valuation_snapshot_latest.csv`
- `hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json`
- `hk_ah_premium_relative_value_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_blue_chip_leader_rotation`

- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv`
- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json`
- `hk_blue_chip_leader_rotation_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_composite_factor_quality_value_momentum`

- `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv`
- `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json`
- `hk_composite_factor_quality_value_momentum_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_factor_mix_qvlm_risk_parity`

- `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv`
- `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv.manifest.json`
- `hk_factor_mix_qvlm_risk_parity_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_central_soe_value_quality_select`

- `hk_central_soe_value_quality_select_factor_snapshot_latest.csv`
- `hk_central_soe_value_quality_select_factor_snapshot_latest.csv.manifest.json`
- `hk_central_soe_value_quality_select_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_free_cash_flow_quality`

- `hk_free_cash_flow_quality_factor_snapshot_latest.csv`
- `hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_free_cash_flow_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_index_rebalance_event`

- `hk_index_rebalance_event_event_calendar_snapshot_latest.csv`
- `hk_index_rebalance_event_event_calendar_snapshot_latest.csv.manifest.json`
- `hk_index_rebalance_event_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_low_vol_dividend_quality`

- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_quality_growth_low_volatility`

- `hk_quality_growth_low_volatility_factor_snapshot_latest.csv`
- `hk_quality_growth_low_volatility_factor_snapshot_latest.csv.manifest.json`
- `hk_quality_growth_low_volatility_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_liquid_momentum_quality`

- `hk_liquid_momentum_quality_feature_snapshot_latest.csv`
- `hk_liquid_momentum_quality_feature_snapshot_latest.csv.manifest.json`
- `hk_liquid_momentum_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_residual_momentum_quality`

- `hk_residual_momentum_quality_factor_snapshot_latest.csv`
- `hk_residual_momentum_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_residual_momentum_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_shareholder_yield_quality`

- `hk_shareholder_yield_quality_factor_snapshot_latest.csv`
- `hk_shareholder_yield_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_shareholder_yield_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_southbound_flow_momentum`

- `hk_southbound_flow_momentum_flow_snapshot_latest.csv`
- `hk_southbound_flow_momentum_flow_snapshot_latest.csv.manifest.json`
- `hk_southbound_flow_momentum_ranking_latest.csv`
- `release_status_summary.json`

非 snapshot 港股策略，例如 `hk_listed_global_etf_rotation`，保留在 `HkEquityStrategies`，并直接使用 `market_history`，不经过本仓库发布 snapshot。

后续 snapshot 候选研究记录在 `docs/research/hk_snapshot_strategy_candidates.md`。`hk_low_vol_dividend_quality`、`hk_liquid_momentum_quality`、`hk_composite_factor_quality_value_momentum`、`hk_factor_mix_qvlm_risk_parity`、`hk_central_soe_value_quality_select`、`hk_quality_growth_low_volatility`、`hk_residual_momentum_quality`、`hk_shareholder_yield_quality`、`hk_free_cash_flow_quality`、`hk_southbound_flow_momentum`、`hk_ah_premium_relative_value` 和 `hk_index_rebalance_event` 已有可测试 scaffold，但还没有 production 数据源，也没有 live-enabled。

### 本地样例构建

```bash
PYTHONPATH=src python scripts/build_blue_chip_sample.py
```

或本地安装后调用 package entrypoint：

```bash
hkeq-build-blue-chip-leader-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output
```

`hk_liquid_momentum_quality` 复用相同的样例价格和 universe 输入，但写出自己的 artifact 文件名：

```bash
PYTHONPATH=src python scripts/build_liquid_momentum_sample.py
```

生成的 feature snapshot 同时包含 `high_63_gap` 和 `high_252_gap`，用于验证港股动量研究中的短/长周期 price-to-recent-high 形态；`high_63_gap` 仍保持 optional 以兼容旧 contract。

或：

```bash
hkeq-build-liquid-momentum-quality-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output/liquid_momentum_quality
```

`hk_residual_momentum_quality` 是更接近美股横截面动量因子的单股票 snapshot scaffold。它不直接从价格样例推导，而是要求上游因子引擎提供 residual / industry-neutral momentum、行业相对动量、beta、波动率和回撤字段：

```bash
PYTHONPATH=src python scripts/build_residual_momentum_sample.py
```

或：

```bash
hkeq-build-residual-momentum-quality-snapshot \
  --factor-snapshot examples/residual_momentum_quality/factor_snapshot.sample.csv \
  --output-dir data/output/residual_momentum_quality
```

`hk_shareholder_yield_quality` 需要外部提供股息、回购、总股本变化、FCF、ROE、负债和风险字段。它是低换手股东回报/质量 scaffold，不是 production 披露抓取器：

```bash
PYTHONPATH=src python scripts/build_shareholder_yield_sample.py
```

或：

```bash
hkeq-build-shareholder-yield-quality-snapshot \
  --factor-snapshot examples/shareholder_yield_quality/factor_snapshot.sample.csv \
  --output-dir data/output/shareholder_yield_quality
```

`hk_low_vol_dividend_quality` 需要 factor snapshot 输入，因为股息、盈利、beta 和派息字段不能只从价格推导：

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

或：

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --output-dir data/output/low_vol_dividend_quality
```

`hk_quality_growth_low_volatility` 需要外部提供 growth、quality、valuation 和 low-volatility factor snapshot；它是质量成长低波 scaffold，不是 production fundamentals 数据源。live-enable 前必须能追溯 HSI QGLV 官方四因子（ROE、Accruals Ratio、Cash Flow-to-Debt、Growth in ROA adjusted by P/B）、winsorized z-score / component averaging、Financials / negative-equity / missing-factor 处理，以及 HSI low-volatility quality screen 和 MSCI quality descriptors：

```bash
PYTHONPATH=src python scripts/build_quality_growth_low_volatility_sample.py
```

或：

```bash
hkeq-build-quality-growth-low-volatility-snapshot \
  --factor-snapshot examples/quality_growth_low_volatility/factor_snapshot.sample.csv \
  --output-dir data/output/quality_growth_low_volatility
```

`hk_composite_factor_quality_value_momentum` 需要更完整的 factor snapshot，覆盖质量、价值、动量、低波动和港股通 eligible 字段。它是港股单股票多因子选股框架的 scaffold；在具备 production factor 数据源和 walk-forward 证据前仍不能 live-enabled：

```bash
PYTHONPATH=src python scripts/build_composite_factor_sample.py
```

或：

```bash
hkeq-build-composite-factor-qvm-snapshot \
  --factor-snapshot examples/composite_factor_quality_value_momentum/factor_snapshot.sample.csv \
  --output-dir data/output/composite_factor_quality_value_momentum
```

`hk_factor_mix_qvlm_risk_parity` 需要外部提供 quality / value / momentum / low-volatility 因子分数和 factor-volatility snapshot；它是 QVLM risk-parity 多因子 scaffold，不是 production factor 数据源。live-enable 前还必须追溯 HSI QVLM parent universe、四个 component-index return history、risk-parity 权重、12% capping、MSCI Factor Mix A-Series 等权 Q/V/L component 和 capped methodology：

```bash
PYTHONPATH=src python scripts/build_factor_mix_qvlm_risk_parity_sample.py
```

或：

```bash
hkeq-build-factor-mix-qvlm-risk-parity-snapshot \
  --factor-snapshot examples/factor_mix_qvlm_risk_parity/factor_snapshot.sample.csv \
  --output-dir data/output/factor_mix_qvlm_risk_parity
```

`hk_central_soe_value_quality_select` 需要外部提供 central-SOE / government largest-shareholder 分类、ownership pct、value / quality / low-vol / momentum 因子、股息收益和风险字段；它是港股政策价值/央国企质量选股 scaffold，不是 production SOE 分类或 fundamentals 数据源。live-enable 前必须追溯 SASAC/MOF source-list effective-date drift、largest-shareholder look-through、HSI Z-score / missing-measure / 40% screening / buffer rules、5% factor-index cap 和 10% base-index cap：

```bash
PYTHONPATH=src python scripts/build_central_soe_value_quality_sample.py
```

或：

```bash
hkeq-build-central-soe-value-quality-select-snapshot \
  --factor-snapshot examples/central_soe_value_quality_select/factor_snapshot.sample.csv \
  --output-dir data/output/central_soe_value_quality_select
```

`hk_free_cash_flow_quality` 需要外部提供 FCF / EV / ROE / reporting-date 可用性等 fundamentals snapshot；live-enable 还要求 FCF 公式口径、EV 的市值/债务/现金/FX 输入、restatement/as-of、sector normalization 以及金融/地产/负 FCF 例外策略可审计。它是 FCF yield 质量价值 scaffold，不是 production fundamentals 数据源：

```bash
PYTHONPATH=src python scripts/build_free_cash_flow_sample.py
```

或：

```bash
hkeq-build-free-cash-flow-quality-snapshot \
  --factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv \
  --output-dir data/output/free_cash_flow_quality
```

`hk_southbound_flow_momentum` 需要外部提供 southbound flow snapshot，因为港股通净买入、top-10 turnover、CCASS 南向持仓占比、eligible-stock 变更和持仓变化不能只从价格推导；live-enable 前还要校验 HKEX data-dissemination change 和 raw-vs-vendor reconciliation：

```bash
PYTHONPATH=src python scripts/build_southbound_flow_sample.py
```

或：

```bash
hkeq-build-southbound-flow-momentum-snapshot \
  --flow-snapshot examples/southbound_flow_momentum/flow_snapshot.sample.csv \
  --output-dir data/output/southbound_flow_momentum
```

`hk_ah_premium_relative_value` 需要外部提供 A/H 溢价和 H 股趋势 snapshot，因为 A 股价格、H 股价格、FX、adjusted market cap、互联互通 eligible 状态和 AH Smart-style switch thresholds 不能只从 H 股价格推导；live-enable 前还要审计极端溢价假反转、A 股准入、卖空、结算和 FX 约束：

```bash
PYTHONPATH=src python scripts/build_ah_premium_sample.py
```

或：

```bash
hkeq-build-ah-premium-relative-value-snapshot \
  --valuation-snapshot examples/ah_premium_relative_value/valuation_snapshot.sample.csv \
  --output-dir data/output/ah_premium_relative_value
```

`hk_index_rebalance_event` 需要外部提供指数审查 event calendar snapshot，因为公告日、有效日、候选加入/剔除概率和滑点估计不能只从价格推导：

```bash
PYTHONPATH=src python scripts/build_index_rebalance_event_sample.py
```

或：

```bash
hkeq-build-index-rebalance-event-snapshot \
  --event-snapshot examples/index_rebalance_event/event_snapshot.sample.csv \
  --output-dir data/output/index_rebalance_event
```

### 研究回测样例

`hk_liquid_momentum_quality` 还没有 production 数据源；当前只提供本地 CSV research harness，用来验证 snapshot 生成、调仓、交易成本和指标计算链路：

```bash
PYTHONPATH=src python scripts/research_hk_liquid_momentum_quality_backtest.py \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv
```

输出中的 `research_status=sample_harness_only_not_production_backtest` 表示这不是生产级历史回测。

### 启用状态

`hk_blue_chip_leader_rotation`、`hk_low_vol_dividend_quality`、`hk_liquid_momentum_quality`、`hk_composite_factor_quality_value_momentum`、`hk_factor_mix_qvlm_risk_parity`、`hk_central_soe_value_quality_select`、`hk_residual_momentum_quality`、`hk_shareholder_yield_quality`、`hk_free_cash_flow_quality`、`hk_southbound_flow_momentum`、`hk_ah_premium_relative_value` 和 `hk_index_rebalance_event` 当前都只是架构 scaffold。不要把这些样例 artifact 接入定时 Cloud Run 交易，除非同时满足：

- snapshot 数据源已验证；
- 策略包明确把对应 profile 提升为 `runtime_enabled`；
- 平台 dry-run 订单预览、lot-size、HKD 现金口径和人工审批都完成。


优先用 promotion matrix 确认候选优先级、研究依据、数据依赖和 live-enable 缺口：

```bash
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --json
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --profile hk_shareholder_yield_quality --json
```

matrix 还会输出 `backtest_validation_policy`，作为所有港股策略的统一回测门槛：最大回撤不得超过 30%（profile 有更严格阈值时按更严格阈值）、必须使用 point-in-time 输入、禁止未来函数和 survivorship bias、禁止按全样本最优收益选参、必须有 walk-forward / OOS 和多周期稳健性、每个 OOS fold 最大回撤 <= 30%、年化收益/最大回撤比至少 0.50、参数敏感性/holdout 稳定性、净收益扣费、费用/滑点/价差压力后仍有正超额收益、最差月/最差调仓损失和 time-under-water 恢复约束、与现有 live profile 的相关性及组合级风险预算、熊市/震荡/低流动性压力，并覆盖 HK 成本、滑点、lot-size、停牌、VCM/CAS、杠杆/做空/融资可行性与容量约束。matrix 还会输出 `recommended_live_enablement_sequence`、每个 profile 的 `recommended_live_enablement_stage` 和 `next_live_enablement_action`。当前顺序仍然是先做低波红利、股东收益、FCF 质量这三个低换手质量/收益候选；动量因子候选保留在后续研究阶段，并需要额外证明 HSI close-to-high descriptor、MSCI 6/12 个月 one-month-skip risk-adjusted momentum、volatility normalization、turnover buffer、sector/capacity 和 momentum-crash 控制。`baseline_rotation_live_enablement_policy` 会约束 `hk_blue_chip_leader_rotation` 这个基线轮动 scaffold：必须证明 HSI 成分股/复核方法论、点时间价格、基准相对动量、52 周高点、sector/liquidity、board-lot、VCM/CAS 和交易时段规则 provenance，并完成相对动量 vs HSI tracker / liquid momentum / 52-week-high / sector-neutral / rebalance-buffer ablation 后，才允许移除 dry-run。`quality_yield_live_enablement_policy` 会约束首批质量/收益候选；live-enable evidence validator 现在还会对这些 profile 条件要求 `strategy_policy_evidence`，必须证明 policy version、stable evidence URI、fresh `evidence_generated_at`、同 universe ablation、stress tests 和 data-provenance flags 全部通过。具体来说，必须在同一 survivorship-safe universe 上比较 low-vol dividend、shareholder yield 和 FCF 三种信号，证明 forecast dividend yield estimate history、forecast vs trailing yield ablation、stale estimate-revision controls、dividend yield trap、港股通 eligible universe、连续三年现金分红、payout-ratio bounds、price-crash / bottom-decile screen、大中盘市值 shortlist、一年高波动剔除、financial-soundness screen、派息覆盖、回购金额与实际股本减少、HKEX next-day repurchase returns、treasury-share retention/cancellation/resale、moratorium/blackout/connected-person controls、post-buyback financing / convertible / public-float review、treasury-share resale / dilution、FCF reporting-date / restatement、sector concentration 和 rate-cycle stress 都已通过，再允许移除 dry-run。`momentum_live_enablement_comparison` 会单独比较 residual / liquid / composite 三种形态；同一 `momentum_live_enablement_policy` 也会出现在 per-profile readiness、live-enable evidence template 和 validator result 中；live-enable evidence validator 现在还会对这些动量 profile 条件要求 `strategy_policy_evidence`，必须证明 policy version、stable evidence URI、fresh `evidence_generated_at`、动量 ablation、stress tests 和 data-provenance flags 全部通过，避免平台工具把动量 profile 当成普通 snapshot scaffold 处理：`hk_residual_momentum_quality` 是最接近美股横截面动量因子选股的首选动量候选，`hk_liquid_momentum_quality` 是数据更容易落地的价格动量 fallback，`hk_composite_factor_quality_value_momentum` 则需要 factor ablation 证明 momentum sleeve 本身有效后再考虑。`special_situation_live_enablement_policy` 会约束南向资金、AH 溢价和指数调仓这三个港股特殊情形候选：必须证明 HKEX / Hang Seng 官方来源、Stock Connect 日历和持仓/成交、AH close-time / FX 对齐、HSI 指数方法论 / operation guide / regular rebalancing schedule / next-review notice / review-result press release provenance、指数 review announcement-to-effective window、add/delete labels、fast-entry / suspension / buffer-rule exceptions、HKEX CAS / market-on-close order constraints、signal decay、crowding / slippage stress 和 dry-run order-preview provenance 后，才允许考虑移除 dry-run。`quality_growth_live_enablement_policy` 会约束 `hk_quality_growth_low_volatility` scaffold：必须证明 quality/growth/low-volatility 因子拆解、HSI QGLV 官方四因子（ROE、Accruals Ratio、Cash Flow-to-Debt、Growth in ROA adjusted by P/B）、winsorized z-score / component averaging、Financials / negative-equity / missing-factor 处理、MSCI quality ROE / stable earnings / low leverage 对齐、HSI low-vol quality screen、minimum-volatility optimizer constraints、cash-conversion / accrual quality-trap controls、Southbound universe、sector-neutral、real-estate/financial concentration、growth deceleration、valuation/regulation/low-vol crowding stress、生产 fundamentals reporting-date 和 dry-run order-preview provenance。`factor_mix_live_enablement_policy` 会约束新增的 `hk_factor_mix_qvlm_risk_parity` scaffold：必须证明 Q/V/L/M 因子历史、HSI QVLM parent universe、component-index returns、risk-parity weight / 12% cap lineage、factor-volatility 和 covariance/correlation 历史、HSI equal-weight factor-mix benchmark、MSCI Factor Mix A-Series equal-weight Q/V/L component 和 capped methodology controls、同 universe 的 equal-weight / composite QVM / leave-one-out / component-overlap ablation、factor crowding / factor-correlation breakdown / momentum crash / value trap / low-vol reversal / cap-induced turnover stress、HK 成本容量和 dry-run order-preview provenance。`policy_value_live_enablement_policy` 会约束新增的 `hk_central_soe_value_quality_select` scaffold：必须证明 point-in-time central-SOE largest-shareholder/ownership 分类、SASAC/MOF source-list effective dates 和 effective-date drift、largest-shareholder look-through chain、HKEX Southbound eligible-security history、HSI Central SOEs value/quality factor-index constituent / Z-score / missing-measure averaging / 40% screening / buffer rules / 5% 与 10% capping lineage、value-quality 与 broad value-quality / HSI value-quality / existing quality-yield 的同 universe ablation、sector concentration、policy-event / SOE reform / parent restructuring / eligibility removal / connected-transaction / sanction / dividend-cut / cap-turnover stress、HK 成本容量和 dry-run order-preview provenance。`future_research_backlog` 现在收录十七个 research-only 候选：`hk_earnings_revision_quality_overlay` 只能作为 quality/value/low-vol/dividend/FCF 的盈利预期修正 overlay，不能直接进入 live；`hk_low_size_quality_liquidity_premium` 只能在 Hang Seng Low Size-style 质量筛选、free-float market-cap 历史、HSICS 行业、ADV/spread/board-lot/suspension/capacity 证据充分后再研究；`hk_stock_connect_inclusion_event_flow` 只能在 Stock Connect eligible-security change list、announcement/effective date、sell-only status、南向成交/CCASS 持仓确认和 raw-vs-vendor reconciliation 完成后再研究；`hk_short_selling_pressure_risk_overlay` 只能作为 crowded-long / short-squeeze / negative-information 风险 overlay 候选，不能变成做空执行策略；`hk_director_dealing_disclosure_quality_overlay` 只能使用已披露的 SFC/HKEX Disclosure of Interests / director-dealing notices 作为 alignment / undervaluation overlay，并需要 filing lag、correction/cancellation、blackout/moratorium、connected-person transfer、routine option exercise 和 buyback overlap 控制；`hk_dually_traded_liquid_reversal_overlay` 只能作为高流动性双重上市 / cross-listed 标的的短周期反转 overlay，必须先证明 dual-listing mapping、外盘/港股收盘和 FX 对齐、weekly reversal 信号、spread/fee/slippage/VCM/CAS、停牌和容量控制；`hk_earnings_announcement_drift_overlay` 只能作为公开 HKEXnews 业绩公告、profit warning / alert 和 PEAD 事件 overlay，必须先证明公告发布时间、复牌时间、盈利 surprise、双语标题/正文分类、短卖资格、流动性、滑点和事件窗口成本控制；`hk_lottery_stock_risk_exclusion_overlay` 只能作为 lottery-like / MAX / IVOL / ISKEW 风险排除或降权 overlay，不能直接变成做空策略，必须先证明点时间 lottery 特征、低价/高波动/高偏度、市场波动或下跌 regime、流动性、短卖资格、停牌、成本和同 universe ablation；`hk_equity_financing_dilution_risk_overlay` 只能作为 rights issue / open offer / placement / convertible issuance 等融资公告后的摊薄和 adverse-selection 风险 overlay，不能简单做空所有融资公告，必须区分 rights offers、growth placements、issue discount、dilution、use of proceeds、underwriter、股东承诺、minority approval、2018 规则变化、completion/cancellation 和交易停复牌影响；`hk_connected_transaction_governance_risk_overlay` 只能作为 connected transaction / related-party transaction 的治理、tunneling 或 expropriation 风险排除或降权 overlay，不能假设所有关联交易都为负面，必须区分 connected person、ultimate controller、交易类型、定价政策、资产估值、独立财务顾问意见、独立股东批准、豁免状态、INED/审计师年审、propping/strategic transaction 与少数股东价值损失；`hk_takeover_privatization_event_spread_overlay` 只能作为 takeover / merger / privatisation / possible-offer 的事件价差 overlay，不能作为 live merger-arbitrage 策略，必须先证明 Rule 3.7 possible offer、Rule 3.5 firm intention、offer period、offer price/spread、conditions、acceptance level、scheme / compulsory acquisition、withdrawal/lapse、break price、交易停复牌和 disclosure-dealing controls；`hk_distribution_ex_date_entitlement_overlay` 只能作为 cash/special/scrip dividend、stock distribution、bonus issue、split/consolidation 的 ex-entitlement 事件 overlay，不能作为 live dividend-capture 策略，必须先证明 ex-date、record date、book closure、payment date、currency、adjustment factor、exchange adjusted previous close、settlement holiday、typhoon/extreme-condition change、ADR/dual-listing date mismatch、成本和容量控制；`hk_ipo_lockup_overhang_event_overlay` 只能作为新上市公司 IPO 后、cornerstone / pre-IPO investor lock-up 到期和供给 overhang 的风险 overlay，不能作为 IPO 认购、首日翻炒或做空 lock-up 策略，必须先证明 listing date、prospectus、offer price、allotment result、cornerstone identity/allocation、lock-up expiry、public float、double-dipping、clawback、stabilization、block trade、short-sale eligibility、流动性和容量控制；`hk_audit_opinion_suspension_risk_overlay` 只能作为 disclaimer / adverse / qualified / going-concern 审计意见、停牌、复牌和退市风险 overlay，不能作为复牌博弈策略，必须先证明审计意见分类、Rule 13.50A、audit issue remedial period、long suspension / delisting、auditor resignation、forensic investigation、resumption guidance、流动性和容量控制；`hk_share_repurchase_execution_signal_overlay` 只能作为 HKEX 日度实际回购执行强度、首次/重复回购和低估值信号 overlay，不能重复现有 shareholder-yield scaffold，也不能直接变成追逐回购公告的 live 策略，必须先证明 daily report、mandate/program/waiver、treasury-share retention/cancellation/resale、moratorium/blackout/connected-person、post-buyback financing/dilution、流动性和 same-universe ablation 控制；`hk_liquid_pairs_cointegration_stat_arb_overlay` 只能作为高流动性 pairs / basket relative-value research overlay，不能在没有 borrow/short-sale/margin/order-preview 证据时成为 live stat-arb 策略；必须先证明 pair universe、cointegration/spread half-life/breakdown、borrow fee、designated short-selling、tick rule、VCM/CAS、停牌/单腿缺口、同 universe ablation 和成本压力；`hk_macro_liquidity_inflation_rate_sensitivity_overlay` 只能作为 CPI / inflation、HKMA base rate、HIBOR、aggregate balance 和 HKD liquidity-regime 的宏观风险 / tilt overlay，不能作为单独宏观择时策略，必须先证明 release lag / revision、currency peg、sector / property / financial / dividend-yield rate sensitivity、同 universe ablation 和容量压力。其内嵌的 `future_research_live_enablement_policy` 仍用于阻止尚未 scaffold 的新联网研究候选绕过新 profile contract、候选专属 source-audit 字段、point-in-time consensus estimate/revision history、free-float market-cap/size factor history、Stock Connect eligibility change history、designated short-selling security history、short-selling turnover/short-ratio history、Disclosure of Interests / director-dealing notice history、blackout/moratorium context、dually traded mapping / reversal cost history、HKEXnews announcement / profit-warning / earnings-surprise timestamp history、lottery-feature IVOL/ISKEW/MAX/price history、equity-financing rights/open-offer/placement/convertible dilution history、connected-transaction announcement/circular/shareholder-approval and governance-risk history、takeover possible-offer/firm-intention/offer-period/spread/completion-risk history、distribution ex-date/record-date/payment/price-adjustment/settlement history、IPO listing/cornerstone/pre-IPO lock-up expiry/overhang/stabilization history、audit-opinion disclaimer/adverse/qualified/going-concern/suspension/resumption/delisting history、share-repurchase daily execution / mandate / treasury-share retention-resale / post-buyback dilution history、pairs cointegration / spread stability / borrow-shortability / pair-leg cost history、liquidity/capacity controls、同 universe ablation、walk-forward 证据、artifact provenance、dry-run order-preview、双语通知、rollout controls 和 operator approval。

切换任何 snapshot profile 前先输出 readiness 计划：

```bash
PYTHONPATH=src python scripts/print_snapshot_readiness.py \
  --profile hk_liquid_momentum_quality \
  --platform longbridge \
  --json
```

该输出会明确 `runtime_enabled=false`、通用阻断原因和 profile-specific live-enable 要求；它不是 Cloud Run 部署命令。
readiness JSON 也会输出 `evidence_uri_policy`、`execution_capacity_policy`、`dry_run_order_preview_policy`、`baseline_rotation_live_enablement_policy`、`quality_yield_live_enablement_policy`、`quality_growth_live_enablement_policy`、`factor_mix_live_enablement_policy`、`momentum_live_enablement_policy`、`policy_value_live_enablement_policy`、`special_situation_live_enablement_policy`、`rollout_risk_policy` 和 `notification_audit_policy`，平台可以在 artifact 接入前先拒绝不稳定或带 secret-like query 参数的证据链接，并要求 baseline rotation 提供 HSI constituent / execution provenance、首批 quality/yield 候选提供同 universe ablation、forecast dividend yield vs trailing yield ablation、stale estimate-revision 控制、yield-trap、HSHYLV/HSSCHYS-style Southbound / three-year cash-dividend / payout-ratio / price-crash screen / high-volatility exclusion / financial-soundness screen、S&P Access HK Low Volatility High Dividend methodology / constituent / rebalance / capping reconciliation、share-count/treasury-share、FCF reporting-date、sector/rate-cycle stress 证据；同时 dry-run 订单预览必须证明 ADV 容量、board-lot rounding、odd-lot avoidance、交易时段路由、VCM/price-band 控制、raw order preview / quote snapshot / fee breakdown URI 与 sha256 provenance、EN/ZH-Hans 双语通知、correlation id、脱敏和稳定 delivery-log URI，以及分阶段上线、kill switch、SWT/VCM runbook 和扩容前观察期。

也可以输出全部 snapshot profile 的统一 live-enable matrix，供平台切换前做机器可读门禁：

```bash
PYTHONPATH=src python scripts/print_snapshot_readiness.py \
  --all \
  --platform longbridge \
  --json
```

当前 matrix 的 `live_enable_gate=blocked_until_production_evidence`，表示这些 scaffold 仍需 production snapshot source、manifest 发布、walk-forward backtest、平台 dry-run 订单预览、券商权限/费用校验和足够的 rebalance/event window 证据（普通 profile 至少 3 个，event profile 至少 1 个）。

matrix 同时输出 `evidence_uri_policy`、`artifact_provenance_policy`、`evidence_freshness_policy`、`execution_capacity_policy`、`dry_run_order_preview_policy`、`baseline_rotation_live_enablement_policy`、`quality_yield_live_enablement_policy`、`quality_growth_live_enablement_policy`、`factor_mix_live_enablement_policy`、`momentum_live_enablement_policy`、`policy_value_live_enablement_policy`、`special_situation_live_enablement_policy` 和 `rollout_risk_policy`，供平台切换工具自动要求 `https://`、`gs://` 或 `s3://` 证据 URI，并拒绝带 token/password/signature 等 secret-like query 参数、缺少不可变 artifact release 溯源、超过时效门槛、没有通过 ADV/board-lot/odd-lot/VCM 容量校验、缺少 order preview artifact provenance、缺少 baseline rotation HSI constituent / execution provenance、首批 quality/yield ablation / forecast-dividend-yield controls / yield-trap / Southbound / three-year cash-dividend / payout-ratio / price-crash screen / high-volatility exclusion / financial-soundness screen / S&P Access HK Low Volatility High Dividend reconciliation / share-count / FCF reporting-date / sector stress 证据、缺少动量因子 HSI/MSCI descriptor reconciliation、one-month-skip/risk-adjusted momentum、ablation / stress-window 证据、缺少南向资金 / AH 溢价 / 指数调仓的 signal-decay、日历/收盘对齐、官方 schedule / review-result press-release、fast-entry / suspension / buffer-rule exception、CAS / market-on-close、crowding/slippage stress 证据，或缺少分阶段上线/回滚/tripwire 计划的证据。

live-enable 模板和校验结果也会输出同一份 `evidence_uri_policy`、`artifact_provenance_policy`、`evidence_freshness_policy`、`execution_capacity_policy`、`dry_run_order_preview_policy`、`baseline_rotation_live_enablement_policy`、`quality_yield_live_enablement_policy`、`quality_growth_live_enablement_policy`、`factor_mix_live_enablement_policy`、`momentum_live_enablement_policy`、`policy_value_live_enablement_policy`、`special_situation_live_enablement_policy`、`rollout_risk_policy`、`notification_audit_policy` 和 `production_source_audit_policy`。通过 live-enable 校验的 evidence pack 不能只填布尔值：对 `hk_blue_chip_leader_rotation`，还必须提供 `strategy_policy_evidence` 条件段，且 `policy_version` 必须匹配 `hk_snapshot_baseline_rotation_live_enablement_policy.v1`，并证明 HSI 成分股/复核、基准相对动量、52 周高点、sector/liquidity、board-lot/VCM/CAS/交易时段、rebalancing buffer 和 dry-run provenance；对 `hk_low_vol_dividend_quality`、`hk_shareholder_yield_quality` 和 `hk_free_cash_flow_quality`，还必须提供 `strategy_policy_evidence` 条件段，且 `policy_version` 必须匹配 `hk_snapshot_quality_yield_live_enablement_policy.v1`、`status=passed`、`evidence_uri` 必须稳定、`evidence_generated_at` 必须新鲜，所有 quality/yield ablation、stress-test 和 data-provenance flags 必须为 true；对 `hk_residual_momentum_quality`、`hk_liquid_momentum_quality` 和 `hk_composite_factor_quality_value_momentum`，`strategy_policy_evidence.policy_version` 必须匹配 `hk_snapshot_momentum_live_enablement_policy.v1`，并证明 residual/liquid/composite 同 universe ablation、HSI/MSCI descriptor reconciliation、one-month-skip/risk-adjusted momentum、momentum crash stress 和 data-provenance flags 全部通过；对 `hk_quality_growth_low_volatility`、`hk_factor_mix_qvlm_risk_parity`、`hk_central_soe_value_quality_select`、`hk_southbound_flow_momentum`、`hk_ah_premium_relative_value` 和 `hk_index_rebalance_event`，同一 section 也必须匹配各自的 quality-growth / factor-mix / policy-value / special-situation policy version，并通过对应 ablation、stress-test 和 data-provenance flags；production source audit 也必须覆盖通用 point-in-time / adjusted price / corporate action / suspension / stale price / missing field / symbol mapping / survivorship-safe universe 字段，也必须提供 `source_coverage_start` / `source_coverage_end`、稳定 `production_source_uri`、`source_quality_report_uri` 和 `point_in_time_data_dictionary_uri`，并覆盖 profile-specific 字段（例如 shareholder yield 的 HKEX buyback disclosure、next-day repurchase returns、treasury-share retention/cancellation/resale、moratorium/blackout controls 和 post-buyback financing review、southbound flow 的 Stock Connect daily turnover / holding history / trading-calendar alignment、A/H premium 的 A/H close alignment / close-time policy / FX source provenance / eligibility history、quality growth 的 revenue / earnings / ROE growth、accruals、cash-flow-to-debt、Growth in ROA adjusted by P/B、HSI QGLV winsorized z-score / component averaging / Financials / negative-equity / missing-factor policy、HSI low-vol quality screen、volatility / sector / Southbound eligibility history）；`production_source_audit_policy.source_reference_urls` 会列出每个 profile 建议核对的一手来源，例如 HKEXnews、HKEX Stock Connect statistics、Hang Seng Indexes 或 S&P index pages。artifact pack validation 必须满足 `artifact_provenance_policy`，包括不可变 `artifact_release_id`、contract version、snapshot sha256、row count、published snapshot/manifest/ranking/release-summary URI、非样例 artifact、manifest sha256/row-count 对账和 release summary ready 证明。artifact pack validation、walk-forward backtest、平台 dry-run order preview、券商权限/费用校验、rebalance/event window 和 runtime rollout plan 都必须提供非空、稳定的 `evidence_uri`（允许 `https://`、`gs://`、`s3://`），且 URI 不能包含 token/password/signature 等 secret-like query 参数；上述非审批证据段还必须提供 ISO 日期格式的 `evidence_generated_at`，并满足模板中 `evidence_freshness_policy.max_allowed_age_days_by_section` 的时效门槛，避免用过期 source audit、回测或 dry-run 证据解锁实盘。平台 dry-run order preview 还必须满足 `execution_capacity_policy`、`dry_run_order_preview_policy` 和 `notification_audit_policy`：ADV 窗口天数、median daily turnover、单笔订单 ADV 占比和本次 rebalance ADV 占比都要在阈值内，并证明 liquidity cap、board-lot rounding、odd-lot avoidance、交易时段路由和 VCM/price-band controls 已验证；还必须提供 `dry_run_session_id`、稳定的 `raw_order_preview_uri` / `quote_snapshot_uri` / `fee_breakdown_uri`、对应 64 位 hex sha256、非 sample artifact、敏感字段脱敏、quote 覆盖全 symbols、fee breakdown 与券商预览对账、order preview 与策略决策对账；通知证据必须使用 `hk_live_enablement_notification.v1` / `hk_snapshot_live_enablement_dry_run`，覆盖 EN/ZH-Hans 文案、profile/platform/status/order-preview 摘要、correlation id、敏感字段脱敏和稳定 `notification_delivery_log_uri`；`runtime_rollout_plan` 必须满足 `rollout_risk_policy`，包括分阶段上线、初始资金/单标的上限、盘中和累计回撤 tripwire、kill switch、operator notification、SWT/VCM runbook、回滚计划和扩容前观察期；`risk_approval.approval_reference` 也必须非空。

发布 artifact 后、平台读取前，必须先校验 artifact pack：

```bash
hkeq-validate-snapshot-artifact-pack \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir <published-artifact-dir> \
  --json
```

该校验会检查 snapshot / manifest / ranking / release summary 是否齐全、manifest 里的 profile / contract version / sha256 / row count 是否和实际文件一致。

最后，在移除 dry-run 或把 profile 标为 runtime-enabled 前，还必须校验 live-enable evidence pack：

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality \
  --platform longbridge \
  --json > live-enable-evidence.json
```

```bash
hkeq-validate-live-enable-evidence \
  --evidence-file <live-enable-evidence.json> \
  --json
```

该证据包必须覆盖 production 数据源审计、artifact pack validator 结果和发布溯源、walk-forward / out-of-sample 回测、平台 dry-run order preview、券商权限/费用确认、足够的 rebalance/event window（普通 profile 至少 3 个，event profile 至少 1 个）、runtime rollout plan，以及人工审批。数据源审计字段由 profile 决定，并在模板的 `production_source_audit_policy.required_boolean_fields` 中列出；生产数据源本体还必须提供覆盖区间、稳定 `production_source_uri`、`source_quality_report_uri` 和 point-in-time data dictionary URI；建议核对来源在 `production_source_audit_policy.source_reference_urls` 中列出；没有逐项证明前不能通过 live-enable。artifact 发布溯源字段在 `artifact_provenance_policy.required_fields` / `required_uri_fields` 中列出，必须证明发布 URI、sha256、row count、contract version 和 immutable release id。每个非审批证据段还必须填写 `evidence_generated_at`，并在 `validation_as_of` 日期下满足 `evidence_freshness_policy` 的 section-specific 时效门槛。平台 dry-run order preview 必须同时通过 `execution_capacity_policy`、`dry_run_order_preview_policy` 和 `notification_audit_policy`，包括 ADV 窗口、最低 median daily turnover、单笔订单和整体 rebalance ADV 占比、board-lot rounding、odd-lot avoidance、交易时段路由和 VCM/price-band controls、`dry_run_session_id`、稳定 raw order preview / quote snapshot / fee breakdown URI、对应 sha256、脱敏、quote 覆盖全 symbols、fee breakdown 与券商预览对账、order preview 与策略决策对账，以及 `hk_snapshot_live_enablement_dry_run` 双语通知 delivery-log。runtime rollout plan 必须通过 `rollout_risk_policy`，包括初始资金上限、单标的上限、回撤 tripwire、kill switch、SWT/VCM runbook 和扩容前观察期。默认最大回撤门槛为 30%；年化收益/最大回撤比还必须至少达到 0.50，避免高回撤低收益策略通过；回测还必须覆盖至少 3 年 walk-forward / out-of-sample 区间、正年化收益、低于 profile 年化换手上限、相对 profile 基准为正超额收益，并显式纳入港股费用/征费、印花税或豁免、滑点、lot-size rounding、停牌处理、survivorship-bias、look-ahead-bias、每个 OOS fold 回撤、参数敏感性/holdout 稳定性、净收益扣费、压力窗口、杠杆/做空/融资可行性、corporate-action/delisting/stale-price 控制；普通 snapshot profile 至少需要 3 个 paper/dry-run rebalance window，event profile 至少需要 1 个 event window。

### 平台集成

如果未来 profile 被提升，先把 snapshot 和 manifest 发布到平台 runtime artifact 位置，然后设置：

- `IBKR_FEATURE_SNAPSHOT_PATH` and `IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH` for `InteractiveBrokersPlatform`.
- `LONGBRIDGE_FEATURE_SNAPSHOT_PATH` and `LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH` for `LongBridgePlatform`.

平台服务也必须运行在港股市场模式：

- IBKR: `IBKR_MARKET=HK`, `IBKR_MARKET_EXCHANGE=SEHK`, `IBKR_MARKET_CURRENCY=HKD`.
- LongBridge: `ACCOUNT_REGION=HK` or `LONGBRIDGE_MARKET=HK`.

## English

Feature-snapshot pipeline scaffold repository for QuantStrategyLab HK snapshot-backed profiles.

## Scope

This repository owns HK snapshot-backed artifact contracts, sample builders, and future publication boundaries. It is intentionally separate from the non-snapshot HK strategy repository. It does not submit orders, store broker credentials, or switch Cloud Run services. The current data builder is a scaffold/reference implementation, not a production HK data feed.

The current snapshot scaffolds cover:

#### `hk_ah_premium_relative_value`

- `hk_ah_premium_relative_value_valuation_snapshot_latest.csv`
- `hk_ah_premium_relative_value_valuation_snapshot_latest.csv.manifest.json`
- `hk_ah_premium_relative_value_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_blue_chip_leader_rotation`

- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv`
- `hk_blue_chip_leader_rotation_feature_snapshot_latest.csv.manifest.json`
- `hk_blue_chip_leader_rotation_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_composite_factor_quality_value_momentum`

- `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv`
- `hk_composite_factor_quality_value_momentum_factor_snapshot_latest.csv.manifest.json`
- `hk_composite_factor_quality_value_momentum_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_factor_mix_qvlm_risk_parity`

- `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv`
- `hk_factor_mix_qvlm_risk_parity_factor_snapshot_latest.csv.manifest.json`
- `hk_factor_mix_qvlm_risk_parity_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_central_soe_value_quality_select`

- `hk_central_soe_value_quality_select_factor_snapshot_latest.csv`
- `hk_central_soe_value_quality_select_factor_snapshot_latest.csv.manifest.json`
- `hk_central_soe_value_quality_select_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_free_cash_flow_quality`

- `hk_free_cash_flow_quality_factor_snapshot_latest.csv`
- `hk_free_cash_flow_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_free_cash_flow_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_index_rebalance_event`

- `hk_index_rebalance_event_event_calendar_snapshot_latest.csv`
- `hk_index_rebalance_event_event_calendar_snapshot_latest.csv.manifest.json`
- `hk_index_rebalance_event_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_low_vol_dividend_quality`

- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv`
- `hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_low_vol_dividend_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_quality_growth_low_volatility`

- `hk_quality_growth_low_volatility_factor_snapshot_latest.csv`
- `hk_quality_growth_low_volatility_factor_snapshot_latest.csv.manifest.json`
- `hk_quality_growth_low_volatility_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_liquid_momentum_quality`

- `hk_liquid_momentum_quality_feature_snapshot_latest.csv`
- `hk_liquid_momentum_quality_feature_snapshot_latest.csv.manifest.json`
- `hk_liquid_momentum_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_residual_momentum_quality`

- `hk_residual_momentum_quality_factor_snapshot_latest.csv`
- `hk_residual_momentum_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_residual_momentum_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_shareholder_yield_quality`

- `hk_shareholder_yield_quality_factor_snapshot_latest.csv`
- `hk_shareholder_yield_quality_factor_snapshot_latest.csv.manifest.json`
- `hk_shareholder_yield_quality_ranking_latest.csv`
- `release_status_summary.json`

#### `hk_southbound_flow_momentum`

- `hk_southbound_flow_momentum_flow_snapshot_latest.csv`
- `hk_southbound_flow_momentum_flow_snapshot_latest.csv.manifest.json`
- `hk_southbound_flow_momentum_ranking_latest.csv`
- `release_status_summary.json`

Non-snapshot HK strategies such as `hk_listed_global_etf_rotation` stay in `HkEquityStrategies` and consume direct `market_history`; they do not publish snapshots through this repository.

Future snapshot candidate research is documented in `docs/research/hk_snapshot_strategy_candidates.md`. `hk_low_vol_dividend_quality`, `hk_liquid_momentum_quality`, `hk_composite_factor_quality_value_momentum`, `hk_factor_mix_qvlm_risk_parity`, `hk_central_soe_value_quality_select`, `hk_quality_growth_low_volatility`, `hk_residual_momentum_quality`, `hk_shareholder_yield_quality`, `hk_free_cash_flow_quality`, `hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, and `hk_index_rebalance_event` now have tested scaffolds, but they still have no production data source and are not live-enabled.

## Local build from sample data

```bash
PYTHONPATH=src python scripts/build_blue_chip_sample.py
```

Or call the package entrypoint after installing locally:

```bash
hkeq-build-blue-chip-leader-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output
```

`hk_liquid_momentum_quality` uses the same sample price/universe inputs and writes its own artifact filenames:

```bash
PYTHONPATH=src python scripts/build_liquid_momentum_sample.py
```

The generated feature snapshot includes both `high_63_gap` and `high_252_gap`, so the scaffold can test the short/long price-to-recent-high momentum shape used by HK momentum research while keeping `high_63_gap` optional for backward compatibility.

or:

```bash
hkeq-build-liquid-momentum-quality-snapshot \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv \
  --output-dir data/output/liquid_momentum_quality
```

`hk_residual_momentum_quality` is the closer analogue to a US-style cross-sectional stock momentum factor. It is not derived directly from the bundled price sample; the upstream factor engine must provide residual / industry-neutral momentum, industry-relative momentum, beta, volatility, and drawdown fields:

```bash
PYTHONPATH=src python scripts/build_residual_momentum_sample.py
```

Or:

```bash
hkeq-build-residual-momentum-quality-snapshot \
  --factor-snapshot examples/residual_momentum_quality/factor_snapshot.sample.csv \
  --output-dir data/output/residual_momentum_quality
```

`hk_shareholder_yield_quality` expects external dividend, buyback, share-count-change, FCF, ROE, leverage, and risk fields. It is a low-turnover shareholder-return / quality scaffold, not a production disclosure collector:

```bash
PYTHONPATH=src python scripts/build_shareholder_yield_sample.py
```

Or:

```bash
hkeq-build-shareholder-yield-quality-snapshot \
  --factor-snapshot examples/shareholder_yield_quality/factor_snapshot.sample.csv \
  --output-dir data/output/shareholder_yield_quality
```

`hk_low_vol_dividend_quality` expects a factor snapshot input because dividend, earnings, beta, and payout fields are not derivable from prices alone:

```bash
PYTHONPATH=src python scripts/build_low_vol_dividend_sample.py
```

or:

```bash
hkeq-build-low-vol-dividend-quality-snapshot \
  --factor-snapshot examples/low_vol_dividend_quality/factor_snapshot.sample.csv \
  --output-dir data/output/low_vol_dividend_quality
```

`hk_quality_growth_low_volatility` expects an external growth, quality, valuation, and low-volatility factor snapshot. It is a quality-growth low-volatility scaffold, not a production fundamentals data source:

```bash
PYTHONPATH=src python scripts/build_quality_growth_low_volatility_sample.py
```

or:

```bash
hkeq-build-quality-growth-low-volatility-snapshot \
  --factor-snapshot examples/quality_growth_low_volatility/factor_snapshot.sample.csv \
  --output-dir data/output/quality_growth_low_volatility
```

`hk_composite_factor_quality_value_momentum` expects a broader factor snapshot with quality, value, momentum, low-volatility, and Southbound eligibility fields. It is the HK single-name analogue to a multi-factor stock-selection framework, but remains scaffold-only until production factor data and walk-forward evidence exist:

```bash
PYTHONPATH=src python scripts/build_composite_factor_sample.py
```

or:

```bash
hkeq-build-composite-factor-qvm-snapshot \
  --factor-snapshot examples/composite_factor_quality_value_momentum/factor_snapshot.sample.csv \
  --output-dir data/output/composite_factor_quality_value_momentum
```

`hk_factor_mix_qvlm_risk_parity` expects an external factor snapshot with quality, value, momentum, low-volatility, and factor-volatility fields. It is a QVLM risk-parity multi-factor scaffold, not a production factor data source:

```bash
PYTHONPATH=src python scripts/build_factor_mix_qvlm_risk_parity_sample.py
```

or:

```bash
hkeq-build-factor-mix-qvlm-risk-parity-snapshot \
  --factor-snapshot examples/factor_mix_qvlm_risk_parity/factor_snapshot.sample.csv \
  --output-dir data/output/factor_mix_qvlm_risk_parity
```

`hk_central_soe_value_quality_select` expects external central-SOE / government largest-shareholder classification, ownership pct, value / quality / low-vol / momentum factors, dividend yield, and risk fields. It is a HK policy-value / central-SOE quality scaffold, not a production SOE-classification or fundamentals data source:

```bash
PYTHONPATH=src python scripts/build_central_soe_value_quality_sample.py
```

or:

```bash
hkeq-build-central-soe-value-quality-select-snapshot \
  --factor-snapshot examples/central_soe_value_quality_select/factor_snapshot.sample.csv \
  --output-dir data/output/central_soe_value_quality_select
```

`hk_free_cash_flow_quality` expects an external fundamentals snapshot with FCF, enterprise value, ROE, and reporting-date availability fields. Live-enable also requires auditable FCF formula lineage, market-cap/debt/cash/FX inputs for EV, restatement/as-of handling, sector normalization, and financial/real-estate/negative-FCF exception policies. It is an FCF-yield quality/value scaffold, not a production fundamentals data source:

```bash
PYTHONPATH=src python scripts/build_free_cash_flow_sample.py
```

or:

```bash
hkeq-build-free-cash-flow-quality-snapshot \
  --factor-snapshot examples/free_cash_flow_quality/factor_snapshot.sample.csv \
  --output-dir data/output/free_cash_flow_quality
```

`hk_southbound_flow_momentum` expects an external southbound flow snapshot because Stock Connect net-buy, top-10 turnover, CCASS Southbound shareholding percentage, eligible-stock changes, and holding-change fields cannot be derived from prices alone; live-enable also needs HKEX data-dissemination-change handling and raw-vs-vendor reconciliation:

```bash
PYTHONPATH=src python scripts/build_southbound_flow_sample.py
```

or:

```bash
hkeq-build-southbound-flow-momentum-snapshot \
  --flow-snapshot examples/southbound_flow_momentum/flow_snapshot.sample.csv \
  --output-dir data/output/southbound_flow_momentum
```

`hk_ah_premium_relative_value` expects an external A/H premium and H-share trend snapshot because A-share prices, H-share prices, FX, adjusted market cap, Stock Connect eligibility, and AH Smart-style switch thresholds cannot be derived from H-share prices alone; live-enable also needs extreme-premium false-reversal, A-share access, shorting, settlement, and FX-constraint review:

```bash
PYTHONPATH=src python scripts/build_ah_premium_sample.py
```

or:

```bash
hkeq-build-ah-premium-relative-value-snapshot \
  --valuation-snapshot examples/ah_premium_relative_value/valuation_snapshot.sample.csv \
  --output-dir data/output/ah_premium_relative_value
```

`hk_index_rebalance_event` expects an external index-review event calendar snapshot because methodology/operation-guide versions, schedule-file versions, next-review notices, review-result press-release timestamps, constituent weights / pro-forma records, announcement dates, effective dates, add/remove probabilities, and slippage estimates cannot be derived from prices alone. Its live-enable gate now also requires MOC-vs-next-open and pro-forma-weighted-vs-equal-weight ablations, plus HKEX CAS random-close / two-stage price-limit / order-rejection / passive-flow imbalance controls:

```bash
PYTHONPATH=src python scripts/build_index_rebalance_event_sample.py
```

or:

```bash
hkeq-build-index-rebalance-event-snapshot \
  --event-snapshot examples/index_rebalance_event/event_snapshot.sample.csv \
  --output-dir data/output/index_rebalance_event
```

## Research backtest sample

`hk_liquid_momentum_quality` still has no production data source. The current local CSV research harness verifies snapshot construction, rebalancing, trading-cost application, and metric calculation only:

```bash
PYTHONPATH=src python scripts/research_hk_liquid_momentum_quality_backtest.py \
  --prices examples/blue_chip/prices.sample.csv \
  --universe examples/blue_chip/universe.sample.csv
```

`research_status=sample_harness_only_not_production_backtest` means the output is not a production-grade historical backtest.

## Enablement status

`hk_blue_chip_leader_rotation`, `hk_low_vol_dividend_quality`, `hk_liquid_momentum_quality`, `hk_composite_factor_quality_value_momentum`, `hk_factor_mix_qvlm_risk_parity`, `hk_central_soe_value_quality_select`, `hk_residual_momentum_quality`, `hk_shareholder_yield_quality`, `hk_free_cash_flow_quality`, `hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, and `hk_index_rebalance_event` are currently architecture scaffolds. Do not wire these sample artifacts into scheduled Cloud Run trading until:

- the snapshot data source is validated;
- the strategy package explicitly promotes the profile to `runtime_enabled`;
- platform dry-run order previews, lot-size behavior, HKD cash handling, and operator approval are complete.

Use the promotion matrix first to inspect candidate priority, research evidence, data dependencies, and live-enable gaps:

```bash
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --json
PYTHONPATH=src python scripts/print_snapshot_promotion_matrix.py --profile hk_shareholder_yield_quality --json
```

The matrix also exposes `backtest_validation_policy` as the shared HK backtest gate: max drawdown must stay at or below 30% unless a stricter profile threshold applies; evidence must use point-in-time inputs, avoid look-ahead and survivorship bias, avoid full-sample return-based parameter selection, include walk-forward / OOS and multi-period robustness checks, require each OOS fold max drawdown <= 30%, annual-return-to-max-drawdown ratio >= 0.50, parameter-sensitivity / holdout stability, net-of-cost returns, bear/sideways/low-liquidity stress, and cover HK costs, slippage, lot size, suspensions, VCM/CAS, leverage/shorting/margin feasibility, and capacity constraints. The matrix also exposes `recommended_live_enablement_sequence`, plus each profile's `recommended_live_enablement_stage` and `next_live_enablement_action`. The current order still prioritizes the low-vol dividend, shareholder-yield, and FCF-quality low-turnover quality/yield candidates. The new `baseline_rotation_live_enablement_policy` gates `hk_blue_chip_leader_rotation`: evidence must prove HSI constituent/review methodology, point-in-time adjusted prices, benchmark-relative momentum, 52-week-high, sector/liquidity, board-lot, VCM/CAS, and trading-session provenance, plus relative-momentum versus HSI tracker / liquid momentum / 52-week-high / sector-neutral / rebalance-buffer ablations before dry-run can be removed. `quality_yield_live_enablement_policy` gates those first candidates, and the live-enable evidence validator now conditionally requires a `strategy_policy_evidence` section for these profiles with matching policy version, stable evidence URI, fresh `evidence_generated_at`, and every required ablation, stress-test, and data-provenance flag set to true. Low-vol dividend, shareholder yield, and FCF must be ablated on the same survivorship-safe universe, and evidence must cover forecast-dividend-yield estimate history, forecast-versus-trailing-yield ablation, stale estimate-revision controls, yield-trap controls, Southbound-eligible universe history, three-year cash-dividend records, payout-ratio bounds, price-crash / bottom-decile screens, large/mid-cap shortlisting, one-year high-volatility exclusion, financial-soundness screens, S&P Access HK Low Volatility High Dividend methodology / constituent / rebalance / capping reconciliation, payout coverage, buyback-spend versus share-count reduction, HKEX next-day repurchase returns, treasury-share retention/cancellation/resale, moratorium/blackout/connected-person controls, post-buyback financing / convertible / public-float review, treasury-share resale / dilution, FCF reporting-date and restatement handling, sector concentration, rate-cycle stress, HK costs, turnover caps, and dry-run order-preview provenance before dry-run can be removed. Momentum-factor candidates stay in the later research stage and must also prove HSI close-to-high descriptor, MSCI 6/12-month one-month-skip risk-adjusted momentum, volatility normalization, turnover buffer, sector/capacity, and momentum-crash controls. `momentum_live_enablement_comparison` now compares residual, liquid, and composite variants explicitly, and the same `momentum_live_enablement_policy` is emitted by per-profile readiness, live-enable evidence templates, and validator results. The live-enable evidence validator now also conditionally requires a `strategy_policy_evidence` section for these momentum profiles with matching policy version, stable evidence URI, fresh `evidence_generated_at`, and every required momentum ablation, stress-test, and data-provenance flag set to true, so platform tooling cannot treat momentum profiles as generic snapshot scaffolds: `hk_residual_momentum_quality` is the closest US-style cross-sectional momentum analogue, `hk_liquid_momentum_quality` is the simpler price-momentum fallback when residual inputs are not production-ready, and `hk_composite_factor_quality_value_momentum` needs factor ablation before it can be treated as momentum live evidence. The matrix also exposes `momentum_live_enablement_policy`, which requires residual/liquid/composite same-universe ablation, momentum-sleeve versus quality/value/low-volatility comparisons, 52-week-high versus 12-1 momentum checks, industry-neutral and quality-screen ablations, reversal/high-beta/suspension/Southbound stress windows, data provenance, and dry-run order-preview provenance before any momentum profile can remove dry-run. `special_situation_live_enablement_policy` gates the Southbound-flow, AH-premium, and index-rebalance HK-specialized candidates: evidence must prove HKEX / Hang Seng official-source provenance, Stock Connect calendar, historical daily turnover, top-10 turnover, CCASS Southbound shareholding, eligibility, data-dissemination, raw-vs-vendor reconciliation, and holdings/turnover coverage, AH close-time / FX alignment, HSI index methodology / operation guide versioning, rebalancing schedule-file version / effective-date history, next-review notice scope, review-result press-release timestamps, constituent weight / pro-forma provenance, index review announcement-to-effective windows, add/delete labels, fast-entry / suspension / buffer-rule exception handling, MOC-vs-next-open and pro-forma-weighted-vs-equal-weight ablations, HKEX CAS / market-on-close order constraints, random-close, two-stage price-limit, order-rejection and passive-flow imbalance controls, signal-decay tests, crowding / slippage stress, and dry-run order-preview provenance before dry-run can be removed. `quality_growth_live_enablement_policy` gates the `hk_quality_growth_low_volatility` scaffold: evidence must prove quality/growth/low-volatility factor ablation, HSI QGLV score lineage, MSCI quality ROE / stable-earnings / low-leverage reconciliation, minimum-volatility optimizer constraints, cash-conversion / accrual quality-trap controls, Southbound-universe and sector-neutral tests, real-estate/financial concentration, growth-deceleration, valuation/regulation/low-vol crowding stress, production fundamentals reporting-date provenance, and dry-run order-preview provenance. `factor_mix_live_enablement_policy` gates the new `hk_factor_mix_qvlm_risk_parity` scaffold: evidence must prove Q/V/L/M factor history, HSI QVLM parent universe, component-index returns, risk-parity weight / 12% cap lineage, factor-volatility and covariance/correlation history, HSI equal-weight factor-mix benchmark, MSCI Factor Mix A-Series equal-weight Q/V/L component and capped-methodology controls, same-universe equal-weight / composite QVM / leave-one-out / component-overlap ablations, factor-crowding / factor-correlation-breakdown / momentum-crash / value-trap / low-volatility-reversal / cap-induced turnover stress, HK cost/capacity controls, and dry-run order-preview provenance. `policy_value_live_enablement_policy` gates the new `hk_central_soe_value_quality_select` scaffold: evidence must prove point-in-time central-SOE largest-shareholder / ownership classification, SASAC/MOF source-list effective dates and effective-date drift, largest-shareholder look-through chain, HKEX Southbound eligible-security history, HSI Central SOEs value/quality factor-index constituent / Z-score / missing-measure averaging / 40% screening / buffer rules / 5% and 10% capping lineage, same-universe central-SOE value-quality versus broad value-quality, HSI value-quality factor indexes, and existing quality-yield ablations, sector concentration, policy-event / SOE reform / parent restructuring / eligibility removal / connected-transaction / sanctions / dividend-cut / cap-turnover stress, HK cost/capacity controls, and dry-run order-preview provenance. `future_research_backlog` now contains seventeen research-only candidates: `hk_earnings_revision_quality_overlay` may be tested only as an overlay on quality/value/low-vol/dividend/FCF sleeves, not as a direct live profile; `hk_low_size_quality_liquidity_premium` may be researched only after Hang Seng Low Size-style quality screens, point-in-time free-float market-cap history, HSICS industry history, and ADV/spread/board-lot/suspension/capacity controls exist; `hk_stock_connect_inclusion_event_flow` may be researched only after Stock Connect eligible-security change lists, announcement/effective dates, sell-only status, Southbound turnover / CCASS holding confirmation, and raw-vs-vendor reconciliation exist; `hk_short_selling_pressure_risk_overlay` may be tested only as a crowded-long / short-squeeze / negative-information risk overlay, not as a short-selling execution strategy; `hk_director_dealing_disclosure_quality_overlay` may use only disclosed SFC/HKEX Disclosure of Interests / director-dealing notices as an alignment / undervaluation overlay and must control filing lag, correction/cancellation notices, blackout/moratorium windows, connected-person transfers, routine option exercises, and buyback overlap; `hk_dually_traded_liquid_reversal_overlay` may be tested only as a liquid dually traded / cross-listed short-horizon reversal overlay after dual-listing mapping, foreign/HK close and FX alignment, weekly reversal signal, spread/fee/slippage/VCM/CAS, suspension, and capacity controls are proven; `hk_earnings_announcement_drift_overlay` may be tested only as a public HKEXnews results-announcement, profit-warning / alert, and PEAD event overlay after announcement publication timestamps, trading-resumption timestamps, earnings-surprise labels, bilingual headline/body classification, short-sale eligibility, liquidity, slippage, and event-window cost controls are proven; `hk_lottery_stock_risk_exclusion_overlay` may be tested only as a lottery-like / MAX / IVOL / ISKEW risk exclusion or underweight overlay, not as a direct short-selling strategy, after point-in-time lottery features, low-price / high-volatility / high-skewness history, market-volatility or drawdown regimes, liquidity, short-sale eligibility, suspensions, costs, and same-universe ablations are proven; `hk_equity_financing_dilution_risk_overlay` may be tested only as a dilution and adverse-selection overlay after rights issue, open offer, placement, convertible-issuance, issue-discount, use-of-proceeds, underwriting, shareholder-commitment, minority-approval, 2018 rule-change, completion/cancellation, and trading-halt/resumption controls are proven; `hk_connected_transaction_governance_risk_overlay` may be tested only as a connected-transaction governance, tunneling, or expropriation risk overlay after connected-person, ultimate-controller, transaction-type, pricing-policy, asset-valuation, independent-financial-adviser, independent-shareholder-approval, exemption, INED/auditor annual-review, propping/strategic-transaction, and minority-shareholder-value-loss controls are proven; `hk_takeover_privatization_event_spread_overlay` may be tested only as a takeover / merger / privatisation / possible-offer event-spread overlay after Rule 3.7 possible-offer, Rule 3.5 firm-intention, offer-period, offer-price/spread, conditions, acceptance-level, scheme / compulsory-acquisition, withdrawal/lapse, break-price, trading-halt, and disclosure-dealing controls are proven; `hk_distribution_ex_date_entitlement_overlay` may be tested only as an ex-entitlement event overlay after cash/special/scrip dividend, stock-distribution, bonus-issue, split/consolidation, ex-date, record-date, book-closure, payment-date, currency, adjustment-factor, exchange-adjusted previous-close, settlement-holiday, typhoon/extreme-condition change, ADR/dual-listing mismatch, cost, and capacity controls are proven; `hk_ipo_lockup_overhang_event_overlay` may be tested only as a post-IPO supply-overhang risk overlay after listing-date, prospectus, offer-price, allotment-result, cornerstone identity/allocation, lock-up expiry, public-float, double-dipping, clawback, stabilization, block-trade, short-sale eligibility, liquidity, and capacity controls are proven; `hk_audit_opinion_suspension_risk_overlay` may be tested only as a disclaimer / adverse / qualified / going-concern audit-opinion, suspension, resumption, and delisting-risk overlay after audit-opinion classification, Rule 13.50A, remedial-period, long-suspension / delisting, auditor-resignation, forensic-investigation, resumption-guidance, liquidity, and capacity controls are proven; `hk_share_repurchase_execution_signal_overlay` may be tested only as an executed-buyback signal after daily HKEX report, mandate/program, treasury-share retention/resale, blackout/moratorium, post-buyback dilution, liquidity, capacity, and shareholder-yield ablation evidence are audited; `hk_liquid_pairs_cointegration_stat_arb_overlay` may be tested only as a liquid pairs / basket relative-value research overlay, not as live stat-arb, until pair universe, cointegration/spread half-life/breakdown, borrow fee, designated short-selling, tick-rule, VCM/CAS, suspension or one-leg gap, same-universe ablation, and cost-stress evidence are audited; `hk_macro_liquidity_inflation_rate_sensitivity_overlay` may be tested only as a CPI / inflation, HKMA base-rate, HIBOR, aggregate-balance, and HKD liquidity-regime risk / tilt overlay, not as standalone macro timing, until release-lag / revision, currency-peg, sector / property / financial / dividend-yield rate-sensitivity, same-universe ablation, and capacity-stress evidence are audited. Its nested `future_research_live_enablement_policy` still prevents any new non-scaffolded external research idea from bypassing a new profile contract, candidate-specific source-audit fields, point-in-time consensus estimate/revision history, free-float market-cap/size factor history, Stock Connect eligibility change history, designated short-selling security history, short-selling turnover / short-ratio history, Disclosure of Interests / director-dealing notice history, blackout/moratorium context, dually traded mapping / reversal cost history, HKEXnews announcement / profit-warning / earnings-surprise timestamp history, lottery-feature IVOL/ISKEW/MAX/price history, equity-financing rights/open-offer/placement/convertible dilution history, connected-transaction announcement/circular/shareholder-approval and governance-risk history, takeover possible-offer/firm-intention/offer-period/spread/completion-risk history, distribution ex-date/record-date/payment/price-adjustment/settlement history, IPO listing/cornerstone/pre-IPO lock-up expiry/overhang/stabilization history, audit-opinion disclaimer/adverse/qualified/going-concern/suspension/resumption/delisting history, share-repurchase daily execution / mandate / treasury-share retention-resale / post-buyback dilution history, pairs cointegration / spread stability / borrow-shortability / pair-leg cost history, liquidity/capacity controls, same-universe ablation, walk-forward evidence, artifact provenance, dry-run order-preview evidence, bilingual notifications, rollout controls, and operator approval.

Print the readiness plan before switching any snapshot profile:

```bash
PYTHONPATH=src python scripts/print_snapshot_readiness.py \
  --profile hk_liquid_momentum_quality \
  --platform longbridge \
  --json
```

The output explicitly reports `runtime_enabled=false`, blocking reasons, and profile-specific live-enable requirements; it is not a Cloud Run deployment command.
The readiness JSON also exposes `evidence_uri_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `baseline_rotation_live_enablement_policy`, `quality_yield_live_enablement_policy`, `quality_growth_live_enablement_policy`, `factor_mix_live_enablement_policy`, `momentum_live_enablement_policy`, `policy_value_live_enablement_policy`, `special_situation_live_enablement_policy`, `rollout_risk_policy`, and `notification_audit_policy`, allowing platform tooling to reject unstable evidence links or links with secret-like query parameters before artifact wiring, require baseline-rotation HSI constituent / execution provenance, first-candidate quality/yield ablation, forecast-dividend-yield versus trailing-yield ablation, stale estimate-revision controls, and yield-trap/Southbound/three-year cash-dividend/payout-ratio/price-crash screen/high-volatility exclusion/financial-soundness screen/S&P Access HK Low Volatility High Dividend reconciliation/share-count/FCF reporting-date/sector-stress evidence, and require dry-run order-preview proof for ADV capacity, board-lot rounding, odd-lot avoidance, session routing, VCM/price-band controls, raw order-preview / quote-snapshot / fee-breakdown URI and sha256 provenance, bilingual EN/ZH-Hans notifications with correlation ids and redaction, staged rollout, kill switch, SWT/VCM runbooks, and observation windows before scale-up.

You can also print a machine-readable live-enable matrix for every snapshot profile before platform switching:

```bash
PYTHONPATH=src python scripts/print_snapshot_readiness.py \
  --all \
  --platform longbridge \
  --json
```

The current matrix reports `live_enable_gate=blocked_until_production_evidence`, meaning these scaffolds still need a production snapshot source, manifest publication, walk-forward backtest, platform dry-run order preview, broker permission/fee verification, and the required rebalance/event-window evidence pack (at least three windows for normal profiles and at least one event window for event profiles).

The matrix also exposes `evidence_uri_policy`, `artifact_provenance_policy`, `evidence_freshness_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `baseline_rotation_live_enablement_policy`, `quality_yield_live_enablement_policy`, `quality_growth_live_enablement_policy`, `factor_mix_live_enablement_policy`, `momentum_live_enablement_policy`, `policy_value_live_enablement_policy`, `special_situation_live_enablement_policy`, `rollout_risk_policy`, and `notification_audit_policy`, so platform switch-plan tooling can require `https://`, `gs://`, or `s3://` evidence URIs and reject links that contain token/password/signature-like query parameters, missing immutable artifact release provenance, evidence that exceeds the section freshness windows, dry-run order previews that fail ADV / board-lot / odd-lot / VCM capacity checks, missing raw order-preview / quote-snapshot / fee-breakdown URI and sha256 provenance, missing baseline-rotation HSI constituent / execution provenance, missing quality/yield ablation, forecast-dividend-yield versus trailing-yield ablation, stale estimate-revision controls, and yield-trap/Southbound/three-year cash-dividend/payout-ratio/price-crash screen/high-volatility exclusion/financial-soundness screen/S&P Access HK Low Volatility High Dividend reconciliation/share-count/FCF reporting-date/sector-stress evidence, missing momentum HSI/MSCI descriptor reconciliation, one-month-skip / risk-adjusted momentum, ablation/stress-window evidence, missing Southbound-flow / AH-premium / index-event signal-decay, calendar/close-alignment, official schedule / review-result press-release, fast-entry / suspension / buffer-rule exception, CAS / market-on-close, and crowding/slippage stress evidence, or rollout plans that lack capital caps, tripwires, kill switch, SWT/VCM runbooks, and rollback controls before they are logged, stored, or displayed.

After publishing artifacts and before platform loading, validate the artifact pack:

```bash
hkeq-validate-snapshot-artifact-pack \
  --profile hk_low_vol_dividend_quality \
  --artifact-dir <published-artifact-dir> \
  --json
```

The validator checks that snapshot / manifest / ranking / release summary files exist and that manifest profile, contract version, sha256, and row count match the actual snapshot file.

Finally, before removing dry-run or marking a profile runtime-enabled, validate the live-enable evidence pack:

```bash
hkeq-validate-live-enable-evidence \
  --print-template \
  --profile hk_low_vol_dividend_quality \
  --platform longbridge \
  --json > live-enable-evidence.json
```

```bash
hkeq-validate-live-enable-evidence \
  --evidence-file <live-enable-evidence.json> \
  --json
```

The live-enable template and validation result also expose the same `evidence_uri_policy`, `artifact_provenance_policy`, `evidence_freshness_policy`, `execution_capacity_policy`, `dry_run_order_preview_policy`, `baseline_rotation_live_enablement_policy`, `quality_yield_live_enablement_policy`, `quality_growth_live_enablement_policy`, `factor_mix_live_enablement_policy`, `momentum_live_enablement_policy`, `policy_value_live_enablement_policy`, `special_situation_live_enablement_policy`, `rollout_risk_policy`, `notification_audit_policy`, and `production_source_audit_policy`. For `hk_blue_chip_leader_rotation`, the pack must also include `strategy_policy_evidence` matching `hk_snapshot_baseline_rotation_live_enablement_policy.v1` and prove HSI constituent/review, benchmark-relative momentum, 52-week-high, sector/liquidity, board-lot/VCM/CAS/session, rebalance-buffer, and dry-run provenance. For `hk_low_vol_dividend_quality`, `hk_shareholder_yield_quality`, and `hk_free_cash_flow_quality`, the evidence pack must also include a conditional `strategy_policy_evidence` section whose `policy_version` matches `hk_snapshot_quality_yield_live_enablement_policy.v1`, `status=passed`, `evidence_uri` is stable, `evidence_generated_at` is fresh, and all quality/yield ablation, stress-test, and data-provenance flags are true. For `hk_residual_momentum_quality`, `hk_liquid_momentum_quality`, and `hk_composite_factor_quality_value_momentum`, `strategy_policy_evidence.policy_version` must match `hk_snapshot_momentum_live_enablement_policy.v1`, and the pack must prove residual/liquid/composite same-universe ablation, HSI/MSCI descriptor reconciliation, one-month-skip / risk-adjusted momentum, momentum-crash stress, and data-provenance flags. For `hk_quality_growth_low_volatility`, `hk_factor_mix_qvlm_risk_parity`, `hk_central_soe_value_quality_select`, `hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, and `hk_index_rebalance_event`, the same section must match the corresponding quality-growth / factor-mix / policy-value / special-situation policy version and pass every required ablation, stress-test, and data-provenance flag. The evidence pack must cover production data-source audit, artifact-pack validation result and publication provenance, walk-forward / out-of-sample backtest, platform dry-run order preview, broker permission/fee verification, the required rebalance/event windows, runtime rollout plan, and operator approval. Production source audits must satisfy common point-in-time / adjusted-price / corporate-action / suspension / stale-price / missing-field / symbol-mapping / survivorship-safe-universe fields, source coverage start/end dates, stable `production_source_uri`, `source_quality_report_uri`, `point_in_time_data_dictionary_uri`, plus profile-specific fields such as HKEX buyback disclosure, next-day repurchase returns, treasury-share retention/cancellation/resale, moratorium/blackout controls, and post-buyback financing review for shareholder yield, Stock Connect turnover/holding history, top-10 turnover, CCASS Southbound shareholding, eligible-security history, market-data dissemination changes, raw-vs-vendor reconciliation, and trading-calendar alignment for southbound flow, A/H close-time alignment, AH price-ratio formula lineage, AH Smart switch thresholds, FX provenance, access/shorting/settlement constraints, and eligibility history for AH premium, official review-result source, HSI methodology / operation-guide versions, schedule-file version / next-review notice / review-result press-release provenance, constituent weight / pro-forma records, add/delete labels, fast-entry / suspension / buffer-rule exceptions, HKEX CAS / market-on-close random-close / two-stage price-limit / order-rejection controls, passive-flow imbalance evidence, and event crowding/slippage controls for index events, or revenue / earnings / ROE growth, accruals, cash-flow-to-debt, volatility, sector, and Southbound eligibility history for quality growth. Artifact provenance must include immutable `artifact_release_id`, contract version, snapshot sha256, row count, published snapshot/manifest/ranking/release-summary URIs, non-sample artifact proof, manifest sha256/row-count reconciliation, and release-summary readiness. `production_source_audit_policy.source_reference_urls` lists first-party references to check, such as HKEXnews, HKEX Stock Connect statistics, Hang Seng Indexes, or S&P index pages. The default max-drawdown gate is 30%; the backtest must also cover at least three walk-forward / out-of-sample years, have positive annual return, have positive excess return versus the profile benchmark, remain below the profile annualized-turnover cap, and explicitly include HK fees/levies, stamp duty or exemption, slippage, lot-size rounding, suspension handling, survivorship-bias controls, and look-ahead-bias controls. Normal snapshot profiles need at least three paper/dry-run rebalance windows; event profiles need at least one event window. Passing packs must also include non-empty stable `evidence_uri` values (`https://`, `gs://`, or `s3://`) and ISO-date `evidence_generated_at` values for each non-approval evidence section; generated dates must satisfy `evidence_freshness_policy.max_allowed_age_days_by_section`, dry-run order previews must satisfy `execution_capacity_policy` ADV and HK board-lot / odd-lot / VCM controls, `dry_run_order_preview_policy` (`dry_run_session_id`, stable raw order-preview / quote-snapshot / fee-breakdown URIs, 64-character hex sha256 values, non-sample/redaction/quote-coverage/broker-fee-reconciliation/strategy-decision-reconciliation proof), plus `notification_audit_policy` (`hk_snapshot_live_enablement_dry_run`, EN/ZH-Hans locales, correlation id, redaction, stable `notification_delivery_log_uri`), runtime rollout plans must satisfy `rollout_risk_policy` staged rollout / tripwire / kill-switch / SWT-runbook controls, those URIs must not contain token/password/signature-like query parameters, and `risk_approval.approval_reference` must be non-empty; boolean-only, stale-evidence, missing-provenance, over-capacity, or no-rollout-control packs are rejected.

## Platform integration

After the profile is promoted, publish the snapshot and manifest to the platform runtime artifact location, then set:

- `IBKR_FEATURE_SNAPSHOT_PATH` and `IBKR_FEATURE_SNAPSHOT_MANIFEST_PATH` for `InteractiveBrokersPlatform`.
- `LONGBRIDGE_FEATURE_SNAPSHOT_PATH` and `LONGBRIDGE_FEATURE_SNAPSHOT_MANIFEST_PATH` for `LongBridgePlatform`.

The platform service should also run in HK market mode:

- IBKR: `IBKR_MARKET=HK`, `IBKR_MARKET_EXCHANGE=SEHK`, `IBKR_MARKET_CURRENCY=HKD`.
- LongBridge: `ACCOUNT_REGION=HK` or `LONGBRIDGE_MARKET=HK`.
