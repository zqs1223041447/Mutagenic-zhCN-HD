# batchctl — 批次自动化 CLI（B1-X0）

`batchctl` 为仓库内 AI 批次工作流提供命令式生命周期管理：认领（claim）、状态（status）、交接（handoff）、汇总（collect）、预检（preflight）与清理（cleanup）。所有命令在**仓库内**或**任务 worktree 内**执行，fail-closed（失败即拒绝），不产生副作用除非命令本身要求写文件。

## 运行环境

- Python：项目 venv `02_tools/venv/Scripts/python.exe`（仅用标准库，无第三方依赖）。
- 模块：`scripts/ai/batchctl.py`（入口 `main`），依赖 `repo_util.py` / `abs_path_scan.py` / `secret_scan.py`。

## 命令

```
python scripts/ai/batchctl.py claim B1 --task Z1 --label "示例任务" [--dry-run]
python scripts/ai/batchctl.py status B1
python scripts/ai/batchctl.py handoff B1 --task Z1 --summary "完成 X" --exit-code 0 [--json]
python scripts/ai/batchctl.py collect B1 [--json]
python scripts/ai/batchctl.py preflight B1 [--worktrees-root <dir>]
python scripts/ai/batchctl.py cleanup B1 --batch-dir <dir> [--force] [--allow-unmerged] [--delete-branch]
```

### claim
- 在批次锚点分支 `batch/b<batch>` 上创建任务 worktree；任务状态 `claimed`。幂等：重复 claim 同一任务返回已存在的工作树而非报错。
- `--dry-run`：只报告将创建的位置，不写任何文件、不动 git。
- 任务 id 必须匹配 `^[A-Za-z0-9_-]{1,32}$`（默认示例 `Z1`）。

### status
- 列出批次任务：状态（`claimed`/`handed_off`）、worktree 路径、HEAD。`main` worktree 也会列出。

### handoff
- 记录 `summary` / `exit_code` 到 `status.json` 任务条目，状态置为 `handed_off`；`--task` 必须与 claim 时一致。重复 handoff 允许（覆盖更新），但未 claim 的任务报错。
- `--json`：输出机器可读报告（含 3 项处置决策的按项清单）。

### collect
- 汇总批次内所有 `handed_off` 任务的交接报告，检查**未完成交接**（handoff 缺失或 exit_code != 0），输出合并 YAML/JSON。任何任务未完成 → 汇总标 FAIL（fail-closed）。

### preflight
- 全仓扫描（绝对路径硬编码 + secret 扫描），并检查批次锚点分支上**已认领任务是否触碰不可变目录**（`00_original`/`03_raw`/`04_recovered`）。触碰即失败并列出任务；预检在 `batch/b<batch>` 锚点创建/推进。
- `--worktrees-root <dir>`：覆盖 worktree 根目录推导（测试与异构布局用）。

### cleanup
- 删除批次目录 `--batch-dir` 及其 worktree；未合并的修改默认拒绝，需 `--allow-unmerged` + `--force`；`--delete-branch` 同时删除 `batch/b<batch>` 分支。执行后复扫确认无残留。

## 失败语义（fail-closed）

- 绝对路径扫描 `production_hardcode` 级别命中即 FAIL（`abs_path_scan.py`）。
- `status.json` 缺失/损坏 → 命令拒绝执行。
- handoff 只接受已 claim 且未闭合的任务；collect 遇未完成交接即整体失败。
- cleanup 默认不删任何有未合并修改的内容。

## 已知可移植性债务（保留项，非故障）

以下命中被归类为本地配置/历史证据，扫描器不视为 `production_hardcode`：

| 位置 | 分类 | 说明 |
|---|---|---|
| `manifests/*`（含 baseline、compile_manifest、raw_manifest、recovered_clean_manifest） | provenance_metadata | 历史证据快照，`file.path`/`worktree`/`root` 字段保留 |
| `03_raw/`、`04_recovered/` 内路径 | provenance | 只读来源区 |
| `tools.lock.json` | local_config | 本机构建工具链事实 |
| `status.json` | provenance | 批次状态证据 |
| `docs/` 下示例路径 | docs_example | 文档示例/占位符 |
| `.opencode/skills/**` | local_config | AI 工作台本地工具（如 VM 脚本中的 `G:\VMs`），含可移植性债务注释 |
| `scripts/merge_fonts3_hinted.py` 的 `C:/Windows/Fonts/Deng.ttf` | local_config | 系统字体依赖 |

## 测试

```
python -m unittest discover -s scripts/ai/tests -t scripts/ai/tests
```

56 个测试覆盖：claim 幂等、handoff 只写不读密钥、collect 聚合、preflight 不可变触碰检测、cleanup 拒绝未合并、dry-run 无副作用、全仓扫描无 production_hardcode（本轮迁移后 0 FAIL）、secret 脱敏与 key 文件永不输出内容。
