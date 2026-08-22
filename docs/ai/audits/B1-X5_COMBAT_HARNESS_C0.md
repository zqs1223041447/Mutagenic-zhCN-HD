# B1-X5 — Combat Test Harness C0 远端预审计

> **Task**：B1-X5
> **基线**：`batch/b1-anchor` → `c864480d8908630d602c17f4949b96b65d19b275`
> **TestLevel.gd SHA-256**：`0bc68d4ea29eb4a2340cb35901674b1b512e6a6b09699705e9e8afa5d3d7a96e`
> **状态**：REMOTE C0 COMPLETE；harness 实现与运行验证待本地执行 Agent。

## 1. 现有 Test Level 事实

`Scenes/Levels/TestLevel/TestLevel.gd` 非常轻量：

- 继承 `BaseLevel`；
- `_ready()` 把 player 放到 `Vector2.ZERO`；
- 读取 tiles；
- `Globals.reset()`；
- 立即调用 `spawn_cluster_in_ladder(0, 0, 300, current_wave)`。

`TestSpawner.tscn` 当前只有一个空 `Node2D`，没有脚本、fixture 或 scenario driver。

`BaseLevel.spawn_cluster_in_ladder()` 从 `get_spawnables()` 中随机选择 mob，意味着当前 TestLevel 更像压力/杂乱测试环境，而不是确定性回归 harness。

## 2. X5 设计结论

不要重写 BaseLevel，也不要修改 Player/Mob/GenericSkill 核心逻辑。

X5 应在 TestLevel/测试工具层增加一个**确定性 scenario driver**：

- 显式 seed；
- 显式 scenario id；
- 显式 mob composition；
- 显式 spawn positions/count；
- 统一开始/结束条件；
- 结构化 telemetry/evidence 输出。

## 3. 第一批建议 scenario

至少：

- `movement_dash_smoke`
- `single_melee_hit`
- `single_ranged_pack`
- `rapid_hit_10s`
- `cluster_kill_20`
- `projectile_density`
- `chain_pierce_trigger`

不要默认使用现有“随机 300 mobs”作为所有 Gate 的唯一场景；它可以保留为 `stress_random_300`。

## 4. Telemetry 最小合同

每次 scenario 至少输出：

- scenario id / seed；
- candidate hash / git SHA / modset；
- start/end timestamp；
- boot/fatal；
- spawned / alive / killed；
- duplicate death（若可测）；
- damage/trigger count（若可测）；
- frame/FPS/frame pacing（能力允许）；
- screenshot/capture 路径（能力允许）；
- exit code；
- `PASS/FAIL/NOT_PROVEN` 以及“证明什么/不证明什么”。

## 5. 无人值守 UX

X5 最终应让用户/协调器通过一条命令表达一个意图，例如：

`python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <candidate>`

实际文件名可调整，但不得要求用户手工点十几个菜单、输入绝对路径或人工整理日志。

## 6. 与 sibling 的边界

- X1 提供 Player response Candidate；
- X2 提供 Mob hit reaction Candidate；
- X3 提供 Skill/Projectile/TCE facts；
- X4 提供 Audio foundation；
- X5 只负责可重复 scenario/driver/telemetry，不抢它们的核心 preimage。

本地执行 Agent 接手后应继续实现 harness、运行自测并提交 branch/final SHA/handoff。
