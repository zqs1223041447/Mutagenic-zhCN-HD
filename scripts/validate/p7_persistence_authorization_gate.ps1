param(
    [ValidateSet("ORIGINAL", "CLEAN_NOOP", "C5_L2_LOCALIZED")]
    [string]$CandidateId = "ORIGINAL",
    [string]$RunId = "",
    [switch]$AllowDisposableTestSave,
    [string]$Output = "10_logs/P7-persistence-track-20260814/authorization_gate.json"
)

$ErrorActionPreference = "Stop"
$root = (Get-Location).Path
$outputPath = if ([IO.Path]::IsPathRooted($Output)) {
    [IO.Path]::GetFullPath($Output)
} else {
    [IO.Path]::GetFullPath((Join-Path $root $Output))
}

if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = "P7-" + (Get-Date -Format "yyyyMMdd-HHmmss")
}
if ($RunId -notmatch "^[A-Za-z0-9._-]+$") {
    throw "RunId contains unsafe characters: $RunId"
}

$expectedDllSha256 = "DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799"
$controls = @{
    ORIGINAL = [ordered]@{
        exe = "00_original/Mutagenic.exe"
        expected_exe_sha256 = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
        dll_source = "10_logs/clean_noop/steam_api64.dll"
        note = "Stage the DLL beside a copied ORIGINAL executable in an ephemeral run directory; never write into 00_original."
    }
    CLEAN_NOOP = [ordered]@{
        exe = "10_logs/clean_noop/clean_noop.exe"
        expected_exe_sha256 = "94A53EF47AC49CF2F13157905387932BB517F648A15B7A0200B098237F0015DA"
        dll_source = "10_logs/clean_noop/steam_api64.dll"
        note = "Use the immutable recorded CLEAN NOOP candidate and its adjacent DLL."
    }
    C5_L2_LOCALIZED = [ordered]@{
        exe = "10_logs/C5-L2-character-select-20260814/c5_l2_character_select_normalized.exe"
        expected_exe_sha256 = "4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3"
        dll_source = "10_logs/C5-L2-character-select-20260814/steam_api64.dll"
        note = "Comparison artifact only; compare after ORIGINAL and CLEAN NOOP, never use it as a control base."
    }
}

$control = $controls[$CandidateId]
$exePath = [IO.Path]::GetFullPath((Join-Path $root $control.exe))
$dllSourcePath = [IO.Path]::GetFullPath((Join-Path $root $control.dll_source))
if (-not (Test-Path -LiteralPath $exePath -PathType Leaf)) { throw "Candidate EXE missing: $exePath" }
if (-not (Test-Path -LiteralPath $dllSourcePath -PathType Leaf)) { throw "Runtime DLL source missing: $dllSourcePath" }
$actualExeSha256 = (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash.ToUpperInvariant()
$actualDllSha256 = (Get-FileHash -LiteralPath $dllSourcePath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualExeSha256 -ne $control.expected_exe_sha256) { throw "Candidate SHA mismatch: expected=$($control.expected_exe_sha256) actual=$actualExeSha256" }
if ($actualDllSha256 -ne $expectedDllSha256) { throw "DLL SHA mismatch: expected=$expectedDllSha256 actual=$actualDllSha256" }

$activeProcesses = @(Get-Process -Name Mutagenic -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, MainWindowTitle, Responding)
$adjacentDll = Join-Path (Split-Path -Parent $exePath) "steam_api64.dll"
$authorizationGranted = [bool]$AllowDisposableTestSave
$result = [ordered]@{
    evidence_id = "P7-persistence-authorization-gate-20260814"
    recorded_at = (Get-Date -Format o)
    run_id = $RunId
    candidate_id = $CandidateId
    candidate = $exePath
    candidate_sha256 = $actualExeSha256
    expected_candidate_sha256 = $control.expected_exe_sha256
    dll_source = $dllSourcePath
    dll_source_sha256 = $actualDllSha256
    adjacent_dll = $adjacentDll
    adjacent_dll_present = (Test-Path -LiteralPath $adjacentDll -PathType Leaf)
    active_mutagenic_processes = $activeProcesses
    authorization_granted = $authorizationGranted
    authorization_flag = "AllowDisposableTestSave"
    launch_performed = $false
    save_mutation_performed = $false
    steam_state_read = $false
    runtime_gate = "NOT_STARTED"
    status = if ($authorizationGranted) { "IN_PROGRESS" } else { "HUMAN_REQUIRED" }
    active_blocker = $false
    note = $control.note
    proves = "The selected candidate and runtime DLL are SHA-guarded and this command performed no launch, Steam read, or save mutation. Without the explicit authorization switch, the gate records a nonblocking human checkpoint and stops."
    not_proven = "Runtime boot, disposable character creation, save serialization, Steam callbacks, restart persistence, Quit persistence, input behavior, or cleanup."
    next_action = if ($authorizationGranted) { "Create an isolated staging directory and execute the separately reviewed human persistence protocol; do not reuse a prior save or generated EXE." } else { "Obtain explicit disposable test-save authorization before any state-mutating run; do not infer authorization from this record." }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
[IO.File]::WriteAllText($outputPath, ($result | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $outputPath -Raw -Encoding UTF8
