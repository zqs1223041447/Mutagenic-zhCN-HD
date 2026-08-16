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
public static class IsolatedWindowCapture {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hwnd, IntPtr insertAfter, int x, int y, int cx, int cy, uint flags);
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
$hiddenWindows = [System.Collections.Generic.List[object]]::new()
try {
    Start-Sleep -Seconds $Seconds
    for ($i = 0; $i -lt 20 -and $targetHwnd -eq [IntPtr]::Zero; $i++) {
        $targetHwnd = [IsolatedWindowCapture]::FindByPidAndTitle([uint32]$proc.Id, $ExpectedTitle)
        if ($targetHwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($targetHwnd -eq [IntPtr]::Zero) {
        throw "No visible window titled '$ExpectedTitle' found for pid=$($proc.Id)"
    }

    # TraceMemo is a known always-on-top desktop overlay in this environment.
    # Hide only matching visible top-level windows for this reversible capture,
    # then restore every window in the finally block.
    [IsolatedWindowCapture]::EnumWindows({ param($hwnd, $lParam)
        if ($hwnd -eq $targetHwnd -or -not [IsolatedWindowCapture]::IsWindowVisible($hwnd)) { return $true }
        $titleBuilder = New-Object Text.StringBuilder 512
        [IsolatedWindowCapture]::GetWindowText($hwnd, $titleBuilder, $titleBuilder.Capacity) | Out-Null
        $title = $titleBuilder.ToString()
        if ($title -match '(?i)TraceMemo|迹忆') {
            $hiddenWindows.Add([pscustomobject]@{ hwnd = $hwnd.ToInt64(); title = $title })
            [IsolatedWindowCapture]::ShowWindow($hwnd, 0) | Out-Null
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null

    [IsolatedWindowCapture]::ShowWindow($targetHwnd, 5) | Out-Null
    [IsolatedWindowCapture]::BringWindowToTop($targetHwnd) | Out-Null
    [IsolatedWindowCapture]::SetForegroundWindow($targetHwnd) | Out-Null
    [IsolatedWindowCapture]::SetWindowPos($targetHwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0043) | Out-Null
    Start-Sleep -Milliseconds 1000

    $foreground = [IsolatedWindowCapture]::GetForegroundWindow()
    [uint32]$foregroundPid = 0
    [IsolatedWindowCapture]::GetWindowThreadProcessId($foreground, [ref]$foregroundPid) | Out-Null
    if ($foreground -ne $targetHwnd -or $foregroundPid -ne [uint32]$proc.Id) {
        throw "Target was not foreground after overlay isolation: target=$targetHwnd foreground=$foreground foregroundPid=$foregroundPid"
    }

    $rect = New-Object IsolatedWindowCapture+RECT
    if (-not [IsolatedWindowCapture]::GetWindowRect($targetHwnd, [ref]$rect)) {
        throw "GetWindowRect failed for target HWND=$targetHwnd"
    }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { throw "Invalid target bounds: $($width)x$($height)" }

    $bitmap = New-Object Drawing.Bitmap($width, $height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size, [Drawing.CopyPixelOperation]::SourceCopy)
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
        bounds = "$($width)x$($height)+$($rect.Left)+$($rect.Top)"
        hidden_overlay_windows = @($hiddenWindows)
        screenshot = $outputPath
        seconds = $Seconds
        capture_method = "CopyFromScreen_after_reversible_TraceMemo_isolation"
        verdict = "PASS"
        proves = "the target window was foreground while known TraceMemo overlay windows were temporarily hidden"
        not_proven = "glyph quality, layout, gameplay semantics, persistence, or release readiness until the screenshot is reviewed"
    } | ConvertTo-Json -Depth 6 -Compress
}
finally {
    if ($targetHwnd -ne [IntPtr]::Zero) {
        [IsolatedWindowCapture]::SetWindowPos($targetHwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0043) | Out-Null
    }
    foreach ($entry in $hiddenWindows) {
        [IsolatedWindowCapture]::ShowWindow([IntPtr]$entry.hwnd, 5) | Out-Null
    }
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
    }
}
