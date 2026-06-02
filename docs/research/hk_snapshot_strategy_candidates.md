# HK Snapshot Strategy Candidates

> ⚠️ 投资有风险，不构成投资建议，仅供学习交流用途。

## 中文摘要

- 用途：记录港股 snapshot-backed 策略候选、artifact contract 演进方向和 live-enable 边界。
- 主要覆盖：`hk_blue_chip_leader_rotation`、`hk_low_vol_dividend_quality`、`hk_liquid_momentum_quality`、`hk_composite_factor_quality_value_momentum`、`hk_factor_mix_qvlm_risk_parity`、`hk_quality_growth_low_volatility`、`hk_residual_momentum_quality`、`hk_shareholder_yield_quality`、`hk_free_cash_flow_quality`、`hk_southbound_flow_momentum`、`hk_index_rebalance_event`、`hk_ah_premium_relative_value`。
- 当前状态：`hk_blue_chip_leader_rotation`、`hk_low_vol_dividend_quality`、`hk_liquid_momentum_quality`、`hk_composite_factor_quality_value_momentum`、`hk_factor_mix_qvlm_risk_parity`、`hk_quality_growth_low_volatility`、`hk_residual_momentum_quality`、`hk_shareholder_yield_quality`、`hk_free_cash_flow_quality`、`hk_southbound_flow_momentum`、`hk_ah_premium_relative_value` 和 `hk_index_rebalance_event` 已有可测试 scaffold；本次只补 live-enable policy/evidence gate，不新增 production 数据源，也不改变现有 `hk_blue_chip_leader_rotation` contract。
- 边界：snapshot 仓库只负责数据快照、manifest、ranking preview 和策略 helper；平台仓库负责 Cloud Run、券商权限、订单、通知和运行报告。

Research refresh date: 2026-06-02

This note keeps HK snapshot-backed strategy research separate from the non-snapshot runtime profiles in `HkEquityStrategies`. None of the candidates below are live-enabled. A candidate can only be promoted after the production data source, manifest publication, backtest, paper trading, and platform dry-run evidence are available.

Current live-enable evidence gate:

- `walk_forward_backtest.annual_return` must be positive.
- `walk_forward_backtest.max_drawdown` must not exceed 30% in absolute value.
- `walk_forward_backtest.annualized_turnover` must stay below the profile cap exposed by `hkeq-validate-live-enable-evidence --print-template`.
- `walk_forward_backtest.period_start` / `period_end` must cover at least three out-of-sample years.
- `walk_forward_backtest.benchmark_symbol` must match the profile benchmark, and `strategy_excess_return` must be positive.
- The backtest must explicitly include HK fees/levies, stamp duty or exemption, slippage, lot-size rounding, suspension handling, survivorship-bias controls, and look-ahead-bias controls.
- Normal snapshot profiles need at least three paper/dry-run rebalance windows; event profiles need at least one event window.
- Production source audit, artifact pack validation, walk-forward backtest, platform dry-run order preview, broker permission/fee verification, and rebalance/event-window sections must each include a non-empty stable `evidence_uri` (`https://`, `gs://`, or `s3://`) without token/password/signature-like query parameters; `risk_approval.approval_reference` must also be non-empty. Production source audit must additionally include `source_coverage_start` / `source_coverage_end`, stable `production_source_uri`, stable `source_quality_report_uri`, and stable `point_in_time_data_dictionary_uri`.
- Artifact pack validation must also satisfy `artifact_provenance_policy`: immutable `artifact_release_id`, contract version, snapshot sha256, row count, stable published snapshot/manifest/ranking/release-summary URIs, non-sample proof, manifest sha256/row-count reconciliation, and release-summary readiness.
- Platform dry-run order preview must satisfy `execution_capacity_policy`: enough ADV history, sufficient median daily turnover, single-order and rebalance ADV fractions below caps, and explicit proof that liquidity caps, board-lot rounding, odd-lot avoidance, trading-session routing, and VCM/price-band controls were verified.
- Platform dry-run order preview must also satisfy `dry_run_order_preview_policy`: include `dry_run_session_id`, stable `raw_order_preview_uri`, `quote_snapshot_uri`, and `fee_breakdown_uri`, 64-character hex sha256 values for each artifact, non-sample/redaction proof, quote coverage for all symbols, broker-fee reconciliation, and strategy-decision reconciliation.
- Platform dry-run order preview must also satisfy `notification_audit_policy`: use `hk_live_enablement_notification.v1` with `hk_snapshot_live_enablement_dry_run`, provide EN/ZH-Hans operator text, profile/platform/status/order-preview summary flags, a correlation id, redaction proof, and a stable `notification_delivery_log_uri`.
- Runtime rollout plan must satisfy `rollout_risk_policy`: first live exposure is capped, per-symbol exposure is capped, intraday/cumulative drawdown tripwires are documented, kill switch and rollback are ready, operator notifications are active, severe-weather trading and VCM runbooks are reviewed, and scale-up waits for the required observation window.
- The template and validator expose `production_source_audit_policy.required_boolean_fields`; every profile must prove common point-in-time adjusted price / corporate action / suspension / stale-field / symbol-mapping / survivorship-safe-universe controls plus its own data-source fields before promotion. For example, shareholder yield requires HKEX buyback disclosure and share-count history, southbound flow requires Stock Connect daily turnover and holding history, A/H premium requires A/H close alignment and FX history, and index rebalance requires official review history and announcement/effective timestamps.
- `production_source_audit_policy.source_reference_urls` lists suggested first-party references for each profile, such as HKEXnews share-repurchase reports, HKEX Stock Connect statistics, Hang Seng Indexes methodology/factsheet pages, and S&P index pages. These references explain what to audit; the actual evidence pack must still point to stable internal audit artifacts through section-level `evidence_uri` values.
- The live-enable evidence pack also exposes `evidence_freshness_policy`. Production source audit, artifact pack validation, walk-forward backtest, platform dry-run order preview, broker permission/fee verification, and rebalance/event-window evidence must each include ISO-date `evidence_generated_at` values within the section-specific freshness windows; stale or future-dated evidence remains blocked even if all boolean fields are true.
- Every current snapshot profile family now has a conditional `strategy_policy_evidence` gate. For `hk_blue_chip_leader_rotation`, that gate is `hk_snapshot_baseline_rotation_live_enablement_policy.v1` and requires HSI constituent/review provenance, point-in-time adjusted prices, benchmark-relative momentum, 52-week-high, liquidity/sector, board-lot, VCM/CAS/session controls, rebalance-buffer ablation, and dry-run order-preview provenance.

## External evidence used for prioritization

