# GATES_AND_MIGRATION.md — 路线图与当前迁移任务

## 1. 高阶路线

```text
P0 Repository Closure
→ P1 Godot 4.7.1 Migration
→ P2 Minimal AI Autonomous Loop
→ P3 Playable Baseline
→ P4 Halls-style Visual / Density / Combat Presentation
→ P5 POE-like Skill / Equipment / Affix / Monster / Map Depth
→ P6 Atlas / Endgame
→ Continuous AI-driven Content Expansion
```

以 Gate 驱动，不以固定日期强推。

## 2. 当前工作假设

- 环境 L0/L1 已具备，L3 未闭环
- P1 Wave A 与 L3 closure **并行**
- 不为补 L3 去继续扩建 Legacy gameplay pipeline

## 3. P1-WAVE-A（当前第一批）

### P1-X0 — Conversion Seed

**Goal**  
建立 `product/` Godot 4.7.1 seed 和第一份可复查 conversion/import 证据。

**Allowed**  
- `product/**`
- `migration/conversion/**`
- 相关 test/tool config

**Forbidden**  
- 直接修改 `03_raw/**`
- 直接修改 `04_recovered/**`
- 新增远期 Gameplay

**Acceptance**  
- `project.godot` 明确 Godot 4
- Godot 4.7.1 可识别工程
- import/parse 结果机器可读
- 错误被分类（不要求零错误才算完成）
- 生成 migration seed report

### P1-X1 — Compatibility Inventory

**Goal**  
输出完整的 3.5.3 → 4.7.1 incompatibility inventory。

**Acceptance**  
- 扫描 Script / Scene / Resource / Settings
- 每个 blocker 有 category / path / severity / dependency
- 能生成 blocker DAG
- 可重复运行
- 不得修改 immutable source

### P1-X2 — Product Toolchain Closure

**Goal**  
建立 Product doctor + Godot 4.7.1 headless canonical invocation。

**Acceptance**  
- discovery 不依赖宿主绝对路径
- version 验证
- machine-readable result
- 最小 CI job
- private assets 缺失和真实 tool failure 分类明确

### P1-X3 — Preservation Contracts

**Goal**  
把迁移不可静默丢失的事实机器化。

**Acceptance**  
至少覆盖：
- Classes / Specializations
- Skills / Supports
- Passive / Keystones
- Stats / Tags
- Equipment slots/data
- input actions
- save keys/schema facts
- combat-critical IDs

数量必须从实际源扫描产生，而不是直接相信文档中的约数。

### LEVEL_3-C0 — 并行 Closure

与 P1-X0..X3 并行：
- abs path
- secret
- bootstrap contracts
- ci discovery
- full validation readiness

## 4. Wave A 收口标准

所有可完成 Task handoff 后：
- Coordinator 统一 Review
- 集成
- Product CI
- Evidence promotion
- workspace cleanup
- 生成 Wave B

P1-X0..X3 已完成。Godot 4.7.1 二进制为 DOWNLOADABLE_TOOL：本地 `02_tools/godot/`（gitignore）+ `scripts/bootstrap/fetch_godot.py`。缺失时 discovery 仍是 `NOT_FOUND`，不得改写成 PASS。

## 5. P1-WAVE-B（当前批次）— Boot / Project / Autoload / Input

按子系统推进，不按随机文件拆。

### P1-B0 — Project Settings + Input Map

**Allowed:** `product/project.godot`, `scripts/migration/boot_convert.py`, `migration/conversion/**`, tests

**Forbidden:** `03_raw/**`, `04_recovered/**`, 新增 Gameplay

**Acceptance:**
- `config_version=5` 且 features 含 4.7
- 保留 dash / interact / move_* 等 input actions
- Godot 3 `Object(InputEvent*)` 转为 Godot 4 字段（scancode→keycode 等）
- 机器可读 report

### P1-B1 — Autoload registry + Globals 机械转换

