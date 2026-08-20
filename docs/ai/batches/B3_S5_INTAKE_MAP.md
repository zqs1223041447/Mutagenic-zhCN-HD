# B3 S5 Feedback Intake Map —— 8 项人工验收 → Combat Tunable → Semantic Contract → Regression 映射

> **运行任务**：B3-P1-X2（S5 Feedback Intake）
> **branch**：`agent/b3-p1-x2`
> **base_sha**：`de039a6ce0c86e0c104268f359f3279f7c2ef3a9`
> **状态**：MAPPING ONLY（本文件只产出映射，**不修改任何 mods/ 下 gameplay 数值**）
> **上游依赖**：B3-P0 已完成——`check_all` 已注册 12 组件（B3-X1 闭环），Human S5 gate 保持 HUMAN_REQUIRED（B3_STATUS：8 项人工 A/B 验收等待用户反馈）

## 0. 目的与边界

用户按 8 项人工验收清单逐项反馈 PASS/FAIL 后，本文件把**每一项反馈**直接翻译成：

1. 所属系统（Kill Feel / Camera Impulse / Combat Audio）与**具体 tunable 参数**（当前值 + 建议允许调整范围，范围基于契约约束推导）；
2. 影响该参数的 **semantic contract**（断言点文件:行号）；
3. 该项 FAIL 时需要重跑的 **Gate**（至少对应契约 + `check_all`；修改 mod.json 即需 rebuild → 新 candidate）；
4. 每个 tunable 的**调参影响面**（哪些契约断言/阈值会随参数变化而需同步更新）；
5. FAIL → 自动生成调参任务（B3 Combat Polish 系列，`B3-CP<NN>`）的模板。

**权限边界**：本任务不调参、不改 gameplay、不写 HUMAN_ACCEPTED、不触碰 `00_original/03_raw/04_recovered`。本文档仓库内路径均为 repo-relative，不含宿主绝对路径。

**所有参数当前值均已逐字核对** 自 `mods/b2-x4-kill-feel/mod.json`、`mods/b2-x5-camera-impulse/mod.json`、`mods/b2-x6-combat-audio-layers/mod.json` 的实际 patch 载荷（含被截断展示的长行，已用 JSON 解析复核）。

---

## 1. 8 项人工验收 checklist → 系统 / 参数 / 契约 / FAIL 路径 总表

