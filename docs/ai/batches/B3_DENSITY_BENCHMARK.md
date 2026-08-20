# B3-X3 Build Density Benchmark Scaffold

> **任务 ID**：B3-X3（Build Density Benchmark Scaffold）
> **分支/worktree**：`agent/b3-x3-density-benchmark` @ `<task_worktree>`
> **base_sha**：`68bb1c184dfab3a96554fd3d7c52581ef6c6a266`（= `batch/b3-anchor` = B2-I1 集成 HEAD）
> **合同来源**：`docs/ai/batches/B3_PLAN.md` §B3-X3（GPT 评审批准：只建性能场景/指标/阈值框架，不提高正式游戏密度）
> **状态**：框架完成，scaffold offline 自测 21/21 PASS；真实运行数据待 VM + benchmark-capable candidate

---

## 0. 本任务红线声明

> **当前不修改任何 gameplay 密度数值。**
>
> 本任务产出的是**基线框架**：压力阶梯定义、指标定义、阈值草案、可离线自测的 benchmark runner。
> 不新增游戏内系统、不改动 `mods/` 下任何 gameplay 数值、不改动既有 harness（`scripts/validate/combat_*`）、
> 不触碰 `00_original/03_raw/04_recovered`。真实 density 实验按 B3_PLAN §3 依赖 S2 PASS + S5 稳定后再启动，
> 届时只放宽/调整本框架声明的数值（先经真实数据校准阈值，再谈提升密度）。

---

## 1. 压力阶梯（场景矩阵）

同屏敌人压力阶梯 5 → 20 → 50 → 100，全部复用既有 harness 路由进入（见 §2），
每个级别是独立 JSON 场景定义（`scripts/benchmark/density_matrix.json` 的 `levels`），
与既有 combat scenario 同构（`id/version/summary/default_seed/duration_seconds/end_condition/spawn/player/mob_composition/asserts/proves/not_proven/requires/stress`）。

| Level id | 同屏敌人 | 组成（skeleton_warrior） | duration | default_seed | spread | stress |
|---|---|---|---|---|---|---|
| `density_5` | 5 | 5 | 60s | 2026083001 | 300px | true |
| `density_20` | 20 | 20 | 60s | 2026083002 | 300px | true |
| `density_50` | 50 | 50 | 60s | 2026083003 | 300px | true |
| `density_100` | 100 | 100 | 60s | 2026083004 | 300px | true |

- `spawn.mode = ladder`（x=0, y=0, wave=1），并列到既有 `cluster_kill_20` 的 300px 集群脚印；
- 计划渲染复用 `combat_harness.build_plan`（带 seed 的确定性 RNG），mob resource 取自
  `scripts/validate/combat_scenarios.json` 的 `mob_resources`（零复制、单一事实源）；
- 每个级别 4 条 required 断言：`boot_ok` / 全部生成 / 全部击杀 / `duplicate_deaths == 0`；
  + 1 条 optional 草案断言 `draft_fps_floor >= 30`（与既有 `cluster_kill_20` fps_floor 同值）。

## 2. 场景进入方式（复用 goto_test_level，不新建游戏内系统）

| 项 | 值 |
|---|---|
| 路由 | `goto_test_level` |
| 机制 | 复用 `scripts/validate/launch_harness_game.py` 的既有键位序列（Enter/Enter/F10，即 goto_test_level 真实键位）进入 TestLevel；k5-combat-harness `ScenarioDirector.gd` 消费 `game_request`（scenario_id/seed/duration/plan with res+x+y+count）并写出 telemetry |
| 新游戏内系统 | **none**（`density_matrix.json` `entrance.new_in_game_system = "none"`，selftest 强制校验） |
| runner 默认 launcher | `density_benchmark.py run --scenario <n> --candidate <exe> --apdata <vm_dir>` 时自动组装 `launch_harness_game.py --request … --candidate … --expected-telemetry … --apdata …`；也可用 `--launch` 传入自定义 VM hook |

## 3. 指标定义

指标分两层：**计算层**（host 侧纯函数，无论如何都能算）与**精确层**（benchmark envelope，需要 benchmark-capable candidate 在游戏内产出）。

### 3.1 frame-time（avg / p95 / p99，单位 ms）

| 字段 | 精确层（`metrics.frame_time`） | 计算层（legacy 遥测回退） |
|---|---|---|
| avg_ms | 游戏内原始帧样本均值 | `1000 / perf.fps_avg` |
| p95_ms | 游戏内原始帧样本 P95 | `perf.frame_pacing_p95_ms`（既有遥测已有） |
| p99_ms | 游戏内原始帧样本 P99 | `perf.frame_pacing_p99_ms`（envelope 新增，可选） |
| max_ms | 最差单帧 | `perf.frame_pacing_max_ms`（envelope 新增，可选） |

