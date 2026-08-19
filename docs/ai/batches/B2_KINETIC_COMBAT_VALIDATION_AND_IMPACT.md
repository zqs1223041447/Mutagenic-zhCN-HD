# B2 — Kinetic Combat Validation & Impact

> **Batch ID**：`B2`
> **状态**：OPEN FOR CLAIM
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **目标**：把 B1 的分散能力变成同一可运行 Combat Vertical Slice，并在稳定事件语义上并发推进 Kill Feel / Camera / Combat Audio。

## 0. 执行原则

B2 使用两波并发：

```text
Wave A: X0 + X1 + X2 + X3 并发
                    |
                    +--> Gate A
                         |
                         v
Wave B: X4 + X5 + X6 并发
                    |
                    v
                 B2-I1
```

所有任务从 `batch/b2-anchor` 的同一 SHA 出发。不同 Worker 必须使用独立 branch + worktree。

Build Density 在 B2 **只做性能基线，不做密度数值扩大**。只有 B2 的 aggregate regression、事件层和 Impact 层稳定后，后续批次才能进入真实 density tuning。

---

# Wave A

## B2-X0 — Aggregate Candidate & Harness Regression

### Goal

把 B1 已集成的 gameplay/foundation MOD 组合成同一 aggregate Candidate，并首次把 X5 Combat Harness 用于真实运行态 S2 自动回归。

### Required

1. 解析当前集成线的 B1 modset，明确组合顺序与依赖；
2. canonical resolve/apply/compile/pack/fresh embed；
3. 生成唯一 Build ID、modset hash、candidate hash；
4. 跑 S0 / S1；
5. 用 X5 harness 驱动至少 8 个已定义 scenario；
6. 输出 S2 telemetry/report；
7. 覆盖至少：movement、dash、direct hit、rapid hit、DoT、kill、cluster、projectile density；
8. 验证 duplicate death=0、fatal=0、关键 trigger count 合理；
9. 记录 FPS/frame pacing/voice count/camera event count（能力允许时）；
10. 失败自动定位到具体 MOD 或 scenario。

### Acceptance

- B1 各 MOD 在同一 Candidate 中无结构/语义互相破坏；
- S0/S1 PASS；
- S2 从 NOT RUN 推进为有真实运行证据的 PASS 或明确 BLOCKED；
- 不修改 baseline。

---

## B2-X1 — Combat Event Spine v1

### Goal

把 B1 的 `feat-tce-context` 扩展成稳定的战斗事件语义层，为 Hit Reaction、Kill Feel、Camera、Audio 提供单一事件事实来源，避免每个系统自行猜 direct hit / DoT / crit / kill。

### Required semantics

至少研究并稳定：

- `direct_hit`
- `dot_tick`
- `crit`
- `kill`
- 可安全推导时的 `heavy` / impact tier

事件上下文至少评估：

- attacker / target identity 或安全引用
- skill/projectile context
- damage result
- crit flag
- did_kill
- target position
- event timestamp / sequence id

### Constraints

- 不改变伤害计算结果；
- 不改变 collision；
- death/kill 仍只结算一次；
- DoT 不得伪装成 direct hit；
- 事件层本身不做 Camera shake / Audio 播放 / 大型 FX；
- 优先扩展既有 TCE context，不复制第二套事件总线。

### Verification

增加 semantic contract，至少覆盖：

- direct hit once
- DoT tick 分类正确
- crit flag 正确
- kill once
- 高频 hit 无重复 kill/event explosion

完成后供 Wave B 三个 presentation task 共同依赖。

---

## B2-X2 — Combat S5 Evidence Automation

### Goal

把 Combat S5 从“人工临时看一眼”变成机器可重复准备证据、人工只做最终体验判定的 A/B 流程。

### Required

建立 repo-relative 的 capture/evidence 流程，尽量自动完成：

- baseline / candidate 同 scenario id
- 同 seed
- 同 spawn composition / positions
- 同 camera start
- BEFORE / AFTER 截图
- 能力允许时短视频/帧序列
- telemetry 同步
- Build ID / modset hash / candidate hash
- capture manifest
- 人工评价 checklist

至少为：

- Player Response
- Enemy Hit Reaction
- Kill Feel（Wave B 后）
- Camera
- Audio

预留统一 evidence 格式。

### Constraint

机器只负责准备 S5 evidence，不得把“捕获成功”写成 HUMAN ACCEPTED。