| # | 人工验收项（用户反馈） | 所属系统 | 涉及 S5 aspect package（`scripts/validate/s5_aspects.json`） | 具体 tunable 参数（当前值 → 建议允许调整范围） | 影响该参数的 semantic contract（断言锚点） | FAIL 时需重跑的 Gate（最低） |
|---|---|---|---|---|---|---|
| 1 | 普通 hit 无震 / 有 hit 音效 | Camera（无震=策略硬禁）+ Audio（hit 音=light 层） | `camera`（cm_03）、`audio`（au_02）、`enemy_hit_reaction`（hr_02） | Camera：**无 tunable**（direct_hit 默认禁止是策略，改它=改策略语义非调参）；Audio：`COMBAT_LAYER_LIGHT_WINDOW_MS`（100 → 建议 80–140，**超 100 必须同步契约+自测字面量**）、stream `PUNCH_CLEAN_LIGHT_02.wav`（更换=契约字面量同步） | `semantic_camera_impulse_contract.py` 7a（direct_hit/dot_tick blocked 断言，L355-362）、`semantic_combat_audio_contract.py`（layer mapping light L230、stream 存在 L242/251-253）、`tests/combat_audio/test_combat_audio_layers.py` T1/T6 | ① `semantic_camera_impulse_contract.py` ② `semantic_combat_audio_contract.py` ③ `tests/combat_audio/test_combat_audio_layers.py` ④ `check_all` ⑤ 若改 mod.json → canonical rebuild → 新 candidate → S0/S1/S4 |
| 2 | 小怪击杀 shatter+脉冲+blood_explosion | Kill Feel（shatter 分层）+ Camera（kill 脉冲）+ Audio（kill 音层） | `kill_feel`（kf_02）、`camera`（cm_02）、`audio`（au_03） | Kill Feel：普通击杀 tier=0 无增强（**设计预期差异项**：vanilla 仅 FROZEN 出 shatter，普通击杀为 dissolve；若用户期望普通击杀也有 shatter，属 tier 策略变更而非数值调参）；Camera：`IMPULSE_AMPLITUDE_KILL`（1.6 → 建议 1.4–2.0，需 `< IMPULSE_AMPLITUDE_ELITE_KILL`）× `IMPULSE_KILL_RATIO`（0.72 → 建议 0.65–0.85）实发 1.152；Audio：kill 层 `blood_explosion.wav` + `COMBAT_LAYER_KILL_WINDOW_MS`（300）、`COMBAT_KILL_CLUSTER_THRESHOLD`（3） | `semantic_kill_feel_contract.py`（tier-0 场景 L285-286；boost 调用单点 L234）、`semantic_camera_impulse_contract.py` 7d（L373-381）/7i（L405-409）、`semantic_combat_audio_contract.py`（kill mapping L232、asset L241） | ① 三契约分别重跑 ② `check_all` ③ rebuild → 新 candidate → S0/S1/S4 ④ S5 machine evidence 重新 capture（`s5_evidence.py`） |
| 3 | 5–20 快速击杀集群抑制 | Kill Feel（GameState 级预算）+ Camera（cluster 合并）+ Audio（cluster 聚合） | `kill_feel`（kf_03/kf_04）、`camera`（cm_04）、`audio`（au_05） | Kill Feel：`KILL_FEEL_CLUSTER_WINDOW_MS`（400 → 建议 300–600，契约硬界 [200,2000]）、`KILL_FEEL_CLUSTER_BUDGET`（3 → 建议 2–4，**实际绿色域 [1,5]**，见 §4）；Camera：`IMPULSE_WINDOW_MS`（250 → 建议 240–400，契约需 ≥240）、`IMPULSE_CLUSTER_APPENDIX`（0.3 → 建议 0.20–0.50）、`IMPULSE_CLUSTER_APPENDIX_CAP`（2.0 → 建议 1.5–2.5）、`IMPULSE_BUDGET_MAX`（4.0 → 建议 3.0–4.3）；Audio：`COMBAT_LAYER_KILL_WINDOW_MS`（300）、`COMBAT_KILL_CLUSTER_THRESHOLD`（3 → 建议 2–5，契约**字面量钉死**） | `semantic_kill_feel_contract.py`（rapid/cluster 场景 L296-308 + 范围 L277-278）、`semantic_camera_impulse_contract.py` 7d/7e（L373-387）+ 关联硬界（§4.2）、`semantic_combat_audio_contract.py`（cluster gate L237-240）、`test_combat_audio_layers.py` T3/T7 | ① 三契约 + audio 自测 ② `check_all` ③ rebuild → 新 candidate → S0/S1/S4 ④ S5 场景 `cluster_kill_20` 重新 capture/checklist |
| 4 | 精英 shatter×1.25 | Kill Feel（scale）+ Camera（elite 脉冲） | `kill_feel`（kf_06，样本 `single_ranged_pack` 含 elite） | Kill Feel：`KILL_FEEL_BOOST_ELITE_SCALE`（1.25 → 建议 1.10–1.50，契约无数值断言，自由域）；Camera：`IMPULSE_AMPLITUDE_ELITE_KILL`（2.4 → 建议 2.0–2.8，**须保持 ×`IMPULSE_KILL_RATIO` < `IMPULSE_BUDGET_MAX`**，契约 7i 强制） | `semantic_kill_feel_contract.py`（tier-1 场景 L287-288；elite 分支 L225）、`semantic_camera_impulse_contract.py` 7h（L399-404）/7i（L405-409） | ① kill_feel + camera 契约 ② `check_all` ③ rebuild → 新 candidate → S0/S1/S4 ④ S5 样本重验 |
| 5 | Boss shatter+poof×1.6 | Kill Feel（双爆发 scale） | `kill_feel`（kf_02 延伸；**boss 无专用场景绑定**——见 §7 剩余风险） | Kill Feel：`KILL_FEEL_BOOST_BOSS_SCALE`（1.6 → 建议 1.30–2.00，契约无数值断言）；Camera：boss 击杀走 kill 记录，is_elite 判定取决于 boss 是否携带 `is_elite` 属性（**观察项**，非 tunable） | `semantic_kill_feel_contract.py`（tier-2 场景 L289-290；boss 分支 L224 + shatter+poof 双实例 L235-236） | ① kill_feel 契约 ② `check_all` ③ rebuild → 新 candidate → S0/S1/S4 ④ boss 击杀需人工实机复核（无场景绑定） |
| 6 | 重击 heavy 脉冲 + ice_crack | Camera（玩家受重击）+ Audio（crit→heavy 层） | `camera`（cm_02）、`audio`（au_02）、`enemy_hit_reaction`（hr_03） | Camera：`IMPULSE_AMPLITUDE_HEAVY`（1.2 → 建议 0.8–1.6）、`IMPULSE_HEAVY_THRESHOLD_RATIO`（0.12 → 建议 0.08–0.20，契约 7i 强制 ∈(0,1)）——**触发条件：玩家承受单次伤害 ≥ 12% health_max**；Audio：crit→heavy 层 `ice_crack.wav` + `COMBAT_LAYER_HEAVY_WINDOW_MS`（150 → 建议 130–180，**超 150 必须同步契约+自测**）——**触发条件：crit 事件**（两触发源不同，属设计事实，见 §4.3） | `semantic_camera_impulse_contract.py` 7g（L395-398）/7i（L406-409）+ 发射侧 canary（L295-296）、`semantic_combat_audio_contract.py`（heavy mapping L231、stream L242）、`test_combat_audio_layers.py` T2/T8 | ① camera + audio 契约 + audio 自测 ② `check_all` ③ rebuild → 新 candidate → S0/S1/S4 ④ S5 场景重验（`single_melee_hit` / `rapid_hit_10s`） |
| 7 | DoT 全抑制 | Kill Feel + Camera + Audio（三层策略硬禁） | `enemy_hit_reaction`（hr_04）、`camera`（cm_03）、`audio`（T4 语义、au_04 延伸） | **无 tunable**：Kill Feel `is_dot→tier 0`；Camera `dot_tick` blocked + DoT 击杀走 victim 侧 kill 记录（`blocked_kill_records` 计数）；Audio `dot_tick` early return —— 三层均为策略常量，FAIL 说明契约/代码 bug，**不是调参任务** | `semantic_kill_feel_contract.py`（dot tier-0 L291-292 + `_bad_tokens` 无伤害数学）、`semantic_camera_impulse_contract.py` 7a（L355-362）+ 发射侧（L287-296）、`semantic_combat_audio_contract.py`（dot early return L219-222）、`test_combat_audio_layers.py` T4 | ① 三契约 + audio 自测（canary 全绿仍 FAIL → 查 telemetry `blocked_*` 计数与 runtime 注入点）② `check_all` ③ 修复需 rebuild → 新 candidate → S0/S1/S4 |
| 8 | 全程无报错崩溃 | 跨系统（运行健康） | 全部 aspects（frame soak / fps 捕获点） | **无 tunable**；验证面：S0（结构/roundtrip）、S1（boot + godot log fatal markers）、S2（runtime soak telemetry）、S4 全契约、`check_all` 12 组件（含 abs-path/secret scan） | `s5_evidence.py`（capture/validate 契约）、`semantic_*` 三契约（编译面）、`check_all_components.json` 全量 | ① `check_all` ② S0/S1 重验 ③ S2 若环境可用（B3-X0 已推进）④ 新 candidate 需完整回归——**FAIL 属运行/管线 bug 任务，非调参任务** |

