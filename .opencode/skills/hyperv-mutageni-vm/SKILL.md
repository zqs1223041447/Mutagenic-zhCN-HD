---
name: hyperv-mutageni-vm
description: 操作 Mutageni-Dev 这台 Hyper-V 隔离 Windows 开发 VM。Use when 需要远程执行命令/运行构建/传文件/打 checkpoint/回滚/检查 guest 状态 in the Mutageni-Dev VM。触发词：虚拟机、VM、Hyper-V、Mutageni-Dev、guest、WinRM、PowerShell Direct、checkpoint、快照、回滚、远程执行、Copy-VMFile。
---

# Mutageni-Dev Hyper-V 开发 VM 操作手册

本 skill 是操作 `Mutageni-Dev`（宿主机 `DESKTOP-FBRTNR7` 上的 Hyper-V Gen2 Windows VM）的唯一权威操作方式，基于微软官方文档与参考实现（MSLab）整理，用于指导 AI 在宿主侧自动化管理这台开发 VM。

## 环境事实（勿凭记忆假设）

| 项 | 值 |
|---|---|
| VM 名称 | `Mutageni-Dev`（Gen2/UEFI，4 vCPU，动态内存 4-16GB） |
| guest OS | Windows 10 Enterprise Evaluation 22H2 (19045) |
| VHDX | `G:\VMs\Mutageni-Dev\Virtual Hard Disks\Mutageni-Dev.vhdx` (120GB) |
| 网络 | Default Switch (NAT)，guest IP `172.22.30.219`（DHCP 可能变化，勿硬依赖） |
| guest 可用账户 | **`dev` / `REDACTED`**（Administrators）← 唯一远程可用账户 |
| guest 不可用账户 | `ZZZ`（本地无密码 → WinRM 无法登录，官方约束） |
| 项目工作区 | guest 内 `C:\dev\Mutageni`（宿主 `G:\opencode-Mutageni` 只读参考） |
| 工具链 | venv `C:\dev\Mutageni\02_tools\venv\Scripts\python.exe` (3.11.15)、GDRE 2.6.4、VC++ redist 已装 |
| 既有 checkpoint | `00-clean-os`、`01-dev-toolchain`、`02-mutageni-baseline` |
| 渲染 | **Mesa LLVMpipe 软渲染已生效**：游戏目录放 `opengl32.dll`+`libgallium_wgl.dll`（源 `G:\VMs\Mutageni-Dev\mesa\x64\`），Godot 日志 `Renderer: llvmpipe`，游戏可在 VM 桌面正常显示（几 FPS，够开发验证）。**无 GPU 直通；视觉/游玩最终验证仍建议宿主机** |
| MOD 开发 | **NL2MOD 框架**（`scripts/nlmod/`）：自然语言→intent→mod.json→一键构建→候选 EXE→部署 VM 验证。指南 `docs/ai/nl2mod-guide.md`，规则 `docs/dev-environment/VM_DEVELOPMENT.md` |
| VM 内 GUI 启动 | 用计划任务 `/ru zzz /it`（zzz 在 console 交互会话），远程会话无法拉起可见窗口 |

**两条硬规则**：
1. 远程命令一律显式传 `-Credential`（dev 账户）。`New-PSSession -VMName` 忘传凭证可能触发 guest 内 `vmicvmsession` 服务崩溃（微软已知 bug）。
2. 回滚/删除类操作一律加 `-Confirm:$false`，否则确认框会挂死自动化。

**关键安全不变量**（与 VM_DEVELOPMENT.md §7 一致，必须遵守）：
- 禁止访问宿主 F: 盘；`00_original`/`03_raw`/`04_recovered` 不可变（只读输入）
- 每次从 00_original 新鲜嵌入，不在历史 modded EXE 上叠加
- 候选不自动晋升 baseline（需用户批准）；破坏性操作前先打 checkpoint

## 1. 建立远程会话（首选 PowerShell Direct）

PowerShell Direct（`-VMName`）不依赖 IP/网络/WinRM，只要 VM 在本机运行即可用，是 AI 自动化的首选；WinRM（`-ComputerName`）作为备选。

```powershell
# 首选：PowerShell Direct（VM 在本机即可，与 IP 无关）
$cred = New-Object PSCredential('dev', (ConvertTo-SecureString 'REDACTED' -AsPlainText -Force))
$s = New-PSSession -VMName "Mutageni-Dev" -Credential $cred   # 注意：-VMName 参数集，不是 -ComputerName
Invoke-Command -Session $s -ScriptBlock { hostname; whoami }
Copy-Item -Path "G:\opencode-Mutageni\scripts\build_pack.py" -Destination "C:\dev\Mutageni\scripts\" -ToSession $s -Force
Remove-PSSession $s

