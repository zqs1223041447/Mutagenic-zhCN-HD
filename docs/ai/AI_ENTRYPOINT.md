# AI 工作入口与任务路由（AI_ENTRYPOINT）

> **角色**：所有 AI 新任务的统一入口。开始任何工作前固定读取：`AGENTS.md` → `status.json` → 本文件 → 任务对应 workflow。

---

## 1. 任务路由表

| 用户请求 | 路由 | 构建路径 |
|---|---|---|
| 汉化更多内容 | `mods/localization/` + `translation/glossary` | canonical build |
| 自定义 MOD（数值/技能/怪物等） | 手工 `mods/custom/<id>/mod.json` 或 NL2MOD | canonical build |
| 自然语言 MOD 需求/未确定参数 | 按需加载 `nl2mod-requirement-analysis` | 确认后 canonical build |
| Kinetic Arcane / 战斗手感 / Player Response / Dash / Hit Reaction / Enemy Reaction / Kill Feel / Combat Camera / Combat Audio / Build Density | `docs/requirements/KINETIC_ARCANE_REMASTER.md` + `docs/requirements/COMBAT_VERTICAL_SLICE.md` | C0 → 独立 gameplay MOD → S0/S1/S2/S4 → Combat S5 |
| 并行批次 / X1、X2、X3… / 多 AI 认领 | `docs/ai/PARALLEL_BATCH_WORKFLOW.md` + 当前 batch 文档 | 独立 worktree/branch → 各自验证 → 中央集成 |
| Runtime bug | canonical candidate → VM 验证 | deploy+verify |
| 管线 bug | `scripts/pipeline/` | 修管线，不动输入 |
| VM/工具链 bug | `scripts/vm/` + Hyper-V skill | VM 运维 |
| 存档/持久化问题 | 对应 localization/persistence workflow | canonical build |
| 构建/编译/打包慢 · 性能优化 · FAST/RELEASE | `docs/build/COMPILE_PERFORMANCE_PLAN.md`（L2 构建性能权威，AGENTS.md §6.1 仅入口；**编译时必读**） | `FAST`(dev) / `RELEASE`(promotion) 双模式；按 `Timing→Cache→Worker/Queue→Attestation/Index→Batching/Staging→FAST/RELEASE→pck-patch` 顺序实现 |

---

## 2. 关键权威速查

| 问题 | 看哪里 |
|---|---|
| 禁止行为 | `AGENTS.md` |
| 当前版本/状态 | `status.json` |
| 人类可读状态 | `PROJECT_STATE.md`（生成视图） |
| 原始/恢复来源 | `manifests/provenance/*` + tracked `03_raw/04_recovered` |
| 如何构建 | `docs/architecture/PIPELINE.md` + `scripts/build/` + `scripts/pipeline/` |
| 构建性能如何优化 | `docs/build/COMPILE_PERFORMANCE_PLAN.md`（AGENTS.md §6.1 入口；编译时必读，含 --mode fast/release、缓存、worker、staging 全规范） |
| Kinetic Arcane 总方向 | `docs/requirements/KINETIC_ARCANE_REMASTER.md` |
| Combat Vertical Slice | `docs/requirements/COMBAT_VERTICAL_SLICE.md` |
| 多 Agent 并发/交接/集成 | `docs/ai/PARALLEL_BATCH_WORKFLOW.md` |
| 如何跑游戏/验证 | `docs/dev-environment/VM_DEVELOPMENT.md` + Hyper-V skill |
| baseline | `status.json` trusted_baselines + `releases/*.json` |
| archive | 本地配置的 archive root；仓库不得假设宿主绝对路径 |

---

## 3. Mandatory Preflight

1. 读取 `AGENTS.md`、`status.json`、本文件。
2. 动态解析当前 clone 的 `repo_root`，优先 `git rev-parse --show-toplevel`。
3. 确认目标资产分类与写入边界。
4. `03_raw/04_recovered` 已随仓库 clone 提供，但仍是不可变 Recovered Provenance，只读使用；`00_original` 仍是本地外部版权资产。
5. 若任务已有目标 MOD，确认真实 `preimage_sha256` 与 `expected_occurrences`；C0 阶段不得为了满足格式而猜 preimage。
6. 确认任务 branch/worktree 与回滚路径。
7. Kinetic 任务继续读取两份 requirements；并行批次继续读取 `PARALLEL_BATCH_WORKFLOW.md` 和当前 batch 文档。
8. 不同 Xi 禁止共享同一个可写 working tree。

---

## 4. 构建/验证最小入口

> **编译性能渐进式披露**：本节仅最小入口。凡涉及 `compile / pack / PCK / embed / verify` 耗时或改动 `scripts/build/*.py`，必须先读 `docs/build/COMPILE_PERFORMANCE_PLAN.md` 再执行（见 AGENTS.md §6.1）。

所有脚本必须自己解析 repo root，调用者不应硬编码宿主绝对路径。

```powershell
python scripts/nlmod/build_mod.py --mod-id <id>
python scripts/probe_boot.py <candidate> --seconds 15
# 性能双模式（见 docs/build/COMPILE_PERFORMANCE_PLAN.md §9）
python scripts/nlmod/build_mod.py --mod-id <id> --mode fast      # 日常迭代，默认；NOT PROMOTION ELIGIBLE
python scripts/nlmod/build_mod.py --mod-id <id> --mode release   # Promotion/baseline，必须；fresh + 3744/3744 verify
```

手工 canonical 顺序仍为：resolve → apply → compile → pack → fresh embed → candidate → verify。
性能优化后顺序不变，但 `FAST` 允许缓存/复用/增量 staging，`RELEASE` 保持全量 fail-closed（详见 performance plan §1–§11）。

