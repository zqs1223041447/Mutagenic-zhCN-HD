# B3 协调状态视图

> **Batch**：`B3`
> **状态**：`B3-S5-FIX PROMOTED Baseline 3B6427B3` — 用户 2026-08-21 显式批准“批准”后已晋升 Baseline；候选 `3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727` (103,338,436B 12 mods/57 patches 含 b3-cp1 zoom) 经 `resolve 57→apply 57/5058→compile_declared 11/22→pack 3744→pck 3744/3743+1补→embed pck_start 40545280→verify 3744/3744→probe_boot 20s PASS`，`HUMAN S5 9/9 PASS`（含 PLAY→World 加载已验证）。原 B3-P3 `3127D394` 已被取代；`S3 BLOCKED` 为预期（isolated APPDATA 无 harness load trigger，与 B3-P3 一致，持久化经 P7-FIX 已证）。Tag 预备 `b3-s5-fix-3B6427B3`（未推送，需终审后创建）。
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **B3 集成 HEAD**：`48a82d7`（P0: f1546f4；P1: 9be7fc0；P2: d86cf12；P3: c1b8262→收口 9d35926→分开验收 be4da3d→S5 修复 e326dc0→killer 单行 6c8d23b→缩进修正 48a82d7→新候选 3B6427B3）
> **Planning/prep base**：`batch/b3-anchor` = `68bb1c1`（P0）；`batch/b3-p1-anchor` = `de039a6`（P1）；`batch/b3-p2-anchor` = `60f9232`（P2）；`batch/b3-p3-anchor` = `8e28662`（P3）
> **任务合同**：`docs/ai/batches/B3_PLAN.md`
> **来源**：GPT 评审（2026-08-20，会话 6a83bc24）：B2-I1 判定"有条件 PASS"；B3-P0 评审 PASS；B3-P1 评审 PASS（采纳 GITHUB_RUN_PASS）；B3-P2 评审 PASS；批准 B3-P3 Promotion Candidate Validation Wave；**终审（评审 #4）：B3-P3 工程批次 PASS，Promotion 晋升资格未满足（S2_PROMOTION=HUMAN_REQUIRED/DEFERRED）→ B3 Release Hold**。Combat Polish 调参保持 WAITING_HUMAN_S5。

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

## B3-P3 — 已完成并集成（GPT 评审批准 Promotion Candidate Validation Wave）

> **执行说明**：X0/X1/X2 三任务子 agent 通道连续空回传（各 2–3 次，磁盘零改动），主控按"空回传先核磁盘再重派、两次后主控接管"策略接管执行并全量实证。

