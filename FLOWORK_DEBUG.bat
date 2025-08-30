@echo off
REM ==================================================================
REM == Flowork Developer Debug Launcher ==
REM =============================================================

title Flowork (DEBUG MODE)
echo [INFO] Running in DEBUG mode using Poetry environment...

REM Moving to the directory where this .bat file is located
cd /d "%~dp0"

echo [INFO] Syncing dependencies with poetry.lock...
poetry install --no-root

echo [INFO] Starting the main Flowork application (main.py)...
echo -------------------------------------------------------------
echo.

REM Run the main application using poetry to ensure correct dev environment
poetry run python main.py

echo.
echo -------------------------------------------------------------
echo [INFO] The Flowork application has closed.

REM Hold the command prompt window so it doesn't close immediately.
pause