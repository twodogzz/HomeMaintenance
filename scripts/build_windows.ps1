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

$buildCmd = $null
if (Get-Command pyinstaller -ErrorAction SilentlyContinue) {
    $buildCmd = @("pyinstaller")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $buildCmd = @("py", "-m", "PyInstaller")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $buildCmd = @("python", "-m", "PyInstaller")
}

if ($null -eq $buildCmd) {
    throw "No Python or PyInstaller command found on PATH."
}

Push-Location $projectRoot
try {
    $pyInstallerArgs = @("--noconfirm", $specPath)
    if (-not $NoClean) {
        $pyInstallerArgs = @("--noconfirm", "--clean", $specPath)
    }

    if ($buildCmd.Length -eq 1) {
        & $buildCmd[0] @pyInstallerArgs
    } else {
        & $buildCmd[0] $buildCmd[1] $buildCmd[2] @pyInstallerArgs
    }
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE. If missing, run: python -m pip install pyinstaller"
    }

    $exePath = Join-Path $projectRoot "dist\\HomeMaintenance\\HomeMaintenance.exe"
    Write-Host "Build complete."
    Write-Host "Executable: $exePath"
}
finally {
    Pop-Location
}