### 3.2 FPS（avg / min / p1）

- avg：`perf.fps_avg`（既有）或 envelope `metrics.fps.avg`；
- min：`perf.fps_min`（既有）；
- p1：`perf.fps_p1`（envelope 新增，可选）——1% 长尾帧保护。

### 3.3 event-rate（事件频率，复用 event spine）

- 语义源：B2-X1 Combat Event Spine（`_spine_record` 单总线，`_spine_last_events` 环缓冲每帧 64 上限、seq 水位消费）；
- **精确层**：`metrics.event_rate.events_total`（游戏内 spine seq 收割）→ `events_per_second = events_total / duration_seconds`（host 侧重算）；
- **计算层**（legacy 遥测回退，标记 `derived=true`）：`sum(counters.damage_events + melee_hits + crits + projectiles + triggers) / duration_seconds`；
- **不新建总线**：事件仍走既有 spine/ScenarioDirector telemetry 路径，runner 只做收割口径定义与换算。

### 3.4 voice budget（k4 单漏斗 16 voice）

- 语义源：B1 `k4-audio-foundation`（60ms 流级聚合、**16 concurrent voice budget**、pitch/volume variation、`tree_exited` 回收）；B2-X6 各层窗口叠加其上；
- 口径：`metrics.voice_budget.max_concurrent`（实测最大并发 voice）与 `metrics.voice_budget.over_budget_count`（超 16 的样本数，漏斗语义下应为 0）；
- 预算与密度无关：k4 漏斗是**固定预算**，阶梯只观察它在高密度下是否被击穿。

### 3.5 camera budget（X5 impulse 预算）

- 语义源：B2-X5 Camera Impulse 聚合器（`get_camera_impulse_telemetry()`）；
- 固定预算常量：`IMPULSE_BUDGET_MAX = 4.0`、`IMPULSE_MAX_OFFSET = 3.5`、`IMPULSE_WINDOW_MS = 250`、`IMPULSE_DECAY_PER_SEC = 9.0`、cluster 附录上限 `2.0`；
- 口径：`metrics.camera_budget.max_amplitude`（≤4.0）、`max_offset`（≤3.5）、`capped_amplitude_count`、`capped_offset_count`（钳制次数）、`impulses_total`（供钳制占比计算）。

## 4. 阈值草案（需真实数据校准）

> 全部为**草案**（`thresholds.draft = true`，selftest 强制），**只报告、不打分、不 gate PASS/FAIL**；
> 评分只由各级别 required 断言决定。校准流程见 §6。

| 指标 | 草案阈值 | 依据 |
|---|---|---|
| frame_time p95 | ≤ 33.33ms | 30fps 地板等效（与既有 `fps_floor = 30` 草案一致） |
| frame_time p99 | ≤ 50ms | 尾部帧保护草案 |
| fps avg | ≥ 30 | 与 `cluster_kill_20` 既有草案同值 |
| fps p1 | ≥ 20 | 长尾帧保护草案 |
| event_rate | 只记录不设上限 | 峰值由聚合/预算机制（voice 16 / camera clamp / X6 层窗口）吸收 |
| voice max_concurrent | ≤ 16 | k4 单漏斗固定预算 |
| voice over_budget_count | == 0 | 任意超预算即丧失漏斗语义 |
| camera max_amplitude | ≤ 4.0 | X5 `IMPULSE_BUDGET_MAX` |
| camera max_offset | ≤ 3.5 | X5 `IMPULSE_MAX_OFFSET` 安全帽 |
| camera capped_ratio | ≤ 0.1（capped_amplitude_count / impulses_total） | 钳制占比草案 |

阈值表机器可读于 `scripts/benchmark/density_matrix.json` → `thresholds`（每条带 `rationale` 与 `draft: true`）。

## 5. 执行方法

### 5.1 脚手架离线验证（无需 VM；本任务验收路径）

```powershell
# 1) 21 项 offline 自测（含矩阵契约/阶梯计数/确定性/dry-run 骨架/envelope 校验/
#     legacy 派生/阈值评估/双 schema 兼容/进入复用/mods 未动/abs-path/secret）
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py selftest

# 2) dry-run 骨架（不 launch，产出 request + NOT_PROVEN report，退出码 3）
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py run --scenario 100 --dry-run
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py run --scenario 100 --candidate <exe> --dry-run --json

# 3) 查看矩阵/级别/确定性计划
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py levels
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py describe --scenario 50
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py plan --scenario 100 --seed 2026083004
```

