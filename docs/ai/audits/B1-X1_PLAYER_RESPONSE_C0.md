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
