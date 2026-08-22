# P4 美术补全计划

本文件是一份完备计划，交给本地 AI 自行排工执行即可。  
美术补全只是其中一个子工作，**不要**为此单独建设并行调度、多 Worker 流水线或复杂 Batch 体系。

---

## 1. 目标

用「仓库已有 PNG + 下列已确认的自由/可商用素材」补全 missing_asset：

1. 优先消掉技能 / 状态 / 词条 / 基础 UI 的缺失引用（机制与界面报错）。
2. 再补装备、掉落、道具图标。
3. 再补角色、怪物、地牢瓦片与必要 VFX。
4. 仍匹配不上的，用占位图并登记，不要假装已解决。

完成后应达到：

- 场景与资源不再依赖不存在的 `.aseprite` 源文件。
- 缺失引用要么已映射到真实 PNG，要么明确标记为占位。
- 有一份来源与授权记录，以及一份映射表。

---

## 2. 约束

**要做**

- 先用 `04_recovered/sprites` 与 `product/sprites` 里已有 PNG，按文件名 stem 把 `.aseprite` 引用改成 `.png`。
- 只使用下文列出的素材库（或同等许可、风格接近的替代包，使用前记录来源与许可）。
- 像素图导入使用 Nearest，避免模糊。
- 每个下载包保留来源 URL、许可、日期。

**不要做**

- 不要从 `web.poecdn.com`、PoEDB 页面或 PoE GGPK 批量抓官方美术当工程贴图。
- 不要复制 Halls of Torment / Path of Exile 受保护资产。
- 不要把「缺少 .aseprite 源文件」继续当成必须等人给源的阻塞项。`.aseprite` 源视为永久放弃。

**策略声明（写入项目 Decision / product_state）**

```text
ART_SOURCE_POLICY = OWN_RECOVERED_PNG + APPROVED_FREE_PACKS
ASEPRITE_SOURCES  = PERMANENTLY_WAIVED
POE_CDN_ART       = NOT_USED_AS_GAME_STOCK
```

---

## 3. 工作顺序（逻辑顺序，不是调度方案）

1. 扫描 `product/` 内全部缺失引用，列出路径、期望后缀、引用来源、大致类别（技能 / 状态 / 词条 / 装备 / UI / 角色 / 地块 / VFX / 其它）。
2. 用仓库已有 PNG 做同名重映射。
3. 按下面三类素材补洞：技能状态词条 → 装备道具 UI → 角色怪物地牢与 VFX。
4. 统一导入设置，更新引用。
5. 剩余项做占位并归档清单。

本地 AI 可自行决定一次做完还是分几次做，不必按多 Agent 并行拆。

---

## 4. 素材来源

### 4.1 技能 / 状态 / 词条图标（先补）

| 资源 | 规格 | 授权 | 用途 |
|------|------|------|------|
| RPG Ability Icons（frosty_rabbid） | 24×24 | CC0 | 投射物、斩击、元素法术 |
| RPG Skill Icons（Viktor） | 64 / 128，可缩小 | CC0 | Buff / Debuff / 被动符号 |
| Pixel Art RPG Skill Icons（KURΛI） | 16×16 | 免费商用（禁止转售素材包） | 带品质边框的词缀与进阶技能 |
| Game-icons.net | 矢量 / PNG | CC BY 3.0 | 剪影占位，批量上色后垫底 |
| OpenGameArt CC0 技能合集 | 16×16 / 32×32 | CC0 / OGA-BY | 火球、冰刺、旋风等常见技能视觉 |

入口：

- https://frosty-rabbid.itch.io/rpg-ability-icons
- https://v-ktor.itch.io/rpg-skill-icons
- https://kurai7.itch.io/rpg-skill-icons
- https://game-icons.net/（CC BY，打包时保留作者列表）
- https://opengameart.org/（过滤 CC0，关键词 skill / spell / ability）

### 4.2 装备 / 道具 / 掉落 / 基础 UI

| 资源 | 规格 | 授权 | 用途 |
|------|------|------|------|
| Kenney – Tiny Dungeon | 16×16 | CC0 | 兵器、盔甲、药水、箱子 |
| Kenney – Micro Roguelike | 8×8 / 16×16 | CC0 | 小道具、小地图、极简地形图标 |
| Shikashi's Fantasy Icons | 32×32 | 免费可商用 | 药剂、矿石、卷轴、戒指项链 |
| RPG Pixel Art Icon Pack | 16×16 / 24×24 | CC0 | UI 框、金币、钥匙、消耗品 |

入口：

