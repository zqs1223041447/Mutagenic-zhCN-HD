# PACKAGE_MANIFEST.md — Lean v3.2 + P3 细化 包说明

## 1. 定位

本包是对原 Final v2 / Lean v3 / 仓库当前 AGENT 的**再校准与强化**。

它反映：
- 仓库实际进度（P1 完成，P2 收尾，准备 P3）
- 强制并行开发
- 子 Agent / Worker 必须使用 background 模式
- 从当前研制阶段到 Public Release 的完整 Gate 框架

历史文件可以作为参考，但**不得进入本地 AI 当前启动必读链**。

## 2. 唯一根入口

```text
AGENT.MD
```

## 3. 文件清单（Lean v3.2 + P3 细化）

| 文件 | 职责 |
|------|------|
| `AGENT.MD` | 唯一根执行协议（含强制并行 + background、当前状态、Gate 摘要） |
| `START_HERE.md` | 启动指针 |
| `PRODUCT_CONTRACT.md` | 产品北极星、系统关系、Item/Endgame 哲学、参考边界 |
| `GATES_AND_MIGRATION.md` | 高阶路线与迁移历史 |
| `DEVELOPMENT_PLAN_FRAMEWORK.md` | 从研制到发布的完整开发计划框架 |
| `P3_PLAYABLE_BASELINE.md` | **P3 Playable Baseline 详细执行计划（工作流/验收/Batch）** |
| `OPERATING_MODEL.md` | 多 Agent 调度（并行 + background）、Task、Git、工作区 |
| `SYSTEM_PROMPT.md` | gork 启动指令 |
| `AGENTS.md` | 兼容入口 |
| `PACKAGE_MANIFEST.md` | 本文件 |

## 4. 相比之前版本的主要变化

- 根据仓库 `state/product_state.json` 更新当前真实进度（P1 DONE，P2 进行中）
- **强制并行开发**：无依赖 Task 默认并行，禁止串行排队
- **强制 background 模式**：所有 Worker Task 必须以 background 启动
- 新增 `DEVELOPMENT_PLAN_FRAMEWORK.md`，覆盖 P2 收尾 → P3 → P4 → P5 → P6 → Release
- 明确 Steam 真接入已永久删除
- 美术缺失不阻塞玩法闭环的原则写清

## 5. 使用原则

- 启动只读最小集
- 机器状态优先
- 先推进可玩基线，不提前建设没有明确收益的大型平台
- 本包若未来需要扩展，优先在现有文件中更新

## 6. 版本

- Lean v3.2 + P3 细化
- 基于仓库 2026-08-21 实际进度 + 用户对并行/background 的强制要求
- 目标：贴合现状、强制并行、从研制到发布有清晰框架
