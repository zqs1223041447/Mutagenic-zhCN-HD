# PACKAGE_MANIFEST.md — Lean v3 包说明

## 1. 定位

本包是对原 `Mutagenic_AI_GOAL_Final_v2_20260821` 的**精简重构**。

它废止此前作为执行权威的：
- 多份旧 Master Plan
- 多版 GOAL Handoff
- Final v2 完整包中的绝大多数专题文档

历史文件可以作为参考，但**不得进入本地 AI 当前启动必读链**。

仓库内 `docs/` 只保留可复用对照与只读证据。分类：`docs/README.md`。旧入口与实施合同已删除。

## 2. 唯一根入口

```text
AGENT.MD
```

## 3. 文件清单（Lean v3）

| 文件 | 职责 |
|------|------|
| `AGENT.MD` | 唯一根执行协议（目标、锁定决议、当前 Gate、gork/AGY/opencode/gpt 调度规则、工作区卫生、人类边界） |
| `START_HERE.md` | 启动指针 |
| `PRODUCT_CONTRACT.md` | 产品北极星、系统关系、Item/Endgame 哲学、参考边界 |
| `GATES_AND_MIGRATION.md` | 高阶路线 + P1-WAVE-A 详细任务与验收标准 |
| `OPERATING_MODEL.md` | 多 Agent 调度（gork 主控）、Task 格式、Git 规则、工作区结构、简化 Retention、Batch 收口 |
| `SYSTEM_PROMPT.md` | gork 启动指令（含 Worker 优先级） |
| `AGENTS.md` | 兼容入口 |
| `PACKAGE_MANIFEST.md` | 本文件 |

## 4. 相比 v2 的主要变化

**删除 / 大幅压缩：**
- 完整 8 级 Retention Class + 详细清理流程
- 完整目录 Taxonomy（180+ 行）
- Document Evidence Lifecycle 独立文档
- Machine Maintenance Automation 详细规范
- Art / Audio / Visual / Performance 详细文档
- Itemization / Skills / Monsters / Map / Atlas 详细设计
- PoEDB & Compliance 独立文档
- QA / Telemetry / CI 完整基线文档
- Task Preflight / Handoff / Failure Recovery 独立长文
- Adoption Self-Check 独立文档
- 大量重复的 USER_LOCKED 与环境事实描述

**保留并强化：**
- 0 人工代码目标与人类介入边界
- Godot 4.7.1 单主线 + Legacy 只读
- P1-WAVE-A 具体任务与验收
- 产品不可退化约束
- 工作区必须保持干净
- Canonical 文档原位更新原则

**新增：**
- 明确的 Current Priorities & Non-Goals（防止自己再次臃肿）
- 更清晰的“平台建设永远服务于游戏进度”
- 本包自身也必须遵守文档卫生规则
- **本地 Agent 调度模型**：主 AGENT 为 gork；优先用 AGY（gemini cli）干活，额度不足切换 opencode；疑难杂症调用 gpt 专家会诊

## 5. 使用原则

- 启动只读最小集
- 机器状态优先
- 先推进可玩迁移，不提前建设没有明确收益的大型平台
- 本包若未来需要扩展，优先在现有文件中更新，而不是再拆出新的专题文档

## 6. 版本

- Lean v3.1（补充本地 Agent 技能路由）
- 基于 2026-08-21 原 Final v2 重构 + 用户补充的 AGY / opencode / gpt 技能调度要求
- 目标：更少文档、更高信号、更贴合当前 P1 阶段，并明确 gork 如何调度现有技能
