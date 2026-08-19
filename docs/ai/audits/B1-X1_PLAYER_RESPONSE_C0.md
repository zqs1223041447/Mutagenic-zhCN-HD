# B1-X1 — Player Response C0 远端预审计

> **Task**：B1-X1
> **基线**：`batch/b1-anchor` → `c864480d8908630d602c17f4949b96b65d19b275`
> **来源**：tracked `04_recovered/Scenes/Player/Player.gd`
> **文件 SHA-256**：`3f0099897fc13c5b16d01042b96042acb301ec8ad9ba078611c06f646c43b25c`
> **状态**：REMOTE C0 + DECLARATIVE CANDIDATE READY；未做本地 build/runtime Gate。

## 1. 真实控制链

`Player._physics_process(delta)` 每物理帧：

1. 读取鼠标左键目标或 `Input.get_vector(move_left/right/up/down)`；
2. 将输入归一化并乘 `stats.gs("movement_speed")`；
3. 计算 `(velocity - linear_velocity).normalized() * movement_speed`；
4. 用 `apply_central_impulse(delta * 15.0 * force_direction)` 追逐目标速度；
5. Dash 使用 `Input.is_action_just_pressed("dash")`，冷却 0.75s；
6. Dash impulse 为 `velocity.normalized() * Constants.DASH_AMOUNT`。

## 2. C0 结论

### Movement response

当前移动并不是简单 `linear_velocity = target`，而是 RigidBody impulse 追逐，因此确实存在可调 response profile。但在没有实机 A/B 前，不应远端拍脑袋提高 `15.0` 或基础 movement_speed。

### Dash response

存在一个确定性响应缺口：

- Dash 方向完全来自**当前帧 `velocity`**；
- 当玩家没有按移动键、也没有按住左键移动时，`velocity == Vector2.ZERO`；
- 此时 Dash 按键满足冷却条件却得到零 impulse，声音仍会播放并进入 0.75s cooldown。

这会产生明确的“按下 Dash 但角色没动，而且技能进入冷却”的无响应体验。

## 3. 第一 Candidate 选择

`k1-player-response` v0.1 只处理上述确定性缺口：

- 缓存最近一次非零移动方向；
- 当前帧有移动输入时 Dash 仍使用当前方向；
- 当前帧无移动输入时 Dash 使用最近方向；
- 不改 `DASH_AMOUNT`；
- 不改 0.75s cooldown；
- 不改 `movement_speed`；
- 不改变碰撞、存档或技能系统。

默认最近方向初始化为 `Vector2.RIGHT`，保证游戏刚开始尚无历史移动方向时 Dash 也有确定性结果；本地 S5 可决定是否改为鼠标朝向/角色朝向作为更优 fallback。

## 4. 风险

- 这是响应性修复，不代表整个 movement acceleration 已完成调优。
- 初始 fallback 为 RIGHT 是安全确定性策略，但最终产品体验仍需 S5。
- 后续若 X4/Camera 要接 Dash impulse，应依赖 Dash 事件/方向，不要重复修改本段 preimage。

## 5. 本地接手动作

1. 运行 `k1-player-response` resolve/apply；
2. compile → pack → fresh embed；
3. S0 / S1 / S2 / S4；
4. TestLevel A/B：移动中 Dash、静止 Dash、连续 Dash、鼠标移动模式、键盘模式；
5. 记录 BEFORE/AFTER，S5 未人工接受前不写 gameplay PASS。

## 6. 本地 canonical build 结果（2026-08-20 实机执行）

> 候选 SHA-256：`40D5F0640695D6A89F1D00AEA5FABFF969722690A04699A0E5341D48C1AC8E95`
> Build ID：`20260820-0009-40D5F0640695`；完整证据见 gitignored `10_logs/B1-X1-20260819/build.json` 及 s0/s1/s4 各证据文件。

- preimage 逐字节核对 PASS：`04_recovered/Scenes/Player/Player.gd` SHA=`3f009989…c25c` 与 mod.json 两处 `preimage_sha256` 一致；两处 `old_text`（含 tab 缩进）`expected_occurrences=1` 全部命中；文件为 LF 行尾，无 CR 干扰。
- 构建链 PASS：resolve（1 mod/2 patches）→ apply（5058-file worktree 复制，guard 后仅改 Player.gd）→ compile（venv 3.11.15 + GDRE 编译唯一 `Scenes/Player/Player.gd` → .gde+.remap）→ pack（3744 条目，delta 恰为 2 个物理路径：`Player.gde`、`Player.gd.remap`）→ normalize（1 个零字节 MD5 修正）→ fresh embed（00_original SHA `C7B5D5A5…1209`）。
- S0 PASS：候选 EXE 提取 3744/3744、0 MD5 不匹配；delta 与声明完全一致、无意外变更；PCK 结构 3744 条目全有效；pristine roundtrip 3/3 MATCH（含 `Scenes/Player/Player` 本身，证明管线无缺陷）。
- S1 PASS：`probe_boot.py` 20s 真窗口 `Mutagenic`、无 ALERT、无 fatal；boot 使用 SHA `DCFAA13A…E799` 相邻 stub DLL（存档控制件）。
- S2 core smoke：NOT RUN（宿主无法自动驱动游戏内移动/Dash 输入；需 X5 harness 或人工）。
- S4 PASS：GDRE 从**最终候选 EXE** 恢复 `Player.gd`，SHA=`9ab80451…ccac` 与构建 worktree 逐字节相同；`last_move_direction = Vector2.RIGHT` 已嵌入；移动时缓存最近非零方向、静止 Dash fallback 到最近方向、`apply_central_impulse(dash_direction * Constants.DASH_AMOUNT)` 生效；`movement_speed`（5 处）、`DASH_AMOUNT`（1 处）、`dash_cooldown = 0.75` 未变。
- S5：NOT RUN / NOT HUMAN-ACCEPTED（需要游戏内输入驱动 + 人工 A/B，未执行）。

**证明什么**：k1-player-response v0.1 经确定性 canonical 管线产出结构完整、可启动、语义已嵌入最终 EXE 的候选。
**不证明什么**：真实输入下 Dash 的运行时手感（S2）、静止/移动/连续 Dash 的实机 A/B（S5）、长期稳定性、中央集成后的聚合行为。
