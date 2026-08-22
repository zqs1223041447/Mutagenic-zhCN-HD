# P4-ANIM 多帧行走动画接入计划（P4-ANIM 最小可用闭环）

生成时间: 2026-08-22
任务: P4-ANIM
状态: READY — 可脚本部分已落地，itch 手动包待用户放入后由 WIRE 自动纳入
关联脚本: `scripts/bootstrap/fetch_cc0_anim.py` / `product/scenes/Mobs/FakeWalkBob.gd` / `product/Shaders/FakeWalkBob.gdshader`

---

## 1. 目标与非目标

**目标（最小可用闭环）**
- 为玩家/主力小怪 6–8 种提供 Idle/Run（walk）两动画，FPS 6–10，可 flip_h。
- 免费 CC0 优先，管线打通：`product/sprites/_acquired/ -> product/sprites/_mapped/ -> SpriteFrames.tres -> WIRE`
- 单帧占位期间用程序化 FakeWalkBob（tween/shader）提供动感，真帧落地后 `play("walk")` 一键替换。

**非目标**
- 不下载 itch 需手动包（0x72 / o_lobster / Shade），仅登记待手动下载。
- 不改已有 `_mapped` 单帧包装器（仅新增示例与新目录）。
- 不 commit（按任务要求）。

---

## 2. 选型与可用 CC0 包（librarian 报告快照）

### P0（最贴合，已验证 CC0）

| 包 | 许可 | 获取 | 内容 | 适配 |
|---|---|---|---|---|
| **0x72 DungeonTileset II v1.7** | CC0 1.0 | itch 手动 0$ https://0x72.itch.io/dungeontileset-ii | Knight / Wizard / Elf / Orc 等 idle / run / hit (4 方向或侧视) | 玩家与主力小怪首选，帧数足 (idle 4, run 6-8) |
| **o_lobster Simple Dungeon Crawler** | CC0 1.0 | itch 手动 0$ https://o-lobster.itch.io/simple-dungeon-crawler | Knight / Zombie / Slime 2帧动画 (16x16) | 轻量 fallback，小怪可用 |

### P1（备选）

| 包 | 许可 | 获取 | 备注 |
|---|---|---|---|
| Shade Puny 系列 | CC0 1.0 | itch 手动 | 像素小人多套，需筛选 idle/run |
| 其他 itch CC0 | CC0 | 手动 | 按需 |

### 已脚本直链（已落地）

| 包 | 许可 | 直链 | 落盘 | 规格 |
|---|---|---|---|---|
| **OGA 16x16 base sprites** | CC0 1.0 | `https://opengameart.org/sites/default/files/base_male.png` / `base_female.png` | `product/sprites/_acquired/oga_16x16-base-sprites/` (`SOURCE.txt` + `fetch_manifest.json`) | 126x144 PNG，18px 网格 (16px +2px padding)，7 cols ×8 rows；含 1 idle +6 walk ×4 dir |
| blocky dungeon / skeleton / slimes 补充 | CC0 1.0 | OGA files 直链 | 可选 `--with-optional` | 同上 CC0 |

**SHA256（本次实测）**
- base_male.png: `62ce53be0a21aab54fbca2fbf5c8ef4156ae0d30dfc74044599e33a7c0cf319c` (2966 bytes)
- base_female.png: `787d7a4a8a281ae547b6843c2c2ae898fb4ba9284f4cc04aee1024b26da9b0b1` (3012 bytes)

---

## 3. `_mapped` 目录结构草案（按 librarian 2.2 建议）

### 3.1 现状

```
product/sprites/
  _acquired/          # 原始下载（CC0 包、OGA、kenney、game-icons.net）
    generated_spriteframes/  # 旧批量单帧包装器（兼容保留，不改）
    oga_16x16-base-sprites/  # NEW: base_male/female + SOURCE.txt
    frosty-rabbid_rpg-ability-icons/ ...
  _mapped/            # 旧映射（actors/ equipment/ skills/ ...）单帧包装器
  _placeholders/
```

