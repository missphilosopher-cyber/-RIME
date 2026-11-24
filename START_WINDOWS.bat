@echo off
setlocal
cd /d "%~dp0"
echo Starting PRIME local prototype...
if exist ".venv\Scripts\python.exe" goto dependencies
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
    if errorlevel 1 goto python_error
    py -3 -m venv .venv
) else (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
    if errorlevel 1 goto python_error
    python -m venv .venv
)
if errorlevel 1 goto setup_error
:dependencies
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto setup_error
echo Keep this window open. Press Ctrl+C here to stop.
".venv\Scripts\python.exe" app.py --open
if errorlevel 1 goto launch_error
exit /b 0
:python_error
echo Python 3.11 or newer is required. Install Python, enable PATH, and try again.
pause
exit /b 1
:setup_error
echo Setup did not finish. Check the error above and your internet connection.
pause
exit /b 1
:launch_error
echo The app stopped with an error. Check the message above.
echo If port 5050 is busy, run .venv\Scripts\python.exe app.py --port 5051 --open
pause
exit /b 1
