# B1 协调状态视图

> **用途**：B1 并行研发的协调视图，供执行 Agent 与中央集成读取。
> **不是产品状态权威**：产品/验证状态仍以 `status.json` 和对应 evidence 为准。
> **更新时间**：2026-08-20（B1-I1 中央集成完成）

## B1-I1 集成结果（2026-08-20）

- X0–X5 全部完成并 push，中央集成至 `agent/kinetic-arcane-remaster-foundation`，无文件冲突（merge-tree 预检 rc=0）。
- 集成提交：`182e79f`(X0) → `0f69ba6`(X1) → `44e6e41`(X2) → `0abfc8d`(X3) → `009d046`(X4) → `6cea0e6`(X5)，集成线 HEAD 推进至 `6cea0e6`。
- 集成后验证：abs-path scan 0 FAIL（仅 WARN 级 provenance_metadata/local_config）；secret scan 无真实泄漏（findings 全为测试夹具 dummy，已脱敏）；关键交付文件齐全。
- X1/X2/X4 各 MOD 已在新基线本地 canonical build 通过 S0/S1/S4（fresh embed from 00_original，GDRE 语义恢复确认）；X5 15/15 自测 PASS；X3 为审计+TCE context 移植。
- 待办：aggregate candidate 聚合构建与回归（与后续批次一起做）；Combat S5 实机/人工验收；baseline promotion 需人工显式批准。

## 当前基线

- Integration line：`agent/kinetic-arcane-remaster-foundation`
- Frozen base ref：`batch/b1-anchor`
- Frozen base SHA：`c864480d8908630d602c17f4949b96b65d19b275`
- 基线含义：最新 `main`（已跟踪且 byte-preserving 的 `03_raw/04_recovered`、clone/deploy 基础）+ Kinetic Arcane requirements + 可移植/并行治理。
- `00_original` 仍不入 Git；fresh embed、boot、VM S4/S5 仍需本地运行环境。

## 主线同步说明

早期 B1 基线建立时，仓库尚未把 `03_raw/04_recovered` 纳入 Git。主线已经改变这一事实，因此协调 AI 已完成基线重整：

- `03_raw/04_recovered` 现在直接随 clone 提供，仍为不可变 Recovered Provenance；
- GitHub/远端 AI 可以读取真实 recovered 源码、审查真实 old_text/preimage；
- 不再以“GitHub 缺少 recovered 源码”为默认前提；
- 仓库内部路径仍必须 repo-relative；
- 多 Agent 必须使用独立 worktree，禁止共享主工作树。

旧 Kinetic 线保留快照：`archive/kinetic-pre-main-sync-20260819`，仅用于 forensic，不作为新任务基线。

## Xi 状态

| Task | Branch | 当前状态 | Head | 本地下一动作 |
|---|---|---|---|---|
| B1-X0 | `agent/b1-x0-batch-automation` | REMOTE C0 DONE / 实现待执行 | `53446b8c118ac546147d070ce16a56b8895afebc` | 实现 worktree-aware batchctl、scanner、secret scan、handoff/collect/integration-preflight，并运行自测 |
| B1-X1 | `agent/b1-x1-player-response` | REMOTE C0 + CANDIDATE READY | `3d0f9aff685111e4c3b9d1843ea7d647cb0447d3` | 直接对 `k1-player-response` resolve/apply → build → S0/S1/S2/S4 → A/B S5；修复可恢复问题 |
| B1-X2 | `agent/b1-x2-hit-reaction` | REMOTE C0 + CANDIDATE READY | `46c44846de3c873853aeba38e0451f666d44bb98` | 直接对 `k2-hit-reaction` resolve/apply → build → S0/S1/S2/S4 → A/B S5；验证 DoT/状态色/死亡一次性 |
| B1-X3 | `agent/b1-x3-combat-pipeline` | PORTED / 待中央集成 | `5418f275b74013d73f813f839f28ba9ef37173e4` | 无需重做 C0；B1-I1 做 aggregate 回归 |
| B1-X4 | `agent/b1-x4-camera-audio` | PORTED+FIXED / 待新基线运行验证 | `e061b4758eb16cb034c95dcb9125ca9f4f41a8a8` | v0.2 重跑 compile/S0/S1/S4；S5 后置 |
| B1-X5 | `agent/b1-x5-combat-harness` | REMOTE C0 DONE / harness 实现待执行 | `d388233242ab9ca95c73e9ae67e17ba9a1f2bcb2` | 实现 deterministic scenario driver / seed / telemetry / report，并自测 |

## X0 远端 C0 结论

最新主线 `scripts/bootstrap_deploy.py` 已以 `Path(__file__).resolve().parents[1]` 定位 repo root，属于正确正例，不应重写。

Scanner 必须区分：

- `production_hardcode`：FAIL；
- `provenance_metadata`：保留并 INFO/WARN，例如 recovered manifest 的历史 `source` 绝对路径；
- `docs_example`：INFO，例如 `C:\path\to\Mutagenic.exe`；
- local ignored config：允许本地存在但不得进入生产默认值。

