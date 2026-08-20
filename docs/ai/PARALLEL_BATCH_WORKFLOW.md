# Parallel Batch Workflow — 多 Agent 无人值守研发

> **角色**：定义协调 AI 如何拆批、执行 AI 如何认领、多个任务如何隔离并行，以及全部完成后如何中央集成。
> **Authority**：L2 执行流程；低于 `AGENTS.md` 与 `status.json`。
> **目标**：用户长期不在电脑前时，每一批仍能产生大块、可验证、可集成的进展，同时把人工操作压到最低。

---

## 1. 工作模型

采用固定模型：

**Batch Planning → Parallel Claim → Autonomous Execution → Handoff → Central Integration → Aggregate Regression → Next Batch**

协调 AI 负责：

- 定义批次目标；
- 拆出 X1/X2/X3…；
- 避免任务边界互相踩文件；
- 定义验收和停止条件；
- 收齐结果后决定集成顺序；
- 解决分支/语义冲突；
- 跑 aggregate regression；
- 更新 PR/现状；
- 编排下一批。

执行 AI 负责一个 Xi 的完整闭环，而不是只完成其中一个小步骤。

---

## 2. 用户只 clone 一次

用户把 GitHub 仓库 clone 到任意本地目录后，该 clone 即成为本地开发基准。

AI 必须动态解析：

- `<repo_root>`：当前 clone 根目录；
- `<repo_parent>`：其父目录；
- `<repo_name>`：仓库目录名。

禁止把历史开发机的盘符、用户名或 clone 路径写成任务前提。

并行任务禁止通过“再 clone N 份仓库”解决隔离问题。

---

## 3. 并行隔离

### 3.1 一任务一 branch、一任务一 worktree

每个 Xi 使用：

- 独立 branch；
- 独立 Git worktree；
- 独立 Generated 输出；
- 独立日志/evidence 命名空间。

多个 AI 禁止同时写同一个 worktree。

推荐 branch：

`agent/<batch>-<task>-<short-name>`

例如：

`agent/b1-x1-player-response`

### 3.2 worktree 目录自动推导

推荐逻辑位置：

`<repo_parent>/<repo_name>.worktrees/<batch>/<task>`

这只是从当前 clone 运行时推导的布局，不是宿主固定路径。

用户不应被要求手工创建、计算或输入这个目录。

### 3.3 主工作树保护

主 clone 用于：

- 用户正常工作；
- 协调 AI 查看总体状态；
- 最终中央集成。

执行 Xi 默认不直接在主工作树实施功能修改。

如果主工作树有未提交用户改动：

- 不 reset；
- 不 clean；
- 不自动 stash 后遗忘；
- 不把无关改动混入 Xi；
- 优先从已知安全 base 创建独立 task worktree。

---

## 4. Xi 任务包标准

协调 AI 每次给出的 Xi 至少包含：

### Identity

- Batch ID
- Task ID
- 推荐 branch 名
- base ref/SHA

### Goal

- 本任务要产生什么用户可感知或工程可复用成果；
- 为什么此任务值得独立并发。

### Scope

- 优先文件/系统；
- 明确禁止碰的 sibling task 范围；
- 可创建的 MOD/脚本/测试。

### Required execution

默认：

**PREFLIGHT → AUDIT → IMPLEMENT → BUILD → VERIFY → FIX/RETRY → COMMIT → PUSH → HANDOFF**

### Verification

明确本任务至少需要哪些 S0/S1/S2/S4/S5、静态检查、单元/集成测试或 evidence。

### Stop conditions

只有明确 Gate 才允许提前停下并等待用户。

---

## 5. 无人值守原则

用户长期不在电脑前，因此执行 Agent 必须默认：

- 普通实现细节自行决策；
- 可恢复失败自行诊断；
- 修复后自动重跑；
- 缺少可选工具时优先使用仓库已有替代路径；
- 对不可运行的验证明确标记 NOT RUN，而不是伪造 PASS；
- 能继续做静态/结构验证时继续推进；
- 完成任务授权范围内所有可完成工作后才交接。

不要因为以下普通情况停止：

- 第一次编译失败；
- 测试用例失败；
- lint/格式失败；
- 一个参数需要在合理范围内选择；
- 一个函数名和预期不同但可通过源码追踪定位；
- 分支需要 rebase 到任务 base 内可自动处理的非语义冲突。

---

## 5.1 子 Agent 空回传 → 自动重派 → Coordinator 接管（supervisor 证据协议）

> 背景：B3-P3 批次实测，子 Agent 通道在长任务上多次出现 **session error 空回传**（返回空结果、无任何工具调用、磁盘零改动）。该现象不是任务失败，而是通道故障。本协议固化无人值守下的处理顺序与证据要求。

### 5.1.1 判定顺序（每次空回传必须执行）

1. **先核磁盘，再重派**：收到空回传后，立即检查任务 worktree / 目标路径是否有实际改动（`git status`、文件存在性、产物 SHA）。磁盘有产物 → 按产物继续；磁盘零改动 → 进入重派。
2. **重派计数**：同一任务最多重派 2 次（共 3 次尝试）。每次重派必须携带前次失败摘要，禁止原样重复同一 prompt。
3. **Coordinator 接管**：第 3 次空回传后，Coordinator 直接接管执行该任务（不继续消耗子 Agent 会话），并在批次控制面记录 takeover 证据。
4. **接管即全量实证**：Coordinator 接管后按任务原始验收标准全量执行（不因接管而降低证据要求），如实记录 PASS/BLOCKED。

### 5.1.2 证据固化要求

每次空回传与接管必须在批次控制面（BATCH_STATUS.md / evidence bundle）记录：

