# bootstrap.ps1 - 鲁棒的 bootstrap 入口，不再依赖裸 python 导致 9009 静默退出
# 优先级: python -> python3 -> python3.11 -> py -3.11 -> uv run -> 绝对路径
param([switch]$CheckOnly,[string]$JsonOut,[switch]$Verbose)
$ErrorActionPreference="Continue"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if(!$repoRoot -or !(Test-Path "$repoRoot\AGENTS.md")){ $repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName }
if(!(Test-Path "$repoRoot\AGENTS.md")){ Write-Host "[bootstrap-wrapper] FAIL: cannot resolve repo root from script location (no AGENTS.md)"; exit 2 }
# 确保 MUTAGENIC_DEVKIT_ROOT 可见
if(!$env:MUTAGENIC_DEVKIT_ROOT){ $env:MUTAGENIC_DEVKIT_ROOT = [Environment]::GetEnvironmentVariable("MUTAGENIC_DEVKIT_ROOT","User"); if($env:MUTAGENIC_DEVKIT_ROOT){ Write-Host "[bootstrap-wrapper] 注入 MUTAGENIC_DEVKIT_ROOT=$env:MUTAGENIC_DEVKIT_ROOT (来自注册表)" } }
# 自愈 shim
try{ & "$HOME\.local\bin\repair_python_shim.ps1" | Out-Null } catch {}
function Find-Python {
  $cands = @(
    "$HOME\.local\bin\python.exe",
    "$HOME\.local\bin\python3.exe",
    "$HOME\.local\bin\python3.11.exe",
    "$HOME\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe"
  )
  foreach($p in $cands){ if(Test-Path $p){ try{ $v=& $p --version 2>&1; if($LASTEXITCODE -eq 0 -and $v -match "Python 3\.11"){ return $p } } catch {} } }
  foreach($cmd in @("python","python3","python3.11","py")){
    try{ $found=Get-Command $cmd -ErrorAction SilentlyContinue; if($found){ $p=$found.Source; $v=& $p --version 2>&1; if($LASTEXITCODE -eq 0 -and $v -notmatch "Store" -and $v -match "Python"){ # 过滤 0字节假启动器：Length=0 会导致 where 失败但 Get-Command 仍可能返回
        if(Test-Path $p){ $len=(Get-Item $p -Force -ErrorAction SilentlyContinue).Length; if($len -eq 0){ continue } }
        return $p
      } } } catch {}
  }
  # py launcher
  try{ $v=py -3.11 --version 2>&1; if($LASTEXITCODE -eq 0){ return "py -3.11" } } catch {}
  # uv run
  try{ $uv=Get-Command uv -ErrorAction SilentlyContinue; if($uv){ return "uv run --python 3.11 python" } } catch {}
  return $null
}
$py = Find-Python
if(!$py){ Write-Host "[bootstrap-wrapper] FAIL: 找不到可用 Python 3.11" -ForegroundColor Red; Write-Host "  已尝试: .local\bin\python.exe, python3, python3.11, py -3.11, uv run"; Write-Host "  当前 where python:"; cmd /c where python 2>&1 | Write-Host; Write-Host "  请运行: uv python install 3.11; & `"$HOME\.local\bin\repair_python_shim.ps1`""; exit 9009 }
Write-Host "[bootstrap-wrapper] 使用 Python: $py" -ForegroundColor Cyan
if($py -like "py *"){ $pyCmd = $py } elseif($py -like "uv *"){ $pyCmd = $py } else { $pyCmd = "`"$py`"" }
$script = Join-Path $repoRoot "scripts\bootstrap\bootstrap_dev_env.py"
$args = @()
if($CheckOnly){ $args += "--check-only" }
if($Verbose){ $args += "--verbose" }
if($JsonOut){ $args += "--json"; $args += $JsonOut }
Write-Host "[bootstrap-wrapper] 执行: $pyCmd $script $($args -join ' ')"
if($py -eq "py -3.11"){ & py -3.11 $script @args; $code=$LASTEXITCODE }
elseif($py -like "uv *"){ & uv run --python 3.11 python $script @args; $code=$LASTEXITCODE }
else { & $py $script @args; $code=$LASTEXITCODE }
if($code -eq 9009){ Write-Host "[bootstrap-wrapper] FAIL 9009: Python 启动器仍指向 Windows Store 假启动器，请检查 PATH 顺序和 repair脚本" -ForegroundColor Red }
exit $code
