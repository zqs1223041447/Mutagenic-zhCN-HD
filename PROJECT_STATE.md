# Mutagenic 当前项目状态

> 2026-08-21 起实行 Product/Legacy 状态分层。

## Product 当前权威

机器状态：`state/product_state.json`

- 当前阶段：`P0_REPO_CLOSURE`
- 唯一产品引擎：Godot 4.7.1 stable
- 固定集成分支：`agent/kinetic-arcane-remaster-foundation`
- 决议：取消 Godot 3.5.3 / 4.7.1 双活开发；3.5.3 降级为只读 Legacy Reference。
- 下一主 Gate：`P1_GODOT_4_7_1_MIGRATION_READY`

## Legacy 当前事实

`status.json`、`releases/*.json`、`docs/ai/audits/**` 保留 B1/B2/B3、Localization、P7 与 `3B6427B3...` 的历史事实。

这些事实继续可用于迁移对照，但不再决定新产品路线。历史治理 hold 不允许被伪造成已验证事实，也不阻塞 Godot 4.7.1 Product 迁移启动。

## 本次治理收口

- Fresh Clone 改为显式 clone 固定集成分支。
- Release manifest 的宿主绝对归档路径改为逻辑 `<archive_root>` 定位。
- 新增裁剪后的 12 份核心 Master Plan。
- 新增 Product toolchain requirements 与 `product_doctor.py`。
- PR #1 应同步到 Godot 4.7.1 单主线现状并继续保持 Draft。

## 下一批本地 AI 工作

在本提交 CI 通过后启动 P1 Wave A：

1. P1-X0：Godot 4.7.1 Conversion Seed。
2. P1-X1：3.5.3 → 4.x API/语法/资源兼容性静态清单。
3. P1-X2：Product Toolchain + headless 验证闭环。
4. P1-X3：迁移保持契约，冻结现有技能/Support/Passive/装备/存档/战斗事实。

详见 `docs/ai/master-plan/2026-08-21/10_GATE_ROADMAP_NEXT_BATCH.md`。