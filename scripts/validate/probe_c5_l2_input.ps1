param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [int]$StartupSeconds = 5,
    [int]$AfterEnterMilliseconds = 2500,
    [int]$AfterEscapeMilliseconds = 1500,
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
using System.Threading;
using System.Runtime.InteropServices;
public static class C5L2InputProbeNativeV1 {
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern void keybd_event(byte key, byte scan, uint flags, UIntPtr extra);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
  public static void Tap(byte key) {
    keybd_event(key, 0, 0, UIntPtr.Zero);
    Thread.Sleep(80);
    keybd_event(key, 0, 2, UIntPtr.Zero);
  }
}
"@

$logDir = Join-Path $env:APPDATA "Godot\app_userdata\Mutagenic\logs"
$startedAt = Get-Date
$beforeLogs = @()
if (Test-Path -LiteralPath $logDir) {
    $beforeLogs = @(Get-ChildItem -LiteralPath $logDir -Filter "godot*.log" -File | Select-Object -ExpandProperty FullName)
}
$proc = Start-Process -FilePath $exePath -WorkingDirectory $workDir -PassThru
$hwnd = [IntPtr]::Zero
$enterSent = $false
$escapeSent = $false
try {
    Start-Sleep -Seconds $StartupSeconds
    for ($i = 0; $i -lt 20 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [C5L2InputProbeNativeV1]::Find([uint32]$proc.Id, $ExpectedTitle)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "No visible window titled '$ExpectedTitle' for pid=$($proc.Id)" }
    [C5L2InputProbeNativeV1]::BringWindowToTop($hwnd) | Out-Null
    [C5L2InputProbeNativeV1]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 300

    [C5L2InputProbeNativeV1]::Tap(0x0D)
    $enterSent = $true
    Start-Sleep -Milliseconds $AfterEnterMilliseconds
    $afterEnter = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    $gameWindowAfterEnter = [C5L2InputProbeNativeV1]::Find([uint32]$proc.Id, $ExpectedTitle)
    $alertWindowAfterEnter = [C5L2InputProbeNativeV1]::Find([uint32]$proc.Id, "ALERT!")

    if ($afterEnter -and $gameWindowAfterEnter -ne [IntPtr]::Zero) {
        [C5L2InputProbeNativeV1]::Tap(0x1B)
        $escapeSent = $true
        Start-Sleep -Milliseconds $AfterEscapeMilliseconds
    }
    $afterEscape = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    $gameWindowAfterEscape = if ($afterEscape) { [C5L2InputProbeNativeV1]::Find([uint32]$proc.Id, $ExpectedTitle) } else { [IntPtr]::Zero }
    $alertWindowAfterEscape = if ($afterEscape) { [C5L2InputProbeNativeV1]::Find([uint32]$proc.Id, "ALERT!") } else { [IntPtr]::Zero }

    # Capture process/window state first, then release the candidate's log
    # handle before hashing newly written Godot logs. The previous order could
    # fail on a locked shared godot.log.
    $processStoppedBeforeLogCapture = $false
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
        $processStoppedBeforeLogCapture = $true
        Start-Sleep -Milliseconds 200
    }

    $newLogs = @()
    if (Test-Path -LiteralPath $logDir) {
        $newLogs = @(Get-ChildItem -LiteralPath $logDir -Filter "godot*.log" -File | Where-Object { $_.LastWriteTime -ge $startedAt.AddSeconds(-1) } | Sort-Object LastWriteTime)
    }
    $logEvidence = @()
    foreach ($log in $newLogs) {
        $content = Get-Content -LiteralPath $log.FullName -Raw -ErrorAction SilentlyContinue
        $logEvidence += [ordered]@{
            path = $log.FullName
            sha256 = (Get-FileHash -LiteralPath $log.FullName -Algorithm SHA256).Hash.ToUpperInvariant()
            line_count = @($content -split "`r?`n").Count
            fatal_markers = @($content -split "`r?`n" | Where-Object { $_ -match "ALERT!|Couldn't load project|FATAL|SCRIPT ERROR|Segmentation fault" })
            transition_related_lines = @($content -split "`r?`n" | Where-Object { $_ -match "CharacterSelect|CharacterSlot|PopupManager|Node not found|ViewportTexture" })
        }
    }
    $fatalCount = @($logEvidence | ForEach-Object { $_.fatal_markers }).Count
    $result = [ordered]@{
        evidence_id = "C5-L2-input-probe-v1-20260814"
        recorded_at = (Get-Date -Format o)
        candidate = $exePath
        candidate_sha256 = $actualExeSha256
        adjacent_runtime_dll = $dllPath
        adjacent_runtime_dll_sha256 = $dllSha256
        working_directory = $workDir
        pid = $proc.Id
        startup_window_title = $ExpectedTitle
        startup_window_found = ($hwnd -ne [IntPtr]::Zero)
        enter_sent = $enterSent
        after_enter_process_alive = ($null -ne $afterEnter)
        after_enter_game_window_found = ($gameWindowAfterEnter -ne [IntPtr]::Zero)
        after_enter_alert_window_found = ($alertWindowAfterEnter -ne [IntPtr]::Zero)
        escape_sent = $escapeSent
        after_escape_process_alive = ($null -ne $afterEscape)
        after_escape_game_window_found = ($gameWindowAfterEscape -ne [IntPtr]::Zero)
        after_escape_alert_window_found = ($alertWindowAfterEscape -ne [IntPtr]::Zero)
        process_stopped_before_log_capture = $processStoppedBeforeLogCapture
        logs = $logEvidence
        fatal_marker_count = $fatalCount
        status = if (($null -ne $afterEnter) -and ($gameWindowAfterEnter -ne [IntPtr]::Zero) -and ($alertWindowAfterEnter -eq [IntPtr]::Zero) -and ($fatalCount -eq 0)) { "HUMAN_REQUIRED" } else { "FAIL" }
        proves = "the exact candidate passed its SHA/DLL checks, accepted a foreground Enter key event, and remained observable without an ALERT or captured fatal marker during the short probe"
        not_proven = "that Enter activated StartButton, that CharacterSelect was displayed, any translated label rendering, visual quality, close behavior, gameplay, persistence, or release readiness"
        next_action = "use the SHA-guarded human checklist; do not upgrade the C5-L2 Gate from this input probe alone"
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
    [IO.File]::WriteAllText($outputPath, ($result | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
    Get-Content -LiteralPath $outputPath -Raw -Encoding UTF8
} finally {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; $proc.WaitForExit() }
}
