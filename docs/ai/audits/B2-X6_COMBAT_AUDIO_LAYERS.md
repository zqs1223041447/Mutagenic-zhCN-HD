# B2-X6 Combat Audio Layers v1 审计

> 任务：B2-X6（Combat Audio Layers v1）
> 基线：`ea7854f6ad0602da52e06ab5b5e475fbc79f1e23`（batch/b2-waveb-anchor）
> 分支/worktree：`agent/b2-x6-combat-audio-layers` @ `<task_worktree>`
> 可运行契约：`scripts/validate/semantic_combat_audio_contract.py`
> 自测：`tests/combat_audio/test_combat_audio_layers.py`
> 审计级别：C0 静态 + 契约/策略模型模拟（只读 `04_recovered` + `mods/`，无运行 / 无 VM）

---

## 1. 目标

在 B1 `k4-audio-foundation`（60ms 流级聚合、16 concurrent voice budget、pitch/volume variation、`tree_exited` 计数回收）与 B2-X1 Combat Event Spine（`direct_hit` / `dot_tick` / `crit` / `kill` 事件语义）之上，建立事件分层的 combat audio：

- **light 层**：direct hit -> `Sounds/Hits/PUNCH_CLEAN_LIGHT_02.wav`，窗口 100ms；
- **heavy 层**：crit -> `Sounds/Hits/ice_crack.wav`，窗口 150ms；
- **kill 层**：kill -> `Sounds/SFX/blood_explosion.wav`，窗口 300ms + 集群聚合（同一 300ms 窗口内 >=3 kill 只出 1 声；窗口首声播，其余抑制）；
- **dot_tick**：直接抑制（DoT 不按 tick 产生 impact spam）；
- **kill 层玩家过滤**：只有击杀者是玩家才播 kill 声（玩家死亡 / 敌人互相击杀不出 kill 层音效）。

约束执行：
- 所有音频仍只经 k4 `play_sound_effect` 收口（voice budget / tree_exited / 60ms 流级聚合 / variation 原样保留）；
- 不改伤害数值、不改事件语义、不复制第二总线、不新增二进制资产；
- 不 build / pack / boot（B2-X3 集成阶段做 aggregate）。

## 2. 范围与责任边界

| 文件 | 归属 | 处置 |
|---|---|---|
| `Globals/Globals.gd` | B1 k4（sound_effect/rare_orb_sfx 区、play_sound_effect 区） | 只读审计 + 2 个新增 CODE_PATCH（锚点 `var selected_character_name = "default"` 与 `func play_orb_sound(orb_type):`，与 k4 区域零重叠） |
| `Scenes/Stats.gd` | X1 spine + X6 drain | 只读审计 + 3 个新增 CODE_PATCH（锚点 `var accumulated_time = 0`、`func _physics_process` 签名、apply_damage return 块；与 feat-tce / feat-tce-context / b2-x1 区域零重叠） |
| `mods/feat-tce`、`mods/feat-tce-context`、`mods/b2-x1-combat-event-spine`、`mods/k4-audio-foundation` | 依赖链 | 只读依赖（契约内模拟整链应用） |
| 声音资产 | `04_recovered/Sounds/` | 只读复用（3 个既有 wav，零新增） |

新 MOD：`mods/b2-x6-combat-audio-layers`（CODE_PATCH，dependencies: `b2-x1-combat-event-spine` + `k4-audio-foundation`）。

## 3. 分层策略 v1

### 3.1 事件 -> 层映射（唯一事实源 = `Globals.play_combat_event`）

| event_class | 层 | 流 | 窗口 | 语义 |
|---|---|---|---|---|
| `direct_hit` | light | PUNCH_CLEAN_LIGHT_02.wav（未被他处使用） | 100ms | <=10 声/秒，不形成音频机枪；零伤害命中（multiplier=0）无事件、无声音 |
| `crit` | heavy | ice_crack.wav（未被他处使用） | 150ms | crit 与普通 hit 听觉可区分 |
| `kill` | kill | blood_explosion.wav（仅 BloodExplosion.gd 在击杀特效场景使用） | 300ms | 与 hit 流完全不同；集群聚合 <=1 声/300ms |
| `dot_tick` | - | - | - | 直接 return，无每 tick impact |

### 3.2 分层窗口与集群聚合

