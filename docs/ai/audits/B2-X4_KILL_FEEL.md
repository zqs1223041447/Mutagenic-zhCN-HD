# B2-X4: Kill Feel v1 — 审计文档

- 任务：B2-X4 | Branch：`agent/b2-x4-kill-feel`
- 基座：`ea7854f6ad0602da52e06ab5b5e475fbc79f1e23`（= `batch/b2-waveb-anchor`，Wave A 已集成，含 X1 事件脊柱）
- 交付：`mods/b2-x4-kill-feel/mod.json`、`scripts/validate/semantic_kill_feel_contract.py`、本审计文档
- 验证：`semantic_kill_feel_contract.py` 全项 PASS；resolve+apply 干跑 PASS（见下文）

## 1. 设计

### 1.1 统一 kill 事件消费（不复制第二套事件总线）
死亡表现层不发射任何事件、不写 spine。只在 `Mob._on_death` → `spawn_death_animation()`
末尾**只读**消费 X1 事件脊柱：

- 数据源：被击杀者自身 `stats._spine_last_events` 尾部记录（X1 语义：`died` 信号为
  `call_deferred`，`apply_damage` 全部完成（含 `kill` 记录写入）后才进入 `_on_death`；
  死亡后 `health<=0/is_dead` 早退保证无后续追加 ⇒ 尾部即 kill 记录）。
- 判定：`event_class == "kill"` 且 `did_kill == true`；不满足则静默回退 vanilla（不伪造表现）。
- 字段消费：`is_dot`（DoT 击杀抑制）、无 `did_crit`（X1 kill 记录不含该字段，crit 分层列入
  not_proven / v2 预留）。

### 1.2 强度分层（普通 kill 与 elite/boss 预留分层）
| Tier | 判定 | 表现 |
|---|---|---|
| -1 | 无 kill 记录 / 非 kill 记录 | 零扩展，纯 vanilla |
| 0 | 普通击杀 或 `is_dot == true`（DoT 击杀） | 零扩展，纯 vanilla（低噪声） |
| 1 | `is_elite` | `shatter.instance()` 爆发（scale 1.25） |
| 2 | `is_level_boss` | `shatter` + `poof`（BurningDeath）双爆发（scale 1.6） |

- 复用 Mob.gd 既有 preload 资产（`shatter = ShatterExplosion.tscn`、`poof = BurningDeath.tscn`），
  不新增任何资产/贴图。
- 增强 FX 全部加挂既有 `ground_layer`，与 vanilla frozen/burning 分支互不干扰
  （elite+frozen 死亡会叠双 shatter —— 属于强度语义，已记录）。

### 1.3 cluster kill 抑制（防 FX 爆炸）
- 共享预算挂 GameState globals（`kill_feel_budget`，键 `KILL_FEEL_BUDGET_KEY`），
  不触碰 GameState.gd（`get_global/set_global` 为 pristine 既有 API，已核验）。
- 预算：`KILL_FEEL_CLUSTER_WINDOW_MS = 400`ms 窗口内 `KILL_FEEL_CLUSTER_BUDGET = 3` 次增强；
  超出只放 vanilla dissolve，绝不为单次死亡堆叠多个爆发。
- 5–20 集群击杀场景：同窗口最多 3 个爆发（模型仿真验证），随后静默降级。

## 2. 修改面（全部锚定 pristine Mob.gd，preimage `ba46348c…`）

| Patch | 锚点（count=1） | 内容 |
|---|---|---|
| P1 consts | `var last_global_position\nvar _needs_recheck = false` | 预算键/窗口/预算/两层 scale 常量 |
| P2 helpers | `func spawn_death_animation():`（前插） | `_kill_feel_tier()` / `_kill_feel_consume_budget()` / `_kill_feel_apply_boost(tier)` |
| P3 call | BURNING 分支尾（`ground_layer.add_child(poof_instance)` 后追加） | `_kill_feel_apply_boost(_kill_feel_tier())`（唯一调用点） |

- 与 k2-hit-reaction 的 Mob.gd 3 处 patch 锚点（`pathing/velocity`、hit reaction 计时等）
  零重叠（contract 内做 old/new 文本互斥校验）。
- 不触碰：`apply_damage` / `reduce_health` / 伤害数值 / `queue_free` / pickup 掉落 /
  `trigger_effects` / `_spine_record` / camera / shake / hit-stop（contract 逐 token 禁止）。

## 3. 死亡顺序与 death-once 审计

- pristine `_on_death` 体：`spawn_death_animation()`（offset 3021）→ `queue_free()`（offset 3049），
  drop 逻辑在死亡动画之前 ⇒ P3 调用点位于 `spawn_death_animation` 内部（vanilla FX 之后、
  `queue_free` 之前），不插入任何 drop/死亡顺序变更。
- death-once：kill 记录由 X1 保证单次发射（`did_kill` 分支仅执行一次 + `health<=0/is_dead`
  早退）；本 mod 只读不写、全文件仅 1 个 boost 调用点（contract 断言 count==1），无二次 `queue_free`。

## 4. 验证矩阵

| 场景 | 断言 | 结果 |
|---|---|---|
| single kill（普通） | tier 0，零扩展 | PASS（模型） |
| single elite kill | tier 1 → 1 次爆发 | PASS（模型） |
| boss kill | tier 2 → shatter+poof | PASS（模型） |
| rapid multi-kill（5 连） | 同窗口 ≤ budget(3) | PASS（模型） |
| cluster（20 杀洪泛） | 同窗口 ≤ 3，其余降级 | PASS（模型） |
| DoT 击杀（含 elite/boss） | tier 0，且不消耗预算 | PASS（模型） |
| 非 kill 记录 | tier -1，无伪造表现 | PASS（模型） |
| 窗口重置 | 溢出后新窗口恢复预算 | PASS（模型） |
| death once | 唯一调用点、无二次 queue_free | PASS（静态） |
| drop order | vanilla 顺序完好 | PASS（静态） |

- contract：**N/N PASS**，`exit 0`（含 manifest 不变量、preimage/occurrence 守卫、
  k2 重叠互斥、X1 kill 事件可推导性、绝对路径扫描、LF）。
- resolve+apply 干跑：base=`04_recovered`，resolve 排序按依赖链含本 mod；apply 全量
  `changed_path_count` 仅含 Mob.gd 相关，preimage/occurrence 守卫通过，产物置于
  `10_logs/b2-x4-dryrun/`（gitignored）。

## 5. not_proven / remaining risks

- 真实 in-game 死亡 FX 观感与性能（需 VM S5 + 目视/录制）。
- 窗口内 >3 次精英集群的“有 3 个爆发 + 其余静默”是否足够可读 —— 需人工验收，可调
  `KILL_FEEL_CLUSTER_BUDGET`。
- crit 强度层未接入（X1 kill 记录无 `did_crit`）；v2 可读 penultimate 记录或由 X1 扩展记录字段。
- 极端时序 kill 记录缺失时静默回退 vanilla（安全但不炫）。
- 预算持久化：`GameState` globals 在场景重载时由既有 reset 语义管理，未做跨场恢复验证。
