# AI_ENTRYPOINT — Mutagenic Product 开发入口

> 新 AI 会话不要依赖旧聊天。固定读取：`AGENTS.md` → `state/product_state.json` → 本文件 → Master Plan/任务文件。

## 当前总方向

产品开发已经统一到 **Godot 4.7.1 stable**。Godot 3.5.3 仅作为 `03_raw/04_recovered/status/releases` 的 Legacy Reference，不再继续新增产品功能。

## Fresh Clone

先执行：`docs/dev-environment/QUICKSTART_FRESH_CLONE.md`。

必须显式 clone：

```powershell
git clone --branch agent/kinetic-arcane-remaster-foundation --single-branch https://github.com/zqs1223041447/Mutagenic-zhCN-HD.git
cd Mutagenic-zhCN-HD
python scripts/bootstrap/product_doctor.py
```

`product_doctor.py` 不要求 Legacy 私有 EXE；它只判断 Product 仓库/分支/Python/Godot 4.7.1 工具链状态。

## 当前路由

| 目标 | 入口 |
|---|---|
| 当前阶段/下一批 | `state/product_state.json` |
| 总计划 | `docs/ai/master-plan/2026-08-21/00_README.md` |
| Godot 4.7.1 迁移 | `docs/ai/master-plan/2026-08-21/03_GODOT_4_7_1_MIGRATION.md` |
| 多 Agent / batchctl | `docs/ai/master-plan/2026-08-21/04_AUTONOMOUS_AGENT_CONTROL_PLANE.md` |
| Gameplay 架构 | `docs/ai/master-plan/2026-08-21/05_GAMEPLAY_ARCHITECTURE.md` |
| 装备/技能/怪物/终局 | `docs/ai/master-plan/2026-08-21/06_ITEM_SKILL_MONSTER_ENDGAME.md` |
| 美术/性能 | `docs/ai/master-plan/2026-08-21/07_ART_VISUAL_AUDIO_PERFORMANCE.md` |
| QA/CI/Release | `docs/ai/master-plan/2026-08-21/08_QA_CI_RELEASE.md` |
| Git/worktree | `docs/ai/master-plan/2026-08-21/09_GITHUB_WORKTREE_WORKFLOW.md` |
| 下一批 | `docs/ai/master-plan/2026-08-21/10_GATE_ROADMAP_NEXT_BATCH.md` |
| Legacy 历史事实 | `status.json` + `releases/*.json` + `docs/ai/audits/**` |

## Mandatory Preflight

1. 确认当前 branch/worktree/dirty state。
2. 读取 Product state 的 phase、gate、next_batch。
3. 不写 `00_original/03_raw/04_recovered`。
4. 不提交秘密和宿主绝对路径。
5. Worker 只写自己的任务分支；Coordinator 才能集成固定中央分支。
6. 每个任务交付必须包含：变更、测试、证据、未证明、风险、下一步。

## 当前禁止事项

- 不继续为 Godot 3.5.3 新增 Gameplay。
- 不为了“兼容双轨”复制一套 Product 逻辑回 Legacy。
- 不先建设 SQLite/复杂数据湖/复杂 Release 工厂再开始迁移。
- 不默认用网页自动化批量抓取 POE/PoEDB。
- 不把 MCP 输出当作唯一事实；CLI/测试/运行证据优先。