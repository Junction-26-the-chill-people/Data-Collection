@echo off
setlocal
if defined WITHIN_PYTHON (
  "%WITHIN_PYTHON%" "%~dp0scripts\preview_server.py" %*
  exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0scripts\preview_server.py" %*
  exit /b
)
python "%~dp0scripts\preview_server.py" %*
if errorlevel 1 (
  echo Python 3 is needed for the local street-map preview. Set WITHIN_PYTHON to your Python executable.
  pause
)
