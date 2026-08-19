# B1 协调状态视图

> **状态**：`COMPLETED / INTEGRATED`
> **完成日期**：2026-08-20
> **用途**：B1 归档式协调视图；产品/验证状态仍以 `status.json` 和对应 evidence 为权威。

## B1-I1 最终结果

- B1-X0～X5 全部完成、push 并中央集成至 `agent/kinetic-arcane-remaster-foundation`。
- B1 frozen base：`batch/b1-anchor` @ `c864480d8908630d602c17f4949b96b65d19b275`。
- 集成任务提交顺序：`182e79f`(X0) → `0f69ba6`(X1) → `44e6e41`(X2) → `0abfc8d`(X3) → `009d046`(X4) → `6cea0e6`(X5)。
- B1-I1 完成提交：`ad6e85f26be2e25ce2749a36412b3ee0d185231b`。
- merge-tree 预检无文件冲突。
- 集成后 absolute-path scan：0 FAIL；仅允许的 provenance/local-config 类提示。
- secret scan：无真实 secret 泄漏；命中均为已脱敏测试夹具。

## Workstream 最终状态

| Task | 最终状态 | 主要交付 |
|---|---|---|
| B1-X0 | DONE + INTEGRATED | `scripts/ai/batchctl.py`、abs-path/secret scan、repo util、56 项单测、23 处宿主硬编码迁移 |
| B1-X1 | DONE + INTEGRATED | `mods/k1-player-response`；静止 Dash 最近方向 fallback |
| B1-X2 | DONE + INTEGRATED | `mods/k2-hit-reaction`；health-loss 节流视觉反馈 |
| B1-X3 | DONE + INTEGRATED | Combat Pipeline 审计、`feat-tce-context`、semantic contract |
| B1-X4 | DONE + INTEGRATED | `mods/k4-audio-foundation` v0.2；聚合、voice budget、生命周期回收、variation |
| B1-X5 | DONE + INTEGRATED | deterministic Combat Harness、8 scenarios、telemetry schema、15/15 selftest、游戏内接入 MOD |

## 已验证

- X1 / X2 / X4：本地 canonical build 的 S0 / S1 / S4 PASS，均为 `00_original` fresh embed，并由 GDRE 语义恢复确认。
- X5：15/15 自测 PASS。
- X0：单元测试、absolute-path scan、secret scan PASS。

## 明确未完成的 Gate

- **B1 aggregate candidate**：尚未把全部 B1 gameplay/foundation MOD 作为同一组合 Candidate 做聚合回归。
- **S2 core smoke**：尚未基于 X5 harness 完成真实运行态自动回归。
- **Combat S5**：尚未 human-accepted；需要同场景 A/B 与最终人工体验判断。
- **baseline promotion**：未执行，仍需用户显式批准。

这些未完成项转入 B2，不回退为 B1-Xn “待执行”。

## 重要资产与路径规则

- `03_raw/**`、`04_recovered/**` 已随 clone 提供，但仍为 byte-preserving 不可变 Recovered Provenance。
- `00_original/**` 不入 Git，只允许本地合法持有的原版资产参与 fresh embed。
- 所有 repo 内工程路径必须从当前 clone 的 repo root 推导；生产代码禁止宿主绝对路径硬编码。
- 多 Agent 仍必须一任务一 branch + 一独立 worktree。

## 后续入口

B1 已关闭，不应再启动任何 B1-X0～X5 重做任务。

后续统一读取：

- `docs/ai/batches/B2_KINETIC_COMBAT_VALIDATION_AND_IMPACT.md`
- `docs/ai/batches/B2_STATUS.md`

B2 将承接 aggregate candidate、S2 自动回归、Combat S5 证据自动化，以及事件驱动的 Kill Feel / Camera / Combat Audio。