### 3.2 推荐新增（与旧兼容并存）

```
product/sprites/
  _acquired/
    oga_16x16-base-sprites/
      base_male.png
      base_female.png
      SOURCE.txt
      fetch_manifest.json
    0x72-dungeontileset-ii/        # 手动放入后自动纳入（见 p4_art_needs_manual_download.json）
    o_lobster-simple-dungeon-crawler/
    shade-puny/
  _mapped/                         # 保持旧 actors/ 不动，新增以下为 P4-ANIM 专用
    player/                        # NEW
      player_idle.tres             # 示例：OGA base_male walk 6帧切片（当前整图占位，TODO 细化）
      player_walk.tres             # 示例：同上，切片后为 6 帧 walk
      knight/                      # 0x72 Knight 示例（待手动包落地）
        idle.tres                  # 4 帧
        walk.tres                  # 6 帧
        hit.tres
      wizard/
        idle.tres
        walk.tres
    mobs/                          # NEW（与旧 _mapped/actors/ 并存，WIRE 优先新路径）
      zombie/
        idle.tres                  # o_lobster Zombie 2帧 -> 扩展为 4帧 idle / 6帧 walk（插值或去重）
        walk.tres
      slime/
        idle.tres
        walk.tres
      skeleton/                    # 0x72 / OGA skeleton
        idle.tres
        walk.tres
      spider/                      # 现有 mutated_spider 升级
        idle.tres
        walk.tres
      # 6-8 种主力：zombie, slime, skeleton_archer, skeleton_warrior, spider, attack_dog, chilled_bones, fire_bomber
    _anim_source_index.json        # 可选：记录每个 SpriteFrames 的源 PNG 与切片坐标，供 WIRE 校验
```

**WIRE 策略**
- 已有 `_mapped/actors/*.png` 单帧包装器保持可运行；新 `player/` 与 `mobs/*/` 多帧 `*.tres` 优先被 `Mob.tscn` / `Player.tscn` 的 `frames` 引用（若存在）。
- 用户手动包放入 `_acquired/<slug>/` 后，`fetch_cc0_anim.py` 不负责；下一轮 WIRE 脚本扫描 `_acquired/` 并自动生成对应 `_mapped/<category>/` 的 SpriteFrames（按本计划命名）。

---

## 4. 动画命名与参数

### 4.1 命名

| 动画名 | 含义 | 帧数建议 | 循环 |
|---|---|---|---|
| `idle` | 待机（替代 `default`） | 1–4 帧（OGA 为 1 帧单图；0x72 为 4 帧） | true |
| `walk` | 行走/奔跑（替代奔跑） | 6–8 帧（OGA walk 6 帧；0x72 run 6–8 帧） | true |
| `hit` | 受击（可选，复用 walk 第1帧+闪白） | 1–2 帧 | false |
| `default` | 兼容保留，指向 `idle` 首帧 | 1 帧 | true |

> Godot 侧：`AnimatedSprite2D.play("walk")` / `play("idle")`；旧代码中 `sprite_frames.get_frame_count("default")` 需兼容指向 `idle`。

### 4.2 FPS 与速度

- **FPS**: 6–10（推荐 8）。玩家可按 `stats.gs("movement_speed")` 动态缩放 `speed_scale`（见 `Player.gd` 已有 `playback_speed = 2.0 * ms / base_ms`）。
- **Mob**: 固定 8 FPS，受 `FROZEN` 状态置 `speed_scale=0`。
- **时长**: `walk` 6帧 @8 FPS = 0.75s 一循环，与 FakeWalkBob 0.24s bob 叠加时视觉不冲突（真帧落地后 bob 自动禁用）。

### 4.3 flip_h 策略

- 统一只存 **向右** 侧视帧；向左通过 `AnimatedSprite2D.flip_h = true` 镜像。
- `Player.gd` / `Mob.gd` 已有 `velocity.x` / `target_direction.x` 驱动 `flip_h`，新帧无需额外左右两套。
- OGA 4 方向（up/down/left/right）仅取 **side** 行（walk 6帧侧视）；top/down 可后续扩展为 `walk_up` / `walk_down`（暂不阻塞）。

