@echo off
setlocal
REM doctor.cmd - locate Python 3.11 without hitting Windows Store alias (exit 9009)
set "PY_CANDIDATE="
for %%P in ("%USERPROFILE%\.local\bin\python.exe" "%USERPROFILE%\.local\bin\python3.exe" "%USERPROFILE%\.local\bin\python3.11.exe" "%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe") do (
  if exist "%%~P" (
    "%%~P" --version >nul 2>&1
    if not errorlevel 1 (
      set "PY_CANDIDATE=%%~P"
      goto :found
    )
  )
)
where python >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%I in ('where python') do (
    "%%I" --version >nul 2>&1
    if not errorlevel 1 (
      if not "%%~zI"=="0" (
        set "PY_CANDIDATE=%%I"
        goto :found
      )
    )
  )
)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
  set "PY_CANDIDATE=py -3.11"
  goto :found
)
uv --version >nul 2>&1
if not errorlevel 1 (
  set "PY_CANDIDATE=uv run --python 3.11 python"
  goto :found
)
:found
if "%PY_CANDIDATE%"=="" (
  echo [doctor.cmd] FAIL: Python 3.11 not found
  echo   tried .local\bin\python.exe, python, python3, py -3.11, uv run
  echo   where python:
  where python
  echo   fix: uv python install 3.11 ^& powershell -ExecutionPolicy Bypass -File "%USERPROFILE%\.local\bin\repair_python_shim.ps1"
  exit /b 9009
)
echo [doctor.cmd] using Python: %PY_CANDIDATE%
if exist "%USERPROFILE%\.local\bin\repair_python_shim.ps1" powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.local\bin\repair_python_shim.ps1" >nul 2>&1
set "SCRIPT=%~dp0dev_doctor.py"
%PY_CANDIDATE% "%SCRIPT%" %*
set "CODE=%ERRORLEVEL%"
if "%CODE%"=="9009" echo [doctor.cmd] FAIL 9009: Windows Store python alias
exit /b %CODE%
