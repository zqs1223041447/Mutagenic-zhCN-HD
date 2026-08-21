# Mutagenic AI Development Master Plan — Slim 2026-08-21

这是 2026-08-21 用户批准后的**裁剪版执行计划**。旧 38 份规划包不再作为执行入口。

核心决议：

1. Godot 4.7.1 stable 是唯一活动产品引擎。
2. Godot 3.5.3 仅保留只读 Legacy Reference，不维持双轨 Gameplay/Build/CI。
3. 先迁移、先形成可玩基线，再逐步补强自动化基础设施。
4. AI 工厂坚持 0 人工代码、多 Agent、worktree、中央集成；但不提前建设没有测量收益的复杂平台。
5. Halls of Torment 影响视觉/密度/反馈，不改变主动 ARPG 核心。
6. POE-like 深度通过原创机制实现，不复制受保护内容。

执行顺序：

`P0 仓库收口 → P1 Godot 4.7.1 迁移 → P2 最小 AI 自治闭环 → P3 功能回归 → P4 Halls 风格 → P5 Build/装备/怪物/Map → P6 Atlas/Endgame → 内容扩张`

本目录共 12 份核心文档，AI 只需按任务读取相关文件，不再每次加载 38 份同级文档。