### 4.4 Godot 导入设置（像素风）

| 属性 | 值 | 说明 |
|---|---|---|
| Filter | **Off** (Nearest) | 保持像素锐利 |
| Mipmaps | Off | 避免模糊 |
| Fix Alpha Border | On | 避免黑边 |
| Snap | **Snap 2D Transforms to Pixel** (Project Settings) | 摄像机与 sprite 像素对齐 |
| Integer | CanvasItem 使用整数坐标 | `position` 取整，避免半像素抖动 |
| Texture Import | `Compress Mode = Lossless` | 16x16 小图无损 |

**示例 `.import` 片段**
```
[remap]
importer="texture"
type="CompressedTexture2D"
path="res://.godot/imported/base_male.png-xxx.ctex"
metadata={
  "imported_formats": ["ctex"],
  "texture_type": 0
}
[params]
compress/mode=0
compress/high_quality=false
mipmaps/generate=false
process/fix_alpha_border=true
process/HDR_as_SRGB=false
process/invert_color=false
process/normal_map_invert_y=false
process/premult_alpha=false
roughness/mode=0
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/bptc_ldr=0
compress/normal_map=0
compress/channel_pack=0
mipmaps/limit=-1
detect_3d/compress_to_normal_map=false
svg/scale=1.0
editor/scale_with_editor_scale=false
editor/convert_colors_with_editor_theme=false
```

---

## 5. 程序化 Fallback 方案 A（已落地）

### 5.1 Tween 版本：`product/scenes/Mobs/FakeWalkBob.gd`

```gdscript
var bob: Tween
func set_fake_walk(active: bool):
    if active: # 循环 tween position:y ±1px + scale 1.0->1.02，周期 0.24s
    else: # 恢复基线
```

- 在 `_physics_process` 中根据 `velocity.length() > 10` 调用：
  ```gdscript
  @onready var fake_bob = $FakeWalkBob  # 或 FakeWalkBob.new()
  func _physics_process(delta):
      fake_bob.set_fake_walk(velocity.length() > 10.0)
      # 或 fake_bob.update_from_velocity(velocity)
  ```
- **兼容**：若 `AnimatedSprite2D.sprite_frames.has_animation("walk")` 存在多帧，`set_fake_walk()` 自动改为 `sprite.play("walk")` / `play("idle")`，不再 tween。

### 5.2 Shader 版本：`product/Shaders/FakeWalkBob.gdshader`

```glsl
shader_type canvas_item;
uniform float walk_speed : hint_range(0.0,20.0)=0.0;
void vertex(){
    float freq = 6.2831853 / 0.24;
    if (walk_speed > 0.5) VERTEX.y += sin(TIME*freq) * 1.0;
}
```

- 脚本驱动：`material.set_shader_parameter("walk_speed", moving ? 10.0 : 0.0)`。

### 5.3 集成建议

- **Player**: 在 `Player.gd` 的 `_physics_process` 末尾接 `fake_bob.update_from_velocity(velocity)`，或在 `BodyParts` 上挂 `FakeWalkBob` 子节点并设 `target_path` 指向 `SpriteContainer`。
- **Mob**: 在 `Mob.gd` 的 `_physics_process` 中 `fake_bob.set_fake_walk(cached_ms > 0 and linear_velocity.length() > 10)`。
- **迁移**：真帧切片完成后，全局搜索 `set_fake_walk` 替换为 `play("walk")` / `play("idle")` 即可；FakeWalkBob 可保留作为受击抖动备用。

---

## 6. 示例 SpriteFrames 管线（已验证）

### 6.1 示例文件

- `product/sprites/_mapped/player/player_idle.tres` — 占位：整张 `base_male.png` 单帧（TODO：切片为 6 帧 idle）
- `product/sprites/_mapped/player/player_walk.tres` — 占位：整张 `base_male.png` 单帧（TODO：按 18px 网格切片 6 帧 walk side）

