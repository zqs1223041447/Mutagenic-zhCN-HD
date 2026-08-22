# DEVELOPMENT_PLAN_FRAMEWORK.md — 从研制到发布的开发计划框架

> Gate 驱动。不以固定日期强推。  
> 所有无依赖任务**必须并行**，Worker **必须使用 background 模式**。  
> 本文件与 `AGENT.MD`、`GATES_AND_MIGRATION.md` 配套使用。

---

## 0. 当前起点（2026-08-21 晚间校准）

| 项目 | 状态 |
|------|------|
| P1 Godot 4.7.1 Migration（Waves A–N） | **DONE**（静态迁移主体收敛） |
| P2-BATCH-1 | **DONE**（Steam 层简化 + boot 基线 + 冒烟三跳 SMOKE_PASS） |
| P2-BATCH-2 | **DONE**（TestLevel runtime Nil 收敛） |
| product_runtime_ready | false（继续推进） |
| LEVEL_3_FULL_VALIDATION | PASS |
| 剩余主要信号 | missing_asset ≈256（.aseprite 等，美术边界）；运行时错误持续收敛中 |
| Steam 真接入 | **永久删除**（USE_STEAM=false 最终形态） |

**当前工作焦点：完成 P2 稳定化 → 进入并完成 P3 Playable Baseline。**

---

## 1. 总体 Gate 路线（研制 → 发布）

```text
P1 Migration                    ✅ 已完成
    ↓
P2 Minimal AI Autonomous Loop   ← 当前
    ↓
P3 Playable Baseline            ← 下一核心目标
    ↓
P4 Visual / Density / Combat Feel
    ↓
P5 Systems Depth（Skill/Item/Monster/Map）
    ↓
P6 Atlas / Endgame
    ↓
Release Candidate
    ↓
Public Release（需人类授权）
```

每个 Gate 必须具备：
- 清晰的 Acceptance Criteria（可机器验证优先）
- Evidence 要求
- 明确的 Parallelizable 任务拆分
- 退出条件（Exit Criteria）

---

## 2. P2 Minimal AI Autonomous Loop（当前收尾）

**目标：** 建立可重复的「boot probe → 冒烟跳转 → 取证 bundle → 状态回写」闭环，并让 product_runtime_ready 趋向 true。

**建议并行批次方向：**

| 方向 | 说明 | 可并行 |
|------|------|--------|
| 运行时错误收敛 | 继续降低 headless / smoke 过程中的脚本错误与 Nil 引用 | 是（按错误类别拆） |
| 取证 bundle 标准化 | 固定 Evidence 格式与晋升路径 | 是 |
| missing_asset 分类 | 区分「代码可修 / 需人类提供源 / 可接受替代」 | 是 |
| 状态回写自动化 | product_state 与 GitHub 中文状态同步可靠 | 是 |
| 冒烟扩展 | 在 TestLevel 基础上增加更多稳定跳转点 | 部分依赖 |

**Exit Criteria（建议）：**
- headless boot + 核心冒烟链路可重复通过
- 关键 Evidence 可自动生成并晋升
- product_runtime_ready 可被诚实标记为 true，或明确剩余 BLOCKED 项仅限美术源
- 工作区清理与并行调度已成习惯

**不阻塞项：** .aseprite 源缺失 → 标记 HUMAN_INPUT_REQUIRED 或采用占位/替代后继续。

---

## 3. P3 Playable Baseline（下一核心 Gate）

**完整细化见 `P3_PLAYABLE_BASELINE.md`（执行权威）。**

**定义：** 玩家可完成完整最小循环，且该循环可被自动化测试覆盖。

```text
进入角色 → 进入世界 → 移动+Dash → 释放技能 → 击杀怪物
→ 拾取装备 → 打开技能/被动界面 → 保存/读取
```

**前置：** 必须先完成 **P2-BATCH-3**（BaseLevel tile / TierLoader / audio bus），否则世界进入流仍阻塞。

