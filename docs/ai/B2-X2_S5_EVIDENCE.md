# S5 Evidence 工具（Legacy 3.5.3）

`scripts/validate/s5_evidence.py` 给旧 candidate 准备 A/B 证据包。机器只产证据，**不得**代写 HUMAN_ACCEPTED。

这不是当前 Product Gate，也不启动 Combat Polish。

```text
python scripts/validate/s5_evidence.py aspects
python tests/s5_evidence/run_s5_selfchecks.py
```

| 文件 | 角色 |
|---|---|
| `scripts/validate/s5_aspects.json` | aspect 目录 |
| `scripts/validate/s5_evidence.py` | driver |
| `docs/ai/audits/B2-X2_S5_EVIDENCE_SELFTEST_EVIDENCE.json` | 当时 23/23 自测证据 |

只读复用 harness 的 catalog / telemetry schema，不要为 3.5.3 再扩一套总线。