`03_raw/04_recovered` 现在可直接从 clone 中读取真实内容与 preimage；真正 Candidate 的 fresh embed、boot、S4/S5 仍需要本地 `00_original`、工具链与运行/VM 环境。

---

## 5. 工作区与路径规则

### 5.1 当前 clone 就是工程根

- 当前用户实际 clone 的仓库是开发根，不绑定任何固定盘符、用户名或历史目录。
- `03_raw/04_recovered` 已在 Git 中，禁止再建立外部 recovered junction 作为默认方案。
- `00_original`、VM、archive、外部工具链等通过本地忽略配置、环境变量、CLI 参数或工具发现注入。
- 如果主工作树已有用户未提交改动，AI 不得 reset、clean、覆盖或静默纳入任务提交。

### 5.2 并行开发隔离

- 用户只 clone 一次仓库。
- 每个 Xi 使用独立 branch + Git worktree。
- worktree 路径由自动化从 `repo_root` 推导，例如 `<repo_parent>/<repo_name>.worktrees/<batch>/<task>`；这只是逻辑布局，不是固定绝对路径。
- 执行 Agent 必须在自己的 task worktree 中运行，不得把所有 Agent 都以主 `repo_root` 作为 `--dir` 启动。
- 已成功集成的 worktree 可自动清理；未合并或失败任务保留 branch/evidence。

---

## 6. Kinetic Arcane / Combat Remaster 专用路由

### 6.1 必读顺序

1. `AGENTS.md`
2. `status.json`
3. 本文件
4. `docs/requirements/KINETIC_ARCANE_REMASTER.md`
5. `docs/requirements/COMBAT_VERTICAL_SLICE.md`
6. 实际 pipeline / VM workflow

### 6.2 第一原则

**Player Response → Gameplay Readability → Interaction Clarity → Impact → Visual Hierarchy → Consistency → Modern Appearance → Decoration**

禁止用“全局大幅提速”“每 hit 震屏/Hit Stop”“满屏 Bloom”替代真实响应和因果反馈。

### 6.3 执行顺序

1. 只读审计 tracked `04_recovered` 中真实源码/节点；
2. 完成 C0 Experience Audit：SHA、old_text/preimage、调用入口、事件频率、风险、现有 MOD 冲突；
3. 拆成职责单一、可回滚的声明式 gameplay MOD；
4. canonical build；
5. S0 / S1 / S2 / S4；
6. 同一代表性场景 BEFORE / AFTER Combat S5；
7. 未完成对应验证前不得把 Candidate 写成 PASS，不修改 `status.json` 冒充完成。

### 6.4 GitHub Connector 环境边界

由于 `03_raw/04_recovered` 已入库，GitHub 侧 AI **可以读取真实 recovered 源码、计算/审查 preimage、检查调用链和生成声明式 patch**；不再使用“GitHub 不含 recovered”这一旧前提。

但 GitHub 侧仍不能仅凭仓库证明：

- fresh embed Candidate 已生成；
- boot/FPS 已通过；
- VM S4/S5 已通过；
- 最终主观手感已验收。

这些必须由具备本地 `00_original` 与运行环境的执行 Agent 留证。

### 6.5 协作分支

Kinetic Arcane 远端集成线：

`agent/kinetic-arcane-remaster-foundation`

执行 Xi 使用独立临时 branch；最终合并顺序由协调 AI 决定。

---

## 7. 并行批次 / 无人值守专用路由

当用户要求“一大批进展”“长期不在电脑前”“多 Agent 并发”时，默认批次模式。

每个 Xi 默认授权覆盖：

**CLAIM → PREFLIGHT → AUDIT → IMPLEMENT → BUILD → VERIFY → FIX/RETRY → COMMIT → PUSH → HANDOFF**

普通实现选择、测试失败、构建失败、可恢复依赖问题不应立刻等待用户；Agent 应在任务范围内自行修复并推进。

### 7.1 交接合同

每个 Xi 返回至少：

- `task_id`
- `branch`
- `base_sha`
- `final_sha`
- 修改文件/路径
- MOD/脚本/测试产物
- Candidate Build ID（若适用）
- S0/S1/S2/S4/S5 状态
- 自动重试/失败摘要
- 潜在冲突路径
- 剩余风险
- 推荐集成顺序/依赖

### 7.2 中央集成

所有 Xi 完成后，协调 AI 负责：

1. 校验 branch/commit 与 base；
2. 检查越界、absolute-path、secret、preimage 漂移；
3. 分析文件/语义冲突；
4. 决定 merge/rebase/cherry-pick 顺序；
5. 建立 aggregate candidate；
6. 跑完整回归；
7. 更新 Draft PR 与当前现状；
8. 编排下一批。

### 7.3 人类操作目标

正常情况下用户只需要：

1. 首次 clone 仓库，并配置本地 `00_original`/工具/VM；
2. 把协调 AI 给出的 Xi 任务 ID 交给执行 AI，或启动批次控制器；
3. 批次结束后把 branch/SHA/handoff 交回协调 AI。

不要求用户手工建 worktree、计算绝对路径、逐项跑测试、整理 diff 或决定合并顺序。

---

## 8. 自动化基础设施优先级

批次控制器至少应提供：

- repo root / path portability 全仓扫描；
- 一键 task worktree/branch claim；
- task status / handoff / cleanup；
- batch collect；
- integration preflight；
- secret scan + absolute-path scan；
- 无交互构建/验证包装；
- 失败重试与结构化日志。

**关键约束**：批次控制器启动执行 Agent 时必须传入各自 task worktree，而不是统一传主 `repo_root`。