# 即用即弃（单命令，推荐小任务）
Invoke-Command -VMName "Mutageni-Dev" -Credential $cred -ScriptBlock { python --version }

# 备选：WinRM over IP（仅当 PowerShell Direct 连不上但网络通时）
$s2 = New-PSSession -ComputerName "172.22.30.219" -Credential $cred   # 需宿主 TrustedHosts 含该 IP（已配置）
```

**PowerShell Direct 前置条件**：VM 本机运行 + guest 至少配置过一个用户配置（`dev` ✓）+ 宿主以 Hyper-V 管理员运行 + 显式 guest 凭证。

## 2. 判断 guest 真正可用（三步，勿只看 State）

`State=Running` 只代表电源状态，不代表 guest OS 就绪。固定使用三段式：

```powershell
$vm = Get-VM -Name "Mutageni-Dev"
if ($vm.State -ne "Running") { Start-VM -Name "Mutageni-Dev" }

# 轮询到 Running + Heartbeat OK
while (($vm = Get-VM -Name "Mutageni-Dev").State -ne "Running" -or
       ($vm | Get-VMIntegrationService -Name Heartbeat).PrimaryStatusDescription -ne "OK") {
    Start-Sleep -Seconds 5
}

# 最强信号：guest 内实际执行一条命令探测成功才算就绪
$ok = $false
while (-not $ok) {
    $ok = Invoke-Command -VMName "Mutageni-Dev" -Credential $cred -ScriptBlock { $true } -ErrorAction SilentlyContinue
    if (-not $ok) { Start-Sleep -Seconds 5 }
}
```

常用状态查询：
```powershell
Get-VM -Name "Mutageni-Dev" | Select-Object Name,State,CPUUsage,Uptime,CheckpointType
Get-VMIntegrationService -VMName "Mutageni-Dev" | Select-Object Name,Enabled,PrimaryStatusDescription
(Get-VMNetworkAdapter -VMName "Mutageni-Dev").IPAddresses   # guest 启动后才有 IP
```

## 3. 文件传输

| 方向 | 推荐方式 | 说明 |
|---|---|---|
| 宿主 → guest | `Copy-VMFile` | 免建会话/免凭证，单条命令最稳；**需先启用 Guest Service Interface** |
| 双向 / 复用身份 | `Copy-Item -ToSession / -FromSession` | 复用已建 PSSession；`-FromSession` 是 guest→宿主**唯一**方式 |

```powershell
# 一次性启用 Guest Service Interface（默认关闭，只做一次）
Enable-VMIntegrationService -VMName "Mutageni-Dev" -Name "Guest Service Interface"

# 宿主 → guest（免凭证）
Copy-VMFile -VMName "Mutageni-Dev" -SourcePath "G:\opencode-Mutageni\09_output\foo.pck" `
            -DestinationPath "C:\dev\Mutageni\09_output\foo.pck" -CreateFullPath -Force

# guest → 宿主（只有 Copy-Item -FromSession 能做）
$s = New-PSSession -VMName "Mutageni-Dev" -Credential $cred
Copy-Item -Path "C:\dev\Mutageni\09_output\foo.pck" -Destination "G:\VMs\Mutageni-Dev\export\" -FromSession $s -Force
Remove-PSSession $s
```

> 拷贝到 `C:\Windows\System32` / `C:\Program Files` 等系统目录可能有权限问题（社区已知），先拷临时目录再移动。

