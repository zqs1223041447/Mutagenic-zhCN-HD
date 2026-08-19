# B2 协调状态视图

> **Batch**：`B2`
> **状态**：`WAVE_A_READY`
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **Frozen base ref**：`batch/b2-anchor`
> **任务合同**：`docs/ai/batches/B2_KINETIC_COMBAT_VALIDATION_AND_IMPACT.md`
> **产品状态权威**：仍为 `status.json` + evidence；本文件只负责 B2 调度。

## B1 继承事实

- B1-X0～X5 已全部集成；禁止重做 B1 workstream。
- B1 gameplay/foundation 单 MOD 的 S0/S1/S4 已有本地证据，但尚无全部 B1 MOD 同一 aggregate Candidate 的回归证据。
- S2 core smoke 尚未运行。
- Combat S5 尚未 HUMAN ACCEPTED。
- baseline promotion 未执行。

## Wave A — 立即并发

| Task | 状态 | 目标 |
|---|---|---|
| B2-X0 | READY | B1 aggregate Candidate + X5 harness 真实 S2 回归 |
| B2-X1 | READY | Combat Event Spine v1：direct hit / DoT / crit / kill 单一事件语义 |
| B2-X2 | READY | Combat S5 A/B evidence automation；机器准备证据，不冒充人工验收 |
| B2-X3 | READY | batchctl / scanner / harness / semantic contracts 的无人值守控制平面强化 |

主控应在资源允许时同时拉起 X0～X3，不得无理由串行。

## Gate A

Wave B 之前至少要求：

- X0 aggregate Candidate 未发现阻断性结构/boot 回归；
- X1 Event Spine semantic contract PASS；
- 将 X1 必需事件层与必要回归修复集成后冻结新的 `batch/b2-waveb-anchor`。

## Wave B — Gate A 后并发

| Task | 状态 | 依赖 | 目标 |
|---|---|---|---|
| B2-X4 | WAITING_GATE_A | X1 | Kill Feel v1 |
| B2-X5 | WAITING_GATE_A | X1 | Camera Impulse v1；heavy/crit/kill，普通 hit/DoT 默认不震 |
| B2-X6 | WAITING_GATE_A | X1 + B1 X4 | Combat Audio Layers v1；hit/crit/kill/cluster 分层 |

X4/X5/X6 应在 `batch/b2-waveb-anchor` 上并发，不从旧 `batch/b2-anchor` 私自继续。

## B2-I1

Wave A / Wave B 完成后中央集成：

`collect → scope/security/path review → preimage/semantic conflict → integration → final aggregate candidate → S0/S1/S2/S4 → machine S5 evidence → HUMAN S5 gate → B3 planning`

## B2 不做的事

- 不自动 promotion baseline；
- 不修改 `00_original/03_raw/04_recovered`；
- 不在 B2 扩大战斗密度数值；Build Density 只建立性能/回归基线；
- 不用 every-hit camera shake / hit-stop / audio spam 伪造手感。

## 主控最简启动指令

```text
启动 B2：解析 batch/b2-anchor，使用 batchctl 为 B2-X0～X3 建立独立 branch/worktree，并行拉起四个 Worker；持续监控、失败重试、完成即补位。Gate A 通过后由主控集成必要前置并冻结 batch/b2-waveb-anchor，再并行拉起 B2-X4～X6。最终执行 B2-I1 聚合回归、push、更新 PR/handoff；除真正人工 Gate 外不要等待用户。
```
