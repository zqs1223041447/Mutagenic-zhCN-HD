# P3_PLAYABLE_BASELINE.md — Playable Baseline 详细计划（Lean v3.2）

> 本文件是 P3 的执行权威细化。  
> gork 必须按本文件拆 Task DAG，**无依赖任务并行 + background 模式**执行。  
> 与 `AGENT.MD`、`DEVELOPMENT_PLAN_FRAMEWORK.md` 配套使用。

---

## 1. P3 定义与 Exit Criteria

### 定义

玩家可完成以下最小可玩循环，且该循环**可被自动化测试完整覆盖**：

```text
进入角色
→ 进入世界（TestLevel 或 DefaultLevel）
→ 移动 + Dash
→ 释放至少 1 个主动技能
→ 击杀至少 1 只怪物
→ 拾取至少 1 件装备/掉落
→ 打开技能界面 + 被动树界面（可查看，基础交互）
→ 保存 → 读取（状态可恢复）
```

### Exit Criteria（全部满足才可标记 P3 PASS）

| ID | 条件 | 验证方式 |
|----|------|----------|
| E1 | headless 下可从 LoadGame 稳定到达角色可选/已选状态 | 自动化 smoke |
| E2 | 可进入世界场景（TestLevel 优先）且无阻断级脚本错误 | 自动化 smoke + error budget |
| E3 | 角色可移动与 Dash，位置变化可观测 | 自动化 / 坐标断言 |
| E4 | 可释放至少 1 个主动技能，产生可观测战斗事件 | combat harness / 事件日志 |
| E5 | 可击杀至少 1 只怪物（生命归零 + 死亡事件） | combat harness |
| E6 | 可拾取至少 1 件掉落物并进入背包/装备逻辑 | 自动化断言 |
| E7 | 技能界面与被动树界面可打开且不崩溃 | UI smoke |
| E8 | Save → Load 后关键状态（位置/生命/装备/技能）可恢复 | persistence 测试 |
| E9 | 上述 E1–E8 有可复查 Evidence，并写入 product_state | Evidence 晋升 |
| E10 | product_runtime_ready 可诚实标为 true，或剩余 BLOCKED 仅限已记录的美术源缺失 | 状态机 |

**Error Budget（建议）：**  
P3 完成时，核心冒烟路径上的脚本错误数应 ≤ 当前 P2 基线的显著下降值（具体数字由 gork 在启动 P3 时用机器校准写入 Task）。不得把「大量错误但仍能勉强跑」标为 PASS。

---

## 2. 进入 P3 的前置条件

### 必须先完成或显式豁免

| 前置 | 当前状态（2026-08-21 快照） | 处理 |
|------|-----------------------------|------|
| P2-BATCH-1 | DONE | — |
| P2-BATCH-2 | DONE | — |
| **P2-BATCH-3** | **READY**（BaseLevel tile pipeline 残留 + TierLoader Array + audio bus index） | **必须先做或与 P3-A/B 严格串行依赖**。阻塞正常世界进入流。 |
| product_runtime_ready | false | P3 过程中推进，Exit 时评估 |
| Steam 真接入 | 已永久删除 | 禁止再规划 |

**强制：** gork 启动 P3 主工作前，必须先把 P2-BATCH-3 闭环（或拆成可并行子任务并完成）。不得跳过 tile/TierLoader 问题直接宣称「可进入世界」。

---

## 3. P3 工作流拆分（并行默认）

P3 按**工作流（Workstream）**拆，而不是按随机文件。每个工作流可再拆多个 Task。

```text
P2-BATCH-3（前置，阻塞世界进入）
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  P3 并行核心（无相互硬依赖的可同时 background）              │
│                                                           │
│  P3-A  Character / Save 表面                               │
│  P3-B  World Entry + Movement/Dash                        │
│  P3-C  Combat Loop（技能→伤害→击杀）                        │
│  P3-D  Loot / Equipment 基础                               │
│  P3-E  Skill UI + Passive Tree UI 基础                       │
│                                                           │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
                   P3-F  End-to-End Automation Harness
                   （依赖 A–E 的最小可用版本）
                            │
                            ▼
                   P3-G  Evidence 晋升 + product_state 收口
```

### 3.1 P2-BATCH-3（前置，必须先清）

**Goal：** 消除阻塞正常世界进入的 Godot 4 残留。

**范围（已知）：**
- BaseLevel tile pipeline：`get_used_cells` layer 参数、`set_cell` G3 形式、`update_bitmask_region`
- TierLoader Array 错误
- audio bus index

**Acceptance：**
- BaseLevel / TestLevel / DefaultLevel 可在 headless 下加载且无上述类别的阻断错误
- 相关错误从 boot/smoke 日志中消失或降为可接受的非阻断警告
- Evidence：错误前后对比 + 场景加载成功报告

