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
Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class DpiAwareWindowCapture {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hwnd, IntPtr insertAfter, int x, int y, int cx, int cy, uint flags);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attribute, out RECT rect, int size);
    [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hwnd);
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
$targetHwnd = [IntPtr]::Zero
$hiddenOverlays = [System.Collections.Generic.List[object]]::new()
try {
    Start-Sleep -Seconds $Seconds
    for ($i = 0; $i -lt 20 -and $targetHwnd -eq [IntPtr]::Zero; $i++) {
        $targetHwnd = [DpiAwareWindowCapture]::FindByPidAndTitle([uint32]$proc.Id, $ExpectedTitle)
        if ($targetHwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($targetHwnd -eq [IntPtr]::Zero) { throw "No visible '$ExpectedTitle' window for pid=$($proc.Id)" }

    [DpiAwareWindowCapture]::EnumWindows({ param($hwnd, $lParam)
        if ($hwnd -eq $targetHwnd -or -not [DpiAwareWindowCapture]::IsWindowVisible($hwnd)) { return $true }
        $titleBuilder = New-Object Text.StringBuilder 512
        [DpiAwareWindowCapture]::GetWindowText($hwnd, $titleBuilder, $titleBuilder.Capacity) | Out-Null
        $title = $titleBuilder.ToString()
        if ($title -match '(?i)TraceMemo|迹忆') {
            $hiddenOverlays.Add([pscustomobject]@{ hwnd = $hwnd.ToInt64(); title = $title })
            [DpiAwareWindowCapture]::ShowWindow($hwnd, 0) | Out-Null
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null

    [DpiAwareWindowCapture]::ShowWindow($targetHwnd, 5) | Out-Null
    [DpiAwareWindowCapture]::BringWindowToTop($targetHwnd) | Out-Null
    [DpiAwareWindowCapture]::SetForegroundWindow($targetHwnd) | Out-Null
    [DpiAwareWindowCapture]::SetWindowPos($targetHwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0043) | Out-Null
    Start-Sleep -Milliseconds 1000

    $foreground = [DpiAwareWindowCapture]::GetForegroundWindow()
    [uint32]$foregroundPid = 0
    [DpiAwareWindowCapture]::GetWindowThreadProcessId($foreground, [ref]$foregroundPid) | Out-Null
    if ($foreground -ne $targetHwnd -or $foregroundPid -ne [uint32]$proc.Id) {
        throw "Target was not foreground: target=$targetHwnd foreground=$foreground pid=$foregroundPid"
    }

    $dwmRect = New-Object DpiAwareWindowCapture+RECT
    $dwmResult = [DpiAwareWindowCapture]::DwmGetWindowAttribute($targetHwnd, 9, [ref]$dwmRect, [Runtime.InteropServices.Marshal]::SizeOf($dwmRect))
    if ($dwmResult -ne 0) { throw "DwmGetWindowAttribute(DWMWA_EXTENDED_FRAME_BOUNDS) failed: $dwmResult" }
    $width = $dwmRect.Right - $dwmRect.Left
    $height = $dwmRect.Bottom - $dwmRect.Top
    if ($width -le 0 -or $height -le 0) { throw "Invalid DWM bounds: $($width)x$($height)" }

    $bitmap = New-Object Drawing.Bitmap($width, $height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($dwmRect.Left, $dwmRect.Top, 0, 0, $bitmap.Size, [Drawing.CopyPixelOperation]::SourceCopy)
    $graphics.Dispose()
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose()

    [pscustomobject]@{
        exe = $exePath
        pid = $proc.Id
        hwnd = $targetHwnd.ToInt64()
        expected_title = $ExpectedTitle
        foreground_hwnd = $foreground.ToInt64()
        foreground_pid = $foregroundPid
        dpi = [DpiAwareWindowCapture]::GetDpiForWindow($targetHwnd)
        dwm_bounds = "$($width)x$($height)+$($dwmRect.Left)+$($dwmRect.Top)"
        hidden_overlay_windows = @($hiddenOverlays)
        screenshot = $outputPath
        seconds = $Seconds
        capture_method = "CopyFromScreen_using_DWMWA_EXTENDED_FRAME_BOUNDS"
        verdict = "PASS"
        proves = "the target window was foreground and the capture used DWM physical bounds rather than logical GetWindowRect bounds"
        not_proven = "glyph quality, layout, gameplay semantics, persistence, or release readiness until the screenshot is reviewed"
    } | ConvertTo-Json -Depth 6 -Compress
}
finally {
    if ($targetHwnd -ne [IntPtr]::Zero) {
        [DpiAwareWindowCapture]::SetWindowPos($targetHwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0043) | Out-Null
    }
    foreach ($entry in $hiddenOverlays) {
        [DpiAwareWindowCapture]::ShowWindow([IntPtr]$entry.hwnd, 5) | Out-Null
    }
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
    }
}
