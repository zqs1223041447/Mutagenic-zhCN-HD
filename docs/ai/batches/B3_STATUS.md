# B3 协调状态视图

> **Batch**：`B3`
> **状态**：`B3-P2_INTEGRATED`（B3-P0 四任务 + B3-P1 三任务 + B3-P2 三任务全部集成：CI 云端 PASS / S2 telemetry 生命周期闭环 / Validation-Promotion 候选分隔 / S3 persistence 无人值守门禁；check_all 13/13 PASS）
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **B3 集成 HEAD**：`d86cf12`（P0: f1546f4；P1: 9be7fc0；P2: X0→X1→X2 依序合并，仅 check_all_components.json 双组件冲突已消解）
> **Planning/prep base**：`batch/b3-anchor` = `68bb1c1`（P0）；`batch/b3-p1-anchor` = `de039a6`（P1）；`batch/b3-p2-anchor` = `60f9232`（P2）
> **任务合同**：`docs/ai/batches/B3_PLAN.md`
> **来源**：GPT 评审（2026-08-20，会话 6a83bc24）：B2-I1 判定"有条件 PASS"；B3-P0 评审 PASS；B3-P1 评审 PASS（采纳 GITHUB_RUN_PASS）；批准 B3-P2 S2/S3/候选边界收口；Combat Polish 调参保持 WAITING_HUMAN_S5。

## B3-P0 — 已完成并集成

| Task | 状态 | 分支 / final_sha | 交付 |
|---|---|---|---|
| B3-X0 | ✅ COMPLETED → `agent/b3-x0-s2-route-recovery` = `968e188` | S2 路由定位：VK_F10 0x7A→0x79 修正（0x7A 实为 F11）+ seed save 生成器（make_harness_seed_save.py）+ 磁盘级可观测性（heartbeat/marker 时间线/save 指纹）；真实运行（原 B2 candidate，hash 不变）后断点定位=主循环冻结（godot.log 停于残缺 'Doing actual save from '，存档 sha 3+ 分钟不变），S2 保持 BLOCKED 如实；新增 `docs/ai/audits/B2-I1_S2_SUPPLEMENT.json`（不改历史证据） |
| B3-X1 | ✅ COMPLETED → `agent/b3-x1-control-plane-closure` = `a6b1eed` | check_all 组件注册表 6→11：event_spine 改 required + 注册 kill_feel 80/80、camera 93/93、combat_audio 120/120、audio selftest 14/14、s5 selfcheck 23/23；新增 `.github/workflows/ci-static-semantic.yml`（repo-only，不依赖原版 EXE；11 组件全 stdlib 可跑） |
| B3-X2 | ✅ COMPLETED → `agent/b3-x2-evidence-hygiene` = `57febdc` | mod.json 元数据修正（15→14 mods、移除不存在的 b2-x2-combat-timing）；B2_STATUS 旧启动指令归档标注；PR #1 body 控制字符污染清理（gh 2.97.0：38 处反引号、7 处 \a、2 处 \b，Draft 不变）；status.json 新增 B2-I1 非 baseline gate_scope/evidence（trusted_baselines 未动、无 promotion） |
| B3-X3 | ✅ COMPLETED → `agent/b3-x3-density-benchmark` = `9e02a36` | Build Density 基准脚手架：`docs/ai/batches/B3_DENSITY_BENCHMARK.md`（5/20/50/100 压力阶梯、frame-time/FPS/event-rate/voice/camera budget 指标、阈值草案）+ `scripts/benchmark/`（density_matrix.json、density_benchmark.py、selftests 21/21、telemetry schema）；零 gameplay 密度改动、零新总线 |

集成验证：merge-tree 预检 conflict_blocks=0（四分支两两 clean）；合并后 check_all 11/11 PASS（event_spine 44/44、kill_feel 80/80、camera 93/93、combat_audio 120/120、audio selftest 14/14、s5 selfcheck 23/23、pipeline 78/78、harness selftest 16/16、batchctl 56 tests）；abs-path production_hardcode=0；secret findings=0；worktrees 全部清理（B3-X1 长路径残留已手动清除）。