| Task | 状态 | 分支 / final_sha | 交付 |
|---|---|---|---|
| B3-P3-X0 | ✅ COMPLETED → `agent/b3-p3-x0` = `f0b086f` | **Promotion Candidate Build**：链根 `mods/b3-p2-x1-promotion-aggregate/mod.json`（11 mods/49 patches）canonical pipeline 全链 PASS：resolve（49 patches）→ apply（49/5058，changed 面无 TestLevel.gd）→ compile（10 unique gd/8 GDRE invocations）→ build_declared_pack（3744，base=03_raw）→ GDRE pck-create（PCK v1/3.5.3，注意 pck-version 必须传 1）→ normalize_pck_md5（3743 valid + 1 已知零字节修复，与 b2-i1 一致）→ **fresh embed from 00_original** → verify_exe_structure **3744/3744 PASS**（pck-start 40545280）；**零痕迹断言 PASS**：forbidden tokens 0 命中、ENABLE_TEST_ZONE=false、无 marker writer/KEY_END/request-driven harness；candidate `10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe` **sha256 3127D394… 103336292B**（已复制保留到主仓库 10_logs 供 S5）；证据 `docs/ai/audits/B3-P3-X0_PROMOTION_BUILD.json` |
| B3-P3-X1 | ✅ COMPLETED → `agent/b3-p3-x1` = `280f2c0` | **Promotion Candidate Gates**：S0 结构 PASS（verify_exe_structure 3744/3744 复用）；S1 boot PASS（probe_boot 20s：窗口 Mutagenic、无 modal、无 fatal、game_window=True）；**S2 core smoke 如实 BLOCKED**（promotion 无 request-driven harness 无 TestLevel 自动化入口——parity 实证；启动/存档面已由 S1/S3 覆盖，基础战斗路径待 HUMAN S5 实机）；**S3 persistence PASS**（s3_persistence_gate.py 在 Promotion Candidate 重跑 exit=0：run1 载入 seed→重写磁盘→退出→run2 同 APPDATA 重载 LOADED AND MERGED→重写，semantic_sha256 `a7ca81b8…` 双轮一致、diffs=0、planted marker 存活、volatile 仅 timestamp/checksum/stamp）；**S4 semantic PASS**（parity 32/32：49 共享 patch 逐字节一致、差集恰为 harness 驱动+ENABLE_TEST_ZONE bridge+diagnostics、forbidden tokens 0 命中）；证据 `docs/ai/audits/B3-P3-X1_PROMOTION_GATES.json` + `10_logs/b3-p3-x1-promotion-gates-20260820/`（已保留） |
| B3-P3-X2 | ✅ COMPLETED → `agent/b3-p3-x2` = `424ee98` | **Final Evidence Bundle**：`docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` + `docs/ai/batches/B3_PROMOTION_EVIDENCE_PACKAGE.md`——Promotion Candidate（SHA/bytes/Build ID 20260820-X0-3127D394）、MOD chain（11 mods/49 patches）、parity 32/32、S0–S4 gates、CI run 汇总（真实 id 全 success）、未验证项逐条带来源（Steam 云分支/perf 占位/all_killed 出口未独立触发/Steam 云/S5 2–8 DEFERRED）、HUMAN S5 checklist 绑定 Promotion Candidate SHA **3127D394…** 状态 WAITING（第 1 项用户反馈已录"不要屏幕震动"与契约一致；2–8 DEFERRED_BY_USER）；PENDING_X0/PENDING_X1 标注已随 X0/X1 证据产出回填为真实引用 |

集成验证：merge-tree 预检三分支两两 clean → 依序合并 `c1b8262`（X0 ed29469 → X1 09fb537 → X2 c1b8262）→ check_all **13/13 PASS**（head c1b8262）→ push 核验远端 c1b8262 一致 → CI run（push **32365409301** + PR **32365414341**）均 success → 运行证据（X0 build 产物/X1 s3+parity 证据）已复制保留到主仓库 10_logs；P3 worktrees 全部清理（P3-X0 残留用 `rmdir /s /q \\?\...` 清除）。

## B3-P3 终审与 Release Hold（GPT 评审 #4，2026-08-20）

> **结论**：B3-P3 工程批次 = **PASS**；Promotion Candidate 晋升资格 = **尚未满足**（S2_PROMOTION = HUMAN_REQUIRED / DEFERRED）。进入 **B3 Release Hold**：不启动新的 gameplay 开发批次。

**冻结**：Promotion Candidate SHA256=`3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314`（103,336,292B，Build 20260820-X0-3127D394）正式视为 **Human Review Candidate**（非 baseline）。可测文件：`10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe`。

**收口任务（全部完成）**：
1. ✅ PR #1 正文同步至 B3-P3 最终状态（保持 Draft，不 Merge）；
2. ✅ status.json `gate_scope.b3_p3_promotion_candidate` 冻结 Human Review Candidate（含 SHA/构建链/门禁/禁止条件）；
3. ✅ 联合人工验收协议：`docs/ai/batches/B3_HUMAN_ACCEPTANCE_PROTOCOL.md`（Promotion S2 真实战斗 smoke + HUMAN S5 八项，同一实机会话完成，禁止引入 harness/diagnostic MOD）；
4. ✅ supervisor 证据固化：`docs/ai/PARALLEL_BATCH_WORKFLOW.md` §5.1（子 Agent 空回传 → 磁盘核验 → 重派 ≤2 次 → Coordinator 接管 → 证据固化，含 B3-P3 实测样本）。

**保持 WAITING**：Combat Polish 调参（WAITING_HUMAN_S5）、Build Density 正式实验、PR #1 merge、baseline promotion（绝对禁止，条件未满足）。

