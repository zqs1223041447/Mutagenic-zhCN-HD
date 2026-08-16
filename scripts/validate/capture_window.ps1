param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [int]$Seconds = 8
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$outputPath = [IO.Path]::GetFullPath($Output)
$outputDir = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class WindowCaptureNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
try {
    Start-Sleep -Seconds $Seconds
    $live = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($null -eq $live -or $live.MainWindowHandle -eq 0) {
        throw "Candidate process has no visible main window: pid=$($proc.Id)"
    }
    [WindowCaptureNative]::SetForegroundWindow($live.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 500
    $rect = New-Object WindowCaptureNative+RECT
    if (-not [WindowCaptureNative]::GetWindowRect($live.MainWindowHandle, [ref]$rect)) {
        throw "GetWindowRect failed for pid=$($proc.Id)"
    }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) {
        throw "Invalid window bounds: $($width)x$($height)"
    }
    $bitmap = New-Object Drawing.Bitmap($width, $height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    [pscustomobject]@{
        exe = $exePath
        pid = $proc.Id
        window_title = $live.MainWindowTitle
        bounds = "$($width)x$($height)+$($rect.Left)+$($rect.Top)"
        screenshot = $outputPath
        seconds = $Seconds
        verdict = "PASS"
        proves = "the candidate displayed a visible window that was captured"
        not_proven = "gameplay semantics, persistence, and screenshot interpretation beyond the visible frame"
    } | ConvertTo-Json -Compress
}
finally {
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
    }
}
