# Run-ElevatedSilent.ps1
# 以最高权限运行 PowerShell 脚本。策略（自动降级）：
#   1) 首选：一次性计划任务提权 —— 无 UAC、无窗口（任务计划程序直接以当前用户的提升令牌启动，不经过 consent.exe）
#   2) 回退：若本机策略禁止非提权进程注册 RunLevel=Highest 任务（拒绝访问 0x80070005），
#      自动改用 Start-Process -Verb RunAs -WindowStyle Minimized —— 会弹一次 UAC 确认框，
#      但提权窗口最小化到任务栏、不抢前台（输出仍写日志）。
#  输出重定向到日志文件（默认：脚本所在目录\<脚本名>.elev.log），任务条目用后自动清理。
#
# 用法：
#   & '.\Run-ElevatedSilent.ps1' -File 'G:\VMs\Mutageni-Dev\a1_step2.ps1'
#   & '.\Run-ElevatedSilent.ps1' -File 'x.ps1' -ArgumentList 'a','b' -LogFile 'G:\VMs\out.log' -NoWait
#
# 限制：只提升目标脚本进程本身；脚本内再 `Start-Process` 的子进程不会自动继承最高权限。

param(
    [Parameter(Mandatory = $true)][string]$File,
    [string[]]$ArgumentList = @(),
    [string]$LogFile = "",
    [switch]$NoWait,
    [int]$TimeoutSec = 3600
)

$ErrorActionPreference = "Stop"

# ---------- 校验 ----------
if (-not (Test-Path -LiteralPath $File -PathType Leaf)) {
    throw "脚本不存在: $File"
}
$resolvedFile = (Resolve-Path -LiteralPath $File).Path
$scriptDir = Split-Path -Parent $resolvedFile

if (-not $LogFile) {
    $LogFile = Join-Path $scriptDir (((Get-Item -LiteralPath $resolvedFile).BaseName) + ".elev.log")
}

# ---------- 构造被提升的命令 ----------
# 必须用 -Command 以便支持 *> 重定向（-File 会把重定向当成脚本参数传给脚本）
$innerArgs = ($ArgumentList | ForEach-Object { "'" + ($_ -replace "'", "''") + "'" }) -join " "
$inner = "& '$resolvedFile' $innerArgs *> '$LogFile'"

$elevatedNow = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "[elev] 目标脚本: $resolvedFile"
Write-Host "[elev] 日志: $LogFile"

$taskName = $null
$usedTask = $false
$code = 0

# ---------- 路线 1：计划任务静默提权（无 UAC、无窗口） ----------
try {
    $cmdline = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command `"$inner`""
    $taskName = "opencode-silent-elev-" + [guid]::NewGuid().ToString("N").Substring(0, 8)
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $cmdline -WorkingDirectory $scriptDir
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(1)
    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Seconds $TimeoutSec) `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal `
        -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -LogonType Interactive `
        -RunLevel Highest

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    $usedTask = $true
    Start-ScheduledTask -TaskName $taskName
    Write-Host "[elev] 静默提权任务已启动: $taskName"

    if ($NoWait) {
        Start-Sleep -Seconds 5   # 给触发器时间确保任务已触发，随后 finally 清理任务条目（进程不受影响）
        Write-Host "[elev] 已转入后台运行"
        return
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $done = $false
    do {
        Start-Sleep -Seconds 2
        $info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
        if (-not $info) { break }
        $done = $info.LastTaskResult -ne 267009 -and $info.LastTaskResult -ne 267010
    } while (-not $done -and (Get-Date) -lt $deadline)

    if (-not $done) {
        throw "等待静默提权任务超时 (${TimeoutSec}s)，日志: $LogFile"
    }
    $code = $info.LastTaskResult
    Write-Host "[elev] 执行完成，退出码: $code（0=成功）"
}
catch {
    # 仅当任务尚未注册成功时考虑回退；任务已启动后的错误（超时/Start 失败）是真错误，上抛
    if ($usedTask) { throw }

    $permDenied = ($_.FullyQualifiedErrorId -match 'PermissionDenied') `
        -or ($_.Exception.Message -match '80070005') `
        -or ($_.CategoryInfo.Category -eq 'PermissionDenied')

    if (-not $permDenied) { throw }

    Write-Warning "[elev] 本机禁止非提权进程注册提权计划任务（拒绝访问 0x80070005）"
    Write-Warning "[elev] 回退到最小化提权：将弹出一次 UAC 确认框（请点[是]），提权窗口最小化到任务栏不抢前台"

    # ---------- 路线 2：最小化 RunAs（会弹一次 UAC） ----------
    $runAsArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-Command', $inner)
    $p = Start-Process -FilePath "powershell.exe" -Verb RunAs -WindowStyle Minimized -PassThru -ArgumentList $runAsArgs
    if ($NoWait) {
        Write-Host "[elev] 已后台启动（未等待）"
        return
    }
    $p.WaitForExit()
    $code = $p.ExitCode
    Write-Host "[elev] 执行完成，退出码: $code（0=成功）"
}
finally {
    if ($usedTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
}

if ($code -ne 0) {
    Write-Warning "[elev] 脚本返回非零退出码，请查看日志: $LogFile"
}
exit $code
