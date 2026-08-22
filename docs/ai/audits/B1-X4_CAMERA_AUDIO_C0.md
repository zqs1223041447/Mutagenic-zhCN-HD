# B1-X4 — Camera & Combat Audio Foundation：C0 审计 + 实现证据

- **Task**: B1-X4
- **Branch**: `agent/b1-x4-camera-audio`
- **新基线**: `c864480d8908630d602c17f4949b96b65d19b275`（当前 `batch/b1-anchor`）
- **来源**: 原 X4 在旧 B1 anchor 完成；本文件由协调 AI 在主线同步后移植并做 portability / voice-budget 修正。
- **结论**: Audio 侧保留独立 foundation MOD（`k4-audio-foundation`）；Camera 侧只交事实审计 + 集成要求，不抢 X1 的 Player preimage。

---

## 1. Camera 现状

证据来自 tracked `03_raw/Scenes/Player/Player.tscn` 与 tracked `04_recovered`。

- 唯一 gameplay `Camera2D` 位于 Player 根 `RigidBody2D` 下。
- Camera 无独立脚本；工程未发现现成 gameplay shake/impulse 管理器。
- 已知参数：`current=true`、`zoom=0.5`、`smoothing_enabled=true`、`offset_v=0.21`。
- 因 camera 接入最终需要 `Player.tscn/Player.gd`，属于 X1 的核心 preimage 范围，本任务不抢写。

### 交给 X1 / 中央集成的 Camera 要求

- 复用现有 Camera2D，不新建第二个 gameplay camera。
- 普通 hit 默认不 shake；heavy/crit/elite 采用聚合 impulse。
- cluster AoE 同帧 N 次事件必须聚合成一次 camera 事件。
- camera offset/zoom 必须回到基线，不形成长期漂移。

---

## 2. Audio 现状

证据源：tracked `04_recovered/Globals/Globals.gd`。

- SFX 汇聚点：`Globals.play_sound_effect(stream, bus="SFX")`，大量调用统一经过这里。
- 每次播放实例化 `SoundEffect.tscn`，原实现无聚合窗口、voice budget、pitch/volume variation。
- cluster kill、多弹爆炸、高频 cast 存在声音堆叠风险。

---

## 3. `k4-audio-foundation`

改动只针对 `Globals/Globals.gd`，保持伤害/碰撞/技能语义不变：

1. 同一 `bus + stream instance` 的 60ms 聚合窗口；
2. 全局活动 SFX 上限 16；
3. `tree_exited` 回收活动计数，避免依赖节点名称判断；
4. pitch ±4%、volume 0..-2dB 的轻微变化；
5. 保留 `enable_sfx` / `enable_drops` 门控和 null/bus 防护。

协调修正：旧实现通过遍历 root children 并比较 `child.name == "SoundEffect"` 统计 voice；重名节点在 Godot 中可能自动改名，因此新基线改为 `_sfx_active_count` + `tree_exited`，消除该隐患。

---

## 4. 原任务验证证据

旧基线执行结果：

- resolve/apply/compile/pack/PCK normalize：PASS
- S0：PASS（3744/3744）
- S1：PASS（15s 真窗口，无 ALERT/fatal）
- S4：PASS（从最终 EXE recover 到目标 `Globals.gd` 并确认 limiter 常量/函数）

原 Generated 证据目录属于本地日志，不写宿主绝对路径；逻辑位置记为：

`<repo_root>/10_logs/b1-x4-k4-audio-foundation-*/`

**注意**：本次移植对 voice-budget 实现做了协调修正，因此旧 S0/S1/S4 只能证明原 foundation 方向与 patch 链可行；修正版在 B1 aggregate 前必须重新执行 compile/S0/S1/S4。

---

## 5. 尚未证明

- 60ms / 16 voices / pitch-volume 范围的最终战斗听感：需要 Combat S5。
- Camera feedback：未实现，等待 X1/后续 impact 批次。
- 修正版 limiter 的 runtime Gate：等待新基线本地 aggregate 回归。
