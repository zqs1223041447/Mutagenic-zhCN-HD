# B2-X5 Camera Impulse v1 审计

> 任务：B2-X5（Camera Impulse v1）
> 基线：`ea7854f6ad0602da52e06ab5b5e475fbc79f1e23`（batch/b2-anchor）
> 分支/worktree：`agent/b2-x5-camera-impulse` @ `<task_worktree>`
> 可运行契约：`scripts/validate/semantic_camera_impulse_contract.py`
> 审计级别：C0 静态 + 契约模拟（只读 `04_recovered` + `mods/`，无运行 / 无 VM）

---

## 1. 目标

在 Player.gd 建立相机 impulse aggregator，消费 B2-X1 事件脊柱（`Stats._spine_last_events`）产生受控相机偏移：玩家击杀（kill / elite kill）与玩家承受的重击（heavy）触发 impulse；crit 记录提供轻量 impulse；普通 direct_hit / dot_tick 默认禁止。不改伤害逻辑，不新建事件总线，不新增 autoload / 二进制资产。

约束执行：
- emission 侧（Stats.gd）只在高价值点**旁路注入** `_spine_impulse`（复用 X1 `_spine_record`，不复制事件系统）；普通 direct_hit 与 DoT tick 不发任何 impulse；
- consume 侧（Player.gd）对 `direct_hit` / `dot_tick` / X1 自带 `kill` 记录一律跳过并计入 `blocked_*` 遥测；
- 聚合幅度受 `IMPULSE_BUDGET_MAX` 预算钳制、窗口内 cluster kill 子加性合并、逐帧线性衰减、最终 offset 幅度受 `IMPULSE_MAX_OFFSET` 安全帽钳制；
- 不修改 Stats.gd / Player.gd 任何伤害计算、碰撞、死亡结算。

## 2. 范围与责任边界

| 文件 | 归属 | 处置 |
|---|---|---|
| `Scenes/Stats.gd` | X3 + X1 + X5 | 只读审计 + 3 个新增 CODE_PATCH（锚定原始文本；S2 锚在 on_kill 尾部 swiftness 块、S3 锚在 X1 dot 块与 direct_hit 块之间，均避开 feat-tce / feat-tce-context / b2-x1 区域） |
| `Scenes/Player/Player.gd` | X5 | 3 个新增 CODE_PATCH（vars / camera2d 引用 / 聚合器函数集；锚点避开 k1 的 dash 区域） |
| `Scenes/Mobs/Mob.gd` | X2 | **禁止修改**（原 preimage 不变） |
| `mods/feat-tce`、`mods/feat-tce-context`、`mods/b2-x1-combat-event-spine` | base（已集成/并行） | 只读依赖；本任务声明 `dependencies: ["b2-x1-combat-event-spine"]` |

新 MOD：`mods/b2-x5-camera-impulse`（CODE_PATCH，6 patches）。

## 3. 设计

### 3.1 事件策略（consumption policy，唯一事实源 = Player._impulse_poll_events）

| 事件 | 处置 | 幅度 | 遥测 |
|---|---|---|---|
| `direct_hit` | 跳过 | — | `blocked_direct_hits += 1` |
| `dot_tick` | 跳过 | — | `blocked_dot_ticks += 1` |
| `kill`（X1 victim 侧记录） | 跳过 | — | `blocked_kill_records += 1` |
| `crit`（玩家作为 victim 时） | 轻量 impulse | `0.6`（IMPULSE_CRIT_AMPLITUDE） | `crits += 1` |
| `impulse` / `kill` | budget impulse | `amplitude * 0.72`（KILL_RATIO） | `kills += 1`，elite 另计 |
| `impulse` / `heavy` | budget impulse | `1.2`（Stats 侧恒定） | `heavies += 1` |

### 3.2 emission 侧（Stats.gd）

- `_spine_impulse(kind, context)`：补 `impulse_kind` 后转发 `_spine_record("impulse", context)`（单总线）。
- on_kill 尾部：仅当 `get_parent()` 在 player group 时，向本实例缓冲追加 `impulse_kind=kill` 记录；elite 由 `victim.get_parent().get("is_elite")` 判定，幅度 1.6/2.4。不改变击杀/掉落/经验结算。
- apply_damage 内 `accumulated_applied_damage += ...` / `last_damage_time = 0` 之后（即 X1 dot 块与 direct_hit 块之间，不触碰任何发射点）：仅当 `is_player and not is_dot_damage and combined_effective_damage >= health_max * 0.12` 时追加 `impulse_kind=heavy` 记录（幅度 1.2）。