## B3-P1 — 已完成并集成（GPT 评审批准 Diagnostics/Readiness Wave）

| Task | 状态 | 分支 / final_sha | 交付 |
|---|---|---|---|
| B3-P1-X0 | ✅ COMPLETED → `agent/b3-p1-x0` = `2386881` | CI Bring-up：诊断=协调线每次 push/PR sync 均有真实 Actions run 且全 success（GPT 评审时点无 run 已自愈；"combined status 为空"是 legacy commit-status 通道盲区，Actions 走 check-runs API）；修复=workflow 增加 `workflow_dispatch`；**GITHUB_RUN_PASS 真实**（run 32339170665/32339176772 等 6 个 success，artifact ci-gate-evidence 上传）；状态文档落盘 |
| B3-P1-X1 | ✅ COMPLETED → `agent/b3-p1-x1` = `ae769fe` | S2 Save Bisect：声明式 diagnostic MOD（`mods/b3-p1-s2-diagnostic`，12 patches）+ `save_bisect_runner.py`；do_save_game 全部 11 子步骤（m01→m11）6 次运行每次写满——"Doing actual save from 处冻结"是 kill 时日志 flush 截断伪影，存档路径毫秒级完成；c7 修复后 `Destination found:test_level` + `[COMBAT_HARNESS] spawns=started`（3 次）——**S2 全链首次闭环**；遗留：telemetry 未写出（玩家被 3 只 SkeletonWarrior 击杀打断 20s 计时，归 combat 切片）；bisect 证据 `docs/ai/audits/B3-P1-S2_BISECT.json`；候选 `Mutagenic_s2diag2.exe` sha256 F7A8C874… 3744/3744 |
| B3-P1-X2 | ✅ COMPLETED → `agent/b3-p1-x2` = `a9a77ed` | S5 Feedback Intake：`docs/ai/batches/B3_S5_INTAKE_MAP.md`（242 行）——8 项人工验收 checklist → Kill/Camera/Audio tunable（现值→建议范围）→ semantic contract → FAIL regression 路径全映射；含调参影响面（Camera 契约 7d/7h/7i 联合不定式、Audio 字面量钉死、Kill Feel budget 绿域 [1,5]）、调参任务模板（B3-CP<NN> + G1–G10 验证序列）；未改任何 gameplay 数值；human gate 语义保持（HUMAN_ACCEPTED 仅人工录入） |

集成验证：merge-tree 预检 3 分支两两 clean → 依序合并 `9be7fc0` → check_all 11/11 PASS → abs-path production_hardcode=0 → secret findings=0 → worktrees 全部清理（P1-X0 长路径残留已手动清除）。

## B3-P2 — 已完成并集成（GPT 评审批准 S2/S3/候选边界收口）

