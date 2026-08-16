# Mutageni 隔离 Windows 开发 VM 环境文档

> 状态：**已建立并验收**（2026-08-15）
> 虚拟机方案：**Windows 原生 Hyper-V**
> 本文件是后续开发 AI 的入口文档，替代所有临时命令记录。

---

## 1. 方案选择

**采用 Hyper-V**，原因：

- 宿主机（Windows 10 Pro 19045, AMD Ryzen 7 5700X3D, 32GB RAM）在用户修复后已完整启用 Hyper-V（全部功能 Enabled，vmms 运行，Get-VMHost 正常）。
- Hyper-V 是宿主自带虚拟化，零额外软件、支持 production checkpoint、资源开销低。
- 用户明确要求放弃 QEMU/WHPX 方案（QEMU 已在上一轮完整移除）。

**上一轮 QEMU 已彻底清理**（本轮验证）：无 qemu 进程 / PATH 无条目 / F:\Program Files\qemu 已删 / 无卸载注册表项 / winget 无记录 / 无监听端口。

---

## 2. VM 配置

| 项目 | 值 |
|---|---|
| VM 名称 | `Mutageni-Dev` |
| Generation | 2 (UEFI) |
| vCPU | 4 |
| 内存 | 动态内存：Min 4GB / Startup 8GB / Max 16GB |
| VHDX | 120GB 动态扩展，`G:\VMs\Mutageni-Dev\Virtual Hard Disks\Mutageni-Dev.vhdx` |
| 网络 | Default Switch (NAT)，guest IP `172.22.30.219`（DHCP 可能变化） |
| Secure Boot | Off（Windows 已安装完成，为兼容虚拟显卡渲染关闭） |
| Checkpoint 类型 | Production |
| 存储路径 | `G:\VMs\Mutageni-Dev\`（Virtual Machines / Virtual Hard Disks / ISO） |

Windows guest：**Windows 10 Enterprise Evaluation 22H2**（19045，SHA-256 `EF7312733A9F5D7D51CFA04AC497671995674CA5E1058D5164D6028F0938D668`）。

---

## 3. VM 内账户与远程通道

| 账户 | 密码 | 角色 |
|---|---|---|
| `dev` | `REDACTED` | Administrators（自动化通道，WinRM 已启用） |
| `ZZZ` | 无 | 本地用户（用户手动安装时创建） |

- WinRM：VM 内已 `Enable-PSRemoting`，防火墙已关闭（开发 VM 内网）。
- 宿主 TrustedHosts 已加入 `172.22.30.219`。
- 远程连接示例（在宿主 PowerShell）：
  ```powershell
  $cred = New-Object PSCredential('dev', (ConvertTo-SecureString 'REDACTED' -AsPlainText -Force))
  $s = New-PSSession -ComputerName 172.22.30.219 -Credential $cred
  Invoke-Command -Session $s -ScriptBlock { hostname }   # DESKTOP-A4DG3RP
  ```
- 文件传输：`Copy-Item -Path <host> -Destination <vm> -ToSession $s -Recurse -Force`

---

## 4. 项目布局（VM 内）

```
C:\dev\Mutageni\
  00_original/      原始游戏（Mutagenic.exe 指纹 C7B5D5A5...）
  01_baseline/      基线指纹
  02_tools/         工具链（venv + gdre + 字体）
  03_raw/           原始提取（3744）
  03_raw_gdre/      GDRE 恢复参考
  04_recovered/     恢复源码（5058，已验证 clean manifest 一致）
  05_schema/        游戏 schema
  05_translation/   翻译工作
  06_worktree/      构建 worktree
  07_compiled/      编译产物
  08_pack/          PCK 打包
  09_output/        输出
  10_logs/          状态（status.json + P7 candidate）
  manifests/        manifest 与哈希
  mods/             MOD 定义
  scripts/          Python 构建工具
  docs/             文档
  AGENTS1.md / PROJECT_STATE.md / tools.lock.json / 汉化.md