- HKEX's 10-year Stock Connect review says Southbound ADT reached HK$38.3B in Q1-Q3 2024 and accounted for 16.9% of Hong Kong market turnover; Southbound ETF ADT reached HK$2.53B in Q3 2024. HKEX also exposes historical daily Stock Connect statistics, Southbound CCASS shareholding search, eligible securities, and a 2024 data-dissemination change that removes real-time buy/sell/total turnover while preserving historical daily/monthly totals and top-10 active-stock turnover. This makes flow snapshots worth researching, but only with collector, point-in-time eligibility, and data-dissemination controls. References: https://www.hkex.com.hk/Mutual-Market/Connect-Hub/Stock-Connect-White-Paper?sc_lang=en, https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Statistics/Historical-Daily?sc_lang=en, https://www3.hkexnews.hk/sdw/search/mutualmarket.aspx?t=hk, https://www.hkex.com.hk/mutual-market/stock-connect/eligible-stocks/view-all-eligible-securities?sc_lang=en, and https://www.hkex.com.hk/News/Market-Communications/2024/2404122news?sc_lang=en
- Hang Seng Indexes and HKEX provide the official HSI page, HSI methodology / index-methodology guide, securities market statistics, trading mechanism, and VCM references needed for a baseline blue-chip rotation source audit. This is useful for platform plumbing and smoke-testing artifact contracts, but live-enable still requires same-universe ablation versus an HSI tracker and momentum alternatives, plus board-lot/VCM/session dry-run proof. References: https://www.hsi.com.hk/eng/indexes/all-indexes/hsi, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsie.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf, https://www.hkex.com.hk/Market-Data/Statistics/Securities-Market?sc_lang=en, https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en, and https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/VCM?sc_lang=en
- Hang Seng Low Volatility Index selects low-volatility HK-listed large/mid-cap companies with positive earnings and dividend records; as of April 2026 its fact sheet reports dividend yield and annual volatility fields that are directly useful for factor snapshots. Reference: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hslvie.pdf
- Hang Seng High Dividend Yield Index uses net-dividend-yield ranking, annual review, and 10% constituent cap; its methodology also includes exceptional handling for abnormally high-yield candidates. Reference: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshdyie.pdf
- Hang Seng SCHK High Dividend Low Volatility Index (HSHYLV) targets Southbound-eligible Hong Kong securities and documents a three-consecutive-fiscal-year cash-dividend record, payout-ratio bounds, and price-performance screening. This is now reflected in the low-vol dividend live-enable source audit. References: https://www.hsi.com.hk/eng/indexes/all-indexes/hshylv, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hshylve.pdf, and https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hshylve.pdf
- Hang Seng SCHK High Dividend Yield Screened Index (HSSCHYS) adds a screened high-dividend reference for Southbound-eligible large/mid-cap names. Its factsheet reports financially sound company screening and its methodology reference documents market-value shortlisting, one-year high-volatility exclusion, three-year cash-dividend records, and price-performance screening; its April 2026 factsheet reports strong total-return history but the data remain index/backtest evidence, not our live performance. References: https://www.hsi.com.hk/eng/indexes/all-indexes/hsschys, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsschyse.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsschkye.pdf, and https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20231214T000000.pdf
- S&P Dow Jones Indices research and index methodology on Hong Kong smart beta and low-volatility high-dividend portfolios supports combining dividend yield with low-volatility screening rather than buying high yield alone; the S&P Access Hong Kong Low Volatility High Dividend Index measures 50 least-volatile high-yielding stocks, and the newer ETF Connect Hong Kong & U.S. low-vol high-dividend index explicitly references HKEX ETF Connect eligibility. References: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3054594, https://www.indexologyblog.com/2017/10/19/does-low-volatility-enhance-dividend-investing-in-the-hong-kong-market/, https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-low-volatility-high-dividend-index/, https://www.spglobal.com/spdji/en/methodology/article/sp-low-volatility-high-dividend-indices-methodology/, and https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-etf-connect-hong-kong-us-low-volatility-high-dividend-index/
- Hang Seng Indexes' 2019 momentum research reports a positive momentum effect in the Hong Kong market across tested descriptors, with current-price-to-high-price (CTH) performing well and a 3-month plus 12-month CTH combination with semi-annual rebalancing presented as a more investable design. Reference: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20191216T000000.pdf
- HSI's Quality Growth Low Volatility methodology and MSCI's Quality / Minimum Volatility materials support a defensive growth direction, but live-enable must not treat ROE or low volatility as sufficient by themselves. Required evidence now includes HSI QGLV score lineage, MSCI quality variables (ROE, stable earnings growth, low leverage), minimum-volatility optimizer constraints, cash-conversion / accrual quality-trap controls, sector concentration, and Southbound universe capacity. References: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsqglve.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsqglve.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisve.pdf, https://www.msci.com/indexes/group/quality-indexes, https://www.msci.com/indexes/index/721604, https://www.msci.com/indexes/group/minimum-volatility-indexes/, and https://www.msci.com/documents/10199/1396fa66-b4bd-40f3-8dfb-0109895d94ac
- Hang Seng's current Momentum Indexes methodology is explicitly designed to gauge momentum-factor performance while considering tracking error and factor exposure; it uses quality screening, factor tilting, industry-neutral weighting, capping, half-yearly reviews, and quarterly rebalancing. This supports an explicit momentum-factor snapshot, while our implementation keeps residual/industry-neutral fields upstream and blocks live-enable until turnover/cost evidence is available. Reference: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf
- Hang Seng's April 2026 SCHK SOEs Momentum Index fact sheet describes a Southbound-tradable SOE momentum index with momentum screening, weight tilting, a 5% security cap, and published volatility/fundamental fields. This supports a constrained momentum sleeve, but it is also evidence that live-enable must test concentration, SOE/policy-event risk, and Southbound eligibility rather than copying a raw price signal. Reference: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscsme.pdf
- MSCI's Hong Kong Momentum / Hong Kong Listed Southbound Momentum materials and Momentum Indexes methodology add an independent descriptor family: 6-month and 12-month risk-adjusted momentum with one-month reversal skip, volatility normalization, score ranking, capping, and turnover-buffer style controls. This is useful live-enable evidence, but it is not production proof; our snapshots must reconcile MSCI-style descriptors with HSI close-to-high / 12-1 fields before platform selection. References: https://www.msci.com/indexes/group/momentum-indexes, https://www.msci.com/indexes/index/711028, https://www.msci.com/indexes/documents/methodology/2_MSCI_Momentum_Indexes_Methodology_20250417.pdf, and https://www.msci.com/documents/10199/a79b1588-26c8-5224-d68b-269b256ba22c
- Hang Seng's SCHK SOEs factor methodology uses current price to 52-week high as its momentum factor and combines quality, value, low-volatility, and momentum into a selected-factor index. This supports keeping pure momentum as a snapshot component and evaluating future composite factor variants rather than live-enabling a high-turnover price-only signal. References: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisme.pdf and https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf
- HKEX's May 2026 ETF Connect factsheet reports rising Southbound ETF turnover and lists HK-listed eligible ETFs across broad market, technology, high-dividend, biotech, and global exposure categories. This supports ETF-based rotation research while keeping single-name momentum in snapshot contracts until production evidence is stronger. Reference: https://www.hkex.com.hk/-/media/HKEX-Market/Products/Securities/Exchange-Traded-Products/Launch/Inclusion-of-ETFs-in-Stock-Connect_Investor.pdf
- HKEX's June 2025 listing-regulation newsletter says on-exchange share buybacks doubled from HK$127B in 2023 to HK$262B in 2024, and HKEXnews publishes daily share-repurchase reports. This supports a shareholder-yield snapshot that combines dividends, actual buybacks, share-count change, and quality controls. References: https://www.hkex.com.hk/-/media/HKEX-Market/Listing/Rules-and-Guidance/Other-Resources/Listed-Issuers/LIR-Newsletter/newsletter_202506.pdf and https://www3.hkexnews.hk/reports/sharerepur/sbn.asp
- A 2025 southbound-flow predictability paper reports that southbound capital flows can predict short-term HK stock returns and that a weekly long-short portfolio reached up to 25.84% annualized after Fama-French five-factor adjustment. This is useful research evidence for `hk_southbound_flow_momentum`, but it is not our live evidence because the paper uses external databases and a long-short construction. Reference: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5128472
- HKEX's treasury-share rule materials add mandatory implementation details for buyback-derived factors: next-day share-repurchase returns, purchased-share cancellation versus treasury retention, resale moratorium/blackout and connected-person controls, and review of post-buyback financing or public-float effects. These are now explicit source-audit fields for `hk_shareholder_yield_quality`. References: https://en-rules.hkex.com.hk/rulebook/9-repurchase-securities-and-treasury-shares, https://en-rules.hkex.com.hk/entiresection/498, https://www.hkex.com.hk/News/Regulatory-Announcements/2024/240412news?sc_lang=en, and https://www.hkex.com.hk/Listing/Education-Centre/Listed-Issuers/Share-Repurchase-and-Treasury-Shares?sc_lang=en
- S&P Global Market Intelligence research reports that high forecast dividend yield factors outperformed Hong Kong SAR's benchmark by 2.43% annualized over the past decade and had better risk-adjusted metrics than trailing dividend yield. This supports keeping shareholder yield tied to dividend/quality fields rather than pure buyback intensity. Reference: https://www.spglobal.com/market-intelligence/en/news-insights/research/forecast-dividend-yield-strategy-outperforms-hong-kong-sar
- Hang Seng's SCHK Free Cash Flow Index aims to track 50 high free-cash-flow-yield HK-listed securities eligible for Southbound Trading, with methodology requiring positive EV, positive FCF for the latest three consecutive fiscal years, a price-performance screen, half-yearly review, FCF weighting, and a 10% security cap. S&P's Access Hong Kong Free Cash Flow 50 methodology adds an explicit FCF/EV formula, sector-specific FCF calculations, positive FCF/EV eligibility, ROE and liquidity checks, a 50-constituent selection process, and 5% security/sector diversification constraints. This supports promoting `free_cash_flow_yield` from a composite sleeve into a dedicated `hk_free_cash_flow_quality` scaffold, while still blocking live-enable until production fundamentals are audited. References: https://www.hsi.com.hk/eng/indexes/all-indexes/hsscfcf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hsscfcfe.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscfcfe.pdf, https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-free-cash-flow-50-index/, https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-access-hk-fcf-50-index.pdf, and https://www.spglobal.com/spdji/en/indices/dividends-factors/sp-access-hong-kong-dividend-free-cash-flow-index/
- Hang Seng Indexes regular reviews use quarterly data cutoffs at the end of March, June, September, and December with review results announced within eight weeks; HSIL also publishes an operation guide and schedule files, while HKEX CAS documentation defines random-close and two-stage price-limit/order-type constraints. This supports event-calendar snapshots, but event sample size, MOC-vs-next-open execution choice, pro-forma weighting, order rejection, passive-flow imbalance, and slippage risk are material. References: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_methodology_guide_e.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/index_operation_guide_e.pdf, https://www.hsi.com.hk/static/uploads/contents/en/products/is_update.xlsx, https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/CAS?sc_lang=en, and https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en
- Hang Seng Stock Connect China AH Premium Index tracks the average price premium or discount of A shares over H shares for liquid AH companies that are eligible for Northbound and Southbound Stock Connect. The April 2026 fact sheet reported the index above 120, while HSI's 2024 index flash treated a 15-year high in AH premium as a possible market-trough signal rather than guaranteed convergence. HSI's AH Smart note documents share-class switching when AH price ratio thresholds are breached, and SSE's SH-HK AH Premium methodology documents an adjusted-market-cap / FX formula for A-vs-H premium. H-share discount signals therefore remain observable, but live-enable must recompute price-ratio lineage and stress false reversals, FX, settlement, and A-share access / shorting constraints. References: https://www.hsi.com.hk/eng/indexes/all-indexes/ahpremium, https://www.hsi.com.hk/eng/indexes/all-indexes/chinaah, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/ahpremiume.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/index_flash/20240124T000000.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/blog/20210914T000000.pdf, and https://english.sse.com.cn/indices/indices/list/indexmethods/c/H50066_h50066hbooken_EN.pdf
- Hang Seng's Risk Parity Factor Mix (QVLM) index combines quality, value, low-volatility, and momentum component indexes on the Hang Seng Large-Mid Cap (Investable) universe with a risk-parity approach and 12% cap, while Hang Seng also publishes an equal-weight factor-mix series. MSCI maintains a Hong Kong Factor Mix A-Series Capped index integrating quality, value, and low-volatility factor strategies in equal weights. This supports an active `hk_factor_mix_qvlm_risk_parity` scaffold, but live-enable still requires same-universe ablations versus HSI equal-weight factor mix, MSCI equal-weight Q/V/L controls, and composite QVM plus component-index return, factor-volatility, covariance, capping, and turnover provenance. References: https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/factsheets/hssbmfrpe.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbmfrpe.pdf, https://www.hsi.com.hk/eng/indexes/all-indexes/hssbmfew, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hsscsqe.pdf, https://www.msci.com/indexes/factor-indexes/factor-mix-a-series-indexes, https://www.msci.com/indexes/index/705097, https://www.msci.com/eqb/methodology/meth_docs/MSCI_Factor_Mix_Indexes_Methodology_Apr16.pdf, and https://www.msci.com/research-and-insights/paper/the-msci-quality-mix-indexes

