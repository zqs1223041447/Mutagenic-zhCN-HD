param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [int]$Seconds = 5,
    [string]$ExpectedTitle = "Mutagenic"
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$outputPath = [IO.Path]::GetFullPath($Output)
$workDir = Split-Path -Parent $exePath
$dllPath = Join-Path $workDir "steam_api64.dll"
$actualExeSha256 = (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualExeSha256 -ne $ExpectedSha256.ToUpperInvariant()) {
    throw "Candidate SHA-256 mismatch: expected=$ExpectedSha256 actual=$actualExeSha256"
}
if (-not (Test-Path -LiteralPath $dllPath -PathType Leaf)) {
    throw "Adjacent steam_api64.dll is missing: $dllPath"
}
$dllSha256 = (Get-FileHash -LiteralPath $dllPath -Algorithm SHA256).Hash.ToUpperInvariant()

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class HumanVisualLaunchNativeV16 {
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory $workDir -PassThru
$hwnd = [IntPtr]::Zero
try {
    Start-Sleep -Seconds $Seconds
    for ($i = 0; $i -lt 20 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [HumanVisualLaunchNativeV16]::Find([uint32]$proc.Id, $ExpectedTitle)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "No visible window titled '$ExpectedTitle' for pid=$($proc.Id)" }
    [HumanVisualLaunchNativeV16]::ShowWindow($hwnd, 9) | Out-Null
    [HumanVisualLaunchNativeV16]::BringWindowToTop($hwnd) | Out-Null
    [HumanVisualLaunchNativeV16]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    $live = Get-Process -Id $proc.Id -ErrorAction Stop
    $result = [pscustomobject]@{
        evidence_id = "C5-L1-human-visual-session-v16-20260814"
        candidate = $exePath
        candidate_sha256 = $actualExeSha256
        adjacent_runtime_dll = $dllPath
        adjacent_runtime_dll_sha256 = $dllSha256
        working_directory = $workDir
        pid = $proc.Id
        hwnd = $hwnd.ToInt64()
        window_title = $ExpectedTitle
        responding = $live.Responding
        launch_status = "PASS"
        visual_status = "HUMAN_REQUIRED"
        session_status = "IN_PROGRESS"
        process_left_running = $true
        proves = "the exact candidate passed its hash check, launched with the adjacent DLL, and produced a responding visible Mutagenic window brought to the foreground"
        not_proven = "the StartButton text, Chinese glyph rendering, fallback, clipping, layout, gameplay, persistence, or release readiness"
        next_action = "human observation and checklist result are required before changing the localization Gate"
    }
    $json = $result | ConvertTo-Json -Depth 5
    [IO.File]::WriteAllText($outputPath, $json, [Text.UTF8Encoding]::new($false))
    $json
} catch {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; $proc.WaitForExit() }
    throw
}
