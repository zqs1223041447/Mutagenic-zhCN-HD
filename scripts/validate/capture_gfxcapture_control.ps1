param(
    [Parameter(Mandatory = $true)]
    [string]$ControlExe,
    [Parameter(Mandatory = $true)]
    [string]$CandidateExe,
    [Parameter(Mandatory = $true)]
    [int]$CandidateProcessId,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,
    [string]$Ffmpeg = "ffmpeg.exe"
)

$ErrorActionPreference = "Stop"
$controlPath = (Resolve-Path -LiteralPath $ControlExe).Path
$candidatePath = (Resolve-Path -LiteralPath $CandidateExe).Path
$outputDir = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $outputDir) {
    throw "Refusing to reuse existing output directory: $outputDir"
}
New-Item -ItemType Directory -Path $outputDir | Out-Null
$ffmpegPath = (Get-Command $Ffmpeg -ErrorAction Stop).Source

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class GfxCaptureControlV23Native {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
  public static IntPtr Find(uint wantedPid, string wantedTitle) {
    IntPtr found=IntPtr.Zero;
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); var s=new StringBuilder(512); GetWindowText(h,s,s.Capacity); if(p==wantedPid && IsWindowVisible(h) && string.Equals(s.ToString(),wantedTitle,StringComparison.OrdinalIgnoreCase)){found=h;return false;} return true;},IntPtr.Zero);
    return found;
  }
}
"@

function Get-HashUpper([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Find-Window([int]$ProcessId) {
    for ($i = 0; $i -lt 40; $i++) {
        $h = [GfxCaptureControlV23Native]::Find([uint32]$ProcessId, "Mutagenic")
        if ($h -ne [IntPtr]::Zero) { return $h }
        Start-Sleep -Milliseconds 250
    }
    throw "No visible Mutagenic window for pid=$ProcessId"
}

function Capture-Window([string]$Label, [int]$ProcessId, [IntPtr]$Hwnd, [string]$ExePath) {
    $output = Join-Path $outputDir ("capture_gfxcapture_{0}_v23.png" -f $Label)
    $filter = "gfxcapture=hwnd=$($Hwnd.ToInt64()):capture_cursor=false:capture_border=false"
    $vf = "hwdownload,format=bgra"
    $logPath = Join-Path $outputDir ("ffmpeg_{0}.log" -f $Label)
    $stdoutPath = Join-Path $outputDir ("ffmpeg_{0}.stdout.log" -f $Label)
    $stderrPath = Join-Path $outputDir ("ffmpeg_{0}.stderr.log" -f $Label)
    $argumentList = @('-y', '-hide_banner', '-loglevel', 'warning', '-f', 'lavfi', '-i', $filter, '-vf', $vf, '-frames:v', '1', '-c:v', 'png', '-update', '1', $output)
    $ffmpegProcess = Start-Process -FilePath $ffmpegPath -ArgumentList $argumentList -WorkingDirectory $outputDir -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $exitCode = $ffmpegProcess.ExitCode
    $stdout = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw -Encoding utf8 } else { '' }
    $stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw -Encoding utf8 } else { '' }
    [IO.File]::WriteAllText($logPath, "STDOUT`n$stdout`nSTDERR`n$stderr", [Text.UTF8Encoding]::new($false))
    if (-not (Test-Path -LiteralPath $output)) { throw "gfxcapture output missing for $Label; exit=$exitCode" }
    $process = Get-Process -Id $ProcessId -ErrorAction Stop
    return [ordered]@{
        label = $Label
        exe = $ExePath
        exe_sha256 = Get-HashUpper $ExePath
        pid = $ProcessId
        hwnd = $Hwnd.ToInt64()
        title = $process.MainWindowTitle
        responding = $process.Responding
        output = Split-Path -Leaf $output
        output_size = (Get-Item -LiteralPath $output).Length
        output_sha256 = Get-HashUpper $output
        ffmpeg_exit_code = $exitCode
        capture_method = "ffmpeg gfxcapture direct HWND with hwdownload"
    }
}

$controlDll = Join-Path (Split-Path -Parent $controlPath) "steam_api64.dll"
$candidateDll = Join-Path (Split-Path -Parent $candidatePath) "steam_api64.dll"
if (-not (Test-Path -LiteralPath $controlDll -PathType Leaf)) { throw "Control DLL missing: $controlDll" }
if (-not (Test-Path -LiteralPath $candidateDll -PathType Leaf)) { throw "Candidate DLL missing: $candidateDll" }
$candidateProcess = Get-Process -Id $CandidateProcessId -ErrorAction Stop
if ((Resolve-Path -LiteralPath $candidateProcess.Path).Path -ne $candidatePath) { throw "Candidate PID does not own expected EXE" }

$controlProcess = Start-Process -FilePath $controlPath -WorkingDirectory (Split-Path -Parent $controlPath) -PassThru
try {
    Start-Sleep -Seconds 5
    $controlHwnd = Find-Window $controlProcess.Id
    $controlRecord = Capture-Window "control_c2" $controlProcess.Id $controlHwnd $controlPath
} finally {
    if (-not $controlProcess.HasExited) { Stop-Process -Id $controlProcess.Id -Force -ErrorAction SilentlyContinue; $controlProcess.WaitForExit() }
}

Start-Sleep -Milliseconds 500
$candidateHwnd = Find-Window $CandidateProcessId
$candidateRecord = Capture-Window "candidate_c5_l1" $CandidateProcessId $candidateHwnd $candidatePath
$record = [ordered]@{
    evidence_id = "C5-L1-capture-gfxcapture-runs-v23-20260814"
    control = $controlRecord
    candidate = $candidateRecord
    same_output_sha256 = ($controlRecord.output_sha256 -eq $candidateRecord.output_sha256)
    proves = "the exact C2 control and C5-L1 candidate were captured with the same direct-HWND gfxcapture path and hashes were recorded"
    not_proven = "visual content unless the PNGs are reviewed and the control/candidate outputs distinguish"
}
$metadataPath = Join-Path $outputDir "capture_gfxcapture_runs_v23.json"
[IO.File]::WriteAllText($metadataPath, ($record | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
$record | ConvertTo-Json -Depth 8
