# OPERATING_MODEL.md — 多 Agent、Task、Git 与工作区实践（Lean v3.2）

## 1. 组织模型（gork 调度 + AGY / opencode 执行 + gpt 会诊）

### 角色

| 角色 | 技能/身份 | 职责 |
|------|-----------|------|
| **Coordinator（主 AGENT）** | **gork** | 校准状态、生成 Task DAG、**并行调度** Worker、Review/Merge、状态与 Evidence 更新、清理、生成下一批、决定何时请 gpt 会诊。gork **不亲自串行干活** |
| **Primary Worker** | **AGY**（gemini cli） | 默认执行具体 Task：编码、迁移、测试、产出 Evidence 与 Handoff |
| **Fallback Worker** | **opencode**（opencode cli） | AGY 额度不足或不可用时接替执行 |
| **Expert Consultant** | **gpt** | 仅在疑难杂症或复杂情况下由 gork 调用，提供分析与建议，不直接执行代码修改 |

### 强制并行 + Background 模式

```text
1. 无依赖 Task 默认并行
2. 所有 Worker Task 必须使用 background 模式启动
3. gork 不得同步等待一个 Worker 完成后再启动其他可并行 Task
4. 单个 Worker 失败不阻塞其他并行任务
```

### 调度优先级

```text
1. 优先派给 AGY
2. AGY 额度耗尽 / 不可用 → 自动切换 opencode，并记录切换原因
3. 疑难杂症 / 复杂情况 → gork 先调用 gpt 会诊，再决定继续或调整
```

**疑难杂症触发条件（示例）：**
- 同一 Task 连续失败 ≥ 2 次且非明显环境问题
- 大范围不兼容、blocker DAG 复杂
- 重大架构取舍（影响多个系统）
- 需要深度根因分析或跨模块推理

gpt 输出仅为建议，最终决策与执行仍由 gork 负责。gpt 不直接更新中央分支或提交代码。

### Worker 约束

Worker（AGY / opencode）**不得**：
- 擅改 USER_LOCKED 决议
- 直接更新中央集成分支
- 把普通工程问题交给用户
- 将过程文件长期留在主仓库
- 自行决定切换到另一个 Worker 或调用 gpt（由 gork 统一调度）

---

## 2. Task 必备字段（精简 + 并行）

```text
Task ID
Goal
Why Now
Scope
Allowed Paths
Forbidden Paths
Dependencies（显式列出；空则默认可并行）
Acceptance Criteria（必须可机器验证）
Required Evidence
Known Risks
Rollback
Handoff Format
Preferred Worker（默认 AGY）
Needs Expert（可选）
Parallelizable（true/false）
```

没有明确 Acceptance Criteria 和 Allowed/Forbidden Paths 的任务不得开始大规模修改。

gork 在分配时根据当前 AGY 额度、任务复杂度、历史失败次数动态决定实际 Worker 与是否先请 gpt。

---

## 3. Git 规则

**中央集成分支（固定）：**  
`agent/kinetic-arcane-remaster-foundation`

**Worker 分支：**  
`agent/<batch>-<task>-<slug>`

规则：
- Worker 不直接更新中央分支
- Coordinator 负责集成
- 禁止 `git add .`、`git add -A`、`git add --all`
- 只 stage 精确确认的路径
- commit、PR、状态说明使用**中文**
- tracked 文件不得包含宿主绝对路径、secret、private EXE、script key

---

## 4. 工作区结构（推荐最小）

```text
<WORKSPACE_ROOT>/
├─ Mutagenic-zhCN-HD/          # 唯一主 Clone
├─ worktrees/
│  ├─ active/                  # 当前并行 Worker
│  └─ quarantine/              # 异常/待审
├─ runtime/                    # 运行时输出（不进 Git）
├─ scratch/                    # 临时转换/生成
├─ artifacts/
│  └─ evidence/                # 有价值证据
├─ archive/                    # 归档
└─ private/                    # 私有资产（永不自动删除）
```

长期只维护**一个主 Clone**。并行 Worker 使用 worktree，不要复制多个彼此漂移的完整仓库。

---

## 5. 工作区卫生强制原则

- 主仓库只放真正需要版本控制的 Source / Schema / Test / Canonical Docs / 小型机器状态
- `scratch/`、普通 runtime 输出、下载缓存、临时构建 **不得进入 Git**
- 成功 worktree 在完成集成和证据晋升后**立即删除**
- 失败 worktree 先提取 failure bundle，再删除或进入短期 quarantine
- 过程文件不是因为“以后可能有用”就永久保存
- PRIVATE / IMMUTABLE / Baseline / Release 不得被自动清理

---

## 6. 简化 Retention

| 类型 | 处理 |
|------|------|
| 临时（scratch / cache / temp） | 任务完成立即删除 |
| 普通运行日志 / 截图 / trace | Evidence 提取后删除 |
| Task / Batch Evidence | 保留到后续 Gate 稳定，或压缩归档 |
| Baseline / Release | 长期 / 永久保留 |
| Private / Immutable | 永不自动删除 |

---

## 7. 错误分类与重试

- **TRANSIENT**：自动 retry / backoff
- **DETERMINISTIC_CODE**：修代码
- **ENVIRONMENT**：自动修环境
- **PRIVATE_DEPENDENCY**：必要时 HUMAN_INPUT_REQUIRED
- **PRODUCT_DECISION**：必要时 HUMAN_INPUT_REQUIRED

---

## 8. Batch 收口

一个 Batch 完成后 Coordinator 必须：
1. 统一 Review
2. merge-tree / 冲突预检
3. 集成
4. 跑 Batch Gate
5. 更新 Product state
6. 压缩 Worker handoff 为 Batch summary
7. 晋升 Evidence
8. 执行 workspace cleanup
9. 生成下一批 READY Task（并**立即并行 background 启动**无依赖项）

---

## 9. 中文状态同步模板（推荐）

```markdown
## 当前状态
- Phase / Gate / HEAD
- Product Engine: Godot 4.7.1
- Legacy: Read-Only Reference

## 本批完成
- ...

## 验证与证据
- PASS / BLOCKED / NOT_PROVEN

## 工作区卫生
- 已删除成功 worktree
- 已清理 runtime/scratch
- 已晋升 Evidence

## 并行调度
- 本批并行 Task 数 / background 执行情况
- Worker 切换记录（如有）

## 风险
- ...

## 下一批计划
- ...
```

禁止写“CI 全绿”除非当前对应 run 已明确验证。