| Task | 状态 | 分支 / final_sha | 交付 |
|---|---|---|---|
| B3-P2-X0 | ✅ COMPLETED → `agent/b3-p2-x0` = `4d7f540` | **S2 Telemetry Closure**：k5 harness telemetry 生命周期 v2（scenario 启动即建 session 文件 + 2s checkpoint flush + 统一 `_finish_harness_exit` 出口——timeout/all_killed/player_died/scene_exit 均 flush 并记 exit_reason + partial telemetry）+ `runtime_smoke_safe` 免伤豁免场景（seed 2026082201, 3×SkeletonWarrior, timeout 20s，仅 harness 场景显式开启生效，普通游戏零影响）；schema 1.0 加 optional status/exit_reason/checkpoints/session_file + checkpoint_count（density superset 镜像）；**真实 S2 双出口 PASS**：run1 runtime_smoke_safe → exit_reason=timeout、checkpoints=10、driver 7/7 asserts（telemetry valid 0 issues）；run2 single_melee_hit → exit_reason=player_died、checkpoints=9（证明玩家死亡不再丢遥测，闭环 B3-P1-X1 c7 遗留）；候选 `Mutagenic_s2diag_telemetry.exe` sha256 AE8491…（103346052B）；证据 `docs/ai/audits/B3-P2-S2_TELEMETRY.json`；gates：harness 16/16、density 21/21、s5 23/23、check_all 11/11、abs-path/secret 0 |
| B3-P2-X1 | ✅ COMPLETED → `agent/b3-p2-x1` = `c3e38a7` | **Validation/Promotion Candidate Separation**：双候选划分（真实 resolver 三次 resolve）——Validation 14 mods/51 patches、Validation+Diagnostics 15/63、**Promotion 11 mods/49 patches**（`mods/b3-p2-x1-promotion-aggregate`，差集=49=51−2 仅 k5 harness 驱动 + ENABLE_TEST_ZONE bridge）；parity 契约 `semantic_validation_promotion_parity.py` **32/32 PASS**（49 共享正式 patch 逐字节一致、promotion 零禁用面：无 ENABLE_TEST_ZONE=true/marker writer/KEY_END/request-driven harness；pristine 影响面仅 Constants.gd:102 + HideoutLevel.gd:20 共 2 处）；check_all 注册 → **12/12**；文档 `docs/ai/batches/B3_CANDIDATE_SPLIT.md` + 证据 `docs/ai/audits/B3-P2-X1_PARITY_REPORT.json` |
| B3-P2-X2 | ✅ COMPLETED → `agent/b3-p2-x2` = `fc51481` | **S3 Persistence Regression Automation**：无人值守 gate `scripts/validate/s3_persistence_gate.py`（isolated APPDATA → seed save → 启动等存档重写 → 指纹 → 退出 → 冷启动重载 → 同态判定：volatile 豁免 timestamp/checksum/stamp，semantic sha 比对）+ 离线自检 `s3_persistence_selftests.py` **17/17**；**真实运行 PASS**：候选 Mutagenic.exe sha 4ad1de38，run1 load→rewrite→WM_CLOSE、run2 冷启动重载 LOADED AND MERGED、语义指纹双轮同 `a7ca81b8`、diff 路径 0、planted marker 存活、exit 0；check_all 注册 → **13/13**；证据 `docs/ai/audits/B3-P2-S3_EVIDENCE.json` + 手册 `docs/ai/batches/B3-P2-S3_PERSISTENCE_GATE.md`；剩余风险：Steam 云分支未验证（USE_STEAM=false）、promotion 候选必须重跑门禁 |

集成验证：merge-tree 预检 X0↔X1 / X0↔X2 均 clean，仅 X1↔X2 在 `check_all_components.json` 双组件冲突（validation_promotion_parity + s3_persistence_selfcheck，均已保留）→ 依序合并 `d86cf12` → check_all **13/13 PASS**（新增 parity 32/32、s3 17/17）→ abs-path production_hardcode=0 → secret findings=0 → worktrees 全部清理（长路径残留已用 `rmdir /s /q \\?\...` 手动清除）→ push 核验远端 d86cf12 一致 → CI run（push 32354647049 + PR 32354650592）确认。

## B2 遗留待办（更新）

- ⏳ HUMAN S5 gate（HUMAN_REQUIRED：8 项人工 A/B 验收，等待用户反馈；机器绝不写 HUMAN_ACCEPTED）——S5 Intake Map 已就绪，反馈回来可立即生成调参任务。用户已反馈第 1 项"不要屏幕震动"（与契约一致：direct_hit 无 camera impulse），2–8 项 DEFERRED_BY_USER（等后续实际进展再测）；反馈表 `10_logs/s5-human-feedback-20260820.md`
- ✅ S2 telemetry：B3-P2-X0 已闭环——run1 timeout/run2 player_died 双出口真实 telemetry PASS（生命周期 + exit_reason + checkpoint + session 文件全齐）；perf 帧统计仍为占位（frames=0/fps_min=0 由游戏侧后续填充）；all_killed/scene_exit 出口未独立运行触发（代码路径由编译+结构验证覆盖）
- ✅ S3 persistence：B3-P2-X2 已建立无人值守门禁并在当前候选真实 PASS；promotion 候选必须重跑门禁
- ⏳ Validation/Promotion：B3-P2-X1 已分隔并 parity 32/32 PASS；promotion 候选**未构建/未跑 S0–S5**（已声明 gated，not_proven 如实写入报告）
- ⏳ baseline promotion：绝对禁止（强化条件：S0+S1+S2+S3+S4 PASS + HUMAN S5 PASS + GitHub CI PASS + final fresh rebuild + Validation↔Promotion parity PASS + 无 diagnostic/test-only MOD + 用户显式批准）

