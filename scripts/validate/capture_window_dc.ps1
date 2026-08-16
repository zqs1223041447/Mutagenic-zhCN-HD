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
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class WindowDcCapture {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] public static extern IntPtr GetWindowDC(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr hwnd, IntPtr dc);
    [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleDC(IntPtr dc);
    [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleBitmap(IntPtr dc, int width, int height);
    [DllImport("gdi32.dll")] public static extern IntPtr SelectObject(IntPtr dc, IntPtr objectHandle);
    [DllImport("gdi32.dll")] public static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll")] public static extern bool DeleteObject(IntPtr objectHandle);
    [DllImport("gdi32.dll")] public static extern bool BitBlt(IntPtr dest, int x, int y, int width, int height, IntPtr src, int srcX, int srcY, uint rop);
    public static IntPtr Find(uint wantedPid, string wantedTitle) {
        IntPtr result = IntPtr.Zero;
        EnumWindows((hwnd, lParam) => {
            uint pid; GetWindowThreadProcessId(hwnd, out pid);
            var text = new StringBuilder(512); GetWindowText(hwnd, text, text.Capacity);
            if (pid == wantedPid && IsWindowVisible(hwnd) && string.Equals(text.ToString(), wantedTitle, StringComparison.OrdinalIgnoreCase)) { result = hwnd; return false; }
            return true;
        }, IntPtr.Zero);
        return result;
    }
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
try {
    Start-Sleep -Seconds $Seconds
    $hwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 10 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [WindowDcCapture]::Find([uint32]$proc.Id, $ExpectedTitle)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "No visible target window found" }
    [WindowDcCapture]::ShowWindow($hwnd, 9) | Out-Null
    [WindowDcCapture]::BringWindowToTop($hwnd) | Out-Null
    [WindowDcCapture]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    $rect = New-Object WindowDcCapture+RECT
    if (-not [WindowDcCapture]::GetWindowRect($hwnd, [ref]$rect)) { throw "GetWindowRect failed" }
    $width = $rect.Right - $rect.Left; $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { throw "Invalid bounds" }
    $dc = [WindowDcCapture]::GetWindowDC($hwnd)
    if ($dc -eq [IntPtr]::Zero) { throw "GetWindowDC failed" }
    $memoryDc = [IntPtr]::Zero
    $bitmapHandle = [IntPtr]::Zero
    $oldBitmap = [IntPtr]::Zero
    try {
        $memoryDc = [WindowDcCapture]::CreateCompatibleDC($dc)
        $bitmapHandle = [WindowDcCapture]::CreateCompatibleBitmap($dc, $width, $height)
        if ($memoryDc -eq [IntPtr]::Zero -or $bitmapHandle -eq [IntPtr]::Zero) { throw "GDI compatible surface creation failed" }
        $oldBitmap = [WindowDcCapture]::SelectObject($memoryDc, $bitmapHandle)
        if (-not [WindowDcCapture]::BitBlt($memoryDc, 0, 0, $width, $height, $dc, 0, 0, 0x00CC0020)) { throw "BitBlt failed" }
        $bitmap = [Drawing.Bitmap]::FromHbitmap($bitmapHandle)
        $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
        $bitmap.Dispose()
    } finally {
        if ($memoryDc -ne [IntPtr]::Zero -and $oldBitmap -ne [IntPtr]::Zero) { [WindowDcCapture]::SelectObject($memoryDc, $oldBitmap) | Out-Null }
        if ($bitmapHandle -ne [IntPtr]::Zero) { [WindowDcCapture]::DeleteObject($bitmapHandle) | Out-Null }
        if ($memoryDc -ne [IntPtr]::Zero) { [WindowDcCapture]::DeleteDC($memoryDc) | Out-Null }
        [WindowDcCapture]::ReleaseDC($hwnd, $dc) | Out-Null
    }
    [pscustomobject]@{
        exe = $exePath; pid = $proc.Id; hwnd = $hwnd.ToInt64(); expected_title = $ExpectedTitle
        bounds = "$($width)x$($height)+$($rect.Left)+$($rect.Top)"; screenshot = $outputPath
        capture_method = "GetWindowDC"
        verdict = "PASS"
        proves = "a target HWND was found and a window-DC capture was attempted"
        not_proven = "that the GPU-rendered frame was captured correctly, glyph rendering, layout, gameplay, or persistence"
    } | ConvertTo-Json -Compress
} finally {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; $proc.WaitForExit() }
}
