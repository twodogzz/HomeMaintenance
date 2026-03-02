@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PS_SCRIPT=%SCRIPT_DIR%build_windows.ps1

if not exist "%PS_SCRIPT%" (
  echo build_windows.ps1 not found: %PS_SCRIPT%
  exit /b 1
)

if /I "%~1"=="noclean" (
  powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%" -NoClean
) else (
  powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
)

if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo Build finished successfully.
endlocal