---

## B2-X3 — Unattended Batch / CI Hardening

### Goal

把 B1-X0 自动化真正跑成后续批次可无人值守依赖的控制平面。

### Required

从干净 clone/含空格路径等条件验证：

- `batchctl claim`
- `status`
- `handoff`
- `collect`
- `preflight`
- `cleanup` fail-closed

建立一个统一的 machine preflight/check 入口，组合：

- batchctl 单测
- abs-path scan
- secret scan
- combat harness selftests
- semantic combat pipeline contract
- 新增 event spine contract（X1 完成后在集成阶段接入）

不得让多个 Agent 共享主 working tree。

### Acceptance

后续主控可以用少量命令完成批次创建、并发 worktree 管理、收集与集成前审查；失败给出稳定退出码和机器可读报告。

---

# Gate A

Wave B 启动前至少满足：

1. B2-X0 的 B1 aggregate Candidate 没有发现阻止继续的结构/boot 回归；
2. B2-X1 Combat Event Spine 的语义 contract PASS；
3. X1 已集成到新的 `batch/b2-waveb-anchor`；
4. 若 X0 暴露真实回归，先修复回归再冻结 Wave B anchor。

X2/X3 不要求阻塞 Wave B，除非它们发现治理或工具级硬失败。

---

# Wave B

## B2-X4 — Kill Feel v1

### Depends on

`B2-X1 Combat Event Spine`

### Goal

基于稳定 `kill` event 建立第一版明确、低噪声的 Kill Feel，不改变伤害/掉落/死亡顺序。

### Required

- 审计现有 dissolve / death FX / drop order；
- 使用统一 kill event；
- 普通 kill 与 elite/boss 预留强度分层；
- 优先复用现有资产；
- 防止 cluster kill 形成不可读 FX 爆炸；
- 不依赖每 hit shake/hit-stop。

### Verification

至少覆盖 single kill、rapid multi-kill、5–20 cluster、elite、death once、drop order。

---

## B2-X5 — Camera Impulse v1

### Depends on

`B2-X1 Combat Event Spine`

### Goal

建立真正的 Camera impulse aggregator，并只绑定到高价值事件。

### Event policy

默认允许候选：

- heavy
- crit（轻量或条件化）
- kill / elite kill（受预算控制）

默认禁止：

- every ordinary hit
- every DoT tick

### Required

- amplitude budget
- short aggregation window
- decay
- maximum offset / safety cap
- cluster kill 合并
- event count telemetry

不得修改 Player/Mob 伤害逻辑。

---

## B2-X6 — Combat Audio Layers v1

### Depends on

`B2-X1 Combat Event Spine` + B1 `k4-audio-foundation`

### Goal

在现有 60ms 聚合、16 voice budget、pitch/volume variation 基础上建立事件分层的 combat audio。

### Required

至少建立/验证：

- light/direct hit
- crit/heavy
- kill
- cluster kill suppression/aggregation

优先复用仓库现有声音资产，不为本轮强行引入新的二进制资产。

必须验证：

- voice budget 不泄漏；
- `tree_exited` 回收稳定；
- 高频 hit 不形成音频机枪；
- DoT 不按 tick 产生 impact spam；
- kill 能从普通 hit 中被听觉区分。

---

# B2-I1 — Central Integration

全部 REQUIRED workstream 完成后，协调 AI 执行：

1. collect handoffs；
2. scope / immutable / secret / abs-path review；
3. base/final SHA 校验；
4. preimage drift；
5. semantic conflict graph；
6. 决定集成顺序；
7. 合并 X0–X6；
8. 生成最终 B2 aggregate Candidate；
9. aggregate S0 / S1 / S2 / S4；
10. 生成机器 S5 evidence；
11. 人工 S5 仍保持 HUMAN_REQUIRED；
12. 更新 B2_STATUS / PR；
13. 只有用户显式批准才允许 baseline promotion；
14. 根据结果规划 B3（预计才进入 Build Density / 更完整 Combat Polish）。

---

# Worker 最简认领

Wave A：

```text
认领 B2-Xn：读取 B2 任务合同和当前状态，按仓库规则全自动执行到最远可验证状态，commit、push、handoff；普通失败自行修复，不等待用户。
```

Wave B：由主控在 Gate A 通过并冻结 `batch/b2-waveb-anchor` 后自动拉起 X4/X5/X6。
