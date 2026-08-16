# data/poedb — POEDB/poewiki 参考数据（本地结构化 JSON）

> 用途：把 POEDB / poewiki 的机制与数据参考落成本地结构化 JSON，供后续 MOD 设计
> （掉落表、地图机制、兽园配方、传奇装备 trigger/condition 标注）使用。
> 本目录是 **Source of Truth 数据目录**，会进入 Git。
> 数据为参考信息，**不是**对 Mutagenic 的绑定实现；落地到游戏需按
> `docs/ai/nl2mod-requirement-analysis.md` 的 POEDB 规则走需求分析。

## 1. 文件清单

| 文件 | 内容 | 记录数 | 覆盖 |
|---|---|---|---|
| `maps.json` | 地图：tier / monster_level / boss_names / 独特地图词缀 | 194 | 独特地图完整(词缀)，普通地图完整(等级/首领) |
| `divination_cards.json` | 命运卡：名称 / 堆叠 / 奖励 / 抽样掉落 | 464 | 列表完整，dropped_by 抽样 |
| `beasts.json` | 野兽：family / damage% / life% / spectre / 配方角色 | 51 | 抽样(配方兽+首领) |
| `beastcraft_recipes.json` | 血祭坛配方：category / 主兽 / 填充兽数 / 备注 | 79 | 完整(3.29 状态) |
| `map_device_recipes.json` | 地图装置配方：消耗品 → 结果图 / 等级 | 88 | 完整 |
| `map_mods.json` | 地图腐化词缀 + 合成成本 + tier 段 | 12+16 | 抽样结构 |
| `unique_items.json` | 代表性传奇：mods + 人工 mod_type 标注 | 13 | 抽样(重点 trigger/condition) |

每个 JSON 顶层统一结构：

```json
{
  "schema_version": 1,
  "as_of": "2026-08-16",
  "source": ["<抓取 URL 列表>"],
  "coverage": "完整/部分/抽样 + 说明",
  "items": [ ... ]
}
```

## 2. 字段说明（snake_case，无 HTML）

- **maps**：`name` `url` `tier` `monster_level`(=area_level) `boss_names[]` `mods[]`
  `requires_level`(仅独特地图物品等级) `drop_location`(未抓取) `unique_flag`
- **divination_cards**：`name` `slug` `url` `stack_size` `reward`(原样文本)
  `drop_level`(抽样) `dropped_by[]`(抽样)
- **beasts**：`name` `family`(Farric/Craicic/Fenumal/Saqawine/Primal/Vivid/Wild/boss)
  `damage_pct` `life_pct` `spectre` `tame_beast` `url` `recipe_roles[]`
- **beastcraft_recipes**：`category` `description` `main_beasts[]`(1-2 只)
  `filler_count`(配方固定 4 只，主兽外的填充数) `notes`
- **map_device_recipes**：`inputs[]`(消耗品) `result_map` `map_url` `level`
  （`result_map=null` 表示献祭类，无结果图）
- **map_mods**：`tier_ranges[]`（white/yellow/red/special）
  `map_corruption[]`（`description` + `weights{tag:weight}`）`map_costs[]`
- **unique_items**：`name` `base_type` `class` `level_req` `mods[]`(原样)
  `mod_type{trigger, condition, cost}`（**人工标注**，非游戏字段）
  `url`

### mod_type 标注约定（unique_items）

标注对象是物品上的**机制性词缀**，字段值示例：

```jsonc
{ "trigger": "trigger_on_hit" | "trigger_on_attack" | "trigger_on_crit" |
              "trigger_on_kill" | "trigger_on_bow_attack" | "grant_skill" | null,
  "condition": "melee_critical_strike" | "minion_spells" | "stat_threshold" |
               "if_crit_recently" | "on_minion_death" | null,
  "cost": "life_cost" | "self_damage" | "life_sacrifice_via_skill" | "no_cost_when_triggered" | null }
```

设计时遵循 `docs/ai/nl2mod-requirement-analysis.md` §8：Trigger / Condition / Effect
做成本地通用能力，由物品数据引用，而不是把特殊代码散落到脚本里。

## 3. 抓取方法（可复现）

- 列表页用 `webfetch` 抓 poedb.tw（如 `/us/Maps`、`/us/Divination_Cards`、`/us/Beast`），
  再用 Python 脚本解析 markdown 结构入库。
- 机制与配方表以 poewiki 兜底/为主（`/wiki/Beastcrafting`、`/wiki/Map`）。
- poedb 逐物品页（如 `/us/Mjölner`）用于独特物品词缀原文与传奇物品 mod_type 标注。
- 数据日期 `as_of=2026-08-16`（Allflame / 3.28+ 时代数据）。

## 4. 已知缺口 / 下一步

- `drop_location`（地图掉落来源）与 `dropped_by` 仅抽样；全量需逐页抓取（464 卡 / 100+ 图）。
- 普通地图词缀（前缀/后缀/隐式 + weight/tier）未入库，见 poewiki `List_of_map_mods`。
- 野兽完整 1025 行统计表已解析（临时），未全量入库，可随时补。
- 独特地图 boss_names 大多缺失（poewiki 布局不同），如需可从各图页补。

### 落地建议：掉落表模型（map_id → item_id → drop_weight）

建议按下面结构组织本地掉落表，作为 MOD 声明的数据输入：

```jsonc
// mods/<xxx>/drop_tables.json
{
  "drop_tables": [
    {
      "map_id": "Burial_Chambers",
      "entries": [
        { "item_id": "divination_card:the_doctor", "drop_weight": 100, "drop_level": 75 },
        { "item_id": "unique:the_doctor_reward",   "drop_weight": 1 }
      ]
    }
  ]
}
```

- `map_id` 对齐 `maps.json` 的 `name`（slug 化）。
- `item_id` 建议统一命名空间：`divination_card:*` / `unique:*` / `beast:*`。
- `drop_weight` 为相对权重；`drop_level` 决定该掉落是否可出现在该图（对齐
  `divination_cards.json.drop_level` 与地图 `monster_level`）。
- 设计后再走 canonical pipeline（`docs/architecture/PIPELINE.md`）产出 MOD，勿直接改游戏脚本。
