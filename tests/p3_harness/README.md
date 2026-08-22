# P3 End-to-End Automation Harness

P3 可玩基线（角色 → 世界 → 战斗 → 拾取 → UI → 存档）的步骤化自动化验证驱动。
E4–E7 已接线到本车道交付的探针 CLI（implemented=true），E1/E2/E3/E8 的
runner 钩子仍预留，归编排车道填充，无需改动驱动代码。

沿用现有体系约定（扩展而非另造）：

- 退出码契约对齐 `scripts/validate/combat_harness.py`（0=PASS / 2=FAIL / 3=NOT_RUN / 4=USAGE）
- 报告为机器可读 JSON，带 `proves` / `not_proven` 字段（对齐 S3/S5 evidence 风格）
- runner 命令模板引用既有工具：boot probe、smoke probe、combat harness、s3 persistence gate、P3 探针

## 用法

```bash
# 全部步骤（E4-E7 会真实执行探针；引擎不可用时记 FAIL/BLOCKED）
python tests/p3_harness/p3_e2e.py

# 选择性执行
python tests/p3_harness/p3_e2e.py --steps E1,E3

# stdout 只输出机器可读 JSON
python tests/p3_harness/p3_e2e.py --json-only

# 指定报告输出路径（默认 runtime/p3_harness_report.json）
python tests/p3_harness/p3_e2e.py --out path/to/report.json

# 列出步骤与 runner 就绪状态
python tests/p3_harness/p3_e2e.py --list-steps
```

CLI 参数：

| 参数 | 说明 |
| --- | --- |
| `--out PATH` | JSON 报告路径，默认 `runtime/p3_harness_report.json`（相对仓库根） |
| `--steps E1,E3` | 逗号分隔的子集；未选中的步骤在报告中记为 `SKIP` |
| `--config PATH` | 覆盖默认 config（默认 `tests/p3_harness/config.json`） |
| `--json-only` | stdout 仅打印完整 JSON 报告 |
| `--list-steps` | 打印步骤清单与就绪状态后退出 |

## 步骤与 P3 Exit Criteria 对照表

| 步骤 | Exit Criterion | 断言内容 | 当前状态 | 预期 runner |
| --- | --- | --- | --- | --- |
| E1 | LoadGame 到达角色可选/已选 | 启动产品到达角色选择态，无阻断错误 | NOT_RUN | boot probe + 角色选择标记断言 |
| E2 | 进入 TestLevel 无阻断错误 | TestLevel 加载 reached 且无 fatal 签名 | NOT_RUN | smoke probe（scenes=test_level） |
| E3 | 移动+Dash 位置断言 | move/dash 输入后的位移符合声明增量 | NOT_RUN | combat harness `movement_dash_smoke` |
| E4 | 释放主动技能产生战斗事件 | 技能伤害 bundle 使怪物 HP 下降 | **PASS（已接线）** | `scripts/validate/p3_combat_probe.py` |
| E5 | 击杀怪物 | HP 归零触发 died 信号 + 尸体移除 | **PASS（已接线）** | `scripts/validate/p3_combat_probe.py` |
| E6 | 拾取掉落进库存 | 碰撞拾取后进入可查询库存（orbs 计数） | **PASS（已接线）** | `scripts/validate/p3_loot_probe.py` |
| E7 | 技能界面+被动树界面打开不崩溃 | 两界面经 PopupManager 打开/关闭，栈清零 | **PASS（已接线）** | `scripts/validate/p3_ui_probe.py` |
| E8 | Save→Load 关键状态恢复 | 存档-读档语义关键状态一致 | NOT_RUN | s3 persistence gate |

E1/E2/E3/E8 的 config 条目归编排车道；本车道只接了 E4–E7。

## 探针说明（P3-C/D/E）

三个探针均为 headless driver scene + Python CLI 包装：