```

**原则：宿主 `G:\opencode-Mutageni` 是只读参考源；VM `C:\dev\Mutageni` 是实际开发工作区。** 不要在宿主项目里做实时编辑或生成缓存。

---

## 5. 工具链版本（全部为项目事实，非推定）

| 工具 | 版本 | 位置 | 验证 |
|---|---|---|---|
| Python | 3.11.15 | `02_tools\venv\Scripts\python.exe` | `--version` → Python 3.11.15 ✓ |
| PyCryptodome | 3.23.0 | venv | `from Crypto.Cipher import AES` ✓ |
| fontTools | 4.63.0 | venv | `from fontTools.ttLib import TTFont` ✓ |
| frida | 17.17.0 | venv | `import frida` ✓ |
| GDRE Tools | 2.6.4 | `02_tools\gdre\gdre_tools.exe` | `--version` → Godot RE Tools v2.6.4 ✓ |
| git | 2.55.0 | VM 系统 | `git --version` |
| uv | 0.12.5 | `C:\Users\dev\.local\bin\uv.exe` | `uv --version` |
| VC++ Redist | 14.44.35211 (x64) | VM 系统 | 注册表已确认 |

> 注：venv 是**在 VM 内重建**的（宿主 venv 的 uv trampoline 指向宿主 Python 路径，复制后失效）。重建命令：
> `C:\Users\dev\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe -m venv C:\dev\Mutageni\02_tools\venv`
> 依赖安装：`pip install pycryptodome==3.23.0 fonttools==4.63.0 frida==17.17.0 colorama prompt_toolkit pygments wcwidth websockets`

---

## 6. 项目完整性验证（已执行）

**04_recovered clean manifest 验证（VM 内）**：
```
OK       = 5058
MISMATCH = 0
MISSING  = 0
VERDICT  = PASS
```
与宿主验证结果完全一致（`G:\VMs\Mutageni-Dev\verify_recovered_vm.py` 脚本，VM 内 `C:\dev\Mutageni\verify_recovered_vm.py`）。

---

## 7. Runtime smoke test（P7-FIX candidate）

candidate：`C:\dev\Mutageni\10_logs\P7-fix-persistence-20260814\runtime_candidate\Mutagenic.exe`

| 检查 | 结果 |
|---|---|
| SHA-256 | `83970CCF4B258D5C6370925BE7DEB574EC601B71D4A16F8D1FD2FBCFB7D3C495` ✓（与项目记录一致） |
| 相邻 DLL | `steam_api64.dll`（DCFAA13A...）已放置同目录 ✓ |
| VC++ 运行库 | 缺失导致 0xC0000135 → 已装 Redist 后解决 ✓ |
| 引擎启动 | GLES2 模式启动，进程存活 20s+，responding=True，无 ALERT、无 fatal ✓ |
| 视觉渲染 | ⚠️ VM 无 GPU 直通（Microsoft Hyper-V Video 虚拟显卡），窗口无法创建。**最终视觉/游玩验证在宿主机执行**（任务规则允许：VM 内开发构建 + 宿主最终验证） |

**重要**：`probe_boot.py` 在 VM 内 verdict FAIL 是**预期行为**（无窗口 = 无 game_window/boot marker），不是 candidate 本身问题。candidate 在宿主已通过完整 boot gate（见 `10_logs\P7-fix-persistence-20260814\machine_evidence.json`，PASS + human checkpoint 已确认持久化）。

启动命令（VM 内）：
```powershell
& 'C:\dev\Mutageni\10_logs\P7-fix-persistence-20260814\runtime_candidate\Mutagenic.exe' --video-driver GLES2
```

---

## 8. 恢复点（Checkpoint）

| 名称 | 创建时间 | 内容 |
|---|---|---|
| `00-clean-os` | 2026-08-15 10:31 | Windows 基础系统 + 手动安装完成 |
| `01-dev-toolchain` | 2026-08-15 13:40 | 工具链（venv/GDRE/依赖/VC++）就绪 |
| `02-mutageni-baseline` | 2026-08-15 20:10 | 项目迁移 + 5058 验证 + smoke test 完成 |

> 另有一个系统自动 checkpoint（10:21），可忽略或清理。

恢复/回滚命令（提权 PowerShell）：
```powershell
Restore-VMSnapshot -VMName "Mutageni-Dev" -Name "00-clean-os" -Confirm:$false
Get-VMSnapshot -VMName "Mutageni-Dev"   # 查看
Checkpoint-VM -VMName "Mutageni-Dev" -SnapshotName "03-<label>"   # 新建
```

---

## 9. 宿主 ↔ VM 文件交换

- **宿主 → VM**：`Copy-Item -ToSession $s`（见第 3 节）
- **VM → 宿主**（导出 MOD/EXE）：
  ```powershell
  $s = New-PSSession -ComputerName 172.22.30.219 -Credential $cred
  Copy-Item -Path "C:\dev\Mutageni\09_output\*" -Destination "G:\opencode-Mutageni\09_output\" -FromSession $s -Recurse -Force
  ```
- 导出建议目录：宿主 `G:\opencode-Mutageni\09_output\`（已有）或 `G:\VMs\Mutageni-Dev\export\`。

---

## 10. 下一位开发 AI 快速开始

1. 启动 VM：`Start-VM -Name "Mutageni-Dev"`（提权）
2. 确认 guest IP：`Get-VMNetworkAdapter -VMName "Mutageni-Dev"` → IPAddresses
3. 建会话（见第 3 节，IP 若变化用新 IP）
4. 验证工具链：`C:\dev\Mutageni\02_tools\venv\Scripts\python.exe --version`
5. 项目入口：读 `C:\dev\Mutageni\AGENTS1.md`、`C:\dev\Mutageni\10_logs\status.json`
6. 汉化开发：`C:\dev\Mutageni\汉化.md` + `mods/` + `scripts/`

**宿主规则提醒**：
- ❌ 禁止访问宿主 F: 盘（除已删除的 F:\Program Files\qemu 不再涉及）
- ✅ 宿主 `G:\opencode-Mutageni` 只读参考，开发在 VM 内
- ✅ 04_recovered 只允许验证，禁止重建/修改
- ✅ 不擅自宣布 candidate 为正式 baseline（需用户批准）

---

## 11. 已知限制与风险

1. **GPU 渲染受限**：VM 无 GPU 直通，视觉级验证必须在宿主。若未来需要 VM 内流畅游玩，可考虑 GPU-P（需要支持硬件与额外配置，暂不实施）。
2. **VM 内时间时区**：VM 显示 UTC（19:40 vs 宿主 10:40 之类偏移），因手动安装未应用 unattend 的 China Standard Time。可手动修正：`tzutil /s "China Standard Time"`。
3. **steam_api64.dll**：candidate 运行需要同目录 steam_api64.dll（已放置）。项目根也有副本。
4. **10_logs 未全量迁移**：只复制了 status.json 和 P7 candidate 目录。历史构建日志仍在宿主（`G:\opencode-Mutageni\10_logs`，约 17GB），需要时从宿主读取（只读）或按需复制。
5. **VM 网络**：Default Switch NAT，guest 可上网（用于 pip/下载）。IP 可能随 DHCP 变化。

---

## 12. 宿主实际变更清单（本任务）

- ✅ 卸载并删除 QEMU（F:\Program Files\qemu、C:\Users\ZQS\qemu、Downloads 中 qemu/7z 辅助文件）
- ✅ 启动宿主 WinRM 服务 + TrustedHosts 加入 `172.22.30.219`
- ✅ 创建 `G:\VMs\Mutageni-Dev\`（VM 配置、VHDX、ISO）
- ✅ 复制 Windows ISO 与 autounattend 到 VM 目录
- ✅ 创建/验证三个 checkpoint
- ⚠️ 宿主机未安装任何开发工具、未改 PATH、未装 Python 包（符合要求）
- ⚠️ 宿主 F: 盘自 QEMU 删除后未再访问（唯一访问过的 F: 路径是已授权删除的 F:\Program Files\qemu）
- ✅ 宿主 `G:\opencode-Mutageni\04_recovered` 未修改（宿主侧验证 5058/5058 通过于 2026-08-14）

---

*文档维护：docs/dev-environment/README.md（本文件）。后续环境变更请更新此文件并保持证据链。*