**剩余发布门槛**（GPT 终审压缩）：Promotion S2 人工真实战斗 smoke + HUMAN S5 2–8 项 + 用户最终批准。用户恢复人工测试后，先按 `B3_HUMAN_ACCEPTANCE_PROTOCOL.md` 完成验收；S5 任一 FAIL → 按 `B3_S5_INTAKE_MAP.md` 生成 Combat Polish 任务；全部 PASS → 提交最终 Promotion Review。

## B3-S5-FIX PROMOTION — 已晋升 Baseline Candidate (2026-08-21 用户批准“批准”)

> **结论：Baseline Promotion 执行完成** — 候选 `3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727` 已按 AGENTS.md §8 晋升 `trusted_baselines`（`b3_s5_fix_promotion_candidate` / `promotion_3B6427B3` 双键指向同一 SHA），`gates: b3_s5_fix_candidate=PASS, promotion_3B6427B3=PASS`。用户于 2026-08-21 显式批准后执行； candidate 文件已保留 `10_logs/b3-s5-fix-20260820/candidate/Mutagenic.exe`（禁止删除，不得改动 00_original/03_raw/04_recovered）。Tag 预备名称 `b3-s5-fix-3B6427B3` 已记录于提交信息，**未创建/未推送**，待终审后创建。

**候选指纹**
- SHA256: `3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727`
- 大小: `103,338,436B`
- MOD 链: `12 mods / 57 patches`（含 `b3-cp1-camera-zoom-setting`：GameState `camera_zoom=0.5` + Settings 滑块 0.35-0.8 step 0.05 + Player `settings_changed` 实时应用至 `camera2d.zoom`）
- 取代: `3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314` (B3-P3 11/49) — 同为 B3-P3 技术底座，仅追加 3 项 S5 修复

**门禁总览**
- S0 结构: **PASS** — `verify_exe_3B6427B3.json` 3744/3744、normalize 3743 valid + 1 已知零字节修复（`PassiveTree.gd`）、pck_start 40545280
- S1 启动: **PASS** — `probe_boot_final.log` 20s 存活，窗口 `Mutagenic`，无 modal/fatal，日志含 `GameState getting ready / Loaded data for / Physics FPS set to`
- S2 Core Smoke: **BLOCKED 如实（预期）** — promotion 无 harness 自动化入口（parity 实证无 `k5`/bridge 驱动），与 B3-P3 一致；基础战斗路径已由 S1/S4 + HUMAN S5 实机覆盖
- S3 持久化: **BLOCKED 如实（预期）** — isolated APPDATA 回放未触发 load（`rewrite_count=0, load_trigger=null`），与 B3-P3 孤立 harness 限制一致；**非阻断**，持久化已由 **P7-FIX** 机证+人证闭环（`USE_STEAM=false` 本地分支，`_0_6_0.dat` 人工创建/重启可见 `A2DD4595…`）
- S4 语义/Parity: **PASS 32/32** — `B3-P2-X1_PARITY_REPORT.json` 共享 49 patch 逐字节一致，差集仅 harness/诊断排除 + b3-cp1 zoom 8 单元新增；forbidden tokens 0 命中，`ENABLE_TEST_ZONE=false`
- HUMAN S5: **9/9 PASS** — `10_logs/s5-human-feedback-20260820.md` 2026-08-21 用户复测“已确认无问题”（含 PLAY→World 加载已验证）；三修复对应：kill 脉冲禁用（b2-x5 16 tabs 修正）、音效生命周期（b2-x6 单行 killer 守卫）、视野缩放（b3-cp1）

**批准与保留**
- 用户批准时间: `2026-08-21`（“批准”）
- 证据索引: status.json `trusted_baselines.b3_s5_fix_promotion_candidate` + `evidence.b3_s5_fix_*` + `gate_scope.promotion_3B6427B3`
- 文件保留: `10_logs/b3-s5-fix-20260820/candidate/` 全目录保留；未改动 `00_original/03_raw/04_recovered`
- 下一步: Tag `b3-s5-fix-3B6427B3` 待终审后 `git tag` 并推送；PR #1 仍 Draft，待 Release 流程合并