> 当前为 **整图占位**，确保 `AnimatedSprite2D.frames = preload("res://sprites/_mapped/player/player_walk.tres")` 管线可导入；待细化时按 `126x144` 的 18px 网格提取 `(row=0, col=0..5)` 的 16x16 子图生成 6 个 `AtlasTexture`。

### 6.2 切片坐标（待细化，基于 126x144 实测）

- 网格：7 cols ×8 rows，cell 18px（含 2px 透明 padding），sprite 有效 16px 居中。
- 推荐 walk side 行：`row=0` 或 `row=2`（需目视确认方向），`col=0..5` 各取 `16x16` 子图，生成 6 帧。
- 工具：`Pillow` 脚本 `scripts/bootstrap/slice_oga_sheet.py`（待补充）可批量产出 `walk_0.png ... walk_5.png` 再合成 `SpriteFrames`。

### 6.3 导入验证

- 运行 `fetch_cc0_anim.py` 已验证 `base_male.png` / `base_female.png` 为有效 PNG，可被 Godot 导入为 `CompressedTexture2D`。
- 示例 `player_idle.tres` / `player_walk.tres` 在 Godot 4.7.1 中可直接作为 `AnimatedSprite2D.frames`，`play("default")` 正常显示占位大图；切片后 `play("walk")` 自动 8 FPS 循环。

---

## 7. itch 手动包接入（下一轮 WIRE）

见 `migration/inventory/p4_art_needs_manual_download.json`：

- **0x72 DungeonTileset II v1.7** — CC0 — https://0x72.itch.io/dungeontileset-ii — Knight/Wizard/Elf 等 idle/run/hit（首选）
- **o_lobster Simple Dungeon Crawler** — CC0 — https://o-lobster.itch.io/simple-dungeon-crawler — Knight/Zombie/Slime 2帧
- **Shade Puny** — CC0 — https://shade.itch.io/... — 小人多套（备选）

用户 0$ 手动下载后解压至 `product/sprites/_acquired/<slug>/`，下一轮 `WIRE` 脚本扫描并生成 `_mapped/player/` / `_mapped/mobs/<name>/` 的 `idle.tres` / `walk.tres`（命名同 §4.1）。

---

## 8. 验收与回滚

**验收**
- `python scripts/bootstrap/fetch_cc0_anim.py` 在有网时 `DOWNLOADED` 2 PNG，`SOURCE.txt` 含 URL/许可/日期/SHA256。
- `FakeWalkBob.gd` / `FakeWalkBob.gdshader` 存在且 `set_fake_walk()` 可被 `velocity.length()>10` 驱动。
- `product/sprites/_mapped/player/player_idle.tres` 与 `player_walk.tres` 可被 Godot 加载（占位整图，注明待细化）。
- `p4_art_needs_manual_download.json` 含 3 itch 包登记，WIRE 可自动纳入。
- 不改旧 `_mapped` 单帧包装器，不下载 itch 包，不 commit。

**回滚**
- 删除 `product/sprites/_acquired/oga_16x16-base-sprites/` 与 `product/sprites/_mapped/player/` 示例文件即可回到单帧状态；`FakeWalkBob` 为可选组件，不影响旧逻辑。

---

## 9. 后续 TODO（用户下载后）

- [ ] 用户放入 0x72 等 3 包后，运行 WIRE 脚本按 §3.2 生成 `mobs/zombie` 等 6–8 种 `walk.tres`。
- [ ] 用 Pillow 按 18px 网格切片 OGA sheet，替换 `player_walk.tres` 整图占位为真 6 帧。
- [ ] 在 `Player.tscn` 的 `BodyParts` 与 `Mob.tscn` 的 `Sprite` 上切换 `frames` 指向新 `walk.tres`，并把 `set_fake_walk` 调用替换为 `play("walk")`。
- [ ] Godot 导入设置统一为 Nearest + Lossless + Snap，验证 flip_h 镜像与 FPS 6–10 观感。
