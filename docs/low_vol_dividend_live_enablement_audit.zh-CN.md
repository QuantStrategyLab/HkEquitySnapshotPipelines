# 港股低波股息质量 Live-Enable 审计

[English version](./low_vol_dividend_live_enablement_audit.md)

该工具是 `hk_low_vol_dividend_quality` 进入真正 live-enable 前的最终机器校验入口。
它合并检查三个独立 gate：

1. production snapshot artifact pack 校验；
2. LongBridge live-enable evidence 校验；
3. IBKR live-enable evidence 校验。

它不会生成 evidence、不会部署 Cloud Run、不会发布 artifact、不会移除 dry-run 控制，也不会下券商订单。
只要任一 gate 缺失或失败，命令就会返回非 0 退出码。

## 使用方式

```bash
python scripts/audit_low_vol_dividend_live_enablement.py \
  --artifact-dir gs-mounted-or-local-production-artifacts \
  --longbridge-evidence-file evidence/longbridge_live_enablement_evidence.json \
  --ibkr-evidence-file evidence/ibkr_live_enablement_evidence.json \
  --validation-as-of 2026-06-03 \
  --json
```

安装包后也可以使用 entry point：

```bash
hkeq-audit-low-vol-dividend-live-enable \
  --artifact-dir gs-mounted-or-local-production-artifacts \
  --longbridge-evidence-file evidence/longbridge_live_enablement_evidence.json \
  --ibkr-evidence-file evidence/ibkr_live_enablement_evidence.json \
  --json
```

## 通过条件

只有同时满足以下条件才会通过：

- artifact pack 通过 `hkeq-validate-snapshot-artifact-pack`；
- artifact snapshot 至少包含 20 行，sample/smoke 小样本不能作为 production-sized release；
- 两个平台 evidence 文件都通过 `hkeq-validate-live-enable-evidence`；
- evidence 新鲜、稳定、无 secret-like URI，并且字段完整；
- 两个平台 dry-run order preview、中英文通知日志、券商权限、rollout 控制和 operator approval 都已补齐。

sample artifact、pending template、缺失平台 dry-run evidence 或 stale evidence 都会保持 `live_enablement_allowed=false`。