完整预审计：`docs/ai/audits/B1-X0_PORTABILITY_C0.md`。

## X1 远端 C0 / Candidate

真实 `Player.gd` 显示 Dash 直接使用当前 `velocity.normalized()`；静止时 velocity 为零，但仍会播放声音并进入 0.75s cooldown，形成确定性无响应缺口。

`k1-player-response` v0.1 已创建：

- 缓存最近非零移动方向；
- 当前有输入时仍使用当前方向；
- 静止 Dash fallback 到最近方向；
- 不改 movement_speed、DASH_AMOUNT、cooldown、碰撞、伤害或存档。

完整预审计：`docs/ai/audits/B1-X1_PLAYER_RESPONSE_C0.md`。

## X2 远端 C0 / Candidate

`Stats.damage_taken` 只对 Player emit，Mob 没有现成 direct-hit/crit signal。为了不抢 X3 的 `Stats.gd` preimage，v0.1 采用 health-loss visual reaction：

- 60ms `Sprite.self_modulate` 反馈；
- 160ms 最小间隔；
- 与现有状态 `Sprite.modulate` 分层；
- 不改伤害、碰撞、死亡、掉落、TCE；
- direct hit / DoT / crit-heavy 细分留给后续 combat event foundation。

完整预审计：`docs/ai/audits/B1-X2_HIT_REACTION_C0.md`。

## X3 移植说明

X3 已从旧 anchor 移植到新基线，当前相对 `batch/b1-anchor` 仅领先 1 个任务提交，包含：

- `docs/ai/audits/B1-X3-combat-pipeline.md`
- `docs/ai/audits/B1-X3-combat-pipeline-evidence.json`
- `mods/feat-tce-context/mod.json`
- `scripts/validate/semantic_combat_pipeline_contract.py`

历史 evidence 中记录的旧 base SHA 属于原执行 provenance，不伪改；当前 branch ancestry 已以新 anchor 为父提交。

## X4 协调修正说明

原 X4 的方向可用，但中央审查修正了两个问题：

1. 旧审计文档的宿主 `G:\...` evidence 路径改为 `<repo_root>/10_logs/...` 逻辑路径；
2. voice budget 从 `child.name == "SoundEffect"` 遍历计数升级为 `_sfx_active_count` + `tree_exited` 生命周期回收，并将聚合 key 改为 `bus + stream instance`。

X4 v0.2 必须在新基线本地重跑 compile/S0/S1/S4；原运行证据只证明旧版本方向和构建链可行。

## X5 远端 C0 结论

- `TestSpawner.tscn` 当前只是空 `Node2D`；
- `TestLevel._ready()` 直接执行 `spawn_cluster_in_ladder(0, 0, 300, current_wave)`；
- BaseLevel 从 spawnables 随机选择 mob。

因此现有 TestLevel 适合压力试验，不是确定性回归 harness。X5 应新增显式 scenario id + seed + composition + spawn positions/count + telemetry/report；保留随机 300 mobs 作为独立 stress scenario。

完整预审计：`docs/ai/audits/B1-X5_COMBAT_HARNESS_C0.md`。

## 自动化注意事项

旧 Kinetic 快照中曾出现 `scripts/batch-monitor/batch_monitor.ps1`，会把多个 Agent 都以同一个主 `repo_root` 作为 `--dir` 启动，违反隔离规则；该实现没有迁入新基线。

X0 必须确保：

- 每个 Xi 独立 branch + 独立 Git worktree；
- 执行 Agent 工作目录是对应 task worktree；
- claim/status/handoff/collect/cleanup/integration-preflight 一条命令一个人类意图；
- 不要求用户输入绝对路径；
- cleanup 对未合并/未知/脏 worktree fail-closed。

## 当前并发启动建议

现在推荐同时继续：

- `B1-X0`：从现有 C0 继续实现自动化；
- `B1-X1`：从现有 Candidate 直接 build/Gate；
- `B1-X2`：从现有 Candidate 直接 build/Gate；
- `B1-X5`：从现有 C0 继续实现 harness；
- `B1-X4`：在现有 branch 重跑 v0.2 Gate。

`B1-X3` 无需重做，等待 B1-I1。

最简指令：

`继续 B1-Xn：读取当前 branch 已有 C0/Candidate，按仓库规则全自动推进到最远可验证状态并更新 handoff。`

X4：

`继续 B1-X4：基于当前分支执行 v0.2 新基线 compile/S0/S1/S4，修复可恢复问题并更新 handoff。`

## B1-I1 进入条件

以下全部满足后进入中央集成：

- X0 完成自动化实现与自测；
- X1/X2 完成本地 build/Gates 或给出真实不可自动解决阻塞；
- X3 当前移植成果保留；
- X4 v0.2 新基线运行 Gate 完成或给出真实阻塞；
- X5 harness 实现/自测完成；
- 各任务提供 branch/final SHA/evidence/潜在冲突路径。

随后由协调 AI 统一执行 conflict graph → integration ordering → preimage drift review → aggregate candidate → aggregate S0/S1/S2/S4 → 必要 Combat S5 → B2 编排。