**Parallelizable：** 内部可按「tile / TierLoader / audio」拆成子 Task 并行。

**Preferred Worker：** AGY

---

### 3.2 P3-A — Character Entry & Save Surface

**Goal：** 从 LoadGame/Menu 稳定进入「角色已选/可玩」状态，Save/Load 表面可用。

**关键路径（参考）：**
- `product/scenes/LoadGame.tscn`（main_scene）
- `product/scenes/Menu.tscn`
- `product/Globals/GameState.gd`、Save 相关 key
- Character select 相关场景/逻辑

**Dependencies：** 无硬依赖 P3 其他流（可与 B/C/D/E 并行准备）

**Acceptance：**
- headless 可到达角色可选或已选状态
- 可触发 New Game / Continue 的最小路径
- Save 写出、Load 读回至少包含：角色标识、基础属性、位置（若已进世界）
- 无阻断级脚本错误

**Required Evidence：**
- smoke 日志（LoadGame → Menu → Character）
- save 文件前后 diff 或 schema 断言
- error 计数

**Parallelizable：** true（相对其他 P3 流）

---

### 3.3 P3-B — World Entry + Movement / Dash

**Goal：** 角色可进入世界场景，可移动与 Dash，位置变化可机器观测。

**关键路径：**
- `product/scenes/World.tscn`
- `product/scenes/Levels/TestLevel`、`DefaultLevel`、`BaseLevel`
- `product/scenes/Player/Player.tscn` + `Player.gd`
- 输入与 Dash 相关 action

**Dependencies：**
- **硬依赖 P2-BATCH-3**（tile/世界加载）
- 软依赖 P3-A（有角色上下文更稳，但可用测试角色桩）

**Acceptance：**
- headless 或自动化可加载 TestLevel（优先）并生成 Player
- 移动指令后位置发生变化（断言）
- Dash 可触发且有位移或状态变化
- 无阻断级移动/物理脚本错误

**Required Evidence：**
- 场景加载报告
- 位置采样日志（t0 / t1）
- Dash 事件或状态日志

**Parallelizable：** 在 P2-BATCH-3 完成后 true

---

### 3.4 P3-C — Combat Loop（技能 → 伤害 → 击杀）

**Goal：** 至少 1 个主动技能可释放，对至少 1 只怪物造成伤害并击杀。

**关键路径：**
- `product/scenes/Skills/`、`product/Globals/Skills.gd`、SkillTiers
- `product/scenes/Mobs/`、Monster* Globals
- `product/scenes/Projectiles/`、StatusEffects
- `tests/combat_harness/`

**Dependencies：**
- 软依赖 P3-B（有世界与 Player 更真实）
- 可用 combat_harness 做隔离验证，降低对完整世界的依赖

**Acceptance：**
- 可实例化至少 1 个可释放技能
- 可实例化至少 1 只怪物
- 技能命中后怪物生命下降
- 生命归零触发死亡/移除
- combat_harness 或等价自动化可重复

**Required Evidence：**
- combat_harness 报告（或等价）
- 伤害事件 / 死亡事件日志
- 前后 HP 断言

**Parallelizable：** true（可与 A/D/E 并行；与 B 可部分重叠）

---

### 3.5 P3-D — Loot / Equipment 基础

**Goal：** 击杀或测试源可产生掉落，角色可拾取并进入装备/背包逻辑。

**关键路径：**
- Equipment / Gene 相关 Globals 与场景
- 掉落 / pickup 逻辑
- `product/scenes/Interactables/` 等

**Dependencies：**
- 软依赖 P3-C（真实击杀掉落更完整）
- 可用测试直接 spawn 掉落物，降低耦合

**Acceptance：**
- 至少 1 种掉落物可生成
- 角色碰撞/交互后可拾取
- 拾取后进入可查询的库存或装备槽
- 无阻断级装备脚本错误

**Required Evidence：**
- 掉落生成与拾取日志
- 库存/装备槽断言

**Parallelizable：** true

---

### 3.6 P3-E — Skill UI + Passive Tree UI 基础

**Goal：** 技能界面与被动树界面可打开、可查看、不崩溃；基础交互可用。

**关键路径：**
- Skill / Passive 相关 UI 场景
- `product/Globals/PassiveTreeData.gd`、`PassiveTreeUtils.gd`
- `product/passive_tree_data/`
- GUI / Popups / UI 目录下相关场景

**Dependencies：** 无硬依赖其他 P3 流（可早期并行）

