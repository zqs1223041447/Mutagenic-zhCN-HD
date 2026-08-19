# B1-X3 Combat Pipeline C0 审计

> 任务：B1-X3（Skill/Projectile/TCE Combat Pipeline）
> 基准：`b378eb1d412ae739237a1cd7d1922797b0be6af2`（batch/b1-anchor）
> 分支/worktree：`agent/b1-x3-combat-pipeline` @ `<task_worktree>`（由 B1 批次协调器分配）
> 证据：`docs/ai/audits/B1-X3-combat-pipeline-evidence.json`（文件 SHA canary + 锚点行号）
> 可运行契约：`scripts/validate/semantic_combat_pipeline_contract.py`
> 审计级别：C0 静态（只读 `04_recovered` + `mods/`，无运行）

---

## 1. 范围与责任边界

| 文件 | 归属 | 处置 |
|---|---|---|
| `Scenes/Skills/GenericSkill.gd` | X3 | 只读审计 + foundation patch |
| `Scenes/Projectiles/Projectile.gd` | X3 | 只读审计（本次不 patch） |
| `Scenes/Stats.gd` | X3 | 只读审计 + foundation patch（依赖 feat-tce 后置文本） |
| `Scenes/Skills/Playable/{Arrow,Axe}/*.gd`、`Projectiles/Skills/*Projectile.gd`、`AreaInstantDamageApplier/*` | X3 审计面 | 只读 |
| `Scenes/Player/Player.gd` | X1 | **禁止修改**（preimage 不变） |
| `Scenes/Mobs/Mob.gd` | X2 | **禁止修改**（preimage 不变） |
| `mods/feat-tce`、`mods/feat-projectile-data-driven` | base | 依赖/审计 |

## 2. 任务 7 问回答（均带证据行号，见 evidence JSON anchors）

### Q1 技能如何施放（输入接线路径）
- **无用户直连输入**：`Player.gd` 只处理 dash（line 91）；没有按键接技能的直接路径。
- 施放是**纯冷却自动施放**：`GenericSkill._physics_process`(112) 每物理帧计冷却 → 到期 `_cast()`(1452) → `not is_disabled and can_cast()`(1455) 守卫 → `cast()`(1484)。
- `can_cast()`(1481) 基类 + Playable 变体（`Arrow.can_cast`(7) 在 8 行调 `get_visible_enemies(true)`，见 Q6）。
- 结论：任何"前摇/取消/按住"能力都需**新建状态机**（挂点 `_physics_process`/`_cast`，X3 owned）；当前无 startup/recovery 状态可增强。

### Q2 攻速/施放速度如何换算
- `get_cooldown()`(1407) = cooldown / cast_speed（floor 0.025s，精确 clamp 待 S1）；`get_stat`(340)/`get_effective_tier`(316) 提供数据；非帧率依赖。
- 含义：cast_speed 越高 `can_cast` 触发越频繁 → Q6 成本。

### Q3 投射物速度/射程/寿命
- `Projectile.gd`：`lifetime` 默认 2.0(29)、`max_distance_travelled` 默认 300(21)、`class_name Projectile`(3)、`skill_parent_weakref`(26)。
- 覆盖通道（feat-projectile-data-driven）：技能从可选项读 `get_projectile_lifetime/get_projectile_max_range`，缺省回退 2.0/300。
- 速度：Playable cast 侧 `force = get_force()`(1328) → `linear_velocity`（Arrow.gd:28）。

### Q4 pierce/chain 在哪实现（保证方）
- **不在 Projectile 内部区分**：`hits = 1 + get_extra_hits()`（Arrow.gd:26，pierce+chain 预算合并）；`chains = get_chains()`(27)；链重定向在 `_on_hit`。
- `Projectile.on_enter`(100)：`hits -= 1`、虚钩 `on_hit(target)` + `_on_hit()`、`expired` 守卫；`hits<=0 and has_limited_hits` → `destroy_projectile`(121/124)。
- 保证方 = 玩家（get_extra_hits/get_pierces/get_chains）+ 投射物 hits 预算。per-hit 事件不区分第几跳；如需区分，唯一鉴权点在 `Projectile.on_enter`。