> 说明：crit 不单独发射；玩家被暴击时该 crit 记录自然落在玩家 Stats 缓冲（`on_take_damage` 路径，X1 direct_hit_emit 处 `_spine_event_class(false, did_crit)` 派生），被玩家相机轮询消费。玩家命中怪物的 crit 记录落在怪物 Stats，玩家相机看不到——设计取舍，见 §7 R3。

### 3.3 聚合器（Player.gd）

常量：`IMPULSE_BUDGET_MAX=4.0`、`IMPULSE_WINDOW_MS=250`、`IMPULSE_DECAY_PER_SEC=9.0`、`IMPULSE_MAX_OFFSET=3.5`、`IMPULSE_CRIT_AMPLITUDE=0.6`、`IMPULSE_KILL_RATIO=0.72`、`IMPULSE_CLUSTER_APPENDIX=0.3`、`IMPULSE_CLUSTER_APPENDIX_CAP=2.0`。

- `_process(delta)`：轮询 `stats._spine_last_events` 中 `seq > _impulse_last_seq` 的新记录 → 逐条按 §3.1 处置；然后 `_impulse_decay`；最后 `_impulse_apply_offset`（`camera2d.offset` 取聚合幅度方向向量，幅度受 MAX_OFFSET 钳制）。
- `_impulse_add(added, is_kill)`：幅度单调钳制到 `min(amplitude + added, BUDGET_MAX)`（`capped_amplitude` 计数）；聚合窗口 = 最近一次幅度归零或新 group 起点后 250ms 内叠加；cluster kill 规则：窗口内连续击杀，第 2 起按 `min(0.3*(n-1), 2.0)` 子加性附录（`clusters += 1`）。
- `_impulse_decay(delta)`：线性衰减 `max(0, amplitude - 9.0*delta)`。
- 遥测：`get_camera_impulse_telemetry()` 暴露 `events/impulses/kills/elite_kills/heavies/crits/clusters/blocked_direct_hits/blocked_dot_ticks/blocked_kill_records/capped_amplitude/capped_offset`。

## 4. Patch 清单（mods/b2-x5-camera-impulse）

| # | 文件 | unit_id | 锚点（04_recovered 原始文本） |
|---|---|---|---|
| S1 | Stats.gd | spine_impulse::helper | `func cap_resistance(resistance, maximum = 0.75):`（前置 4 常量 + `_spine_impulse`） |
| S2 | Stats.gd | on_kill::kill_impulse | on_kill 尾部 swiftness 块（`if randf() < gs("swiftness_boon_on_kill_chance"):\n\t\t\t\t\t\t\t\tadd_swiftness_boon(1)`） |
| S3 | Stats.gd | apply_damage::heavy_impulse | `\t\t\t\taccumulated_applied_damage += combined_effective_damage\n\t\t\t\tlast_damage_time = 0` |
| P1 | Player.gd | camera_impulse::vars | `var debug_path_points = []`（追加常量/状态/遥测） |
| P2 | Player.gd | camera_impulse::camera2d_ref | `onready var stats = $Stats`（追加 `camera2d`） |
| P3 | Player.gd | camera_impulse::aggregator | `func _physics_process(delta):`（前置 `_process` + 4 个聚合器函数） |

所有 patch：`preimage_sha256` 为各自文件整文件原始 SHA（Stats.gd=`c187245e...`，Player.gd=`3f009989...`），`expected_occurrences == 1`，行尾 LF。
锚点经程序化核验与 feat-tce / feat-tce-context / b2-x1 / k1 / k2 / b2-x0-* / c5-l13 / c5-l16 / feat-autosave 的 old_text/new_text 区域零重叠（契约 §2b）。`target_original_sha256` 与 b2-x1 链一致（`C7B5D5A5...`，resolve_mod_chain 要求整链一致）。

## 5. 验证结果

### 5.1 semantic contract（venv python，可重复）

```
venv\Scripts\python.exe scripts/validate/semantic_camera_impulse_contract.py
checks: 93/93 passed
verdict: PASS   (exit code 0)
```