**Acceptance：**
- 可从游戏内或测试入口打开技能界面
- 可打开被动树界面
- 显示至少部分真实数据（技能名/节点），不崩溃
- 关闭界面后可回到游戏状态

**Required Evidence：**
- UI open/close 日志
- 截图或节点树断言（可选）
- error 计数

**Parallelizable：** true

---

### 3.7 P3-F — End-to-End Automation Harness

**Goal：** 把 A–E 串成一条可重复的自动化冒烟/回归路径。

**Dependencies：** A–E 均达到「最小可用」

**Acceptance：**
- 单条命令或脚本可跑通：LoadGame → 角色 → 世界 → 移动 → 技能 → 击杀 → 拾取 → 开 UI → Save/Load
- 结果机器可读（PASS/FAIL + 分步证据）
- 可在 CI 或本地 headless 重复

**Required Evidence：**
- harness 运行报告
- 分步时间戳与断言结果
- 最终 product_state 更新建议

**Parallelizable：** false（收口性质，但 harness 内部步骤可并行准备）

---

### 3.8 P3-G — Evidence 晋升与状态收口

**Goal：** 所有 P3 Evidence 晋升，product_state 更新，P3 标记完成或明确剩余 BLOCKED。

**Acceptance：**
- E1–E10 均有对应 Evidence 或明确的 BLOCKED 记录（仅允许美术源类）
- `state/product_state.json` 反映 P3 结果
- 中文 GitHub 状态同步
- 工作区清理完成

---

## 4. 建议的 Batch 执行顺序（给 gork）

### Phase 0 — 前置清障（可立刻启动）

```text
P2-BATCH-3
  ├─ P2-B3-TILE   BaseLevel tile API 残留      (background)
  ├─ P2-B3-TIER   TierLoader Array 错误        (background)
  └─ P2-B3-AUDIO  audio bus index              (background)
```

三者无硬依赖，**必须并行 background**。

### Phase 1 — P3 并行启动（P2-BATCH-3 完成后，或 B 对世界加载的依赖满足后）

```text
并行 background：
  P3-A  Character/Save
  P3-C  Combat Loop（可用 harness 隔离）
  P3-D  Loot 基础（可用 spawn 桩）
  P3-E  Skill/Passive UI
  P3-B  World/Movement（依赖 P2-BATCH-3）
```

### Phase 2 — 串联与收口

```text
P3-F  E2E Automation Harness
P3-G  Evidence + product_state 收口
```

---

## 5. Task 模板（创建具体 Task 时使用）

```text
Task ID: P3-A-01
Goal: ...
Why Now: 解锁角色进入与存档表面
Scope: ...
Allowed Paths: product/scenes/LoadGame* ; product/scenes/Menu* ; product/Globals/GameState* ; ...
Forbidden Paths: 03_raw/** ; 04_recovered/** ; 直接改中央分支
Dependencies: []          # 空 = 默认可并行
Acceptance Criteria:
  - ...
Required Evidence:
  - ...
Known Risks: ...
Rollback: ...
Preferred Worker: AGY
Needs Expert: false
Parallelizable: true
```

---

## 6. 错误与美术边界策略

| 类型 | 策略 |
|------|------|
| 代码/API/脚本错误 | 必须修，计入 Error Budget |
| 逻辑缺失导致循环中断 | 必须修或提供测试桩 |
| missing_asset（.aseprite 等） | 不阻塞 P3 Exit；记录为 BLOCKED/HUMAN_INPUT_REQUIRED 或采用占位后继续 |
| 主观手感/视觉 | 不作为 P3 Exit 条件；留给 P4 |

---

## 7. 与现有测试资产的关系

已有：
- `tests/combat_harness/` — 优先扩展为 P3-C 的核心验证
- `tests/s3_persistence/` — 优先用于 P3-A / E8
- `tests/s5_evidence/` — Evidence 格式参考

**原则：** 扩展现有 harness，而不是从零再造一套并行测试体系。

---

## 8. gork 启动 P3 的检查清单

1. 读取本文件 + 最新 `state/product_state.json`
2. 确认 P2-BATCH-3 状态；未完成则**先并行 background 清障**
3. 用机器校准当前 boot/smoke 错误基线，写入 Error Budget
4. 生成 P3 Task DAG（显式 Dependencies，空则并行）
5. **立即 background 并行启动**所有 READY 且无依赖的 Task
6. 监控、集成、失败重试（连续失败 ≥2 且非环境问题 → 请 gpt 会诊）
7. A–E 最小可用后启动 P3-F
8. P3-G 收口，更新 product_state，中文同步 GitHub
9. 工作区清理

**禁止：** 串行排队本可并行的 P3 工作流；禁止在未完成 P2-BATCH-3 时宣称「世界已可进入」。