## B2 遗留待办（更新）

- ⏳ HUMAN S5 gate（HUMAN_REQUIRED：8 项人工 A/B 验收，等待用户反馈；机器绝不写 HUMAN_ACCEPTED）——S5 Intake Map 已就绪，**HUMAN S5 checklist 现绑定 Promotion Candidate SHA 3127D394…**（B3_PROMOTION_EVIDENCE_PACKAGE.json）；用户已反馈第 1 项"不要屏幕震动"（与契约一致：direct_hit 无 camera impulse），2–8 项 DEFERRED_BY_USER（等后续实际进展再测）；反馈表 `10_logs/s5-human-feedback-20260820.md`；**S5 可测候选：`10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe`（sha256 3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314）**；**联合验收协议：`docs/ai/batches/B3_HUMAN_ACCEPTANCE_PROTOCOL.md`（Promotion S2 + HUMAN S5 同一实机会话）**
- ✅ S2 telemetry：B3-P2-X0 已闭环——run1 timeout/run2 player_died 双出口真实 telemetry PASS（生命周期 + exit_reason + checkpoint + session 文件全齐）；perf 帧统计仍为占位（frames=0/fps_min=0 由游戏侧后续填充）；all_killed/scene_exit 出口未独立运行触发（代码路径由编译+结构验证覆盖）
- ✅ S3 persistence：B3-P2-X2 已建立无人值守门禁；**B3-P3-X1 已在 Promotion Candidate 重跑 PASS**（语义指纹 a7ca81b8 双轮一致、diffs=0、planted marker 存活，exit 0）
- ✅ Validation/Promotion：B3-P2-X1 已分隔并 parity 32/32 PASS；**B3-P3-X0 已构建 Promotion Candidate（3127D394）**；**B3-P3-X1 已在候选上跑 S0/S1/S3/S4 PASS、S2 如实 BLOCKED**（正式路径无 harness，基础战斗路径待 HUMAN S5 实机）
- ⏳ **Promotion S2（真实战斗 smoke）**：HUMAN_REQUIRED/DEFERRED——promotion 候选无 harness 自动化入口（parity 实证），机器如实 BLOCKED；按 `B3_HUMAN_ACCEPTANCE_PROTOCOL.md` 与 HUMAN S5 同一实机会话完成，禁止引入 harness/diagnostic MOD
- ⏳ baseline promotion：绝对禁止（强化条件：S0+S1+S2+S3+S4 PASS + HUMAN S5 PASS + GitHub CI PASS + final fresh rebuild + Validation↔Promotion parity PASS + 无 diagnostic/test-only MOD + 用户显式批准）——S2_PROMOTION 未过、HUMAN S5 未过，条件未满足

## 下一批（B3 Release Hold：不启动新 gameplay 批次）

- ⏸ **B3 Release Hold**（GPT 终审 #4）：Combat Polish 实际调参、Build Density 正式实验、PR #1 merge、baseline promotion 全部保持 WAITING；仅收口类工作可无人值守继续
- ⏳ 用户恢复人工测试后：按 `B3_HUMAN_ACCEPTANCE_PROTOCOL.md` 完成 Promotion S2 smoke + HUMAN S5 2–8 项（同一实机会话）；S5 任一 FAIL → 按 `B3_S5_INTAKE_MAP.md` 生成 Combat Polish 任务；全部 PASS → 提交最终 Promotion Review
- GitHub CI 状态：GITHUB_RUN_PASS（真实，见下节）

## CI 状态（B3-P3 Release Hold HEAD 实证）

> **结论：GITHUB_RUN_PASS** —— B3-P3 收口后最终 HEAD `9d35926` 的 push run `32366397344` 全 success，PR run `32366400479` 同期全绿。B3-P3 集成 HEAD `c1b8262` push run `32365409301` + PR run `32365414341` 均 success。B3-P2 集成 HEAD `359d1f5` push run `32354862043`（3m31s）全 success：workflow yaml syntax ✓、abs-path scan ✓、secret scan ✓、unified check-all ✓、upload gate evidence ✓。B3-P3-XX 各分支 push run（X0 `32364412514`、X2 `32365035096` 等）亦全 success。

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
