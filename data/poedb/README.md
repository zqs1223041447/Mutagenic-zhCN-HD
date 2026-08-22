# data/poedb — 外部机制参考

本地 JSON，来自 POEDB / poewiki 的**机制抽样**，供以后抽象设计对照。

**不是** Mutagenic 的 Source of Truth，也不是绑定实现。`PRODUCT_CONTRACT.md`：External Reference → Mechanism Abstraction → Mutagenic Original Design。不得复制受保护资产、文本、名称或数值表；不得默认批量抓取。P1 不展开 Item / Endgame 实现。

| 文件 | 内容 |
|---|---|
| `maps.json` | 地图 tier / 等级 / 首领 |
| `divination_cards.json` | 命运卡抽样 |
| `beasts.json` / `beastcraft_recipes.json` | 野兽与配方参考 |
| `map_device_recipes.json` / `map_mods.json` | 地图装置 / 地图词缀结构 |
| `unique_items.json` | 少量传奇 trigger/condition 标注 |

落地到游戏必须改成 Mutagenic 自己的 schema 与命名，不能把本目录当 drop-in 数据。