## Candidate priority

| Priority | Candidate | Snapshot type | Suggested status | Why |
| ---: | --- | --- | --- | --- |
| 1 | `hk_low_vol_dividend_quality` | `factor_snapshot` | scaffolded, not live | Best fit for HK evidence; slower rebalance can absorb costs. |
| 2 | `hk_shareholder_yield_quality` | `factor_snapshot` | scaffolded, not live | Combines dividends, actual buybacks, share-count change, FCF, and low-volatility quality controls. |
| 3 | `hk_free_cash_flow_quality` | `factor_snapshot` | scaffolded, not live | Dedicated FCF-yield quality/value scaffold with Southbound eligibility and low-volatility risk controls. |
| 4 | `hk_quality_growth_low_volatility` | `factor_snapshot` | scaffolded, not live | Quality-growth with low-volatility controls is supported by Hang Seng / MSCI evidence, but it needs production fundamentals and factor ablation. |
| 5 | `hk_factor_mix_qvlm_risk_parity` | `factor_snapshot` | scaffolded, not live | Risk-parity QVLM diversifies quality, value, low-volatility, and momentum sleeves, but it needs factor-volatility provenance and ablations. |
| 6 | `hk_central_soe_value_quality_select` | `factor_snapshot` | scaffolded, not live | Central-SOE value-quality uses a HK-specific policy/value universe, but it needs ownership provenance, sector concentration, and policy-event stress controls. |
| 7 | `hk_residual_momentum_quality` | `factor_snapshot` | scaffolded, not live | Closer US-style cross-sectional momentum analogue with residual / industry-neutral momentum and beta/volatility controls. |
| 8 | `hk_liquid_momentum_quality` | `feature_snapshot` | scaffolded, not live | Direct answer to HK stock momentum; uses liquid large/mid caps, risk-adjusted momentum, 52-week-high proximity, and trend filters. |
| 9 | `hk_composite_factor_quality_value_momentum` | `factor_snapshot` | scaffolded, not live | HK analogue to a multi-factor stock-selection model; combines quality, value, momentum, and low-volatility. |
| 10 | `hk_southbound_flow_momentum` | `flow_snapshot` | scaffolded, not live | Southbound flow is economically relevant, but raw data must be normalized and smoothed. |
| 11 | `hk_ah_premium_relative_value` | `valuation_snapshot` | scaffolded, not live | HK-specific signal, safer first as valuation overlay than long/short arbitrage. |
| 12 | `hk_blue_chip_leader_rotation` | `feature_snapshot` | scaffolded, not live | Useful platform contract baseline, but not the preferred first single-name live strategy. |
| 13 | `hk_index_rebalance_event` | `event_calendar_snapshot` | scaffolded, not live | Official review calendar is repeatable, but sample size and slippage make live promotion harder. |

The detailed sketches below keep the historical implementation-note order. For machine-readable promotion order, use `hkeq-print-snapshot-promotion-matrix --json`; its `recommended_live_enablement_sequence`, `recommended_live_enablement_stage`, `next_live_enablement_action`, and `momentum_live_enablement_comparison` fields are the source of truth for platform status pages and live-enable planning.

### Baseline blue-chip rotation live-enable policy

`hk_blue_chip_leader_rotation` remains a baseline feature-snapshot scaffold for platform contract validation, not the preferred first single-name live strategy. It now has a machine-readable `baseline_rotation_live_enablement_policy` so it cannot bypass the same strategy-policy gate applied to factor, momentum, and special-situation profiles.

Required pre-live evidence now includes:

- blue-chip rotation versus HSI tracker on the same survivorship-safe universe;
- baseline rotation versus `hk_liquid_momentum_quality`, relative momentum versus absolute momentum versus 52-week-high, and HSI-only versus HSI/HSCEI/HSTECH liquid-universe ablations;
- sector-neutral versus sector-unconstrained leader weights, quality/liquidity filter on/off, and rebalance-buffer versus naive monthly rotation checks;
- HSI/HSTECH leadership reversal, China macro / HKD liquidity, crowded blue-chip slippage, suspension/stale-price/corporate-action, sector concentration, turnover spike, lot-size, VCM/CAS, and trading-session stress windows;
- point-in-time HSI constituent/review history, adjusted price history, benchmark-relative momentum, 52-week-high, ADV/market-cap/board-lot, sector classification, corporate-action/suspension/stale-price, rebalance-buffer/capacity, and HKEX VCM/trading-session provenance.

The live-enable evidence validator now requires `strategy_policy_evidence.policy_version=hk_snapshot_baseline_rotation_live_enablement_policy.v1` for this profile, with passed status, stable URI, fresh `evidence_generated_at`, and every required ablation, stress-test, and data-provenance flag set to true.

### Quality / yield first-candidate live-enable policy

The first promotion bucket remains `hk_low_vol_dividend_quality`, `hk_shareholder_yield_quality`, and `hk_free_cash_flow_quality`, but they now have their own machine-readable `quality_yield_live_enablement_policy`. Before any of them can remove dry-run, platform evidence must compare all three on the same survivorship-safe universe and prove that the apparent yield/quality edge is not just a dividend trap, buyback headline, stale fundamental, or sector bet.

Required pre-live evidence now includes:

- low-vol dividend vs shareholder-yield vs FCF same-universe ablation;
- HSI HSHYLV/HSSCHYS versus S&P Access HK Low Volatility High Dividend same-universe reconciliation, including methodology, constituent, rebalance, and capping history;
- forecast dividend yield versus trailing dividend yield same-universe ablation with point-in-time estimate history and stale-revision controls;
- dividend-yield-only vs dividend-quality controls;
- HSHYLV-style Southbound eligibility, three-year cash-dividend record, payout-ratio bounds, and price-crash / bottom-decile screens;
- HSSCHYS-style large/mid-cap market-value shortlist, one-year high-volatility exclusion, and financial-soundness screens;
- raw buyback yield vs share-count-reduction-adjusted shareholder yield;
- HKEX next-day share-repurchase returns, treasury-share cancellation/retention/resale treatment, moratorium/blackout/connected-person controls, and post-buyback financing / convertible / public-float review;
- raw FCF yield vs sector-normalized FCF quality;
- forecast-dividend cuts, estimate-revision staleness, financials-sector forward-yield concentration, yield-trap, payout-cut, property/financials/utilities sector concentration, rate-cycle/HKD-liquidity, treasury-share resale/dilution, reporting-date/restatement, suspension, lot-size and slippage stress windows.

