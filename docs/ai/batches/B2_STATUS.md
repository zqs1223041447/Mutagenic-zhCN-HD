# B2 协调状态视图

> **Batch**：`B2`
> **状态**：`WAVE_B_ACTIVE`（Gate A 已通过并冻结 `batch/b2-waveb-anchor`）
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **Wave A 集成 HEAD**：`ba4a0120`（X1→X2→X3→X0 依序合并完成）
> **Frozen base ref（Wave A）**：`batch/b2-anchor` = `2a40ec4d`
> **Frozen base ref（Wave B）**：`batch/b2-waveb-anchor`（本文件提交后更新为当前集成 HEAD）
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
| B2-X0 | ✅ COMPLETED → `agent/b2-x0` = `7009481c` | B1 aggregate Candidate + X5 harness 真实 S2 回归；S0 PASS / S1 PASS / S2 BLOCKED（launcher 键盘路由未产出 telemetry，已如实记录，非阻断） |
| B2-X1 | ✅ COMPLETED → `agent/b2-x1-combat-event-spine` = `ec5e23e` | Combat Event Spine v1：direct hit / DoT / crit / kill 单一事件语义；contract 44/44 PASS + resolve/apply dry-run PASS |
| B2-X2 | ✅ COMPLETED → `agent/b2-x2-s5-evidence` = `179e6ac` | Combat S5 A/B evidence automation；23/23 自测 PASS；机器准备证据，不冒充人工验收 |
| B2-X3 | ✅ COMPLETED → `agent/b2-x3-ci-hardening` = `602c595a` | batchctl / scanner / harness / semantic contracts 的无人值守控制平面强化；check_all 全组件 PASS（event_spine_contract 接入位已预留） |

Wave A 已完成并集成：`47bdc2d`(X1) → `e2f9cab`(X2) → `e7a3a72`(X3) → `ba4a0120`(X0)。集成后验证：abs-path scan production_hardcode=0、secret findings=0、X1 contract 44/44 PASS、check_all 组件 PASS。

## Gate A

Wave B 之前至少要求：

- X0 aggregate Candidate 未发现阻断性结构/boot 回归；✅ S0/S1 PASS（S2 BLOCKED 非阻断，保留人工核查项）
- X1 Event Spine semantic contract PASS；✅ 44/44 PASS
- 将 X1 必需事件层与必要回归修复集成后冻结新的 `batch/b2-waveb-anchor`；✅ 本文件提交后更新引用

**Gate A 判定：PASS（2026-08-20）**。冻结 `batch/b2-waveb-anchor` = 当前集成 HEAD。

## Wave B — Gate A 后并发

| Task | 状态 | 依赖 | 目标 |
|---|---|---|---|
| B2-X4 | ✅ CLAIMED → `agent/b2-x4-kill-feel` | X1 | Kill Feel v1 |
| B2-X5 | ✅ CLAIMED → `agent/b2-x5-camera-impulse` | X1 | Camera Impulse v1；heavy/crit/kill，普通 hit/DoT 默认不震 |
| B2-X6 | ✅ CLAIMED → `agent/b2-x6-combat-audio-layers` | X1 + B1 X4 | Combat Audio Layers v1；hit/crit/kill/cluster 分层 |

X4/X5/X6 已在 `batch/b2-waveb-anchor` 上并发。

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
