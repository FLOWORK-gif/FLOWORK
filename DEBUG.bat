[FULL CODE FOR FILE: DEBUG.bat]
@echo off
REM ==================================================================
REM == Flowork Developer Debug Launcher ==
REM ==================================================================
title Flowork (DEBUG MODE)
echo [INFO] Running in DEBUG mode using Poetry environment...
cd /d "%~dp0"

echo [INFO] Syncing dependencies with poetry.lock...
poetry install --no-root
REM (MODIFIED) Check if the previous command was successful
if %ERRORLEVEL% neq 0 (
    echo [FATAL] Poetry install failed. Aborting.
    pause
    exit /b 1
)

echo [INFO] Starting the main Flowork application (main.py)...
echo -------------------------------------------------------------
echo.
poetry run python main.py
REM (MODIFIED) Check if the main application ran successfully
if %ERRORLEVEL% neq 0 (
    echo [ERROR] The Flowork application closed with an error.
    pause
    exit /b 1
)

echo.
echo -------------------------------------------------------------
echo [INFO] The Flowork application has closed successfully.
pause
REM (MODIFIED) Explicitly exit with success code 0
exit /b 0