## 下一批（待 HUMAN S5 反馈 + GPT 评审）

- B3 Combat Polish 实际调参（Kill/Camera/Audio 数值）→ WAITING_HUMAN_S5（S5 Intake Map 提供任务书模板；用户 2–8 项 DEFERRED_BY_USER）
- B3 Density 真实实验（提高密度并测性能/可读性）→ 依赖 S2 telemetry 完成 + S5 稳定
- B3-P2-X1 后续：promotion 候选构建 + 其上 S0–S5 重跑（含 S3 gate 重跑）→ 交 B3-P2 集成后的后续批次
- GitHub CI 状态：GITHUB_RUN_PASS（真实，见下节）

## CI 状态（B3-P2 集成 HEAD 实证）

> **结论：GITHUB_RUN_PASS** —— B3-P2 集成后最终 HEAD `359d1f5` 的 push run `32354862043`（3m31s）全 success：workflow yaml syntax ✓、abs-path scan ✓、secret scan ✓、unified check-all ✓、upload gate evidence ✓。PR run `32354867312` 同期全绿。B3-P2-XX 各分支 push run（X0 `32354141596`、X2 `32350960008` 等）亦全 success。

> **结论：GITHUB_RUN_PASS** —— `ci-static-semantic`（workflow_id 338323634）在协调线每次 push / PR sync 均产生真实 Actions run 且全部 success，非本地 check_all 冒充。

**诊断经过（gh CLI 实测，不猜）**：
1. workflow 是否被识别：`gh workflow list` → `ci-static-semantic active 338323634` ✅；
2. 协调线 HEAD 是否有 run：`gh api repos/.../actions/runs` → de039a6（B3-P0 集成 HEAD）push run `32337242527` + PR run `32337246144` 均 `conclusion=success`；后续 cf059cf 的 push/PR run（`32338068644`/`32338071546`）同样 success ✅；
3. Draft PR #1：`gh pr checks 1` 显示 2 个 check `pass`，`pull_request` 事件（opened/synchronize）在 Draft PR 上照常触发——Draft 不是无 run 的原因；
4. "combined status 为空"真相：`GET /commits/{sha}/status` 返回 `statuses: []` 是 **legacy commit-status contexts 通道**；GitHub Actions 结果走 **Check Runs API**（`check-runs` 实证 2 个 run success）。空 statuses 是 API 语义，不代表 CI 未运行；GPT 评审时的 combined-status 工具观察的通道看不到 Actions。

**修复（最小改动）**：workflow 增加 `workflow_dispatch` 触发（手动复验通道，`gh workflow run ci-static-semantic --ref <branch>`）；`push`/`pull_request` 保持全分支/PR 监听。行为无其他变更。

**复验**：`agent/b3-p1-x0` 分支 push + dispatch 各产生一个 run，均 PASS（详见该任务交接的 run id/url）。

**查看方式**：`gh pr checks 1`、`gh run list`、`gh run view <id>` 或仓库 Actions tab；PR 合并所需 required checks 若启用 branch protection 才会写 branch 状态，当前 repo 未启用。

## 主控最简启动指令（B3-P0/P1 已执行完毕）

```text
启动 B3-P0：以 batch/b3-anchor=68bb1c1 为统一 base，batchctl claim B3-X0~X3 四个独立 worktree，并行派发；
X0=S2 路由修复（工具修复后用原 candidate 重跑，禁倒填 B2 PASS）、X1=check_all/CI 闭环、X2=证据/状态/PR 卫生、X3=密度基准脚手架；
全部完成后 merge-tree 预检 → 依序合并 → check_all 全回归 → push 核验 → 清理 worktree → 更新本状态与 PR → GPT 评审。
B3-P1/B3-P2 已按同模式执行并集成（B3-P2 见上节）。
```