- 每层独立 `_combat_audio_last_played[layer]` 时间窗；窗口未过 -> 静默（含同帧多事件）。
- kill 集群：`_combat_audio_allow_kill_cluster` 以窗口内**首个 kill 的时间**为窗起点；窗内 `count > threshold(3)` 直接 false；最终 `return count == 1` -> 窗口内仅首声播放，2..N 全部抑制 -> **>=3 kill 汇聚为单声**（聚合语义）。
- 层窗口（100/150/300ms）叠加在 k4 的 60ms 流级聚合之上（k4 仍每流 60ms 防回声、16 并发封顶、pitch/volume variation 照旧）。
- kill 层玩家过滤：`record.source` 为击杀者 Stats；`killer == null or not killer.is_player` -> return（玩家死亡不播 kill 声、敌人互杀不播）。

### 3.3 事件消费（Stats.gd drain）

- 消费点：`_combat_audio_drain_spine_events()`，注入在 **apply_damage return 块之前**（X1 未触碰锚点），`_physics_process` 签名前定义。
- 增量语义：`_combat_audio_consumed_seq` 实例级水位；`_spine_event_seq <= 水位` 早退，环缓冲只转发 `seq > 水位` 的新记录。
- **选择在 apply_damage 内同步 drain 而非 _physics_process 的原因**：X1 的 kill 记录写在**被击杀者实例**上；死亡经 `call_deferred("emit_signal", "died")` -> Mob `_on_death` -> `queue_free()`（同帧末）；纯 _physics_process drain 在部分树顺序下会错过最后一帧 kill 记录。apply_damage 末尾 drain 保证每条记录（含 kill）在产出当次调用内消费（幂等：seq 水位）。
- 每条记录被精确消费一次；重复调用天然幂等；任何 apply_damage 都产出至少一条 spine 记录（除 multiplier=0 零伤害路径——drain 早退，无声音，符合"无 impact"语义）。

## 4. Patch 清单（mods/b2-x6-combat-audio-layers）

| # | unit_id | 锚点（04_recovered 原始文本） | 增量 |
|---|---|---|---|
| G1 | globals::combat_audio_state | `var selected_character_name = "default"` (L14) | 追加 4 常量 + 3 state var + 3 preload |
| G2 | globals::play_combat_event_layer_policy | `func play_orb_sound(orb_type):` (L216) | 前置 play_combat_event + 4 个 helper |
| S1 | stats::drain_consumed_seq_var | `var accumulated_time = 0` (L88) | 追加 `_combat_audio_consumed_seq` |
| S2 | stats::drain_func_before_physics_process | `func _physics_process(delta: float) -> void :` (L253) | 前置 drain 函数 |
| S3 | stats::drain_call_before_return | apply_damage return 块 (L863-865) | return 前注入 drain 调用 |

所有 patch：`expected_occurrences == 1`，preimage 分别为对应原始文件整文件 SHA；行尾 LF。
锚点与 feat-tce / feat-tce-context / b2-x1 / k4 的 old_text/new_text 区域零重叠（契约内全链模拟 + 全 mods 横扫描，均程序化核验）。

## 5. 验证结果

### 5.1 semantic contract（venv python，可重复）

```
venv\Scripts\python.exe scripts/validate/semantic_combat_audio_contract.py
checks: 120/120 passed
verdict: PASS   (exit code 0)
```

覆盖：
- manifest 不变量（id / CODE_PATCH / 双依赖 / target_original_sha256 / patch 数 / 路径白名单 / preimage / occurrence）；
- 依赖链整链模拟（feat-tce -> feat-tce-context -> b2-x1 -> k4 -> X6，同 apply_mod 的 preimage+occurrence walk），X6 5 patch 在全链后仍逐字节唯一；
- canary：light/heavy/kill/dot_tick 映射；窗口 100/150/300；threshold=3；集群首声语义；kill 玩家过滤；play_combat_event 内唯一 play_sound_effect 漏斗；X6 不触碰 k4 limiter 内部（`_sfx_last_play`/`_sfx_active_count`）；drain 定义+调用各 1、seq 水位守卫、`Globals.play_combat_event(record)` 转发、drain 调用早于 apply_damage return（唯一 did_kill 键行作锚）；
- 无伤害/语义漂移（以**链后基线**为对照，隔离 X6 自身增量）：`*=`、`+= combined_effective_damage`、`on_kill(`、`trigger_effects(` 计数不变；apply_damage 签名不变；
- 3 个音频资产存在；X6 old/new 文本与任何其他 mod 同文件 patch 零交叉（全 mods 横扫描）；4 个 X6 文件无宿主绝对路径（`res://` 不会误报，正则已加 word-boundary 守卫）。

### 5.2 自测（policy model，venv python，可重复）

```
venv\Scripts\python.exe tests/combat_audio/test_combat_audio_layers.py
selftest checks: 14/14 passed
verdict: PASS (policy model)   (exit code 0)
```

