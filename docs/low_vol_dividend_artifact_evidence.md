# HK Low-Volatility Dividend Quality Artifact Evidence Draft

[中文版本](./low_vol_dividend_artifact_evidence.zh-CN.md)

This tool turns a validated `hk_low_vol_dividend_quality` artifact directory into an `artifact_pack_validation` evidence draft.
It is the bridge between `hkeq-validate-snapshot-artifact-pack` and the full live-enable evidence validator.

The command does not publish artifacts, deploy Cloud Run, approve live trading, or mark sample artifacts as production evidence.

## Usage

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

## Passing behavior

The artifact section is marked `passed` only when:

- local artifact-pack validation passes;
- an immutable release id is supplied and is not `latest`, `sample`, `dev`, or `test`;
- stable published snapshot, manifest, ranking, release-summary, and evidence URIs are supplied;
- the operator explicitly confirms immutable release identity, non-sample publication, manifest sha256/row-count provenance, and release-summary readiness.

Even if this section passes, the full live-enable evidence pack remains blocked until production source, walk-forward backtest, platform dry-run, broker permission, rebalance-window, rollout, risk approval, and strategy-policy evidence also pass.
