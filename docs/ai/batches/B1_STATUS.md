# B1 协调状态视图

> **用途**：B1 并行研发的协调视图，供执行 Agent 与中央集成读取。
> **不是产品状态权威**：产品/验证状态仍以 `status.json` 和对应 evidence 为准。
> **更新时间**：2026-08-19

## 当前基线

- Integration line：`agent/kinetic-arcane-remaster-foundation`
- Frozen base ref：`batch/b1-anchor`
- Frozen base SHA：`c864480d8908630d602c17f4949b96b65d19b275`
- 基线含义：最新 `main`（已跟踪且 byte-preserving 的 `03_raw/04_recovered`、clone/deploy 基础）+ Kinetic Arcane requirements + 可移植/并行治理。
- `00_original` 仍不入 Git；fresh embed、boot、VM S4/S5 仍需本地运行环境。

## 主线同步说明

早期 B1 基线建立时，仓库尚未把 `03_raw/04_recovered` 纳入 Git。2026-08-18 主线已改变这一事实，因此协调 AI 已完成基线重整：

- `03_raw/04_recovered` 现在直接随 clone 提供，仍为不可变 Recovered Provenance；
- GitHub/远端 AI 可以读取真实 recovered 源码、审查真实 old_text/preimage；
- 不再以“GitHub 缺少 recovered 源码”为默认前提；
- 仓库内部路径仍必须 repo-relative；
- 多 Agent 必须使用独立 worktree，禁止共享主工作树。

旧 Kinetic 线已保留快照：`archive/kinetic-pre-main-sync-20260819`，仅用于 forensic，不作为新任务基线。

## Xi 状态

| Task | Branch | 当前状态 | Head / Base | 下一动作 |
|---|---|---|---|---|
| B1-X0 | `agent/b1-x0-batch-automation` | READY / 待执行 | base=`c864480d…` | 实现正确的 worktree-aware batchctl、portability/secret scan、handoff/collect/integration preflight |
| B1-X1 | `agent/b1-x1-player-response` | READY / 待执行 | base=`c864480d…` | 读取 tracked `04_recovered`，完成 Player C0 → `k1-player-response` → Candidate/Gates |
| B1-X2 | `agent/b1-x2-hit-reaction` | READY / 待执行 | base=`c864480d…` | 读取 tracked `04_recovered`，完成 Mob C0 → `k2-hit-reaction` → Candidate/Gates |
| B1-X3 | `agent/b1-x3-combat-pipeline` | PORTED / 待中央集成 | head=`5418f275b74013d73f813f839f28ba9ef37173e4` | 保留 C0、`feat-tce-context`、semantic contract；B1-I1 做 aggregate 回归 |
| B1-X4 | `agent/b1-x4-camera-audio` | PORTED+FIXED / 待新基线运行验证 | head=`e061b4758eb16cb034c95dcb9125ca9f4f41a8a8` | v0.2 voice budget 已修正；本地重跑 compile/S0/S1/S4，S5 后置 |
| B1-X5 | `agent/b1-x5-combat-harness` | READY / 待执行 | base=`c864480d…` | 建立 TestLevel 无人值守 Combat Harness 与 telemetry/evidence |

## X3 移植说明

X3 已从旧 anchor 移植到新基线，当前相对 `batch/b1-anchor` 仅领先 1 个任务提交，包含：

- `docs/ai/audits/B1-X3-combat-pipeline.md`
- `docs/ai/audits/B1-X3-combat-pipeline-evidence.json`
- `mods/feat-tce-context/mod.json`
- `scripts/validate/semantic_combat_pipeline_contract.py`

历史 evidence 中记录的旧 base SHA 属于原执行 provenance，不应伪改；当前 branch ancestry 已以新 anchor 为父提交。

## X4 协调修正说明

原 X4 的方向可用，但中央审查发现两个需要修正的问题：

1. 旧审计文档含某台机器的 `G:\...` evidence 路径，已改为 `<repo_root>/10_logs/...` 逻辑路径；
2. 原 voice budget 通过 `child.name == "SoundEffect"` 遍历计数，Godot 重名节点可能自动改名，已升级为 `_sfx_active_count` + `tree_exited` 生命周期回收，并将聚合 key 改为 `bus + stream instance`。

因此 X4 v0.2 必须在新基线本地重新执行 compile/S0/S1/S4；原运行证据只证明旧版本方向和构建链可行。

## 自动化注意事项

旧 Kinetic 快照中曾出现 `scripts/batch-monitor/batch_monitor.ps1`，它会把多个 Agent 都以同一个主 `repo_root` 作为 `--dir` 启动，违反隔离规则。该实现**没有迁入新基线**。

B1-X0 必须实现：

- 每个 Xi 独立 branch + 独立 Git worktree；
- OpenCode/其他执行 Agent 的工作目录必须是对应 task worktree；
- claim/status/handoff/collect/cleanup/integration-preflight 一条命令一个人类意图；
- 不要求用户手工输入绝对路径；
- cleanup 对未合并/未知工作树 fail-closed。

## 当前并发启动建议

可以立即并发执行：

- `B1-X0`
- `B1-X1`
- `B1-X2`
- `B1-X5`

同时让 `B1-X4` 在其现有 branch 上继续执行新基线 v0.2 的 compile/S0/S1/S4 验证。

`B1-X3` 无需重做，等待 B1-I1。

执行 AI 的最简指令仍为：

`认领 B1-Xn，按仓库规则全自动执行到最远可验证状态。`

对于 X4 使用：

`继续 B1-X4：基于当前分支执行 v0.2 新基线 compile/S0/S1/S4，修复可恢复问题并更新 handoff。`

## B1-I1 进入条件

以下全部满足后进入中央集成：

- X0/X1/X2/X5 完成交接；
- X3 当前移植成果保留；
- X4 v0.2 新基线运行 Gate 完成或明确给出不可自动解决的真实阻塞；
- 各任务提供 branch/final SHA/evidence/潜在冲突路径。

随后由协调 AI统一执行 conflict graph → integration ordering → aggregate candidate → aggregate S0/S1/S2/S4 → 必要 Combat S5 → B2 编排。