## 4. VM 生命周期与 Checkpoint

### 启停
```powershell
Start-VM -Name "Mutageni-Dev"                    # 启动后必须做第 2 节就绪检查
Stop-VM -Name "Mutageni-Dev"                     # 受控关机（guest 关机，默认）
Stop-VM -Name "Mutageni-Dev" -TurnOff            # 兜底拔电源（可能丢未保存数据，仅卡死时用）
```

### Checkpoint 最佳实践
- 保持默认 `Production` 类型（VSS 数据一致；回滚后 VM 处于 **Off**，需手动 Start-VM）。
- **关闭自动 checkpoint**（避免 AI 每次重启 VM 产生无意义快照链）：
  ```powershell
  Set-VM -Name "Mutageni-Dev" -AutomaticCheckpointsEnabled $false
  ```
- **每次有风险操作前打 checkpoint**，名称可回查：`before-feature-x`。
- 维护**浅链**：完成任务后删除不需要的中间 checkpoint（删除会自动合并差异盘，**绝不要手动删 .avhdx**）。

```powershell
# 创建
Checkpoint-VM -VMName "Mutageni-Dev" -SnapshotName "before-c5-l21" -Confirm:$false

# 回滚（标准流程：先留逃生线 → 回滚 → 等 Off → 启动 → 健康检查）
Checkpoint-VM -VMName "Mutageni-Dev" -SnapshotName "before-rollback" -Confirm:$false
Restore-VMSnapshot -VMName "Mutageni-Dev" -Name "02-mutageni-baseline" -Confirm:$false
while ((Get-VM -Name "Mutageni-Dev").State -ne "Off") { Start-Sleep -Seconds 3 }
Start-VM -Name "Mutageni-Dev"
# …然后执行第 2 节就绪检查

# 查看 / 删除
Get-VMSnapshot -VMName "Mutageni-Dev" -Tree
Get-VMSnapshot -VMName "Mutageni-Dev" -Name "old-cp" | Remove-VMSnapshot -Confirm:$false
```

## 5. 在 guest 内执行命令 / 启动进程

```powershell
$s = New-PSSession -VMName "Mutageni-Dev" -Credential $cred

# 执行构建 / 脚本（项目工具链）
Invoke-Command -Session $s -ScriptBlock {
    & 'C:\dev\Mutageni\02_tools\venv\Scripts\python.exe' 'C:\dev\Mutageni\scripts\build_pack.py' 2>&1 | Out-String
    "exit: $LASTEXITCODE"
}

# 启动后台进程（构建/测试/daemon）—— 立即返回，勿前台等待；输出重定向到文件防缓冲阻塞
Invoke-Command -Session $s -ScriptBlock {
    Start-Process -FilePath 'C:\dev\Mutageni\02_tools\venv\Scripts\python.exe' `
                  -ArgumentList 'scripts\probe_boot.py','C:\dev\Mutageni\10_logs\P7-fix-persistence-20260814\runtime_candidate\Mutagenic.exe' `
                  -RedirectStandardOutput 'C:\dev\Mutageni\10_logs\smoke.log' -WindowStyle Hidden
}

# 查看 guest 日志 / 服务
Invoke-Command -Session $s -ScriptBlock { Get-WinEvent -LogName Application -MaxEvents 20 | Select-Object TimeCreated,Message }
Remove-PSSession $s
```

**已知限制（官方明确）**：远程会话**无法拉起 guest 可见的 GUI 窗口**——进程会启动但界面不显示，且前台命令不返回。需要可见桌面的交互步骤（如游戏视觉验证）只能在 VM 控制台（VMConnect）由用户操作，或使用计划任务交互式令牌。**runtime 视觉/游玩验证一律在宿主机执行**。

## 6. AI 自动化铁律（防挂起清单）