- `task_id`、`attempt` 次数、每次回传类型（session error / 空结果 / 部分结果）；
- 磁盘核验结果（改动文件列表或"零改动"）；
- 重派时的增量上下文；
- takeover 决策（第几次后接管、接管原因）；
- 接管后执行链与最终证据文件引用。

### 5.1.3 与证据可信度的关系

- 接管不改变成果可信度：证据以**最终产物 + 验证报告**为准，与执行者身份无关；
- 空回传本身不是失败证据，也不得被当作"任务未完成"；
- 任何 PASS 都必须有对应证据文件（verified_at/command/artifact），接管路径同样适用。

### 5.1.4 B3-P3 实测记录（参考样本）

- B3-P3-X0：3 次空回传 → Coordinator 接管 → 全链构建 PASS（`docs/ai/audits/B3-P3-X0_PROMOTION_BUILD.json`）；
- B3-P3-X2：2 次空回传，但磁盘留有 bundle 产物 → 按产物提交并回填（`docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`）；
- B3-P3-X1：1 次空回传 → Coordinator 接管 → 门禁 PASS/BLOCKED 如实（`docs/ai/audits/B3-P3-X1_PROMOTION_GATES.json`）。

---

## 6. 真正人工 Gate

以下才可以阻塞等待用户：

1. baseline promotion；
2. 会修改/删除 immutable provenance；
3. 不可逆外部资产操作；
4. 工具无法取得必要的人类凭据/外部授权；
5. 两种冲突方案都会改变产品意图且没有现有规范可裁决；
6. 最终 S5 需要纯主观体验选择且无法通过既有 acceptance rule 自动判定。

即使命中人工 Gate，Agent 也应先完成 Gate 之前所有可自动完成的工作并提交证据。

---

## 7. Handoff 标准

每个 Xi 完成后必须返回结构化结果：

- `task_id`
- `branch`
- `base_sha`
- `final_sha`
- `commits`
- `changed_files`
- `created_mods`
- `created_tools`
- `build_id`
- `candidate_hash`
- `S0`
- `S1`
- `S2`
- `S4`
- `S5`
- `tests`
- `retry_summary`
- `potential_conflict_paths`
- `remaining_risks`
- `recommended_integration_order`

报告必须说明：

- 什么已经证明；
- 什么尚未证明；
- 哪些结论来自静态分析；
- 哪些来自最终 Candidate；
- 哪些需要中央集成后重新验证。

---

## 8. 中央集成规则

所有 Xi 完成后，不由执行 Agent 各自往集成线乱合。

协调 AI 集中执行：

### I0 — Collect

收集全部 branch、SHA、报告和 evidence。

### I1 — Scope Review

确认：

- 是否越界；
- 是否包含用户无关改动；
- 是否引入宿主绝对路径；
- 是否引入 secret；
- 是否修改 immutable；
- 是否与 status.json 事实冲突。

### I2 — Conflict Graph

建立：

- 文件冲突；
- 函数/节点语义冲突；
- MOD dependency；
- preimage 漂移；
- build/test infrastructure 冲突。

### I3 — Integration Order

根据依赖决定：

- merge；
- rebase；
- cherry-pick；
- 重新生成 patch；
- 拒绝某个 Xi 的局部实现但保留其审计结论。

### I4 — Aggregate Candidate

在集成线生成 fresh aggregate candidate。

### I5 — Regression

至少重新验证受影响的：

- S0；
- S1；
- S2；
- 所有相关 S4；
- 必要 Combat S5；
- absolute-path scan；
- secret scan。

### I6 — Report

协调 AI 更新：

- Draft PR；
- 当前已集成能力；
- 未解决风险；
- 下一批 Y1/Y2/Y3…。

---

## 9. 路径可移植性合同

所有 Xi 都必须检查：

- 不把 `<repo_root>` 展开后的真实绝对路径写进 Git；
- 不把 worktree 实际路径写进 Source of Truth；
- repo 内引用使用 repo-relative；
- repo 外路径来自本地配置/env/CLI；
- Python 优先 `pathlib.Path`；
- PowerShell 优先 `Join-Path` / `Resolve-Path`；
- 安全边界使用 real path containment 校验；
- 脚本可从 repo 内任意 cwd 启动。

发现历史绝对路径时：

1. 判断它是文档示例、local environment、测试夹具还是生产依赖；
2. 生产依赖必须改成动态 root/config；
3. 文档示例优先改成 `<repo_root>` 等逻辑路径；
4. 无法立即迁移的历史兼容点登记为 portability debt，不得继续复制。

---

## 10. 人类最简操作目标

目标不是让用户成为 Git worktree 管理员。

正常情况下，用户只需要：

1. 首次 clone/部署；
2. 把协调 AI 输出的 X1/X2/X3…分别交给执行 AI；
3. 等执行 AI 完成；
4. 把 branch/SHA/报告交回协调 AI；
5. 仅在真正人工 Gate 时做决定。

未来 orchestration tooling 应进一步把第 2–4 步压缩成一键/单命令批次管理。

---

## 11. Orchestration Tooling 目标

下一阶段应优先实现 repo-relative 的 `scripts/ai/` 工具，使人类不需要手工管理并发基础设施。

目标能力：

- `batch init`：建立 Batch ID 与任务表；
- `task claim`：自动创建 branch/worktree；
- `task status`：显示 Xi 状态；
- `task handoff`：收集 SHA、diff、build/test 结果；
- `batch collect`：汇总所有 Xi；
- `integration preflight`：冲突/绝对路径/secret/preimage 扫描；
- `task cleanup`：集成后安全删除 worktree；
- 所有命令从当前 clone 自动解析 repo root。

在这些工具落地前，执行 AI 仍需遵守本文件的同等隔离和交接合同。
