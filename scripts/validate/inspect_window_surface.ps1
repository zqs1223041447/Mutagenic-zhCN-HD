param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [int]$Seconds = 5
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class SurfaceInspectNative {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT rect, int size);
  [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hwnd, int index);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hwnd, ref POINT point);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hwnd, out RECT rect);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
}
"@

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
try {
    Start-Sleep -Seconds $Seconds
    $hwnd = [SurfaceInspectNative]::Find([uint32]$proc.Id, "Mutagenic")
    if ($hwnd -eq [IntPtr]::Zero) { throw "No Mutagenic window for pid=$($proc.Id)" }
    $windowRect = New-Object SurfaceInspectNative+RECT
    $clientRect = New-Object SurfaceInspectNative+RECT
    $dwmRect = New-Object SurfaceInspectNative+RECT
    [SurfaceInspectNative]::GetWindowRect($hwnd,[ref]$windowRect) | Out-Null
    [SurfaceInspectNative]::GetClientRect($hwnd,[ref]$clientRect) | Out-Null
    [SurfaceInspectNative]::DwmGetWindowAttribute($hwnd,9,[ref]$dwmRect,[Runtime.InteropServices.Marshal]::SizeOf($dwmRect)) | Out-Null
    $clientOrigin = New-Object SurfaceInspectNative+POINT
    [SurfaceInspectNative]::ClientToScreen($hwnd,[ref]$clientOrigin) | Out-Null
    [uint32]$windowPid=0; [SurfaceInspectNative]::GetWindowThreadProcessId($hwnd,[ref]$windowPid) | Out-Null
    $foreground = [SurfaceInspectNative]::GetForegroundWindow()
    [uint32]$foregroundPid=0; [SurfaceInspectNative]::GetWindowThreadProcessId($foreground,[ref]$foregroundPid) | Out-Null
    $title = New-Object Text.StringBuilder 512; [SurfaceInspectNative]::GetWindowText($hwnd,$title,$title.Capacity) | Out-Null
    $class = New-Object Text.StringBuilder 512; [SurfaceInspectNative]::GetClassName($hwnd,$class,$class.Capacity) | Out-Null
    [pscustomobject]@{
      exe=$exePath; pid=$proc.Id; hwnd=$hwnd.ToInt64(); window_pid=$windowPid; foreground_hwnd=$foreground.ToInt64(); foreground_pid=$foregroundPid;
      title=$title.ToString(); class_name=$class.ToString(); visible=[SurfaceInspectNative]::IsWindowVisible($hwnd); responding=(Get-Process -Id $proc.Id).Responding;
      iconic=[SurfaceInspectNative]::IsIconic($hwnd); zoomed=[SurfaceInspectNative]::IsZoomed($hwnd); style=[SurfaceInspectNative]::GetWindowLong($hwnd,-16); exstyle=[SurfaceInspectNative]::GetWindowLong($hwnd,-20);
      window_rect="$($windowRect.Right-$windowRect.Left)x$($windowRect.Bottom-$windowRect.Top)+$($windowRect.Left)+$($windowRect.Top)";
      client_rect="$($clientRect.Right-$clientRect.Left)x$($clientRect.Bottom-$clientRect.Top)+$($clientOrigin.X)+$($clientOrigin.Y)";
      dwm_rect="$($dwmRect.Right-$dwmRect.Left)x$($dwmRect.Bottom-$dwmRect.Top)+$($dwmRect.Left)+$($dwmRect.Top)";
      verdict="PASS"; proves="the candidate window surface metadata was collected from the exact process-owned HWND"; not_proven="the actual GPU pixels or visual glyph quality"
    } | ConvertTo-Json -Depth 5
} finally {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; $proc.WaitForExit() }
}
