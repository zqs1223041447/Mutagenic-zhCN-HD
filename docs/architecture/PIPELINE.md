# Legacy 3.5.3 构建管线（只读对照）

这是 **Godot 3.5.3** 声明式 MOD → PCK embed 的取证管线，对应仓库里现有的 `scripts/patch/`、`scripts/build/`、`scripts/validate/`。

**不是** Godot 4.7.1 Product 构建路径。Product 主线见 `GATES_AND_MIGRATION.md`。P1 不为这条管线继续做性能平台或新玩法 MOD。

不可变输入：`00_original/`、`03_raw/`、`04_recovered/`。禁止直接改它们。

---

## 管线（Legacy）

```
00_original/Mutagenic.exe
  → 03_raw（3744 paths）
  → 04_recovered（只读参考源码）
  → mods/<id>/mod.json（preimage_sha256 + expected_occurrences）
  → resolve → apply → compile → pack → fresh embed → candidate
  → S0 结构 / S1 boot / S2 smoke / S3 persistence / S4 semantic / S5 人工
```

| 阶段 | 脚本 |
|---|---|
| resolve | `scripts/patch/resolve_mod_chain.py` |
| apply | `scripts/patch/apply_mod.py` |
| compile | `scripts/build/compile_declared_scripts.py` |
| pack | `scripts/build/build_declared_pack.py` |
| normalize | `scripts/build/normalize_pck_md5.py` |
| embed | `scripts/embed_pck.py`（必须从 `00_original` 新鲜嵌入） |
| 结构校验 | `scripts/validate/verify_exe_structure.py` |

- 改动必须是结构化 patch，禁止对 `.gd/.tscn/.tres/.json` 做全局文本替换。
- 只编译 manifest 声明的脚本。
- 禁止在旧 modded EXE 上叠加。
- 仓库内路径从 `repo_root` 推导；禁止把宿主盘符写进 tracked 代码。

`mods/` 里已有的汉化 / Kinetic 补丁是 Legacy 产物，供对照与 Preservation，不是当前要继续扩的主线。
