# docs/ — 文档分类

当前执行权威不在本目录。启动只读：

1. `AGENT.MD`
2. `state/product_state.json`
3. `START_HERE.md`
4. `PRODUCT_CONTRACT.md`
5. `GATES_AND_MIGRATION.md`

本目录只放 **Legacy 对照、工具说明、历史摘要、只读证据**。不得当作任务入口或 Product Gate。

Godot **4.7.1** 是唯一 Product 引擎。Godot **3.5.3** 只读参考。禁止再给 3.5.3 认领批次、继续汉化主线、或把「禁止升级 Godot 4」写回任务。

---

## 保留（可复用，正文已按当前主线改过）

| 路径 | 用途 |
|---|---|
| `docs/ai/source-map.md` + `source_index.json` | 定位 `04_recovered` 里 525 个 `.gd`；P1 扫描用 |
| `docs/ai/scene-resource-map.md` | 场景/资源对照。本 clone **没有** `05_schema/game_schema.json`，文中 schema SHA 无法就地复核 |
| `docs/ai/audits/**` | **只读证据**。禁止改写 PASS/FAIL |
| `docs/ai/batches/B1_STATUS.md` `B2_STATUS.md` `B3_STATUS.md` | Legacy 批次已完成事实。不是待办 |
| `docs/ai/batchctl.md` | 旧 `batchctl` CLI。禁止用来认领 B1/B2/B3 |
| `docs/ai/B1-X5_COMBAT_HARNESS.md` | Legacy 3.5.3 harness 怎么跑。不是 Product 测试入口 |
| `docs/ai/B2-X2_S5_EVIDENCE.md` | Legacy S5 证据工具。人工体验结论不得由机器代写 |
| `docs/architecture/PIPELINE.md` | 3.5.3 声明式 MOD → embed 取证管线。**不是** Godot 4 Product 构建路径 |
| `docs/build/README.md` | `scripts/build/` 是 Legacy 编译脚本索引。不为 3.5.3 继续做性能平台 |
| `docs/DEPLOYMENT.md` | clone / 私资产 / 目录事实 |
| `docs/dev-environment/QUICKSTART_FRESH_CLONE.md` | bootstrap / doctor。L3 不阻塞 P1 |
| `docs/requirements/PHASE0_VISUAL_AUDIT.md` | 2026-08-16 对 3.5.3 视觉的只读事实。不是实施合同 |
| `docs/requirements/KINETIC_ARCANE_REMASTER.md` | 远期战斗体验意图（P4+）。当前不实施 |
| `docs/zh_CN_glossary.md` | zh_CN 术语对照。迁移时防译名漂移，不启动新汉化批次 |
| `data/poedb/` | 外部机制参考，不是游戏实现 |

---

## 已删除（无复用 / 会错引）

旧 AI 入口、并行批次合同、NL2MOD 指南、二次开发指引、B1/B2/B3 认领计划、HD/PHASE 1–6 实施规格、Combat Slice 合同、2026-08-13「最终报告」、汉化 workflow、VM/宿主手册、8 级证据策略、20 章 3.5.3 编译性能方案、Godot 3.x Mod SDK 研究报告。

证据仍在 `docs/ai/audits/`、`status.json`、`releases/`。