1. **永远显式 `-Credential`**（dev 账户），禁止空密码账户（ZZZ）远程。
2. **`-Confirm:$false`** 加在 Checkpoint/Restore/Remove 类命令上。
3. 脚本内**禁用** `Enter-PSSession`（交互式会挂死）；用 `Invoke-Command -VMName` 一次性调用。
4. 长任务：guest 内输出重定向到文件（`Out-File` / `-RedirectStandardOutput`），避免管道缓冲填满挂起；宿主侧大任务可 `-AsJob`。
5. 等待就绪用**轮询/`Wait-VM`**，不要裸 `Start-Sleep` 猜时长。
6. 关键步骤 `-ErrorAction Stop` + try/catch，失败日志落盘到 `G:\VMs\Mutageni-Dev\`。
7. **`-RunAsAdministrator` 不适用于 VM 连接**（那是容器参数集），凭证必须显式传。
8. 口令**不写进项目文档/脚本明文入库**；需要落盘用 `Export-Clixml`（DPAPI，仅本机本用户可解）或宿主侧环境变量/凭据管理器。
9. **宿主侧需要管理员权限的脚本（Hyper-V 模块等）一律最小化提权**：禁止裸 `Start-Process powershell -Verb RunAs`——它会弹 UAC 全屏安全桌面 + 置顶一个"管理员: Windows PowerShell"窗口，阻塞用户其他操作。必须提权时用 `-WindowStyle Minimized`（UAC 确认框是 Windows 安全设计无法后台化，但提权窗口最小化到任务栏、不抢前台）：
   ```powershell
   Start-Process powershell -Verb RunAs -WindowStyle Minimized -Wait `
     -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','G:\VMs\Mutageni-Dev\a1_step2.ps1'
   ```
   需要看进度就把脚本输出重定向到文件（脚本内 `Add-Content`/`Out-File`），不用打开最小化窗口。

## 7. 常见故障排查

| 症状 | 原因与处置 |
|---|---|
| `New-PSSession -VMName` 报 "credential is invalid" | 凭证错误，或 guest 无已配置用户配置（应存在 dev）；确认 `dev/REDACTED` |
| 报 "A remote session might have ended" | VM 未运行 / guest 还在启动 / 引导需人工输入 → 先做第 2 节就绪检查 |
| guest 内 `vmicvmsession` 服务崩溃 | 历史 bug：`New-PSSession -VMName` 未传凭证导致 → 进 guest `Restart-Service -Name vmicvmsession`，并始终显式 `-Credential` |
| WinRM 连不上 / 认证失败 | guest 需已 `Enable-PSRemoting` + 宿主 TrustedHosts 含该 IP + 显式 `-Credential`；ZZZ 无密码账户不能用 |
| `Copy-VMFile` 失败 "no suitable virtual switch / Guest Service Interface" | 未启用 Guest Service Interface → 执行第 3 节 `Enable-VMIntegrationService` |
| 游戏进程启动但无窗口 / probe_boot FAIL | **预期行为**：VM 无 GPU 直通。视觉验证移宿主，VM 内只看进程存活+无 ALERT+无 fatal |
| 回滚后 VM 是 Off | Production checkpoint 不含内存状态，回滚后需手动 `Start-VM`（见第 4 节） |

## 8. 快速参考（复制即用）

```powershell
$cred = New-Object PSCredential('dev', (ConvertTo-SecureString 'REDACTED' -AsPlainText -Force))
$s    = New-PSSession -VMName "Mutageni-Dev" -Credential $cred
Invoke-Command -Session $s -ScriptBlock {
    & 'C:\dev\Mutageni\02_tools\venv\Scripts\python.exe' --version
    (Get-CimInstance Win32_OperatingSystem).Caption
}
Remove-PSSession $s
```

宿主侧提权执行模板（最小化，不抢前台）：
```powershell
Start-Process powershell -Verb RunAs -WindowStyle Minimized -Wait `
  -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','G:\VMs\Mutageni-Dev\<脚本>.ps1'
```

---

*依据：Microsoft Learn — PowerShell Direct、Copy-VMFile、Checkpoint-VM/Restore-VMSnapshot/Get-VM/Get-VMIntegrationService/Set-VM、Hyper-V checkpoints、Manage Hyper-V Integration Services、about_Remote_Troubleshooting、PowerShell Remoting FAQ；参考实现 microsoft/MSLab。环境事实核对于 2026-08-15。*