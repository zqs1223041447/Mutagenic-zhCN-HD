# Combat Harness（Legacy 3.5.3）

`scripts/validate/combat_harness.py` 用来驱动旧 candidate 的 TestLevel 场景。**不是** Godot 4 Product 测试入口，也不表示要继续做 Kinetic 批次。

```text
python scripts/validate/combat_harness.py scenarios
python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <candidate.exe>
python tests/combat_harness/run_selfchecks.py
```

| 文件 | 角色 |
|---|---|
| `scripts/validate/combat_harness.py` | host 侧 driver |
| `scripts/validate/combat_scenarios.json` | 场景清单 |
| `scripts/validate/combat_telemetry_schema.json` | telemetry schema |
| `mods/k5-combat-harness/mod.json` | 把 driver 接到 TestLevel 的 Legacy MOD |
| `docs/ai/audits/B1-X5_COMBAT_HARNESS_SELFTEST_EVIDENCE.json` | 当时自测证据 |

路径从 `repo_root` 推导。不要改 `00_original` / `03_raw` / `04_recovered`。
