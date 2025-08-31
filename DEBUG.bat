@echo off
REM ==================================================================
REM == Flowork Developer Debug Launcher ==
REM =============================================================
title Flowork (DEBUG MODE)
echo [INFO] Running in DEBUG mode using Poetry environment...
cd /d "%~dp0"
echo [INFO] Syncing dependencies with poetry.lock...
poetry install --no-root
echo [INFO] Starting the main Flowork application (main.py)...
echo -------------------------------------------------------------
echo.
poetry run python main.py
echo.
echo -------------------------------------------------------------
echo [INFO] The Flowork application has closed.
pause