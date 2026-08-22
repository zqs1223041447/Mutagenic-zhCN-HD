# B2-X1 Combat Event Spine v1 审计

> 任务：B2-X1（Combat Event Spine v1）
> 基线：`2a40ec4d844a76f53c525a54e602b85f85f432b9`（batch/b2-anchor）
> 分支/worktree：`agent/b2-x1-combat-event-spine` @ `<task_worktree>`
> 可运行契约：`scripts/validate/semantic_event_spine_contract.py`
> 审计级别：C0 静态 + 契约模拟（只读 `04_recovered` + `mods/`，无运行 / 无 VM）

---

## 1. 目标

把 B1 的 `feat-tce-context` 旁边对齐出稳定的战斗事件语义层：统一 `direct_hit` / `dot_tick` / `crit` / `kill` 四分类，补全 context（`event_class` / `seq` / `timestamp_ms` / `did_kill` / source / target / is_dot / did_crit / skill_parent），供 Wave B（X4 Kill Feel、X5 Camera Impulse、X6 Combat Audio）消费。

约束执行：
- 不改变伤害计算结果；不改变 collision；death/kill 仍只结算一次；
- DoT 不伪装成 direct hit（`dot_tick` 只在 `if is_dot_damage:` 分支发射）；
- 事件层只记录，不做 Camera shake / Audio 播放 / FX；
- 不复制第二套事件总线：`trigger_effects(` 调用点数量在脊柱应用前后不变（contract 断言），脊柱只做旁路记录 `_spine_record`。

## 2. 范围与责任边界

| 文件 | 归属 | 处置 |
|---|---|---|
| `Scenes/Stats.gd` | X3（既有）+ X1 事件层 | 只读审计 + 5 个新增 CODE_PATCH（锚定原始文本，绝不与 feat-tce / feat-tce-context 区域重叠） |
| `Scenes/Player/Player.gd` | X1 | **禁止修改**（原 preimage 不变） |
| `Scenes/Mobs/Mob.gd` | X2 | **禁止修改**（原 preimage 不变） |
| `mods/feat-tce`、`mods/feat-tce-context` | base（已集成） | 只读依赖 |
| `project.godot` autoload 区 | — | 不触碰（不加新 autoload，事件脊柱挂在 Stats 实例 + _spine_last_events 缓冲） |

新 MOD：`mods/b2-x1-combat-event-spine`（CODE_PATCH，dependencies: `feat-tce-context`）。

## 3. 事件语义 v1

### 3.1 四分类判定规则（唯一事实源 = `Stats.apply_damage`）

| event_class | 判定 | 发射位置（应用后） | 语义 |
|---|---|---|---|
| `direct_hit` | `not is_dot_damage and damage_multiplier != 0` 且未暴击 | apply_damage 内 `on_take_damage` 调用前一行 | 每落地命中一次；block/evade/deflect(multiplier=0) 不计数 |
| `crit` | 同上且 `did_crit == true` | 同一发射点（`_spine_event_class(false, did_crit)` 派生） | crit 是 direct_hit 的属性投影，不重复发射 |
| `dot_tick` | `is_dot_damage == true`（DoT 结算路径） | `if is_dot_damage:` 分支内 | 每 DoT tick 一次；永不与 direct_hit 同发 |
| `kill` | `attacker_stats != null and did_kill` | did_kill 分支内，`on_kill` 调用后 | 每死亡恰好一次（health<=0/is_dead 早退在前，天然幂等） |

DoT 击杀：kill 事件 `is_dot=true` 透传，供 X4/X5/X6 分层；DoT 不伪装 direct hit。

### 3.2 context 字段表

| 字段 | 类型 | 来源 | 说明 |
|---|---|---|---|
| `event_class` | String | 实参 | direct_hit/dot_tick/crit/kill |
| `seq` | int | `_spine_event_seq` 实例级递增 | 单 Stats 实例单调；全局单调需消费方聚合（not_proven） |
| `timestamp_ms` | int | `OS.get_ticks_msec()` | 毫秒时间戳 |
| `did_kill` | bool | context 显式传入（kill 为 true；其余默认 false） | contract 断言 kill 事件必带 true |
| `source` | Stats/weakref 语义未定型 | attacker_stats | 攻击者 Stats 引用（可能被 queue_free，消费方需实例校验） |
| `target` | Stats | self | 承受方 Stats 引用 |
| `is_dot` | bool | 发射分支 | dot_tick 恒 true；kill 透传 DoT 击杀 |
| `did_crit` | bool | 发射分支 | crit 恒 true；direct_hit 携带 |
| `skill_parent` | Node | apply_damage 入参 | 技能节点（可能为 null，如环境/DoT 无技能） |

记录进入 `_spine_last_events` 环形缓冲（上限 64，`pop_front` 淘汰），每个 Stats 实例一份；downstream 读实例缓冲或扩展 TCE trigger 配置消费字段。

## 4. Patch 清单（mods/b2-x1-combat-event-spine，全部 Scenes/Stats.gd）

