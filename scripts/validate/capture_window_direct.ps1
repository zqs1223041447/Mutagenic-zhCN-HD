param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [int]$Seconds = 8,
    [string]$ExpectedTitle = "Mutagenic"
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$outputPath = [IO.Path]::GetFullPath($Output)
$outputDir = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class DirectWindowCapture {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);
    public static IntPtr FindByPidAndTitle(uint wantedPid, string wantedTitle) {
        IntPtr found = IntPtr.Zero;
        EnumWindows((hwnd, lParam) => {
            uint pid;
            GetWindowThreadProcessId(hwnd, out pid);
            var text = new StringBuilder(512);
            GetWindowText(hwnd, text, text.Capacity);
            if (pid == wantedPid && IsWindowVisible(hwnd) &&
                string.Equals(text.ToString(), wantedTitle, StringComparison.OrdinalIgnoreCase)) {
                found = hwnd;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
try {
    Start-Sleep -Seconds $Seconds
    $hwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 10 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [DirectWindowCapture]::FindByPidAndTitle([uint32]$proc.Id, $ExpectedTitle)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) {
        throw "No visible window titled '$ExpectedTitle' found for pid=$($proc.Id)"
    }
    [DirectWindowCapture]::ShowWindow($hwnd, 9) | Out-Null
    [DirectWindowCapture]::BringWindowToTop($hwnd) | Out-Null
    [DirectWindowCapture]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500

    $rect = New-Object DirectWindowCapture+RECT
    if (-not [DirectWindowCapture]::GetWindowRect($hwnd, [ref]$rect)) {
        throw "GetWindowRect failed for hwnd=$hwnd"
    }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { throw "Invalid window bounds: $($width)x$($height)" }

    $bitmap = New-Object Drawing.Bitmap($width, $height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $hdc = $graphics.GetHdc()
    try {
        $printed = [DirectWindowCapture]::PrintWindow($hwnd, $hdc, 2)
    } finally {
        $graphics.ReleaseHdc($hdc)
        $graphics.Dispose()
    }
    if (-not $printed) {
        $bitmap.Dispose()
        throw "PrintWindow failed for hwnd=$hwnd"
    }
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose()
    [pscustomobject]@{
        exe = $exePath
        pid = $proc.Id
        hwnd = $hwnd.ToInt64()
        expected_title = $ExpectedTitle
        bounds = "$($width)x$($height)+$($rect.Left)+$($rect.Top)"
        screenshot = $outputPath
        seconds = $Seconds
        capture_method = "PrintWindow(hwnd)"
        verdict = "PASS"
        proves = "the screenshot was rendered from the target process window handle with an exact title match"
        not_proven = "gameplay semantics, persistence, and visual interpretation beyond the captured frame"
    } | ConvertTo-Json -Compress
}
finally {
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
    }
}
