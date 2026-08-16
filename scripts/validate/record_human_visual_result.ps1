param(
    [Parameter(Mandatory = $true)]
    [string]$SessionPath,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedCandidateSha256,
    [Parameter(Mandatory = $true)]
    [ValidateSet("PASS", "FAIL")]
    [string]$VisualVerdict,
    [Parameter(Mandatory = $true)]
    [bool]$MainMenuVisible,
    [Parameter(Mandatory = $true)]
    [bool]$AlertDialogAbsent,
    [Parameter(Mandatory = $true)]
    [bool]$StartButtonTextExact,
    [Parameter(Mandatory = $true)]
    [bool]$GlyphsOkay,
    [Parameter(Mandatory = $true)]
    [bool]$FallbackOkay,
    [Parameter(Mandatory = $true)]
    [bool]$ClippingOkay,
    [Parameter(Mandatory = $true)]
    [bool]$LayoutOkay,
    [string]$Observer = "human",
    [string]$Notes = "",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$sessionFullPath = (Resolve-Path -LiteralPath $SessionPath).Path
$session = Get-Content -LiteralPath $sessionFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
$candidatePath = (Resolve-Path -LiteralPath $session.candidate).Path
$expected = $ExpectedCandidateSha256.ToUpperInvariant()
$actual = (Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actual -ne $expected) {
    throw "Candidate SHA-256 mismatch: expected=$expected actual=$actual"
}

$dllPath = (Resolve-Path -LiteralPath $session.adjacent_runtime_dll).Path
$dllSha256 = (Get-FileHash -LiteralPath $dllPath -Algorithm SHA256).Hash.ToUpperInvariant()
$checklist = [ordered]@{
    main_menu_visible = $MainMenuVisible
    alert_dialog_absent = $AlertDialogAbsent
    start_button_text_exact = $StartButtonTextExact
    glyphs_okay = $GlyphsOkay
    fallback_okay = $FallbackOkay
    clipping_okay = $ClippingOkay
    layout_okay = $LayoutOkay
}
$allChecksPass = @($checklist.Values | Where-Object { -not $_ }).Count -eq 0
if ($VisualVerdict -eq "PASS" -and -not $allChecksPass) {
    throw "VisualVerdict PASS requires every checklist field to be true"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path (Split-Path -Parent $sessionFullPath) "human_visual_result_v17.json"
}
$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputFullPath) | Out-Null
$record = [ordered]@{
    evidence_id = "C5-L1-human-visual-result-v17-20260814"
    session_evidence = $sessionFullPath
    candidate = $candidatePath
    candidate_sha256 = $actual
    adjacent_runtime_dll = $dllPath
    adjacent_runtime_dll_sha256 = $dllSha256
    observer = $Observer
    observed_at = (Get-Date -Format o)
    visual_verdict = $VisualVerdict
    checklist = $checklist
    notes = $Notes
    proves = "the named observer recorded the complete C5-L1 menu visual checklist against the SHA-verified candidate"
    not_proven = "broad localization quality, other screens, core gameplay, persistence, Steam behavior, or release readiness"
    state_change = "not_applied; primary agent must review this evidence before changing any project Gate"
}
[IO.File]::WriteAllText($outputFullPath, ($record | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $outputFullPath -Raw -Encoding UTF8
