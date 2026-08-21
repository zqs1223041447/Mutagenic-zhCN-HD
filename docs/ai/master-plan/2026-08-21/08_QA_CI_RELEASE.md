# QA、CI 与 Release

测试金字塔：schema/static → unit → headless integration → runtime → replay → visual regression → performance → soak。

P1 迁移初期优先：

- project parse/import/headless boot。
- GDScript parse/静态兼容清单。
- scene/resource load contracts。
- 核心数据数量与标识保持。
- 输入/存档/战斗 smoke。

Godot MCP 在可启动后用于编辑/检查/运行；Stagehand 等到第一可玩 Product baseline 后接入正式 runtime 回归。

Legacy CI 只保留到足以保护迁移参考事实，不继续扩建成双轨发布流水线。

Product development baseline 可在机器 Gate 成熟后自动晋升；Public Release 默认仍需用户明确批准。