### 5.2 真实运行（需 S2 PASS + VM + benchmark-capable candidate；B3 后续批次）

```powershell
# 默认 launcher（自动组装 launch_harness_game.py），或 --launch 自定 VM hook
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py run --scenario 100 --candidate <candidate_exe> --apdata <vm_apdata_dir>
venv\Scripts\python.exe scripts\benchmark\density_benchmark.py run --scenario 5   --candidate <candidate_exe> --launch "<vm hook>"
```

### 5.3 日志位置与证据命名（10_logs/ 不入库）

| 内容 | 路径（相对 repo root） |
|---|---|
| game_request / 计划包 | `10_logs/benchmark/requests/density_<n>_<seed>.json` |
| 遥测（运行产出或 copy） | `10_logs/benchmark/telemetry/density_<n>_<seed>.json` |
| 结构化证据报告 | `10_logs/benchmark/reports/density_<n>_<seed>_<PASS|FAIL|NOT_PROVEN>.json` |
| 自测证据 | `10_logs/benchmark_selfcheck/density_benchmark_selfcheck_evidence.json` |

报告包含：level/seed/plan_sha256/candidate/modset/entrance/timestamps/metrics/thresholds
（draft + evaluations + summary）/assertions/result/exit_code/proves/not_proven/evidence_paths；
`--json` 可直接在 stdout 打印同一结构化 JSON 摘要。

## 6. 校准与后续（明确留给后续批次）

1. 真实数据采集：在 VM 上用 benchmark-capable candidate 跑 5/20/50/100（每级 ≥3 次取稳定），
   产出 envelope telemetry；legacy 遥测只做 derived 参考，不用于定阈值；
2. 阈值固化：以 L1（density_5）实测为地板，p95/p99/voice/camera 按固定预算主张对齐，
   fps/event-rate 按密度曲线定拦截线；固化前 `draft: true` 保持不变；
3. 正式密度实验：阈值固化后才允许提 gameplay density 数值（新 MOD/CODE_PATCH，走 canonical pipeline），
   以本框架做前后对比回归；
4. 注册到控制面：`scripts/ai/check_all_components.json` 增加
   `{id: density_benchmark_selftests, kind: python, relpath: scripts/benchmark/density_benchmark_selftests.py}`
   （属于 B3-X1/X3 集成期动作，本任务不抢先改动注册表）。

## 7. 复用关系与总线声明

| 能力 | 复用源 | 本任务动作 |
|---|---|---|
| 场景/计划契约与 seed 确定性 | `scripts/validate/combat_harness.py`（build_plan / 断言 / 退出码 / schema 校验） | 直接 import 复用（零改动） |
| mob resources 单一事实源 | `scripts/validate/combat_scenarios.json` | 读取复用（零改动） |
| 场景进入 | `scripts/validate/launch_harness_game.py`（goto_test_level 键位序列） | 默认 launcher 组装（零改动） |
| 遥测单总线 | k5 ScenarioDirector → combat telemetry（event spine 单总线） | 定义 benchmark envelope（`density_telemetry_schema.json`，base schema 的超集） |
| 事件语义 | B2-X1 event spine | 只做收割口径与 event-rate 换算 |
| voice 预算 | B1 k4 单漏斗 16 voice | 只做 gauge 口径 |
| camera 预算 | B2-X5 impulse 聚合器 | 只做 gauge 口径 |

**新总线：无。** 新增契约面只有三处：`density_matrix.json`（压力阶梯）、
`density_telemetry_schema.json`（测量信封，可选字段）、`density_benchmark.py`（host 侧 runner），
且 envelope 与 base combat schema 的兼容性由 selftest `base_schema_compat` 强制。

## 8. 验证记录（本任务验收）

| 门 | 结果 |
|---|---|
| offline selftest（venv，无 VM） | 21/21 PASS（exit 0），证据 `10_logs/benchmark_selfcheck/density_benchmark_selfcheck_evidence.json` |
| dry-run（--scenario 5/20/50/100） | request + NOT_PROVEN 骨架（exit 3），含 `--json` 结构化摘要 |
| 合成遥测正向演示 | density_50 fixture → PASS（exit 0），metrics/thresholds 全量评估 |
| repo-wide abs-path scan | production_hardcode = 0 |
| repo-wide secret scan | findings = 0 |
| mods/ 未动 | `git status -- mods/` 空；本任务 diff 无 mods/ 路径 |
| 既有 harness 回归 | combat_harness 及其 selftest 未改动（无回归面） |
| 真实密度数据 | 不要求 VM 即可验证框架本身；真实运行数据留后续批次（见 §6） |