This policy is grounded in current external evidence: Hang Seng's HSHYLV index documents Southbound, three-year cash-dividend, payout-ratio, and price-performance screens for HK low-volatility high-dividend selection; HSSCHYS adds high-dividend screened large/mid-cap, high-volatility-exclusion, and financial-soundness references; S&P documents low-volatility high-dividend research, methodology, index-linked product evidence, and ETF Connect eligibility context for Hong Kong; S&P Global Market Intelligence separately reports that forecast dividend yield outperformed trailing dividend yield in Hong Kong research, so the policy now requires point-in-time estimate provenance and forecast-vs-trailing ablation instead of accepting forward yield by default; HKEX reports rapidly growing on-exchange buyback activity, provides share-repurchase reports, and documents treasury-share resale / moratorium / blackout controls; and Hang Seng/S&P maintain Free Cash Flow / Dividend Free Cash Flow Hong Kong index references. The live-enable evidence validator now requires a conditional `strategy_policy_evidence` section for these quality/yield profiles, with passed status, stable URI, fresh `evidence_generated_at`, matching `hk_snapshot_quality_yield_live_enablement_policy.v1`, and every required ablation, stress-test, and data-provenance flag set to true. The policy is still a gate, not a live switch: production fundamentals/disclosure data, walk-forward backtests, artifact provenance, dry-run order previews, bilingual notification logs, and operator approval remain mandatory.

### Momentum factor live-enable comparison

Hong Kong can support a US-style momentum factor stock-selection architecture, but it should not be a raw high-turnover price chase. The machine-readable comparison now ranks the three momentum-related scaffolds before any live-enable attempt:

1. `hk_residual_momentum_quality` is the preferred first momentum-factor candidate because it is closest to a US-style cross-sectional momentum model: residual / industry-neutral momentum, industry-relative momentum, benchmark-relative momentum, beta, volatility, drawdown, suspension, and Southbound eligibility controls.
2. `hk_liquid_momentum_quality` is the simpler price-momentum fallback when production residual-factor history is not ready. It is easier to source from adjusted prices, liquidity, and recent-high/trend fields, but needs stricter turnover and reversal stress tests.
3. `hk_composite_factor_quality_value_momentum` should be treated as a broader multi-factor model, not proof of a standalone momentum strategy, until factor ablation shows the momentum sleeve adds robust excess return beyond quality, value, and low-volatility.

All three must be compared on the same survivorship-safe universe, benchmark window, HK cost/slippage/lot-size model, artifact provenance policy, evidence freshness policy, execution-capacity policy, `dry_run_order_preview_policy`, bilingual notification audit policy, rollout tripwires, and operator approval flow before dry-run can be removed. The same `momentum_live_enablement_policy` is now emitted by the promotion matrix, per-profile readiness output, and live-enable evidence template/validator results, so platform tooling cannot accidentally treat momentum profiles as generic snapshot scaffolds. The live-enable evidence validator now also requires a conditional `strategy_policy_evidence` section for momentum profiles, with passed status, stable URI, fresh `evidence_generated_at`, matching `hk_snapshot_momentum_live_enablement_policy.v1`, and every required momentum ablation, stress-test, and data-provenance flag set to true. The same conditional section is now enforced for baseline rotation, quality-growth, factor-mix, policy-value, and special-situation profiles, each with its own matching policy version and all required ablation, stress-test, and data-provenance flags set to true. The machine-readable `momentum_live_enablement_policy` now requires factor ablation (`residual_vs_liquid_vs_composite_same_universe`, momentum sleeve versus quality/value/low-volatility sleeves, 52-week-high versus 12-1 momentum, MSCI 6/12-month one-month-skip versus HSI close-to-high descriptors, risk-adjusted versus raw momentum, industry-neutral versus unconstrained, and quality-screen on/off), stress windows (HSI/HSTECH sharp reversal, high-beta rebound, suspensions/stale prices, Southbound holiday/policy events, fee/slippage/lot-size sensitivity, turnover-buffer spikes, sector concentration, and Southbound momentum-universe capacity), and data provenance for point-in-time adjusted prices, industry classification, ROE/debt/EPS variability, current-price-to-52-week-high, MSCI-style 6/12-month one-month-skip momentum, volatility normalization, winsorization/ranking, HSI smart-beta descriptor history, benchmark comparisons, ADV, and suspension history.

### Flow / valuation / event special-situation live-enable policy

`hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, and `hk_index_rebalance_event` are now grouped by a machine-readable `special_situation_live_enablement_policy`. They remain later-stage snapshot scaffolds, but platform status pages and the live-enable evidence validator now use the same `strategy_policy_evidence` gate to show exactly why these HK-specific ideas are blocked before live use.

Required pre-live evidence now includes:

- Southbound flow versus price-momentum same-universe ablation, plus signal-decay and rebalance-frequency ablation;
- AH-premium overlay versus plain value/quality same-universe ablation;
- index-rebalance event window versus baseline liquidity-filter ablation, add/delete candidate-probability ablation, announcement-close versus effective-close execution-window ablation, market-on-close versus next-open execution ablation, official schedule versus press-release source reconciliation, and pro-forma-weighted versus equal-weight event-trade ablation;
- Stock Connect holiday, quota/policy-event, trading-suspension, missing-flow-day, real-time data-suppression, top-10-only turnover, CCASS shareholding lag, eligibility-mismatch, and crowding-reversal stress windows;
- AH close-time, FX-source, exchange-holiday, H-share liquidity, premium-widening, and short-sale/settlement constraint stress windows;
- official index review announcement-to-effective-date, quarterly review result announcement-after-close, review-schedule change / delayed press-release, effective-date market-on-close auction / passive-flow, fast-entry / suspension / buffer-rule exception, CAS random-close / two-stage price-limit / order-rejection, passive-flow closing-auction liquidity gap, add/delete side-label, slippage/capacity, and crowding stress windows.

Production source audits must now prove official HKEX Stock Connect turnover/holding and eligibility history, historical daily market turnover, top-10 turnover, CCASS Southbound shareholding percent issued, Stock Connect data-dissemination changes, raw-vs-vendor reconciliation, Stock Connect calendar alignment, AH pair mapping, AH price-ratio formula lineage, AH Smart share-class-switch thresholds, A-share access / shorting / settlement constraints, FX provenance, official index review result source URI, HSI methodology / operation-guide version history, quarterly schedule / cutoff and schedule-file version / effective-date history, next-review notice timestamps/scope, review-result press-release timestamps, constituent weight / pro-forma records, constituent add/delete effective-date history, fast-entry / suspension / buffer-rule exception history, announcement/effective timestamps, event side labels, HKEX CAS / market-on-close order-type, random-close, two-stage price-limit and order-rejection controls, closing-auction imbalance / passive-flow / spread evidence, and order-preview liquidity/crowding evidence. This policy is a gate, not a live switch: without production collectors, point-in-time history, walk-forward or event-window evidence, dry-run order-preview provenance, bilingual notification logs, rollout controls, and operator approval, all three profiles remain non-live.


### Quality-growth low-volatility live-enable policy

`hk_quality_growth_low_volatility` is now an active defensive-growth factor-snapshot scaffold, not a runtime profile. It remains blocked from live use until production evidence proves that growth, quality, and low-volatility each add robust excess return after HK costs, sector caps, and capacity constraints.

Required pre-live evidence now includes:

- quality-growth low-vol versus low-vol dividend, quality-only, growth-only, low-vol-only, first quality/yield candidates, and momentum candidates on the same survivorship-safe universe;
- HSI QGLV official four-component score lineage: ROE, accruals ratio, cash-flow-to-debt, and Growth in ROA adjusted by P/B, including winsorized z-scores, component averaging, Financials-only handling, negative-equity treatment, and missing-factor policy;
- MSCI quality variables (ROE, stable earnings growth, low financial leverage) reconciled against HSI QGLV score lineage;
- HSI low-volatility quality screen (ROE, debt-to-equity, 5-year EPS variability, and 12-month volatility) plus minimum-volatility optimizer constraints compared with simple beta / residual-volatility / drawdown filters;
- point-in-time reporting dates, restatements, valuation normalization, negative-equity / financials policy, cash-conversion and accrual quality-trap controls;
- stress windows for growth deceleration, high-P/B growth reversal, factor missingness / restatement / negative-equity handling, high valuation / HKD liquidity, platform regulation / technology drawdowns, real-estate / financials concentration, low-volatility crowding reversal, suspensions, holidays, lot-size, and slippage.

### Factor-mix QVLM risk-parity live-enable policy

`hk_factor_mix_qvlm_risk_parity` is now an active factor-snapshot scaffold, not a future backlog hint. It remains blocked from live use until production evidence proves that risk-parity QVLM improves robustness versus simpler factor mixes after HK costs and capacity constraints.

Required pre-live evidence now includes:

- QVLM risk-parity versus equal-weight factor mix on the same survivorship-safe universe;
- HSI QVLM risk-parity versus HSI equal-weight factor mix, and MSCI equal-weight Q/V/L factor mix versus HSI QVLM with and without the momentum sleeve;
- QVLM factor mix versus `hk_composite_factor_quality_value_momentum` on the same universe;
- quality, value, momentum, and low-volatility sleeve leave-one-out ablation;
- risk-parity factor-volatility window sensitivity, factor covariance/correlation stability, component-index overlap adjustment, cap-induced turnover, and rebalance-window sensitivity;
- HSI parent-universe, Quality/Value/Low Volatility/Momentum component-index methodology versions and return history, 12% cap / component-overlap history, factor score formula lineage, winsorization, and factor-leg turnover/capacity/crowding evidence;
- sector-neutral versus sector-unconstrained checks;
- factor crowding, low-volatility reversal, momentum crash, value-trap rotation, rate/HKD liquidity, Southbound holiday/policy-event, suspension, lot-size, slippage, and capacity stress windows.

Production source audits must prove point-in-time Q/V/L/M factor history, HSI QVLM parent Large-Mid Cap Investable universe, component-index methodology versions and return history, factor-volatility and risk-parity weight history, factor covariance/correlation history, HSI equal-weight factor-mix benchmark, MSCI factor-mix A-Series component-index equal weighting and capped-methodology history, component-overlap / sector-cap / single-name-cap history, sector classification, Southbound eligibility, valuation/fundamental reporting dates, liquidity, suspensions, and corporate-action controls before dry-run can be removed.


### Policy value / central-SOE live-enable policy

`hk_central_soe_value_quality_select` has been promoted from the future backlog into an active factor-snapshot scaffold. The external basis is Hang Seng's SCHK Central SOEs factor methodology: the universe targets Southbound-eligible companies whose own company or largest shareholder is a Chinese Central SOE, with the Central SOE source traced to SASAC and central-financial SOE lists, and the available indexes include value, quality, low-volatility, momentum, and selected-factor variants. The scaffold therefore combines a central-SOE ownership universe with value, quality, low-volatility, momentum, dividend-yield, and risk controls.

Required pre-live evidence now includes:

- point-in-time central-SOE largest-shareholder classification, look-through ownership chain, SASAC/MOF source-list effective dates, ownership percentage, source-list effective-date drift, and methodology-version history;
- HSI Central SOEs value/quality factor-index constituent, Z-score standardisation, missing-measure averaging, 40% factor-screening / buffer-rule lineage, 5% factor-index cap, and 10% base-weight cap lineage;
- HKEX Southbound point-in-time eligible-security history, including eligibility removal and Stock Connect calendar gaps;
- central-SOE value-quality versus broad value-quality, HSI Central SOEs value/quality factor indexes, all-SOE, and non-policy value-quality ablations on the same survivorship-safe universe;
- value-quality versus value-only and quality-only sleeve ablation, plus state-ownership threshold and SASAC-versus-MOF source sensitivity;
- sector-neutral versus sector-unconstrained checks because financials, energy, telecom, and infrastructure SOEs can dominate the universe;
- policy-event, SOE reform, SASAC/MOF reclassification, parent restructuring, source-list effective-date drift, HSI factor-screen/cap turnover spikes, macro-credit/property/rate-cycle, public-float, connected-transaction, sanctions/geopolitical, dividend-cut, suspension, lot-size, slippage, and capacity stress windows.

This policy is a gate, not a live switch: production ownership/fundamentals data, walk-forward evidence with max drawdown <= 30%, artifact provenance, dry-run order-preview evidence, bilingual notifications, rollout controls, and operator approval remain mandatory before dry-run can be removed.

### Quality growth low-volatility live-enable policy

`hk_quality_growth_low_volatility` is now an active factor-snapshot scaffold, not just a backlog hint. It is still blocked from live use until production evidence proves the quality-growth and low-volatility edge is robust after HK costs and capacity constraints.

Required pre-live evidence now includes:

- quality-growth low-vol versus low-vol dividend on the same survivorship-safe universe;
- quality-only versus growth-only versus low-vol-only ablation, plus HSI QGLV four-component score versus raw quality-growth-input ablation;
- HSI QGLV official four-component lineage for ROE, accruals ratio, cash-flow-to-debt, and Growth in ROA adjusted by P/B, including winsorized z-score averaging, Financials-only handling, negative-equity treatment, and missing-factor policy;
- HSI low-volatility quality screen versus simple 12-month-volatility / beta / drawdown filters;
- Southbound-eligible universe versus broader HK universe checks;
- sector-neutral versus sector-unconstrained weights;
- stress windows for growth deceleration, rate/HKD liquidity, high-P/B valuation reversal, factor missingness / restatement / negative equity, platform regulation, financials/property normalization, low-volatility crowding reversal, suspensions, lot-size, slippage, and Southbound holiday effects.

Production source audits must prove point-in-time revenue, earnings and ROA growth, ROE, accruals, cash-flow-to-debt, Growth in ROA adjusted by P/B, HSI QGLV winsorized z-score / component-averaging / Financials / negative-equity / missing-factor policy, HSI low-volatility quality-screen inputs, valuation normalization, volatility/beta/drawdown/liquidity history, sector classification, Southbound eligibility, and methodology-version provenance before dry-run can be removed.

### Future non-scaffolded backlog

The promotion matrix still exposes `future_research_backlog` for ideas that are supported by external index/research evidence but are not active artifact contracts. The backlog now contains `hk_earnings_revision_quality_overlay`, a research-only candidate that should use point-in-time analyst EPS forecast revisions as an overlay on existing HK quality, value, low-volatility, dividend, and FCF sleeves rather than as a standalone high-turnover signal; `hk_low_size_quality_liquidity_premium`, a research-only candidate that should test whether low-size exposure still adds robust excess return after Hang Seng Low Size-style quality screening, industry controls, and capacity filters; `hk_stock_connect_inclusion_event_flow`, a research-only event candidate that should test Stock Connect inclusion/exclusion and sell-only transitions with Southbound turnover or CCASS holding confirmation; `hk_short_selling_pressure_risk_overlay`, a research-only overlay candidate that should use HKEX short-selling turnover, designated-shortable status, and short-interest ratio evidence as a crowded-long / short-squeeze / negative-information risk signal, not as a direct shorting strategy; `hk_director_dealing_disclosure_quality_overlay`, a research-only overlay candidate that should use only disclosed SFC/HKEX Disclosure of Interests / director-dealing notices as an alignment / undervaluation signal after filing-lag, correction/cancellation, blackout/moratorium, connected-person transfer, routine option-exercise, and buyback-overlap controls; and `hk_dually_traded_liquid_reversal_overlay`, a research-only overlay candidate that should test liquid dually traded / cross-listed short-horizon reversal only after dual-listing mapping, foreign/HK close and FX alignment, weekly reversal signal, spread/fee/slippage/VCM/CAS, suspension, and capacity controls. S&P DJI earnings-revision research supports testing the first direction in Asia but also highlights why an overlay is more practical than a standalone strategy when turnover is high. Hang Seng Low Size methodology and smart-beta materials support testing the second direction, but only with free-float market-cap, HSICS industry, ROE / debt-to-equity / EPS-variability quality screens, ADV, spread, board-lot, suspension, and free-float capacity controls. HKEX eligible-securities lists and expansion announcements support testing the third direction, while event-study evidence suggests inclusion/exclusion effects can decay, so signal-decay and crowding stress are mandatory. HKEX regulated-short-selling data and Hong Kong short-sale research support testing the fourth direction, while squeeze, borrow, tick-rule, and option-hedging controls remain mandatory. SFC Part XV / DI Notices and HKEX Disclosure of Interests data support the fifth direction as a legal disclosed-information overlay, and Hong Kong director-dealing / share-repurchase research suggests the signal can interact with buyback undervaluation evidence, so illegal-insider-information language and trading assumptions must be avoided. Hong Kong contrarian / reversal research supports the sixth direction, but transaction costs can erase short-term overreaction profits, so the design must be restricted to liquid, execution-audited dually traded names and stay non-live until walk-forward evidence passes. References: https://www.spglobal.com/spdji/en/research/article/earnings-revision-overlay-on-fundamental-factors-in-asia/, https://www.spglobal.com/spdji/en/documents/research/research-do-earnings-revisions-matter-in-asia.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/methodologies/IM_hssbisse.pdf, https://www.hsi.com.hk/static/uploads/contents/en/news/pressRelease/20210118T000000.pdf, https://www.hsi.com.hk/static/uploads/contents/en/dl_centre/research_paper/20220408T000000.pdf, https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Eligible-Stocks/View-All-Eligible-Securities?sc_lang=en, https://www.hkex.com.hk/News/News-Release/2023/230303news?sc_lang=en, https://www.hkex.com.hk/-/media/HKEX-Market/Mutual-Market/Stock-Connect/Getting-Started/Information-Booklet-and-FAQ/FAQ/FAQ_En.pdf, https://econpapers.repec.org/article/kapapfinm/v_3a30_3ay_3a2023_3ai_3a4_3ad_3a10.1007_5fs10690-022-09395-3.htm, https://www.hkex.com.hk/Services/Trading/Securities/Overview/Regulated-Short-Selling?sc_lang=en, https://www.hkex.com.hk/Market-Data/Statistics/Securities-Market/Short-Selling-Turnover-Today?sc_lang=en, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2434387, https://www.sciencedirect.com/science/article/pii/S0378426609002064, https://www.sfc.hk/en/Rules-and-standards/Securities-and-Futures-Ordinance-Part-XV---Disclosure-of-Interests?oldnode=0, https://www.sfc.hk/en/Rules-and-standards/Securities-and-Futures-Ordinance-Part-XV---Disclosure-of-Interests/DI-Notices, https://www2.hkexnews.hk/Shareholding-Disclosures/Disclosure-of-Interests?sc_lang=en, https://econpapers.repec.org/paper/hkmwpaper/222008.htm, https://www.sciencedirect.com/science/article/abs/pii/S1042443110000338, https://www.sciencedirect.com/science/article/abs/pii/S0927538X10000600, https://ideas.repec.org/a/taf/applec/v46y2014i12p1335-1349.html, https://www.tandfonline.com/doi/abs/10.1207/S15427579JPFM0403_5, https://scholars.hkbu.edu.hk/en/publications/intraday-price-reversals-for-index-futures-in-the-us-and-hong-kon, https://www.hkex.com.hk/Services/Trading/Securities/Overview/Trading-Mechanism?sc_lang=en, and https://www.hkex.com.hk/Services/Rules-and-Forms-and-Fees/Fees/Securities-%28Hong-Kong%29/Trading/Transaction?sc_lang=en. `future_research_live_enablement_policy` keeps these and any newly discovered non-scaffolded ideas explicitly non-selectable until each new idea receives a new snapshot profile name, a new contract version, candidate-specific source-audit fields, point-in-time factor/classification, consensus-estimate revision, free-float market-cap, Stock Connect eligibility-change, designated short-selling, short-turnover, disclosed-interest / director-dealing notice, dually traded mapping / reversal cost, liquidity, and capacity history, analyst coverage/vendor, HSICS, official eligible-security methodology, HKEX regulated-short-selling controls, or SFC/HKEX DI-notice filing-lag / blackout / moratorium context, same-universe ablation against existing quality/yield, momentum, and special-situation profiles, walk-forward evidence versus `02800` and the candidate benchmark, drawdown/turnover/capacity controls, artifact provenance, dry-run order-preview evidence, bilingual notifications, rollout controls, and operator approval. This avoids silently turning a research idea into a live profile by mutating an existing contract in place.

These backlog entries must not be added to an existing contract in-place. If promoted, each needs a new profile name, new contract version, production source audit policy, artifact contract, walk-forward evidence, dry-run evidence, notification audit evidence, and operator approval.

## 1. `hk_low_vol_dividend_quality`

Recommended first snapshot-backed build after `hk_blue_chip_leader_rotation`. A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/low_vol_dividend_quality_strategy.py`, with artifact names defined in `src/hk_equity_snapshot_pipelines/contracts.py`. It remains non-production and not live-enabled.

