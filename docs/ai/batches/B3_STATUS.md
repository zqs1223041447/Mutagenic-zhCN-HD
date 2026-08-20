# B3 协调状态视图

> **Batch**：`B3`
> **状态**：`B3-P0_INTEGRATED`（四任务全部集成：S2 路由定位 / 控制面闭环 / 元数据卫生 / 密度基准脚手架；check_all 11/11 PASS）
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **B3 集成 HEAD**：`f1546f4`（X0→X1→X2→X3 依序合并，merge-tree 预检全部 clean）
> **Planning/prep base**：`batch/b3-anchor` = `68bb1c1`（B2-I1 集成 HEAD，GPT 评审指定统一 base）
> **任务合同**：`docs/ai/batches/B3_PLAN.md`
> **来源**：GPT 评审（2026-08-20，会话 6a83bc24）：B2-I1 判定"有条件 PASS"，批准立即启动 B3-P0 四任务，Combat Polish 调参保持 WAITING_HUMAN_S5。

## B3-P0 — 已完成并集成

| Task | 状态 | 分支 / final_sha | 交付 |
|---|---|---|---|
| B3-X0 | ✅ COMPLETED → `agent/b3-x0-s2-route-recovery` = `968e188` | S2 路由定位：VK_F10 0x7A→0x79 修正（0x7A 实为 F11）+ seed save 生成器（make_harness_seed_save.py）+ 磁盘级可观测性（heartbeat/marker 时间线/save 指纹）；真实运行（原 B2 candidate，hash 不变）后断点定位=主循环冻结（godot.log 停于残缺 'Doing actual save from '，存档 sha 3+ 分钟不变），S2 保持 BLOCKED 如实；新增 `docs/ai/audits/B2-I1_S2_SUPPLEMENT.json`（不改历史证据） |
| B3-X1 | ✅ COMPLETED → `agent/b3-x1-control-plane-closure` = `a6b1eed` | check_all 组件注册表 6→11：event_spine 改 required + 注册 kill_feel 80/80、camera 93/93、combat_audio 120/120、audio selftest 14/14、s5 selfcheck 23/23；新增 `.github/workflows/ci-static-semantic.yml`（repo-only，不依赖原版 EXE；11 组件全 stdlib 可跑） |
| B3-X2 | ✅ COMPLETED → `agent/b3-x2-evidence-hygiene` = `57febdc` | mod.json 元数据修正（15→14 mods、移除不存在的 b2-x2-combat-timing）；B2_STATUS 旧启动指令归档标注；PR #1 body 控制字符污染清理（gh 2.97.0：38 处反引号、7 处 \a、2 处 \b，Draft 不变）；status.json 新增 B2-I1 非 baseline gate_scope/evidence（trusted_baselines 未动、无 promotion） |
| B3-X3 | ✅ COMPLETED → `agent/b3-x3-density-benchmark` = `9e02a36` | Build Density 基准脚手架：`docs/ai/batches/B3_DENSITY_BENCHMARK.md`（5/20/50/100 压力阶梯、frame-time/FPS/event-rate/voice/camera budget 指标、阈值草案）+ `scripts/benchmark/`（density_matrix.json、density_benchmark.py、selftests 21/21、telemetry schema）；零 gameplay 密度改动、零新总线 |

集成验证：merge-tree 预检 conflict_blocks=0（四分支两两 clean）；合并后 check_all 11/11 PASS（event_spine 44/44、kill_feel 80/80、camera 93/93、combat_audio 120/120、audio selftest 14/14、s5 selfcheck 23/23、pipeline 78/78、harness selftest 16/16、batchctl 56 tests）；abs-path production_hardcode=0；secret findings=0；worktrees 全部清理（B3-X1 长路径残留已手动清除）。

## B2 遗留待办（不变）

- ⏳ HUMAN S5 gate（HUMAN_REQUIRED：8 项人工 A/B 验收，等待用户反馈；机器绝不写 HUMAN_ACCEPTED）
- ⏳ S2 telemetry：断点已定位（主循环冻结），根因核查需 VM/人工（B3-X0 已产出 supplement 证据 + 修复工具）
- ⏳ baseline promotion：绝对禁止（需 S2 PASS + HUMAN S5 PASS + 元数据修正 + 最终 fresh rebuild 全验证）

## 下一批（待 HUMAN S5 反馈 + GPT 评审）

- B3 Combat Polish 实际调参（Kill/Camera/Audio 数值）→ WAITING_HUMAN_S5，暂不 claim
- B3 Density 真实实验（提高密度并测性能/可读性）→ 依赖 S2 PASS + S5 稳定
- ✅ GitHub CI Bring-up（B3-P1-X0）完成：GITHUB_RUN_PASS（真实 Actions run 实证，见下）

## CI 状态（B3-P1-X0 Bring-up 实证）

> **结论：GITHUB_RUN_PASS** —— `ci-static-semantic`（workflow_id 338323634）在协调线每次 push / PR sync 均产生真实 Actions run 且全部 success，非本地 check_all 冒充。

**诊断经过（gh CLI 实测，不猜）**：
1. workflow 是否被识别：`gh workflow list` → `ci-static-semantic active 338323634` ✅；
2. 协调线 HEAD 是否有 run：`gh api repos/.../actions/runs` → de039a6（B3-P0 集成 HEAD）push run `32337242527` + PR run `32337246144` 均 `conclusion=success`；后续 cf059cf 的 push/PR run（`32338068644`/`32338071546`）同样 success ✅；
3. Draft PR #1：`gh pr checks 1` 显示 2 个 check `pass`，`pull_request` 事件（opened/synchronize）在 Draft PR 上照常触发——Draft 不是无 run 的原因；
4. "combined status 为空"真相：`GET /commits/{sha}/status` 返回 `statuses: []` 是 **legacy commit-status contexts 通道**；GitHub Actions 结果走 **Check Runs API**（`check-runs` 实证 2 个 run success）。空 statuses 是 API 语义，不代表 CI 未运行；GPT 评审时的 combined-status 工具观察的通道看不到 Actions。

**修复（最小改动）**：workflow 增加 `workflow_dispatch` 触发（手动复验通道，`gh workflow run ci-static-semantic --ref <branch>`）；`push`/`pull_request` 保持全分支/PR 监听。行为无其他变更。

**复验**：`agent/b3-p1-x0` 分支 push + dispatch 各产生一个 run，均 PASS（详见该任务交接的 run id/url）。

**查看方式**：`gh pr checks 1`、`gh run list`、`gh run view <id>` 或仓库 Actions tab；PR 合并所需 required checks 若启用 branch protection 才会写 branch 状态，当前 repo 未启用。

## 主控最简启动指令（B3-P0 已执行完毕）

```text
启动 B3-P0：以 batch/b3-anchor=68bb1c1 为统一 base，batchctl claim B3-X0~X3 四个独立 worktree，并行派发；
X0=S2 路由修复（工具修复后用原 candidate 重跑，禁倒填 B2 PASS）、X1=check_all/CI 闭环、X2=证据/状态/PR 卫生、X3=密度基准脚手架；
全部完成后 merge-tree 预检 → 依序合并 → check_all 全回归 → push 核验 → 清理 worktree → 更新本状态与 PR → GPT 评审。
```
