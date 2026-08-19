# B1-X5 Combat Test Harness — 使用说明

> **任务**：B1-X5（Combat Test Harness & Automation）
> **权威层级**：L2 工具文档；低于 `AGENTS.md` / `status.json`。
> **范围**：把 TestLevel 发展为可重复、尽可能无人值守的 Combat Vertical Slice 验证环境。
> **只读边界**：不修改 `00_original/03_raw/04_recovered`；不修改 Player/Mob/GenericSkill 核心逻辑（X1/X2/X3/X4 preimage 由各自分支持有）。
> **状态**：driver/telemetry/自测已落地（S0 静态/结构自测 PASS）；真实游戏内运行在本机未执行，标 NOT RUN（见下）。

---

## 1. 一句话

> 一条命令一个意图：

```text
python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <candidate.exe>
```

不需要手工点菜单、不需要手工整理日志、不需要输入宿主绝对路径。

## 2. 交付文件

| 文件 | 角色 |
|---|---|
| `scripts/validate/combat_harness.py` | 确定性 scenario driver（host 侧）：解析 catalog、生成 seed 化 spawn plan、校验 telemetry、评估断言、输出 evidence 报告与退出码 |
| `scripts/validate/combat_scenarios.json` | scenario 清单（Source of Truth，8 个第一批场景） |
| `scripts/validate/combat_telemetry_schema.json` | telemetry 最小合同（机器可读 schema，版本 1.0） |
| `scripts/validate/combat_harness_selftests.py` | 静态/结构自测（无游戏也可跑），产出 evidence JSON |
| `tests/combat_harness/run_selfchecks.py` | 自测入口包装（repo root 自动解析） |
| `docs/ai/audits/B1-X5_COMBAT_HARNESS_SELFTEST_EVIDENCE.json` | 本批次自测证据（真实运行结果） |
| `test_fixtures/combat_harness/ScenarioDirector.gd` | 游戏内 reference fixture（已 GDRE 3.5.0 编译验证；与 MOD 内嵌逻辑同步维护） |
| `mods/k5-combat-harness/mod.json` | 声明式 MOD：TestLevel.gd 接入 scenario driver（零新增 res:// 路径，roundtrip 3744 保持；已通过 apply_mod preimage 守卫 + GDRE 编译验证） |

## 3. 快速开始

```text
# 列出全部 scenario
python scripts/validate/combat_harness.py scenarios

# 查看某个 scenario 定义
python scripts/validate/combat_harness.py describe --scenario cluster_kill_20

# 渲染 seed 化 spawn plan（同 seed 输出字节级一致，可用 --raw 单行）
python scripts/validate/combat_harness.py plan --scenario cluster_kill_20 --seed 2026082005

# 对候选 EXE 跑一个 scenario（无运行环境时产出 NOT_PROVEN 骨架报告）
python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <candidate.exe>

# 带启动器（VM/游戏脚本）全自动跑：启动器负责拉起游戏；游戏结束后 driver 读取 telemetry 并判定
python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <candidate.exe> --launch "powershell scripts/vm/run_scenario.ps1 -Scenario cluster_kill_20"

# 静态/结构自测（venv python，无游戏依赖）
python scripts/validate/combat_harness.py selfcheck
python tests/combat_harness/run_selfchecks.py
```

## 4. 第一批 scenario 清单