### Q5 事件派发语义：hit/crit/kill 触发几次、谁监听
- **唯一伤害入口** `Stats.apply_damage`(607)：`roll_crit`(597) → block 早退(627-634) → evade 早退(636-640) → **每次生效命中恰好一次** `on_take_damage(...)`(779) → `did_kill` 时**恰好一次** `attacker_stats.on_kill(self, is_dot_damage)`(811) → `died` 信号 call_deferred。
- 防守侧 `on_take_damage`(1041)：DoT 早退(1043)；**每次落地命中一次** `skill_parent.on_hit()`(1304)，crit 再加 `on_crit()`(1306)。
- 攻击侧：`GenericSkill.on_hit`(94)/`on_crit`(87) 守卫 `not is_triggered and stats.is_player` → `stats.trigger_on_hit()`(103)/`trigger_on_crit()`(92) = TCE 派发点（Stats.gd:910/899）。
- TCE（feat-tce）：派发注入在 `on_kill`(872 区)/`trigger_on_crit`/`trigger_on_hit`/`on_take_damage`(1041) 顶部；**on_take_damage 的派发在 is_dot 守卫(1043)之前 → DoT 每 tick 也到 TCE on_take_damage**（per-trigger cooldown 按 mod_id 去重，context 带 is_dot 可过滤）。
- DoT：`BaseEffect._physics_process`(69) 每物理帧(60/s) `on_tick`(89) → `apply_damage(is_dot_damage=true)` → 跳过 block/evade/on_take_damage；**DoT 击杀可触发 on_kill**（is_dot_damage 透传）。

### Q6 高频成本（最高频部分 + 如何测量）
- **can_cast 可见性扫描**：每次冷却到期 `get_visible_enemies(true)`（Stats.gd:2033 遍历 nearby_enemies，逐目标 intersect_ray mask=256；nearby 维护在 2231/2238）→ 高攻速（floor 0.025s）下每秒最多 ~40 次扫描 × N 敌人。
- **chain 重定向**：每跳 `get_visible_allies` 全树组扫描（静态证据）。
- **DoT 每帧伤害**：60 次 apply_damage/s/效果。
- **每命中开销**：FloatingDamageManager + 音效/粒子 + on_hit/on_crit 守卫分支。
- 测量：S5 lane 在 VM 内做帧预算探针（cast 计数/raycast 计数/伤害事件计数）；X3 不改任何数值。

### Q7 Impact Profile 挂点候选（证据 + 理由）
| 事件 | 挂点 | 证据 | 注意 |
|---|---|---|---|
| per-cast | `_cast`(1452) / Playable cast() | Q1 | 自动施放时=冷却节拍 |
| per-hit | `on_take_damage`(1041) DoT 守卫后 | Q5 | 玩家挨打也走此路 → 用 attacker_stats.is_player 过滤 |
| per-kill | apply_damage did_kill 分支(809-811) | Q5 | 死亡动画在防守侧（Mob._on_death），queue_free 延迟 |
| contact FX | `Projectile.on_enter`(100) / AoE applier(45) | Q4 | 唯一带 pierce/chain 鉴别点 |
| TCE 聚合 | `Stats.trigger_effects`（feat-tce） | Q5 | 伤害类 trigger 的天然聚合点；本次 foundation 落此 |

## 3. foundation 能力：mods/feat-tce-context
- **内容**（行为零变化，可选参数 + context 键扩展）：
  1. `Stats.trigger_on_hit(target = null, did_crit = false)`：context 增加 `target`/`did_crit`；
  2. `Stats.trigger_on_crit(target = null)`：context 增加 `target`；
  3. `Stats.on_take_damage` 内 `skill_parent.on_hit(self, did_crit)` / `skill_parent.on_crit(self)` 透传；
  4. `GenericSkill.on_hit(target = null, did_crit = false)` / `on_crit(target = null)` 透传到 stats。
- **消费者**：后续 damage 类 trigger（"on hit with crit"、"on_hit 对目标附加"）无需再改事件链；on_take_damage context 已由 feat-tce 提供 attacker_stats/did_crit/skill_parent。
- **为什么不做更多**：hit/crit/kill 链已是单次派发；改数值/频率无 S5 测量支撑；pierce/chain 鉴别需改 Projectile（无当前消费者）。不为"必须有代码"制造 patch。

## 4. 风险登记（R1-R5，详见 evidence JSON）
- R1(mid)：高攻速下 can_cast raycast 扫描成本 → S5 实测后再调。
- R2(low)：TCE on_take_damage 对 DoT tick 也派发 → per-trigger cooldown + is_dot 条件过滤。
- R3(low)：hits 合并 pierce+chain 预算，per-hit 事件无跳数鉴别 → 消费方按需用 Projectile.on_enter。
- R4(low)：block/evade 早退 → per-hit 计数不含未命中尝试；attempt 级指标需在 apply_damage 守卫前挂钩。
- R5(info)：DoT 击杀可触发 on_kill（is_dot 透传）→ 消费方过滤。

## 5. 未证明项（手写交接时必须保留）
- runtime 冷却 floor 0.025s 精确 clamp（需 VM 帧探针）
- chain 每跳 get_visible_allies 成本数值（仅静态证据）
- 最大密度下 per-hit FX 计数（需 S5）
- TCE 端到端触发（feat-tce 未证明项）

## 6. Build 记录（由 build 步骤回填）
- Build ID：`B1-X3-combat-pipeline-<YYYYMMDD>`（10_logs/，gitignored）
- Gate 状态：resolve / apply / compile / delta / pack / pck / roundtrip / boot / semantic → 见 build.json