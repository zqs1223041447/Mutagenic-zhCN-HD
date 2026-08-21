# Fresh Clone — Godot 4.7.1 Product 单主线

> 目标：新机器/新 AI 会话直接进入固定集成分支，不再误落 `main`，也不被 Legacy 私有资产阻塞 Product 开发。

## 1. Clone 固定分支

```powershell
git clone --branch agent/kinetic-arcane-remaster-foundation --single-branch https://github.com/zqs1223041447/Mutagenic-zhCN-HD.git
cd Mutagenic-zhCN-HD
git branch --show-current
python scripts/bootstrap/product_doctor.py
```

期望 branch：

`agent/kinetic-arcane-remaster-foundation`

## 2. Product 工具链

必需：

- Git >= 2.40
- Python >= 3.11
- Godot 4.7.1 stable

如果 Godot 不在 PATH，设置：

```powershell
$env:MUTAGENIC_GODOT4 = "<your-godot-4.7.1-executable>"
python scripts/bootstrap/product_doctor.py
```

脚本结果：

- `PRODUCT_DEV_READY`：仓库与 Godot 4.7.1 就绪。
- `PRODUCT_REPO_READY_TOOLCHAIN_BLOCKED`：仓库可工作，但本机尚未找到正确 Godot；AI 可以继续做静态迁移/文档/数据任务，不得伪称 runtime PASS。

## 3. 进入任务前读取

1. `AGENTS.md`
2. `state/product_state.json`
3. `docs/ai/AI_ENTRYPOINT.md`
4. `docs/ai/master-plan/2026-08-21/00_README.md`
5. `state/product_state.json.next_batch`

## 4. Legacy 私有资产

`00_original/Mutagenic.exe`、script key、GDRE 只在需要复验 Godot 3.5.3 Legacy 历史构建时使用。

**Product Godot 4.7.1 迁移和新功能开发不得以缺少这些私有资产为默认阻塞条件。**

旧的 `bootstrap_dev_env.py` / `dev_doctor.py` 继续保留给 Legacy 复验；Product 默认用 `product_doctor.py`。

## 5. 工作区

推荐固定结构：

```text
<WORKSPACE_ROOT>/
├─ Mutagenic-zhCN-HD/   # 唯一主 clone
├─ worktrees/           # AI 管理
├─ tool-cache/
├─ runtime/
├─ artifacts/
└─ private/
```

仓库不得记录 `<WORKSPACE_ROOT>` 的真实绝对路径。