| scenario id | 意图 | 组成 | 结束条件 | 关键断言（required） |
|---|---|---|---|---|
| `movement_dash_smoke` | 移动/Dash 冒烟 | 无怪 | 30s 超时 | boot.ok |
| `single_melee_hit` | 单近战直接命中基线 | 1 SkeletonWarrior | 全灭或 20s | boot.ok、spawned>=1 |
| `single_ranged_pack` | 远程 pack 基线 | 3 SkeletonArcher | 全灭或 30s | boot.ok、spawned>=3 |
| `rapid_hit_10s` | 10 秒高频受击浸泡 | 5 SkeletonWarrior | 10s 超时 | boot.ok |
| `cluster_kill_20` | **旗舰** 5–20 群杀切片 | 10 近战 + 5 远程 + 5 Zombie | 全灭或 60s | boot.ok、spawned>=20、killed>=20、duplicate_deaths==0 |
| `projectile_density` | 高投射物密度浸泡 | 8 Zombie | 30s 超时 | boot.ok |
| `chain_pierce_trigger` | 链/穿/触发样本 | 6 Zombie | 全灭或 30s | boot.ok、duplicate_deaths==0 |
| `stress_random_300` | 保留原随机 300 压力场景 | 300 random（明确 seed） | 60s 超时 | boot.ok、spawned>=300 |

`optional` 能力（damage_events / triggers / projectiles / fps / dashes / player_moves 等）由游戏内 fixture 能测就测、不能测记为 `not_measured`，**不影响 PASS/FAIL 判定**（只记录）。

## 5. Telemetry 最小合同（v1.0）

游戏内 fixture 运行结束后必须产出 telemetry JSON，driver 校验后评估：

```json
{
  "schema_version": "1.0",
  "scenario_id": "cluster_kill_20",
  "seed": 2026082005,
  "started_at": "...Z",
  "ended_at": "...Z",
  "boot": {"ok": true, "fatal_count": 0, "alert_count": 0},
  "counters": {"spawned": 20, "alive": 0, "killed": 20, "duplicate_deaths": 0,
               "damage_events": 40, "melee_hits": 30, "crits": 2,
               "projectiles": 10, "triggers": 0, "player_moves": 50, "dashes": 4},
  "perf": {"frames": 1800, "fps_avg": 60.0, "fps_min": 55.0, "fps_max": 62.0, "frame_pacing_p95_ms": 17.5},
  "capture": {"screenshots": ["..."], "video": null},
  "runtime": {"exit_code": 0, "in_game_result": "PASS", "notes": []}
}
```

合同字段全量定义见 `scripts/validate/combat_telemetry_schema.json`；root 必填：`schema_version / scenario_id / seed / started_at / ended_at / boot / counters / runtime`；counters 必填：`spawned / alive / killed / duplicate_deaths`。scenario_id/seed 与请求不符或 schema 违规 → 判定 NOT_PROVEN。

## 6. 结果与退出码（契约）

| 退出码 | 含义 | 触发 |
|---|---|---|
| 0 | PASS | telemetry 有效，所有 required 断言测得且满足 |
| 2 | FAIL | 至少一个 required 断言测得且违反 |
| 3 | NOT_PROVEN | 未运行 / telemetry 缺失或无效 / required 字段未测得 |
| 1 | SELFTEST_FAIL | `selfcheck` 内部断言失败 |
| 4 | USAGE | 参数/场景/候选引用错误 |

每个 `run` 在 `<out-dir>/reports/<scenario>_<seed>_<RESULT>.json` 落一份 evidence 报告，包含：scenario/seed、candidate sha256 + repo HEAD SHA + modset、起止时间戳、boot/fatal、spawned/alive/killed、duplicate death、damage/trigger 计数、frame/FPS、screenshot 路径、exit code、逐断言表、`proves` / `not_proven`（证明什么/不证明什么）。默认 out-dir 为 `<repo_root>/10_logs/combat_harness`（git-ignored，不入库）。

## 7. 确定性契约

- scenario 定义（id/seed/composition/spawn 几何/断言）全部显式声明于 `combat_scenarios.json`；
- host 侧 `plan` 子命令用 Python `random.Random(seed)` 渲染 spawn 计划，同 seed 字节级一致（自测锁定）；
- 游戏内 fixture 用 Godot `seed()` 同 seed 复现摆放与选择，telemetry 回传；
- `stress_random_300` 是唯一“随机组成”场景（保留原 ladder 压力行为），其 seed 同样显式；
- plan 版本号 `plan_version=1`；将来如需改变摆放算法必须升版本，避免静默破坏同 seed 复现。

