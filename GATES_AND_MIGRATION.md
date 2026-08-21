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

后续子系统（本波不做）：Menu / Character / Save → World / Movement → Combat → Skill/Passive → Equipment → VFX/Audio

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
