param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [int]$ProcessId,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [string]$ExpectedTitle = "Mutagenic"
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$actualSha256 = (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualSha256 -ne $ExpectedSha256.ToUpperInvariant()) {
    throw "Candidate SHA-256 mismatch: expected=$ExpectedSha256 actual=$actualSha256"
}
$process = Get-Process -Id $ProcessId -ErrorAction Stop
$processPath = $process.Path
if ([string]::IsNullOrWhiteSpace($processPath) -or ((Resolve-Path -LiteralPath $processPath).Path -ne $exePath)) {
    throw "PID $ProcessId is not the expected candidate: process_path=$processPath candidate=$exePath"
}
$dllPath = Join-Path (Split-Path -Parent $exePath) "steam_api64.dll"
if (-not (Test-Path -LiteralPath $dllPath -PathType Leaf)) {
    throw "Adjacent steam_api64.dll is missing: $dllPath"
}
$dllSha256 = (Get-FileHash -LiteralPath $dllPath -Algorithm SHA256).Hash.ToUpperInvariant()

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class HumanVisualSnapshotNativeV20 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hwnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hwnd, ref POINT point);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT rect, int size);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
  public static uint OwnerPid(IntPtr hwnd) { uint p; GetWindowThreadProcessId(hwnd,out p); return p; }
}
"@

$hwnd = [HumanVisualSnapshotNativeV20]::Find([uint32]$ProcessId, $ExpectedTitle)
if ($hwnd -eq [IntPtr]::Zero) {
    throw "No visible window titled '$ExpectedTitle' for pid=$ProcessId"
}
$windowRect = New-Object HumanVisualSnapshotNativeV20+RECT
$clientRect = New-Object HumanVisualSnapshotNativeV20+RECT
$dwmRect = New-Object HumanVisualSnapshotNativeV20+RECT
[HumanVisualSnapshotNativeV20]::GetWindowRect($hwnd, [ref]$windowRect) | Out-Null
[HumanVisualSnapshotNativeV20]::GetClientRect($hwnd, [ref]$clientRect) | Out-Null
[HumanVisualSnapshotNativeV20]::DwmGetWindowAttribute($hwnd, 9, [ref]$dwmRect, [Runtime.InteropServices.Marshal]::SizeOf($dwmRect)) | Out-Null
$clientOrigin = New-Object HumanVisualSnapshotNativeV20+POINT
[HumanVisualSnapshotNativeV20]::ClientToScreen($hwnd, [ref]$clientOrigin) | Out-Null
$foreground = [HumanVisualSnapshotNativeV20]::GetForegroundWindow()
$title = New-Object Text.StringBuilder 512
$class = New-Object Text.StringBuilder 512
[HumanVisualSnapshotNativeV20]::GetWindowText($hwnd, $title, $title.Capacity) | Out-Null
[HumanVisualSnapshotNativeV20]::GetClassName($hwnd, $class, $class.Capacity) | Out-Null
$foregroundPid = [HumanVisualSnapshotNativeV20]::OwnerPid($foreground)
$outputPath = [IO.Path]::GetFullPath($Output)
$resultPath = Join-Path (Split-Path -Parent $exePath) "human_visual_result_v17.json"
$record = [ordered]@{
    evidence_id = "C5-L1-human-visual-session-snapshot-v20-20260814"
    session_evidence = "human_visual_session_v16.json"
    candidate = $exePath
    candidate_sha256 = $actualSha256
    adjacent_runtime_dll = $dllPath
    adjacent_runtime_dll_sha256 = $dllSha256
    pid = $ProcessId
    hwnd = $hwnd.ToInt64()
    window_title = $title.ToString()
    class_name = $class.ToString()
    responding = $process.Responding
    visible = [HumanVisualSnapshotNativeV20]::IsWindowVisible($hwnd)
    foreground_hwnd = $foreground.ToInt64()
    foreground_pid = $foregroundPid
    window_rect = "$($windowRect.Right-$windowRect.Left)x$($windowRect.Bottom-$windowRect.Top)+$($windowRect.Left)+$($windowRect.Top)"
    client_rect = "$($clientRect.Right-$clientRect.Left)x$($clientRect.Bottom-$clientRect.Top)+$($clientOrigin.X)+$($clientOrigin.Y)"
    dwm_rect = "$($dwmRect.Right-$dwmRect.Left)x$($dwmRect.Bottom-$dwmRect.Top)+$($dwmRect.Left)+$($dwmRect.Top)"
    visual_result_file_exists = Test-Path -LiteralPath $resultPath
    session_status = "IN_PROGRESS"
    visual_status = "HUMAN_REQUIRED"
    proves = "at snapshot time the SHA-verified candidate window metadata and process ownership were recorded"
    not_proven = "the human-observed StartButton text, glyphs, fallback, clipping, or layout"
    next_action = "record and review human_visual_result_v17.json before changing the localization Gate"
}
[IO.File]::WriteAllText($outputPath, ($record | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $outputPath -Raw -Encoding UTF8
