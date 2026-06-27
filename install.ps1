$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FontDir = Join-Path $RepoDir "fonts\ttf"

if (-not (Test-Path $FontDir)) {
    throw "Trace Mono fonts not found at: $FontDir"
}

$Fonts = Get-ChildItem -Path $FontDir -Filter "*.ttf"
if ($Fonts.Count -eq 0) {
    throw "No .ttf files found in: $FontDir"
}

$Shell = New-Object -ComObject Shell.Application
$FontsFolder = $Shell.Namespace(0x14)
if ($null -eq $FontsFolder) {
    throw "Could not open the Windows Fonts folder."
}

foreach ($Font in $Fonts) {
    $Destination = Join-Path $env:WINDIR ("Fonts\" + $Font.Name)
    if (Test-Path $Destination) {
        Write-Host "Already installed $($Font.Name)"
        continue
    }

    $FontsFolder.CopyHere($Font.FullName)
    Write-Host "Installed $($Font.Name)"
}

Write-Host "Trace Mono installed. Select 'Trace Mono Console' or 'Trace Mono Inspect' in your terminal."