**覆盖自检**：8/8 项全覆盖；每项至少 1 个可追溯到 mod.json 实际字段的 tunable（或明确"无 tunable=策略/修复任务"）；每项 FAIL 均有明确验证路径（契约 + check_all + rebuild 条件）。

---

## 2. 参数溯源表（当前值 100% 来自 mod.json 实际 patch 载荷）

### 2.1 Kill Feel —— `mods/b2-x4-kill-feel/mod.json`（patch unit `Scenes/Mobs/Mob.gd::kill_feel::consts`，L37）

| 参数 | 当前值 | 建议允许调整范围 | 范围依据 |
|---|---|---|---|
| `KILL_FEEL_CLUSTER_WINDOW_MS` | 400 | 300–600 | `semantic_kill_feel_contract.py` L277 硬界 [200,2000]（超界契约 FAIL） |
| `KILL_FEEL_CLUSTER_BUDGET` | 3 | 2–4 | 契约 L278 自解界 [1,6]；**场景模型约束实际绿色域 [1,5]**（L298/301：5 连杀断言 `== budget`，budget=6 时 5≠6 契约 FAIL） |
| `KILL_FEEL_BOOST_ELITE_SCALE` | 1.25 | 1.10–1.50 | 契约无数值断言（仅 const 存在 + tier 逻辑 canary），自由域；留 FX 可读性人工判断 |
| `KILL_FEEL_BOOST_BOSS_SCALE` | 1.6 | 1.30–2.00 | 同上（契约 L233-236 仅断言 shatter/poof 复用） |

GameState 级注记：cluster budget 存于 GameState globals 键 `kill_feel_budget`（`_kill_feel_consume_budget` L20-23）——窗口/budget 变更影响**跨场景持久化的预算状态**，但数值本身只被 kill-feel 契约范围检查约束。

### 2.2 Camera Impulse —— `mods/b2-x5-camera-impulse/mod.json`

发射侧（patch `Scenes/Stats.gd::spine_impulse::helper`，L35）：