### Required future columns

These columns should be added in a new contract version only after a reliable fundamentals and corporate-action source is selected:

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `market_cap_hkd`, `lot_size`;
- `dividend_yield_net`, `dividend_yield_trailing_12m`, `dividend_stability_3y`;
- `earnings_positive`, `pe_ratio`, `payout_ratio`, `free_cash_flow_yield` when available;
- `realized_vol_126`, `realized_vol_252`, `beta_252`, `maxdd_252`;
- `mom_6m`, `mom_12_1`, `sma200_gap` as trend/risk filters;
- `suspension_days_63`, `corporate_action_flag`, `eligible`.

### Ranking sketch

1. Filter by liquidity, market cap, positive earnings, non-extreme PE, non-suspended status, and dividend sanity checks.
2. Score high but sustainable dividend yield, low realized volatility / beta, and quality fields.
3. Apply sector caps because banks, telecom, utilities, and property can dominate high-dividend screens.
4. Rebalance monthly or quarterly only; use hold buffers to limit turnover.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/low_vol_dividend_quality.py` and `scripts/build_low_vol_dividend_sample.py` now provide a local factor-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/low_vol_dividend_quality/factor_snapshot.sample.csv`. This validates contract plumbing only; it is not a production fundamentals data source.

### Promotion boundary

Do not live-enable until:

- production snapshot source is audited;
- dividend and corporate-action adjustments match broker cash/dividend treatment;
- walk-forward backtest includes realistic HK fees, lot-size rounding, suspension handling, and sector caps;
- platform dry-run proves artifact loading, order preview, notifications, and rollback.

## 2. `hk_liquid_momentum_quality`

This is the explicit HK analogue of a US-style snapshot momentum stock-selection strategy. A tested scaffold exists in `src/hk_equity_snapshot_pipelines/liquid_momentum_quality_strategy.py`.

### Required columns

It intentionally reuses the price-feature style contract already available to `hk_blue_chip_leader_rotation`:

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `history_days`;
- `mom_3m`, `mom_6m`, `mom_12_1`, `rel_mom_6m_vs_benchmark`;
- `high_252_gap`, `sma200_gap`, `vol_63`, `maxdd_126`;
- optional `high_63_gap`, `market_cap_hkd`, `lot_size`, `suspension_days_63`, `corporate_action_flag`.

`high_63_gap` and `high_252_gap` are the repository's price-to-recent-high equivalents for 3-month and 12-month CTH-style momentum. `high_63_gap` is optional for backward compatibility, but the local CSV builder now emits it so future production snapshots can validate the short/long CTH combination explicitly.

### Ranking sketch

1. Filter to liquid names with enough history, positive 6-month and 12-1 momentum, positive 200-day trend, no recent suspension, and acceptable volatility/drawdown.
2. Score risk-adjusted 6-month and 12-1 momentum, benchmark-relative momentum, combined 63-day / 252-day high proximity, and trend strength.
3. Penalize high short-term volatility and drawdown.
4. Apply sector caps and hold buffers so a single hot sector does not dominate.

### Promotion boundary

Do not live-enable until:

- a production feature snapshot source handles total-return adjustments, corporate actions, suspensions, and stale prices;
- walk-forward backtests include positive annual return, max drawdown under 30%, profile-compliant annualized turnover, stamp duty, fees, lot-size rounding, liquidity caps, suspensions, and slippage;
- paper-trading confirms turnover and order preview quality on IBKR and LongBridge.

### Current research harness

`scripts/research_hk_liquid_momentum_quality_backtest.py` provides a local CSV backtest harness for the scaffold. It is useful for testing the end-to-end snapshot/rebalance/metric flow, but it deliberately emits `research_status=sample_harness_only_not_production_backtest` because the bundled sample data is not a production HK historical dataset.

## 3. `hk_residual_momentum_quality`

