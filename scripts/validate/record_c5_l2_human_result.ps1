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
    [bool]$CharacterSelectReached,
    [Parameter(Mandatory = $true)]
    [bool]$CharacterTitleTextExact,
    [Parameter(Mandatory = $true)]
    [bool]$CreateButtonTextExact,
    [Parameter(Mandatory = $true)]
    [bool]$CloseButtonTextExact,
    [Parameter(Mandatory = $true)]
    [bool]$GlyphsOkay,
    [Parameter(Mandatory = $true)]
    [bool]$FallbackOkay,
    [Parameter(Mandatory = $true)]
    [bool]$ClippingOkay,
    [Parameter(Mandatory = $true)]
    [bool]$LayoutOkay,
    [bool]$ReturnToMenuOkay = $true,
    [string]$Observer = "human",
    [string]$Notes = "",
    [string]$ScreenshotPath = "",
    [string]$OutputPath = "",
    [string]$EvidenceId = "C5-L2-human-result-v1-20260814"
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
    character_select_reached = $CharacterSelectReached
    character_title_text_exact = $CharacterTitleTextExact
    create_button_text_exact = $CreateButtonTextExact
    close_button_text_exact = $CloseButtonTextExact
    glyphs_okay = $GlyphsOkay
    fallback_okay = $FallbackOkay
    clipping_okay = $ClippingOkay
    layout_okay = $LayoutOkay
    return_to_menu_okay = $ReturnToMenuOkay
}
$allChecksPass = @($checklist.Values | Where-Object { -not $_ }).Count -eq 0
if ($VisualVerdict -eq "PASS" -and -not $allChecksPass) {
    throw "VisualVerdict PASS requires every C5-L2 checklist field to be true"
}

$screenshot = $null
if (-not [string]::IsNullOrWhiteSpace($ScreenshotPath)) {
    $screenshotFullPath = (Resolve-Path -LiteralPath $ScreenshotPath).Path
    $screenshot = [ordered]@{
        path = $screenshotFullPath
        sha256 = (Get-FileHash -LiteralPath $screenshotFullPath -Algorithm SHA256).Hash.ToUpperInvariant()
    }
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path (Split-Path -Parent $sessionFullPath) "human_visual_result_c5_l2_v1.json"
}
$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
$record = [ordered]@{
    evidence_id = $EvidenceId
    session_evidence = $sessionFullPath
    candidate = $candidatePath
    candidate_sha256 = $actual
    adjacent_runtime_dll = $dllPath
    adjacent_runtime_dll_sha256 = $dllSha256
    observer = $Observer
    observed_at = (Get-Date -Format o)
    visual_verdict = $VisualVerdict
    checklist = $checklist
    screenshot = $screenshot
    notes = $Notes
    proves = "the named observer recorded the complete C5-L2 main-menu-to-character-selection checklist against the SHA-verified candidate"
    not_proven = "other screens, character creation gameplay, persistence, Steam behavior, broad localization quality, or release readiness"
    state_change = "not_applied; primary agent must review this evidence before changing the C5-L2 Gate"
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputFullPath) | Out-Null
[IO.File]::WriteAllText($outputFullPath, ($record | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $outputFullPath -Raw -Encoding UTF8
