# Canonical Pipeline — 架构总览（L2）

> **Authority**: L2 流水线权威，低于 `AGENTS.md`（L0）与 `status.json`（L1）。
> **渐进式披露**：本文件仅概述 canonical 流水线与验证分层；**构建性能优化的完整 20 章执行方案**见 `docs/build/COMPILE_PERFORMANCE_PLAN.md`（AGENTS.md §6.1 仅入口）。凡任务触及 `compile / pack / PCK / embed / verify` 耗时，必读该文件再动 `scripts/build/*.py`。

---

## 1. 唯一构建路径

```
pristine (00_original/Mutagenic.exe)
  → fingerprint
  → raw extraction (03_raw, 3744 paths)
  → recovered (04_recovered, 5058 files)
  → schema / declarative MOD (mods/<id>/mod.json, preimage + expected_occurrences)
  → resolve → apply → compile → pack → fresh embed → candidate
  → roundtrip / boot / semantic verify (S0-S5) → evidence → human-only promote → baseline
```

- **VM 定位**：部署/运行/观察/语义验证环境，**不是**构建系统。
- **NL2MOD 定位**：自然语言 → 声明式 MOD 的前端，**不得**复制第二套构建逻辑。

---

## 2. 声明式 MOD

所有改动必须是 `mods/<id>/mod.json`：

- `CODE_PATCH` / `VALUE_PATCH` / `RESOURCE_PATCH` / `ASSET_PATCH` / `TEXT_PATCH`
- 每条带 `preimage_sha256` + `expected_occurrences`
- 禁止全局文本替换 `.gd/.tscn/.tres/.json`（必须结构化 patcher + preimage 守卫）
- 禁止批量重编译所有恢复脚本（只编译 manifest 声明的）

---

## 3. 流水线阶段（与 performance plan 对应）

| 阶段 | 权威脚本 | 输出 | 说明 |
|---|---|---|---|
| resolve | `scripts/patch/resolve_mod_chain.py` | `modset.lock / resolved_mod.json` | 依赖链解析 |
| apply | `scripts/patch/apply_mod.py` | worktree | 结构化 patch 应用 |
| compile | `scripts/build/compile_declared_scripts.py` | `07_compiled/` | 仅声明 `.gd`，支持 `--cache` |
| pack_tree | `scripts/build/build_declared_pack.py` | `08_pack/` | 从 `03_raw` copy + 声明 overlay |
| pck_create | `scripts/build/*` + GDRE | `.pck` | 生成 PCK |
| normalize_md5 | `scripts/build/normalize_pck_md5.py` | normalized PCK | fail-closed 全量扫描 |
| embed | `scripts/embed_pck.py` + `fix_pe_pck_section.py` | candidate EXE | **fresh embed** 从 `00_original` |
| verify | `scripts/validate/verify_exe_structure.py` etc | evidence | S0-S5 分层 |

每个 build 唯一 `Build ID: YYYYMMDD-HHMMSS-<hash>`，产出 manifest 记录 `git_commit / game_fingerprint / schema_hash / toolchain_hash / modset_hash / original_exe_hash / candidate_exe_hash / encryption_key_id / build_time / host`。

---

## 4. 验证分层

- **S0 结构**：roundtrip 3744/3744、delta 精确、PCK checksum
- **S1 boot**：真实窗口/进程 + 无 ALERT + 无 fatal
- **S2 core smoke / S3 persistence / S4 mod-specific / S5 visual**（按需）
- **语义确认**：GDRE 从最终 EXE 恢复目标 `.gde`，确认新值已嵌入

每个 Gate 必须有证据文件（`verified_at / command / artifact`）。

---

## 5. 构建性能双模式（摘要，详情见 performance plan）

> **渐进式披露**：本节仅摘要，完整规范见 `docs/build/COMPILE_PERFORMANCE_PLAN.md` §9。任何优化不得削弱 RELEASE 的 fail-closed 验证链。

- `FAST DEV BUILD` (`--mode fast`): 日常迭代默认，允许 persistent compile cache、toolchain attestation 复用、base hash index、persistent pack staging、collision-safe batching、quick checks；标注 `NOT PROMOTION ELIGIBLE`。
- `CANONICAL RELEASE BUILD` (`--mode release`): 中央集成/Promotion/baseline/PR Gate 唯一合法路径；fresh 全量 + 3744/3744 + 全量 roundtrip；Promotion Candidate 必须此模式。
- 缓存根 `<repo_root>/.cache/`（`MUTAGENIC_CACHE_ROOT` 可覆盖），已 `.gitignore`；cache key 含 `相对路径+源码SHA+GDRE SHA+bytecode+工具版本+key指纹(SHA)`，禁止落盘真实 key。
- 并发：Coding 并行，Heavy Build/Verify 各 1 槽；CLI `--workers` > `build_profile.json` > 默认。
- 报告：`10_logs/<build-id>/timing.json` + `build.json` 分阶段 `wall_time_ms / cpu_time_ms / cache_hits / gdre_invocations / workers` 等。

**实施顺序**（性能 plan §18）：`Timing → Cache → Worker/Queue → Attestation/Index → Batching/Staging → FAST/RELEASE → pck-patch 实验`，每步 `实现→benchmark→回归→commit→push` 后再下一步。

---

## 6. 不可变与禁止项

- `00_original/**` / `03_raw/**` / `04_recovered/**` 不可修改（`03_raw` 3744 path，`04_recovered` 5058 files 已 manifest 绑定）。
- 禁止 hardlink `03_raw` 到可写 pack tree、禁止在旧 modded EXE 上叠加、禁止跳过 preimage、禁止关闭完整 S0、禁止抽样冒充完整 Gate、禁止硬编码宿主绝对路径。
- 仓库内路径必须从 `repo_root` 推导（`git rev-parse --show-toplevel` 优先）；仓库外路径经配置/环境变量/CLI 注入（`MUTAGENIC_*_ROOT` 命名）。

---

## 7. 阅读指引

- 新任务：`AGENTS.md` → `status.json` → `docs/ai/AI_ENTRYPOINT.md` → 本文件 → `docs/build/COMPILE_PERFORMANCE_PLAN.md`（如涉编译耗时）
- 性能优化任务：直接 `AGENTS.md §6.1` → `docs/build/COMPILE_PERFORMANCE_PLAN.md` 全文 → `scripts/build/*.py`
- 多 Agent 并行：`docs/ai/PARALLEL_BATCH_WORKFLOW.md`

*权威层级：AGENTS.md（L0）> status.json（L1）> 本文件与 docs/build/COMPILE_PERFORMANCE_PLAN.md（L2 流水线/性能）。*
