param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$resolved = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
$bytes = [System.IO.File]::ReadAllBytes($resolved)
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $encoding = [System.Text.Encoding]::UTF8
    $offset = 3
} elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
    $encoding = [System.Text.Encoding]::Unicode
    $offset = 2
} elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
    $encoding = [System.Text.Encoding]::BigEndianUnicode
    $offset = 2
} else {
    $encoding = [System.Text.Encoding]::UTF8
    $offset = 0
}
$text = $encoding.GetString($bytes, $offset, $bytes.Length - $offset)
$null = $text | ConvertFrom-Json
[System.IO.File]::WriteAllText($resolved, $text, [System.Text.UTF8Encoding]::new($false))
Write-Output "UTF8_NORMALIZED $resolved"