- https://kenney.nl/assets/tiny-dungeon
- https://kenney.nl/assets/micro-roguelike
- itch 上检索 Shikashi's Fantasy Icons、RPG Pixel Art Icon Pack，下载前核对页内授权

### 4.3 角色 / 怪物 / 地牢 / VFX

| 资源 | 规格 | 授权 | 用途 |
|------|------|------|------|
| Lords Of Pain（Pupkin） | 等轴 / 顶视 | Demo 免费；完整版以页内许可为准 | 暗黑写实骨架、恶魔，气质接近 Halls / Diablo |
| 0x72 Dungeon Tileset II | 16×16 | CC0 | 骷髅、恶魔、骑士 Idle/Run，深色地牢地块 |
| Pixel Art Hell Tiles & Enemies | 16×16 / 32×32 | 以页内为准（部分付费） | 熔岩、焦土、地狱生物 |
| Pipoya VFX | 序列帧 | 免费（以页内为准） | 斩击、火/冰/雷命中、受击粒子 |

入口：

- https://trevor-pupkin.itch.io/lords-of-pain
- OpenGameArt / itch 检索 0x72 Dungeon Tileset II（确认 CC0）
- itch 检索 Pixel Art Hell Tiles And Enemies
- Pipoya VFX 作者页（确认免费条款后再用）

付费包只用许可明确允许的部分；Demo 范围外的不要默认当可入库素材。

---

## 5. 目录与引用规则

建议落点（可按现有工程习惯微调，但语义保持不变）：

```text
product/sprites/
├─ _acquired/          # 下载原包，按来源分子目录，附 SOURCE.txt
├─ _mapped/            # 已按项目语义重命名的最终 PNG（场景只引用这里或原有 sprites）
│  ├─ skills/
│  ├─ status/
│  ├─ affixes/
│  ├─ equipment/
│  ├─ items/
│  ├─ ui/
│  ├─ actors/
│  ├─ tiles/
│  └─ vfx/
└─ _placeholders/      # 仍无匹配的占位图
```

- `_acquired` 只归档，不直接给场景引用。
- 每个来源目录的 `SOURCE.txt` 写：URL、许可、下载日期、包版本。
- 汇总授权：`product/sprites/_acquired/ATTRIBUTION.md`（CC BY 必须列出作者）。

---

## 6. 映射规则

1. **自有图优先**：`blizzard.aseprite` 若已有 `blizzard.png`（recovered 或 product），直接改引用。
2. **精确名**：技能 id、状态名、装备槽名能对上素材文件名就用。
3. **语义桶**：对不上精确名时，按元素/类型归类  
   fire / cold / lightning / physical / chaos / minion / aura / movement / potion / armor / weapon / ui
4. **占位**：仍空则放到 `_placeholders/`，清单里标 `PLACEHOLDER`，不要留悬空路径。

映射表建议保存为机器可读 JSON，例如：

```json
{
  "schema_version": 1,
  "policy": "OWN_RECOVERED_PNG + APPROVED_FREE_PACKS",
  "entries": [
    {
      "missing_ref": "res://sprites/skills/blizzard.aseprite",
      "category": "skill",
      "status": "MAPPED",
      "resolved_to": "res://sprites/_mapped/skills/blizzard.png",
      "source_pack": "frosty_rabbid_ability",
      "license": "CC0"
    }
  ]
}
```

`status` 只用：`OWN_REMAP` | `MAPPED` | `PLACEHOLDER`。不要长期留未登记的缺失。

---

## 7. Godot 导入

像素资源默认：

```ini
[rendering]
textures/canvas_textures/default_texture_filter=0
```

`0` = Nearest。图标与像素精灵不要开无必要的 mipmap。缩放尽量用整数倍（16→32→64）。

已是点阵的 16×16 / 24×24 包不要再做会模糊的二次缩放。非点阵图若必须缩小，用最近邻。

---

## 8. 完成标准

- 缺失清单覆盖扫描时的全部引用。
- 能用自有 PNG 解决的，都已改引用。
- 技能 / 状态 / 词条 / 基础 UI：不是已映射，就是已占位并登记。
- 装备 / 道具：同上。
- 若许可允许，至少有一套可用的深色地牢瓦片，以及若干通用敌人或 VFX 帧可加载。
- `ATTRIBUTION.md` 与映射表齐全。
- product_state 或 Decision 中记下上述策略，并不再把「缺少 aseprite 源」列为人类阻塞。

---

## 9. 给执行者的一句话

先吃仓库里已有的 PNG，再用本清单里的自由包按「技能状态词条 → 装备 UI → 角色地牢 VFX」补洞，改引用、记来源、占位收口。排工方式由本地 AI 自己决定。
