param(
    [Parameter(Mandatory = $true)] [string]$ControlExe,
    [Parameter(Mandatory = $true)] [string]$CandidateExe,
    [Parameter(Mandatory = $true)] [int]$CandidateProcessId,
    [Parameter(Mandatory = $true)] [string]$OutputDirectory,
    [string]$Ffmpeg = "ffmpeg.exe"
)

$ErrorActionPreference = "Stop"
$controlPath = (Resolve-Path -LiteralPath $ControlExe).Path
$candidatePath = (Resolve-Path -LiteralPath $CandidateExe).Path
$outputDir = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $outputDir) { throw "Refusing to reuse existing output directory: $outputDir" }
New-Item -ItemType Directory -Path $outputDir | Out-Null
$ffmpegPath = (Get-Command $Ffmpeg -ErrorAction Stop).Source

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class DdaGrabControlV26Native {
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
  public static IntPtr Find(uint wantedPid) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),"Mutagenic",StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
}
"@

function Hash-Upper([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant() }
function Start-Window([string]$ExePath) {
    $proc = Start-Process -FilePath $ExePath -WorkingDirectory (Split-Path -Parent $ExePath) -PassThru
    Start-Sleep -Seconds 5
    $hwnd = [IntPtr]::Zero
    for ($i=0; $i -lt 20 -and $hwnd -eq [IntPtr]::Zero; $i++) {
        $hwnd = [DdaGrabControlV26Native]::Find([uint32]$proc.Id)
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 250 }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "No Mutagenic window for pid=$($proc.Id)" }
    [DdaGrabControlV26Native]::ShowWindow($hwnd, 9) | Out-Null
    [DdaGrabControlV26Native]::BringWindowToTop($hwnd) | Out-Null
    [DdaGrabControlV26Native]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    return [pscustomobject]@{ Process=$proc; Hwnd=$hwnd }
}
function Bring-ExistingWindow([int]$ProcessId) {
    $hwnd = [DdaGrabControlV26Native]::Find([uint32]$ProcessId)
    if ($hwnd -eq [IntPtr]::Zero) { throw "No Mutagenic window for existing pid=$ProcessId" }
    [DdaGrabControlV26Native]::ShowWindow($hwnd, 9) | Out-Null
    [DdaGrabControlV26Native]::BringWindowToTop($hwnd) | Out-Null
    [DdaGrabControlV26Native]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    return $hwnd
}
function Capture-Desktop([string]$Label, [string]$ExePath, [int]$ProcessId, [IntPtr]$Hwnd) {
    $output = Join-Path $outputDir ("capture_ddagrab_{0}_v26.png" -f $Label)
    $filter = "ddagrab=framerate=1:video_size=2048x1152:offset_x=0:offset_y=0:draw_mouse=0"
    $vf = "hwdownload,format=bgra"
    $stdoutPath = Join-Path $outputDir ("ffmpeg_{0}.stdout.log" -f $Label)
    $stderrPath = Join-Path $outputDir ("ffmpeg_{0}.stderr.log" -f $Label)
    $args = @('-y','-hide_banner','-loglevel','warning','-f','lavfi','-i',$filter,'-vf',$vf,'-frames:v','1','-c:v','png','-update','1',$output)
    $ff = Start-Process -FilePath $ffmpegPath -ArgumentList $args -WorkingDirectory $outputDir -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    if (-not (Test-Path -LiteralPath $output)) { throw "ddagrab output missing for $Label; exit=$($ff.ExitCode)" }
    return [ordered]@{
        label=$Label; exe=$ExePath; exe_sha256=Hash-Upper $ExePath; pid=$ProcessId; hwnd=$Hwnd.ToInt64();
        output=(Split-Path -Leaf $output); output_size=(Get-Item -LiteralPath $output).Length; output_sha256=Hash-Upper $output;
        ffmpeg_exit_code=$ff.ExitCode; capture_method='ffmpeg ddagrab Desktop Duplication with hwdownload';
        stderr=(Get-Content -LiteralPath $stderrPath -Raw -Encoding utf8)
    }
}

$candidate = Get-Process -Id $CandidateProcessId -ErrorAction Stop
if ((Resolve-Path -LiteralPath $candidate.Path).Path -ne $candidatePath) { throw "Candidate PID does not own expected EXE" }
$control = $null
try {
    $control = Start-Window $controlPath
    $controlRecord = Capture-Desktop 'control_c2' $controlPath $control.Process.Id $control.Hwnd
} finally {
    if ($control -and -not $control.Process.HasExited) { Stop-Process -Id $control.Process.Id -Force -ErrorAction SilentlyContinue; $control.Process.WaitForExit() }
}
$candidateHwnd = Bring-ExistingWindow $CandidateProcessId
$candidateRecord = Capture-Desktop 'candidate_c5_l1' $candidatePath $CandidateProcessId $candidateHwnd
$record = [ordered]@{
    evidence_id='C5-L1-capture-ddagrab-runs-v26-20260814'; control=$controlRecord; candidate=$candidateRecord;
    same_output_sha256=($controlRecord.output_sha256 -eq $candidateRecord.output_sha256);
    proves='the exact C2 control and C5-L1 candidate were captured with the same ddagrab Desktop Duplication path and hashes were recorded';
    not_proven='visual content unless the PNGs are reviewed and the control/candidate outputs distinguish'
}
[IO.File]::WriteAllText((Join-Path $outputDir 'capture_ddagrab_runs_v26.json'), ($record | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
$record | ConvertTo-Json -Depth 8