覆盖（策略模型转录 + 从应用后 Globals.gd 提取常量驱动）：
- T1 机枪 hit：13 hit/500ms -> <=5 声（100ms 窗）；
- T2 crit 连发：<=4 声/500ms（150ms 窗）；
- T3 kill 集群：5 kill/200ms -> 恰 1 声（聚合语义）；
- T4 DoT tick：10 tick/500ms -> 0 声；
- T5 玩家死亡（killer 非玩家）-> 0 声；
- T6 light+kill 同帧 -> 双声（层独立）；
- T7 窗口重置后 kill 恢复发声；
- T8 100 混合事件/2s -> 32 声（<=34 层窗口理论上限，聚合生效）。

### 5.3 干跑证明（resolve + apply，10_logs 本地证据）

```
venv\Scripts\python.exe scripts/patch/resolve_mod_chain.py --manifest mods/b2-x6-combat-audio-layers/mod.json --mods-root mods --output 10_logs/b2-x6-dryrun/resolved-combat-audio.json --report 10_logs/b2-x6-dryrun/resolve_report.json
verdict: PASS   (resolution_order: feat-tce -> feat-tce-context -> b2-x1 -> k4 -> b2-x6, 34 patches, 0 asset overlay)

venv\Scripts\python.exe scripts/patch/apply_mod.py --base 04_recovered --manifest 10_logs/b2-x6-dryrun/resolved-combat-audio.json --out 10_logs/b2-x6-dryrun/combat_audio_worktree --report 10_logs/b2-x6-dryrun/apply_report.json
verdict: PASS   (changed_path_count=34, file_count=5058, recorded_at=2026-08-20T02:02:51+00:00)
```

产物抽查（工具落盘文件）：`Scenes/Stats.gd` L258 drain 定义 + L898 调用；`Globals/Globals.gd` L251 `play_combat_event`、L26 `COMBAT_KILL_CLUSTER_THRESHOLD = 3`、L297 集群闸门、`combat_sfx_kill` preload、`killer.is_player` 均在场。

## 6. 消费接口（X4/X5/B2-I1 后续）

1. 本 MOD 自身消费 X1 spine：`Globals.play_combat_event(record)` 接受 `_spine_record` 产出的完整 record dict（`event_class`/`seq`/`timestamp_ms`/`did_kill`/source/target/is_dot/did_crit/skill_parent）；未知 event_class 默认落 light 层（向前兼容）。
2. 分层可调参（v1 常量集中）：`COMBAT_LAYER_*_WINDOW_MS`、`COMBAT_KILL_CLUSTER_THRESHOLD`；音频流 preload 独立变量，替换即换音色，无需新资产。
3. 与 k4 的关系：X6 是 k4 之上的**策略层**；k4 仍保有每流 60ms 防回声、16 并发、pitch/volume variation、`tree_exited` 计数。X6 不注册新 autoload、不改 project.godot。
4. X4 Kill Feel 若做 kill 镜头/震动，可复用 kill 事件（X6 已含玩家过滤规则参考）。

## 7. 风险登记

- R1(low)：`play_combat_event` 同步调用链（apply_damage -> drain -> play_sound_effect -> add_child）——与既有 OnKill/BloodExplosion 同帧播放路径一致，无新增重入风险；每 apply_damage 一次水位检查为 O(1)（早退），仅在写记录时遍历环缓冲（<=64）。
- R2(low)：kill 层流 `blood_explosion.wav` 与 `BloodExplosion.gd`（击杀特效粒子）共用同一 preload 实例 -> k4 以实例 ID 聚合：同 60ms 内两者只出 1 声（语义同向：均为死亡冲击声，不冲突）。
- R3(info)：层窗口为 v1 手感常量，未做真实听感调优（S5 人工门在 B2-I1 后）。
- R4(info)：`killer.is_player` 依赖 Stats `is_player` 字段（原版已存在，19 处引用），无需新状态。
- R5(info)：玩家死亡 -> kill 记录在玩家实例 -> 被玩家过滤规则抑制（不播"自己杀死自己"的 kill 声）。

## 8. 未证明项（诚实声明）

- 真实游戏 runtime 音频行为（VM boot + harness telemetry 未跑；S1/S2 无 VM 环境）；
- GDScript 编译 / pack / boot（GDRE --compile 在 B2 中央集成 aggregate 阶段执行）；
- 听感平衡：层窗口 100/150/300 与三音色混音未人工验收（S5 HUMAN_ACCEPT 保留）；
- 与 X4/X5 同帧效果叠加后的整体手感（Wave B 并行，B2-I1 聚合验证）；
- `play_combat_event` 每帧调用频率上限的实测基准（策略模型证明窗口上限，未测真实引擎开销）。