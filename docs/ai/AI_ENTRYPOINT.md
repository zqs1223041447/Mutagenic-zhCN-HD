# AI 工作入口与任务路由（AI_ENTRYPOINT）

> **角色**：所有 AI 新任务的统一入口。开始任何工作前**固定读取**：
> 1. `AGENTS.md`（L0 唯一全局规范）
> 2. `status.json`（L1 机器权威状态）
> 3. 本文件（任务路由）
> 4. 与任务对应的 workflow 文档（docs/workflows/ 或 docs/dev-environment/）

---

## 1. 任务路由表

| 用户请求 | 路由 | 构建路径 |
|---|---|---|
| 汉化更多内容 | `mods/localization/`（38 切片）+ `translation/glossary` | canonical build |
| 自定义 MOD（数值/技能/怪物等） | 手工 `mods/custom/<id>/mod.json` **或** NL2MOD（`scripts/nlmod/`） | canonical build |
| "用自然语言改 X" | NL2MOD 前端（`docs/ai/nl2mod-guide.md`） | canonical build |
| 自然语言 MOD 需求/疑问/未确定参数 | **按需**加载 `nl2mod-requirement-analysis` skill → 规则 `docs/ai/nl2mod-requirement-analysis.md`（不进 Preflight） | 确认后 canonical build |
| Runtime bug（游戏运行异常） | canonical candidate → VM 验证（Hyper-V skill） | deploy+verify |
| 管线 bug | `scripts/pipeline/` | 修管线，不动输入 |
| VM/工具链 bug | `scripts/vm/` + Hyper-V skill | VM 运维 |
| 存档/持久化问题 | `mods/localization/zh_CN` + P7 实验记录 | canonical build |

---

## 2. 关键决策速查（"一个问题一个权威答案"）

| 问题 | 看哪里 |
|---|---|
| 哪些行为禁止？ | `AGENTS.md` |
| 当前版本/状态？ | `status.json` |
| 人类可读状态？ | `PROJECT_STATE.md`（生成视图） |
| 游戏原始指纹/提取/恢复？ | `manifests/provenance/*` |
| 哪些 MOD 构成版本？ | `modset.lock.json` |
| 如何构建？ | `docs/architecture/PIPELINE.md` + `scripts/pipeline/` |
| 自然语言怎么变 MOD？ | `docs/ai/nl2mod-guide.md` |
| 自然语言需求怎么分析？（按需） | `nl2mod-requirement-analysis` skill → `docs/ai/nl2mod-requirement-analysis.md` |
| 如何跑游戏/验证？ | `docs/dev-environment/VM_DEVELOPMENT.md` + Hyper-V skill |
| 哪个是 baseline？ | `status.json` trusted_baselines + `releases/*.json` |
| 历史大文件在哪？ | `G:\Mutageni-Archive\`（archive index） |

---

## 3. 开始工作前（Mandatory Preflight）

1. **读** AGENTS.md + status.json + 本文件。
2. **确认**目标资产分类（Source of Truth / Immutable / Generated / Evidence / Local）。
3. **确认** 00_original/03_raw/04_recovered 未被动过（只读）。
4. **确认** 目标 MOD manifest 的 preimage 与 expected_occurrences 正确。
5. **确认** 有回滚路径（checkpoint 或 git commit）。

---

## 4. 构建/验证最小命令（canonical）

```powershell
# 构建（一键流水线，NL2MOD 或手工 MOD 均适用）
python scripts/nlmod/build_mod.py --mod-id <id>

# 或手工 canonical（见 docs/architecture/PIPELINE.md）
python scripts/patch/resolve_mod_chain.py ...
python scripts/patch/apply_mod.py ...
python scripts/build/compile_declared_scripts.py --worktree <patched> --manifest <resolved> --out <dir> --report <file>
python scripts/build/build_declared_pack.py ...
python scripts/embed_pck.py ...

# 验证
python scripts/probe_boot.py <candidate> --seconds 15   # S1 boot
# 语义确认（权威）：GDRE 恢复目标 .gde 验证新值
```

> **编译加速（v8.1+）**：`compile_declared_scripts.py` 已内置去重（1284 声明条目 → 57 唯一 .gd）+ 按目录批量 `--compile` + 并行实例（`--workers N`，默认 4）+ 增量缓存（`--cache <dir>`，按源文件 sha256 复用 `.gde`）。全量冷编译 ~13s；缓存热编译 ~0.3s、0 次 GDRE 启动。迭代时给 `build_mod.py` 传 `--compile-cache <dir>`（默认 `<out>/compile_cache`）即可复用。产物与旧链路逐字节一致（gde/remap sha256 已对齐验证）。

---

## 5. 工作区边界（勿越界）

- **宿主 `G:\opencode-Mutageni`**：Source of Truth（Git 管理）+ Immutable（00/03/04）+ 本地工具。
- **VM `C:\dev\Mutageni`**：部署/运行/观察执行环境，不编辑源码、不做 canonical build。
- **归档 `G:\Mutageni-Archive\`**：E2/E3 证据历史（索引 + manifest，不入活动区）。
- **禁止**：F: 盘访问、修改 00/03/04、泄露 key、自动晋升 baseline。