| 探针 | Driver scene | CLI | 证据 |
| --- | --- | --- | --- |
| 战斗 E4/E5 | `res://scenes/Mobs/probes/p3_combat_probe.tscn` | `python scripts/validate/p3_combat_probe.py` | `migration/conversion/p3_c_combat.json` |
| 拾取 E6 | `res://scenes/UI/probes/p3_loot_probe.tscn` | `python scripts/validate/p3_loot_probe.py` | `migration/conversion/p3_d_loot.json` |
| UI E7 | `res://scenes/UI/probes/p3_ui_probe.tscn` | `python scripts/validate/p3_ui_probe.py` | `migration/conversion/p3_e_ui.json` |

已知残留（如实记录）：

- 战斗探针证据中有 1 条非致命 SCRIPT ERROR：`FloatingDamageManager` 的
  `interpolate_property`（G3 Tween API 残留，位于 product/scenes/Particles/**，
  超出本车道写域，未修）。
- E6 的掉落物是测试桩：真实 Pickups 场景（OrbPickup/GenePickup/PortalPickup）
  的恢复归另一车道所有（本会话中期仅部分落地）；拾取碰撞契约与库存入账
  （Stats.add_orb）均为真实生产代码。
- Projectiles/Skills 下多个 `_ready` override 未调用 `super._ready()`
  （G3→G4 行为差异），影响玩家施法弹道链路；MobSkill 已修复（E4/E5 所需），
  其余留给后续 attempt。

## 为什么 E1/E2/E3/E8 仍是 NOT_RUN

1. **runner 未接线**：E1–E3、E8 的命令模板已指向既有工具，但 attempt 还需补齐
   candidate/launch/标记断言等参数；这些条目归编排车道所有，本车道不动。
2. 整跑结果为 `NOT_RUN`（退出码 3）当且仅当没有任何步骤产生 PASS/FAIL；
   现在 E4–E7 已接线并通过，全量运行会得到 PASS（前提是引擎可用）。

## 报告 schema

```json
{
  "harness_id": "P3-E2E",
  "schema_version": "1.0",
  "ran_at": "2026-08-22T00:00:00Z",
  "repo_head_sha": "<git sha 或 null>",
  "selected_steps": ["E1", "E2"],
  "steps": [
    {
      "step_id": "E1",
      "status": "NOT_RUN",
      "detail": "runner hook reserved (implemented=false); ...",
      "evidence_path": null
    }
  ],
  "summary": {"total": 8, "pass": 0, "fail": 0, "not_run": 8, "skip": 0},
  "result": "NOT_RUN",
  "proves": "...",
  "not_proven": "..."
}
```

- 每步固定四个字段：`step_id` / `status`（PASS|FAIL|NOT_RUN|SKIP）/ `detail` /
  `evidence_path`（无证据时为 null）。
- 整体 `result`：任一 FAIL → FAIL；否则存在 PASS → PASS；否则 NOT_RUN。

## 如何填充一个步骤（后续 attempt）

1. 在 `config.json` 找到对应步骤的 `runner`。
2. 把 `implemented` 改为 `true`，按需修改 `command_template`。
3. 可用占位符（由驱动渲染）：`{python}` `{repo_root}` `{product_dir}`
   `{godot_bin}` `{report}` `{out_dir}` `{evidence_dir}` `{step_evidence}`，
   场景：`{load_game_scene}` `{menu_scene}` `{test_level_scene}`，
   工具：`{boot_probe}` `{smoke_probe}` `{combat_harness}`
   `{s3_persistence_gate}` `{p3_combat_probe}` `{p3_loot_probe}`
   `{p3_ui_probe}`。
4. runner 以 `rc==0 → PASS`、非 0 → FAIL 分类；超时/派生失败记 FAIL；
   `{step_evidence}` 渲染出的文件若真实存在则写入 `evidence_path`。

## 单元测试

```bash
pytest scripts/ai/tests/test_p3_harness.py
```

覆盖：报告 schema 校验、`--steps` 选择逻辑、NOT_RUN 默认行为、runner 钩子
执行分类（注入 fake run，绝不触碰 Godot）、config 结构契约与源码卫生。