| 参数 | 当前值 | 建议允许调整范围 | 范围依据 |
|---|---|---|---|
| `IMPULSE_AMPLITUDE_KILL` | 1.6 | 1.4–2.0 | 契约 7i（L406）强制 `< IMPULSE_AMPLITUDE_ELITE_KILL`；无其他数值断言 |
| `IMPULSE_AMPLITUDE_ELITE_KILL` | 2.4 | 2.0–2.8 | 契约 7i（L407-409）强制 `× IMPULSE_KILL_RATIO < IMPULSE_BUDGET_MAX`（当前 1.728 < 4.0） |
| `IMPULSE_AMPLITUDE_HEAVY` | 1.2 | 0.8–1.6 | 无数值硬约束（7g 用字面量 1.2 作镜检输入，非常量断言） |
| `IMPULSE_HEAVY_THRESHOLD_RATIO` | 0.12 | 0.08–0.20 | 契约 7i（L406）强制 ∈(0,1) |

聚合侧（patch `Scenes/Player/Player.gd::camera_impulse::vars`，L68）：

| 参数 | 当前值 | 建议允许调整范围 | 范围依据（契约隐式硬界均来自镜检模拟输入） |
|---|---|---|---|
| `IMPULSE_BUDGET_MAX` | 4.0 | 3.0–4.3 | 隐式硬界 **(2.4r, 4.8r+3a)** = (1.728, 4.356)：7h（L399-404）需 `B > 2.4r`；7d（L373-381）需 `4.8r+3a > B`（4 连杀在 kill3 触发 cap 且 `capped_amplitude ≥ 2`） |
| `IMPULSE_WINDOW_MS` | 250 | 240–400 | 7d 隐式需 **≥ 240**（0/80/160/240ms 四杀必须同窗分组，否则 `clusters==3` 断言 FAIL，L375-380）；7e（L383-387）需 < 10000（平凡） |
| `IMPULSE_DECAY_PER_SEC` | 9.0 | 6–12 | 7c（L369-371）公式自适应（任意正值通过） |
| `IMPULSE_MAX_OFFSET` | 3.5 | 2.5–4.5 | 7f（L388-394）仅断言 `offset == min(amplitude, max_offset)`，任何值通过；观感帽建议 ≤ budget |
| `IMPULSE_CRIT_AMPLITUDE` | 0.6 | 0.4–0.8 | 7b（L363-367）断言 3×crit_amp（自适应）；7f 需 30×crit ≥ B（平凡） |
| `IMPULSE_KILL_RATIO` | 0.72 | 0.65–0.85 | 隐式硬界 **((B−3a)/4.8, B/2.4)** ≈ (0.646, 1.667)：7d 需 `4.8r+3a > B`；7h 需 `2.4r < B` |
| `IMPULSE_CLUSTER_APPENDIX` | 0.3 | 0.20–0.50 | 隐式下界 **a > (B−4.8r)/3 ≈ 0.181**（7d kill3 需累计 4.356 > 4.0 触发 cap#1；低于则 `capped_amplitude ≥ 2` 断言 FAIL） |
| `IMPULSE_CLUSTER_APPENDIX_CAP` | 2.0 | 1.5–2.5 | 隐式下界 cap ≥ 2a（kill3 appendix=2a 不被截断 → ≥0.6）；7d 数字关系按当前 a/B 导出，改 cap 需重跑镜检确认 cap#1 仍在 kill3 发生 |

### 2.3 Combat Audio —— `mods/b2-x6-combat-audio-layers/mod.json`（patch `Globals/Globals.gd::combat_audio_state` + `play_combat_event_layer_policy`，L28/L36）

| 参数 | 当前值 | 建议允许调整范围 | 范围依据 |
|---|---|---|---|
| `COMBAT_LAYER_LIGHT_WINDOW_MS` | 100 | 80–140 | 契约**字面量钉死** `= 100`（L233-236）；自测结构断言 `== (100,150,300)`（L141-144）；T1 需 ≥100（L156-159）；T8 需 `2000/L + 2000/H ≤ 34`（L185-189）。**改值必须同步契约 L233-236 + 自测 L141-144（若突破 T1/T8 边界还需调阈值）** |
| `COMBAT_LAYER_HEAVY_WINDOW_MS` | 150 | 130–180 | 契约字面量钉死 `= 150`（L233-236）；自测 L141-144；T2 需 ≥125（L160-163）；T8 需 H ≥ 142（L=100 时 floor(1980/H)+1 ≤ 14）。**同上同步要求** |
| `COMBAT_LAYER_KILL_WINDOW_MS` | 300 | 250–400 | 契约字面量钉死 `= 300`（L233-236）；自测 L141-144；T3 需 ≥160（L164-167，5 kills/200ms 仅 1 声）、T7 需 <500（L181-184）。**同上同步要求** |
| `COMBAT_KILL_CLUSTER_THRESHOLD` | 3 | 2–5 | 契约字面量钉死 `= 3`（L237）；自测 L145-146（解析常量，行为自适应，T3 对 ≥1 均通过）。**改值必须同步契约 L237 + 自测 L145-146** |
| （stream 槽位）`combat_sfx_light/heavy/kill` | PUNCH_CLEAN_LIGHT_02.wav / ice_crack.wav / blood_explosion.wav | 换资产=非数值调参 | 契约字面量钉死（L241-242）+ 资产存在性检查（L251-253）；更换需同步断言并确认 `04_recovered/Sounds/` 下资产存在 |

