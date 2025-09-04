echo off
REM ==================================================================
REM == Flowork Developer Debug Launcher (FINAL WITH PROGRESS) ==
REM =============================================================
title Flowork (DEBUG MODE)
echo [INFO] Running in DEBUG mode with a full portable environment...
cd /d "%~dp0"

REM --- Define path to the full portable Python ---
SET "PORTABLE_PYTHON=%~dp0python\python.exe"

REM --- Force PATH to use our local portable tools FIRST ---
echo [INFO] Forcing PATH to use local portable Python...
SET "PATH=%~dp0python;%~dp0python\Scripts;%PATH%"

REM --- Pre-flight Check ---
IF NOT EXIST "%PORTABLE_PYTHON%" (
    echo [FATAL] Portable Python not found at: %PORTABLE_PYTHON%
    pause
    exit /b
)

REM --- Step 1: Bootstrap Poetry if missing ---
echo [INFO] Checking for Poetry...
poetry --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN] Poetry not found. Installing it into the portable environment...
    echo [INFO] This may take a few minutes. Please wait for pip to finish downloading...

    REM (FIX) Removed the '--quiet' flag to show real-time download and installation progress.
    python -m pip install poetry

) ELSE (
    echo [INFO] Poetry is already available.
)

REM --- Step 2: Configure Poetry to create .venv locally ---
echo [INFO] Configuring Poetry to create virtual environment inside the project...
poetry config virtualenvs.in-project true --local
IF %ERRORLEVEL% NEQ 0 (
    echo [FATAL] Failed to configure Poetry.
    pause
    exit /b
)

REM --- Step 3: Sync project dependencies ---
echo [INFO] Syncing project dependencies...
poetry install --no-root
IF %ERRORLEVEL% NEQ 0 (
    echo [FATAL] 'poetry install' failed. Check your internet or poetry.lock file.
    pause
    exit /b
)

REM --- Step 4: Run the main application ---
echo [INFO] Starting the main Flowork application...
echo -------------------------------------------------------------
echo.
SET "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
"%VENV_PYTHON%" main.py
echo.
echo -------------------------------------------------------------
[INFO] The Flowork application has closed.
pause