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
public static class ForegroundCaptureNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint source, uint target, bool attach);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hwnd, IntPtr insertAfter, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
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
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
try {
    Start-Sleep -Seconds $Seconds
    $hwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 10 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [ForegroundCaptureNative]::FindByPidAndTitle([uint32]$proc.Id, $ExpectedTitle)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "No visible window titled '$ExpectedTitle' found for pid=$($proc.Id)" }

    $before = [ForegroundCaptureNative]::GetForegroundWindow()
    [uint32]$beforePid = 0
    [ForegroundCaptureNative]::GetWindowThreadProcessId($before, [ref]$beforePid) | Out-Null
    $currentThread = [ForegroundCaptureNative]::GetCurrentThreadId()
    [uint32]$beforeThread = 0
    [ForegroundCaptureNative]::GetWindowThreadProcessId($before, [ref]$beforeThread) | Out-Null
    $attached = $false
    try {
        if ($beforeThread -ne 0 -and $beforeThread -ne $currentThread) {
            $attached = [ForegroundCaptureNative]::AttachThreadInput($currentThread, $beforeThread, $true)
        }
    [ForegroundCaptureNative]::ShowWindow($hwnd, 9) | Out-Null
    [ForegroundCaptureNative]::BringWindowToTop($hwnd) | Out-Null
    [ForegroundCaptureNative]::SetForegroundWindow($hwnd) | Out-Null
    # Temporarily place the target above unrelated always-on-top desktop windows.
    # It is restored in the finally block before the process exits.
    [ForegroundCaptureNative]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0043) | Out-Null
    } finally {
        if ($attached) { [ForegroundCaptureNative]::AttachThreadInput($currentThread, $beforeThread, $false) | Out-Null }
    }
    Start-Sleep -Milliseconds 750
    $after = [ForegroundCaptureNative]::GetForegroundWindow()
    if ($after -ne $hwnd) {
        throw "Target window did not become foreground: target=$hwnd actual=$after before=$before"
    }

    $rect = New-Object ForegroundCaptureNative+RECT
    if (-not [ForegroundCaptureNative]::GetWindowRect($hwnd, [ref]$rect)) { throw "GetWindowRect failed for hwnd=$hwnd" }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { throw "Invalid window bounds: $($width)x$($height)" }
    $bitmap = New-Object Drawing.Bitmap($width, $height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size, [Drawing.CopyPixelOperation]::SourceCopy)
    $graphics.Dispose()

    $sampleStep = 16
    $samples = 0
    $nonBlack = 0
    for ($y = 0; $y -lt $height; $y += $sampleStep) {
        for ($x = 0; $x -lt $width; $x += $sampleStep) {
            $pixel = $bitmap.GetPixel($x, $y)
            $samples++
            if (($pixel.R + $pixel.G + $pixel.B) -gt 12) { $nonBlack++ }
        }
    }
    $nonBlackRatio = if ($samples -gt 0) { [double]$nonBlack / $samples } else { 0 }
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose()
    $verdict = if ($nonBlackRatio -ge 0.01) { "PASS" } else { "FAIL" }
    [pscustomobject]@{
        exe = $exePath
        pid = $proc.Id
        hwnd = $hwnd.ToInt64()
        expected_title = $ExpectedTitle
        foreground_before = $before.ToInt64()
        foreground_after = $after.ToInt64()
        foreground_pid_before = $beforePid
        bounds = "$($width)x$($height)+$($rect.Left)+$($rect.Top)"
        screenshot = $outputPath
        seconds = $Seconds
        sample_count = $samples
        non_black_sample_count = $nonBlack
        non_black_ratio = $nonBlackRatio
        verdict = $verdict
        proves = "the screenshot was captured from the target process after an exact foreground-window assertion"
        not_proven = "gameplay semantics, persistence, and visual quality beyond the captured frame"
    } | ConvertTo-Json -Compress
}
finally {
    if ($hwnd -ne [IntPtr]::Zero) {
        [ForegroundCaptureNative]::SetWindowPos($hwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0043) | Out-Null
    }
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit()
    }
}