**并行工作流：**
- P3-A Character/Save
- P3-B World + Movement/Dash（依赖 P2-BATCH-3）
- P3-C Combat Loop
- P3-D Loot/Equipment
- P3-E Skill + Passive UI
- P3-F E2E Automation Harness（依赖 A–E 最小可用）
- P3-G Evidence 晋升与状态收口

**Exit Criteria：** 见 `P3_PLAYABLE_BASELINE.md` 的 E1–E10（含 Error Budget 与 product_runtime_ready）。

---

## 4. P4 Visual / Density / Combat Feel

**目标：** 在现有资产边界内，提升战斗可读性、怪潮密度感、击杀与受击反馈节奏（参考 Halls of Torment 的视觉语言与信息优先级，但不复制资产）。

**并行方向：**
- 轮廓 / 危险信息可读性
- 击杀 / 受击 VFX 节奏
- 摄像机与屏幕反馈
- 性能基线（高密度时的帧时）

**约束：** 不提前建设完整美术生产管线；优先用现有资源 + 程序化/配置手段达成可读性。

---

## 5. P5 Systems Depth

**目标：** 达到「可构筑、有深度」的 Skill / Support / Item / Affix / Monster / Map 系统。

**并行方向（高阶）：**
- Skill + Support 深度与标签交互
- Itemization（Base / Rare / Legendary）与 Affix 权重
- Monster Mods 与精英行为
- Map Mods 与基础 Map Item 流程

保持「External Reference → Mechanism Abstraction → Mutagenic Original Design」流程，不复制受保护内容。

---

## 6. P6 Atlas / Endgame

**目标：**

```text
Map Item → Craft → Consume → Instance → Boss / Drop → Next Map → Atlas
```

支持奖励强化、目标农场、玩家塑造终局路线。

在 P5 系统稳定后再大规模展开。可提前做数据 schema 与最小原型，但不得拖慢 P3/P4。

---

## 7. Release Candidate → Public Release

**Release Candidate 最低条件（建议）：**
- P3 全自动可验证
- 核心系统在 P5 达到可玩深度
- 无阻断级崩溃与数据损坏
- 存档兼容策略明确
- 性能在目标配置下可接受
- Evidence 与版本指纹完整

**Public Release：** 必须获得人类明确授权。AI 不得自行发布。

---

## 8. 跨 Gate 强制执行规则

1. **并行默认 + Background 强制**  
   所有无依赖 Task 必须并行派发，Worker 必须 background 模式运行。见 `AGENT.MD` 第 6 节。

2. **Evidence 优先于文档**  
   每个 Gate 的完成以机器可复查 Evidence 为准，而不是长篇报告。

3. **美术边界不阻塞玩法**  
   missing_asset 中属于源文件缺失的，单独标记，不阻止 P3 闭环推进。

4. **平台服务于进度**  
   不为「更完美的 AI 平台」而推迟可玩基线。

5. **人类只处理真正需要人类的事**  
   见 `AGENT.MD` 第 9 节。普通工程问题全部由 gork + AGY/opencode 闭环。

6. **状态单一真相源**  
   `state/product_state.json` 是当前权威。Legacy status.json / PROJECT_STATE.md 仅作历史参考。

---

## 9. 建议的近期行动顺序（给 gork）

1. 校准最新 `product_state.json` 与 HEAD。
2. 识别 P2 剩余可并行收敛项（错误分类、Evidence 标准化、可代码修复的 missing_asset）。
3. **立即以 background 模式并行启动** 所有无依赖 READY Task。
4. 同时准备 P3 的 Task DAG 草案（角色/世界/战斗/拾取/UI/存档/自动化）。
5. 每个 Batch 收口后更新状态、清理工作区、中文同步 GitHub、生成下一批。

**禁止串行排队本可并行的工作。禁止输出「请告诉我下一步」。**