This is the more explicit US-style cross-sectional momentum-factor scaffold. It is separate from `hk_liquid_momentum_quality`: the liquid variant can be derived from price features, while this profile expects an upstream factor engine to neutralize broad market/industry effects and provide residual momentum fields. A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/residual_momentum_quality_strategy.py`. Live-enable now also requires HSI close-to-high descriptor and MSCI-style 6/12-month one-month-skip risk-adjusted momentum reconciliation, model-fit-window audit, sector neutralization, turnover buffers, and momentum-crash controls.

### Required columns

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `market_cap_hkd`, `history_days`;
- raw momentum: `mom_3m`, `mom_6m`, `mom_12_1`;
- neutralized momentum: `residual_mom_12_1`, `industry_relative_mom_6m`, `rel_mom_6m_vs_benchmark`;
- trend / price-to-high: `high_252_gap`, `sma200_gap`, optional `high_63_gap`;
- risk: `realized_vol_126`, `beta_252`, `maxdd_252`;
- `suspension_days_63`;
- optional `eligible`, `lot_size`, `southbound_eligible`, `corporate_action_flag`.

### Ranking sketch

1. Filter to liquid, Southbound-eligible names with positive raw momentum, positive residual momentum, positive industry-relative and benchmark-relative momentum, acceptable beta/volatility/drawdown, and no recent suspension.
2. Score raw 12-1/6M/3M momentum, residual / industry-neutral momentum, 52-week-high proximity, 200-day trend, and risk controls.
3. Apply sector caps and hold buffers to reduce crowded industry bets and turnover.
4. Allocate uninvested weight to `02800` as a safe-haven placeholder until production risk controls are finalized.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/residual_momentum_quality.py` and `scripts/build_residual_momentum_sample.py` provide a local factor-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/residual_momentum_quality/factor_snapshot.sample.csv`. This validates contract plumbing only; it is not a production residual-momentum data source.

### Promotion boundary

Do not live-enable until:

- residual momentum and industry-relative momentum are reproducible from survivorship-safe adjusted history;
- sector/industry neutralization, beta estimation, and benchmark-relative returns are audited against a fixed point-in-time universe;
- walk-forward tests include positive annual return, positive excess return versus `02800`, max drawdown under 30%, annualized turnover below 120%, realistic HK fees, stamp duty or exemption, slippage, lot-size rounding, liquidity caps, survivorship/look-ahead controls, and suspension handling;
- platform dry-run confirms artifact loading, order preview, notifications, and rollback on both IBKR and LongBridge.

## 4. `hk_composite_factor_quality_value_momentum`

This is the broader HK single-name multi-factor scaffold. It converts the external evidence for quality, value, low-volatility, and momentum into one factor-snapshot contract instead of relying on a pure price-only momentum signal. A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/composite_factor_quality_value_momentum_strategy.py`. It remains non-production and not live-enabled.

### Required columns

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `market_cap_hkd`;
- quality: `roe_ttm`, `earnings_variability_3y`, `debt_to_equity`;
- value: `book_to_price`, `earnings_yield`, `free_cash_flow_yield`;
- momentum/trend: `mom_12m_to_high`, `sma200_gap`;
- risk: `realized_vol_252`, `beta_252`, `maxdd_252`;
- `suspension_days_63`;
- optional `eligible`, `lot_size`, `dividend_yield_net`, `southbound_eligible`, `corporate_action_flag`.

### Ranking sketch

1. Filter to liquid, Southbound-eligible names with positive profitability, positive valuation-yield fields, acceptable trend, and no recent suspension.
2. Score quality, value, momentum-to-high/trend, and low-volatility sleeves separately, then combine them into a composite rank.
3. Apply sector caps and hold buffers to reduce concentration and turnover.
4. Allocate uninvested weight to `02800` as a safe-haven placeholder until production risk controls are finalized.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/composite_factor_quality_value_momentum.py` and `scripts/build_composite_factor_sample.py` provide a local factor-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/composite_factor_quality_value_momentum/factor_snapshot.sample.csv`. This validates contract plumbing only; it is not a production factor data source.

### Promotion boundary

Do not live-enable until:

- production quality/value/momentum/low-vol factor sources are audited and survivorship-safe;
- walk-forward tests include positive annual return, positive excess return versus an aligned benchmark, max drawdown under 30%, annualized turnover below 120%, realistic HK fees, stamp duty or exemption, slippage, lot-size rounding, liquidity caps, survivorship/look-ahead controls, and suspension handling;
- sector-cap, hold-buffer, and safe-haven behavior are reviewed across bull, bear, and sideways regimes;
- platform dry-run confirms artifact loading, order preview, notifications, and rollback on both IBKR and LongBridge.

## 5. `hk_shareholder_yield_quality`

This is a low-turnover capital-return quality scaffold. It combines cash dividends, actual buybacks, and share-count change with FCF, ROE, leverage, trend, and risk controls. It is snapshot-backed because the required buyback and share-count fields must come from audited disclosures rather than raw price history.

### Required columns

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `market_cap_hkd`;
- capital return: `dividend_yield_net`, `buyback_yield_12m`, `net_payout_yield`;
- quality: `free_cash_flow_yield`, `roe_ttm`, `debt_to_equity`;
- risk/trend: `realized_vol_252`, `maxdd_252`, `sma200_gap`;
- `suspension_days_63`;
- optional `eligible`, `lot_size`, `southbound_eligible`, `corporate_action_flag`, `share_count_change_12m`, `payout_ratio`, `earnings_yield`, `treasury_share_ratio`, `buyback_days_63`.

### Ranking sketch

1. Filter to liquid, Southbound-eligible names with positive net payout yield, non-negative dividend/buyback yield, positive FCF yield, positive ROE, acceptable leverage, limited share-count growth, acceptable trend, and no recent suspension.
2. Score net payout yield, buyback yield, dividend yield, dilution penalty, FCF yield, ROE, leverage, low volatility / drawdown, and trend.
3. Apply sector caps and hold buffers because financials, telecom, and utilities can dominate capital-return screens.
4. Allocate uninvested weight to `02800` as a safe-haven placeholder until production risk controls are finalized.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/shareholder_yield_quality.py` and `scripts/build_shareholder_yield_sample.py` provide a local factor-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/shareholder_yield_quality/factor_snapshot.sample.csv`. This validates contract plumbing only; it is not a production HKEX disclosure collector.

### Promotion boundary

Do not live-enable until:

- production dividend, buyback, treasury-share, share-count, FCF, ROE, and debt fields are audited and survivorship-safe;
- buyback yield is reconciled against actual share-count reduction, dilution, treasury-share resale, and corporate actions;
- walk-forward tests include positive annual return, positive excess return versus `02800`, max drawdown under 30%, annualized turnover below 100%, realistic HK fees, stamp duty or exemption, slippage, lot-size rounding, liquidity caps, survivorship/look-ahead controls, and suspension handling;
- platform dry-run confirms artifact loading, order preview, notifications, and rollback on both IBKR and LongBridge.

## 6. `hk_free_cash_flow_quality`

A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/free_cash_flow_quality_strategy.py`, with artifact names defined in `src/hk_equity_snapshot_pipelines/contracts.py`. It remains non-production and not live-enabled because it needs audited fundamentals, reporting-date availability, survivorship-safe history, FCF formula lineage, EV input lineage, restatement/as-of handling, sector normalization, and negative-FCF / financial-real-estate exception handling.

### Required columns

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, `market_cap_hkd`;
- `free_cash_flow_hkd`, `enterprise_value_hkd`, `free_cash_flow_yield`, plus production lineage for the FCF formula and EV market-cap/debt/cash/FX inputs;
- `roe_ttm`, `revenue_growth_ttm`;
- `realized_vol_252`, `maxdd_252`, `sma200_gap`;
- `suspension_days_63`;
- optional `eligible`, `lot_size`, `southbound_eligible`, `corporate_action_flag`, `earnings_yield`, `debt_to_equity`, `fcf_yield_percentile_3y`.

### Ranking sketch

1. Filter to liquid, Southbound-eligible names with positive free cash flow, positive enterprise value, positive ROE, acceptable revenue growth, positive FCF yield, acceptable trend, and no recent suspension.
2. Score FCF yield and optional FCF-yield percentile, profitability/growth, low realized volatility / drawdown, and trend strength.
3. Apply sector caps and hold buffers so energy, telecom, financial, or real-estate names do not dominate the portfolio.
4. Allocate uninvested weight to `02800` as a safe-haven placeholder until production risk controls are finalized.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/free_cash_flow_quality.py` and `scripts/build_free_cash_flow_sample.py` provide a local factor-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/free_cash_flow_quality/factor_snapshot.sample.csv`. This validates contract plumbing only; it is not a production fundamentals data source.

### Promotion boundary

Do not live-enable until:

- production FCF, EV, ROE, revenue, FCF formula lineage, EV input lineage, and reporting-date availability are audited and survivorship-safe;
- negative-FCF, financial-sector and real-estate EV/FCF exceptions, restatements, corporate actions, stale fundamentals, as-of snapshots, and sector normalization/concentration are handled explicitly;
- walk-forward tests include positive annual return, positive excess return versus an aligned benchmark, max drawdown under 30%, annualized turnover below 100%, realistic HK fees, stamp duty or exemption, slippage, lot-size rounding, liquidity caps, survivorship/look-ahead controls, and suspension handling;
- platform dry-run confirms artifact loading, order preview, notifications, and rollback on both IBKR and LongBridge.

## 7. `hk_southbound_flow_momentum`

A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/southbound_flow_momentum_strategy.py`, with artifact names defined in `src/hk_equity_snapshot_pipelines/contracts.py`. It remains non-production and not live-enabled because the Stock Connect data collector, point-in-time eligible-security history, raw HKEX/CCASS reconciliation, and data-quality controls are not implemented here.

### Required columns