## 8. 游戏内运行（NOT RUN 状态说明）

本机当前无 VM/Godot 运行环境，真实游戏内运行**未执行**，因此任何 `run` 在没有 telemetry 输入时产出 **NOT_PROVEN**（这是契约行为，不是失败）。接入运行环境的两个必备件已就绪：

1. **游戏内 reference fixture** `test_fixtures/combat_harness/ScenarioDirector.gd`：读请求 JSON（含 scenario 定义 + seed + plan）、Godot seed、按 plan 刷怪、统计 counters/perf、写 telemetry JSON；
2. **声明式 MOD** `mods/k5-combat-harness/mod.json`：CODE_PATCH 仅改 `Scenes/Levels/TestLevel/TestLevel.gd`（X5 自有主范围），`_ready()` 委托给 director；请求经 `user://combat_harness/request_<scenario>_<seed>.json` 传入，telemetry 写 `user://combat_harness/telemetry_<scenario>_<seed>.json`；无请求文件时保持原 stress_random_300 行为（向后兼容）。

接入步骤（运行环境就绪后）：
1. canonical build `mods/k5-combat-harness` → candidate；
2. 宿主把用户数据目录（Godot `user://` 对应目录）映射/同步到 `<out-dir>/userdata`（P7 已有 isolated-APPDATA 先例）；
3. `python scripts/validate/combat_harness.py run --scenario X --candidate <candidate> --launch "..."`；
4. driver 读到 telemetry 后自动完成 S1(boot/fatal)/S4(combat semantic counters) 判定并落报告。

## 9. 与 sibling 边界

- X1（Player response）/X2（Mob hit reaction）/X3（Skill/Projectile/TCE）/X4（Camera/Audio）：X5 不修改这些文件、不抢其 preimage；X5 只提供可重复 scenario/driver/telemetry；
- 本任务不改动任何 `04_recovered` 内容；TestLevel 接入以声明式 MOD 形式存在；
- 潜在冲突路径：`Scenes/Levels/TestLevel/TestLevel.gd`（X5 MOD 唯一 patch 目标，sibling 无涉）；`scripts/validate/` 与 X0 的 `scripts/ai/` 无文件重叠。

## 10. 证明什么 / 不证明什么

**已证明（本机自测，证据：`docs/ai/audits/B1-X5_COMBAT_HARNESS_SELFTEST_EVIDENCE.json`）**：
- 8 个 scenario 定义可解析且契约字段完整；seed 确定性（同 seed 同 plan，异 seed 异 plan；`plan` CLI 输出字节级一致）；
- dry-run 骨架报告包含 telemetry 合同全部字段，结果 NOT_PROVEN、退出码 3；
- telemetry 有效→PASS(0)；required 违反→FAIL(2)；schema 违规/缺失→NOT_PROVEN(3)；
- 错误场景（未知 scenario / 缺 candidate）非零退出码；任意 cwd 可启动；X5 文件无宿主绝对路径、无 secret 样 token；
- **MOD 载荷可应用且可编译**：`mods/k5-combat-harness` 经 `scripts/patch/apply_mod.py` 以 TestLevel.gd 全文件 preimage（0bc68d4e…）守卫应用 PASS（occurrence=1），补丁后脚本与 `ScenarioDirector.gd` fixture 均经 GDRE `--bytecode=3.5.0-stable` 编译成功（TestLevel.gd 编译前 631B→应用后 4.4KB，无语法错误）。

**尚未证明（NOT RUN / 需运行环境）**：
- 真实游戏内 boot、真实 spawn/kill/death 计数、真实 FPS/frame pacing、真实 duplicate-death 行为；
- k5-combat-harness MOD 的 candidate 构建（pack/embed/boot）；
- 任何 Combat 手感（属 S5 人工 Gate）。
