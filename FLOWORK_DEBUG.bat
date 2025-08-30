@echo off
REM ==================================================================
REM == www.teetah.art ==
REM == sahidiaola@gmail.com ==
REM =============================================================

title Flowwork (DEBUG MODE)
echo [INFO] Running in DEBUG mode...

REM Moving to the directory where this .bat file is located
cd /d "%~dp0"

echo [INFO] Running initial library check (setup.py)...
REM Running setup to verify library Up-to-date
python scripts/setup.py

echo [INFO] Starting the main Flowork application (main.py)...
echo -------------------------------------------------------------
echo.

REM ====================================================================
REM === MAIN CHANGES HERE ===
REM 1. Uses "python.exe" (instead of pythonw.exe) to display output.
REM 2. Removes "START" so the application runs in this window and we can view the logs.
"%~dp0\python\python.exe" main.py
REM =====================================================================

echo.
echo -------------------------------------------------------------
echo [INFO] The Flowork application has closed.

REM Hold the command prompt window so it doesn't close immediately.
pause