k4 漏斗注记（不可动层）：`play_combat_event` 仍走唯一 `play_sound_effect(stream)` 漏斗（契约 L226-227），k4 `SFX_MAX_CONCURRENT = 16`、`SFX_AGGREGATE_WINDOW_MS`、pitch/volume variation 由 `k4-audio-foundation` 控制（X6 new_text 不得触碰，契约 L243-249）——**调参永远不动漏斗本身**。

---

## 3. 每个 tunable 的调参影响面（契约断言同步矩阵）

### 3.1 Kill Feel（`semantic_kill_feel_contract.py`）

| 参数变化 | 受影响的断言 | 是否需要同步契约脚本 |
|---|---|---|
| `KILL_FEEL_CLUSTER_WINDOW_MS` | L277 范围检查（自适应解析 manifest 常量）；L296-308 场景模型（参数驱动） | 否（窗口在 [200,2000] 内即绿）；超界 → 契约 FAIL 需改 L277 |
| `KILL_FEEL_CLUSTER_BUDGET` | L278 范围检查；L298 `5 连杀 == budget`、L301 `20 连杀 == budget` | **是，存在特殊耦合**：budget ∈ [1,5] 契约绿域内无需改；改到 6 而范围检查放行但场景断言 FAIL——若要支持 6，需改 L298/301 场景期望 |
| `KILL_FEEL_BOOST_ELITE_SCALE` | 无数值断言（仅 const 存在 canary L226 之外无 scale 检查） | 否 |
| `KILL_FEEL_BOOST_BOSS_SCALE` | 同上 | 否 |

cluster cap 变更是 **GameState 级**：`kill_feel_budget` 按键跨场景存活（L212-217 断言 get/set API 存在，数值变化不触碰该 canary），但实际运行时预算状态持久化行为需 S2/实机复核——影响面超出本契约脚本，属"契约覆盖不到、需 runtime 证据"的已知缺口。

### 3.2 Camera Impulse（`semantic_camera_impulse_contract.py`）——最高耦合区

镜检模拟（§7）用**从 patch 解析的真实常量**驱动，但断言拓扑与数值强耦合：

| 参数变化 | 受影响的断言 | 隐式硬界（保持契约不改脚本的绿域） | 越界后果 |
|---|---|---|---|
| `IMPULSE_BUDGET_MAX` (B) | 7d（L373-381）、7h（L399-404）、7i（L407-409） | (2.4r, 4.8r+3a) | `merged_final==B` / `capped_amplitude≥2` / `2.4r < B` 断言 FAIL → 需同步 7d/7h 期望 |
| `IMPULSE_KILL_RATIO` (r) | 7d、7h、7i（elite×r<B） | ((B−3a)/4.8, B/2.4) | 同左 |
| `IMPULSE_CLUSTER_APPENDIX` (a) | 7d（cap#1 时机） | (B−4.8r)/3 < a | a 过小 → kill3 不触 cap → `capped_amplitude≥2` FAIL |
| `IMPULSE_CLUSTER_APPENDIX_CAP` | 7d（kill4 appendix=min(3a,cap)） | cap ≥ 2a | cap 截断附录 → 数字关系漂移，需镜检重跑确认 |
| `IMPULSE_WINDOW_MS` | 7d（四杀分组）、7b/7e（同窗语义） | [240, 10000) | <240 → `clusters==3` FAIL |
| `IMPULSE_MAX_OFFSET` | 7f | 任意 ≥0 | 无（断言公式自适应） |
| `IMPULSE_DECAY_PER_SEC` | 7c | 任意 >0 | 无 |
| `IMPULSE_CRIT_AMPLITUDE` | 7b、7f | 任意 >0（30×crit ≥ B 平凡） | 无 |
| `IMPULSE_AMPLITUDE_KILL` | 7i（< ELITE）；**7d 镜检输入为字面量 1.6** | < `IMPULSE_AMPLITUDE_ELITE_KILL` | 改大缩小不影响 7d 数字（镜检输入固定 1.6），仅 7i 顺序断言 |
| `IMPULSE_AMPLITUDE_ELITE_KILL` | 7i（×r<B）、7h（镜检输入字面量 2.4） | ×r < B | 超界 → 7i FAIL（需同步 7i 阈值） |
| `IMPULSE_AMPLITUDE_HEAVY` | 7g（镜检输入字面量 1.2） | 无 | 无 |
| `IMPULSE_HEAVY_THRESHOLD_RATIO` | 7i（∈(0,1)） | (0,1) | 越界 FAIL |

