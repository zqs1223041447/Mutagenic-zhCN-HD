# B2 协调状态视图

> **Batch**：`B2`
> **状态**：`B2-I1_COMPLETE`（final aggregate Candidate 构建完成：S0/S1/S4 PASS，machine S5 evidence 已产出；S2 保持 BLOCKED 如实；HUMAN S5 gate 保持 HUMAN_REQUIRED）
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **B2 集成 HEAD**：`2917fff`（Wave A `ba4a0120` + X4/X5/X6 依序合并）
> **Frozen base ref（Wave A）**：`batch/b2-anchor` = `2a40ec4d`
> **Frozen base ref（Wave B）**：`batch/b2-waveb-anchor` = `ea7854f`
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
| B2-X4 | ✅ COMPLETED → `agent/b2-x4-kill-feel` = `8f4a65f` | X1 | Kill Feel v1；contract 80/80 PASS + apply dry-run PASS；分层 normal/elite/boss + cluster 预算抑制（GameState 400ms/3 cap），复用 shatter/poof 资产，零新总线/零伤害改动 |
| B2-X5 | ✅ COMPLETED → `agent/b2-x5-camera-impulse` = `54fa8d2` | X1 | Camera Impulse v1；contract 93/93 PASS；impulse 仅绑定 kill/elite_kill/heavy（普通 hit/DoT 默认不震），budget/window/decay/cap/cluster 合并/telemetry 齐备 |
| B2-X6 | ✅ COMPLETED → `agent/b2-x6-combat-audio-layers` = `d5d70ae` | X1 + B1 X4 | Combat Audio Layers v1；contract 120/120 + selftest 14/14 PASS；light/heavy/kill/cluster 分层经 k4 单漏斗（16 voice budget/tree_exited 保留），DoT 抑制，零新增二进制资产 |

Wave B 已完成并集成：`fe17456`(X4) → `03a2b20`(X5) → `2917fff`(X6)。集成后验证：三个 contract 全 PASS、abs-path production_hardcode=0、secret findings=0。

## B2-I1

Wave A / Wave B 完成后中央集成：

- ✅ collect handoffs（X0–X6 全部完成）
- ✅ scope / immutable / secret / abs-path review（abs-path 0 hardcode、secret 0 findings；00_original/03_raw/04_recovered 未触碰）
- ✅ base/final SHA 校验（全部 base=对应 anchor，final SHA 远端核验）
- ✅ preimage drift / semantic conflict graph（merge-tree 预检全部 conflict_blocks=0；X4/X5/X6 相互与 X1 锚点零重叠）
- ✅ 合并 X0–X6 → `2917fff`
- ✅ final aggregate Candidate（`mods/b2-i1-aggregate` 14-mod RESOLVED_MOD_CHAIN，resolve/apply 51 patches / compile 11 unique .gd / pack 3744 entries / normalize / fresh embed 全 PASS；candidate 103,341,700 bytes）
- ✅ aggregate S0/S1（roundtrip 11/11、delta 精确、exe_structure 3744/3744、normalize rejected=0；probe_boot PASS）
- ✅ aggregate S4（五个 semantic contract 全 PASS：event_spine 44/44、kill_feel 80/80、camera 93/93、combat_audio 120/120、pipeline 78/78）
- ⏳ aggregate S2（BLOCKED 如实记录：launcher window_found=true、telemetry_found=false，无 VM 环境限制同 B2-X0；不阻断交付，待 VM/人工核查）
- ✅ machine S5 evidence（s5_evidence selfcheck 23/23 PASS；5 aspect candidate-side package 已产出，NOT_RUN skeleton，machine_status=EVIDENCE_PREPARED，机器绝不写 HUMAN_ACCEPTED）
- ⏳ HUMAN S5 gate（保持 HUMAN_REQUIRED，人工/VM 验收）
- ⏳ 更新 PR（本文件提交后执行）
- ⏳ B3 planning（含 Build Density 基线与更完整 Combat Polish）

## B2 不做的事

- 不自动 promotion baseline；
- 不修改 `00_original/03_raw/04_recovered`；
- 不在 B2 扩大战斗密度数值；Build Density 只建立性能/回归基线；
- 不用 every-hit camera shake / hit-stop / audio spam 伪造手感。

## 主控最简启动指令

```text
启动 B2：解析 batch/b2-anchor，使用 batchctl 为 B2-X0～X3 建立独立 branch/worktree，并行拉起四个 Worker；持续监控、失败重试、完成即补位。Gate A 通过后由主控集成必要前置并冻结 batch/b2-waveb-anchor，再并行拉起 B2-X4～X6。最终执行 B2-I1 聚合回归、push、更新 PR/handoff；除真正人工 Gate 外不要等待用户。
```
