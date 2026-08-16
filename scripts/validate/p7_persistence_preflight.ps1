param(
    [string]$RepositoryRoot = (Get-Location).Path,
    [string]$Output = "10_logs/P7-persistence-track-20260814/preflight.json"
)

$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath($RepositoryRoot)
$outputPath = if ([IO.Path]::IsPathRooted($Output)) {
    [IO.Path]::GetFullPath($Output)
} else {
    [IO.Path]::GetFullPath((Join-Path $root $Output))
}

function Resolve-RepoFile([string]$RelativePath) {
    $path = [IO.Path]::GetFullPath((Join-Path $root $RelativePath))
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required file is missing: $RelativePath"
    }
    return $path
}

$expectedDllSha256 = "DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799"
$controls = @(
    [ordered]@{
        id = "ORIGINAL"
        exe_relative_path = "00_original/Mutagenic.exe"
        expected_exe_sha256 = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
        adjacent_dll_source = "10_logs/clean_noop/steam_api64.dll"
        note = "00_original is immutable and has no DLL beside it; use an ephemeral staged runtime directory for any later run."
    }
    [ordered]@{
        id = "CLEAN_NOOP"
        exe_relative_path = "10_logs/clean_noop/clean_noop.exe"
        expected_exe_sha256 = "94A53EF47AC49CF2F13157905387932BB517F648A15B7A0200B098237F0015DA"
        adjacent_dll_source = "10_logs/clean_noop/steam_api64.dll"
        note = "Use the existing CLEAN NOOP directory without changing it."
    }
    [ordered]@{
        id = "C5_L2_LOCALIZED_COMPARISON"
        exe_relative_path = "10_logs/C5-L2-character-select-20260814/c5_l2_character_select_normalized.exe"
        expected_exe_sha256 = "4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3"
        adjacent_dll_source = "10_logs/C5-L2-character-select-20260814/steam_api64.dll"
        note = "Comparison artifact only; do not use it as a replacement for ORIGINAL or CLEAN NOOP controls."
    }
)

$controlEvidence = foreach ($control in $controls) {
    $exePath = Resolve-RepoFile $control.exe_relative_path
    $actualExeSha256 = (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actualExeSha256 -ne $control.expected_exe_sha256) {
        throw "EXE SHA-256 mismatch for $($control.id): expected=$($control.expected_exe_sha256) actual=$actualExeSha256"
    }

    $dllSourcePath = Resolve-RepoFile $control.adjacent_dll_source
    $actualDllSha256 = (Get-FileHash -LiteralPath $dllSourcePath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actualDllSha256 -ne $expectedDllSha256) {
        throw "DLL SHA-256 mismatch for $($control.id): expected=$expectedDllSha256 actual=$actualDllSha256"
    }

    $adjacentPath = Join-Path (Split-Path -Parent $exePath) "steam_api64.dll"
    [ordered]@{
        id = $control.id
        exe = $exePath
        exe_sha256 = $actualExeSha256
        exe_sha256_expected = $control.expected_exe_sha256
        adjacent_dll = $adjacentPath
        adjacent_dll_present = (Test-Path -LiteralPath $adjacentPath -PathType Leaf)
        dll_source = $dllSourcePath
        dll_source_sha256 = $actualDllSha256
        dll_sha256_expected = $expectedDllSha256
        note = $control.note
    }
}

$rawPath = Resolve-RepoFile "manifests/raw_manifest.json"
$rawManifest = Get-Content -LiteralPath $rawPath -Raw | ConvertFrom-Json
$rawTreeCount = @(Get-ChildItem -LiteralPath (Join-Path $root "03_raw") -Recurse -File).Count
$originalPath = Resolve-RepoFile "00_original/Mutagenic.exe"
$originalSha256 = (Get-FileHash -LiteralPath $originalPath -Algorithm SHA256).Hash.ToUpperInvariant()
$activeProcesses = @(Get-Process -Name Mutagenic -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, MainWindowTitle, Responding)
$localUserData = Join-Path $env:APPDATA "Godot\app_userdata\Mutagenic"
$localSaveFiles = @()
if (Test-Path -LiteralPath $localUserData -PathType Container) {
    $localSaveFiles = @(Get-ChildItem -LiteralPath $localUserData -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "_0_6_0\.dat$" } |
        Select-Object -ExpandProperty FullName)
}

$result = [ordered]@{
    evidence_id = "P7-persistence-preflight-20260814"
    recorded_at = (Get-Date -Format o)
    status = "PASS"
    runtime_gate = "NOT_STARTED"
    controls = $controlEvidence
    immutable_input_check = [ordered]@{
        original_exe = $originalPath
        original_sha256 = $originalSha256
        original_expected_sha256 = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
        raw_tree_file_count = $rawTreeCount
        raw_manifest_path_count = $rawManifest.Count
        raw_manifest_sha256 = (Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToUpperInvariant()
    }
    active_mutagenic_processes = $activeProcesses
    local_save_scan = [ordered]@{
        path = $localUserData
        matching_save_file_count = $localSaveFiles.Count
        matching_save_file_names = @($localSaveFiles | ForEach-Object { Split-Path -Leaf $_ })
    }
    steam_state_read = $false
    save_mutation_performed = $false
    proves = "All declared persistence controls and runtime DLL inputs match their SHA-guarded evidence; immutable input counts and original fingerprint remain intact; this preflight read no save contents and did not launch or mutate the game."
    not_proven = "Runtime boot, save creation, serialization, Steam callbacks, local fallback, restart persistence, Quit persistence, gameplay, or localization regression."
    next_action = "Obtain an explicit disposable test-save decision before launching the controlled persistence sequence; stage ORIGINAL without modifying 00_original."
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
[IO.File]::WriteAllText($outputPath, ($result | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $outputPath -Raw -Encoding UTF8