> 结论：Camera 契约的 7d/7h/7i 是**联合数值不定式**。调参任务必须按 §5 模板先算绿域（或同步契约断言），再落到 mod.json。

### 3.3 Combat Audio（`semantic_combat_audio_contract.py` + `tests/combat_audio/test_combat_audio_layers.py`）——字面量钉死区

| 参数变化 | 受影响的断言 | 需同步的文件/行 |
|---|---|---|
| 任一 window 变化 | 契约 L233-236 字面量 `= 100/150/300`；自测 L141-144 `== (100,150,300)`；T1（L≥100）、T2（H≥125）、T3（K≥160）、T7（K<500）、T8（2000/L+2000/H≤34，H≥142@L=100） | `semantic_combat_audio_contract.py` L233-236 + `tests/combat_audio/test_combat_audio_layers.py` L141-144（必要时 T1/T2/T8 阈值） |
| `COMBAT_KILL_CLUSTER_THRESHOLD` | 契约 L237 字面量 `= 3`；自测 L145-146；T3（自适应，≥1 均绿） | `semantic_combat_audio_contract.py` L237 + `test_combat_audio_layers.py` L145-146 |
| stream 更换 | 契约 L241-242 字面量、L251-253 资产存在性 | 契约两处 + 确认 `04_recovered/Sounds/` 资产 |

> 结论：Audio 是**同步成本最高**的系统——任何数值改动 = 契约脚本 + 自测脚本两处字面量/阈值同步，然后整体重跑。调参任务模板必须把这两文件列为必改清单（仅当参数确实偏离现值时）。

---

## 4. 需要写进调参任务书的设计事实（防误判）

1. **#1 的"无震"与"有 hit 音"是不同机制**：无震 = Camera 聚合器对 `direct_hit` 硬跳过（策略，调参数无效，改它=改策略注册）；有音 = Audio light 层（可调 window 控密度）。FAIL#1 若为"有震"→ 查代码/telemetry `blocked_direct_hits`，不是调参。
2. **#2 的"小怪 shatter"预期与 v1 设计冲突**：vanilla `spawn_death_animation` 仅 FROZEN 分支出 shatter、BURNING 出 poof，普通击杀只有 dissolve；b2-x4 对普通击杀 tier=0 零增强。用户若反馈"小怪击杀没有 shatter" → 属 tier 策略变更（把普通击杀接入增强层），需走设计变更流程而非数值调参。文档如实记录此预期差异。
3. **#6 两个触发源不同**：Camera heavy 脉冲 = 玩家**承受** ≥12% max HP 单次伤害（`IMPULSE_HEAVY_THRESHOLD_RATIO`，玩家受击侧）；Audio heavy 层 = **crit 事件**（打出暴击，玩家攻击侧）。"重击 heavy 脉冲+ice_crack" 是一次观感上的组合验收，但两侧 tunable 独立，FAIL 时需分别定位是哪一侧。
4. **#7 DoT 抑制没有中间档**：三层全是早期返回策略。用户反馈"DoT 有声音/有震动"只能是契约或注入点 bug（或 DoT 击杀的 kill 音误放——注意 kill 音频的 `killer.is_player` 守卫与 DoT 击杀记录在 victim 侧的路径差异，`blocked_kill_records` 为 0 即说明聚合器未见到异常记录）。
5. **audio 的 heavy 层由 crit 而非"重击"驱动**：若用户感觉"重击声音不对"，先确认是 crit 音还是 heavy 受击音缺失，再定位参数。

---

## 5. FAIL → 自动生成调参任务模板（B3 Combat Polish 系列）

### 5.1 任务书模板（每个 FAIL 项选择对应参数子集实例化）

