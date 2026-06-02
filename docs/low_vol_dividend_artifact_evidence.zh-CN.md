# 港股低波股息质量 Artifact Evidence 草稿

[English version](./low_vol_dividend_artifact_evidence.md)

该工具把已通过本地校验的 `hk_low_vol_dividend_quality` artifact 目录转换为 `artifact_pack_validation` evidence 草稿。
它连接 `hkeq-validate-snapshot-artifact-pack` 和完整 live-enable evidence validator。

该命令不会发布 artifact、不会部署 Cloud Run、不会批准 live trading，也不会把 sample artifact 标记为 production evidence。

## 使用方式

```bash
python scripts/draft_low_vol_dividend_artifact_evidence.py \
  --artifact-dir data/output/low_vol_dividend_quality \
  --artifact-release-id hk-low-vol-dividend-quality-20260603-001 \
  --published-snapshot-uri gs://.../hk_low_vol_dividend_quality_factor_snapshot_latest.csv \
  --published-manifest-uri gs://.../hk_low_vol_dividend_quality_factor_snapshot_latest.csv.manifest.json \
  --published-ranking-uri gs://.../hk_low_vol_dividend_quality_ranking_latest.csv \
  --published-release-summary-uri gs://.../release_status_summary.json \
  --evidence-uri gs://.../artifact_pack_validation.json \
  --evidence-generated-at 2026-06-03 \
  --confirm-immutable-release \
  --confirm-published-artifacts-not-sample \
  --confirm-manifest-provenance \
  --confirm-release-summary-ready
```

## 通过行为

只有满足以下条件，artifact section 才会标记为 `passed`：

- 本地 artifact-pack validation 通过；
- 提供 immutable release id，且不能是 `latest`、`sample`、`dev` 或 `test`；
- 提供稳定的 snapshot、manifest、ranking、release-summary 和 evidence URI；
- operator 显式确认 immutable release identity、非 sample 发布、manifest sha256/row-count provenance 和 release-summary readiness。

即使该 section 通过，完整 live-enable evidence pack 仍需要 production source、walk-forward backtest、platform dry-run、broker permission、rebalance-window、rollout、risk approval 和 strategy-policy evidence 全部通过。