覆盖：
- manifest 不变量（id / dependencies 含 b2-x1 / patch_type / 6 patches / asset_overlays 空 / target_original_sha256 与链一致）；
- 逐 patch：path 白名单、preimage == 原始整文件 SHA、old_text 逐字节计数 == expected_occurrences（==1）；
- 与 10 个 sibling mod 的同路径 old_text/new_text 双向子串重叠审计（0 hits）；
- 对 pristine Stats.gd / Player.gd 按顺序模拟 6 patch 全量应用（与 apply_mod.py 同 occurrence walk）；
- emission canary：`_spine_impulse` 调用点 kind 仅 kill/heavy；DoT 累计区与 direct_hit 发射区无 impulse；kill 记录 player-group 门控 + victim 父节点 elite 判定；heavy 记录 `is_player`/`not is_dot_damage`/阈值门控；复用 `_spine_record`（无第二总线，无 trigger_effects 调用）；
- consume canary：direct_hit/dot_tick 跳过计数、crit 轻量、kill/elite/heavy budget 消费、预算钳制、offset 安全帽、decay、cluster 计数器、12 项遥测字段、`get_camera_impulse_telemetry`、每帧 `camera2d.offset` 写入；
- 伤害逻辑 canary：无 `damage_multiplier`/`health`/`combined_effective_damage` 赋值，无 `reduce_health(`/`on_take_damage(`/`apply_central_impulse(` 注入；
- MirrorAggregator 模拟（常量从 patch 实际载荷解析）：A. 5 direct_hit + 3 dot_tick → 零幅度 + blocked 计数；B. 3 crit → 1.8；C. decay 0.2s → 归零；D. t=0/80/160/240 四次 kill → kills=4 / clusters=3 / 幅度钳到 4.0；E. 间隔 10s 两次 kill → 2 组 / clusters=0；F. 30 crit → amplitude=4.0、offset==3.5；G. heavy 1.2；H. elite 2.4*0.72≈1.728；I. 遥测总量一致；
- 无宿主绝对路径扫描（mod.json / contract / audit 三文件）。

### 5.2 干跑证明（preimage + occurrence 守卫生效）

见 `10_logs/b2-x5-dryrun/`：resolve_mod_chain（root= mods/b2-x5-camera-impulse/mod.json）→ apply_mod（base=04_recovered，out 为新建目录）report 通过，postimage 落盘；产物中核验 `_spine_impulse` 调用点与聚合器函数存在。

## 6. 下游消费接口

- `get_camera_impulse_telemetry()`：调试 / harness 断言入口（VM S4/S5 用）。
- 相机 offset 每帧由 `_process` 覆写 `camera2d.offset`；既有 `offset_v = 0.21`（Player.tscn）不受影响（不同属性）。
- 后续 X6（Combat Audio）可直接复用 `_spine_last_events` 缓冲与 X1 语义（不依赖本任务聚合器）。

## 7. 风险登记

- R1(mid)：elite 判定依赖 `victim.get_parent().get("is_elite")`（Mob 节点属性，非 Stats 字段）；若该属性不存在则视为普通 kill（幅度 1.6）——不影响正确性，只影响分层。
- R2(mid)：`seq` 为实例级 → 玩家相机只轮询**自己** Stats 的缓冲；玩家命中怪物的 crit / 击杀（attacker=玩家时 kill 记录在玩家侧，见 §3.2 设计）覆盖主路径，但怪物侧事件（他人打怪）天然不可见，符合"玩家视角"目标。
- R3(low)：DoT 击杀不产生 kill impulse（X1 kill 记录在 victim 侧且 `is_dot=true` 时仍按 blocked_kill_records 计数）——设计取舍，不扩散。
- R4(low)：`camera2d.offset` 与 Camera2D smoothing 叠加观感未知，需 VM S5 人工验收。
- R5(low)：`_process` 内对 buffer 全量扫描（上限 64 条）每帧成本可忽略；事件风暴由预算钳制兜底。
- R6(info)：`source`/`target` 强引用字段在事件记录中，消费方（本任务不读 source）无需解引用；后续调用需 `is_instance_valid` 保护。

## 8. 未证明项（诚实声明）

- 真实游戏 runtime 聚合器逐帧行为与观感（VM boot + harness telemetry 未跑；S1/S2/S4/S5 无 VM 环境）；
- 编译 / pack / boot（compile/pack 需完整管线与 GDRE 环境，B2-X3 集成阶段跑 aggregate）；
- Camera2D smoothing 与 offset 叠加的实际效果；
- elite 判定在真实 Mob 上的有效性；
- GDScript 语法级校验（apply 后文件未过 GDRE --compile；contract 只证明文本层守卫与结构不变量）。