```text
任务 id：  B3-CP<NN>-<slug>          （NN 顺序号；slug 如 kill-feel-cluster / camera-pulse / audio-light-window）
branch：   agent/b3-cp<NN>-<slug>    （base：协调线集成后的 B3-P0 HEAD，经协调 AI 分配）
来源：     HUMAN S5 反馈项 #N FAIL（反馈原文 + 用户描述）
调参目标： <参数名> 当前值 → 目标值（必须落在 §2 建议范围 / §3 绿域内；越界须先同步契约断言并说明理由）

必改文件：
  1. mods/b2-x4-kill-feel/mod.json   （若涉及 Kill Feel 参数：patch unit kill_feel::consts）
  2. mods/b2-x5-camera-impulse/mod.json（若涉及 Camera：Stats.gd spine_impulse::helper 或 Player.gd camera_impulse::vars）
  3. mods/b2-x6-combat-audio-layers/mod.json（若涉及 Audio：Globals.gd combat_audio_state / play_combat_event_layer_policy）
条件同步（仅当参数偏离契约平凡域时）：
  4. scripts/validate/semantic_camera_impulse_contract.py  （7d/7h/7i 或隐式硬界漂移时同步断言）
  5. scripts/validate/semantic_combat_audio_contract.py    （window/threshold 字面量 L233-240 变化时）
  6. tests/combat_audio/test_combat_audio_layers.py        （结构字面量 L141-146 / T1/T2/T3/T7/T8 阈值变化时）
  7. docs/ai/audits/B3-CP<NN>.md                            （audit 补充文档，记录调参依据与范围推导）

验证序列（FAIL 回归的最低 Gate，顺序执行，任一 FAIL 即停）：
  G1  affected_contract： semantic_kill_feel_contract.py / semantic_camera_impulse_contract.py / semantic_combat_audio_contract.py
       （受影响者必跑；未受影响者一并跑以证无回归）
  G2  tests/combat_audio/test_combat_audio_layers.py        （仅 audio 涉及）
  G3  scripts/ai/abs_path_scan.py --json  → production_hardcode=0
  G4  scripts/ai/secret_scan.py --json     → findings=0
  G5  scripts/ai/check_all.py              → 12 组件全 PASS（含批控单测、harness 自测、S5 selfcheck）
  G6  canonical rebuild（resolve→apply→compile→pack→fresh embed，scripts/pipeline）→ 新 Build ID + 新 candidate
       （禁止复用 B2-I1 candidate；build manifest 记录 git_commit/modset_hash/original_exe_hash）
  G7  S0（roundtrip/delta/normalize/exe_structure）+ S1（boot + godot log fatal 扫描）
  G8  S4 全契约 aggregate 上下文复验（与 G1 相同脚本，但在 aggregate 14-mod 链上）
  G9  S2（环境可用时：harness telemetry 场景复跑；B3-X0 修复推进后自动恢复）
  G10 s5_evidence.py capture/pair → 新 machine evidence package（machine_status=EVIDENCE_PREPARED）
      → 人工填 s5_checklist_<aspect>_filled.json → checklist 命令验证结构 → 重开 HUMAN S5 循环

交付：task_id/branch/base_sha/final_sha、改动文件清单、Build ID、各 Gate 状态、失败重试记录、剩余风险。
```

### 5.2 8 项 FAIL → 任务实例化速查

| 反馈项 FAIL | 生成任务 | 主要改动文件（mod.json） | 首要验证（除 G5/G6/G7/G8 公共集外） |
|---|---|---|---|
| #1 普通 hit | `B3-CP1-audio-light-window`（有震→策略 bug 任务，非调参；无音→light 参数） | `b2-x6-combat-audio-layers/mod.json`（LIGHT_WINDOW / stream） | camera 契约 7a、audio 契约、T1/T6 |
| #2 小怪击杀 | `B3-CP2-kill-impulse-audio`（脉冲/音层参数；shatter 缺失=tier 策略变更另立任务） | `b2-x5`（AMP_KILL/RATIO）+ `b2-x6`（KILL_WINDOW） | kill-feel（tier-0）、camera 7d/7i、audio kill mapping |
| #3 集群抑制 | `B3-CP3-cluster-suppression` | `b2-x4`（WINDOW/BUDGET）+ `b2-x5`（WINDOW/APPENDIX/APPENDIX_CAP/BUDGET）+ `b2-x6`（KILL_WINDOW/THRESHOLD） | 三契约 cluster 场景 + T3/T7；**三系统联动时优先调 audio 阈值/窗口，其次 camera，最后 kill-feel GameState 预算** |
| #4 精英 | `B3-CP4-elite-tier` | `b2-x4`（ELITE_SCALE）+ `b2-x5`（AMP_ELITE_KILL） | kill-feel tier-1、camera 7h/7i |
| #5 Boss | `B3-CP5-boss-tier` | `b2-x4`（BOSS_SCALE） | kill-feel tier-2 |
| #6 重击 | `B3-CP6-heavy-impulse-crit-cue` | `b2-x5`（AMP_HEAVY/THRESHOLD_RATIO）+ `b2-x6`（HEAVY_WINDOW） | camera 7g/7i、audio T2/T8 |
| #7 DoT | 不生成调参任务 → `B3-FIX<NN>-dot-suppression`（修复任务） | 代码修复（非数值）后 `b2-x4/x5/x6` 相应 patch | 三契约 canary + `blocked_*` telemetry 审计 |
| #8 崩溃 | `B3-FIX<NN>-runtime-stability`（运行/管线 bug 任务） | 不限定 | G3/G4/G5 + S0/S1/S2；若合约涉及 X6 或有 GDScript 编译面 → 全契约 + rebuild |

> 每个任务书必须附带 §3 影响面矩阵中该参数行的"越界后果"与需要同步的契约行号。

---