- `symbol`, `sector`, `close_hkd`, `adv20_hkd`, optional `market_cap_hkd`, `lot_size`;
- `southbound_eligible`;
- `southbound_net_buy_hkd_5d`, `southbound_net_buy_hkd_20d`, `southbound_net_buy_hkd_60d`;
- `southbound_turnover_share_20d`;
- `southbound_holding_pct`, `southbound_holding_pct_change_20d`, `southbound_holding_pct_change_60d`;
- `flow_zscore_20d`, `flow_persistence_score`, `holiday_adjusted_flow_flag`;
- `mom_6m`, `sma200_gap`, `suspension_days_63`, optional `corporate_action_flag`.

### Ranking sketch

Use flow persistence as an overlay on liquid stocks with positive trend. Avoid daily trading; weekly or monthly cadence is safer because Southbound flow can be noisy around holidays, policy news, and index events.

Current scaffold behavior:

1. Filter to point-in-time eligible Stock Connect names with positive 20-day net buy, positive 20-day holding change, positive trend, no recent suspension, and no corporate-action block flag.
2. Score 20/60-day net-buy strength, holding-percentage change, 20-day flow z-score, flow persistence, and 6-month momentum.
3. Apply sector caps and hold buffers, then allocate any uninvested weight to `02800` as safe-haven placeholder.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/southbound_flow_momentum.py` and `scripts/build_southbound_flow_sample.py` provide a local flow-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/southbound_flow_momentum/flow_snapshot.sample.csv`. This validates contract plumbing only; it is not a production Stock Connect feed.

### Promotion boundary

Do not live-enable until:

- production Stock Connect flow source is audited against HKEX historical daily turnover, top-10 active-stock turnover, CCASS Southbound shareholding, eligible-security lists, calendars, holidays, stale rows, corporate actions, data-dissemination changes, and ticker eligibility changes;
- flow z-score and persistence calculations are reproducible from raw data, not manually supplied sample columns;
- walk-forward tests include positive annual return, max drawdown under 30%, profile-compliant annualized turnover, fees, stamp duty, lot-size rounding, missing flow days, and holiday-adjusted flow windows;
- platform dry-run confirms artifact loading, order preview, notifications, and rollback on both IBKR and LongBridge.

## 8. `hk_ah_premium_relative_value`

A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/ah_premium_relative_value_strategy.py`, with artifact names defined in `src/hk_equity_snapshot_pipelines/contracts.py`. It remains non-production and not live-enabled because it needs a reliable AH pair data source, FX normalization, Stock Connect eligibility checks, AH price-ratio formula lineage, share-class-switch threshold validation, A-share access / shorting / settlement constraint review, and survivorship-safe historical samples.

### Required columns

- `symbol`, `a_symbol`, `sector`;
- `h_close_hkd`, `a_close_cny`, `fx_cnyhkd`;
- `h_adv20_hkd`, `h_market_cap_hkd`, optional `lot_size`;
- `connect_eligible_h`, `connect_eligible_a`;
- `ah_premium_pct`, `ah_premium_percentile_3y`, optional `ah_premium_change_20d`, plus production lineage for A-share price, H-share price, FX, and adjusted market-cap inputs;
- `h_mom_6m`, `h_sma200_gap`, `h_vol_63`;
- `suspension_days_63`, optional `southbound_holding_pct_change_20d`, `corporate_action_flag`, `eligible`.

### Ranking sketch

The scaffold is a long-only H-share valuation overlay, not an A/H arbitrage engine:

1. Filter to liquid, point-in-time Stock Connect eligible AH pairs where A shares trade at a meaningful premium to H shares.
2. Require positive H-share 6-month momentum and 200-day trend so the strategy does not buy cheap but falling H shares.
3. Score A/H premium level, premium percentile, recent premium narrowing, H-share momentum/trend, Southbound support, liquidity, and extreme-premium false-reversal controls.
4. Apply sector caps and put uninvested weight into `02800`.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/ah_premium_relative_value.py` and `scripts/build_ah_premium_sample.py` provide a local valuation-snapshot artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/ah_premium_relative_value/valuation_snapshot.sample.csv`. This validates contract plumbing only; it is not a production AH premium feed.

### Promotion boundary

Do not live-enable until:

- AH pair mapping, index-constituent history, AH price-ratio formula, exchange holidays, A/H closing-time mismatch, FX source, and Stock Connect eligibility are audited;
- AH premium history is survivorship-safe and adjusted for share class / corporate actions;
- walk-forward tests include HK fees, lot-size rounding, liquidity caps, and realistic delayed H-share execution;
- the strategy remains long-only unless A-share access, borrow, shorting, settlement, and FX constraints are explicitly approved.

## 9. `hk_index_rebalance_event`

A tested scaffold now exists in `src/hk_equity_snapshot_pipelines/index_rebalance_event_strategy.py`, with artifact names defined in `src/hk_equity_snapshot_pipelines/contracts.py`. It remains non-production and not live-enabled because event labels, announcement timestamps, effective dates, official schedule / review-result provenance, fast-entry / suspension / buffer-rule exceptions, CAS / market-on-close execution controls, and slippage estimates must be audited from official index-review records.

Primary live-enable source gates should use official Hang Seng Indexes / HKEX records:

- HSI Index Methodology Guide and Index Operation Guide for quarterly cutoff, review timing, fast-entry, suspension, rebalancing, and index schedule rules;
- HSI regular rebalancing schedule (`is_update.xlsx`) plus next-review notices and review-result press releases as immutable event-source records;
- HKEX Closing Auction Session and trading-mechanism references for market-on-close order type, random-close, price-limit, and execution-window constraints.

### Required columns

- `symbol`, `index_family`, `review_cycle`, `data_cutoff_date`, `announcement_date`, `effective_date`;
- `event_side`;
- `predicted_add_probability`, `predicted_remove_probability`;
- `official_add_flag`, `official_remove_flag` after announcements;
- `days_to_effective`, `event_liquidity_score`, `estimated_slippage_bps`;
- `close_hkd`, `adv20_hkd`, `market_cap_hkd`, `post_announcement_momentum_5d`;
- `suspension_days_63`, optional `sector`, `lot_size`, `index_weight_estimate`, `crowding_score`, `corporate_action_flag`, `eligible`.

### Ranking sketch

Use this as an event study first. The scaffold is intentionally long-only and small-exposure:

1. Filter to predicted or official additions; exclude removals and stale event windows.
2. Require high liquidity, acceptable estimated slippage, no recent suspension, and positive distance to the effective date.
3. Score official-add confirmation, predicted add probability, liquidity, estimated index weight, post-announcement momentum, slippage, and crowding.
4. Apply conservative sector caps and put uninvested weight into `02800`.

### Current artifact harness

`src/hk_equity_snapshot_pipelines/index_rebalance_event.py` and `scripts/build_index_rebalance_event_sample.py` provide a local event-calendar artifact builder. It writes the standard snapshot, manifest, ranking, and release-summary files from `examples/index_rebalance_event/event_snapshot.sample.csv`. This validates contract plumbing only; it is not a production index-event database.

### Promotion boundary

Do not live-enable until:

- index review calendars, announcement timestamps, effective dates, and add/remove identifiers are audited against official records;
- HSI rebalancing schedule, next-review notices, and review-result press releases are ingested with stable source URIs and immutable artifact hashes;
- event samples are built without look-ahead bias and include delistings, suspended names, and failed predictions;
- walk-forward event-window tests include capacity, crowding, realistic slippage, lot-size rounding, fast-entry / suspension / buffer-rule exceptions, and effective-date timing;
- HKEX CAS / market-on-close order handling proves at-auction / at-auction-limit order constraints, random-close behavior, price-limit checks, and passive-flow crowding controls;
- platform dry-run proves order preview, cancellation/rollback, and operator notifications across at least one review cycle.

## 10. Deferred true A/H arbitrage

### Required future columns

- `h_symbol`, `a_symbol`, `ah_premium_pct`, `ah_premium_percentile_3y`;
- `connect_eligible_h`, `connect_eligible_a`;
- `h_liquidity_score`, `a_liquidity_score`, `fx_rate_source`;
- optional Southbound holding and flow fields.

### Ranking sketch

The scaffold above deliberately starts as a long-only H-share valuation overlay. True long/short arbitrage should be deferred until borrow, A-share access, FX, settlement, and short-sale constraints are confirmed.

## Contract impact

`hk_low_vol_dividend_quality`, `hk_liquid_momentum_quality`, `hk_composite_factor_quality_value_momentum`, `hk_quality_growth_low_volatility`, `hk_factor_mix_qvlm_risk_parity`, `hk_residual_momentum_quality`, `hk_shareholder_yield_quality`, `hk_free_cash_flow_quality`, `hk_southbound_flow_momentum`, `hk_ah_premium_relative_value`, and `hk_index_rebalance_event` now use their own contract versions and artifact names; `hk_blue_chip_leader_rotation` keeps its existing artifact filenames and required columns. Future candidates should use new profile names and new contract versions rather than overloading existing scaffolds.
