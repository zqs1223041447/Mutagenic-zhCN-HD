# batchctl（Legacy 批次 CLI）

`scripts/ai/batchctl.py` 是 B1 留下的 3.5.3 批次工具：claim / status / handoff / collect / preflight / cleanup。它读写旧 `status.json`。

**不要**用它认领 B1/B2/B3。现行调度是 `OPERATING_MODEL.md`（gork → AGY / opencode）。当前 Gate 是 P1-WAVE-A。

```text
python scripts/ai/batchctl.py status B1
python scripts/ai/batchctl.py preflight B1
```

失败即拒绝：生产代码里的宿主绝对路径、secret、触碰 `00_original`/`03_raw`/`04_recovered` 会 FAIL。`status.json` 损坏则命令拒绝执行。
