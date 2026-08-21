# Build 性能优化 — 渐进式披露索引

> **本目录是 `scripts/build/` 的文档侧镜像**。AI 涉及编译/打包耗时时，按本索引逐层深入，**不把 `COMPILE_PERFORMANCE_PLAN.md` 全文回填 `AGENTS.md`**。

---

## 1. 入口层级

| 层 | 文件 | 角色 | 何时读 |
|---|---|---|---|
| L0 | `AGENTS.md §6.1` | 全局硬规则 + 双模式默认行为（~30 行摘要） | 任何任务必读 |
| L1 | `docs/ai/AI_ENTRYPOINT.md §4` | 任务路由 + 最小构建入口 + `--mode fast/release` 示例 | 任务分发时 |
| L2 | `docs/architecture/PIPELINE.md §5` | 流水线总览 + 性能双模式摘要 | 理解 pipeline 时 |
| L2 权威 | `docs/build/COMPILE_PERFORMANCE_PLAN.md` | **20 章完整执行方案**（Timing/Cache/Worker/Queue/Attestation/BaseIndex/Batching/Staging/FAST/RELEASE/pck-patch） | **改 `scripts/build/*.py` 或优化耗时前必读全文** |
| L3 | `scripts/build/*.py` | 实现 | 编码时 |

---

## 2. 双模式速查

```powershell
# 日常迭代（默认，NOT PROMOTION ELIGIBLE）
python scripts/nlmod/build_mod.py --mod-id <id> --mode fast

# 晋升/发布（fresh + 3744/3744 + S0-S4 全量，Promotion 唯一合法）
python scripts/nlmod/build_mod.py --mod-id <id> --mode release
```

- `FAST` 允许：persistent compile cache、toolchain attestation 复用、base hash index、persistent staging、collision-safe batching、quick checks
- `RELEASE` 必须：fresh resolve/apply、validated 编译、fresh pack、full PCK+normalize、fresh embed、3744/3744 verify、roundtrip
- 缓存：`<repo_root>/.cache/`（`gdre/` `pack_stage/` `base_index/` `build_profile.json`），`MUTAGENIC_CACHE_ROOT` 可覆盖，已 `.gitignore`

---

## 3. 20 章导航（按 performance plan 顺序）

| 章 | 主题 | 优先级 | 关键产出 |
|---|---|---|---|
| §0 | 总原则 | — | FAST vs RELEASE 双路径底线 |
| §1 | Timing 基线 | P0 | `10_logs/<build-id>/timing.json` |
| §2 | Persistent Compile Cache | P1 | `.cache/gdre/` + cache key |
| §3 | GDRE Worker Autotune | P1 | `.cache/build_profile.json` |
| §4 | Build Queue | P1 | build semaphore |
| §5 | Toolchain Attestation Cache | P1 | `TOOLCHAIN_ATTESTATION_REUSED` |
| §6 | Immutable Base Hash Index | P1 | `.cache/base_index/` |
| §7 | Collision-Safe GDRE Batching | P2 | invocations 8→≤3 |
| §8 | Persistent Mutable Pack Staging | P2 | `.cache/pack_stage/` |
| §9 | FAST/RELEASE 双模式 | P1 | `--mode fast/release` |
| §10 | normalize_pck_md5 Gate | — | RELEASE 保持全量 |
| §11 | verify_exe_structure Gate | — | 3744/3744 必过 |
| §12 | GDRE --pck-patch 实验 | 实验 | A/B equivalence 后才入 FAST |
| §13 | 旧编译链防误用 | — | `LEGACY_FULL_COMPILE` |
| §14 | 性能报告 | — | FAST/RELEASE 打印 |
| §15 | 验收标准 | — | Case A-D |
| §16 | 性能目标 | — | invoke 0/1, 3744→touched |
| §17 | 多 Agent 拆分 | — | BUILD-X0~X7 |
| §18 | 集成顺序 | — | X0→X1+2+3→I1→X4+5→I2→X6→X7 |
| §19 | 停止条件 | — | <5% 不入，任何不一致 rollback |
| §20 | 最终交付 | — | baseline yaml |

---

## 4. 实施纪律

1. 严格按 `§18` 顺序单步推进：`实现 → benchmark → correctness regression → commit → push` 后再下一步
2. 每步提供 `before/after duration + speedup + functional diff + check_all + abs_path_scan + secret_scan`
3. 单步提速 <5% 且显著增复杂不入 canonical；任何 `.gde/PCK` 不一致或 S0/S1/S3/S4 回归立即 rollback
4. 每日默认 `FAST`，仅中央集成/Promotion 用 `RELEASE`

---

## 5. 相关文档

- 流水线总览：`docs/architecture/PIPELINE.md`
- 并行批次：`docs/ai/PARALLEL_BATCH_WORKFLOW.md`
- 性能 Plan 全文：`docs/build/COMPILE_PERFORMANCE_PLAN.md`（编译时必读）

*不要把本索引或 plan 全文复制回 AGENTS.md；保持渐进式披露。*
