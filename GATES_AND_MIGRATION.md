# GATES_AND_MIGRATION.md — 路线图与迁移状态（Lean v3.2）

## 1. 高阶路线

```text
P0 Repository Closure
→ P1 Godot 4.7.1 Migration          ✅ DONE（Waves A–N）
→ P2 Minimal AI Autonomous Loop     ← 当前收尾
→ P3 Playable Baseline              ← 下一核心
→ P4 Visual / Density / Combat Feel
→ P5 Systems Depth
→ P6 Atlas / Endgame
→ Release Candidate → Public Release
```

以 Gate 驱动，不以固定日期强推。详细框架见 `DEVELOPMENT_PLAN_FRAMEWORK.md`。

## 2. P1 完成摘要

P1-WAVE-A 至 P1-WAVE-N 全部完成：
- Conversion Seed、Compatibility Inventory、Toolchain、Preservation Contracts
- Boot / Project / Autoload / Input
- Menu / Character / Save
- World / Spawn / Movement / Dash
- Combat / Projectile / Status
- Mob / AI 基础
- Skill 场景 + Skill/Passive UI 基础
- Equipment / Gene 基础
- Levels / Interactables / Environment
- Globals API 残留清理
- 首次 headless boot + 错误大幅收敛
- Shader 与类解析级联收敛（SCRIPT ERROR → 1，shader 错误 → 0）

剩余主要信号：missing_asset（.aseprite 等）属美术管线边界。

## 3. P2 状态

- BATCH-1 DONE：Steam 层简化（USE_STEAM=false 永久）、boot 基线、冒烟三跳 SMOKE_PASS
- BATCH-2 DONE：TestLevel runtime Nil 收敛
- 继续方向：运行时错误进一步收敛、取证 bundle 标准化、product_runtime_ready 推进、为 P3 准备自动化 harness

## 4. P3 Playable Baseline（目标定义）

```text
进入角色 → 进入世界 → 移动+Dash → 释放技能 → 击杀怪物
→ 拾取装备 → 打开技能/被动界面 → 保存/读取
```

上述流程必须可被自动化测试覆盖。

**执行权威：`P3_PLAYABLE_BASELINE.md`**（含工作流拆分、Acceptance、Batch 顺序、前置 P2-BATCH-3）。

## 5. 迁移原则（持续有效）

- 迁移不是长期双轨兼容工程
- Legacy 只允许：行为与数值对照、数据和资源参考、旧存档/构建取证、必要 forensic rebuild、迁移兼容验证
- Legacy 禁止：新增 Product Gameplay、新系统长期双实现、为 3.5.3 扩建长期产品基础设施
- 输入边界只读：`03_raw/`、`04_recovered/`、`status.json`、`releases/`、`docs/ai/audits/`

## 6. 并行执行提醒

所有无依赖的后续 Task **必须并行**，Worker **必须 background 模式**。见 `AGENT.MD` 第 6 节。
