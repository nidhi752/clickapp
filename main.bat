@echo off
setlocal enableextensions
cd /d "%~dp0"

set "VENV_PYW=%~dp0.venv\Scripts\pythonw.exe"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if exist "%VENV_PYW%" (
  set "PYW=%VENV_PYW%"
) else if exist "%VENV_PY%" (
  set "PYW=%VENV_PY%"
) else (
  for %%I in (pythonw.exe) do set "PYW=%%~$PATH:I"
  if not defined PYW (
    for %%I in (python.exe) do set "PYW=%%~$PATH:I"
  )
)

if not defined PYW (
  msg * "StickyCheck error: could not find pythonw/python. Run the console .bat to see details."
  exit /b 1
)

set "STICKYCHECK_MODE=desktop"
set "PYTHONUTF8=1"

rem Start without attaching to this console
start "" "%PYW%" -X utf8 "%~dp0trial2.py"
endlocal