## 6. 与 `s5_evidence.py` human gate 的关系（本映射不替代记录流程）

- 唯一 HUMAN_ACCEPTED 录入路径 = `scripts/validate/s5_evidence.py`：machine 只产出 `machine_status=EVIDENCE_PREPARED`、`verdict=null`；人工填 `s5_checklist_<aspect>_filled.json`（每 question 的 judgment + conclusion 的 verdict/accepted_sides/signed_by/signed_at）→ `checklist` 命令做结构校验 → 判定存档。selfcheck 内建 `human_gate_never_auto_accepted` 断言（B2-I1：s5_evidence selftest 23/23 PASS 含此断言）。
- **本映射文档的作用**：仅在用户 8 项反馈回来时把"FAIL 项 + 用户描述"翻译成调参/修复任务书（§5）。它**不写任何 verdict、不产生 checklist 文件、不改变 human_gate 状态**。
- 流程闭环：用户反馈 FAIL → 本映射生成调参任务 → 调参完成新 candidate → §5 验证序列 G10 重新生成 S5 machine evidence → **由用户再次填 checklist** → 才可能 HUMAN_ACCEPTED。调参任务本身不自动验收。
- B2-I1_AGGREGATE_EVIDENCE.json `S5_machine` 段：5 个 aspect package 均为 candidate-side NOT_RUN skeleton（vm_not_launched/telemetry_missing），human_gate 未接受——与本任务是同一 gate 的不同准备物：B2-I1 是 evidence 骨架，本文件是 feedback→tunable 翻译层。

---

## 7. 校验记录与剩余风险

### 7.1 映射完整性自检（本任务交付前已逐项核对）

- [x] 8 项 checklist 全覆盖（§1 总表 8 行，系统/tunable/契约/FAIL 路径四列齐全）；
- [x] 每个 tunable 可追溯到 mod.json 实际字段（§2 溯源表 20 个参数，均给出 patch unit 与当前值——值全部来自 `mod.json` patch `new_text` 解析，非推测）；
- [x] 每个 FAIL 有明确验证路径（§1 每行 + §5.1 G1–G10 公共序列）；
- [x] 契约断言锚点均给出 `文件:行号`（§2/§3）；
- [x] 文档无宿主绝对路径（repo-relative；§6 引用的 B2-I1 文件仅按仓库路径）；
- [x] 未修改任何 mods/ 下 gameplay 数值（本批次 diff 仅含本文档）。

### 7.2 剩余风险（如实登记）

| 风险 | 说明 | 缓解 |
|---|---|---|
| boss 无 S5 场景绑定 | `s5_aspects.json` 的 kill_feel 场景仅 cluster_kill_20 / single_ranged_pack（样本含 elite），无 boss 专属绑定 → #5 FAIL 只能靠用户实机自由操作反馈，无机器 capture | 人工验收时标注 boss 观察点；或后续批次新增 boss 场景绑定（需 harness 支持） |
| 观感参数无法机器断言 | scale/window/幅度 的"手感"边界（如 1.10 vs 1.50）本质是人的判断，契约只给结构/数值绿域 | 建议范围保守居中；调参任务按"最小步进 + 用户复验"迭代 |
| Camera 契约隐式硬界非显式文档化 | 7d/7h/7i 的联合不定式（B/r/a 三参数联动）写在镜检模拟里，不是独立范围声明——未来有人只看 mod.json 会被数值迷惑 | 本文件 §3.2 已显式化；调参任务书必须引用 |
| Kill Feel budget 绿色域与范围声明不一致 | 契约 L278 声言允许 1–6，但场景 L298 使 budget=6 契约 FAIL（实际 [1,5]） | 本文件 §2.1 已标注"实际绿色域 [1,5]"；如需支持 6 须先改契约场景断言 |
| S2 仍 BLOCKED（历史） | B2-I1 S2 未取到 harness telemetry；B3-X0 已推进修复 | §5 G9 依赖 B3-X0 结果；未修复前以 S0/S1/S4 + machine S5 骨架为上限证据 |
| 竞态（is_elite 观察项） | Camera elite 脉冲依赖 victim 父节点 `is_elite` 属性（非 Stats 字段），运行时判定未机器证实；boss 是否 is_elite 未知 | #4/#5 调参时附带 telemetry `elite_kills` 计数核验项 |

---

## 8. 本批不做什么（重申边界）

- ❌ 不改任何 gameplay 数值（Combat Polish 实际调参保持 WAITING_HUMAN_S5，收到用户反馈后由 §5 模板生成任务执行）；
- ❌ 不写 HUMAN_ACCEPTED、不改 s5_evidence 流程（§6）；
- ❌ 不触碰 `00_original/03_raw/04_recovered`；不修改 B2 历史证据文件；
- ❌ 不引入宿主绝对路径。