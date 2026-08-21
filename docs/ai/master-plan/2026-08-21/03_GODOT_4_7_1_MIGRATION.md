# Godot 4.7.1 单主线迁移

## 原则

迁移是一次性主线转换，不维持双活 Product。

`04_recovered` 只读 → 生成/转换到 `product/` → 修兼容性 → 垂直切片恢复可玩 → 3.5.3 正式 retired as development platform。

## P1 顺序

1. 建立 Godot 4.7.1 `product/project.godot` seed。
2. 自动清点 GDScript 3→4 语法/API、Scene/Resource、Input、Autoload、Save、Audio、Particles、Shader 等兼容问题。
3. 用工具转换能转换的内容；其余生成机器可读 blocker inventory。
4. 按切片恢复：Boot → Menu → Character → World → Combat → Equipment/Skills/Passive → Save。
5. 每个切片都建立与 Legacy 事实对应的保持契约。

## 禁止

- 不在 3.5.3 同步实现新 Product 功能。
- 不因为迁移困难就删掉核心系统。
- 不先重写整个游戏再第一次运行；始终追求尽早可启动、可测试。

## P1 完成条件

Godot 4.7.1 Product 能独立启动并完成核心玩法闭环，之后 Legacy 构建链只剩 forensic/reference 用途。