| # | unit_id | 锚点（04_recovered 原始文本） | 增量 |
|---|---|---|---|
| P1 | vars::spine | `var accumulated_applied_damage = 0.0` (L125) | 追加 `_spine_event_seq` / `_spine_last_events` |
| P2 | insert_spine_helpers | apply_damage 签名行 (L607) | 前置 `_spine_event_class` / `_spine_record` |
| P3 | apply_damage::dot_tick_emit | `if is_dot_damage:` 块 (L765-766) | 分支内追加 dot_tick 发射 |
| P4 | apply_damage::direct_hit_emit | `if not is_dot_damage and damage_multiplier != 0:` (L778-779) | on_take_damage 前插入发射 |
| P5 | apply_damage::kill_emit | `if attacker_stats != null and did_kill:` (L809-811) | on_kill 调用后追加 kill 发射 |

所有 patch：`preimage_sha256 == c187245e...`（Stats.gd 整文件原始 SHA），`expected_occurrences == 1`，行尾 LF。
锚点与 feat-tce / feat-tce-context 的 old_text/new_text 区域（keystones/status_flags 变量区、reduce_health/on_kill 函数区、trigger_on_crit/trigger_on_hit 签名区、on_take_damage 头部、skill_parent.on_hit/on_crit 区）零重叠（已程序化核验）。

## 5. 验证结果

### 5.1 semantic contract（venv python，可重复）

```
venv\Scripts\python.exe scripts/validate/semantic_event_spine_contract.py
checks: 44/44 passed
verdict: PASS   (exit code 0)
```

覆盖：
- manifest 不变量（id / dependencies 含 feat-tce-context / target_original_sha256）；
- 逐 patch：path 白名单 Scenes/Stats.gd、preimage == 原始 SHA、old_text 逐字节计数 == expected_occurrences；
- 对 pristine Stats.gd 按顺序模拟 5 patch 全量应用（与 apply_mod.py 同的 occurrence walk）；
- 语义 canary：`trigger_effects(` 数量不变（无第二总线）；`*=` 与 `+= combined_effective_damage` 计数不变（无伤害数值改动）；3 个发射点 + 1 个定义；dot_tick 在 is_dot_damage 块内；crit 绑定 did_crit；kill 带 did_kill=true；缓冲上限 64；seq/timestamp_ms 存在；
- 无宿主绝对路径扫描（mod.json / contract / audit 三文件）。

### 5.2 干跑证明（preimage + occurrence 守卫生效）

见 10_logs 下 apply 干跑 report：resolve_mod_chain → apply_mod（base=04_recovered）通过，postimage 落盘（补齐证据引用）。

## 6. 下游消费接口（X4/X5/X6）

1. **读缓冲**：任意系统对受害者 Stats 实例读 `stats._spine_last_events`（Array，最新 64 条，含全字段）；或直接监听既有信号（`died` / `damage_taken`）并在回调中取 `stats._spine_last_events.back()`。
2. **过滤策略建议（X5/X6）**：camera/audio 默认只消费 `event_class == "crit" or "kill"`（heavy 由 ctx.is_dot/damage 阈值自行聚合，事件层不越界做轻重判定）；`dot_tick` 建议节流聚合（事件层不节流，60/s 上限由消费方预算）。
3. **TCE trigger 配置**：既有 trigger context 已由 feat-tce-context 带 target/did_crit（on_hit/on_crit）与 is_dot（on_kill/on_take_damage）；事件层不复制该通道，仅旁路记录。
4. X4 的 elite/boss 分层：kill 事件无 elite 字段（Mob 未 patch），X4 需自读 `target.get_parent()` 的 is_elite/is_level_boss（保持 Player/Mob preimage 不变的代价，已登记风险）。

## 7. 风险登记

- R1(mid)：`seq` 实例级非全局 → 高频多目标场景下时间线排序需消费方按 timestamp_ms 聚合；v1 接受，Wave B 消费方自行规整。
- R2(low)：source/target 为强引用，queue_free 后消费方调用需 `is_instance_valid` 保护（Godot 引用计数对象 freed 后访问报错）。
- R3(low)：事件层无节流，DoT 高频 tick / 高频 hit 的事件流冲击由 X5/X6 预算控制（X6 已有 60ms 聚合 + 16 voice budget 可复用）。
- R4(info)：kill 事件在 defender 的 Stats 实例上记录（与 on_kill 攻击者侧方向相反）→ 消费方读被击杀者缓冲，或改从 attacker 侧 on_kill 追加记录（v1 不扩散）。

## 8. 未证明项（诚实声明）

- 真实游戏 runtime 事件序列（VM boot + harness telemetry 未跑；S1/S2 无 VM 环境）；
- 编译 / pack / boot（compile/pack 需完整管线与 GDRE 环境，B2-X3 集成阶段跑 aggregate）；
- X4/X5/X6 端到端消费效果（Wave B 任务各自验证）；
- GDScript 语法级校验（apply 后文件未过 GDRE --compile；contract 只证明文本层守卫与结构不变量）。