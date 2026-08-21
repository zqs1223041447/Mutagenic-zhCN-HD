# Gate 路线与下一批

## 路线

P0 仓库收口 → P1 Godot 4.7.1 迁移 → P2 最小 AI 自治 → P3 原功能回归 → P4 Halls 风格 → P5 POE-like Build/装备/怪物/Map → P6 Atlas/Endgame。

没有固定日期承诺；每阶段只在退出 Gate 满足后推进。

## P0 退出 Gate

- 固定分支 Fresh Clone 正确。
- 当前 CI 绿。
- Product/Legacy 权威关系明确。
- 12 份核心计划已入库。
- PR #1 与真实状态一致。

## P1 Wave A（可并行）

- **P1-X0 Conversion Seed**：创建 `product/` Godot 4.7.1 seed、转换日志、首次 import/parse 证据。
- **P1-X1 Compatibility Inventory**：静态扫描 3.5.3→4.x API/语法/scene/resource incompatibility，输出 blocker DAG。
- **P1-X2 Product Toolchain Closure**：Godot 4.7.1 headless 命令、doctor、tool lock、CI 最小 Product job。
- **P1-X3 Preservation Contracts**：冻结 4 Classes、8 Specs、53 Skills、60 Supports、326 Passive、88 Keystone、149 Stats、24 Tags、Equipment/Save/Combat 等迁移保持清单。

Wave A 全部 handoff 后由 Coordinator 统一合并，再安排 Wave B：Boot/Autoload/Input、Menu/Character/Save、World/Combat、Equipment/Skill/Passive 四条恢复线。