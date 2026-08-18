# Deployment Guide — 拉取即部署

> 仓库设计目标：**任何人 clone 后即可自行修改与本地构建**，无需依赖仓库外的秘密文件。
> 唯一需要自备的输入：一份**你自己拥有的原版游戏 EXE**（版权资产，永不入库）。

## 1. 仓库里有什么

| 目录 | 内容 | 入库 |
|---|---|---|
| `00_original/` | 原版 Mutagenic.exe（**自备**，见 §3） | ❌ 版权，永不入库 |
| `01_baseline/` | 原版指纹（sha256/size/PE） | ❌ |
| `02_tools/` | GDRE 工具链 + venv（**自备**，见 §5） | ❌ |
| `03_raw/` | 提取物 3744 路径（byte-preserving 入库） | ✅ |
| `04_recovered/` | 恢复源码 5058 文件（byte-preserving 入库） | ✅ |
| `05_schema/` `05_translation/` | schema contracts / 翻译数据 | ✅ |
| `manifests/` | raw/recovered/compile/pack manifest | ✅ |
| `mods/` | 声明式 MOD（mod.json） | ✅ |
| `scripts/` | 管线脚本 | ✅ |
| `06_worktree/…` `09_output/` `10_logs/` | 构建中间物 | ❌ 可再生 |

> 行尾保护：`.gitattributes` 对 `03_raw/**`、`04_recovered/**` 强制 `-text -eol`
>（byte-preserving），任何 checkout 都不会改写 CRLF/LF，`preimage_sha256` 绑定不破。

## 2. 快速开始（30 秒）

```powershell
python -m venv 02_tools/venv
02_tools/venv/Scripts/pip install -r requirements.txt
```

## 3. 放置原版 EXE 并验证指纹

```powershell
# 把你拥有的原版游戏 EXE 复制到仓库根
Copy-Item "C:\path\to\Mutagenic.exe" "00_original\Mutagenic.exe"
```

一键校验 + 恢复密钥 + 校验全树：

```powershell
python scripts/bootstrap_deploy.py
```

bootstrap 依次执行：
1. **指纹校验**：sha256 必须等于
   `c7b5d5a529cd776609f72730662f1f6a8049fe5de20541f7eafe06d0f2451209`（103,290,320 字节）
2. **密钥静态恢复**：`scan_script_key_static.py` 逐 32 字节窗口对 EXE 做
   AES-256-ECB 解密 + GDEC MD5 验证（约 1 亿窗口，8 进程约 2–3 分钟），
   恢复的 key 写入 `manifests/script_key.txt`（已 .gitignore，绝不入库）
3. **全树校验**：`03_raw`（3744 路径）+ `04_recovered`（5058 文件）逐文件
   sha256 对照 manifest

> 密钥为何不入库：AGENTS.md 硬性禁止泄露脚本加密密钥。但恢复过程完全
> 离线、确定性、可复现，任何 clone 者用自己的原版 EXE 都能恢复同一 key。

## 4. 构建（canonical pipeline）

```powershell
# 声明式 MOD 链 → 编译 → pack → fresh embed（从 00_original 新鲜嵌入）
python scripts/patch/resolve_mod_chain.py        # 解析 mods/* 链
python scripts/build/compile_declared_scripts.py # 只编译 manifest 声明的脚本
python scripts/build/build_declared_pack.py      # 构建 08_pack
# GDRE 打包 + 嵌入见 docs/architecture/PIPELINE.md
```

## 5. 工具链（02_tools/，不入库）

| 组件 | 获取方式 |
|---|---|
| `02_tools/gdre/gdre_tools.exe` | [godot-re-tools](https://github.com/bruvzg/godotRE) 发布页，Godot 3.5.3 对应版本（`--force-bytecode-version=3.5.3.stable`） |
| `02_tools/venv/` | `python -m venv` + `pip install -r requirements.txt` |

## 6. 修改一处文本/数值并重新构建（最小改动闭环）

```powershell
# 1. 编辑 04_recovered 中的 .gd/.tscn 确认目标文本与上下文
# 2. 在 mods/<id>/mod.json 声明 CODE_PATCH/VALUE_PATCH（preimage_sha256 = base 文件 sha）
python scripts/patch/apply_mod.py --mod mods/<id>          # 应用
python scripts/build/compile_declared_scripts.py           # 编译
python scripts/build/build_declared_pack.py                # 打包
# 3. fresh embed 生成候选 EXE，见 PIPELINE.md
```

## 7. 验证

- **roundtrip**：`scripts/probe_pristine_roundtrip.py`（3744/3744 提取比对）
- **boot**：`scripts/probe_boot.py`（真实窗口 + 进程存活 + 无 ALERT/fatal）
- **语义确认**：GDRE 从最终 EXE 恢复目标 .gde，确认新值已嵌入

## 8. 常见问题

| 问题 | 处理 |
|---|---|
| 原版 EXE 指纹不匹配 | 你持有的版本与开发版本不同（timestamp 1700160829 = 2023-11-16）；用你版本重建 `01_baseline/game_fingerprint.json` 后跑管线 |
| `bootstrap_deploy.py` 卡在密钥恢复 | 首次约 2–3 分钟，属正常；可用 `--procs` 调并发 |
| GDRE 缺失 | §5 下载后放入 `02_tools/gdre/gdre_tools.exe`，bootstrap 会做恢复链验证 |

## 9. 版权与合规

- `00_original`（原版 EXE）与一切 `09_output/*.exe` 候选产物均含原版游戏内容，
  属商业作品版权，**不得**上传 GitHub Releases 或公开分发。
- 仓库只含提取/恢复的**开发参考**（03_raw/04_recovered，开发用途）与全部
  管线规则、MOD 声明；clone 者需持有原版才能产出可玩 EXE。