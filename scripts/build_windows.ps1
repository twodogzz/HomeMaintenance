param(
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$specPath = Join-Path $scriptDir "HomeMaintenance.spec"

if (-not (Test-Path $specPath)) {
    throw "Spec file not found: $specPath"
}

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller is not installed or not on PATH."
}

Push-Location $projectRoot
try {
    $args = @("--noconfirm", $specPath)
    if (-not $NoClean) {
        $args = @("--noconfirm", "--clean", $specPath)
    }

    & pyinstaller @args
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    $exePath = Join-Path $projectRoot "dist\\HomeMaintenance\\HomeMaintenance.exe"
    Write-Host "Build complete."
    Write-Host "Executable: $exePath"
}
finally {
    Pop-Location
}