**Acceptance:**
- recovered `[autoload]` 全部登记到 Product
- `04_recovered/Globals/**` 复制并机械转换为 Godot 4 GDScript
- JSON 数据目录一并复制（passive_tree_data / skillgen / world_map_data）
- recovered 指纹不变
- 残留 File/Directory/yield 等记入 residuals，不假装已 100% 语义正确

### P1-B2 — Headless import / parse 证据

**Acceptance:**
- 有 Godot 4.7.1 时 `--import --quit` 必须 RAN
- 错误分类（缺 preload 场景/音效是预期，zero errors 不是本波要求）
- 无引擎时 `NOT_RUN` / `NOT_FOUND`，不得改写成 PASS

### LEVEL_3-C0（并行）

- releases/*.json 按 provenance 分类（历史证据，不是 production_hardcode）
- secret 扫描去掉 log-word / f-string 误报；真 secret 仍 FAIL
- bootstrap.cmd / doctor.cmd / fetch_godot / CI discovery
- 不得把仍存在的 production_hardcode 或真 secret 改写成 PASS

## 5b. P1-WAVE-C（当前批次）— Menu / Character / Save

**Allowed:** `product/Scenes/**`（菜单/角色选择/存档弹窗及其直接依赖）、`product/Themes/**`、`product/Fonts/**`、`product/sprites/splash/**`、`product/sprites/gui/**`、`product/Sounds/UI/**`、`scripts/migration/menu_convert.py`、`migration/conversion/**`、tests、`product/project.godot` 的 `run/main_scene` 行

**Forbidden:** `03_raw/**`、`04_recovered/**`、战斗/关卡/怪物子系统、新增 Gameplay

**Acceptance:**
- `Scenes/LoadGame.tscn` + `Scenes/Menu.tscn` + CharacterSelect 在 product 中且 scene format=3
- `run/main_scene` 指向 `res://scenes/LoadGame.tscn`
- LoadGame.gd 使用 Godot 4 刷新率/物理 tick API
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求

## 5c. P1-WAVE-D（已完成）— World / Spawn / Movement

**Allowed:** `product/scenes/World.*`、`product/scenes/Player/**`、`product/scenes/Levels/**`（Default/Spawn/NavMesh/Loader）、`product/scenes/GUI/**`、`product/scenes/Stats.*`、`product/scenes/Popups/EscapeMenu.*`、`product/Tilesets/**`、`product/Shaders/**`、`scripts/migration/world_convert.py`、tests、evidence

**Forbidden:** `03_raw/**`、`04_recovered/**`、Skills/Projectiles/Mobs 全量子系统、新增 Gameplay

**Acceptance:**
- World/Player/BaseLevel/SpawnLocation/DefaultLevel 在 product 且 scene format=3
- Player 保留 dash（`apply_central_impulse` + input action `dash`）
- YSort → Node2D + `y_sort_enabled`
- `run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 import RAN；错误分类；zero errors 不是本波要求

## 5d. P1-WAVE-E（已完成）— Combat / Projectile / Status

**Allowed:** `product/scenes/Skills/GenericSkill.*`、`product/scenes/Projectiles/**`、`product/scenes/StatusEffects/**`、`product/scenes/AreaInstantDamageApplier/**`、`product/scenes/ShaderExplosions/**`、`scripts/migration/combat_convert.py`、tests、`migration/conversion/wave_e_combat_report.json`

**Forbidden:** `03_raw/**`、`04_recovered/**`、Mobs/Levels/Player 全量重写、World 全量重写、GeneEditor/PassiveTree 全量系统、新增 Gameplay

**Acceptance:**
- GenericSkill.gd、Projectile.tscn/gd、BaseEffect.gd、Generic Status Effects 在 product 且 scene format=3 / GDScript 4 语法转换
- Player 保留 dash（`apply_central_impulse` + `dash`）
- `run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求

后续子系统（本波不做）：Mob AI → Skill/Passive Tree UI → Equipment → VFX/Audio

## 5e. P1-WAVE-F（已完成）— Mob / AI 基础

**Allowed:** `product/scenes/Mobs/**`（Mob 基础场景/脚本/Stats node）、`scripts/migration/mob_convert.py`、`migration/inventory/wave_f_mobs_inventory.json`、`migration/conversion/wave_f_mob_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、Skills Playable 全量场景、Levels 全量重写、GeneEditor/PassiveTree 全量系统、新增 Gameplay

**Acceptance:**
- Mob.tscn/gd 与 Stats node 在 product 且 scene format=3 / GDScript 4 语法转换
- 机器可读 mobs inventory（从 04_recovered 扫描产生）
- Player 保留 dash（`apply_central_impulse` + `dash`）
- `run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求

执行模式：gork 并行派发 background 子 agent（inventory 扫描 ∥ converter 实现），由 gork 统一集成验证。

## 5f. P1-WAVE-G（已完成）— Skill 场景资源 + Skill/Passive Tree UI 基础

**Allowed:** `product/scenes/Skills/**`（Playable 技能场景）、`product/sprites/skills/**`、SkillTree/PassiveTree UI 场景与脚本、`scripts/migration/skill_convert.py`、`migration/inventory/wave_g_*.json`、`migration/conversion/wave_g_skill_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、Mobs/Levels 全量重写、GeneEditor 全量系统、新增 Gameplay

**Acceptance:**
- Playable 技能场景在 product 且 scene format=3 / GDScript 4 语法转换
- 技能图标 sprites 复制到位，preload 缺失显著下降
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求

后续子系统（本波不做）：Equipment → VFX/Audio → Levels 补全

## 5g. P1-WAVE-H（已完成）— Equipment / Gene 基础

**Allowed:** `product/Globals/Genes/**`、GeneMods 编译链相关脚本修复（机械转换范畴）、Equipment 数据/UI 场景基础、`scripts/migration/equipment_convert.py`、`migration/inventory/wave_h_*.json`、`migration/conversion/wave_h_equipment_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、Levels 全量重写、新增 Gameplay

**Acceptance:**
- GeneMods autoload 编译链 blocker 显著下降（从 "Could not resolve class GeneMods" 级联中恢复）
- Equipment 相关场景/脚本在 product 且 format=3 / GDScript 4
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求
- 错误归因必须区分"新暴露"与"回归"（对比上一波分类计数）

后续子系统（本波不做）：VFX/Audio → Levels 补全 → Steam 替代层

## 5h. P1-WAVE-I（已完成）— Levels 补全 + 剩余世界资源

**Allowed:** `product/scenes/Levels/**`（Hideout/BossArenas/Ladder/TestLevel 等）、`product/Tilesets/**`、`product/sprites/worldmap/**`、`scripts/migration/levels_convert.py`、`migration/inventory/wave_i_*.json`、`migration/conversion/wave_i_levels_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、Mobs/Skills 全量重写、新增 Gameplay

**Acceptance:**
- Hideout/BossArenas 等关卡场景在 product 且 format=3 / GDScript 4
- worldmap/tileset sprites 复制到位，preload 缺失下降
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 有 4.7.1 则 headless import RAN；错误分类；zero errors 不是本波要求
- 错误归因必须区分"新暴露"与"回归"

后续子系统（本波不做）：Steam 替代层（架构决策，需会诊）→ VFX/Audio → Interactables

## 5i. P1-WAVE-J（已完成）— Interactables / Environment 补全

**Allowed:** `product/scenes/Interactables/**`、`product/scenes/Environment/**`、Wave H/I 延后项（GeneEditor 组件、GearBench、Notice、TrainingDummy）、缺失音效资产、`scripts/migration/interactables_convert.py`、`migration/inventory/wave_j_*.json`、`migration/conversion/wave_j_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、Mobs/Skills/Levels 全量重写、新增 Gameplay

**Acceptance:**
- Interactables/Environment 场景在 product 且 format=3 / GDScript 4
- Wave H 延后的 GeneEditor/GearBench/Notice 与 Wave I 关卡依赖（Brazier/TrainingDummy/ambience_boss.ogg）就位
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- headless import 需连续运行两次取第二次为准（新资产 preload 鸡生蛋）
- 错误归因必须区分"新暴露"与"回归"

后续子系统（本波不做）：Steam 替代层（架构决策，需会诊）→ VFX/Audio 收尾

## 5k. P1-WAVE-L（已完成）— 语义残留收尾 + P1-V0 首次启动

**结果：** GameState.gd 8 处语义改写（DisplayServer/DirAccess/Engine.max_fps）；`product_boot_probe.py` 落地；**Product 首次 headless 启动成功**（rc=0，BOOTED_WITH_ERRORS，575 个运行时脚本错误，17.8s）。运行时错误成为主要信号类别。

## 5l. P1-WAVE-M（已完成）— 战斗资产补全与启动错误收敛

**结果：** 15 个资产根批量复制（380 文件）；import blocker 1000→784；boot script errors 575→490。

## 5m. P1-WAVE-N（当前批次）— 着色器与类解析级联收敛

**Allowed:** `product/**` 中 shader 编译错误修复（Godot 4 shader 语法机械转换）、super-class 解析级联修复、api_member 残留（55 处）、`migration/conversion/wave_n_report.json`、tests、boot probe 复跑证据

**Forbidden:** `03_raw/**`、`04_recovered/**`、语义重写、新增 Gameplay、Steam 替代层实现

**Acceptance:**
- boot probe script_error_count 相对 490 基线显著下降
- Shader compilation failed 类错误清零或逐条归类 residuals
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- 错误归因区分"新暴露"与"回归"

后续子系统（本波不做）：Steam 替代层（需会诊）→ .aseprite SpriteFrames（美术管线边界）

## 5j. P1-WAVE-K（已完成）— Globals 脚本 API 残留清理

**Allowed:** `product/Globals/**`、`product/scenes/**` 中机械 API 重命名（OS.*→DisplayServer/Window、Directory→DirAccess、TYPE_REAL→TYPE_FLOAT、ALIGN_RIGHT→HORIZONTAL_ALIGNMENT_RIGHT、rect_size→size、get_screen_refresh_rate 等已迁移脚本的残留项）、`scripts/migration/api_residue_convert.py`、`migration/conversion/wave_k_report.json`、tests

**Forbidden:** `03_raw/**`、`04_recovered/**`、语义重写（只做等价 API 替换）、新增 Gameplay、Steam 替代层实现

**Acceptance:**
- import 报告中 OS/Directory/TYPE_REAL/ALIGN_RIGHT/rect_size 类 parse 错误显著下降
- 每处替换为 Godot 4 等价 API，不做行为变更；无法等价替换的记 residuals 不强改
- Player 保留 dash；`run/main_scene` 仍是 LoadGame
- recovered 指纹不变
- headless import 双次运行取第二次；错误归因区分"新暴露"与"回归"

后续子系统（本波不做）：Steam 替代层（需会诊）→ .aseprite SpriteFrames（需美术管线决策，Non-Goal 边界内暂缓）

## 6. 进入 P2 / P3 的最低条件

**不是“迁移所有功能才进入下一阶段”。**

当满足以下条件即可推进：
- Product 项目可稳定自动运行（headless）
- 多 Agent 控制闭环可以针对 Product 自我验证
- 状态 / 清理 / 集成自动化可用

**P3 Playable Baseline 的粗定义（后续细化）：**
能进入角色 → 进入世界 → 移动 → 释放技能 → 击杀怪物 → 拾取装备 → 打开技能/被动界面 → 保存/读取，且上述流程可被自动化测试覆盖。

## 7. 迁移原则

- 迁移不是长期双轨兼容工程
- Legacy 只允许：行为与数值对照、数据和资源参考、旧存档/构建取证、必要 forensic rebuild、迁移兼容验证
- Legacy 禁止：新增 Product Gameplay、新系统长期双实现、为 3.5.3 扩建长期产品基础设施
- 输入边界只读：`03_raw/`、`04_recovered/`、`status.json`、`releases/`、`docs/ai/audits/`
