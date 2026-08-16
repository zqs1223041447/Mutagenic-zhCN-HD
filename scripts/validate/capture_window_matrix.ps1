param(
    [Parameter(Mandatory = $true)]
    [string]$Exe,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,
    [int]$Seconds = 8,
    [string]$ExpectedTitle = "Mutagenic"
)

$ErrorActionPreference = "Stop"
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$outDir = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class CaptureMatrixNative {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern IntPtr GetWindowDC(IntPtr h);
  [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr h, IntPtr dc);
  [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleDC(IntPtr dc);
  [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleBitmap(IntPtr dc, int w, int h);
  [DllImport("gdi32.dll")] public static extern IntPtr SelectObject(IntPtr dc, IntPtr obj);
  [DllImport("gdi32.dll")] public static extern bool BitBlt(IntPtr dst, int x, int y, int w, int h, IntPtr src, int sx, int sy, uint rop);
  [DllImport("gdi32.dll")] public static extern bool DeleteObject(IntPtr obj);
  [DllImport("gdi32.dll")] public static extern bool DeleteDC(IntPtr dc);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint pid; GetWindowThreadProcessId(h,out pid); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(pid==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
}
"@

function Save-Bitmap([IntPtr]$Hwnd, [int]$Width, [int]$Height, [string]$Path, [ValidateSet('WindowDC','PrintWindow')] [string]$Method) {
    $dc = [CaptureMatrixNative]::GetWindowDC($Hwnd)
    if ($dc -eq [IntPtr]::Zero) { throw "GetWindowDC failed" }
    $mem = [IntPtr]::Zero; $bmpHandle = [IntPtr]::Zero; $old = [IntPtr]::Zero
    try {
        $mem = [CaptureMatrixNative]::CreateCompatibleDC($dc)
        $bmpHandle = [CaptureMatrixNative]::CreateCompatibleBitmap($dc,$Width,$Height)
        $old = [CaptureMatrixNative]::SelectObject($mem,$bmpHandle)
        $ok = if ($Method -eq 'PrintWindow') { [CaptureMatrixNative]::PrintWindow($Hwnd,$mem,2) } else { [CaptureMatrixNative]::BitBlt($mem,0,0,$Width,$Height,$dc,0,0,0x00CC0020) }
        if (-not $ok) { throw "$Method failed" }
        $bmp = [Drawing.Bitmap]::FromHbitmap($bmpHandle)
        $bmp.Save($Path,[Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
    } finally {
        if ($mem -ne [IntPtr]::Zero -and $old -ne [IntPtr]::Zero) { [CaptureMatrixNative]::SelectObject($mem,$old) | Out-Null }
        if ($bmpHandle -ne [IntPtr]::Zero) { [CaptureMatrixNative]::DeleteObject($bmpHandle) | Out-Null }
        if ($mem -ne [IntPtr]::Zero) { [CaptureMatrixNative]::DeleteDC($mem) | Out-Null }
        [CaptureMatrixNative]::ReleaseDC($Hwnd,$dc) | Out-Null
    }
}

$proc = Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -PassThru
$target = [IntPtr]::Zero
$hidden = [System.Collections.Generic.List[object]]::new()
try {
    Start-Sleep -Seconds $Seconds
    for ($i=0; $i -lt 20 -and $target -eq [IntPtr]::Zero; $i++) { $target=[CaptureMatrixNative]::Find([uint32]$proc.Id,$ExpectedTitle); if($target -eq [IntPtr]::Zero){Start-Sleep -Milliseconds 250} }
    if($target -eq [IntPtr]::Zero){throw "target window not found"}
    [CaptureMatrixNative]::EnumWindows({param($h,$l); if($h -eq $target -or -not [CaptureMatrixNative]::IsWindowVisible($h)){return $true};$sb=New-Object Text.StringBuilder 512;[CaptureMatrixNative]::GetWindowText($h,$sb,$sb.Capacity)|Out-Null;if($sb.ToString() -match '(?i)TraceMemo|迹忆'){ $hidden.Add([pscustomobject]@{hwnd=$h.ToInt64();title=$sb.ToString()});[CaptureMatrixNative]::ShowWindow($h,0)|Out-Null};return $true},[IntPtr]::Zero)|Out-Null
    [CaptureMatrixNative]::ShowWindow($target,5)|Out-Null;[CaptureMatrixNative]::BringWindowToTop($target)|Out-Null;[CaptureMatrixNative]::SetForegroundWindow($target)|Out-Null;[CaptureMatrixNative]::SetWindowPos($target,[IntPtr](-1),0,0,0,0,0x0043)|Out-Null;Start-Sleep -Milliseconds 1000
    $fg=[CaptureMatrixNative]::GetForegroundWindow();[uint32]$fgPid=0;[CaptureMatrixNative]::GetWindowThreadProcessId($fg,[ref]$fgPid)|Out-Null;if($fg -ne $target -or $fgPid -ne [uint32]$proc.Id){throw "target not foreground"}
    $r=New-Object CaptureMatrixNative+RECT;$dwm=[CaptureMatrixNative]::DwmGetWindowAttribute($target,9,[ref]$r,[Runtime.InteropServices.Marshal]::SizeOf($r));if($dwm -ne 0){throw "DWM bounds failed"};$w=$r.Right-$r.Left;$h=$r.Bottom-$r.Top
    $bitmap=[Drawing.Bitmap]::new($w,$h);$graphics=[Drawing.Graphics]::FromImage($bitmap);$graphics.CopyFromScreen($r.Left,$r.Top,0,0,$bitmap.Size,[Drawing.CopyPixelOperation]::SourceCopy);$graphics.Dispose();$screenPath=Join-Path $outDir 'screen.png';$bitmap.Save($screenPath,[Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose()
    Save-Bitmap $target $w $h (Join-Path $outDir 'window_dc.png') 'WindowDC'
    Save-Bitmap $target $w $h (Join-Path $outDir 'print_window.png') 'PrintWindow'
    $files=Get-ChildItem -LiteralPath $outDir -File | ForEach-Object { [pscustomobject]@{name=$_.Name;size=$_.Length;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash} }
    [pscustomobject]@{exe=$exePath;pid=$proc.Id;hwnd=$target.ToInt64();foreground_pid=$fgPid;dwm_bounds="$($w)x$($h)+$($r.Left)+$($r.Top)";hidden_overlay_windows=@($hidden);capture_methods=@('screen','window_dc','print_window');files=@($files);attempt_verdict='PASS';visual_verdict='HUMAN_REQUIRED';proves='all three capture paths were attempted while the target process-owned window was foreground';not_proven='which pixels represent the game surface until images are reviewed'} | ConvertTo-Json -Depth 6
} finally {
    if($target -ne [IntPtr]::Zero){[CaptureMatrixNative]::SetWindowPos($target,[IntPtr](-2),0,0,0,0,0x0043)|Out-Null};foreach($entry in $hidden){[CaptureMatrixNative]::ShowWindow([IntPtr]$entry.hwnd,5)|Out-Null};if(-not $proc.HasExited){Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue;$proc.WaitForExit()}
}
